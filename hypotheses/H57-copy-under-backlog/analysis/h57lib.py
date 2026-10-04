"""H57 analysis library: within-agent slopes, the read-set copy/transform decomposition, pointwise information,
agent-stratified permutation tests and random-effects pooling. Content-agnostic: works on real or synthetic outcome
tables produced by scheme/h57core.outcomes (joined to the skeleton).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import math  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE.parent / "scheme"))
import copy_info as CI  # noqa: E402

MODELS = ("bge", "gte")
CONTROLS = ["log_len", "addressed_f", "early_f", "daypos_f"]   # reply vs broadcast = addressed (Amendment 1)


# ------------------------------------------------------------------------------------------------ preparation
def chance_rate(d: pl.DataFrame, n_col: str, hit_col: str, alpha: float = 100.0) -> np.ndarray:
    """Per-pair chance rate from in-flight pairs: per author, shrunk to the period rate with alpha pseudo-pairs."""
    g = d.group_by("agent").agg(pl.col(n_col).sum().alias("n"), pl.col(hit_col).sum().alias("h"))
    qbar = (float(g["h"].sum()) + 0.5) / (float(g["n"].sum()) + 1.0)
    g = g.with_columns(((pl.col("h") + alpha * qbar) / (pl.col("n") + alpha)).alias("q"))
    return d.select("agent").join(g.select("agent", "q"), on="agent", how="left")["q"].to_numpy()


def prepare(df: pl.DataFrame) -> pl.DataFrame:
    """Analysis sample: k >= 1. Chance-corrected outcomes (Amendment 1) and controls.
    e_{m}   = echo_{m}_R - [1 - (1 - q_m)^k]        (q_m from in-flight pairs; m in bge, gte, both)
    mkn_{f} = mk_near_{f}_R - [1 - (1 - q_mk)^k]    (statements with >= 3 markers)
    Descriptive (mirrored placebo, biased; see Amendment 1): em_{m} = echo_R - echo_F, mks_{f} = share_R - share_F."""
    d = df.filter(pl.col("k") >= 1)
    d = d.with_columns(
        (pl.col("k").cast(pl.Float64) + 1).log(2).alias("logk"),
        pl.col("n_chars").cast(pl.Float64).clip(1, None).log(2).alias("log_len"),
        pl.col("is_reply").cast(pl.Float64).alias("is_reply_f"),
        pl.col("addressed").cast(pl.Float64).alias("addressed_f"),
        pl.col("early").cast(pl.Float64).alias("early_f"),
        pl.col("daypos").fill_null(0.5).cast(pl.Float64).alias("daypos_f"),
        (pl.col("agent").cast(pl.Utf8) + "|" + pl.col("unit_id").fill_null("u")).alias("g_agent_unit"),
        (pl.col("lab").fill_null("?") + "|" + pl.col("unit_id").fill_null("u")).alias("g_lab_unit"),
        (pl.col("agent").cast(pl.Utf8) + "|" + pl.col("pt_date")).alias("cl_agent_day"),
        (pl.col("n_pool_all").fill_null(0) >= 40).cast(pl.Int8).alias("pool_sat"),
    )
    k = d["k"].to_numpy().astype(float)
    ex = {}
    echo_both_R = d["echo_both_R"].to_numpy()
    for m in MODELS + ("both",):
        er = d[f"echo_{m}_R"].to_numpy() if m != "both" else echo_both_R
        q = chance_rate(d, "nI", f"nnear_{m}_Ins")          # primary: siblings excluded (Amendment 1b)
        qs = chance_rate(d, "nI", f"nnear_{m}_I")           # sensitivity: siblings counted as chance
        ex[f"q_{m}"] = q
        ex[f"chance_{m}"] = 1 - (1 - q) ** k
        ex[f"e_{m}"] = er - (1 - (1 - q) ** k)
        ex[f"es_{m}"] = er - (1 - (1 - qs) ** k)
        ex[f"er_{m}"] = er
    for f in ("all", "rare"):
        dm = d.with_columns(pl.when(pl.col(f"mk_n_{f}") >= 3).then(pl.col("nI")).otherwise(0).alias("_nI"))
        q = chance_rate(dm, "_nI", f"nmknear_{f}_Ins")
        qs = chance_rate(dm, "_nI", f"nmknear_{f}_I")
        ex[f"q_mk_{f}"] = q
        ex[f"mkn_{f}"] = d[f"mk_near_{f}_R"].to_numpy() - (1 - (1 - q) ** k)
        ex[f"mkns_{f}"] = d[f"mk_near_{f}_R"].to_numpy() - (1 - (1 - qs) ** k)
        ex[f"mkr_{f}"] = d[f"mk_near_{f}_R"].to_numpy()
    # lag-matched chance (Amendment 2, post hoc): q_b per lag bin from non-sibling in-flight pairs (period-level,
    # shrunk to the period rate with 50 pseudo-pairs); chance = 1 - prod_b (1 - q_b)^{nR_b}
    nb_ = sum(1 for c in d.columns if c.startswith("nR_b"))
    if nb_:
        for m in MODELS + ("both",):
            er = d[f"echo_{m}_R"].to_numpy() if m != "both" else echo_both_R
            tot_n = sum(float(d[f"nI_b{j}"].sum()) for j in range(nb_))
            tot_h = sum(float(d[f"nnear_{m}_I_b{j}"].sum()) for j in range(nb_))
            qbar = (tot_h + 0.5) / (tot_n + 1.0)
            logp = np.zeros(d.height)
            for j in range(nb_):
                qb = (float(d[f"nnear_{m}_I_b{j}"].sum()) + 50 * qbar) / (float(d[f"nI_b{j}"].sum()) + 50)
                ex[f"qlag_{m}_b{j}"] = np.full(d.height, qb)
                logp += d[f"nR_b{j}"].to_numpy() * np.log1p(-min(qb, 0.999))
            ex[f"chancelag_{m}"] = 1 - np.exp(logp)
            ex[f"el_{m}"] = er - (1 - np.exp(logp))
            # short-lag count version (read items < 60 s old, where in-flight pairs exist; bin-specific rates with
            # a Jeffreys prior, no pooling across bins)
            if f"nnear_{m}_R_b0" in d.columns:
                cs, es_ = 0.0, 0.0
                for j in range(nb_ - 1):
                    qj = (float(d[f"nnear_{m}_I_b{j}"].sum()) + 0.5) / (float(d[f"nI_b{j}"].sum()) + 1.0)
                    cs = cs + d[f"nnear_{m}_R_b{j}"].to_numpy().astype(float)
                    es_ = es_ + d[f"nR_b{j}"].to_numpy() * qj
                ex[f"els_{m}"] = cs - es_
                ex[f"nshort_{m}"] = sum(d[f"nR_b{j}"].to_numpy() for j in range(nb_ - 1)).astype(float)
            # count version (linear in pairs, valid when chance near-copies are correlated within a statement)
            if f"nnear_{m}_R_b0" in d.columns:
                cnt = sum(d[f"nnear_{m}_R_b{j}"].to_numpy().astype(float) for j in range(nb_))
                exp_ = sum(d[f"nR_b{j}"].to_numpy() * ex[f"qlag_{m}_b{j}"] for j in range(nb_))
                ex[f"nearcount_{m}"] = cnt
                ex[f"elc_{m}"] = cnt - exp_
        for f in ("all", "rare"):
            ok3 = d[f"mk_n_{f}"].to_numpy() >= 3
            tot_n = sum(float(d[f"nI_b{j}"].to_numpy()[ok3].sum()) for j in range(nb_))
            tot_h = sum(float(d[f"nmknear_{f}_I_b{j}"].sum()) for j in range(nb_))
            qbar = (tot_h + 0.5) / (tot_n + 1.0)
            logp = np.zeros(d.height)
            for j in range(nb_):
                qb = (float(d[f"nmknear_{f}_I_b{j}"].sum()) + 50 * qbar) / (float(d[f"nI_b{j}"].to_numpy()[ok3].sum()) + 50)
                logp += d[f"nR_b{j}"].to_numpy() * np.log1p(-min(qb, 0.999))
            ex[f"mkl_{f}"] = d[f"mk_near_{f}_R"].to_numpy() - (1 - np.exp(logp))
            if f"nmknear_{f}_R_b0" in d.columns:
                cs, es_ = 0.0, 0.0
                for j in range(nb_ - 1):
                    qj = (float(d[f"nmknear_{f}_I_b{j}"].sum()) + 0.5) / (float(d[f"nI_b{j}"].to_numpy()[ok3].sum()) + 1.0)
                    cs = cs + d[f"nmknear_{f}_R_b{j}"].to_numpy().astype(float)
                    es_ = es_ + d[f"nR_b{j}"].to_numpy() * qj
                ex[f"mkls_{f}"] = np.where(ok3, cs - es_, np.nan)
                cnt = sum(d[f"nmknear_{f}_R_b{j}"].to_numpy().astype(float) for j in range(nb_))
                exp_ = 0.0
                for j in range(nb_):
                    qb = (float(d[f"nmknear_{f}_I_b{j}"].sum()) + 50 * qbar) / (float(d[f"nI_b{j}"].to_numpy()[ok3].sum()) + 50)
                    exp_ = exp_ + d[f"nR_b{j}"].to_numpy() * qb
                ex[f"mklc_{f}"] = np.where(ok3, cnt - exp_, np.nan)
    d = d.with_columns(**{kk: pl.Series(v) for kk, v in ex.items()})
    if nb_:
        d = d.with_columns(pl.col(c).fill_nan(None) for f in ("all", "rare")
                           for c in (f"mkl_{f}", f"mklc_{f}", f"mkls_{f}") if c in d.columns)
    d = d.with_columns(pl.col(c).fill_nan(None) for f in ("all", "rare") for c in (f"mkn_{f}", f"mkns_{f}", f"mkr_{f}"))
    mir = {}
    for m in MODELS + ("both",):
        mir[f"em_{m}"] = pl.when(pl.col("f_full")).then(pl.col(f"echo_{m}_R") - pl.col(f"echo_{m}_F"))
    for f in ("all", "rare"):
        mir[f"mks_{f}"] = pl.when(pl.col("f_full")).then(pl.col(f"mk_share_{f}_R") - pl.col(f"mk_share_{f}_F"))
    d = d.with_columns(**mir)
    # addressed-channel outcomes only where the addressed source is unambiguous (named author has one read item)
    addr_cols = [c for c in d.columns if c.endswith("_addr") and (c.startswith("near_") or c.startswith("mkj_"))]
    return d.with_columns(pl.when(pl.col("addr_n") == 1).then(pl.col(c)).otherwise(None).alias(c) for c in addr_cols)


# ------------------------------------------------------------------------------------------------ FE regression
def _codes(a) -> np.ndarray:
    _, inv = np.unique(np.asarray(a), return_inverse=True)
    return inv


def demean(M: np.ndarray, groups: list[np.ndarray], iters: int = 50, tol: float = 1e-10) -> np.ndarray:
    """Within transformation for one or more sets of fixed effects (alternating projections)."""
    M = M.astype(np.float64).copy()
    if M.ndim == 1:
        M = M[:, None]
    for _ in range(iters if len(groups) > 1 else 1):
        prev = M.copy()
        for g in groups:
            cnt = np.bincount(g)
            for j in range(M.shape[1]):
                M[:, j] -= (np.bincount(g, weights=M[:, j]) / np.maximum(cnt, 1))[g]
        if len(groups) == 1 or np.max(np.abs(M - prev)) < tol:
            break
    return M


def fe_ols(y, X, fe: list, cluster, names: list[str]) -> dict:
    """OLS of y on X after absorbing fixed effects; CR1 cluster-robust SEs. Returns coefficient dict."""
    y = np.asarray(y, np.float64)
    X = np.asarray(X, np.float64)
    ok = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    y, X = y[ok], X[ok]
    fe = [_codes(np.asarray(f)[ok]) for f in fe]
    cl = _codes(np.asarray(cluster)[ok])
    n = len(y)
    if n < 30:
        return {"n": n}
    Z = demean(np.column_stack([y, X]), fe)
    yt, Xt = Z[:, 0], Z[:, 1:]
    keep = np.std(Xt, axis=0) > 1e-9
    Xt = Xt[:, keep]
    nm = [nme for nme, k in zip(names, keep) if k]
    XtX = Xt.T @ Xt
    try:
        inv = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        return {"n": n}
    b = inv @ (Xt.T @ yt)
    u = yt - Xt @ b
    G = cl.max() + 1
    S = np.zeros((Xt.shape[1], Xt.shape[1]))
    sc = np.zeros((G, Xt.shape[1]))
    np.add.at(sc, cl, Xt * u[:, None])
    S = sc.T @ sc
    n_fe = sum(len(np.unique(f)) for f in fe)
    dof = max(1, n - Xt.shape[1] - n_fe)
    corr = (G / max(1, G - 1)) * ((n - 1) / dof)
    V = inv @ S @ inv * corr
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    out = {"n": int(n), "n_clusters": int(G)}
    for j, nme in enumerate(nm):
        z = b[j] / se[j] if se[j] > 0 else np.nan
        out[nme] = {"b": float(b[j]), "se": float(se[j]), "z": float(z),
                    "p": float(2 * stats.t.sf(abs(z), df=max(1, G - 1))) if np.isfinite(z) else np.nan}
    return out


def slope(d: pl.DataFrame, y: str, spec: str = "agent", x: str = "logk", extra: list[str] | None = None) -> dict:
    """Within-period slope of outcome y on log2(1+k) with the card's controls.
    spec: agent (agent x unit FE), day (agent x unit + day FE), lab (family x unit FE), none (unit FE)."""
    dd = d.filter(pl.col(y).is_not_null() & pl.col(y).is_finite())
    if dd.height < 30:
        return {"n": dd.height}
    ctrl = [c for c in CONTROLS if not (spec == "day" and c == "early_f")]
    if y.startswith(("pc_", "pt_", "pi_", "near_", "mkj_")):    # source-channel outcomes: all addressed / replies
        ctrl = [c for c in ctrl if c != "addressed_f"]
        if y.endswith("_par") or y.startswith(("pcp_", "ptp_")):
            ctrl = ctrl + ["pool_sat_f"]
            dd = dd.with_columns(pl.col("pool_sat").cast(pl.Float64).alias("pool_sat_f"))
    cols = [x] + ctrl + (extra or [])
    X = dd.select(cols).to_numpy()
    if spec == "agent":
        fe = [dd["g_agent_unit"].to_numpy()]
    elif spec == "day":
        fe = [dd["g_agent_unit"].to_numpy(), dd["pt_date"].to_numpy()]
    elif spec == "lab":
        fe = [dd["g_lab_unit"].to_numpy()]
    else:
        fe = [dd["unit_id"].fill_null("u").to_numpy()]
    r = fe_ols(dd[y].to_numpy(), X, fe, dd["cl_agent_day"].to_numpy(), cols)
    r["mean_y"] = float(dd[y].mean())
    return r


# ------------------------------------------------------------------------------------------------ decomposition
def k_bins(k: np.ndarray) -> np.ndarray:
    """0 = bottom (k <= q1/3), 2 = top (k > q2/3), 1 = middle; on the period's observed k."""
    q1, q2 = np.quantile(k, [1 / 3, 2 / 3])
    if q2 <= q1:                       # heavy ties at small k
        q2 = np.min(k[k > q1]) if np.any(k > q1) else q1
    return np.where(k <= q1, 0, np.where(k > q2, 2, 1))


