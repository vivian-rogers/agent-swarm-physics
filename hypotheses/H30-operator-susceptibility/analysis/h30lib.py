"""H30 library: the operator-susceptibility gauge chi_op.

Two layers:
1. A swarm-agnostic core (Panel, build_base, kick_columns, fit_activity, daily_activity, content_scores, stability).
   It needs only per-minute activity per agent, operator kicks (minute, recipient, class) and, for the content
   channel, statement vectors before/after each kick plus the message direction. `gauge.py` wraps it for any log.
2. Village loaders (shared tables only; holdout refused unless allow_holdout=True, which only confirm.py passes).

Definitions are on the card (hypotheses/H30-operator-susceptibility/README.md, "Definitions"). Threads pinned low:
callers use at most 2 processes.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H30-operator-susceptibility"
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H30-operator-susceptibility"
FIG = HYP / "figures"
HOLDOUT = json.loads((ROOT / "hypotheses/holdout.json").read_text())
SEED = 20261003

sys.path.insert(0, str(ROOT / "hypotheses/H04-reversible-forcing/analysis"))
sys.path.insert(0, str(ROOT / "infra/shared"))
from h04lib import ACT_BINS, IDLE_BINS, window_sum  # noqa: E402  (imported, never modified)

H = 30            # response horizon (min): Y = sum_{tau=1..H} n(m+tau)  (H04's A30)
HIST = 15         # pre-history window for strata (min)
PRE_LO, PRE_HI = -30, -16   # pre-window placebo outcome
SINCE_EDGES = np.array([1, 5, 15, 20, 30, 45, 90])  # minutes since last active: 0|1-4|5-14|15-19|20-29|30-44|45-89|90+; 8 = not yet active
N_SINCE = len(SINCE_EDGES) + 2
KREC_EDGES = np.array([16, 31, 61])    # minutes since the agent's last DIRECT kick (N_tgt, H_men): 1-15|16-30|31-60|none in 60
N_KREC = 4
N_LOCAL = 3 * 4 * 3 * N_SINCE * N_KREC * 3  # state(m-1) x act15 x idle15 x since-bin x kick-recency x day-third
DIRECT = ("N_tgt", "H_men")
CLASSES = ("N_tgt", "N_by", "H_men", "H_und")
CON_WIN_S = 3600.0   # content pre/post window (s)
CON_KMAX = 5         # statements kept per side
N_MATCH = 10         # matched placebos per kick
MIRROR = ("pause", "send_message_back_to_chat", "search_history", "move_to_room")


# =============================================================================== generic core: activity channel

@dataclass
class Panel:
    """One day: per-minute activity of the agents present that day."""
    day: int                 # index within the analysed set of days
    act: np.ndarray          # (n_agents, n_min) int8: 1 active
    idle: np.ndarray         # (n_agents, n_min) int8: 1 declared idle / paused (zeros if unknown)
    agents: np.ndarray       # agent codes (int)
    label: str = ""
    goal_day: int = 0

    @property
    def n_min(self):
        return self.act.shape[1]


@dataclass
class Base:
    """Kick-independent cell table: one row per present agent-minute with full pre-history and horizon."""
    day: np.ndarray
    row: np.ndarray
    agent: np.ndarray
    minute: np.ndarray
    stratum: np.ndarray      # agent x local stratum (compressed later)
    Y: np.ndarray            # sum of n over tau = 1..H
    Ypre: np.ndarray         # sum over tau = -30..-16 (placebo outcome)
    pre_ok: np.ndarray       # minute >= 30
    out_ok: np.ndarray = None  # no village-off minute in [m-15, m+30]
    shapes: dict = field(default_factory=dict)   # day -> (n_agents, n_min)
    offsets: dict = field(default_factory=dict)  # day -> (start index in cell arrays, list of minutes)


def _direct_recency(kicks: pl.DataFrame | None, day: int, na: int, nm: int) -> np.ndarray:
    """(na, nm) minutes since the agent's last direct kick strictly before minute m (large if none today)."""
    last = np.full((na, nm), -10 ** 6, np.int64)
    if kicks is not None and kicks.height:
        g = kicks.filter((pl.col("day") == day) & pl.col("cls").is_in(list(DIRECT)))
        if g.height:
            M = np.zeros((na, nm), bool)
            r = g["row"].to_numpy(); mi = g["minute"].to_numpy()
            ok = (r >= 0) & (r < na) & (mi >= 0) & (mi < nm)
            M[r[ok], mi[ok]] = True
            idx = np.where(M, np.arange(nm)[None, :], -10 ** 6)
            last = np.maximum.accumulate(idx, axis=1)
    rec = np.full((na, nm), 10 ** 6, np.int64)
    rec[:, 1:] = np.arange(1, nm)[None, :] - last[:, :-1]
    return rec


OUTAGE_MIN = 30   # village-off: every present agent silent (no event, no declared pause) for >= 30 consecutive minutes


def outage_minutes(act: np.ndarray, idle: np.ndarray, min_len: int = OUTAGE_MIN) -> np.ndarray:
    """(n_min,) bool: minutes inside a run of >= min_len minutes in which every present agent is silent, between the
    day's first and last active minute (post hoc amendment A2; H16 found such runs in #37, #38 and #51)."""
    silent = ((act == 0) & (idle == 0)).all(0)
    anyact = act.any(0)
    if not anyact.any():
        return np.zeros(act.shape[1], bool)
    first, last = np.argmax(anyact), len(anyact) - 1 - np.argmax(anyact[::-1])
    out = np.zeros(act.shape[1], bool)
    i = first
    while i <= last:
        if silent[i]:
            j = i
            while j <= last and silent[j]:
                j += 1
            if j - i >= min_len:
                out[i:j] = True
            i = j
        else:
            i += 1
    return out


