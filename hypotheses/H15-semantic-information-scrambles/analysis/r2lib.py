"""H15 round 2 estimators (R1-R3). Used by r2_synthetic.py and r2_run.py.

Poisson pseudo-ML with stratum x arm fixed effects (semantic_kappa.poisson_fe for the point estimate) plus a
cluster-robust sandwich variance; cluster bootstrap helper; DerSimonian-Laird pool; trail classes; R3 recall
statistics on hashed term sets with period IDF weights.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from semantic_kappa import dl_pool, poisson_fe  # noqa: E402,F401

import math  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

DATA = ROOT / "data/processed/H15-semantic-information-scrambles/r2"
PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
FOLDER = {"G36": "G36b"}


def codes(a) -> np.ndarray:
    return np.unique(np.asarray(a), return_inverse=True)[1]


# ------------------------------------------------------------------------------------------- Poisson FE + sandwich
def poisson_fe_se(V, X, groups, clusters):
    """beta (semantic_kappa.poisson_fe) and cluster-robust sandwich SEs of the concentrated Poisson score."""
    V = np.asarray(V, float)
    X = np.asarray(X, float)
    g = codes(groups)
    cl = codes(clusters)
    tot = np.bincount(g, weights=V)
    keep = tot[g] > 0
    V, X, g, cl = V[keep], X[keep], codes(g[keep]), codes(cl[keep])
    beta = poisson_fe(V, X, g)
    k = X.shape[1]
    if not np.all(np.isfinite(beta)):
        return beta, np.full(k, np.nan), int(keep.sum())
    tot = np.bincount(g, weights=V)
    eta = X @ beta
    e = np.exp(eta - eta.max())
    mu = e * (tot / np.bincount(g, weights=e))[g]
    wsum = np.bincount(g, weights=mu)
    xbar = np.column_stack([np.bincount(g, weights=mu * X[:, j]) / wsum for j in range(k)])[g]
    Xc = X - xbar
    H = (Xc * mu[:, None]).T @ Xc
    sc = Xc * (V - mu)[:, None]
    S = np.column_stack([np.bincount(cl, weights=sc[:, j]) for j in range(k)])
    try:
        Hi = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        return beta, np.full(k, np.nan), int(keep.sum())
    vc = Hi @ (S.T @ S) @ Hi
    return beta, np.sqrt(np.clip(np.diag(vc), 0, None)), int(keep.sum())


def design(df: pl.DataFrame, classes: list[str], vpre: bool = True) -> tuple[np.ndarray, list[str]]:
    F = (df["etype"] == "F").to_numpy().astype(float)
    cols, names = [], []
    for c in classes:
        x = df[c].cast(pl.Float64).to_numpy()
        cols += [x, x * F]
        names += [c, f"{c}xF"]
    if vpre:
        cols.append(np.log1p(np.clip(df["V_pre"].to_numpy(), 0, None)))
        names.append("log1p_Vpre")
    return np.column_stack(cols), names


def fe_groups(df: pl.DataFrame) -> np.ndarray:
    return (df["stratum"] + "|" + df["etype"]).to_numpy()


def fit(df: pl.DataFrame, y: str, classes: list[str], vpre: bool = True) -> dict:
    X, names = design(df, classes, vpre)
    V = df[y].to_numpy().astype(float)
    ok = np.isfinite(V) & np.all(np.isfinite(X), axis=1)
    b, se, n_used = poisson_fe_se(V[ok], X[ok], fe_groups(df)[ok], df["cluster"].to_numpy()[ok])
    out = {"n": int(ok.sum()), "n_used": n_used, "n_F": int(((df["etype"] == "F").to_numpy() & ok).sum())}
    for nm, bi, si in zip(names, b, se):
        out[nm] = {"b": float(bi), "se": float(si)}
    return out


def boot_fit(df: pl.DataFrame, y: str, classes: list[str], B: int, seed: int, vpre: bool = True) -> dict:
    """Agent-day cluster bootstrap of the interaction coefficients (strata keep their labels; clusters are nested in
    strata, so a duplicated cluster stays in its stratum)."""
    rng = np.random.default_rng(seed)
    X, names = design(df, classes, vpre)
    V = df[y].to_numpy().astype(float)
    ok = np.isfinite(V) & np.all(np.isfinite(X), axis=1)
    X, V = X[ok], V[ok]
    grp = codes(fe_groups(df)[ok])
    cl = codes(df["cluster"].to_numpy()[ok])
    order = np.argsort(cl, kind="stable")
    starts = np.searchsorted(cl[order], np.arange(cl.max() + 1))
    ends = np.append(starts[1:], len(cl))
    draws = []
    for _ in range(B):
        pick = rng.integers(0, cl.max() + 1, cl.max() + 1)
        idx = np.concatenate([order[starts[p]:ends[p]] for p in pick])
        bb = poisson_fe(V[idx], X[idx], grp[idx])
        draws.append(bb)
    D = np.array(draws)
    res = {}
    for j, nm in enumerate(names):
        d = D[:, j]
        d = d[np.isfinite(d)]
        res[nm] = {"lo": float(np.percentile(d, 2.5)), "hi": float(np.percentile(d, 97.5)), "n_ok": int(len(d))} \
            if len(d) > 10 else {"lo": float("nan"), "hi": float("nan"), "n_ok": int(len(d))}
    return res


def rr(b: float) -> float:
    return float(math.exp(b)) if np.isfinite(b) else float("nan")


def pool(per: dict, key: str) -> dict:
    """DL pool of per-period interaction coefficients (log scale) -> RR scale."""
    est = [per[p][key]["b"] for p in per if key in per[p]]
    se = [per[p][key]["se"] for p in per if key in per[p]]
    d = dl_pool(est, se)
    return {"RR": rr(d["est"]), "lo": rr(d["lo"]), "hi": rr(d["hi"]), "k": d["k"], "tau": d["tau"],
            "b": d["est"], "se": d.get("se", float("nan"))}


# ------------------------------------------------------------------------------------------- frames
def load_events(min_win: int = 10) -> pl.DataFrame:
    e = pl.read_parquet(DATA / "events.parquet").filter(pl.col("n_win") >= min_win)
    return e


def trail_classes(e: pl.DataFrame, col: str = "trail24") -> pl.DataFrame:
    """T0 none; T1 1..period median of the positive values; T2 above (sample: A_prev defined)."""
    e = e.filter(pl.col("A_prev") >= 0)
    med = e.filter(pl.col(col) > 0).group_by("period").agg(pl.col(col).median().alias("__m"))
    e = e.join(med, on="period", how="left")
    return e.with_columns(((pl.col(col) > 0) & (pl.col(col) <= pl.col("__m"))).alias("T1"),
                          (pl.col(col) > pl.col("__m")).alias("T2")).drop("__m")


def u_classes(e: pl.DataFrame) -> pl.DataFrame:
    u12 = pl.col("L") | pl.col("M")
    return e.with_columns(u12.alias("U12"), ((pl.col("L35") | pl.col("M35")) & ~u12).alias("U35"))


# ------------------------------------------------------------------------------------------- R3 recall
def idf_maps(notes: pl.DataFrame) -> dict:
    """period -> (sorted term array, idf array): idf = log(N_u / df_u) over the period's notes."""
    out = {}
    for (p,), sub in notes.group_by(["period"]):
        allt = np.concatenate([np.asarray(x, np.int64) for x in sub["terms"].to_list() if len(x)] or [np.zeros(0, np.int64)])
        u, cnt = np.unique(allt, return_counts=True)
        out[p] = (u, np.log(sub.height / cnt))
    return out


