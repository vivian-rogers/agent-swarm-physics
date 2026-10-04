"""H46 estimator library: day tables, unbiased boundary displacements, placebo percentiles, class tests, fingerprint
classifier, ridge information (Kolchinsky-Wolpert observational bound) and the NE41 pair statistic.

Everything takes plain arrays / polars frames so the synthetic validation runs through exactly the same code.
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
import datetime as dt  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H46-style-conserved-charge"
STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]
TC = [f for f in STYLE if f not in ("log_chars", "backticks", "urls")]
MIN_N = 3
GAP_BIN = float(os.environ.get("H46_GAP_BIN", 0.05))   # log10 seconds; NE41 gap strata
CLASSES = ["goal", "rooms", "nudger", "roster", "scaffold"]


# ----------------------------------------------------------------------------------------------- loading
def load_messages(eligible: bool = True) -> pl.DataFrame:
    m = pl.read_parquet(DATA / "messages.parquet")
    if eligible:
        m = m.filter(pl.col("main") & ~pl.col("self_repeat"))
    return m.sort("agent", "pt_date", "t")


def style_matrix(m: pl.DataFrame, kind: str = "tc") -> np.ndarray:
    cols = [f"tc_{f}" for f in TC] if kind == "tc" else [f"s_{f}" for f in STYLE]
    return m.select(cols).to_numpy().astype(np.float64)


_CACHE: dict = {}


def content_matrix(m: pl.DataFrame, kind: str = "resid") -> np.ndarray:
    """Per-message content vectors from the shared DQ5 arrays (unit vectors)."""
    if kind == "raw384":
        if "src" not in _CACHE:
            _CACHE["src"] = pl.read_parquet(SH / "embeddings/statements.parquet", columns=["src_row"])["src_row"].to_numpy()
        arr = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
        X = np.asarray(arr[_CACHE["src"][m["srow"].to_numpy()]], dtype=np.float64)
        return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)
    f = {"resid": "statements_style_resid32_bge_small.npy", "white": "statements_white32_bge_small.npy",
         "resid_period": "statements_style_resid_period32_bge_small.npy"}[kind]
    arr = np.load(SH / "embeddings" / f, mmap_mode="r")
    X = np.asarray(arr[m["srow"].to_numpy()], dtype=np.float64)
    return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)


# ----------------------------------------------------------------------------------------------- day tables
@dataclass
class DayTab:
    keys: pl.DataFrame              # agent, pt_date, unit2, regime, n, row
    M: dict                         # variant -> (n_days, dim) day means
    V: dict                         # variant -> (n_days,) sampling variance of the mean (tr S / n)


def day_table(m: pl.DataFrame, mats: dict, min_n: int = MIN_N) -> DayTab:
    """m sorted by agent, pt_date; mats: variant -> per-message matrix aligned with m."""
    g = (m.with_row_index("_i").group_by("agent", "pt_date", maintain_order=True)
         .agg(pl.col("_i").first().alias("start"), pl.len().alias("n"), pl.col("unit2").first(),
              pl.col("regime").first(), pl.col("goal_no").first(), pl.col("room").mode().first().alias("room")))
    starts = g["start"].to_numpy()
    n = g["n"].to_numpy().astype(np.float64)
    M, V = {}, {}
    for k, X in mats.items():
        S1 = np.add.reduceat(X, starts, axis=0)
        S2 = np.add.reduceat((X * X).sum(1), starts)
        mu = S1 / n[:, None]
        ss = S2 - n * (mu * mu).sum(1)                      # total within-day sum of squares
        var = np.where(n > 1, ss / np.maximum(n - 1, 1), np.nan)
        M[k], V[k] = mu, var / n
    keep = n >= min_n
    keys = g.filter(pl.Series(keep)).drop("start").with_row_index("row")
    return DayTab(keys, {k: v[keep] for k, v in M.items()}, {k: v[keep] for k, v in V.items()})


def add_demeaned(dt_: DayTab, variants: list[str]) -> None:
    """Day-field-removed copies (equal-weight mean over agents present that day)."""
    d = dt_.keys["pt_date"].to_numpy()
    _, inv = np.unique(d, return_inverse=True)
    for k in variants:
        M = dt_.M[k]
        S = np.zeros((inv.max() + 1, M.shape[1]))
        np.add.at(S, inv, M)
        cnt = np.bincount(inv).astype(float)
        dt_.M[k + "_dm"] = M - (S / cnt[:, None])[inv]
        dt_.V[k + "_dm"] = dt_.V[k]


def D_unb(dt_: DayTab, var: str, i: np.ndarray, j: np.ndarray) -> np.ndarray:
    M, V = dt_.M[var], dt_.V[var]
    return ((M[i] - M[j]) ** 2).sum(1) - V[i] - V[j]


# ----------------------------------------------------------------------------------------------- boundaries
def _date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def unit_first_days() -> dict:
    pu = pl.read_parquet(SH / "period_units.parquet")
    out = {r["unit_id"]: r["first_day"] for r in pu.iter_rows(named=True)}
    out["51g1"], out["51g2"] = out["51g"], "2026-08-21"
    return out


def placebo_pairs(dt_: DayTab) -> pl.DataFrame:
    """Adjacent eligible days of an agent within one unit2 (no step change between)."""
    k = dt_.keys.select("row", "agent", "pt_date", "unit2", "regime")
    nxt = k.with_columns(pl.col("row").shift(-1).over("agent").alias("row2"),
                         pl.col("pt_date").shift(-1).over("agent").alias("d2"),
                         pl.col("unit2").shift(-1).over("agent").alias("u2"))
    return nxt.filter(pl.col("row2").is_not_null() & (pl.col("unit2") == pl.col("u2"))).select(
        "agent", pl.col("row").alias("i"), pl.col("row2").alias("j"), pl.col("pt_date").alias("d1"),
        "d2", "regime")


def eval_boundaries(bounds: pl.DataFrame, dt_: DayTab, channels: dict, first_day: dict,
                    win: int = 21, min_p: int = 4, cross_regime_map: dict | None = None) -> pl.DataFrame:
    """channels: name -> variant. cross_regime_map: name -> variant used when the two sides differ in regime.
    Returns one row per (boundary, agent) with D_b, n_p, r, z per channel."""
    keys = dt_.keys
    pp = placebo_pairs(dt_)
    ag = keys["agent"].to_numpy()
    un = keys["unit2"].to_numpy()
    dd = keys["pt_date"].to_numpy()
    rg = keys["regime"].to_numpy()
    pp_ag, pp_i, pp_j = pp["agent"].to_numpy(), pp["i"].to_numpy(), pp["j"].to_numpy()
    pp_d1 = np.array([_date(x).toordinal() for x in pp["d1"].to_list()])
    pp_d2 = np.array([_date(x).toordinal() for x in pp["d2"].to_list()])
    pp_rg = pp["regime"].to_numpy()
    out = []
    for b in bounds.iter_rows(named=True):
        pre, post = set(b["pre"]), set(b["post"])
        tb = _date(min(first_day[u] for u in post)).toordinal()
        in_pre, in_post = np.isin(un, list(pre)), np.isin(un, list(post))
        regs = set(rg[in_pre | in_post])
        cross = len(regs) > 1
        for a in np.unique(ag[in_pre]):
            ipre = np.where(in_pre & (ag == a))[0]
            ipost = np.where(in_post & (ag == a))[0]
            if len(ipre) == 0 or len(ipost) == 0:
                continue
            i = ipre[np.argmax(dd[ipre])]
            j = ipost[np.argmin(dd[ipost])]
            sel = None
            for w in (win, 2 * win):
                s = (pp_ag == a) & (np.abs(pp_d1 - tb) <= w) & (np.abs(pp_d2 - tb) <= w)
                if not cross:
                    s &= np.isin(pp_rg, list(regs))
                if s.sum() >= min_p:
                    sel = s
                    break
            if sel is None:
                continue
            pi, pj = pp_i[sel], pp_j[sel]
            row = {"cls": b["cls"], "ne": b["ne"], "label": b["label"], "agent": int(a), "d_pre": dd[i],
                   "d_post": dd[j], "n_p": int(sel.sum()), "cross_regime": cross}
            for name, var in channels.items():
                v = (cross_regime_map or {}).get(name, var) if cross else var
                if v is None:
                    row[f"r_{name}"] = np.nan
                    continue
                Db = D_unb(dt_, v, np.array([i]), np.array([j]))[0]
                Dp = D_unb(dt_, v, pi, pj)
                row[f"D_{name}"] = float(Db)
                row[f"r_{name}"] = float(((Dp < Db).sum() + 0.5 * (Dp == Db).sum()) / len(Dp))
                sd = Dp.std(ddof=1)
                row[f"z_{name}"] = float((Db - Dp.mean()) / sd) if sd > 0 else np.nan
            out.append(row)
    return pl.DataFrame(out)


def class_test(rows: pl.DataFrame, ch: str, n_rand: int = 20000, n_boot: int = 2000, seed: int = 0) -> dict:
    """T = mean percentile; randomization p (uniform ranks), boundary-cluster bootstrap CI, boundary Wilcoxon."""
    r = rows.filter(pl.col(f"r_{ch}").is_not_nan())
    if r.height == 0:
        return {"n": 0}
    x = r[f"r_{ch}"].to_numpy()
    npl = r["n_p"].to_numpy()
    T = float(x.mean())
    rng = np.random.default_rng(seed)
    sims = np.empty(n_rand)
    for s0 in range(0, n_rand, 2000):
        k = min(2000, n_rand - s0)
        u = rng.integers(0, npl[None, :] + 1, size=(k, len(npl))) / npl[None, :]
        sims[s0:s0 + k] = u.mean(1)
    p_rand = float((1 + (sims >= T).sum()) / (1 + n_rand))
    p_rand_lo = float((1 + (sims <= T).sum()) / (1 + n_rand))
    labels = r["label"].to_numpy()
    ub = np.unique(labels)
    groups = [x[labels == u] for u in ub]
    bt = np.empty(n_boot)
    for k in range(n_boot):
        gs = rng.integers(0, len(groups), len(groups))
        vals = np.concatenate([groups[g][rng.integers(0, len(groups[g]), len(groups[g]))] for g in gs])
        bt[k] = vals.mean()
    per_b = np.array([g.mean() for g in groups])
    if len(per_b) >= 5:
        w = stats.wilcoxon(per_b - 0.5, alternative="greater")
        p_w = float(w.pvalue)
    else:
        p_w = np.nan
    return {"n": int(len(x)), "n_boundaries": int(len(ub)), "T": T, "lo": float(np.quantile(bt, 0.025)),
            "hi": float(np.quantile(bt, 0.975)), "p_rand": p_rand, "p_rand_less": p_rand_lo, "p_wilcoxon": p_w,
            "per_boundary": dict(zip(ub.tolist(), per_b.round(3).tolist())),
            "median_z": float(np.nanmedian(r[f"z_{ch}"].to_numpy())) if f"z_{ch}" in r.columns else np.nan}


def holm(ps: list[float]) -> list[float]:
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    adj = np.empty_like(ps)
    run = 0.0
    m = len(ps)
    for k, idx in enumerate(o):
        run = max(run, min(1.0, (m - k) * ps[idx]))
        adj[idx] = run
    return adj.tolist()


def moves(t: dict, padj: float) -> bool:
    if t.get("n", 0) == 0:
        return False
    ok = t["T"] > 0.5 and padj < 0.05
    if not np.isnan(t.get("p_wilcoxon", np.nan)):
        ok = ok and t["p_wilcoxon"] < 0.05
    return ok


def verdict(tc: dict, ts: dict, pc_adj: float, ps_adj: float, margin: float = 0.10) -> str:
    cm, sm = moves(tc, pc_adj), moves(ts, ps_adj)
    if not cm and not sm:
        return "uninformative"
    if cm and not sm and (ts["T"] - 0.5) <= (tc["T"] - 0.5) / 3 and ts["hi"] <= 0.5 + margin:
        return "conserved"
    if sm and (ts["T"] - 0.5) > (tc["T"] - 0.5) / 3:
        return "broken"
    return "partial"


# ----------------------------------------------------------------------------------------------- fingerprint
def nc_classify(Xtr, ytr, Xte):
    labs = np.unique(ytr)
    C = np.stack([Xtr[ytr == a].mean(0) for a in labs])
    res = Xtr - C[np.searchsorted(labs, ytr)]
    multi = np.isin(ytr, [a for a in labs if (ytr == a).sum() > 1])
    s = res[multi].std(0, ddof=1) if multi.sum() > len(labs[np.isin(labs, ytr[multi])]) + 1 else Xtr.std(0, ddof=1)
    s = np.where(s > 1e-9, s, 1.0)
    d = (((Xte[:, None, :] - C[None]) / s) ** 2).sum(2)
    return labs[np.argmin(d, 1)]


def balanced_acc(y, yhat) -> float:
    return float(np.mean([(yhat[y == a] == a).mean() for a in np.unique(y)]))


def fingerprint_boundary(dt_: DayTab, var: str, pre: set, post: set, k: int = 3, agents=None) -> dict:
    keys = dt_.keys
    ag, un, dd = keys["agent"].to_numpy(), keys["unit2"].to_numpy(), keys["pt_date"].to_numpy()
    M = dt_.M[var]
    tr_i, te_i = [], []
    common = []
    for a in np.unique(ag):
        if agents is not None and a not in agents:
            continue
        ipre = np.where(np.isin(un, list(pre)) & (ag == a))[0]
        ipost = np.where(np.isin(un, list(post)) & (ag == a))[0]
        if len(ipre) == 0 or len(ipost) == 0:
            continue
        common.append(a)
        tr_i += ipre[np.argsort(dd[ipre])][-k:].tolist()
        te_i += ipost[np.argsort(dd[ipost])][:k].tolist()
    if len(common) < 3:
        return {"n_agents": len(common)}
    tr_i, te_i = np.array(tr_i), np.array(te_i)
    yhat = nc_classify(M[tr_i], ag[tr_i], M[te_i])
    cross = balanced_acc(ag[te_i], yhat)
    # ceiling: leave-one-day-out within the pre side (agents with >= 2 pre days)
    ytr = ag[tr_i]
    hits = {}
    for q in range(len(tr_i)):
        a = ytr[q]
        if (ytr == a).sum() < 2:
            continue
        msk = np.ones(len(tr_i), bool)
        msk[q] = False
        yh = nc_classify(M[tr_i[msk]], ytr[msk], M[tr_i[q:q + 1]])[0]
        hits.setdefault(a, []).append(yh == a)
    ceil = float(np.mean([np.mean(v) for v in hits.values()])) if len(hits) >= 3 else np.nan
    return {"n_agents": len(common), "chance": 1.0 / len(common), "cross": cross, "ceiling": ceil}


# ----------------------------------------------------------------------------------------------- ridge information
def ridge_gcv(X, y, alphas=np.logspace(-2, 4, 25)):
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    Uy = U.T @ y
    n = len(y)
    best = None
    for a in alphas:
        f = s ** 2 / (s ** 2 + a)
        yhat = U @ (f * Uy)
        gcv = ((y - yhat) ** 2).mean() / (1 - f.sum() / n) ** 2
        if best is None or gcv < best[0]:
            best = (gcv, a)
    return best[1]


def ridge_fit_predict(Xtr, ytr, Xte, a):
    mx, my = Xtr.mean(0), ytr.mean()
    A = Xtr - mx
    w = np.linalg.solve(A.T @ A + a * np.eye(A.shape[1]), A.T @ (ytr - my))
    return my + (Xte - mx) @ w


def cv_r2(X, y, folds, a):
    pred = np.empty_like(y)
    for f in np.unique(folds):
        te = folds == f
        if te.all():
            return np.nan
        pred[te] = ridge_fit_predict(X[~te], y[~te], X[te], a)
    return float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def bits(r2: float) -> float:
    return float(-0.5 * np.log2(1 - max(r2, 0.0))) if np.isfinite(r2) else np.nan


def twoway_demean(X, a, d, iters=20):
    X = X.astype(np.float64).copy()
    _, ai = np.unique(a, return_inverse=True)
    _, di = np.unique(d, return_inverse=True)
    for _ in range(iters):
        for idx in (ai, di):
            S = np.zeros((idx.max() + 1,) + X.shape[1:])
            np.add.at(S, idx, X)
            X -= (S / np.bincount(idx).reshape((-1,) + (1,) * (X.ndim - 1)))[idx]
    return X


def info_within(X, y, agents, days, n_perm=200, seed=0) -> dict:
    """Within-agent, day-blocked predictive information with the within-agent scramble null."""
    Xd = twoway_demean(X, agents, days)
    yd = twoway_demean(y[:, None], agents, days)[:, 0]
    if len(yd) < 20 or yd.std() < 1e-9:
        return {"n": int(len(yd))}
    a = ridge_gcv(Xd, yd)
    r2 = cv_r2(Xd, yd, days, a)
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_perm):
        perm = np.arange(len(yd))
        for g in np.unique(agents):
            ix = np.where(agents == g)[0]
            perm[ix] = rng.permutation(ix)
        Xp = twoway_demean(X[perm], agents, days)
        null.append(cv_r2(Xp, yd, days, a))
    null = np.array(null)
    med = float(np.median(null))
    return {"n": int(len(yd)), "alpha": float(a), "r2_cv": r2, "bits": bits(r2), "null_r2_median": med,
            "r2_corrected": r2 - med, "bits_corrected": bits(r2 - med),
            "p": float((1 + (null >= r2).sum()) / (1 + n_perm)), "null_r2_q95": float(np.quantile(null, 0.95))}


# ----------------------------------------------------------------------------------------------- NE41 pairs
def pair_percentiles(lab: np.ndarray, dist: np.ndarray, strata: np.ndarray, strata2: np.ndarray, min_n: int = 5):
    """For each crossing pair (lab != 'within'), percentile of its distance among same-stratum within pairs."""
    out = np.full(len(lab), np.nan)
    npl = np.zeros(len(lab), int)
    w = lab == "within"
    for S in (strata, strata2):
        need = (lab != "within") & np.isnan(out)
        if not need.any():
            break
        order = np.argsort(S[w], kind="stable")
        sw, dw = S[w][order], dist[w][order]
        uniq, st = np.unique(sw, return_index=True)
        en = np.append(st[1:], len(sw))
        pos = {u: (s, e) for u, s, e in zip(uniq, st, en)}
        for idx in np.where(need)[0]:
            se = pos.get(S[idx])
            if se is None or se[1] - se[0] < min_n:
                continue
            ref = np.sort(dw[se[0]:se[1]])
            lo = np.searchsorted(ref, dist[idx], "left")
            hi = np.searchsorted(ref, dist[idx], "right")
            out[idx] = (lo + 0.5 * (hi - lo)) / len(ref)
            npl[idx] = len(ref)
    return out, npl


def mean_pct_test(x, npl, clusters, n_rand=20000, n_boot=2000, seed=0) -> dict:
    ok = ~np.isnan(x)
    x, npl, clusters = x[ok], npl[ok], clusters[ok]
    if len(x) == 0:
        return {"n": 0}
    T = float(x.mean())
    rng = np.random.default_rng(seed)
    sims = np.empty(n_rand)
    for s0 in range(0, n_rand, 500):
        k = min(500, n_rand - s0)
        sims[s0:s0 + k] = (rng.integers(0, npl[None, :] + 1, size=(k, len(npl))) / npl[None, :]).mean(1)
    cl = np.unique(clusters)
    groups = [x[clusters == c] for c in cl]
    bt = np.empty(n_boot)
    for k in range(n_boot):
        gs = rng.integers(0, len(groups), len(groups))
        bt[k] = np.concatenate([groups[g] for g in gs]).mean()
    return {"n": int(len(x)), "n_clusters": int(len(cl)), "T": T, "lo": float(np.quantile(bt, 0.025)),
            "hi": float(np.quantile(bt, 0.975)), "p_rand": float((1 + (sims >= T).sum()) / (1 + n_rand)),
            "p_rand_less": float((1 + (sims <= T).sum()) / (1 + n_rand))}