def build_base(panels: list[Panel], hist: int = HIST, horizon: int = H, kicks: pl.DataFrame | None = None,
               strata: str = "full") -> Base:
    """strata = "full" (H30: + fine idle duration + direct-kick recency) or "h04" (H04's pre-history strata)."""
    parts = {k: [] for k in ("day", "row", "agent", "minute", "stratum", "Y", "Ypre", "pre_ok", "out_ok")}
    shapes, offsets, start = {}, {}, 0
    for p in panels:
        act = p.act.astype(np.int8)
        idle = (p.idle.astype(np.int8) * (1 - act)).astype(np.int8)
        na, nm = act.shape
        shapes[p.day] = (na, nm)
        if nm - horizon <= hist + 1 or na == 0:
            offsets[p.day] = (start, np.zeros(0, int))
            continue
        m = np.arange(hist, nm - horizon)
        # history through the kick minute itself (sh = 0; the nudger decides on the agent's state in that minute) or,
        # for the H04 variant, through m - 1 (sh = 1)
        sh = 1 if strata == "h04" else 0
        st = np.where(act == 1, 2, np.where(idle == 1, 1, 0))
        idx = np.where(act == 1, np.arange(nm)[None, :], -1)
        last = np.maximum.accumulate(idx, axis=1)           # last active minute <= t
        lm1 = last[:, m - sh]
        since = (m[None, :] - sh) - lm1
        sbin = np.where(lm1 < 0, N_SINCE - 1, np.digitize(since, SINCE_EDGES))
        krec = np.digitize(_direct_recency(kicks, p.day, na, nm)[:, m], KREC_EDGES)
        if strata == "h04":
            sbin = np.zeros_like(sbin); krec = np.zeros_like(krec)
        a15 = np.clip(window_sum(act, -hist + 1 - sh, -sh)[:, m], 0, 15)
        i15 = np.clip(window_sum(idle, -hist + 1 - sh, -sh)[:, m], 0, 15)
        tod = (m * 3 // nm)[None, :].repeat(na, 0)
        loc = ((((st[:, m - sh] * 4 + ACT_BINS[a15]) * 3 + IDLE_BINS[i15]) * N_SINCE + sbin) * N_KREC + krec) * 3 + tod
        Y = window_sum(act, 1, horizon)[:, m]
        Yp = window_sum(act, PRE_LO, PRE_HI)[:, m]
        rows = np.arange(na)[:, None].repeat(len(m), 1)
        parts["day"].append(np.full(na * len(m), p.day, np.int32))
        parts["row"].append(rows.ravel().astype(np.int16))
        parts["agent"].append(np.repeat(np.asarray(p.agents), len(m)).astype(np.int32))
        parts["minute"].append(np.tile(m, na).astype(np.int32))
        parts["stratum"].append((np.repeat(np.asarray(p.agents), len(m)).astype(np.int64) * N_LOCAL + loc.ravel()))
        parts["Y"].append(Y.ravel().astype(np.float32))
        parts["Ypre"].append(Yp.ravel().astype(np.float32))
        parts["pre_ok"].append(np.tile(m >= -PRE_LO, na))
        off = outage_minutes(act, idle)
        bad = window_sum(off[None, :].astype(np.int8), -hist, horizon)[0, m] > 0
        parts["out_ok"].append(np.tile(~bad, na))
        offsets[p.day] = (start, m)
        start += na * len(m)
    b = Base(**{k: np.concatenate(v) if v else np.zeros(0) for k, v in parts.items()}, shapes=shapes, offsets=offsets)
    _, b.stratum = np.unique(b.stratum, return_inverse=True)
    return b


POST_CLASSES = ("N_by", "H_und")   # future kicks adjusted for: undirected only. Future DIRECTED kicks depend on the
                                   # agent's future state (the nudger fires on agents that stay idle) -> a bad control.


def kick_columns(base: Base, kicks: pl.DataFrame, classes=CLASSES, horizon: int = H, post_classes=POST_CLASSES) -> np.ndarray:
    """Kick regressors: K^c at m for each class; then K^post_c (m+1..m+H) for c in post_classes; then K^pre_c
    (m-30..m-1) for every class. `kicks` needs columns day, row, minute, cls."""
    nc = len(classes)
    pc = [c for c in post_classes if c in classes]
    out = np.zeros((len(base.Y), 2 * nc + len(pc)), np.float32)
    cidx = {c: j for j, c in enumerate(classes)}
    kk = kicks.filter(pl.col("cls").is_in(list(classes)))
    by_day = {d: g for (d,), g in kk.group_by(["day"])} if kk.height else {}
    for d, (na, nm) in base.shapes.items():
        start, m = base.offsets[d]
        if len(m) == 0 or d not in by_day:
            continue
        g = by_day[d]
        K = np.zeros((nc, na, nm), np.int32)
        r = g["row"].to_numpy(); mi = g["minute"].to_numpy(); c = np.array([cidx[x] for x in g["cls"].to_list()])
        ok = (r >= 0) & (r < na) & (mi >= 0) & (mi < nm)
        np.add.at(K, (c[ok], r[ok], mi[ok]), 1)
        blk = slice(start, start + na * len(m))
        for j in range(nc):
            out[blk, j] = K[j][:, m].ravel()
            out[blk, nc + len(pc) + j] = window_sum(K[j], -30, -1)[:, m].ravel()
        for q, cname in enumerate(pc):
            out[blk, nc + q] = window_sum(K[cidx[cname]], 1, horizon)[:, m].ravel()
    return out


def _demean(x: np.ndarray, s: np.ndarray, cnt: np.ndarray) -> np.ndarray:
    mu = np.bincount(s, weights=x, minlength=len(cnt)) / np.maximum(cnt, 1)
    return x - mu[s]


@dataclass
class ActFit:
    classes: tuple
    beta: np.ndarray          # K^c (nc), K^post for POST_CLASSES, K^pre (nc)
    se: np.ndarray            # cluster (agent-day) robust
    n_kicks: dict
    day_A: np.ndarray         # (n_days, nc): sum_cells Xt_c * part_c
    day_B: np.ndarray         # (n_days, nc): sum_cells Xt_c^2
    day_se: np.ndarray        # (n_days, nc): within-day cluster(agent) SE of A/B
    days: np.ndarray          # day labels for rows of day_A
    kick_r: pl.DataFrame      # per kick cell: day,row,minute,cls,K,r,w
    outcome: str = "Y"

    def coef(self, c):
        return float(self.beta[self.classes.index(c)])


def _demean2(x: np.ndarray, s: np.ndarray, cnt: np.ndarray, g: np.ndarray | None, gcnt: np.ndarray | None,
             iters: int = 30, tol: float = 1e-7) -> np.ndarray:
    """Remove stratum fixed effects, and optionally a second additive fixed effect g (alternating projections)."""
    if g is None:
        return _demean(x, s, cnt)
    r = x.copy()
    for _ in range(iters):
        r0 = r
        r = _demean(_demean(r, s, cnt), g, gcnt)
        if np.max(np.abs(r - r0)) < tol * (1 + np.max(np.abs(x))):
            break
    return r


def fit_activity(base: Base, X: np.ndarray, classes=CLASSES, outcome: str = "Y", mask: np.ndarray | None = None,
                 fe2: str | None = "day", strata_extra: np.ndarray | None = None) -> ActFit:
    """fe2: second additive fixed effect: "day" (A2 default: each day's own baseline), "agentday" or None (as
    pre-registered: strata only). strata_extra: an extra per-cell stratum dimension (e.g., the cell's own context-fill
    phase)."""
    y = (base.Y if outcome == "Y" else base.Ypre).astype(np.float64)
    sel = np.ones(len(y), bool) if mask is None else mask.copy()
    if outcome == "Ypre":
        sel &= base.pre_ok
    s = base.stratum[sel].astype(np.int64)
    if strata_extra is not None:
        s = s * 16 + strata_extra[sel].astype(np.int64)
    _, s = np.unique(s, return_inverse=True)
    cnt = np.bincount(s).astype(float)
    g = gcnt = None
    if fe2 == "day":
        _, g = np.unique(base.day[sel], return_inverse=True)
    elif fe2 == "agentday":
        _, g = np.unique(base.day[sel].astype(np.int64) * 4096 + base.row[sel].astype(np.int64), return_inverse=True)
    if g is not None:
        gcnt = np.bincount(g).astype(float)
    Xs = X[sel].astype(np.float64)
    nc = len(classes)
    keep_cols = [j for j in range(Xs.shape[1]) if Xs[:, j].any()]
    Xt = np.zeros_like(Xs)
    for j in keep_cols:
        Xt[:, j] = _demean2(Xs[:, j], s, cnt, g, gcnt)
    yt = _demean2(y[sel], s, cnt, g, gcnt)
    cols = [j for j in keep_cols if (Xt[:, j] ** 2).sum() > 1e-9]
    beta = np.full(Xs.shape[1], np.nan)
    se = np.full(Xs.shape[1], np.nan)
    days_all = base.day[sel]
    udays = np.array(sorted(base.shapes))
    dix = np.searchsorted(udays, days_all)
    nd = len(udays)
    dA = np.full((nd, nc), np.nan); dB = np.zeros((nd, nc)); dse = np.full((nd, nc), np.nan)
    kick_rows = []
    if cols:
        A = Xt[:, cols]
        XtX = A.T @ A
        b = np.linalg.solve(XtX + 1e-9 * np.eye(len(cols)), A.T @ yt)
        e = yt - A @ b
        cl = days_all.astype(np.int64) * 4096 + base.row[sel].astype(np.int64)
        _, cl = np.unique(cl, return_inverse=True)
        G = np.zeros((cl.max() + 1, len(cols)))
        np.add.at(G, cl, A * e[:, None])
        Xi = np.linalg.inv(XtX + 1e-9 * np.eye(len(cols)))
        V = Xi @ (G.T @ G) @ Xi
        beta[cols] = b; se[cols] = np.sqrt(np.diag(V))
        bfull = np.nan_to_num(beta)
        for j in range(nc):
            if j not in cols:
                continue
            part = yt - Xt @ bfull + Xt[:, j] * bfull[j]
            xa = Xt[:, j]
            dA[:, j] = np.bincount(dix, weights=xa * part, minlength=nd)
            dB[:, j] = np.bincount(dix, weights=xa * xa, minlength=nd)
            with np.errstate(invalid="ignore", divide="ignore"):
                chi_d = dA[:, j] / dB[:, j]
                res = part - chi_d[dix] * xa
            sc = np.bincount(cl, weights=xa * np.nan_to_num(res))
            cl_day = np.zeros(cl.max() + 1, np.int64); cl_day[cl] = dix
            v = np.bincount(cl_day, weights=sc ** 2, minlength=nd)
            with np.errstate(invalid="ignore", divide="ignore"):
                dse[:, j] = np.sqrt(v) / dB[:, j]
            kc = (Xs[:, j] > 0) & (xa ** 2 > 1e-10)   # kicked cells alone in a stratum carry no information (w = 0)
            if kc.any():
                with np.errstate(invalid="ignore", divide="ignore"):
                    r = part[kc] / xa[kc]
                kick_rows.append(pl.DataFrame({
                    "day": days_all[kc].astype(np.int32), "row": base.row[sel][kc].astype(np.int32),
                    "agent": base.agent[sel][kc].astype(np.int32), "minute": base.minute[sel][kc].astype(np.int32),
                    "cls": [classes[j]] * int(kc.sum()), "K": Xs[kc, j].astype(np.int32),
                    "r": r.astype(np.float64), "w": (xa[kc] ** 2).astype(np.float64)}))
    nk = {c: int(X[sel][:, j].sum()) for j, c in enumerate(classes)}
    kr = pl.concat(kick_rows) if kick_rows else pl.DataFrame(schema={"day": pl.Int32, "row": pl.Int32, "agent": pl.Int32,
                                                                     "minute": pl.Int32, "cls": pl.Utf8, "K": pl.Int32,
                                                                     "r": pl.Float64, "w": pl.Float64})
    return ActFit(tuple(classes), beta, se, nk, dA, dB, dse, udays, kr, outcome)


def boot_weights(n_days: int, B: int = 1000, seed: int = SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    w = rng.multinomial(n_days, np.full(n_days, 1 / n_days), size=B).astype(float)
    return np.vstack([np.ones((1, n_days)), w])


def ci(x, q=(2.5, 97.5)):
    x = np.asarray(x, float)
    b = x[1:][np.isfinite(x[1:])]
    lo, hi = (np.percentile(b, q) if len(b) > 10 else (np.nan, np.nan))
    return [float(x[0]), float(lo), float(hi)]


def period_ci(fit: ActFit, W: np.ndarray) -> dict:
    """Day-block bootstrap of chi_c = sum_d w_d A_d / sum_d w_d B_d (nuisance terms fixed)."""
    out = {}
    for j, c in enumerate(fit.classes):
        A = np.nan_to_num(fit.day_A[:, j]); B = fit.day_B[:, j]
        if B.sum() <= 0:
            continue
        with np.errstate(invalid="ignore", divide="ignore"):
            out[c] = ci((W @ A) / (W @ B))
        out[c + "_n"] = fit.n_kicks.get(c, 0)
        out[c + "_se_cluster"] = float(fit.se[j]) if np.isfinite(fit.se[j]) else None
    return out


def daily_activity(fit: ActFit) -> pl.DataFrame:
    rows = []
    kc = fit.kick_r.group_by("day", "cls").agg(pl.col("K").sum().alias("n")) if fit.kick_r.height else None
    nmap = {(d, c): n for d, c, n in kc.iter_rows()} if kc is not None else {}
    for i, d in enumerate(fit.days):
        for j, c in enumerate(fit.classes):
            n = nmap.get((int(d), c), 0)
            if n == 0:
                continue
            with np.errstate(invalid="ignore", divide="ignore"):
                est = fit.day_A[i, j] / fit.day_B[i, j]
            rows.append((int(d), c, int(n), float(est), float(fit.day_se[i, j])))
    return pl.DataFrame(rows, schema=["day", "cls", "n", "chi", "se"], orient="row")


def day_swap(kicks: pl.DataFrame, presence: dict, rng: np.random.Generator) -> pl.DataFrame:
    """Move each agent's kicks to a random other day where the agent is present (same minute, same class).
    presence: day -> {agent: row}. Kicks whose minute falls outside the new day are dropped."""
    days = sorted(presence)
    out = []
    for (a,), g in kicks.group_by(["agent"]):
        avail = [d for d in days if a in presence[d]]
        if len(avail) < 2:
            continue
        perm = dict(zip(avail, np.roll(rng.permutation(avail), 1)))
        for d0, gg in g.group_by(["day"]):
            d1 = perm.get(d0[0])
            if d1 is None:
                continue
            out.append(gg.with_columns(pl.lit(d1, dtype=pl.Int32).alias("day"),
                                       pl.lit(presence[d1][a], dtype=pl.Int32).alias("row")))
    return pl.concat(out) if out else kicks.head(0)


# =============================================================================== generic core: content channel

def unit(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.where(n > 0, n, 1)


def pre_post_means(stmt_t: dict, stmt_v: dict, pairs: pl.DataFrame, win: float = CON_WIN_S, kmax: int = CON_KMAX,
                   basis_win: float = 7200.0, basis_kmax: int = 8):
    """pairs: agent, ts (kick time, epoch s). stmt_t[a]: sorted epoch s; stmt_v[a]: (n, d) unit vectors.
    Returns P (pre mean), Q (post mean), n_pre, n_post and B: (n, d, d) projector onto the orthogonal complement of the
    span of the pre statements; S holds the pre statements used for the orthogonal basis (last basis_kmax within
    basis_win; rows without statements have NaN means)."""
    n = pairs.height
    d = next(iter(stmt_v.values())).shape[1] if stmt_v else 32
    P = np.full((n, d), np.nan, np.float32); Q = np.full((n, d), np.nan, np.float32)
    npre = np.zeros(n, np.int16); npost = np.zeros(n, np.int16)
    S = np.full((n, basis_kmax, d), np.nan, np.float32)
    for i, (a, t) in enumerate(pairs.select("agent", "ts").iter_rows()):
        if a not in stmt_t:
            continue
        T = stmt_t[a]
        lo = np.searchsorted(T, t - win, "left"); mid_l = np.searchsorted(T, t, "left")
        mid_r = np.searchsorted(T, t, "right"); hi = np.searchsorted(T, t + win, "right")
        pre = np.arange(max(lo, mid_l - kmax), mid_l)
        post = np.arange(mid_r, min(hi, mid_r + kmax))
        if len(pre):
            P[i] = stmt_v[a][pre].mean(0); npre[i] = len(pre)
            blo = np.searchsorted(T, t - basis_win, "left")
            bas = np.arange(max(blo, mid_l - basis_kmax), mid_l)
            S[i, :len(bas)] = stmt_v[a][bas]
        if len(post):
            Q[i] = stmt_v[a][post].mean(0); npost[i] = len(post)
    return P, Q, npre, npost, S


def _orth_basis(Si: np.ndarray) -> np.ndarray:
    """Orthonormal basis (k, d) of the span of the non-NaN rows of Si."""
    X = Si[np.isfinite(Si).all(1)]
    if len(X) == 0:
        return np.zeros((0, Si.shape[1]))
    q, r = np.linalg.qr(X.T.astype(np.float64))
    keep = np.abs(np.diag(r)) > 1e-6
    return q[:, keep].T


def content_scores(pairs: pl.DataFrame, P: np.ndarray, Q: np.ndarray, U: np.ndarray, msg_meta: pl.DataFrame,
                   S: np.ndarray | None = None, n_match: int = N_MATCH, same_target_min: int = 10,
                   rng: np.random.Generator | None = None) -> pl.DataFrame:
    """Placebo-referenced content susceptibility per kick pair (several estimators; the card names the primary).

    pairs: pair, msg (row into U), agent, day, kind ('nudge'/'human'); P, Q per pair; S pre statements (for orth).
    msg_meta: msg, day, kind, targets. Pool: same kind, other day; for nudges, nudges naming the pair's agent when
    >= same_target_min exist.
      chi       matched: d_true - mean d over the n_match placebos closest in pre-alignment a_pre
      chi_unm   unmatched: d_true - mean d over the whole pool
      chi_reg   regression-adjusted: d_true - (a + b a_pre_true), (a, b) fitted on the pool's (a_pre, d)
      chi_orth  orthogonalized: directions projected off the span of the pre statements; Q.u_perp(true) minus the pool
                mean of Q.u_perp(placebo)  (removes alignment that the message shares with the agent's recent text)
      *_null    the same statistic with a random pool message treated as the true one (pseudo-true null)"""
    rng = rng or np.random.default_rng(SEED)
    keys = ("chi", "chi_unm", "chi_reg", "chi_orth", "d_true", "a_pre", "a_post", "chi_null", "chi_reg_null",
            "chi_orth_null", "match_gap", "u_perp_norm")
    out = {k: np.full(pairs.height, np.nan) for k in keys}
    mm = msg_meta.sort("msg")
    m_day = dict(zip(mm["msg"].to_list(), mm["day"].to_list()))
    kinds = mm["kind"].to_numpy(); mdays = mm["day"].to_numpy(); mids = mm["msg"].to_numpy()
    tgts = mm["targets"].to_list()
    hasU = np.isfinite(U).all(1)
    ok = np.isfinite(P).all(1) & np.isfinite(Q).all(1)
    tgt_sets = [set(t or []) for t in tgts]
    for i, (msg, agent, kind) in enumerate(pairs.select("msg", "agent", "kind").iter_rows()):
        if not ok[i] or not hasU[msg]:
            continue
        d0 = m_day[msg]
        pool = (kinds == kind) & (mdays != d0) & hasU[mids]
        if kind == "nudge":
            same = pool & np.array([agent in t for t in tgt_sets])
            if same.sum() >= same_target_min:
                pool = same
        pidx = mids[pool]
        if len(pidx) < n_match + 1:
            continue
        u = U[msg]; dv = Q[i] - P[i]
        a_t = float(u @ P[i]); d_t = float(u @ dv)
        Up = U[pidx]
        a_p = Up @ P[i]; d_p = Up @ dv
        o = np.argsort(np.abs(a_p - a_t))[:n_match]
        out["chi"][i] = d_t - d_p[o].mean(); out["chi_unm"][i] = d_t - d_p.mean()
        out["d_true"][i] = d_t; out["a_pre"][i] = a_t; out["a_post"][i] = float(u @ Q[i])
        out["match_gap"][i] = float(np.abs(a_p[o] - a_t).mean())
        A = np.column_stack([np.ones(len(a_p)), a_p])
        coef = np.linalg.lstsq(A, d_p, rcond=None)[0]
        out["chi_reg"][i] = d_t - (coef[0] + coef[1] * a_t)
        j = rng.integers(len(pidx))
        rest = np.delete(np.arange(len(pidx)), j)
        o2 = rest[np.argsort(np.abs(a_p[rest] - a_p[j]))[:n_match]]
        out["chi_null"][i] = d_p[j] - d_p[o2].mean()
        A2 = A[rest]; c2 = np.linalg.lstsq(A2, d_p[rest], rcond=None)[0]
        out["chi_reg_null"][i] = d_p[j] - (c2[0] + c2[1] * a_p[j])
        if S is not None:
            Bq = _orth_basis(S[i])
            def perp(V):
                V = np.atleast_2d(V).astype(np.float64)
                Vp = V - (V @ Bq.T) @ Bq if len(Bq) else V
                nrm = np.linalg.norm(Vp, axis=1, keepdims=True)
                return Vp / np.where(nrm > 1e-9, nrm, 1), nrm.ravel()
            ut, nt = perp(u)
            upl, _ = perp(Up)
            q_t = float(ut[0] @ Q[i]); q_p = upl @ Q[i]
            out["chi_orth"][i] = q_t - q_p.mean(); out["u_perp_norm"][i] = float(nt[0])
            out["chi_orth_null"][i] = q_p[j] - q_p[rest].mean()
    return pairs.with_columns(**{k: pl.Series(v) for k, v in out.items()})


def daily_mean(df: pl.DataFrame, col: str, by=("day", "cls")) -> pl.DataFrame:
    return (df.filter(pl.col(col).is_not_nan() & pl.col(col).is_not_null()).group_by(list(by))
            .agg(pl.len().alias("n"), pl.col(col).mean().alias("chi"),
                 (pl.col(col).std() / pl.len().sqrt()).alias("se")).sort(list(by)))


def boot_mean_by_day(df: pl.DataFrame, col: str, days: np.ndarray, W: np.ndarray) -> list:
    g = (df.filter(pl.col(col).is_not_nan() & pl.col(col).is_not_null()).group_by("day")
         .agg(pl.col(col).sum().alias("s"), pl.len().alias("n")))
    S = np.zeros(len(days)); N = np.zeros(len(days))
    pos = {int(d): i for i, d in enumerate(days)}
    for d, s, n in g.iter_rows():
        if int(d) in pos:
            S[pos[int(d)]] = s; N[pos[int(d)]] = n
    if N.sum() == 0:
        return [np.nan, np.nan, np.nan]
    with np.errstate(invalid="ignore", divide="ignore"):
        return ci((W @ S) / (W @ N))


# =============================================================================== stability of a daily series

def stability(daily: pl.DataFrame, min_n: int = 3, min_days: int = 4, kick_values: pl.DataFrame | None = None,
              value_col: str = "r", weight_col: str | None = "w", n_perm: int = 500, seed: int = SEED) -> dict:
    """Heterogeneity and reliability of a daily gauge (columns day, n, chi, se).

    kick_values (optional): per-kick values (day, value_col, weight_col) for the permutation Q test and split-half."""
    d = daily.filter((pl.col("n") >= min_n) & pl.col("chi").is_finite() & pl.col("se").is_finite() & (pl.col("se") > 0)).sort("day")
    k = d.height
    res = {"n_days_eligible": k}
    if k < min_days:
        res["verdict"] = "too few days"
        return res
    x = d["chi"].to_numpy(); s = d["se"].to_numpy(); n = d["n"].to_numpy()
    w = 1 / s ** 2
    mu = float((w * x).sum() / w.sum())
    Q = float((w * (x - mu) ** 2).sum()); df_ = k - 1
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - df_) / c)
    med_se2 = float(np.median(s ** 2))
    res.update({"mean_ivw": mu, "Q": Q, "df": df_, "p_Q": float(stats.chi2.sf(Q, df_)), "tau2": tau2,
                "tau": float(np.sqrt(tau2)), "median_se": float(np.sqrt(med_se2)),
                "R1": tau2 / (tau2 + med_se2) if (tau2 + med_se2) > 0 else np.nan,
                "sd_daily": float(np.std(x, ddof=1)), "median_n": float(np.median(n))})
    sig_kick2 = float(np.median(s ** 2 * n))
    res["kicks_for_R05"] = (sig_kick2 / tau2) if tau2 > 0 else None
    res["kicks_for_R08"] = (4 * sig_kick2 / tau2) if tau2 > 0 else None
    if k >= 5:
        res["lag1"] = float(np.corrcoef(x[:-1], x[1:])[0, 1])
        # lag-1 permutation p (shuffle day order)
        rng = np.random.default_rng(seed)
        null = np.array([np.corrcoef(*(lambda y: (y[:-1], y[1:]))(rng.permutation(x)))[0, 1] for _ in range(n_perm)])
        res["p_lag1"] = float((np.sum(null >= res["lag1"]) + 1) / (n_perm + 1))
    if kick_values is not None and kick_values.height:
        kv = kick_values.filter(pl.col("day").is_in(d["day"].implode()) & pl.col(value_col).is_finite())
        if weight_col and weight_col in kv.columns:
            kv = kv.filter(pl.col(weight_col) > 0)
        vals = kv[value_col].to_numpy(); dd = kv["day"].to_numpy()
        ww = kv[weight_col].to_numpy() if weight_col and weight_col in kv.columns else np.ones(len(vals))
        rng = np.random.default_rng(seed + 1)
        gm = np.average(vals, weights=ww)

        def spread(lbl):
            u = np.unique(lbl)
            m_ = np.array([np.average(vals[lbl == q], weights=ww[lbl == q]) for q in u])
            nn = np.array([(lbl == q).sum() for q in u])
            return np.sum(nn * (m_ - gm) ** 2)

        def dmeans(lbl):
            u = np.unique(lbl)
            return np.array([np.average(vals[lbl == q], weights=ww[lbl == q]) for q in u])

        cl = kv["cluster"].to_numpy() if "cluster" in kv.columns else None
        grp = kv["agent"].to_numpy() if "agent" in kv.columns else None
        schemes = {"kick": None}
        if cl is not None:
            schemes["msg"] = "msg"
        if grp is not None:
            schemes["agent"] = "agent"

        def perm_labels(scheme):
            if scheme is None:
                return rng.permutation(dd)
            if scheme == "msg":   # whole messages move between days (recipients of one message stay together)
                uc, inv = np.unique(cl, return_inverse=True)
                cday = np.zeros(len(uc), dd.dtype); cday[inv] = dd
                return rng.permutation(cday)[inv]
            out_ = dd.copy()       # within-agent: an agent's kicks move between its own days (composition held)
            for g_ in np.unique(grp):
                ix = np.nonzero(grp == g_)[0]
                out_[ix] = rng.permutation(dd[ix])
            return out_

        obs = spread(dd)
        v_obs = float(np.var(dmeans(dd), ddof=1))
        res["var_daily_obs"] = v_obs
        for name, sch in schemes.items():
            perms = [perm_labels(sch) for _ in range(n_perm)]
            null = np.array([spread(pp) for pp in perms])
            sfx = "" if name == "kick" else f"_{name}"
            res["p_perm" + sfx] = float((np.sum(null >= obs) + 1) / (n_perm + 1))
            v_null = float(np.mean([np.var(dmeans(pp), ddof=1) for pp in perms[:200]]))
            res["var_daily_null" + sfx] = v_null
            res["tau2_perm" + sfx] = max(0.0, v_obs - v_null)
            res["R1_perm" + sfx] = max(0.0, 1 - v_null / v_obs) if v_obs > 0 else np.nan
            nbar = float(np.mean([(dd == q).sum() for q in np.unique(dd)]))
            res["kicks_for_R05_perm" + sfx] = (v_null * nbar / res["tau2_perm" + sfx]) if res["tau2_perm" + sfx] > 0 else None
        # split-half (odd/even kicks within day, in time order of rows)
        a_, b_ = [], []
        for q in np.unique(dd):
            v = vals[dd == q]; wq = ww[dd == q]
            if len(v) >= 4:
                a_.append(np.average(v[0::2], weights=wq[0::2])); b_.append(np.average(v[1::2], weights=wq[1::2]))
        if len(a_) >= 4:
            r = float(np.corrcoef(a_, b_)[0, 1])
            res["split_half_r"] = r
            res["split_half_SB"] = 2 * r / (1 + r) if r > -1 else np.nan
            res["split_half_days"] = len(a_)
    return res


def window_reliability(daily: pl.DataFrame, w: int, min_n: int = 3) -> dict:
    """Re-pool a daily series into consecutive w-day blocks (inverse-variance) and recompute tau2 / reliability."""
    d = daily.filter(pl.col("chi").is_finite() & pl.col("se").is_finite() & (pl.col("se") > 0)).sort("day")
    if d.height < 2 * w:
        return {"w": w, "blocks": 0}
    x = d["chi"].to_numpy(); s = d["se"].to_numpy(); n = d["n"].to_numpy()
    blocks = np.arange(d.height) // w
    bx, bs, bn = [], [], []
    for b in np.unique(blocks):
        m_ = blocks == b
        if n[m_].sum() < min_n:
            continue
        ww = 1 / s[m_] ** 2
        bx.append((ww * x[m_]).sum() / ww.sum()); bs.append(np.sqrt(1 / ww.sum())); bn.append(n[m_].sum())
    bd = pl.DataFrame({"day": np.arange(len(bx)), "chi": bx, "se": bs, "n": bn})
    st = stability(bd, min_n=min_n, min_days=3)
    return {"w": w, "blocks": len(bx), "R": st.get("R1"), "p_Q": st.get("p_Q"), "tau": st.get("tau"),
            "median_se": st.get("median_se")}


def wls_slope(y: np.ndarray, x: np.ndarray, w: np.ndarray, groups: np.ndarray | None = None, clusters: np.ndarray | None = None,
              Z: np.ndarray | None = None) -> dict:
    """Weighted LS slope of y on x with optional group fixed effects (demeaned) and extra covariates Z; cluster SE."""
    ok = np.isfinite(y) & np.isfinite(x) & np.isfinite(w) & (w > 0)
    y, x, w = y[ok], x[ok], w[ok]
    cols = [x]
    if Z is not None:
        Zk = Z[ok]
        cols += [Zk[:, j] for j in range(Zk.shape[1])]
    Xm = np.column_stack(cols)
    if groups is not None:
        g = groups[ok]
        _, gi = np.unique(g, return_inverse=True)
        sw = np.bincount(gi, weights=w)
        def dm(v):
            return v - (np.bincount(gi, weights=w * v) / sw)[gi]
        y = dm(y); Xm = np.column_stack([dm(Xm[:, j]) for j in range(Xm.shape[1])])
    else:
        Xm = np.column_stack([np.ones(len(y)), Xm])
    if len(y) < Xm.shape[1] + 3:
        return {"n": int(len(y))}
    sw_ = np.sqrt(w)
    A = Xm * sw_[:, None]; b = y * sw_
    XtX = A.T @ A
    try:
        beta = np.linalg.solve(XtX, A.T @ b)
    except np.linalg.LinAlgError:
        return {"n": int(len(y))}
    e = b - A @ beta
    Xi = np.linalg.pinv(XtX)
    if clusters is not None:
        cl = clusters[ok]
        _, ci_ = np.unique(cl, return_inverse=True)
        G = np.zeros((ci_.max() + 1, A.shape[1])); np.add.at(G, ci_, A * e[:, None])
        V = Xi @ (G.T @ G) @ Xi
    else:
        V = Xi * (e @ e) / max(1, len(y) - A.shape[1])
    j = 0 if groups is not None else 1
    sl, se = float(beta[j]), float(np.sqrt(V[j, j]))
    return {"n": int(len(y)), "slope": sl, "se": se, "lo": sl - 1.96 * se, "hi": sl + 1.96 * se,
            "p": float(2 * stats.norm.sf(abs(sl / se))) if se > 0 else np.nan}


# =============================================================================== village loaders

def calendar() -> pl.DataFrame:
    return pl.read_parquet(SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.Utf8))


