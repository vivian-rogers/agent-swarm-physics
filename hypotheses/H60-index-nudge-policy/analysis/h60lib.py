"""H60 estimator: nudge response surface at idle gates, index policies and cross-fitted direct-method policy values.

State x = (a, k, r): a = a_sus (minutes since the last sustained active run), k = k_sus (glance-robust gate index,
the TS2r analog), r = s_dir (minutes since the last directed read). Outcome models have agent fixed effects:
OLS for active calls in 30 min, logit for sustained / any escape. Shared fitting code: infra/shared/hazard_fe.py.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import hazard_fe as HF  # noqa: E402

OUT = ROOT / "data/processed/H60-index-nudge-policy"
FLOOR = 10.0
Y_COL = {"calls30": "y_calls30", "sus": "y_sus", "any": "y_any"}
A_BINS = [2, 5, 15, 45]          # minutes
R_BINS = [10, 30, 90]            # minutes


def lmin(x):
    return np.log(np.maximum(np.asarray(x, dtype=float), FLOOR) / 60.0)


def prep(df: pl.DataFrame, outcome: str) -> dict:
    d = df.filter(pl.col(Y_COL[outcome]).is_not_null() & pl.col("a_sus").is_not_null()).sort("agent", "t_call")
    y = d[Y_COL[outcome]].cast(pl.Float64).to_numpy()
    M = d["nudged"].to_numpy().astype(float)
    a_min = np.maximum(d["a_sus"].to_numpy(), FLOOR) / 60
    r_raw = np.where(d["s_dir_none"].to_numpy(), d["s_lc"].fill_null(FLOOR).to_numpy(), d["s_dir"].fill_null(FLOOR).to_numpy())
    r_min = np.maximum(r_raw, FLOOR) / 60
    k = d["k_sus"].to_numpy().astype(float)
    n_dir_other = np.maximum(d["n_dir"].to_numpy() - d["n_nudge_me"].to_numpy(), 0).astype(float)
    n_other = np.maximum(d["n_novel"].to_numpy() - d["n_dir"].to_numpy(), 0).astype(float)
    nuis = {"cur_dir_other": np.log1p(n_dir_other), "cur_other": np.log1p(n_other),
            "cur_bookend": (d["n_bookend"].to_numpy() > 0).astype(float),
            "swarm_act10": d["swarm_act10"].fill_null(0).to_numpy().astype(float),
            "ln_last_run": np.log(np.maximum(d["last_run_len"].fill_null(1).to_numpy().astype(float), 1)),
            "r_none": d["s_dir_none"].to_numpy().astype(float)}
    pk = d["prev_kind"].to_numpy()
    ps = d["prev_pause_s"].to_numpy().astype(float)
    nuis["pause_nodur"] = ((pk == "pause") & ~np.isfinite(ps)).astype(float)
    for lo, hi, nm in ((60, 300, "p60_300"), (300, 1800, "p300_1800"), (1800, np.inf, "p1800")):
        nuis[nm] = ((pk == "pause") & (ps > lo) & (ps <= hi)).astype(float)
    hd = np.clip(np.floor(d["h_day"].fill_null(0).to_numpy()), 0, 6)
    for h in range(1, 7):
        nuis[f"hday{h}"] = (hd == h).astype(float)
    nuis = {kk: v for kk, v in nuis.items() if np.std(v) > 0}
    days = d["pt_date"].to_numpy()
    udays, day_codes = np.unique(days, return_inverse=True)
    # chain id: restart at k_sus == 1 within agent (rows sorted by agent, t_call)
    chain = np.cumsum(k == 1)
    return {"y": y, "M": M, "la": np.log(a_min), "lk": np.log(k), "lr": np.log(r_min), "a_min": a_min, "r_min": r_min,
            "k": k, "nuis": nuis, "agent": d["agent"].to_numpy(), "day": day_codes, "days": days, "udays": udays,
            "chain": chain, "y_any": d["y_any"].cast(pl.Float64).to_numpy(), "n": len(y),
            "t": d["t_call"].dt.epoch("s").to_numpy(), "outcome": outcome}


def _X(P, idx, with_r=True, centers=None, M_override=None):
    M = P["M"] if M_override is None else M_override
    c = centers
    cols = {"la": P["la"], "lk": P["lk"], "lr": P["lr"], **P["nuis"], "M": M,
            "M_la": M * (P["la"] - c[0]), "M_lk": M * (P["lk"] - c[1])}
    if with_r:
        cols["M_lr"] = M * (P["lr"] - c[2])
    names = list(cols.keys())
    C = np.column_stack([cols[n][idx] for n in names])
    X, nm = HF.design(C, names, P["agent"][idx])
    return X, nm


def centers_of(P, idx):
    m = idx[P["M"][idx] > 0]
    if len(m) == 0:
        m = idx
    return (float(P["la"][m].mean()), float(P["lk"][m].mean()), float(P["lr"][m].mean()))


def fit(P, idx, with_r=True, centers=None):
    centers = centers or centers_of(P, idx)
    X, nm = _X(P, idx, with_r, centers)
    keep = np.r_[True, X[:, 1:].std(axis=0) > 0]
    if P["outcome"] == "calls30":
        f = HF.fit_ols(X[:, keep], P["y"][idx])
    else:
        f = HF.fit_binary(X[:, keep], P["y"][idx])
    beta = np.zeros(X.shape[1]); beta[keep] = f["beta"]
    cov = np.zeros((X.shape[1], X.shape[1])); kk = np.flatnonzero(keep); cov[np.ix_(kk, kk)] = f["cov"]
    return {"beta": beta, "names": nm, "cov": cov, "centers": centers, "with_r": with_r,
            "agents": np.unique(P["agent"][idx])}


def g_hat(P, model, idx):
    """Predicted nudge effect at rows idx: mu(1, x) - mu(0, x). Agent levels absent from the model get 0."""
    out = []
    for Mv in (1.0, 0.0):
        X, nm = _X(P, idx, model["with_r"], model["centers"], M_override=np.full(P["n"], Mv))
        col = {n: i for i, n in enumerate(model["names"])}
        b = np.array([model["beta"][col[n]] if n in col else 0.0 for n in nm])
        eta = X @ b
        out.append(eta if P["outcome"] == "calls30" else 1 / (1 + np.exp(-eta)))
    return out[0] - out[1]


def theta(model):
    nm = model["names"]
    keys = ["M", "M_la", "M_lk"] + (["M_lr"] if model["with_r"] else [])
    return {k: float(model["beta"][nm.index(k)]) for k in keys}


# ---------- Gittins-style one-nudge-per-chain stopping index ----------
def state_bin(P, idx):
    ab = np.digitize(P["a_min"][idx], A_BINS)
    rb = np.digitize(P["r_min"][idx], R_BINS)
    return ab * (len(R_BINS) + 1) + rb


def stopping_tables(P, sel_idx, nu_sel):
    """Escape (chain end) probability, transition matrix and mean index per state bin, from the selection half."""
    S = (len(A_BINS) + 1) * (len(R_BINS) + 1)
    sb = state_bin(P, sel_idx)
    un = P["M"][sel_idx] == 0
    # chain ends at gate if the gate starts a sustained run: next gate in the same chain absent
    ch = P["chain"][sel_idx]
    nxt_same = np.r_[ch[1:] == ch[:-1], False]
    end = ~nxt_same
    h0 = np.full(S, 0.5)
    T = np.full((S, S), 1.0 / S)
    R = np.zeros(S)
    for s in range(S):
        m = (sb == s)
        if m.sum() > 0:
            R[s] = nu_sel[m].mean()
        mu = m & un
        if mu.sum() >= 5:
            h0[s] = end[mu].mean()
        tr = np.flatnonzero(mu & nxt_same)
        if len(tr) >= 5:
            cnt = np.bincount(sb[tr + 1], minlength=S).astype(float) + 0.1
            T[s] = cnt / cnt.sum()
    return h0, T, R


def stopping_rule(h0, T, R, lam, iters=500):
    S = len(R)
    V = np.zeros(S)
    for _ in range(iters):
        C = (1 - h0) * (T @ V)
        Vn = np.maximum(R - lam, C)
        Vn = np.maximum(Vn, 0)
        if np.max(np.abs(Vn - V)) < 1e-9:
            V = Vn
            break
        V = Vn
    C = (1 - h0) * (T @ V)
    return (R - lam >= C) & (R - lam > 0)


def apply_stopping(P, ev_idx, fire):
    sb = state_bin(P, ev_idx)
    ch = P["chain"][ev_idx]
    hit = fire[sb]
    sel = []
    seen = set()
    for i, (c, h) in enumerate(zip(ch, hit)):
        if h and c not in seen:
            sel.append(i)
            seen.add(c)
    return np.array(sel, dtype=int)


def index_once(P, sel_idx, ev_idx, nu_sel, budget):
    h0, T, R = stopping_tables(P, sel_idx, nu_sel)
    lo, hi = float(R.min()) - 10, float(R.max()) + 1
    best = None
    for _ in range(40):
        lam = (lo + hi) / 2
        s = apply_stopping(P, ev_idx, stopping_rule(h0, T, R, lam))
        if len(s) > budget:
            lo = lam
        else:
            hi = lam
            best = s
    if best is None or len(best) == 0:
        best = apply_stopping(P, ev_idx, stopping_rule(h0, T, R, lo))
    return best


# ---------- cross-fitted policy evaluation ----------
def halves(P):
    return (P["day"] % 2).astype(int)  # interleaved by day order


def evaluate(P, sel_rows, ev_rows):
    """One direction of the cross-fit: selection model on sel_rows, evaluation model on ev_rows."""
    m_sel = fit(P, sel_rows, True)
    m_sel_ak = fit(P, sel_rows, False)
    m_ev = fit(P, ev_rows, True)
    g_ev = g_hat(P, m_ev, ev_rows)
    nu = g_hat(P, m_sel, ev_rows)
    nu_ak = g_hat(P, m_sel_ak, ev_rows)
    nu_sel_own = g_hat(P, m_sel, sel_rows)
    M = P["M"][ev_rows] > 0
    B = int(M.sum())
    out = {"B": B, "n": len(ev_rows)}
    if B == 0:
        return out
    top = np.argsort(-nu)[:B]
    top_ak = np.argsort(-nu_ak)[:B]
    once = np.flatnonzero(P["k"][ev_rows] == 2)
    stop = index_once(P, sel_rows, ev_rows, nu_sel_own, B)
    out.update({
        "logged": float(g_ev[M].mean()), "random": float(g_ev.mean()), "once_early": float(g_ev[once].mean()),
        "index": float(g_ev[top].mean()), "index_ak": float(g_ev[top_ak].mean()),
        "index_once": float(g_ev[stop].mean()) if len(stop) else np.nan, "n_once": int(len(once)),
        "n_index_once": int(len(stop)),
        "sum": {"logged": float(g_ev[M].sum()), "random": float(g_ev.mean() * B), "once_early": float(g_ev[once].mean() * B),
                "index": float(g_ev[top].sum()), "index_ak": float(g_ev[top_ak].sum()),
                "index_once": float(g_ev[stop].sum()) if len(stop) else np.nan},
    })
    out["sel_index_rows"] = ev_rows[top]
    out["sel_once_rows"] = ev_rows[stop] if len(stop) else np.array([], dtype=int)
    out["g_ev"] = g_ev
    return out


POL = ("logged", "random", "once_early", "index", "index_ak", "index_once")


def crossfit(P, rows=None):
    rows = np.arange(P["n"]) if rows is None else rows
    h = halves(P)[rows]
    A, Bh = rows[h == 0], rows[h == 1]
    r1 = evaluate(P, A, Bh)
    r2 = evaluate(P, Bh, A)
    res = {"B": r1["B"] + r2["B"]}
    for p in POL:
        tot = 0.0
        ok = True
        for r in (r1, r2):
            if r["B"] == 0:
                continue
            v = r["sum"][p] if p in r.get("sum", {}) else np.nan
            if p == "index_once":
                # per-nudge value times this half's budget (the stopping policy may spend fewer)
                v = r["index_once"] * r["B"]
            if not np.isfinite(v):
                ok = False
            tot += v
        res[p] = tot / res["B"] if ok and res["B"] > 0 else np.nan
    res["halves"] = [{k: v for k, v in r.items() if k not in ("sel_index_rows", "sel_once_rows", "g_ev")} for r in (r1, r2)]
    res["_r"] = (r1, r2)
    return res


def ratios(v):
    L, O = v["logged"], v["once_early"]
    return {"index/logged": v["index"] / L, "index/once_early": v["index"] / O, "index_once/logged": v["index_once"] / L,
            "index/index_ak": v["index"] / v["index_ak"], "random/logged": v["random"] / L,
            "once_early/logged": O / L, "index_once/once_early": v["index_once"] / O}


def boot_crossfit(P, B, seed=0, rows=None):
    rng = np.random.default_rng(seed)
    rows = np.arange(P["n"]) if rows is None else rows
    rpd = HF.rows_per_day(P["day"][rows])
    vals = []
    for _ in range(B):
        sub = rows[HF.block_resample(P["day"][rows], rng, rpd)]
        # resampling duplicates rows; give duplicated rows distinct chains/days are kept as is
        Q = take(P, sub)
        try:
            v = crossfit(Q)
            vals.append([v[p] for p in POL])
        except Exception:
            continue
    return np.array(vals)


def take(P, idx):
    Q = {}
    for k, v in P.items():
        if k == "nuis":
            Q[k] = {kk: vv[idx] for kk, vv in v.items()}
        elif isinstance(v, np.ndarray) and len(v) == P["n"]:
            Q[k] = v[idx]
        else:
            Q[k] = v
    Q["n"] = len(idx)
    # duplicated days must stay separate blocks for the halves: recode days in draw order
    Q["day"] = np.unique(Q["day"], return_inverse=True)[1] if False else Q["day"]
    # chains: make duplicated chains distinct by position
    Q["chain"] = np.cumsum(np.r_[True, (Q["chain"][1:] != Q["chain"][:-1])])
    Q["nuis"] = {kk: vv for kk, vv in Q["nuis"].items() if np.std(vv) > 0}
    return Q


def ratio_ci(D, num, den):
    i, j = POL.index(num), POL.index(den)
    r = D[:, i] / D[:, j]
    r = r[np.isfinite(r)]
    return [float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))] if len(r) > 10 else [np.nan, np.nan]


def heterogeneity(P, B=200, seed=0):
    """Wald test of theta_a = theta_k = theta_r = 0 with a day-bootstrap covariance (full-sample fit)."""
    rows = np.arange(P["n"])
    m = fit(P, rows, True)
    th = theta(m)
    keys = ["M_la", "M_lk", "M_lr"]
    v = np.array([th[k] for k in keys])
    rng = np.random.default_rng(seed)
    rpd = HF.rows_per_day(P["day"])
    D = []
    for _ in range(B):
        idx = HF.block_resample(P["day"], rng, rpd)
        Q = take(P, idx)
        try:
            mm = fit(Q, np.arange(Q["n"]), True, centers=m["centers"])
            t = theta(mm)
            D.append([t[k] for k in ["M"] + keys])
        except Exception:
            continue
    D = np.array(D)
    S = np.cov(D[:, 1:].T)
    from scipy.stats import chi2
    W = float(v @ np.linalg.solve(S, v))
    g_all = g_hat(P, m, rows)
    return {"theta": th, "theta_ci": {k: [float(np.percentile(D[:, i], 2.5)), float(np.percentile(D[:, i], 97.5))]
                                      for i, k in enumerate(["M"] + keys)},
            "wald": W, "p": float(1 - chi2.cdf(W, 3)), "mean_g_nudged": float(g_all[P["M"] > 0].mean()),
            "mean_g_all": float(g_all.mean()), "n_draws": int(len(D)), "centers": m["centers"]}