def weights(terms: np.ndarray, idf) -> np.ndarray:
    u, w = idf
    i = np.searchsorted(u, terms)
    i = np.clip(i, 0, len(u) - 1)
    return np.where(u[i] == terms, w[i], 0.0)


def recall(terms: np.ndarray, w: np.ndarray, X: np.ndarray) -> float:
    if len(terms) == 0 or w.sum() <= 0:
        return float("nan")
    return float((w * np.isin(terms, X, assume_unique=True)).sum() / w.sum())


def r3_table(notes: pl.DataFrame, post: list | None = None, post10: list | None = None, post31: list | None = None,
             seed: int = 0, n_null: int = 3, min_days: int = 3) -> pl.DataFrame:
    """Per-note recall statistics. `post*` (lists of int64 arrays aligned with `notes`) override the observed windows
    (synthetic worlds). Returns one row per note with r_post, r_pre, E_x, E_s, novel variants and decay terms."""
    rng = np.random.default_rng(seed)
    idf = idf_maps(notes)
    T = [np.asarray(x, np.int64) for x in notes["terms"].to_list()]
    PRE = [np.asarray(x, np.int64) for x in notes["pre"].to_list()]
    POST = post if post is not None else [np.asarray(x, np.int64) for x in notes["post"].to_list()]
    P10 = post10 if post10 is not None else [np.asarray(x, np.int64) for x in notes["post10"].to_list()]
    P31 = post31 if post31 is not None else [np.asarray(x, np.int64) for x in notes["post31"].to_list()]
    per = notes["period"].to_list()
    ag = notes["agent"].to_numpy()
    tt = notes["t"].to_numpy().astype("datetime64[us]").astype(np.int64)
    dnum = notes["pt_date"].str.to_date().to_numpy().astype("datetime64[D]").astype(np.int64)
    W = [weights(T[i], idf[per[i]]) for i in range(len(T))]
    # previous note of the same agent (any period) for novel terms
    order = np.lexsort((tt, ag))
    prev = np.full(len(T), -1)
    for a_, b_ in zip(order[:-1], order[1:]):
        if ag[a_] == ag[b_]:
            prev[b_] = a_
    NOV = []
    for i in range(len(T)):
        excl = PRE[i] if prev[i] < 0 else np.union1d(PRE[i], T[prev[i]])
        NOV.append(~np.isin(T[i], excl))
    # index by period
    by_p = {}
    for i, p in enumerate(per):
        by_p.setdefault(p, []).append(i)
    rows = {k: [] for k in ("r_post", "r_pre", "r_x", "r_s", "E_x", "E_s", "r_nov", "Enov_x", "Enov_s", "E10_s",
                            "E31_s", "nov_w", "n_terms")}
    nan = float("nan")
    for p, idx in by_p.items():
        idx = np.array(idx)
        tp, ap, dp = tt[idx], ag[idx], dnum[idx]
        for j, i in enumerate(idx):
            Ti, Wi = T[i], W[i]
            rows["n_terms"].append(len(Ti))
            rp = recall(Ti, Wi, POST[i])
            rows["r_post"].append(rp)
            rows["r_pre"].append(recall(Ti, Wi, PRE[i]) if len(PRE[i]) or notes["n_pre"][int(i)] > 0 else nan)
            nv = NOV[i]
            rows["nov_w"].append(float(Wi[nv].sum() / Wi.sum()) if Wi.sum() > 0 else nan)
            rn = recall(Ti[nv], Wi[nv], POST[i]) if nv.any() else nan
            rows["r_nov"].append(rn)
            # cross-agent notes: up to n_null other agents, closest in time
            oth = np.flatnonzero(ap != ag[i])
            if len(oth):
                oo = oth[np.argsort(np.abs(tp[oth] - tt[i]))]
                seen, pick = set(), []
                for k in oo:
                    if ap[k] not in seen:
                        seen.add(ap[k])
                        pick.append(idx[k])
                    if len(pick) == n_null:
                        break
                rx = [recall(T[k], W[k], POST[i]) for k in pick]
                rnx = []
                for k in pick:
                    m = ~np.isin(T[k], PRE[i])
                    if m.any():
                        rnx.append(recall(T[k][m], W[k][m], POST[i]))
                rxm = np.nanmean(rx) if rx else nan
                rows["r_x"].append(rxm)
                rows["E_x"].append(rp - rxm)
                rows["Enov_x"].append(rn - np.nanmean(rnx) if rnx and rn == rn else nan)
            else:
                rows["r_x"].append(nan); rows["E_x"].append(nan); rows["Enov_x"].append(nan)
            # window swap: same agent, same period, >= min_days apart
            far = np.flatnonzero((ap == ag[i]) & (np.abs(dp - dnum[i]) >= min_days))
            if len(far):
                pick = idx[rng.choice(far, size=min(n_null, len(far)), replace=False)]
                rs = np.nanmean([recall(Ti, Wi, POST[k]) for k in pick])
                rows["r_s"].append(rs)
                rows["E_s"].append(rp - rs)
                rows["Enov_s"].append(rn - np.nanmean([recall(Ti[nv], Wi[nv], POST[k]) for k in pick]) if nv.any() else nan)
                rows["E10_s"].append(recall(Ti, Wi, P10[i]) - np.nanmean([recall(Ti, Wi, P10[k]) for k in pick]))
                ok31 = [k for k in pick if len(P31[k])]
                rows["E31_s"].append(recall(Ti, Wi, P31[i]) - np.nanmean([recall(Ti, Wi, P31[k]) for k in ok31])
                                     if len(P31[i]) and ok31 else nan)
            else:
                for k in ("r_s", "E_s", "Enov_s", "E10_s", "E31_s"):
                    rows[k].append(nan)
    flat_idx = np.concatenate([np.array(v) for v in by_p.values()])
    out = notes.select("event_index", "agent", "pt_date", "period", "n_post", "n_pre")[flat_idx]
    return out.with_columns(**{k: pl.Series(k, v, dtype=pl.Float64) for k, v in rows.items()})


def cluster_mean_ci(x: np.ndarray, cl: np.ndarray, B: int = 400, seed: int = 0) -> dict:
    ok = np.isfinite(x)
    x, cl = x[ok], codes(cl[ok])
    if len(x) < 5:
        return {"est": float("nan"), "lo": float("nan"), "hi": float("nan"), "se": float("nan"), "n": int(len(x))}
    s = np.bincount(cl, weights=x)
    c = np.bincount(cl).astype(float)
    rng = np.random.default_rng(seed)
    K = len(c)
    bs = []
    for _ in range(B):
        w = np.bincount(rng.integers(0, K, K), minlength=K)
        bs.append((w * s).sum() / (w * c).sum())
    bs = np.array(bs)
    return {"est": float(x.mean()), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
            "se": float(bs.std()), "n": int(len(x)), "n_clusters": int(K)}
