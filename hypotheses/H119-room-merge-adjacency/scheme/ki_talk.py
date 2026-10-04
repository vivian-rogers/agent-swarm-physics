"""Kinetic Ising on talk spins: minute-grid KI-5 with block fields (E1) and the read-gated call model (E2).

Shared by H117 (coupling invariance across field steps) and H119 (room-merge adjacency). The two hypotheses keep
byte-identical copies in their own scheme/ folders (no cross-hypothesis imports, STANDARDS section 8); suggested move:
infra/shared/kinetic_talk.py.

E1 (KI-5 block, H02's KI-5 with block fields):
  s_i(t) = +1 if activity_bins_fixed.state == 4 (talk) in minute t, else -1, on each day's DQ8 all-present window
  (day_matrices.trim_rows on the activity population). m_j(t) = mean of s_j over t-4..t (within the day).
  logit P(s_i(t+1) = +1) = h_i + delta_i(b) + K_i s_i(t) + K'_i m_i(t) + sum_j J_ij m_j(t)   [logistic units = 2J]
  b = (day, 30-min block of minute t+1). L2 penalty lam on J, K, K', delta; intercept unpenalized.
  Cluster-robust sandwich SEs, clusters = the blocks b.
E2 (read-gated call coupling): one row per ledger call c of agent i (context_ledger_turns x call_windows), y = talk call.
  L_c = latency_s (call start -> first record). R_cj = messages of j posted in i's room (the ledger turn's room) in
  [t_call - L_c, t_call); U_cj = messages of j posted in [t_call, t_call + L_c) (any room; same-room count kept apart).
  logit P(y_c) = delta_i(b) + a_i y_{c-1} + sum_k [JR_k XR_k + JU_k XU_k], with XR_k = sum_{j in class k} log(1 + R_cj).
Holdout: every loader drops held-out days (calendar.holdout, cross-checked with common.holdout_mask) unless the module
flag ALLOW_HOLDOUT is set, which only a guarded analysis/confirm.py does. No text is read.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402
import rooms_asof as RA  # noqa: E402
from day_matrices import trim_rows  # noqa: E402

ALLOW_HOLDOUT = False   # set ONLY by a guarded analysis/confirm.py
BOX = 5                 # boxcar length (minutes), H02 KI-5
BLOCK_MIN = 30
LAM = 1.0
MIN_TALK = 10           # talk minutes per agent per side
LAT_MAX = 600.0


class HoldoutError(RuntimeError):
    pass


# ============================================================================ tables
_CAL = None


def calendar() -> pl.DataFrame:
    global _CAL
    if _CAL is None:
        cal = pl.read_parquet(SH / "calendar.parquet")
        hm = np.array(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()), bool)
        assert (hm == cal["holdout"].to_numpy()).all(), "calendar.holdout disagrees with holdout_mask"
        _CAL = cal
    return _CAL


def check_days(days) -> None:
    cal = calendar().filter(pl.col("pt_date").is_in(list(days)))
    if len(cal) != len(set(days)):
        raise ValueError(f"unknown days: {sorted(set(days) - set(cal['pt_date'].to_list()))}")
    if cal["holdout"].any() and not ALLOW_HOLDOUT:
        raise HoldoutError("held-out day requested in exploratory code")


def claude_code() -> set:
    r = pl.read_parquet(SH / "roster.parquet")
    return set(r.filter(pl.col("claude_code"))["agent"].to_list())


def roster_names() -> dict:
    r = pl.read_parquet(SH / "roster.parquet")
    return dict(zip(r["agent"].to_list(), r["name"].to_list()))


# ============================================================================ spins
TRIM = "core60"         # all-present trim over agents with >= 60 active minutes that day (Amendment 0); "dq8" = all


def day_spins(days, trim: str | None = None) -> dict:
    """{day: {'agents', 'talk' (N x K int8 +-1), 'minutes' (K), 't0' (UTC datetime of minute 0)}} on the trimmed grid.
    trim = core60 (default): DQ8 all-present window computed over the day's agents with >= 60 active minutes, so a
    briefly present agent (a newcomer, a temporary leader) does not shrink the day to minutes; dq8: over all agents."""
    trim = trim or TRIM
    check_days(days)
    cc = claude_code()
    cal = calendar().filter(pl.col("pt_date").is_in(list(days)))
    w0 = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    ab = (pl.scan_parquet(SH / "activity_bins_fixed.parquet").select("pt_date", "minute", "agent", "state")
          .filter(pl.col("pt_date").is_in(list(days)) & ~pl.col("agent").is_in(list(cc))).collect())
    out = {}
    for d in sorted(days):
        g = ab.filter(pl.col("pt_date") == d)
        if g.height == 0:
            continue
        agents = np.unique(g["agent"].to_numpy().astype(int))
        L = int(g["minute"].max()) + 1
        S = np.ones((len(agents), L), np.int8)
        S[np.searchsorted(agents, g["agent"].to_numpy()), g["minute"].to_numpy()] = g["state"].to_numpy()
        act = np.where(S >= 3, 1, -1).astype(np.int8)
        pop = (act > 0).any(1)
        agents, S, act = agents[pop], S[pop], act[pop]
        core = (act > 0).sum(1) >= 60 if trim == "core60" else np.ones(len(agents), bool)
        keep = trim_rows(act[core]) if core.any() else np.zeros(act.shape[1], bool)
        mins = np.flatnonzero(keep).astype(np.int32)
        talk = np.where(S[:, keep] == 4, 1, -1).astype(np.int8)
        out[d] = {"agents": agents, "talk": talk, "minutes": mins, "t0": w0[d]}
    return out


def stack(spins: dict, days, agents) -> list:
    """Per day: N_agents x K talk matrix for the given agent list (absent agent -> -1)."""
    res = []
    for d in days:
        r = spins[d]
        K = len(r["minutes"])
        S = -np.ones((len(agents), K), np.int8)
        idx = {a: k for k, a in enumerate(r["agents"])}
        for n, a in enumerate(agents):
            if a in idx:
                S[n] = r["talk"][idx[a]]
        res.append((d, S, r["minutes"], r["t0"]))
    return res


def eligible(spins: dict, sides: list, min_talk: int = MIN_TALK) -> list:
    """Agents present (in the day's activity population) on every day of every side, >= min_talk talk minutes per side."""
    sets = None
    for days in sides:
        for d in days:
            if d not in spins:
                return []
            s = set(spins[d]["agents"].tolist())
            sets = s if sets is None else sets & s
    out = []
    for a in sorted(sets or []):
        ok = True
        for days in sides:
            n = 0
            for d in days:
                r = spins[d]
                k = int(np.flatnonzero(r["agents"] == a)[0])
                n += int((r["talk"][k] > 0).sum())
            ok &= n >= min_talk
        if ok:
            out.append(a)
    return out


def boxcar(S: np.ndarray, L: int = BOX) -> np.ndarray:
    """Mean over t-L+1..t within the row (shorter window at the start)."""
    c = np.cumsum(np.pad(S.astype(np.float64), ((0, 0), (1, 0))), axis=1)
    K = S.shape[1]
    hi = np.arange(1, K + 1)
    lo = np.maximum(0, hi - L)
    return (c[:, hi] - c[:, lo]) / (hi - lo)


# ============================================================================ co-location
def colocation(stacked: list, agents) -> list:
    """Per day: N x K room codes (-1 = no stay) at the middle of each kept minute."""
    out = []
    for d, S, mins, t0 in stacked:
        base = int(t0.timestamp() * 1e6)
        t_us = base + (mins.astype(np.int64) * 60 + 30) * 1_000_000
        R = np.stack([RA.room_at_us(int(a), t_us) for a in agents]).astype(np.int16)
        out.append(R)
    return out


def coloc_share(rooms: list) -> np.ndarray:
    """N x N share of kept minutes in which i and j are in the same room."""
    num = 0
    den = 0
    for R in rooms:
        same = (R[:, None, :] == R[None, :, :]) & (R[:, None, :] >= 0)
        num = num + same.sum(2)
        den += R.shape[1]
    return num / max(den, 1)


# ============================================================================ fitter
def fit_logit_fe(y, X, g, pen, lam_fe=LAM, cluster=None, max_iter=60, tol=1e-7):
    """Penalized logistic regression eta = fe[g] + X b, with fe ~ L2(lam_fe), b ~ L2(pen) (pen per column).

    y: 0/1 (n,), X: (n, p) dense, g: int group codes (n,) 0..G-1, pen: (p,). Newton with a diagonal fe block (Schur).
    Returns dict(b, fe, se (cluster-robust over `cluster`, default g), se0 (model), n, ll, conv).
    """
    y = np.asarray(y, np.float64)
    X = np.asarray(X, np.float64)
    g = np.asarray(g, np.int64)
    n, p = X.shape
    G = int(g.max()) + 1 if n else 0
    pen = np.asarray(pen, np.float64)
    b = np.zeros(p)
    fe = np.zeros(G)

    def objective(b_, fe_):
        eta = X @ b_ + fe_[g]
        return (y * eta - np.logaddexp(0, eta)).sum() - 0.5 * (pen * b_ ** 2).sum() - 0.5 * lam_fe * (fe_ ** 2).sum()

    obj = objective(b, fe)
    conv = False
    for _ in range(max_iter):
        eta = X @ b + fe[g]
        pr = 1 / (1 + np.exp(-eta))
        w = pr * (1 - pr)
        r = y - pr
        D = np.bincount(g, w, G) + lam_fe
        gf = np.bincount(g, r, G) - lam_fe * fe
        C = np.zeros((G, p))
        np.add.at(C, g, X * w[:, None])
        Hb = (X * w[:, None]).T @ X + np.diag(pen)
        gb = X.T @ r - pen * b
        CD = C / D[:, None]
        M = Hb - C.T @ CD
        rhs = gb - CD.T @ gf
        try:
            db = np.linalg.solve(M, rhs)
        except np.linalg.LinAlgError:
            db = np.linalg.lstsq(M, rhs, rcond=None)[0]
        df = (gf - C @ db) / D
        step = 1.0
        while step > 1e-4:
            nb, nf = b + step * db, fe + step * df
            nobj = objective(nb, nf)
            if nobj >= obj - 1e-10:
                break
            step /= 2
        b, fe = nb, nf
        dmax = step * max(np.abs(db).max() if p else 0, np.abs(df).max() if G else 0)
        obj = nobj
        if dmax < tol:
            conv = True
            break
    eta = X @ b + fe[g]
    pr = 1 / (1 + np.exp(-eta))
    w = pr * (1 - pr)
    D = np.bincount(g, w, G) + lam_fe
    C = np.zeros((G, p))
    np.add.at(C, g, X * w[:, None])
    M = (X * w[:, None]).T @ X + np.diag(pen) - C.T @ (C / D[:, None])
    Minv = np.linalg.pinv(M)
    Xt = X - (C / D[:, None])[g]
    sc = (y - pr)[:, None] * Xt
    cl = g if cluster is None else np.asarray(cluster, np.int64)
    _, cinv = np.unique(cl, return_inverse=True)
    nc = int(cinv.max()) + 1
    S = np.zeros((nc, p))
    np.add.at(S, cinv, sc)
    meat = S.T @ S * (nc / max(nc - 1, 1))
    V = Minv @ meat @ Minv
    return {"b": b, "fe": fe, "se": np.sqrt(np.maximum(np.diag(V), 0)), "se0": np.sqrt(np.maximum(np.diag(Minv), 0)),
            "V": V, "n": n, "ll": float(objective(b, fe)), "conv": conv}


# ============================================================================ E1 designs
def e1_rows(stacked: list, i: int, others: list | None = None):
    """Recipient row i of the stacked matrices -> y, X = [s_i, m_i, m_j (j in others)], block codes."""
    ys, Xs, bs = [], [], []
    N = stacked[0][1].shape[0]
    others = [j for j in range(N) if j != i] if others is None else others
    for di, (d, S, mins, t0) in enumerate(stacked):
        if S.shape[1] < BOX + 2:
            continue
        m = boxcar(S)
        y = (S[i, 1:] > 0).astype(np.float64)
        X = np.column_stack([S[i, :-1].astype(np.float64), m[i, :-1]] + [m[j, :-1] for j in others])
        blk = di * 1000 + mins[1:] // BLOCK_MIN
        ys.append(y); Xs.append(X); bs.append(blk)
    y = np.concatenate(ys); X = np.vstack(Xs); blk = np.concatenate(bs)
    _, g = np.unique(blk, return_inverse=True)
    return y, X, g


def fit_e1_full(stacked: list, fields: str = "block", lam: float = LAM):
    """Per-recipient KI-5 fits. Returns J (N x N; diag nan), SE, K (N x 2), conv flags. fields = block | naive."""
    N = stacked[0][1].shape[0]
    J = np.full((N, N), np.nan); SE = np.full((N, N), np.nan); conv = []
    for i in range(N):
        others = [j for j in range(N) if j != i]
        y, X, g = e1_rows(stacked, i, others)
        Xc = np.column_stack([np.ones(len(y)), X])
        pen = np.r_[0.0, np.full(X.shape[1], lam)]
        if fields == "naive":
            r = fit_logit_fe(y, Xc, np.zeros_like(g), pen, lam_fe=1e8, cluster=g)
        else:
            r = fit_logit_fe(y, Xc, g, pen, lam_fe=lam)
        b, se = r["b"][1:], np.maximum(r["se"][1:], r["se0"][1:])   # SE floor: robust SE never below model SE
        J[i, others] = b[2:]; SE[i, others] = se[2:]
        conv.append(r["conv"])
    return J, SE, np.array(conv)


def fit_e1_mf(stacked: list, mask: np.ndarray | None = None, lam: float = LAM):
    """Per-recipient mean-field coupling: one coefficient on sum_{j in mask[i]} m_j(t) (block fields as in E1).
    Returns (b, se) arrays of length N (nan where the recipient has no partner)."""
    N = stacked[0][1].shape[0]
    mask = (~np.eye(N, dtype=bool)) if mask is None else mask
    b = np.full(N, np.nan); se = np.full(N, np.nan)
    for i in range(N):
        js = [j for j in range(N) if mask[i, j]]
        if not js:
            continue
        y, X, g = e1_rows(stacked, i, js)
        Xm = np.column_stack([np.ones(len(y)), X[:, 0], X[:, 1], X[:, 2:].sum(1)])
        r = fit_logit_fe(y, Xm, g, np.array([0.0, lam, lam, lam]), lam_fe=lam)
        b[i] = r["b"][3]; se[i] = max(r["se"][3], r["se0"][3])
    return b, se


def field_logit(stacked: list):
    """Per agent: logit talk rate on the side and its cluster-robust SE (blocks as clusters; delta method)."""
    N = stacked[0][1].shape[0]
    h = np.zeros(N); se = np.zeros(N)
    for n in range(N):
        vals, blks = [], []
        for di, (d, S, mins, t0) in enumerate(stacked):
            vals.append((S[n] > 0).astype(float)); blks.append(di * 1000 + mins // BLOCK_MIN)
        v = np.concatenate(vals); b = np.concatenate(blks)
        p = (v.sum() + 0.5) / (len(v) + 1.0)
        _, inv = np.unique(b, return_inverse=True)
        B = inv.max() + 1
        sb = np.bincount(inv, v - p, B)
        var_p = (sb ** 2).sum() / len(v) ** 2 * B / max(B - 1, 1)
        var_p = max(var_p, p * (1 - p) / len(v))
        h[n] = np.log(p / (1 - p)); se[n] = np.sqrt(var_p) / (p * (1 - p))
    return h, se


def sym(J: np.ndarray, SE: np.ndarray):
    Js = (J + J.T) / 2
    Vs = (SE ** 2 + SE.T ** 2) / 4
    return Js, Vs


def q_stats(Ja, SEa, Jb, SEb, pairmask: np.ndarray) -> dict:
    """Coupling-shift Q, Frobenius D_F (per pair) over the upper-triangle pairs in pairmask (symmetric J)."""
    Jsa, Vsa = sym(Ja, SEa); Jsb, Vsb = sym(Jb, SEb)
    iu = np.triu_indices(Ja.shape[0], 1)
    m = pairmask[iu] & np.isfinite(Jsa[iu]) & np.isfinite(Jsb[iu])
    d = (Jsa[iu] - Jsb[iu])[m]
    v = (Vsa[iu] + Vsb[iu])[m]
    if m.sum() == 0:
        return {"Q": np.nan, "DF": np.nan, "n_pairs": 0}
    return {"Q": float(np.mean(d ** 2 / v)), "DF": float(np.sqrt(np.mean(d ** 2))), "n_pairs": int(m.sum()),
            "Jbar_b": float(np.mean(Jsb[iu][m])), "Jbar_a": float(np.mean(Jsa[iu][m]))}


def f_stat(ha, sea, hb, seb, mask=None) -> float:
    m = np.ones(len(ha), bool) if mask is None else mask
    return float(np.mean(((ha - hb) ** 2 / (sea ** 2 + seb ** 2))[m]))


# ============================================================================ E1 class (block) model
def e1_class_rows(stacked: list, classes: np.ndarray, class_ids: list, coloc_rooms: list | None = None,
                  gate: bool = False):
    """Pooled rows over recipients. classes: N x N int class code per directed pair (recipient i, sender j); -1 = none.
    X = [recipient-specific s_i, m_i (2N columns)] + one column per class: sum_{j in class(i,.)} m_j(t)
    (gate=True multiplies m_j by co-location of i and j at minute t). Groups = (recipient, day, 30-min block)."""
    N = stacked[0][1].shape[0]
    C = len(class_ids)
    ys, Xs, gs, cls = [], [], [], []
    for di, (d, S, mins, t0) in enumerate(stacked):
        if S.shape[1] < BOX + 2:
            continue
        m = boxcar(S)
        R = coloc_rooms[di] if coloc_rooms is not None else None
        for i in range(N):
            y = (S[i, 1:] > 0).astype(np.float64)
            T = len(y)
            Xs_i = np.zeros((T, 2 * N + C))
            Xs_i[:, 2 * i] = S[i, :-1]
            Xs_i[:, 2 * i + 1] = m[i, :-1]
            for k, c in enumerate(class_ids):
                js = np.flatnonzero(classes[i] == c)
                if len(js) == 0:
                    continue
                if gate and R is not None:
                    same = (R[js, :-1] == R[i, :-1][None, :]) & (R[i, :-1][None, :] >= 0)
                    Xs_i[:, 2 * N + k] = (m[js, :-1] * same).sum(0)
                else:
                    Xs_i[:, 2 * N + k] = m[js, :-1].sum(0)
            blk = (i * 100 + di) * 1000 + mins[1:] // BLOCK_MIN
            ys.append(y); Xs.append(Xs_i); gs.append(blk); cls.append(blk)
    y = np.concatenate(ys); X = np.vstack(Xs); blk = np.concatenate(gs)
    _, g = np.unique(blk, return_inverse=True)
    return y, X, g


def fit_e1_class(stacked, classes, class_ids, lam=LAM, coloc_rooms=None, gate=False):
    N = stacked[0][1].shape[0]
    y, X, g = e1_class_rows(stacked, classes, class_ids, coloc_rooms, gate)
    keep = np.abs(X).sum(0) > 0
    pen = np.full(X.shape[1], lam)
    Xc = np.column_stack([np.ones(len(y)), X[:, keep]])
    r = fit_logit_fe(y, Xc, g, np.r_[0.0, pen[keep]], lam_fe=lam)
    b = np.full(X.shape[1], np.nan); se = np.full(X.shape[1], np.nan)
    b[keep] = r["b"][1:]; se[keep] = r["se"][1:]
    V = np.full((X.shape[1], X.shape[1]), np.nan)
    ki = np.flatnonzero(keep)
    V[np.ix_(ki, ki)] = r["V"][1:, 1:]
    C = len(class_ids)
    return {"J": b[2 * N:], "se": se[2 * N:], "V": V[2 * N:, 2 * N:], "conv": r["conv"], "n": r["n"]}


# ============================================================================ E2 (calls)
def calls_frame(days, agents) -> pl.DataFrame:
    """Ledger calls of the given agents on the given days: turn_id, agent, pt_date, t_call (us), L (s), y, room."""
    check_days(days)
    tu = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter(pl.col("pt_date").is_in(list(days)) & pl.col("agent").is_in(list(agents)))
          .select("turn_id", "agent", "pt_date", "t_call", "talk", "room", "holdout").collect())
    if tu["holdout"].any() and not ALLOW_HOLDOUT:
        raise HoldoutError("held-out ledger rows")
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(list(days)))
          .select("turn_id", "latency_s").collect())
    f = (tu.join(cw, on="turn_id", how="inner")
         .filter(pl.col("latency_s").is_not_null() & (pl.col("latency_s") > 0) & (pl.col("latency_s") <= LAT_MAX)
                 & pl.col("t_call").is_not_null())
         .with_columns(pl.col("t_call").dt.epoch("us").alias("tc_us"))
         .sort("agent", "t_call"))
    return f


