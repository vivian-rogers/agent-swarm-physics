"""H42 round 2 (R2, R1): call-level two-layer design on the recipient's call clock.

Layer 1 = the call skeleton (call starts: chains, timers, the chat-mode schedule). Layer 2 = the mark of each call
(talk, tool, timer pause, session start / stop). A read can change call timing only through the reading call's own
decision, so every outcome here is decided by call c after it reads.

Per receiving call c of agent i (all-present window, with a previous receiving call):
  w_c   = clip(min(t_first - t_call, t_call - t_prev, 120 s), 1 s)        (symmetric matched window)
  Rm_X  = agent items of class X read at c, posted in (t_c - w_c, t_c)
  P_X   = agent items of class X for i posted in (t_c, t_c + w_c)          (in flight at c, read later)
  J_O,X = beta(Rm_X) - beta(P_X)   (OLS within agent x day x call-class cells; 1-h block bootstrap)
Classes: cold (named, no exchange in progress), thrn (named, in an exchange), un (unnamed). named = cold + thrn.

Call-skeleton null and synthetic worlds: messages are regenerated on the real call skeleton (each receiving call talks
with its agent x day x class rate, a talking call posts at its real t_first, recipients = other agents in the sender's
room, read at their first receiving call after the post).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H42-readout-hawkes-kernel"
R2 = DATA / "round2"
CLASSES = ("cold", "thrn", "un")
WMAX = 120.0
FIELD_BIN = 600.0


def goal_of(uid: str) -> int:
    return int("".join(ch for ch in uid if ch.isdigit()))


@dataclass
class U2:
    unit_id: str
    goal: int
    regime: str
    calls: pl.DataFrame
    items: pl.DataFrame
    talk: pl.DataFrame          # round-1 talk table (t, room) for the fitted field


def load(uid: str) -> U2:
    g = goal_of(uid)
    f = pl.col("unit_id") == uid
    calls = pl.read_parquet(R2 / f"G{g:02d}/calls.parquet").filter(f)
    items = pl.read_parquet(R2 / f"G{g:02d}/items.parquet").filter(f)
    days = pl.read_parquet(DATA / f"G{g:02d}/days.parquet").filter(f)
    talk = pl.read_parquet(DATA / f"G{g:02d}/talk.parquet").filter(f)
    return U2(uid, g, days["regime"][0], calls, items, talk)


# ============================================================================================ skeleton
@dataclass
class Skel:
    """receiving calls of the unit (all of them, sorted by day, agent, t_call, turn_id) plus row features."""
    day: np.ndarray
    agent: np.ndarray
    t: np.ndarray
    tf: np.ndarray
    te: np.ndarray
    talk: np.ndarray
    kind: np.ndarray
    ctx: np.ndarray
    wake: np.ndarray
    room: np.ndarray
    turn: np.ndarray
    t_next: np.ndarray
    ctx_next_any: np.ndarray
    cell: np.ndarray            # agent x day x class id
    ad: np.ndarray              # agent-day id
    pos: np.ndarray             # position within agent-day
    ad_start: np.ndarray        # first row index of each agent-day
    ad_len: np.ndarray


def skeleton(u: U2) -> Skel:
    rc = (u.calls.filter(pl.col("recv")).sort("day", "agent", "t_call", "turn_id")
          .with_columns(pl.col("room").fill_null(-1)))
    day = rc["day"].to_numpy().astype(np.int64)
    agent = rc["agent"].to_numpy().astype(np.int64)
    ctx = rc["ctx_mode"].to_numpy()
    wake = rc["wake"].to_numpy().astype(bool)
    adkey = day * 1000 + agent
    _, ad = np.unique(adkey, return_inverse=True)
    cls = 2 * (ctx == "cu") + wake
    _, cell = np.unique(adkey * 10 + cls, return_inverse=True)
    starts = np.flatnonzero(np.r_[True, ad[1:] != ad[:-1]])
    lens = np.diff(np.r_[starts, len(ad)])
    pos = np.arange(len(ad)) - np.repeat(starts, lens)
    tn = rc["t_next"].to_numpy()
    return Skel(day, agent, rc["t_call"].to_numpy(), rc["t_first"].to_numpy(), rc["t_end"].to_numpy(),
                rc["talk"].to_numpy().astype(float), rc["kind"].to_numpy(), ctx, wake,
                rc["room"].to_numpy().astype(np.int64), rc["turn_id"].to_numpy().astype(np.int64),
                np.where(np.isnan(tn.astype(float)), np.nan, tn.astype(float)), rc["ctx_next"].to_numpy(),
                cell, ad, pos, starts, lens)


def window_flags(sk: Skel) -> np.ndarray:
    """DQ8 all-present window per day: [max_i first t_call, min_i last t_call] over agents with >= 20 calls."""
    ok = np.zeros(len(sk.t), bool)
    for d in np.unique(sk.day):
        m = sk.day == d
        firsts, lasts = [], []
        for a in np.unique(sk.agent[m]):
            mm = m & (sk.agent == a)
            if mm.sum() >= 20:
                firsts.append(sk.t[mm].min()); lasts.append(sk.t[mm].max())
        if firsts and max(firsts) < min(lasts):
            ok |= m & (sk.t >= max(firsts)) & (sk.t <= min(lasts))
    return ok


# ============================================================================================ design rows
def item_arrays(items: pl.DataFrame):
    a = items.filter(pl.col("kind") == "agent")
    cls = np.where(a["cold"].to_numpy(), 0, np.where(a["named"].to_numpy(), 1, 2))
    return {"day": a["day"].to_numpy().astype(np.int64), "rec": a["recipient"].to_numpy().astype(np.int64),
            "turn": a["turn_id"].to_numpy().astype(np.int64), "s": a["s"].to_numpy().astype(float), "cls": cls}


def design(u: U2, sk: Skel, it: dict | None = None, exo: pl.DataFrame | None = None) -> dict:
    """call rows with read / in-flight counts. it: agent items (dict from item_arrays) — real or synthetic."""
    if it is None:
        it = item_arrays(u.items)
    n = len(sk.t)
    tprev = np.full(n, np.nan)
    has_prev = sk.pos > 0
    tprev[has_prev] = sk.t[np.flatnonzero(has_prev) - 1]
    yprev = np.full(n, np.nan)
    yprev[has_prev] = sk.talk[np.flatnonzero(has_prev) - 1]
    lat = np.maximum(sk.tf - sk.t, 0.0)
    w = np.clip(np.minimum(np.minimum(lat, np.where(has_prev, sk.t - tprev, WMAX)), WMAX), 1.0, None)
    w67 = np.clip(lat, 1.0, WMAX)
    # receiving-call index of each item
    tix = {t: k for k, t in enumerate(sk.turn)}
    rix = np.array([tix.get(t, -1) for t in it["turn"]], np.int64)
    ok = rix >= 0
    out = {}
    for name, win in (("", w), ("h67_", w67)):
        Rm = np.zeros((n, 3)); P = np.zeros((n, 3))
        sel = ok & (it["s"] > sk.t[np.maximum(rix, 0)] - win[np.maximum(rix, 0)])
        np.add.at(Rm, (rix[sel], it["cls"][sel]), 1.0)
        # in-flight: items of the recipient (same day) posted in (t_c, t_c + win)
        key_it = it["day"] * 1000 + it["rec"]
        key_c = sk.day * 1000 + sk.agent
        order = np.lexsort((it["s"], key_it))
        ks, ss, cs = key_it[order], it["s"][order], it["cls"][order]
        for c in range(3):
            mk = cs == c
            kk, sv = ks[mk], ss[mk]
            # composite sort key: key * 1e6 + s (s < 1e5 s within a day)
            comp = kk.astype(float) * 1e6 + sv
            lo = np.searchsorted(comp, key_c * 1e6 + sk.t, side="right")
            hi = np.searchsorted(comp, key_c * 1e6 + sk.t + win, side="left")
            P[:, c] = hi - lo
        out[name + "Rm"] = Rm; out[name + "P"] = P
    Rall = np.zeros((n, 3))
    np.add.at(Rall, (rix[ok], it["cls"][ok]), 1.0)
    out["Rall"] = Rall
    out["Ro"] = Rall.sum(1) - out["Rm"].sum(1)
    out["h67_Ro"] = Rall.sum(1) - out["h67_Rm"].sum(1)
    tot = Rall.sum(1)
    lag1 = np.full(n, 0.0); lag2 = np.full(n, 0.0)
    lag1[sk.pos >= 1] = tot[np.flatnonzero(sk.pos >= 1) - 1]
    lag2[sk.pos >= 2] = tot[np.flatnonzero(sk.pos >= 2) - 2]
    out["R1"], out["R2"] = lag1, lag2
    # exogenous items read at c
    ex = u.items.filter(pl.col("kind") != "agent") if exo is None else exo
    hum = np.zeros(n); nud = np.zeros(n)
    if len(ex):
        er = np.array([tix.get(t, -1) for t in ex["turn_id"].to_numpy()], np.int64)
        kd = ex["kind"].to_numpy()
        m = er >= 0
        np.add.at(hum, er[m & (kd == "human")], 1.0)
        np.add.at(nud, er[m & np.isin(kd, ["nudge", "pause_resume", "automated_other"])], 1.0)
    out["hum"], out["nud"] = hum, nud
    out["yprev"] = yprev
    out["logw"] = np.log(w); out["logw67"] = np.log(w67)
    out["loggap_prev"] = np.log(np.maximum(np.where(has_prev, sk.t - tprev, np.nan), 0.5))
    # outcomes
    gap = sk.t_next - sk.t
    out["talk"] = sk.talk.copy()
    out["pause"] = (sk.kind == "pause").astype(float)
    out["loggap"] = np.where(gap > 0, np.log(np.maximum(gap, 0.5)), np.nan)
    out["loggap_np"] = np.where(sk.kind != "pause", out["loggap"], np.nan)
    # next receiving call's context mode
    nxt = np.full(n, np.nan)
    last = np.r_[sk.ad[1:] != sk.ad[:-1], True]
    idx = np.flatnonzero(~last)
    nxt[idx] = (sk.ctx[idx + 1] == "chat").astype(float)
    out["chatnext"] = nxt
    out["start"] = np.where(sk.ctx == "chat", (sk.kind == "session_start").astype(float), np.nan)
    out["stop"] = np.where(sk.ctx == "cu", (sk.ctx_next_any == "summary").astype(float), np.nan)
    out["keep"] = has_prev & window_flags(sk)
    out["cell"] = sk.cell
    out["block"] = sk.day * 100 + np.floor(np.maximum(sk.t, 0) / 3600).astype(np.int64)
    out["fbin"] = (sk.day * 100 + np.maximum(sk.room, 0)) * 1000 + np.floor(np.maximum(sk.t, 0) / FIELD_BIN).astype(np.int64)
    return out


OUTCOMES = ("talk", "pause", "loggap", "loggap_np", "chatnext", "start", "stop")


def regressors(D: dict, spec: str):
    """spec: 'r2' (named, un), 'r1' (cold, thrn, un), 'h67' (named, un; H67 window + lagged reads)."""
    pre = "h67_" if spec.startswith("h67") else ""
    Rm, P = D[pre + "Rm"], D[pre + "P"]
    if spec in ("r1", "h67_r1"):
        cols = {"Rm_cold": Rm[:, 0], "P_cold": P[:, 0], "Rm_thrn": Rm[:, 1], "P_thrn": P[:, 1],
                "Rm_un": Rm[:, 2], "P_un": P[:, 2]}
        contr = {"cold": ("Rm_cold", "P_cold"), "thrn": ("Rm_thrn", "P_thrn"), "un": ("Rm_un", "P_un")}
    else:
        cols = {"Rm_named": Rm[:, 0] + Rm[:, 1], "P_named": P[:, 0] + P[:, 1], "Rm_un": Rm[:, 2], "P_un": P[:, 2]}
        contr = {"named": ("Rm_named", "P_named"), "un": ("Rm_un", "P_un")}
    cols.update({"Ro": D[pre + "Ro"], "hum": D["hum"], "nud": D["nud"], "yprev": D["yprev"],
                 "logw": D["logw67" if pre else "logw"], "loggap_prev": D["loggap_prev"]})
    if pre:
        cols.update({"R1": D["R1"], "R2": D["R2"]})
    names = list(cols)
    X = np.column_stack([cols[k] for k in names])
    return X, names, contr


def demean(M: np.ndarray, groups: list[np.ndarray], iters: int = 30, tol: float = 1e-9) -> np.ndarray:
    """within transformation over one or more sets of group ids (alternating projections)."""
    M = M.astype(float).copy()
    for it_ in range(iters if len(groups) > 1 else 1):
        before = M.copy() if len(groups) > 1 else None
        for g in groups:
            _, gi = np.unique(g, return_inverse=True)
            cnt = np.bincount(gi)
            for j in range(M.shape[1]):
                M[:, j] -= (np.bincount(gi, weights=M[:, j]) / cnt)[gi]
        if before is not None and np.max(np.abs(M - before)) < tol:
            break
    return M


def fit(D: dict, outcome: str, spec: str = "r2", field: bool = False, B: int = 200, seed: int = 0,
        y_override: np.ndarray | None = None) -> dict:
    """OLS within cells; contrasts J_X = beta(Rm_X) - beta(P_X); 1-h block bootstrap."""
    X, names, contr = regressors(D, spec)
    y = D[outcome] if y_override is None else y_override
    m = D["keep"] & np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    res = {"outcome": outcome, "spec": spec, "field": field, "n": int(m.sum())}
    if m.sum() < 100:
        return res
    Z = np.column_stack([y[m], X[m]])
    groups = [D["cell"][m]]
    if field:
        groups.append(D["fbin"][m])
    Z = demean(Z, groups)
    yy, XX = Z[:, 0], Z[:, 1:]
    sd = XX.std(0)
    keepc = sd > 1e-10
    XX = XX[:, keepc]
    nm = [n_ for n_, k in zip(names, keepc) if k]
    blk = D["block"][m]
    _, bi = np.unique(blk, return_inverse=True)
    nb = bi.max() + 1
    K = XX.shape[1]
    G = np.zeros((nb, K, K)); h = np.zeros((nb, K))
    for b in range(nb):
        s = bi == b
        G[b] = XX[s].T @ XX[s]; h[b] = XX[s].T @ yy[s]
    Gt, ht = G.sum(0), h.sum(0)
    try:
        beta = np.linalg.solve(Gt, ht)
    except np.linalg.LinAlgError:
        beta = np.linalg.lstsq(Gt, ht, rcond=None)[0]
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(B):
        wb = rng.multinomial(nb, np.full(nb, 1.0 / nb)).astype(float)
        try:
            draws.append(np.linalg.solve(np.tensordot(wb, G, 1), wb @ h))
        except np.linalg.LinAlgError:
            continue
    draws = np.array(draws) if draws else np.zeros((0, K))
    ix = {n_: k for k, n_ in enumerate(nm)}
    for X_, (a, b) in contr.items():
        if a in ix and b in ix:
            est = beta[ix[a]] - beta[ix[b]]
            dd = draws[:, ix[a]] - draws[:, ix[b]] if len(draws) else np.array([np.nan])
            res[f"J_{X_}"] = float(est)
            res[f"se_{X_}"] = float(np.std(dd, ddof=1)) if len(dd) > 2 else np.nan
            res[f"lo_{X_}"] = float(np.quantile(dd, 0.025)) if len(dd) > 2 else np.nan
            res[f"hi_{X_}"] = float(np.quantile(dd, 0.975)) if len(dd) > 2 else np.nan
            res[f"bRm_{X_}"] = float(beta[ix[a]]); res[f"bP_{X_}"] = float(beta[ix[b]])
            res[f"nRm_{X_}"] = float(X[m][:, names.index(a)].sum())
        else:
            res[f"J_{X_}"] = np.nan
    res["ybar"] = float(np.mean(y[m]))
    return res


# ============================================================================================ pooling
def dl_pool(est, se):
    """DerSimonian-Laird random-effects pool; returns (mu, se, lo, hi, tau2, k) and the IVW pool."""
    est = np.asarray(est, float); se = np.asarray(se, float)
    m = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[m], se[m]
    k = len(est)
    if k == 0:
        return {"k": 0}
    w = 1 / se ** 2
    mu_f = np.sum(w * est) / w.sum()
    se_f = np.sqrt(1 / w.sum())
    Q = np.sum(w * (est - mu_f) ** 2)
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - np.sum(w ** 2) / w.sum())) if k > 1 else 0.0
    wr = 1 / (se ** 2 + tau2)
    mu = np.sum(wr * est) / wr.sum()
    s = np.sqrt(1 / wr.sum())
    return {"k": k, "re": float(mu), "re_se": float(s), "re_lo": float(mu - 1.96 * s), "re_hi": float(mu + 1.96 * s),
            "tau2": float(tau2), "Q": float(Q), "ivw": float(mu_f), "ivw_se": float(se_f),
            "ivw_lo": float(mu_f - 1.96 * se_f), "ivw_hi": float(mu_f + 1.96 * se_f)}


# ============================================================================================ synthetic messages
def cell_rates(sk: Skel, v: np.ndarray) -> np.ndarray:
    """per-row cell mean of v (agent x day x class)."""
    ok = np.isfinite(v)
    s = np.bincount(sk.cell[ok], weights=v[ok], minlength=sk.cell.max() + 1)
    c = np.bincount(sk.cell[ok], minlength=sk.cell.max() + 1)
    r = np.where(c > 0, s / np.maximum(c, 1), np.nan)
    return r[sk.cell]


def room_field(u: U2, sk: Skel, sigma: float, dt: float = 10.0):
    """z(day, room, t): standardized log of the real agent-message rate in the room, Gaussian-smoothed (sigma s).
    Returns functions z_call (at receiving-call starts) and z_first (at t_first)."""
    tk = u.talk
    zc = np.zeros(len(sk.t)); zf = np.zeros(len(sk.t))
    for d in np.unique(sk.day):
        md = sk.day == d
        T = float(max(np.nanmax(sk.te[md]), np.nanmax(sk.t[md]))) + 60
        n = int(T // dt) + 2
        x = np.arange(n) * dt
        half = int(4 * sigma // dt) + 1
        ker = np.exp(-0.5 * (np.arange(-half, half + 1) * dt / sigma) ** 2)
        ker /= ker.sum()
        for r in np.unique(sk.room[md]):
            mr = md & (sk.room == r)
            tt = tk.filter((pl.col("day") == d) & (pl.col("room") == r))["t"].to_numpy()
            if len(tt) == 0:
                tt = tk.filter(pl.col("day") == d)["t"].to_numpy()
            h = np.bincount(np.clip((tt // dt).astype(int), 0, n - 1), minlength=n).astype(float) / dt
            sm = np.convolve(h, ker, mode="same")
            lz = np.log(sm + 0.1 * (h.mean() + 1e-6))
            lz = (lz - lz.mean()) / (lz.std() + 1e-9)
            zc[mr] = lz[np.clip((sk.t[mr] // dt).astype(int), 0, n - 1)]
            zf[mr] = lz[np.clip((sk.tf[mr] // dt).astype(int), 0, n - 1)]
    return zc, zf


def gen_items(sk: Skel, talk_syn: np.ndarray, shares: dict, rng) -> dict:
    """synthetic agent items: each talking receiving call posts one message at its t_first in its room; recipients are
    other agents whose current room is that room; read at the recipient's first receiving call with t_call > s."""
    out = {"day": [], "rec": [], "turn": [], "s": [], "cls": []}
    for d in np.unique(sk.day):
        md = np.flatnonzero(sk.day == d)
        snd = md[talk_syn[md] > 0]
        if len(snd) == 0:
            continue
        s = sk.tf[snd]; room = sk.room[snd]; sa = sk.agent[snd]
        for a in np.unique(sk.agent[md]):
            ma = md[sk.agent[md] == a]          # sorted by t within the agent-day
            ta = sk.t[ma]
            cur = np.searchsorted(ta, s, side="right") - 1
            croom = sk.room[ma][np.maximum(cur, 0)]
            k1 = np.searchsorted(ta, s, side="right")
            sel = (sa != a) & (croom == room) & (k1 < len(ta))
            if not sel.any():
                continue
            nsel = int(sel.sum())
            pn, pc = shares.get(a, shares["_pool"])
            named = rng.uniform(size=nsel) < pn
            cold = named & (rng.uniform(size=nsel) < pc)
            cls = np.where(cold, 0, np.where(named, 1, 2))
            out["day"].append(np.full(nsel, d)); out["rec"].append(np.full(nsel, a))
            out["turn"].append(sk.turn[ma][k1[sel]]); out["s"].append(s[sel]); out["cls"].append(cls)
    res = {}
    for k, v in out.items():
        dt_ = float if k == "s" else np.int64
        res[k] = np.concatenate(v).astype(dt_) if v else np.zeros(0, dt_)
    return res