def _share(x, y):
    """Copy share s = I_copy / I with Miller-Madow bias corrections (plug-in values from copy_info.mi_parts).
    I_MM = I - (B_xy - B_x - B_y + 1) / (2 n ln 2); I_copy_MM = I_copy - sum_x p(x) / (2 n_x ln 2) over the copy terms."""
    n = len(x)
    if n < 10:
        return np.nan, np.nan, np.nan
    xi, yi, _ = CI.encode(list(x), list(y))
    c, kappa, I, Ic = CI.mi_parts(xi, yi)
    m = max(xi.max(), yi.max()) + 1
    Bx = len(np.unique(xi)); By = len(np.unique(yi)); Bxy = len(np.unique(xi.astype(np.int64) * m + yi))
    I_mm = I - (Bxy - Bx - By + 1) / (2 * n * np.log(2))
    nx = np.bincount(xi, minlength=m)
    py = np.bincount(yi, minlength=m) / n
    ncopy = np.bincount(xi[xi == yi], minlength=m)
    vals = np.nonzero(nx)[0]
    act = (ncopy[vals] / nx[vals]) > py[vals]
    Ic_mm = Ic - np.sum((nx[vals][act] / n) / (2 * nx[vals][act] * np.log(2)))
    Ic_mm = max(Ic_mm, 0.0)
    return (Ic_mm / I_mm if I_mm > 0 else np.nan), I_mm, Ic_mm


