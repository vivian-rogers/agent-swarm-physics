"""H97 estimators and loaders: kickoff memory beta (IV split-half), placebo memory, per-agent chi, shape test,
agent constancy. Used by run.py, natives.py, synthetic.py and confirm.py (same code on real and synthetic data).

A "boundary" is a dict {agent: (X_prev[n_i x 32], Y_post[m_i x 32])} plus a direction k (unit, 32-d).
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
S = ROOT / "data/processed/shared"
ED = S / "embeddings"
DATA = ROOT / "data/processed/H97-quench-restoring-force"
MIN_STMT = 4
MIN_N_TRANSITION = 5
MIN_N_AGENT = 4
N_SPLITS = 50
SUBSPACES = ("par", "perp", "full")


# ============================================================================================ loading
_CACHE: dict = {}


def statement_matrix(model: str = "bge_small", variant: str = "white") -> np.ndarray:
    """32-d unit statement vectors aligned to statements.parquet rows. variant: white | style."""
    key = (model, variant)
    if key not in _CACHE:
        name = {"white": "statements_white32", "style": "statements_style_resid_period32"}[variant]
        _CACHE[key] = np.load(ED / f"{name}_{model}.npy", mmap_mode="r")
    return _CACHE[key]


def dedupe_rows() -> set:
    if "dedupe" not in _CACHE:
        sf = pl.read_parquet(S / "statement_flags.parquet", columns=["srow", "self_repeat_both"])
        _CACHE["dedupe"] = set(sf.filter(pl.col("self_repeat_both"))["srow"].to_list())
    return _CACHE["dedupe"]


def load_design(design: str) -> tuple[pl.DataFrame, dict]:
    stmt = pl.read_parquet(DATA / "stmt.parquet").filter(pl.col("design") == design)
    tr = pl.read_parquet(DATA / "transitions.parquet").filter(pl.col("design") == design).row(0, named=True)
    return stmt, tr


def vectors(design: str, key: str, model: str) -> np.ndarray:
    v = np.load(DATA / "vectors.npz")
    return np.asarray(v[f"{design}|{key}|{model}"], dtype=np.float64)


def agent_center_means(regime: str, exclude_goals: set, model: str, variant: str) -> dict:
    """Leave-period-out agent mean vector (all non-holdout statements of the regime outside exclude_goals)."""
    key = ("center", regime, tuple(sorted(exclude_goals)), model, variant)
    if key in _CACHE:
        return _CACHE[key]
    from common import holdout_mask
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("row")
    st = st.filter((pl.col("regime") == regime) & ~pl.col("goal_no").is_in(list(exclude_goals) + [23]))
    ho = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st = st.filter(pl.Series(~ho))
    Z = statement_matrix(model, variant)
    out = {}
    for (a,), g in st.group_by(["agent"]):
        rows = g["row"].to_numpy()
        if len(rows) >= 50:
            out[int(a)] = np.asarray(Z[np.sort(rows)], dtype=np.float64).mean(0)
    _CACHE[key] = out
    return out


def seg_vectors(stmt: pl.DataFrame, mask_expr, model="bge_small", variant="white", dedupe=False,
                center: dict | None = None) -> dict:
    """{agent: matrix of statement vectors} for the rows selected by mask_expr."""
    sub = stmt.filter(mask_expr)
    if dedupe:
        dr = dedupe_rows()
        sub = sub.filter(~pl.col("row").is_in(list(dr)))
    Z = statement_matrix(model, variant)
    out = {}
    for (a,), g in sub.group_by(["agent"]):
        rows = np.sort(g["row"].to_numpy())
        M = np.asarray(Z[rows], dtype=np.float64)
        if center is not None:
            if int(a) not in center:
                continue
            M = M - center[int(a)]
        out[int(a)] = M
    return out


def boundary(prev: dict, post: dict, min_stmt: int = MIN_STMT) -> dict:
    return {a: (prev[a], post[a]) for a in sorted(set(prev) & set(post))
            if len(prev[a]) >= min_stmt and len(post[a]) >= min_stmt}


# ============================================================================================ split-half arrays
def split_arrays(bd: dict, n_splits: int = N_SPLITS, seed: int = 0, with_y_halves: bool = False):
    """XA, XB: (S, N, d) half means of the prev statements (random halves); Y: (N, d) post means; agents list.
    with_y_halves: also YA, YB (S, N, d) half means of the post statements (for the disattenuated correlation)."""
    rng = np.random.default_rng(seed)
    agents = list(bd)
    N = len(agents)
    d = next(iter(bd.values()))[0].shape[1]
    XA = np.empty((n_splits, N, d)); XB = np.empty((n_splits, N, d)); Y = np.empty((N, d))
    YA = np.empty((n_splits, N, d)); YB = np.empty((n_splits, N, d))
    for j, a in enumerate(agents):
        X, P = bd[a]
        Y[j] = P.mean(0)
        n = len(X); h = n // 2; m = len(P); hm = m // 2
        for s in range(n_splits):
            perm = rng.permutation(n)
            XA[s, j] = X[perm[:h]].mean(0)
            XB[s, j] = X[perm[h:]].mean(0)
            if with_y_halves:
                pm = rng.permutation(m)
                YA[s, j] = P[pm[:hm]].mean(0)
                YB[s, j] = P[pm[hm:]].mean(0)
    if with_y_halves:
        return XA, XB, Y, agents, YA, YB
    return XA, XB, Y, agents


def _proj(A, k, sub):
    """Project arrays (..., d) onto the subspace: par -> (..., 1); perp/full -> (..., d)."""
    if sub == "par":
        return (A @ k)[..., None]
    if sub == "perp":
        return A - (A @ k)[..., None] * k
    return A


def memory_beta(XA, XB, Y, k, sub="full", idx=None):
    """IV memory slope beta (symmetrized over A<->B, summed over splits). idx: agent indices (bootstrap)."""
    if idx is not None:
        XA, XB, Y = XA[:, idx], XB[:, idx], Y[idx]
    pA, pB, pY = _proj(XA, k, sub), _proj(XB, k, sub), _proj(Y, k, sub)
    cA = pA - pA.mean(1, keepdims=True); cB = pB - pB.mean(1, keepdims=True); cY = pY - pY.mean(0, keepdims=True)
    num = (cY[None] * cA).sum() + (cY[None] * cB).sum()
    den = 2 * (cA * cB).sum()
    return num / den if den > 0 else np.nan


def memory_corr(XA, XB, Y, YA, YB, k, sub="full", idx=None):
    """Disattenuated cross-agent memory correlation: cov(y, x) / sqrt(var_true(x) var_true(y)), with the true
    variances from split-half cross products. Scale-free, so a change in the embedding's compression between the two
    segments (a common component that grows on day 1) does not fake memory loss."""
    if idx is not None:
        XA, XB, Y, YA, YB = XA[:, idx], XB[:, idx], Y[idx], YA[:, idx], YB[:, idx]
    pA, pB, pY = _proj(XA, k, sub), _proj(XB, k, sub), _proj(Y, k, sub)
    qA, qB = _proj(YA, k, sub), _proj(YB, k, sub)
    c = lambda A: A - A.mean(-2, keepdims=True)  # noqa: E731
    cA, cB, cY, dA, dB = c(pA), c(pB), c(pY), c(qA), c(qB)
    num = ((cY[None] * cA).sum() + (cY[None] * cB).sum()) / 2
    vx = (cA * cB).sum(); vy = (dA * dB).sum()
    S_ = XA.shape[0]
    if vx <= 0 or vy <= 0:
        return np.nan
    return num / np.sqrt(vx * vy) * 1.0 if S_ else np.nan


def agent_chi_mem(XA, XB, Y):
    """Per-agent chi (memory form, full space, leave-agent-out centroids)."""
    S_, N, d = XA.shape
    out = np.full(N, np.nan)
    for j in range(N):
        o = np.r_[0:j, j + 1:N]
        a = XA[:, j] - XA[:, o].mean(1); b = XB[:, j] - XB[:, o].mean(1); y = Y[j] - Y[o].mean(0)
        num = (a @ y).sum() + (b @ y).sum()
        den = 2 * (a * b).sum()
        out[j] = 1 - num / den if den > 0 else np.nan
    return out


def shape_along_k(XA, XB, Y, k, T_minus_i: np.ndarray, beta_par: float):
    """HH-literal shape along k. D_i = T_-i - u_i (half A), Delta_i = w_i - u_i (half B).
    Returns slope b = 1 - beta_par (IV), intercept a = mean(Delta) - b mean(D) (noise-unbiased means),
    per-agent chi_par_i = mean_s Delta / mean_s D, and the descriptive curvature c (per-split OLS, attenuated)."""
    uA = XA @ k; uB = XB @ k; w = Y @ k
    D = T_minus_i[None, :] - uA; Dl = w[None, :] - uB
    b = 1 - beta_par
    a = Dl.mean() - b * D.mean()
    chi_i = Dl.mean(0) / D.mean(0)
    cs = []
    for s in range(D.shape[0]):
        Xd = np.c_[np.ones(D.shape[1]), D[s], D[s] ** 2]
        if D.shape[1] >= 5:
            coef, *_ = np.linalg.lstsq(Xd, Dl[s], rcond=None)
            cs.append(coef[2])
    return dict(b=b, a=a, chi_i=chi_i, c=float(np.mean(cs)) if cs else np.nan, Dbar=float(D.mean()), Dlbar=float(Dl.mean()))


def boot_beta(XA, XB, Y, k, subs=SUBSPACES, n_boot=1000, seed=1, n_sub_splits=10):
    rng = np.random.default_rng(seed)
    N = Y.shape[0]
    XAs, XBs = XA[:n_sub_splits], XB[:n_sub_splits]
    out = {s: np.empty(n_boot) for s in subs}
    for b in range(n_boot):
        idx = rng.integers(0, N, N)
        if len(np.unique(idx)) < 3:
            idx = rng.permutation(N)
        for s in subs:
            out[s][b] = memory_beta(XAs, XBs, Y, k, s, idx)
    return out


def summarize_boundary(bd: dict, k: np.ndarray, n_boot: int = 1000, seed: int = 0, T_minus: dict | None = None):
    XA, XB, Y, agents = split_arrays(bd, seed=seed)
    res = {"N": len(agents), "agents": agents}
    for s in SUBSPACES:
        res[f"beta_{s}"] = memory_beta(XA, XB, Y, k, s)
    if n_boot:
        bs = boot_beta(XA, XB, Y, k, n_boot=n_boot, seed=seed + 1)
        res["boot"] = bs
    res["chi_mem_i"] = agent_chi_mem(XA, XB, Y)
    if T_minus is not None:
        T = np.array([T_minus.get(a, np.nan) for a in agents])
        ok = np.isfinite(T)
        if ok.sum() >= MIN_N_AGENT:
            sh = shape_along_k(XA[:, ok], XB[:, ok], Y[ok], k, T[ok], res["beta_par"])
            chi_par = np.full(len(agents), np.nan); chi_par[ok] = sh["chi_i"]
            res["shape"] = {kk: v for kk, v in sh.items() if kk != "chi_i"}
            res["chi_par_i"] = chi_par
    res["_arrays"] = (XA, XB, Y)
    return res


def plateau_targets(plat: dict, k: np.ndarray) -> dict:
    """Leave-agent-out mean alignment with k over plateau days (agents with >= MIN_STMT plateau statements)."""
    al = {a: float((M @ k).mean()) for a, M in plat.items() if len(M) >= MIN_STMT}
    out = {}
    for a in set(al) | set():
        pass
    keys = list(al)
    tot = sum(al.values())
    for a in keys:
        out[a] = (tot - al[a]) / (len(keys) - 1) if len(keys) > 1 else np.nan
    # agents without plateau statements: use the full mean
    out["_all"] = tot / len(keys) if keys else np.nan
    return out


def T_for(agents, pt):
    return {a: pt.get(a, pt.get("_all", np.nan)) for a in agents}


# ============================================================================================ meta-analysis
def dl_meta(est, se):
    """DerSimonian-Laird random-effects mean, its SE, tau^2."""
    est = np.asarray(est, float); se = np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) < 2:
        return dict(mean=float(est[0]) if len(est) else np.nan, se=np.nan, tau2=np.nan, k=len(est))
    w = 1 / se ** 2
    m0 = (w * est).sum() / w.sum()
    Q = (w * (est - m0) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / c)
    ws = 1 / (se ** 2 + tau2)
    m = (ws * est).sum() / ws.sum()
    return dict(mean=float(m), se=float(np.sqrt(1 / ws.sum())), tau2=float(tau2), k=int(len(est)))


def sign_test_p(x):
    from scipy.stats import binomtest
    x = np.asarray(x); x = x[np.isfinite(x) & (x != 0)]
    if len(x) == 0:
        return np.nan
    return float(binomtest(int((x > 0).sum()), len(x), 0.5, alternative="greater").pvalue)


# ============================================================================================ agent constancy
def rank_within(df: pl.DataFrame, col: str) -> pl.DataFrame:
    return df.with_columns(((pl.col(col).rank("average").over("design")) / (pl.len().over("design") + 1)).alias("rk"))


def _const_stats(ag, rk, order, min_tr):
    """ag: agent ids; rk: within-design ranks; order: per-row date order (global). Returns r (odd/even split-half), u (ICC)."""
    ids, inv, cnt = np.unique(ag, return_inverse=True, return_counts=True)
    keep = cnt[inv] >= min_tr
    if (cnt >= min_tr).sum() < 5:
        return np.nan, np.nan, 0
    a = inv[keep]; x = rk[keep]; o = order[keep]
    srt = np.lexsort((o, a)); a, x = a[srt], x[srt]
    pos = np.zeros(len(a), int)
    starts = np.r_[0, np.flatnonzero(np.diff(a)) + 1]
    for s0, s1 in zip(starts, np.r_[starts[1:], len(a)]):
        pos[s0:s1] = np.arange(s1 - s0)
    ua = np.unique(a)
    m0 = np.array([x[(a == u) & (pos % 2 == 0)].mean() for u in ua])
    m1 = np.array([x[(a == u) & (pos % 2 == 1)].mean() for u in ua])
    r = float(np.corrcoef(m0, m1)[0, 1])
    n = np.array([(a == u).sum() for u in ua], float); m = np.array([x[a == u].mean() for u in ua])
    v = np.array([x[a == u].var(ddof=1) for u in ua])
    gm = x.mean(); k = len(ua); Nt = n.sum()
    msb = (n * (m - gm) ** 2).sum() / (k - 1); msw = ((n - 1) * v).sum() / (Nt - k)
    n0 = (Nt - (n ** 2).sum() / Nt) / (k - 1)
    s2b = max(0.0, (msb - msw) / n0)
    u = s2b / (s2b + msw) if (s2b + msw) > 0 else np.nan
    return r, u, len(ua)


def constancy(df: pl.DataFrame, col: str, min_tr: int = 4, n_perm: int = 2000, seed: int = 7, date_col="first_day"):
    """df: one row per (design, agent) with col (chi) and date_col. Within-design ranks; split-half r between an agent's
    mean rank over odd- and even-numbered transitions (date order); one-way ICC share u of ranks; permutation of agent
    labels within design (keeps every agent's transition count)."""
    d = rank_within(df.filter(pl.col(col).is_finite()), col)
    ag = d["agent"].to_numpy(); rk = d["rk"].to_numpy(); des = d["design"].to_numpy()
    order = d[date_col].rank("ordinal").to_numpy()
    r0, u0, na = _const_stats(ag, rk, order, min_tr)
    rng = np.random.default_rng(seed)
    groups = [np.flatnonzero(des == z) for z in np.unique(des)]
    rp, up = np.full(n_perm, np.nan), np.full(n_perm, np.nan)
    for b in range(n_perm):
        ag2 = ag.copy()
        for ix in groups:
            ag2[ix] = ag[rng.permutation(ix)]
        rp[b], up[b], _ = _const_stats(ag2, rk, order, min_tr)
    p_r = float((np.sum(rp >= r0) + 1) / (np.sum(np.isfinite(rp)) + 1)) if np.isfinite(r0) else np.nan
    p_u = float((np.sum(up >= u0) + 1) / (np.sum(np.isfinite(up)) + 1)) if np.isfinite(u0) else np.nan
    return dict(r=r0, p_r=p_r, u=u0, p_u=p_u, n_agents=na, n_rows=int(len(ag)),
                r_null95=float(np.nanpercentile(rp, 95)) if np.isfinite(rp).any() else np.nan,
                u_null95=float(np.nanpercentile(up, 95)) if np.isfinite(up).any() else np.nan)


# ============================================================================================ one transition, end to end
def _jack(fun, N):
    vals = np.array([fun(np.r_[0:j, j + 1:N]) for j in range(N)])
    ok = np.isfinite(vals)
    if ok.sum() < 3:
        return np.nan
    v = vals[ok]; n = len(v)
    return float(np.sqrt((n - 1) / n * ((v - v.mean()) ** 2).sum()))


def _shape_a(XA, XB, Y, k, T, idx):
    XA, XB, Y, T = XA[:, idx], XB[:, idx], Y[idx], T[idx]
    bpar = memory_beta(XA, XB, Y, k, "par")
    uA = XA @ k; uB = XB @ k; w = Y @ k
    b = 1 - bpar
    return (w[None] - uB).mean() - b * (T[None] - uA).mean()


def analyze_transition(kick_bd: dict, plac_bds: list, plat_T: dict | None, k: np.ndarray, n_splits: int = N_SPLITS,
                       n_boot: int = 0, seed: int = 0) -> dict:
    """All per-transition statistics. kick_bd/plac_bds: boundaries; plat_T: leave-agent-out plateau targets along k."""
    XA, XB, Y, agents, YA, YB = split_arrays(kick_bd, n_splits=n_splits, seed=seed, with_y_halves=True)
    N = len(agents)
    r = {"N": N, "agents": agents}
    for s in SUBSPACES:
        r[f"rho_{s}"] = memory_corr(XA, XB, Y, YA, YB, k, s)
        r[f"se_rho_{s}"] = _jack(lambda ix, s=s: memory_corr(XA, XB, Y, YA, YB, k, s, ix), N) if N >= 4 else np.nan
    r["iso_diff_rho"] = r["rho_par"] - r["rho_perp"]
    r["se_iso_diff_rho"] = _jack(lambda ix: memory_corr(XA, XB, Y, YA, YB, k, "par", ix)
                                 - memory_corr(XA, XB, Y, YA, YB, k, "perp", ix), N) if N >= 4 else np.nan
    for s in SUBSPACES:
        r[f"beta_{s}"] = memory_beta(XA, XB, Y, k, s)
        r[f"se_beta_{s}"] = _jack(lambda ix, s=s: memory_beta(XA, XB, Y, k, s, ix), N) if N >= 4 else np.nan
    r["iso_diff"] = r["beta_par"] - r["beta_perp"]
    r["se_iso_diff"] = _jack(lambda ix: memory_beta(XA, XB, Y, k, "par", ix) - memory_beta(XA, XB, Y, k, "perp", ix), N) if N >= 4 else np.nan
    r["chi_mem_i"] = agent_chi_mem(XA, XB, Y)
    if n_boot:
        bs = boot_beta(XA, XB, Y, k, n_boot=n_boot, seed=seed + 1)
        for s in SUBSPACES:
            r[f"ci_beta_{s}"] = [float(np.nanpercentile(bs[s], 5)), float(np.nanpercentile(bs[s], 95))]
        r["_boot"] = bs
    # placebo memory
    pb = {s: [] for s in SUBSPACES}
    pr = {s: [] for s in SUBSPACES}
    for j, bd in enumerate(plac_bds):
        if len(bd) < MIN_N_TRANSITION:
            continue
        pa, pbb, py, _, pya, pyb = split_arrays(bd, n_splits=max(10, n_splits // 5), seed=seed + 100 + j, with_y_halves=True)
        for s in SUBSPACES:
            pb[s].append(memory_beta(pa, pbb, py, k, s))
            pr[s].append(memory_corr(pa, pbb, py, pya, pyb, k, s))
    r["n_placebo"] = len(pb["full"])
    for s in SUBSPACES:
        v = np.array(pr[s], float)
        r[f"rho0_{s}"] = float(np.nanmedian(v)) if len(v) else np.nan
        r[f"rho0_{s}_all"] = v.tolist()
        sd0 = float(np.nanstd(v, ddof=1) / np.sqrt(len(v))) if len(v) >= 2 else np.nan
        r[f"drho_{s}"] = r[f"rho0_{s}"] - r[f"rho_{s}"]
        r[f"se_drho_{s}"] = float(np.sqrt(r[f"se_rho_{s}"] ** 2 + (sd0 if np.isfinite(sd0) else r[f"se_rho_{s}"]) ** 2))
    for s in SUBSPACES:
        v = np.array(pb[s], float)
        r[f"beta0_{s}"] = float(np.nanmedian(v)) if len(v) else np.nan
        r[f"beta0_{s}_all"] = v.tolist()
        sd0 = float(np.nanstd(v, ddof=1) / np.sqrt(len(v))) if len(v) >= 2 else np.nan
        r[f"dbeta_{s}"] = r[f"beta0_{s}"] - r[f"beta_{s}"]
        r[f"se_dbeta_{s}"] = float(np.sqrt(r[f"se_beta_{s}"] ** 2 + (sd0 if np.isfinite(sd0) else r[f"se_beta_{s}"]) ** 2))
        if n_boot and len(v):
            r[f"ci_dbeta_{s}"] = [float(r[f"beta0_{s}"] - np.nanpercentile(r["_boot"][s], 95) - 1.645 * (sd0 if np.isfinite(sd0) else 0)),
                                  float(r[f"beta0_{s}"] - np.nanpercentile(r["_boot"][s], 5) + 1.645 * (sd0 if np.isfinite(sd0) else 0))]
    # shape along k with the settled (plateau) target
    if plat_T is not None:
        T = np.array([plat_T.get(a, plat_T.get("_all", np.nan)) for a in agents], float)
        if np.isfinite(T).all() and N >= MIN_N_AGENT:
            sh = shape_along_k(XA, XB, Y, k, T, r["beta_par"])
            r["shape_b"], r["shape_a"], r["shape_c"] = sh["b"], sh["a"], sh["c"]
            r["shape_Dbar"], r["shape_Dlbar"] = sh["Dbar"], sh["Dlbar"]
            r["se_shape_a"] = _jack(lambda ix: _shape_a(XA, XB, Y, k, T, ix), N)
            r["se_shape_b"] = r["se_beta_par"]
            r["chi_par_i"] = sh["chi_i"]
    return r