def is_holdout_date(d: str, goal_no) -> bool:
    if goal_no is not None and int(goal_no) in set(HOLDOUT["goal_periods_held_out"]):
        return True
    return any(w["start"] <= d < w["end"] for w in HOLDOUT["ne_windows"])


def period_days(goal_no: int, allow_holdout: bool = False, date_from: str | None = None, date_to: str | None = None) -> list[str]:
    c = calendar().filter((pl.col("goal_no") == goal_no) & (pl.col("window_s") > 0))
    if date_from:
        c = c.filter(pl.col("pt_date") >= date_from)
    if date_to:
        c = c.filter(pl.col("pt_date") < date_to)
    out = []
    for d, g, h in c.select("pt_date", "goal_no", "holdout").iter_rows():
        if (bool(h) or is_holdout_date(d, g)) and not allow_holdout:
            continue
        out.append(d)
    return sorted(out)


def assert_no_holdout(days: list[str]):
    cal = calendar().filter(pl.col("pt_date").is_in(days))
    bad = [d for d, g, h in cal.select("pt_date", "goal_no", "holdout").iter_rows() if h or is_holdout_date(d, g)]
    if bad:
        raise RuntimeError(f"holdout leak: {bad[:5]} ({len(bad)} days)")


def load_panels(days: list[str], allow_holdout: bool = False) -> tuple[list[Panel], dict]:
    if not allow_holdout:
        assert_no_holdout(days)
    cal = calendar().filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    goal_first = {}
    ab = (pl.scan_parquet(SH / "activity_bins.parquet").filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "minute", "agent", "state").collect().sort("pt_date", "agent", "minute"))
    meta = {r["pt_date"]: r for r in cal.iter_rows(named=True)}
    panels = []
    for k, d in enumerate(sorted(days)):
        g = ab.filter(pl.col("pt_date") == d)
        if g.height == 0:
            continue
        agents = np.unique(g["agent"].to_numpy())
        nm = int(g["minute"].max()) + 1
        st = np.ones((len(agents), nm), np.int8)
        st[np.searchsorted(agents, g["agent"].to_numpy()), g["minute"].to_numpy()] = g["state"].to_numpy()
        act = (st >= 3).astype(np.int8); idle = (st == 2).astype(np.int8)
        pres = act.any(1)
        gn = int(meta[d]["goal_no"] or 0)
        goal_first.setdefault(gn, k)
        panels.append(Panel(day=k, act=act[pres], idle=idle[pres], agents=agents[pres].astype(int), label=d))
    # goal-day index = ordinal among ALL active days of the goal (including any holdout days before it)
    full = calendar().filter(pl.col("window_s") > 0).sort("pt_date")
    for p in panels:
        gn = int(meta[p.label]["goal_no"] or 0)
        gd = full.filter(pl.col("goal_no") == gn)["pt_date"].to_list()
        p.goal_day = gd.index(p.label)
    return panels, meta