def near_code(x: np.ndarray, y: np.ndarray, near: np.ndarray, K: int) -> np.ndarray:
    """Message-level copy coding (Amendment 1b): Y = X only if B is a near-copy of its source; a same-cluster
    non-copy becomes the distinct symbol X + K ('same topic, changed'), which counts as transformation."""
    nr = np.nan_to_num(np.asarray(near, dtype=float)) == 1
    return np.where(nr, x, np.where(y == x, x + K, y))


def reply_trend(x, y, b) -> tuple[float, dict]:
    s0, I0, Ic0 = _share(x[b == 0], y[b == 0])
    s2, I2, Ic2 = _share(x[b == 2], y[b == 2])
    return s2 - s0, {"s_bottom": s0, "s_top": s2, "I_bottom": I0, "I_top": I2, "Ic_bottom": Ic0, "Ic_top": Ic2}


def decomposition(d: pl.DataFrame, model: str, K: int = 32, n_perm: int = 500, n_null: int = 100,
                  seed: int = 0, src: str = "addr", coding: str = "near") -> dict:
    """Source channel (Amendment 1): copy/transform decomposition of (code(source), code(B)) by k tercile;
    src = addr (addressed source, primary) or par (DQ2 parent, descriptive). T = s(top) - s(bottom), s = I_copy / I
    (Miller-Madow); one-sided p from permuting k within agent x unit (x pool stratum for par)."""
    dd = d.filter(pl.col(f"x{src}_{model}_K{K}") >= 0)
    if src == "addr":
        dd = dd.filter(pl.col("addr_n") == 1)      # unambiguous addressed source (named author has one read item)
    if dd.height < 60:
        return {"n": dd.height}
    x = dd[f"x{src}_{model}_K{K}"].to_numpy()
    y = dd[f"y_{model}_K{K}"].to_numpy()
    if coding == "near":
        y = near_code(x, y, dd[f"near_{model}_{src}"].to_numpy(), K)
    k = dd["k"].to_numpy().astype(float)
    grp = _codes((dd["g_agent_unit"] + ("|" + dd["pool_sat"].cast(pl.Utf8) if src == "par" else "")).to_numpy())
    b = k_bins(k)
    T, parts = reply_trend(x, y, b)
    rng = np.random.default_rng(seed)
    order = np.argsort(grp, kind="stable")
    starts = np.r_[0, np.flatnonzero(np.diff(grp[order])) + 1, len(grp)]
    null = []
    for _ in range(n_perm):
        bp = b.copy()
        for a, e in zip(starts[:-1], starts[1:]):
            idx = order[a:e]
            bp[idx] = b[rng.permutation(idx)]
        null.append(reply_trend(x, y, bp)[0])
    null = np.array(null)
    null = null[np.isfinite(null)]
    p_one = float((np.sum(null >= T) + 1) / (len(null) + 1)) if np.isfinite(T) and len(null) else np.nan
    out = {"n": int(dd.height), "K": K, "src": src, "coding": coding, "T": float(T), "p_one": p_one,
           "z": float((T - null.mean()) / null.std()) if len(null) > 2 and null.std() > 0 else np.nan,
           "null_mean": float(null.mean()) if len(null) else np.nan, **{k_: float(v) for k_, v in parts.items()}}
    if n_null:
        for j, nmb in ((0, "bottom"), (1, "middle"), (2, "top")):
            m = b == j
            if m.sum() >= 10:
                r = CI.decompose(list(x[m]), list(y[m]), n_null=n_null, seed=seed + j)
                for key in ("n", "c", "kappa", "I", "I_copy", "I_transform", "I_ex", "I_copy_ex", "I_transform_ex"):
                    out[f"{nmb}_{key}"] = float(r[key]) if key in r else np.nan
    return out