def messages_frame(days) -> pl.DataFrame:
    check_days(days)
    c = (pl.scan_parquet(SH / "chat_core.parquet")
         .filter(pl.col("pt_date").is_in(list(days)) & (pl.col("speaker_kind").cast(pl.String) == "agent")
                 & pl.col("agent").is_not_null())
         .select("t", "agent", "room").collect()
         .with_columns(pl.col("t").dt.epoch("us").alias("t_us")).sort("t_us"))
    return c


def e2_counts(calls: pl.DataFrame, msgs: pl.DataFrame, senders: list):
    """R (n x S) visible same-room messages in [t_call - L, t_call); U (n x S) any-room messages in [t_call, t_call + L);
    Us (n x S) same-room part of U."""
    tc = calls["tc_us"].to_numpy().astype(np.int64)
    L = (calls["latency_s"].to_numpy() * 1e6).astype(np.int64)
    room = calls["room"].to_numpy()
    rec = calls["agent"].to_numpy()
    n = len(tc)
    R = np.zeros((n, len(senders)), np.int32); U = np.zeros_like(R); Us = np.zeros_like(R)
    ma = msgs["agent"].to_numpy(); mt = msgs["t_us"].to_numpy().astype(np.int64); mr = msgs["room"].to_numpy()
    for k, j in enumerate(senders):
        sel = ma == j
        tj, rj = mt[sel], mr[sel]
        o = np.argsort(tj); tj, rj = tj[o], rj[o]
        U[:, k] = np.searchsorted(tj, tc + L, "left") - np.searchsorted(tj, tc, "left")
        for r_ in np.unique(rj):
            tr = tj[rj == r_]
            sel_c = room == r_
            if not sel_c.any():
                continue
            R[sel_c, k] = np.searchsorted(tr, tc[sel_c], "left") - np.searchsorted(tr, tc[sel_c] - L[sel_c], "left")
            Us[sel_c, k] = np.searchsorted(tr, tc[sel_c] + L[sel_c], "left") - np.searchsorted(tr, tc[sel_c], "left")
        R[rec == j, k] = 0; U[rec == j, k] = 0; Us[rec == j, k] = 0
    return R, U, Us