def real_shares(u: U2) -> dict:
    a = u.items.filter(pl.col("kind") == "agent")
    g = a.group_by("recipient").agg(pl.col("named").mean().alias("pn"),
                                    (pl.col("cold").sum() / pl.col("named").sum().clip(1)).alias("pc"), pl.len())
    pool = (float(a["named"].mean()), float(a["cold"].sum() / max(a["named"].sum(), 1)))
    sh = {r["recipient"]: ((r["pn"], r["pc"]) if r["len"] >= 50 else pool) for r in g.iter_rows(named=True)}
    sh["_pool"] = pool
    return sh


def skeleton_null(u: U2, sk: Skel, rng):
    """synthetic items under the call-skeleton null (real cell talk rates, no field, no coupling)."""
    p = cell_rates(sk, sk.talk)
    talk_syn = (rng.uniform(size=len(p)) < p).astype(float)
    return gen_items(sk, talk_syn, real_shares(u), rng), talk_syn


def fitted_field_strength(D: dict, z: np.ndarray) -> float:
    """a = within-cell slope of real talk on z divided by the mean talk rate (log-link approximation), in [0, 1.5]."""
    m = D["keep"]
    Zm = demean(np.column_stack([D["talk"][m], z[m]]), [D["cell"][m]])
    b = float(Zm[:, 0] @ Zm[:, 1] / max(Zm[:, 1] @ Zm[:, 1], 1e-9))
    return float(np.clip(b / max(D["talk"][m].mean(), 1e-3), 0.0, 1.5))