def load_operator_messages(days: list[str]) -> pl.DataFrame:
    """Human and automated messages on `days`: kind (human / nudge / bookend), named roster agents, room recipients,
    embedding row. Same class rules as H04 (nudge = automated naming >= 1 roster agent), with the clean mentions."""
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "regime", "room",
                                                               "speaker_kind", "length"]).with_row_index("msg")
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["mentions_roster"])
    chat = chat.with_columns(men["mentions_roster"].alias("named"))
    chat = chat.filter(pl.col("pt_date").is_in(days) & pl.col("speaker_kind").cast(pl.Utf8).is_in(["human", "automated"]))
    exp = (pl.read_parquet(SH / "exposure.parquet").filter(pl.col("msg").is_in(chat["msg"].implode()))
           .group_by("msg").agg(pl.col("agent").alias("recipients")))
    emb = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("emb_row")
    m = chat.join(exp, on="msg", how="left").join(emb, on="message_id", how="left")
    m = m.with_columns(pl.col("named").fill_null(pl.lit([], dtype=pl.List(pl.Int8))),
                       pl.col("recipients").fill_null(pl.lit([], dtype=pl.List(pl.Int8))))
    m = m.with_columns(pl.when(pl.col("speaker_kind").cast(pl.Utf8) == "human").then(pl.lit("human"))
                       .when(pl.col("named").list.len() > 0).then(pl.lit("nudge")).otherwise(pl.lit("bookend")).alias("kind"))
    return m.select("msg", "message_id", "t", "pt_date", "goal_no", "regime", "room", "kind", "named", "recipients",
                    "length", "emb_row")


