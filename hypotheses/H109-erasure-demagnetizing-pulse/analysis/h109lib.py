"""H109 estimators: room axis, statement alignment, gap-matched erasure drop, kickoff control, recovery slopes.

All functions take the scheme tables (data/processed/H109-erasure-demagnetizing-pulse/) and a statement matrix X whose
rows align with statements.parquet (`sid`). The same functions run on real vectors and on synthetic ones.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
D = ROOT / "data/processed/H109-erasure-demagnetizing-pulse"
MODELS = ("bge_small", "gte_modernbert")
STAYER_SHARE = 0.8
MIN_STAYER_STMT = 5
GAP_BIN = 0.05
PERIODS = [36, 37, 38, 39, 41, 42, 44, 51]


def unit(X):
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=-1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


# ------------------------------------------------------------------------------------------------ loading
def load_tables(root: Path = D):
    st = pl.read_parquet(root / "statements.parquet")
    b = pl.read_parquet(root / "boundaries.parquet")
    r = pl.read_parquet(root / "reads.parquet")
    return st, b, r


def load_X(st: pl.DataFrame, model: str, variant: str = "style_resid32") -> np.ndarray:
    A = np.load(ED / f"statements_{variant}_{model}.npy", mmap_mode="r")
    return np.asarray(A[st["srow"].to_numpy()], dtype=np.float64)


# ------------------------------------------------------------------------------------------------ geometry
def day_center(st: pl.DataFrame, X: np.ndarray) -> np.ndarray:
    """x - mean over agents present that day of their day-mean statement vector (agent-weighted)."""
    day = st["pt_date"].to_numpy()
    ag = st["agent"].to_numpy().astype(np.int64)
    Xc = X.copy()
    for d in np.unique(day):
        ix = np.where(day == d)[0]
        a = ag[ix]
        ua, inv = np.unique(a, return_inverse=True)
        M = np.zeros((len(ua), X.shape[1]))
        np.add.at(M, inv, X[ix])
        M /= np.bincount(inv)[:, None]
        Xc[ix] -= M.mean(0)
    return Xc


def agent_constants(st: pl.DataFrame, Xc: np.ndarray) -> dict:
    """(agent, goal) -> leave-period-out agent constant: equal-weight mean of the agent's other-goal mean vectors
    (regime-III non-holdout chat statements). Zero vector when the agent has no other goal."""
    ag = st["agent"].to_numpy().astype(np.int64)
    gl = st["goal_no"].to_numpy().astype(np.int64)
    keys = ag * 1000 + gl
    uk, inv = np.unique(keys, return_inverse=True)
    M = np.zeros((len(uk), Xc.shape[1]))
    np.add.at(M, inv, Xc)
    M /= np.bincount(inv)[:, None]
    by_agent = {}
    for k, m in zip(uk, M):
        by_agent.setdefault(int(k // 1000), []).append((int(k % 1000), m))
    out = {}
    for a, lst in by_agent.items():
        for g, _ in lst:
            others = [m for gg, m in lst if gg != g]
            out[(a, g)] = np.mean(others, 0) if others else np.zeros(Xc.shape[1])
    return out


def field_dirs(model: str, include_holdout: bool = False) -> dict:
    """Per goal: whitened unit vectors of the room kickoffs (by room), the shared kickoff, and the operator-message
    mean per room (>= 3 human messages). Returns {goal: {"kick_room": {room: v}, "kick": v, "op": {room: v}}}."""
    import culture_vectors as CV
    from embed_models import load_whitener, MODELS as EM
    goals = PERIODS + ([45, 46, 47, 50] if include_holdout else [])
    ad = pl.DataFrame({"goal_no": goals, "regime": ["III"] * len(goals)})
    V, idx = CV.directions(model, ad, include_holdout=include_holdout)
    out = {g: {"kick_room": {}, "kick": None, "op": {}} for g in goals}
    for e in idx:
        g = e["goal_no"]
        if g not in out or e["level"] != "goal":
            continue
        if e["kind"] == "kickoff_room" and e["room"] is not None:
            out[g]["kick_room"][int(e["room"])] = V[e["i"]].astype(np.float64)
        elif e["kind"] == "kickoff":
            out[g]["kick"] = V[e["i"]].astype(np.float64)
    W = load_whitener("III", 32, model)
    k = pl.read_parquet(SH / "kicks_classified.parquet").filter(pl.col("kind") == "human_message") \
        .select("message_id", "goal_no", "pt_date", "room")
    from common import holdout_mask
    hm = np.array(holdout_mask(k["pt_date"].to_list(), k["goal_no"].to_list()))
    if not include_holdout:
        k = k.filter(~pl.Series(hm))
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("row")
    k = k.join(ci, on="message_id", how="inner").filter(pl.col("goal_no").is_in(goals))
    C = np.load(ED / f"chat_{EM[model]['suffix']}.npy", mmap_mode="r")
    for (g, r), sub in k.group_by(["goal_no", "room"]):
        if r is None or sub.height < 3:
            continue
        rows = np.sort(sub["row"].to_numpy())
        out[int(g)]["op"][int(r)] = unit(unit(W(np.asarray(C[rows], dtype=np.float32))).mean(0))
    return out


def period_of(st: pl.DataFrame) -> np.ndarray:
    return st["goal_no"].to_numpy().astype(np.int64)


def field_basis(f: dict, rA: int, rB: int) -> np.ndarray:
    """Orthonormal basis (columns) of u_f (room kickoffs differ: cos < 0.95) and u_op (both rooms >= 3 messages)."""
    cols = []
    kr = f["kick_room"]
    if rA in kr and rB in kr and float(kr[rA] @ kr[rB]) < 0.95:
        cols.append(unit(kr[rA] - kr[rB]))
    if rA in f["op"] and rB in f["op"]:
        cols.append(unit(f["op"][rA] - f["op"][rB]))
    if not cols:
        return np.zeros((32, 0))
    Q, R = np.linalg.qr(np.array(cols).T)
    return Q[:, np.abs(np.diag(R)) > 1e-8]


def axes_and_alignment(st: pl.DataFrame, Xc: np.ndarray, X: np.ndarray, A: dict, F: dict,
                       use_const: bool = True, project_fields: bool = True):
    """Returns a (room alignment, NaN for unscoped), b (kickoff alignment), and per-period axis info."""
    n = st.height
    a = np.full(n, np.nan)
    b = np.full(n, np.nan)
    ag = st["agent"].to_numpy().astype(np.int64)
    gl = period_of(st)
    rm = st["room"].to_numpy()
    sig = st["sigma"].to_numpy().astype(np.float64)
    sc = st["scoped"].to_numpy()
    info = {}
    for P in np.unique(gl[sc]):
        ix = np.where(sc & (gl == P))[0]
        rA = int(st["roomA"][int(ix[0])])
        rB = int(st["roomB"][int(ix[0])])
        const = np.array([A.get((int(ag[i]), int(P)), np.zeros(32)) for i in ix]) if use_const else 0.0
        Y = Xc[ix] - const
        # stayers
        stay = {}
        for i_ag in np.unique(ag[ix]):
            m = ag[ix] == i_ag
            sA = np.mean(rm[ix][m] == rA)
            if m.sum() >= MIN_STAYER_STMT and max(sA, 1 - sA) >= STAYER_SHARE:
                home = rA if sA >= 0.5 else rB
                mh = m & (rm[ix] == home)
                stay[int(i_ag)] = (home, Y[mh].mean(0))
        QF = field_basis(F[int(P)], rA, rB) if project_fields else np.zeros((32, 0))
        Pp = np.eye(32) - QF @ QF.T
        kr = F[int(P)]["kick_room"]
        kk = F[int(P)]["kick"]
        kdir = {rA: kr.get(rA, kk), rB: kr.get(rB, kk)}
        nA = sum(1 for v in stay.values() if v[0] == rA)
        nB = sum(1 for v in stay.values() if v[0] == rB)
        info[int(P)] = {"n_stay_A": nA, "n_stay_B": nB, "field_dim": int(QF.shape[1]), "rA": rA, "rB": rB}
        for i_ag in np.unique(ag[ix]):
            SA = [v[1] for k_, v in stay.items() if v[0] == rA and k_ != i_ag]
            SB = [v[1] for k_, v in stay.items() if v[0] == rB and k_ != i_ag]
            if not SA or not SB:
                continue
            u = unit(Pp @ (np.mean(SA, 0) - np.mean(SB, 0)))
            m = ag[ix] == i_ag
            a[ix[m]] = sig[ix[m]] * (Y[m] @ u)
        for r_, kv in kdir.items():
            if kv is None:
                continue
            m = rm[ix] == r_
            b[ix[m]] = X[ix[m]] @ kv
    return a, b, info


# ------------------------------------------------------------------------------------------------ erasure drop
def event_table(b: pl.DataFrame, st: pl.DataFrame, val: np.ndarray, variant: str, post_mask: np.ndarray | None = None):
    """Per boundary: period, cluster (agent-day), stratum (agent x gap bin), label, pre mean, post mean, D.
    post_mask: optional boolean over sids restricting which post statements count (R-fast split)."""
    bb = b.filter(pl.col("variant") == variant)
    gl = period_of(st)
    pre = bb["pre"].to_list()
    post = bb["post"].to_list()
    n = bb.height
    pm, qm = np.full(n, np.nan), np.full(n, np.nan)
    for j in range(n):
        p = [s for s in pre[j] if not np.isnan(val[s])]
        q = [s for s in post[j] if not np.isnan(val[s]) and (post_mask is None or post_mask[s])]
        if p and q:
            pm[j] = val[p].mean()
            qm[j] = val[q].mean()
    k = bb["k_sid"].to_numpy()
    gapbin = np.floor(np.log10(np.maximum(bb["gap_s"].to_numpy(), 1.0)) / GAP_BIN).astype(np.int64)
    ev = pl.DataFrame({"bid": bb["bid"], "period": gl[k], "agent": bb["agent"].cast(pl.Int64), "pt_date": bb["pt_date"],
                       "label": bb["label"], "gapbin": gapbin, "gap_s": bb["gap_s"], "pre": pm, "post": qm})
    ev = ev.filter(pl.col("pre").is_not_nan() & pl.col("post").is_not_nan())
    ev = ev.with_columns((pl.col("post") - pl.col("pre")).alias("D"),
                         (pl.col("agent") * 100000 + pl.col("gapbin")).alias("stratum"))
    return ev


def _delta_core(lab, Dv, pre, strat, w, which="F"):
    isF = (lab == which).astype(np.float64) * w
    isW = (lab == "W").astype(np.float64) * w
    us, si = np.unique(strat, return_inverse=True)
    nF = np.bincount(si, isF, len(us))
    nW = np.bincount(si, isW, len(us))
    sF = np.bincount(si, isF * Dv, len(us))
    sW = np.bincount(si, isW * Dv, len(us))
    pF = np.bincount(si, isF * pre, len(us))
    ok = (nF > 0) & (nW > 0)
    if not ok.any():
        return np.nan, np.nan, np.nan, 0.0
    exc = np.sum(nF[ok] * (sF[ok] / nF[ok] - sW[ok] / nW[ok])) / nF[ok].sum()
    Apre = pF[ok].sum() / nF[ok].sum()
    cover = nF[ok].sum() / max(nF.sum(), 1e-12)
    return exc, Apre, -exc / Apre if Apre != 0 else np.nan, cover


def delta(ev: pl.DataFrame, which: str = "F", nboot: int = 1000, seed: int = 0, cluster: str = "agentday") -> dict:
    """Gap-matched drop fraction with a cluster bootstrap (strata fixed)."""
    if ev.height == 0 or (ev["label"] == which).sum() == 0:
        return {"n": 0}
    lab = ev["label"].to_numpy()
    Dv = ev["D"].to_numpy()
    pre = ev["pre"].to_numpy()
    strat = ev["stratum"].to_numpy()
    cl_key = (ev["agent"].cast(pl.Utf8) + "_" + ev["pt_date"]) if cluster == "agentday" else ev["agent"].cast(pl.Utf8)
    _, cl = np.unique(cl_key.to_numpy(), return_inverse=True)
    exc, Apre, d, cover = _delta_core(lab, Dv, pre, strat, np.ones(len(lab)), which)
    rng = np.random.default_rng(seed)
    nc = cl.max() + 1
    bs = np.full((nboot, 3), np.nan)
    for r in range(nboot):
        wc = rng.multinomial(nc, np.full(nc, 1.0 / nc)).astype(np.float64)
        e2, a2, d2, _ = _delta_core(lab, Dv, pre, strat, wc[cl], which)
        bs[r] = (e2, a2, d2)
    ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]  # noqa: E731
    return {"n": int((lab == which).sum()), "n_W": int((lab == "W").sum()), "coverage": float(cover),
            "excess": float(exc), "excess_ci": ci(bs[:, 0]), "A_pre": float(Apre), "A_pre_ci": ci(bs[:, 1]),
            "delta": float(d), "delta_ci": ci(bs[:, 2]), "delta_se": float(np.nanstd(bs[:, 2])),
            "n_clusters": int(nc)}


def delta_reg(ev: pl.DataFrame) -> dict:
    """Companion: D = bF F + bV V + natural spline(log gap, 4 knots) + agent fixed effects (OLS)."""
    e = ev.filter(pl.col("label").is_in(["F", "V", "W"]))
    if e.height < 50 or (e["label"] == "F").sum() < 10:
        return {}
    lg = np.log10(np.maximum(e["gap_s"].to_numpy(), 1.0))
    kn = np.quantile(lg, [0.05, 0.35, 0.65, 0.95])

    def ns(x):
        def d(k):
            return np.maximum(x - k, 0) ** 3
        K = kn
        cols = [x]
        for k in K[:-2]:
            cols.append((d(k) - d(K[-1])) / (K[-1] - k) - (d(K[-2]) - d(K[-1])) / (K[-1] - K[-2]))
        return np.column_stack(cols)
    ag = e["agent"].to_numpy()
    ua, ai = np.unique(ag, return_inverse=True)
    Xd = np.column_stack([(e["label"] == "F").to_numpy(), (e["label"] == "V").to_numpy(), ns(lg),
                          np.eye(len(ua))[ai]]).astype(np.float64)
    y = e["D"].to_numpy()
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    res = y - Xd @ beta
    XtX = np.linalg.pinv(Xd.T @ Xd)
    se = np.sqrt(np.diag(XtX) * res.var())
    Apre = e.filter(pl.col("label") == "F")["pre"].mean()
    return {"bF": float(beta[0]), "bF_se": float(se[0]), "bV": float(beta[1]), "bV_se": float(se[1]),
            "delta_reg": float(-beta[0] / Apre), "delta_reg_se": float(se[0] / abs(Apre)), "A_pre": float(Apre)}


# ------------------------------------------------------------------------------------------------ recovery
def recovery(b: pl.DataFrame, r: pl.DataFrame, st: pl.DataFrame, val: np.ndarray, variant: str, periods=None,
             nboot: int = 500, seed: int = 0) -> dict:
    """y_k = a_k - pre mean; WLS with event fixed effects on log1p(R), log1p(U), log k."""
    bb = b.filter((pl.col("variant") == variant) & (pl.col("label") == "F"))
    gl = period_of(st)
    pre = bb["pre"].to_list()
    prem = {}
    for bid, p in zip(bb["bid"].to_list(), pre):
        v = [val[s] for s in p if not np.isnan(val[s])]
        if v:
            prem[bid] = float(np.mean(v))
    rr = r.filter(pl.col("variant") == variant).join(bb.select("bid", "agent", "pt_date"), on="bid", how="inner")
    rr = rr.filter(pl.col("bid").is_in(list(prem)))
    y = np.array([val[s] for s in rr["sid"].to_numpy()]) - np.array([prem[i] for i in rr["bid"].to_numpy()])
    per = gl[rr["sid"].to_numpy()]
    keep = ~np.isnan(y)
    if periods is not None:
        keep &= np.isin(per, periods)
    rr = rr.filter(pl.Series(keep))
    y = y[keep]
    if rr.height < 30:
        return {"n": int(rr.height)}
    Xr = np.column_stack([np.log1p(rr["R"].to_numpy()), np.log1p(rr["U"].to_numpy()), np.log(rr["k"].to_numpy())])
    ev = rr["bid"].to_numpy()
    _, ei = np.unique(ev, return_inverse=True)
    cl = np.unique((rr["agent"].cast(pl.Utf8) + "_" + rr["pt_date"]).to_numpy(), return_inverse=True)[1]

    def fit(w):
        sw = np.bincount(ei, w)
        sw[sw == 0] = 1
        Xm = Xr - (np.stack([np.bincount(ei, w * Xr[:, j]) for j in range(3)], 1) / sw[:, None])[ei]
        ym = y - (np.bincount(ei, w * y) / sw)[ei]
        WX = Xm * w[:, None]
        try:
            return np.linalg.solve(WX.T @ Xm, WX.T @ ym)
        except np.linalg.LinAlgError:
            return np.full(3, np.nan)
    est = fit(np.ones(len(y)))
    rng = np.random.default_rng(seed)
    nc = cl.max() + 1
    bs = np.array([fit(rng.multinomial(nc, np.full(nc, 1 / nc)).astype(float)[cl]) for _ in range(nboot)])
    ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]  # noqa: E731
    return {"n": int(len(y)), "n_events": int(ei.max() + 1), "kR": float(est[0]), "kR_ci": ci(bs[:, 0]),
            "kU": float(est[1]), "kU_ci": ci(bs[:, 1]), "g_logk": float(est[2]),
            "kR_minus_kU": float(est[0] - est[1]), "kR_minus_kU_ci": ci(bs[:, 0] - bs[:, 1])}


def re_meta(est: list, se: list) -> dict:
    """DerSimonian-Laird random-effects mean."""
    e, s = np.array(est, float), np.array(se, float)
    ok = np.isfinite(e) & np.isfinite(s) & (s > 0)
    e, s = e[ok], s[ok]
    if len(e) < 2:
        return {"k": int(len(e))}
    w = 1 / s ** 2
    mu_f = np.sum(w * e) / w.sum()
    Qs = np.sum(w * (e - mu_f) ** 2)
    tau2 = max(0.0, (Qs - (len(e) - 1)) / (w.sum() - np.sum(w ** 2) / w.sum()))
    ws = 1 / (s ** 2 + tau2)
    mu = np.sum(ws * e) / ws.sum()
    se_mu = np.sqrt(1 / ws.sum())
    return {"k": int(len(e)), "mu": float(mu), "ci": [float(mu - 1.96 * se_mu), float(mu + 1.96 * se_mu)],
            "se": float(se_mu), "tau2": float(tau2), "I2": float(max(0, (Qs - (len(e) - 1)) / Qs)) if Qs > 0 else 0.0}
