"""H61 estimators: penalised logistic fitness models, forward chaining by day, held-out scores.

Models (README, "Operational definitions"): B0 intercept, B1 class, B2 poster, B3 class + poster,
B4 class + poster + period day + room size (amendment A1), F full (B3 + seed features), Fm full without poster.
Ridge lam on every non-intercept coefficient (standardised features; poster dummies partially pooled).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import optimize, stats  # noqa: E402

# Amendment A1 (2026-10-04, from synthetic S1, before real data): the period-day term is a kickoff-day indicator
# (log day extrapolated beyond the training range under forward chaining), and standardised features are clipped.
FEATS = ["lg_novel", "lg_len", "spec", "indeg", "f_rec", "addressed", "threaded", "kick", "lg_npres"]
CTRL = ["kick", "lg_npres"]
CLIP = 5.0
SEED = [f for f in FEATS if f not in CTRL]
MODELS = {
    "B0": dict(cls=False, poster=False, feats=[]),
    "B1": dict(cls=True, poster=False, feats=[]),
    "B2": dict(cls=False, poster=True, feats=[]),
    "B3": dict(cls=True, poster=True, feats=[]),
    "B4": dict(cls=True, poster=True, feats=CTRL),
    "F": dict(cls=True, poster=True, feats=FEATS),
    "Fm": dict(cls=True, poster=False, feats=FEATS),
}
LAM = 1.0


def prep(df: pl.DataFrame, spec_col: str = "spec_bge") -> pl.DataFrame:
    """Feature columns (raw scale) from the scheme table."""
    return df.with_columns(
        pl.col("n_novel").cast(pl.Float64).log().alias("lg_novel"),
        pl.col("seed_len").cast(pl.Float64).clip(1, None).log().alias("lg_len"),
        pl.col(spec_col).fill_nan(None).fill_null(pl.col(spec_col).fill_nan(None).median()).alias("spec"),
        pl.col("indeg").cast(pl.Float64),
        pl.col("f_receptive").cast(pl.Float64).alias("f_rec"),
        pl.col("addressed").cast(pl.Float64), pl.col("threaded").cast(pl.Float64),
        (pl.col("day").cast(pl.Float64) + 1).log().alias("lg_day"),
        (pl.col("day") == 0).cast(pl.Float64).alias("kick"),
        pl.col("n_present").cast(pl.Float64).log().alias("lg_npres"),
        (pl.col("reach24") >= 2).cast(pl.Int8).alias("y"), (pl.col("reach24") >= 3).cast(pl.Int8).alias("y3"),
        (pl.col("n_read5") >= 1).cast(pl.Int8).alias("y_read5"), (pl.col("n_unread5") >= 1).cast(pl.Int8).alias("y_unread5"),
    )


def _design(df: pl.DataFrame, spec: dict, tr: np.ndarray, posters_tr: np.ndarray | None = None):
    """X (n x k) with intercept first; standardisation and poster levels from the training rows."""
    n = df.height
    cols = [np.ones(n)]
    names = ["const"]
    pen = [False]
    if spec["cls"]:
        c = df["cls"].to_numpy()
        for k in (0, 1, 3):                     # class N (2) is the reference
            cols.append((c == k).astype(float)); names.append(f"cls{k}"); pen.append(True)
    if spec["poster"]:
        p = df["poster"].to_numpy()
        lv = np.unique(p[tr]) if posters_tr is None else posters_tr
        for a in lv:
            cols.append((p == a).astype(float)); names.append(f"p{a}"); pen.append(True)
    for f in spec["feats"]:
        x = df[f].to_numpy().astype(float)
        mu, sd = x[tr].mean(), x[tr].std()
        cols.append(np.clip((x - mu) / sd, -CLIP, CLIP) if sd > 0 else np.zeros(n)); names.append(f); pen.append(True)
    return np.column_stack(cols), names, np.array(pen)


def fit_logit(X: np.ndarray, y: np.ndarray, pen: np.ndarray, lam: float = LAM, w: np.ndarray | None = None):
    w = np.ones(len(y)) if w is None else w
    ybar = np.clip((w * y).sum() / w.sum(), 1e-4, 1 - 1e-4)
    b0 = np.zeros(X.shape[1]); b0[0] = np.log(ybar / (1 - ybar))

    def f(b):
        z = X @ b
        ll = w * (y * z - np.logaddexp(0, z))
        g = X.T @ (w * (y - 1 / (1 + np.exp(-z))))
        return -ll.sum() + 0.5 * lam * (b[pen] ** 2).sum(), -g + lam * np.where(pen, b, 0)

    r = optimize.minimize(f, b0, jac=True, method="L-BFGS-B", options=dict(maxiter=500))
    return r.x


def hess_se(X, y, b, pen, lam=LAM):
    p = 1 / (1 + np.exp(-(X @ b)))
    H = (X * (p * (1 - p))[:, None]).T @ X + lam * np.diag(pen.astype(float))
    try:
        C = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        C = np.linalg.pinv(H)
    return np.sqrt(np.clip(np.diag(C), 0, None))


def predict(b, X):
    return 1 / (1 + np.exp(-(X @ b)))


def forward_chain(df: pl.DataFrame, ycol: str = "y", models=("B0", "B1", "B2", "B3", "B4", "F", "Fm"),
                  min_train: int = 100, lam: float = LAM) -> pl.DataFrame:
    """Held-out predictions for every idea on a test day with >= min_train ideas on earlier days."""
    day = df["day"].to_numpy()
    y = df[ycol].to_numpy().astype(float)
    out = {m: np.full(df.height, np.nan) for m in models}
    test = np.zeros(df.height, bool)
    for d in np.unique(day):
        tr = day < d
        te = day == d
        if tr.sum() < min_train or y[tr].sum() < 3 or te.sum() == 0:
            continue
        test |= te
        for m in models:
            X, names, pen = _design(df, MODELS[m], tr)
            b = fit_logit(X[tr], y[tr], pen, lam)
            out[m][te] = predict(b, X[te])
    res = df.select("idea", "seed_msg", "day", "reach24", ycol).with_columns(pl.Series("test", test))
    return res.with_columns([pl.Series(f"p_{m}", out[m]) for m in models]).filter(pl.col("test"))


def auc(y, s):
    y = np.asarray(y).astype(bool)
    n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0:
        return np.nan
    r = stats.rankdata(s)
    return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def ll(y, p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return y * np.log(p) + (1 - y) * np.log(1 - p)


def lift(yv, p, q=0.10):
    k = max(1, int(round(q * len(p))))
    top = np.argsort(-p, kind="stable")[:k]
    base = yv.mean()
    return float(yv[top].mean() / base) if base > 0 else np.nan


def cluster_boot(stat_fn, clusters: np.ndarray, B: int, rng) -> np.ndarray:
    """Bootstrap over clusters (seed messages): stat_fn(index array) for each replicate."""
    uc, inv = np.unique(clusters, return_inverse=True)
    members = [[] for _ in range(len(uc))]
    for i, c in enumerate(inv):
        members[c].append(i)
    members = [np.array(m) for m in members]
    out = np.empty(B)
    for b in range(B):
        pick = rng.integers(0, len(uc), len(uc))
        idx = np.concatenate([members[k] for k in pick])
        out[b] = stat_fn(idx)
    return out


def score_period(pred: pl.DataFrame, ycol: str = "y", B: int = 2000, seed: int = 0, ref="B3", full="F",
                 extra_refs=("B1", "B2", "B4")) -> dict:
    y = pred[ycol].to_numpy().astype(float)
    reach = pred["reach24"].to_numpy()
    cl = pred["seed_msg"].to_numpy()
    rng = np.random.default_rng(seed)
    out = dict(n_test=int(len(y)), n_pos=int(y.sum()), base=float(y.mean()), n_days_test=int(pred["day"].n_unique()))
    L = {m: ll(y, pred[f"p_{m}"].to_numpy()) for m in ("B0", "B1", "B2", "B3", "B4", "F", "Fm") if f"p_{m}" in pred.columns}
    for m, v in L.items():
        p = pred[f"p_{m}"].to_numpy()
        out[f"ll_{m}"] = float(v.mean())
        out[f"auc_{m}"] = float(auc(y, p))
        out[f"rho_{m}"] = float(stats.spearmanr(p, reach).statistic) if np.std(p) > 0 else np.nan
    pF = pred[f"p_{full}"].to_numpy()
    y3 = (reach >= 3).astype(float)
    out["lift_y"] = lift(y, pF)
    out["lift_y3"] = lift(y3, pF)
    out["lift_y3_B3"] = lift(y3, pred["p_B3"].to_numpy())
    for r in (ref,) + tuple(extra_refs):
        d = (L[full] - L[r]) * 1000
        bs = cluster_boot(lambda idx: d[idx].mean(), cl, B, rng)
        out[f"dll_{full}_{r}"] = float(d.mean())
        out[f"dll_{full}_{r}_lo"], out[f"dll_{full}_{r}_hi"] = (float(x) for x in np.percentile(bs, [2.5, 97.5]))
        out[f"dll_{full}_{r}_se"] = float(bs.std())
    return out


def coefs(df: pl.DataFrame, ycol: str = "y", model: str = "F", lam: float = LAM) -> dict:
    tr = np.ones(df.height, bool)
    X, names, pen = _design(df, MODELS[model], tr)
    y = df[ycol].to_numpy().astype(float)
    b = fit_logit(X, y, pen, lam)
    se = hess_se(X, y, b, pen, lam)
    return {n: (float(bi), float(si)) for n, bi, si in zip(names, b, se) if not n.startswith("p")}


def gains_conv(df: pl.DataFrame, B: int = 300, seed: int = 1) -> dict | None:
    """O5: AUC gain of F over B1 for read-5 and unread-5 adoption, and the bootstrap CI of their difference."""
    pr = forward_chain(df, "y_read5", models=("B1", "F"))
    pu = forward_chain(df, "y_unread5", models=("B1", "F"))
    # align the two outcomes on the same test ideas (test days can differ when one outcome is rare early on)
    j = pr.join(pu.select("idea", "y_unread5", pl.col("p_B1").alias("pu_B1"), pl.col("p_F").alias("pu_F")),
                on="idea", how="inner")
    pr = j
    pu = j.select("idea", "seed_msg", "y_unread5", pl.col("pu_B1").alias("p_B1"), pl.col("pu_F").alias("p_F"))
    yr, yu = pr["y_read5"].to_numpy(), pu["y_unread5"].to_numpy()
    if yr.sum() < 15 or yu.sum() < 15:
        return dict(n_read5=int(yr.sum()), n_unread5=int(yu.sum()), eligible=False)
    a = lambda yv, p, idx: auc(yv[idx], p[idx])  # noqa: E731
    pFr, pBr, pFu, pBu = (x.to_numpy() for x in (pr["p_F"], pr["p_B1"], pu["p_F"], pu["p_B1"]))
    gr = auc(yr, pFr) - auc(yr, pBr)
    gu = auc(yu, pFu) - auc(yu, pBu)
    cl = pr["seed_msg"].to_numpy()
    rng = np.random.default_rng(seed)
    bs = cluster_boot(lambda idx: (a(yr, pFr, idx) - a(yr, pBr, idx)) - (a(yu, pFu, idx) - a(yu, pBu, idx)), cl, B, rng)
    bs = bs[np.isfinite(bs)]
    return dict(n_read5=int(yr.sum()), n_unread5=int(yu.sum()), eligible=True, g_read=float(gr), g_unread=float(gu),
                diff=float(gr - gu), diff_lo=float(np.percentile(bs, 2.5)), diff_hi=float(np.percentile(bs, 97.5)),
                diff_se=float(bs.std()), auc_F_read=float(auc(yr, pFr)), auc_F_unread=float(auc(yu, pFu)))


def dl_pool(est, se):
    """DerSimonian-Laird random-effects mean, SE, tau^2."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return np.nan, np.nan, np.nan
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = (w * (est - mu_f) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / c) if c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mu = (ws * est).sum() / ws.sum()
    return float(mu), float(np.sqrt(1 / ws.sum())), float(tau2)