def e2_design(calls: pl.DataFrame, R, U, senders, classes_fn, class_ids):
    """Pooled design: [a_i * y_prev (one column per recipient)] + XR_k, XU_k per class. classes_fn(i, j) -> class."""
    rec = calls["agent"].to_numpy()
    y = calls["talk"].to_numpy().astype(np.float64)
    agents = sorted(set(rec.tolist()))
    ai = {a: k for k, a in enumerate(agents)}
    yprev = np.zeros(len(y))
    same = np.r_[False, rec[1:] == rec[:-1]]
    yprev[1:] = y[:-1]
    yprev[~same] = 0
    A = len(agents)
    C = len(class_ids)
    X = np.zeros((len(y), A + 2 * C))
    X[np.arange(len(y)), [ai[a] for a in rec]] = yprev
    lR = np.log1p(R); lU = np.log1p(U)
    for k, j in enumerate(senders):
        cls = np.array([classes_fn(a, j) for a in rec])
        for c_i, c in enumerate(class_ids):
            sel = cls == c
            X[sel, A + c_i] += lR[sel, k]
            X[sel, A + C + c_i] += lU[sel, k]
    tday = calls["pt_date"].to_numpy()
    tmin = (calls["tc_us"].to_numpy() // 60_000_000) // BLOCK_MIN
    key = np.array([f"{a}|{d}|{m}" for a, d, m in zip(rec, tday, tmin)])
    _, g = np.unique(key, return_inverse=True)
    return y, X, g, A


def fit_e2(y, X, g, A, C, lam=LAM, min_nz=30):
    keep = (X != 0).sum(0) >= min_nz
    keep[:A] = (X[:, :A] != 0).sum(0) > 0
    Xc = np.column_stack([np.ones(len(y)), X[:, keep]])
    r = fit_logit_fe(y, Xc, g, np.r_[0.0, np.full(keep.sum(), lam)], lam_fe=lam)
    b = np.full(X.shape[1], np.nan); se = np.full(X.shape[1], np.nan)
    b[keep] = r["b"][1:]; se[keep] = r["se"][1:]
    V = np.full((X.shape[1], X.shape[1]), np.nan)
    ki = np.flatnonzero(keep)
    V[np.ix_(ki, ki)] = r["V"][1:, 1:]
    return {"JR": b[A:A + C], "JU": b[A + C:A + 2 * C], "seR": se[A:A + C], "seU": se[A + C:A + 2 * C],
            "V": V[A:, A:], "n": r["n"], "nzR": (X[:, A:A + C] != 0).sum(0), "nzU": (X[:, A + C:] != 0).sum(0),
            "conv": r["conv"]}