def pointwise(x: np.ndarray, y: np.ndarray, fold: np.ndarray, K: int, alpha: float = 0.5, Ky: int | None = None):
    """Cross-fitted pointwise information i, copy part c and transformation part t (bits) per pair.
    X in 0..K-1, Y in 0..Ky-1 (Ky >= K; the copy symbol for x is y = x)."""
    Ky = Ky or K
    n = len(x)
    i = np.full(n, np.nan)
    c = np.full(n, np.nan)
    folds = np.unique(fold)
    for f in folds:
        te = fold == f
        tr = ~te if len(folds) > 1 else np.ones(n, bool)
        N = np.full((K, Ky), alpha)
        np.add.at(N, (x[tr], y[tr]), 1.0)
        pyx = N / N.sum(1, keepdims=True)
        py = N.sum(0) / N.sum()
        a = pyx[np.arange(K), np.arange(K)]
        xs, ys = x[te], y[te]
        i[te] = np.log2(pyx[xs, ys] / py[ys])
        ax, bx = a[xs], py[xs]
        cc = np.where(xs == ys, np.log2(ax / bx), np.log2((1 - ax) / (1 - bx)))
        c[te] = np.where(ax > bx, cc, 0.0)
    return i, c, i - c


def add_pointwise(d: pl.DataFrame, model: str, K: int = 32, src: str = "addr") -> pl.DataFrame:
    """Pointwise copy (pc_m), transformation (pt_m) and total (pi_m) information of each source pair."""
    dd = d.filter(pl.col(f"x{src}_{model}_K{K}") >= 0)
    if src == "addr":
        dd = dd.filter(pl.col("addr_n") == 1)
    if dd.height < 30:
        return d.with_columns(pl.lit(None, dtype=pl.Float64).alias(f"pc_{model}"),
                              pl.lit(None, dtype=pl.Float64).alias(f"pt_{model}"),
                              pl.lit(None, dtype=pl.Float64).alias(f"pi_{model}"))
    days = dd["pt_date"].to_numpy()
    if len(np.unique(days)) >= 2:
        fold = _codes(days)
    else:
        fold = (dd["t"].dt.hour().to_numpy().astype(int) + dd["agent"].to_numpy().astype(int)) % 2
    x = dd[f"x{src}_{model}_K{K}"].to_numpy()
    yc = near_code(x, dd[f"y_{model}_K{K}"].to_numpy(), dd[f"near_{model}_{src}"].to_numpy(), K)
    i, c, t = pointwise(x, yc, fold, K, Ky=2 * K)
    dd = dd.select("sid").with_columns(pl.Series(f"pi_{model}", i), pl.Series(f"pc_{model}", c),
                                       pl.Series(f"pt_{model}", t))
    return d.join(dd, on="sid", how="left")