def build_kicks(panels: list[Panel], msgs: pl.DataFrame) -> pl.DataFrame:
    """One row per (message, recipient present that day): day, row, agent, minute, cls, msg, ts."""
    cal = calendar()
    wstart = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    pidx = {p.label: p for p in panels}
    rows = []
    for r in msgs.filter(pl.col("kind") != "bookend").iter_rows(named=True):
        p = pidx.get(r["pt_date"])
        if p is None:
            continue
        minute = int((r["t"] - wstart[r["pt_date"]]).total_seconds() // 60)
        if minute < 0 or minute >= p.n_min:
            continue
        named = set(int(x) for x in r["named"])
        rec = set(int(x) for x in r["recipients"]) | (named if r["kind"] == "nudge" else set())
        amap = {int(a): i for i, a in enumerate(p.agents)}
        for a in rec:
            if a not in amap:
                continue
            if r["kind"] == "nudge":
                cls = "N_tgt" if a in named else "N_by"
            else:
                cls = "H_men" if a in named else "H_und"
            rows.append((p.day, amap[a], a, minute, cls, int(r["msg"]), r["kind"], r["t"].timestamp(), p.label))
    return pl.DataFrame(rows, schema={"day": pl.Int32, "row": pl.Int32, "agent": pl.Int32, "minute": pl.Int32,
                                      "cls": pl.Utf8, "msg": pl.Int64, "kind": pl.Utf8, "ts": pl.Float64,
                                      "pt_date": pl.Utf8}, orient="row")


def context_fill(kicks: pl.DataFrame, regime: str) -> pl.DataFrame:
    """Turns since the target's last context reset, and the prompt size of its last turn, at each kick."""
    ags = kicks["agent"].unique().to_list()
    t0 = kicks["ts"].min() - 3 * 86400; t1 = kicks["ts"].max() + 60
    lo = dt.datetime.fromtimestamp(t0, dt.timezone.utc); hi = dt.datetime.fromtimestamp(t1, dt.timezone.utc)
    acts = (pl.scan_parquet(SH / "actions.parquet").filter(pl.col("agent").is_in(ags) & (pl.col("t") >= lo) & (pl.col("t") <= hi))
            .filter(~pl.col("action").cast(pl.Utf8).is_in(list(MIRROR)))
            .select("agent", (pl.col("t").dt.epoch("us") / 1e6).alias("ts"),
                    (pl.col("tok_in").fill_null(0) + pl.col("tok_cache_read").fill_null(0) + pl.col("tok_cache_write").fill_null(0)).alias("ptok"),
                    pl.col("tok_in").is_not_null().alias("has_tok")).collect().sort("agent", "ts"))
    reset_type = "CONSOLIDATE" if regime == "III" else "START_USING_COMPUTER"
    ev = (pl.scan_parquet(SH / "events_core.parquet").filter(pl.col("agent").is_in(ags) & (pl.col("t") >= lo) & (pl.col("t") <= hi)
                                                              & (pl.col("action_type").cast(pl.Utf8) == reset_type))
          .select("agent", (pl.col("t").dt.epoch("us") / 1e6).alias("ts")).collect().sort("agent", "ts"))
    A = {a: g for (a,), g in acts.group_by(["agent"])}
    R = {a: g["ts"].to_numpy() for (a,), g in ev.group_by(["agent"])}
    fill = np.full(kicks.height, np.nan); ptok = np.full(kicks.height, np.nan); since_reset_s = np.full(kicks.height, np.nan)
    for i, (a, t) in enumerate(kicks.select("agent", "ts").iter_rows()):
        rs = R.get(a)
        g = A.get(a)
        if rs is None or g is None:
            continue
        j = np.searchsorted(rs, t, "right") - 1
        if j < 0:
            continue
        tr = rs[j]
        at = g["ts"].to_numpy()
        fill[i] = np.searchsorted(at, t, "right") - np.searchsorted(at, tr, "right")
        since_reset_s[i] = t - tr
        k = np.searchsorted(at, t, "right") - 1
        ht = g["has_tok"].to_numpy(); pt = g["ptok"].to_numpy()
        while k >= 0 and at[k] > tr - 1 and not ht[k]:
            k -= 1
        if k >= 0 and ht[k] and at[k] > t - 1800:
            ptok[i] = pt[k]
    return kicks.with_columns(pl.Series("fill", fill), pl.Series("ptok", ptok), pl.Series("since_reset_s", since_reset_s))


def cell_fill_phase(base: Base, panels: list[Panel], regime: str, edges=(14, 28)) -> np.ndarray:
    """Per cell: phase of the agent's context cycle at the start of minute m (turns since its last reset, counting
    `actions` rows except mirror turns): 0 = 0-13, 1 = 14-27, 2 = 28+, 3 = unknown. Uses the calendar window start."""
    cal = calendar()
    wstart = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    ags = sorted({int(a) for p in panels for a in p.agents})
    t_lo = min(wstart[p.label] for p in panels) - dt.timedelta(days=4)
    t_hi = max(wstart[p.label] for p in panels) + dt.timedelta(days=1)
    acts = (pl.scan_parquet(SH / "actions.parquet").filter(pl.col("agent").is_in(ags) & (pl.col("t") >= t_lo) & (pl.col("t") <= t_hi))
            .filter(~pl.col("action").cast(pl.Utf8).is_in(list(MIRROR)))
            .select("agent", (pl.col("t").dt.epoch("us") / 1e6).alias("ts")).collect().sort("agent", "ts"))
    reset_type = "CONSOLIDATE" if regime == "III" else "START_USING_COMPUTER"
    ev = (pl.scan_parquet(SH / "events_core.parquet").filter(pl.col("agent").is_in(ags) & (pl.col("t") >= t_lo) & (pl.col("t") <= t_hi)
                                                              & (pl.col("action_type").cast(pl.Utf8) == reset_type))
          .select("agent", (pl.col("t").dt.epoch("us") / 1e6).alias("ts")).collect().sort("agent", "ts"))
    A = {a: g["ts"].to_numpy() for (a,), g in acts.group_by(["agent"])}
    Rz = {a: g["ts"].to_numpy() for (a,), g in ev.group_by(["agent"])}
    ph = np.full(len(base.Y), 3, np.int8)
    for p in panels:
        start, m = base.offsets[p.day]
        if len(m) == 0:
            continue
        t0 = wstart[p.label].timestamp()
        tm = t0 + 60.0 * m
        for i, a in enumerate(p.agents):
            a = int(a)
            if a not in A or a not in Rz:
                continue
            at, rs = A[a], Rz[a]
            j = np.searchsorted(rs, tm, "right") - 1
            okr = j >= 0
            tr = np.where(okr, rs[np.clip(j, 0, None)], np.nan)
            fill = np.searchsorted(at, tm, "right") - np.searchsorted(at, np.nan_to_num(tr, nan=-1e18), "right")
            b = np.where(~okr, 3, np.digitize(fill, edges)).astype(np.int8)
            ph[start + i * len(m): start + (i + 1) * len(m)] = b
    return ph


def load_statements(days: list[str], regime: str, allow_holdout: bool = False):
    """Whitened (32-d), normalized statement vectors per agent for `days` (+/- 1 h margins are inside days)."""
    if not allow_holdout:
        assert_no_holdout(days)
    from common import load_whitener
    st = pl.read_parquet(SH / "embeddings/statements.parquet").filter(pl.col("pt_date").is_in(days))
    Ec = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(SH / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    W = load_whitener(regime, 32)
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy()
    E = np.empty((st.height, Ec.shape[1]), np.float32)
    mc = kind == "chat"
    E[mc] = Ec[np.sort(src[mc])][np.argsort(np.argsort(src[mc]))] if mc.any() else E[mc]
    E[~mc] = Ei[np.sort(src[~mc])][np.argsort(np.argsort(src[~mc]))] if (~mc).any() else E[~mc]
    V = unit(W(E)).astype(np.float32)
    ts = (st["t"].dt.epoch("us") / 1e6).to_numpy()
    ag = st["agent"].to_numpy()
    stmt_t, stmt_v = {}, {}
    for a in np.unique(ag):
        m = ag == a
        o = np.argsort(ts[m])
        stmt_t[int(a)] = ts[m][o]; stmt_v[int(a)] = V[m][o]
    return stmt_t, stmt_v, st.height


def message_vectors(msgs: pl.DataFrame, regime: str) -> np.ndarray:
    """(max msg + 1, 32) whitened unit vectors indexed by msg (rows without an embedding stay NaN)."""
    from common import load_whitener
    Ec = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    W = load_whitener(regime, 32)
    m = msgs.filter(pl.col("emb_row").is_not_null())
    U = np.full((int(msgs["msg"].max()) + 1, 32), np.nan, np.float32)
    rows = m["emb_row"].to_numpy()
    o = np.argsort(rows)
    E = np.asarray(Ec[rows[o]], np.float32)
    U[m["msg"].to_numpy()[o]] = unit(W(E))
    return U


# =============================================================================== provenance / io

def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "hypotheses/H30-operator-susceptibility"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted-H30" if dirty.strip() else "")


def write_provenance(folder: Path, built_by: str, tables: list[str], params: dict):
    rev = None
    try:
        sp = json.loads((SH / "_provenance.json").read_text())
        for v in sp.values():
            if isinstance(v, dict) and isinstance(v.get("inputs"), dict) and v["inputs"].get("revision"):
                rev = v["inputs"]["revision"]
                break
    except Exception:
        pass
    prov = {"built_by": built_by, "git_commit": git_commit(),
            "inputs": [{"source": "ai-village (via data/processed/shared)", "revision": rev, "tables": tables}],
            "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, np.floating):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.bool_):
            return bool(o)
        return str(o)
    txt = json.dumps(obj, default=conv, indent=1, allow_nan=True)
    txt = txt.replace("NaN", "null").replace("-Infinity", "null").replace("Infinity", "null")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt)