# ------------------------------------------------------------------------------------------------ pooling
def random_effects(b: list[float], se: list[float]) -> dict:
    b, se = np.asarray(b, float), np.asarray(se, float)
    ok = np.isfinite(b) & np.isfinite(se) & (se > 0)
    b, se = b[ok], se[ok]
    k = len(b)
    if k == 0:
        return {"k": 0}
    w = 1 / se ** 2
    bf = np.sum(w * b) / np.sum(w)
    Q = float(np.sum(w * (b - bf) ** 2))
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - (k - 1)) / c) if c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    br = float(np.sum(ws * b) / np.sum(ws))
    ser = float(math.sqrt(1 / np.sum(ws)))
    return {"k": int(k), "b": br, "se": ser, "lo": br - 1.96 * ser, "hi": br + 1.96 * ser,
            "p": float(2 * stats.norm.sf(abs(br / ser))), "tau2": float(tau2), "Q": Q, "fixed_b": float(bf),
            "n_pos": int(np.sum(b > 0)), "n_sig_pos": int(np.sum((b / se) > 1.96)),
            "n_sig_neg": int(np.sum((b / se) < -1.96))}


def stouffer(ps: list[float]) -> float:
    ps = np.clip(np.asarray([p for p in ps if np.isfinite(p)]), 1e-12, 1 - 1e-12)
    if len(ps) == 0:
        return np.nan
    z = stats.norm.isf(ps)
    return float(stats.norm.sf(z.sum() / math.sqrt(len(z))))


def bget(r: dict, name: str = "logk", key: str = "b"):
    v = r.get(name)
    return v.get(key, np.nan) if isinstance(v, dict) else np.nan
