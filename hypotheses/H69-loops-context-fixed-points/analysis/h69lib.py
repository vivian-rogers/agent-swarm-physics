"""H69 estimators: onset and exit models for restatement loops, in-context enrichment, pooling.

All functions take a period's frames (statements, items, pairs) as polars DataFrames and the response column names,
so the same code runs on real flags and on synthetic flags. H69's own code (no imports from other hypotheses).
"""
from __future__ import annotations

import math

import numpy as np
import polars as pl
from scipy import stats

SIGMA_FE = 2.0
CALL_BINS = [0, 1, 2, 4, 8, 16, 32, 64, 10 ** 9]


# ============================================================================ penalized logistic with group effects
def fit_logit(y, X, groups, sigma=SIGMA_FE, clusters=None, max_iter=50):
    """logit P(y) = a_g + X b; a_g ridge toward a free mean (sigma). Returns b, model SE, cluster-robust SE, ll."""
    y = np.asarray(y, float)
    X = np.asarray(X, float).reshape(len(y), -1)
    gr = np.asarray(groups, np.int64)
    G = int(gr.max()) + 1
    p = X.shape[1]
    lam = 1 / sigma ** 2
    m = min(max(y.mean(), 1e-3), 1 - 1e-3)
    a = np.full(G, math.log(m / (1 - m)))
    a0 = a[0]
    b = np.zeros(p)

    def pll(a, a0, b):
        eta = a[gr] + X @ b
        return np.sum(y * eta - np.logaddexp(0, eta)) - 0.5 * lam * np.sum((a - a0) ** 2)

    def hess(a, a0, b):
        eta = a[gr] + X @ b
        mu = 1 / (1 + np.exp(-eta))
        w = mu * (1 - mu)
        K = G + 1 + p
        H = np.zeros((K, K))
        H[np.arange(G), np.arange(G)] = np.bincount(gr, weights=w, minlength=G) + lam
        H[:G, G] = H[G, :G] = -lam
        H[G, G] = lam * G
        WX = X * w[:, None]
        cross = np.stack([np.bincount(gr, weights=WX[:, j], minlength=G) for j in range(p)], axis=1)
        H[:G, G + 1:] = cross
        H[G + 1:, :G] = cross.T
        H[G + 1:, G + 1:] = X.T @ WX
        r = y - mu
        grad = np.concatenate([np.bincount(gr, weights=r, minlength=G) - lam * (a - a0), [lam * np.sum(a - a0)], X.T @ r])
        return H, grad, r
    cur = pll(a, a0, b)
    for _ in range(max_iter):
        H, grad, _ = hess(a, a0, b)
        step = np.linalg.lstsq(H, grad, rcond=None)[0]
        t = 1.0
        while t > 1e-4:
            na, na0, nb = a + t * step[:G], a0 + t * step[G], b + t * step[G + 1:]
            new = pll(na, na0, nb)
            if new >= cur - 1e-10:
                break
            t *= 0.5
        a, a0, b = na, na0, nb
        done = abs(new - cur) < 1e-9
        cur = new
        if done:
            break
    H, _, r = hess(a, a0, b)
    cov = np.linalg.pinv(H)
    se = np.sqrt(np.maximum(np.diag(cov)[G + 1:], 0))
    eta = a[gr] + X @ b
    ll = float(np.sum(y * eta - np.logaddexp(0, eta)))
    se_cl = se.copy()
    if clusters is not None:
        cl = np.unique(np.asarray(clusters), return_inverse=True)[1]
        # scores per observation for all parameters
        S = np.zeros((len(y), G + 1 + p))
        S[np.arange(len(y)), gr] = r
        S[:, G + 1:] = X * r[:, None]
        Sc = np.zeros((cl.max() + 1, S.shape[1]))
        np.add.at(Sc, cl, S)
        nc = Sc.shape[0]
        meat = Sc.T @ Sc * (nc / max(nc - 1, 1))
        V = cov @ meat @ cov
        se_cl = np.sqrt(np.maximum(np.diag(V)[G + 1:], 0))
    return dict(b=b, se=se, se_cl=se_cl, ll=ll, n=int(len(y)), k=G + 1 + p)


# ============================================================================ preparation
O_SCOPE = "seg"  # recheck 2026-10-04: O counts own statements over the whole context segment ("day" = round 1)


def prepare(st: pl.DataFrame, items: pl.DataFrame | None, resp: str = "r_either", nov: str = "nov_bge",
            nov_thr: float | None = None, o_scope: str | None = None) -> tuple[pl.DataFrame, float]:
    """Statement frame with previous-response state, self-share and input counts.
    O (own statements in context) is `o_ctx`: o_seg (whole segment, crosses midnight like k_ctx; primary since the
    segment-cut recheck) or o_day (round 1: same PT day only); frames without o_seg fall back to o_day."""
    sc = o_scope or O_SCOPE
    if sc == "seg" and "o_seg" in st.columns:
        st = st.with_columns(pl.col("o_seg").alias("o_ctx"), pl.col("own_chars_seg").alias("own_chars_ctx"))
    else:
        st = st.with_columns(pl.col("o_day").alias("o_ctx"), pl.col("own_chars_day").alias("own_chars_ctx"))
    if items is not None and items.height:
        read = items.filter(pl.col("inflight") == 0)
        if nov_thr is None:
            nov_thr = float(read[nov].median()) if read.height else 0.5
        agg = (items.with_columns((pl.col(nov) >= nov_thr).alias("novel"))
               .group_by("sid").agg(
                   (pl.col("novel") & (pl.col("inflight") == 0)).sum().alias("nov_read"),
                   (pl.col("novel") & (pl.col("inflight") == 1)).sum().alias("nov_infl"),
                   ((pl.col("inflight") == 0) & (pl.col("kind") == "nudge")).sum().alias("read_nudge"),
                   ((pl.col("inflight") == 0) & (pl.col("kind") == "human")).sum().alias("read_human"),
                   ((pl.col("inflight") == 1) & (pl.col("kind") == "nudge")).sum().alias("infl_nudge"),
                   ((pl.col("inflight") == 1) & (pl.col("kind") == "human")).sum().alias("infl_human")))
        st = st.join(agg, on="sid", how="left")
    for c in ("nov_read", "nov_infl", "read_nudge", "read_human", "infl_nudge", "infl_human"):
        if c not in st.columns:
            st = st.with_columns(pl.lit(0).alias(c))
        st = st.with_columns(pl.col(c).fill_null(0))
    st = st.sort("agent", "t").with_columns(
        pl.col(resp).cast(pl.Int8).shift(1).over("agent", "pt_date").alias("r_prev"),
        pl.col("nov_read").shift(-1).over("agent", "pt_date").fill_null(0).alias("nov_read_next"),
        (pl.col("o_ctx") / (pl.col("o_ctx") + pl.col("k_ctx")).clip(lower_bound=1)).alias("s_self"),
        (pl.col("own_chars_ctx") / (pl.col("own_chars_ctx") + pl.col("chars_ctx")).clip(lower_bound=1)).alias(
            "s_chars"),
        (pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("aday"),
    )
    return st, nov_thr


def _X(df, cols):
    out = []
    for c in cols:
        if c.startswith("log1p:"):
            out.append(np.log1p(df[c[6:]].fill_null(0).to_numpy().astype(float)))
        elif c.startswith("log:"):
            out.append(np.log(np.maximum(df[c[4:]].fill_null(1).to_numpy().astype(float), 1.0)))
        else:
            out.append(df[c].fill_null(0).to_numpy().astype(float))
    return np.column_stack(out)


ONSET_CTRL = ["log1p:n_prev_day", "log:lag_prev_s", "log1p:ctx_pos", "log1p:n_read"]
EXIT_CTRL = ["log:calls_prev", "log:lag_prev_s", "log1p:n_prev_day"]


def onset(st: pl.DataFrame, resp: str = "r_either", share: str = "s_self"):
    """Entry model among r_prev == 0. Returns b_s (linear), split b_O, b_K, hinge profile."""
    d = st.filter(pl.col("r_prev") == 0)
    if d.height < 50 or d[resp].sum() < 10:
        return None
    y = d[resp].to_numpy().astype(float)
    ag = np.unique(d["agent"].to_numpy(), return_inverse=True)[1]
    cl = d["aday"].to_list()
    C = _X(d, ONSET_CTRL)
    s = d[share].to_numpy().astype(float)
    lin = fit_logit(y, np.column_stack([s, C]), ag, clusters=cl)
    split = fit_logit(y, np.column_stack([np.log1p(d["o_ctx"].to_numpy()), np.log1p(d["k_ctx"].to_numpy()), C]), ag,
                      clusters=cl)
    best = None
    for ss in np.arange(0.1, 0.91, 0.05):
        h = fit_logit(y, np.column_stack([np.maximum(s - ss, 0), C]), ag)
        if best is None or h["ll"] > best[1]["ll"]:
            best = (float(ss), h)
    aic_lin = -2 * lin["ll"] + 2 * lin["k"]
    aic_hinge = -2 * best[1]["ll"] + 2 * (best[1]["k"] + 1)
    return dict(n=int(len(y)), n_events=int(y.sum()), b_s=float(lin["b"][0]), se_s=float(lin["se_cl"][0]),
                b_O=float(split["b"][0]), se_O=float(split["se_cl"][0]), b_K=float(split["b"][1]),
                se_K=float(split["se_cl"][1]), s_star=best[0], b_hinge=float(best[1]["b"][0]),
                dAIC_hinge=float(aic_lin - aic_hinge), ctrl=dict(zip(ONSET_CTRL, map(float, lin["b"][1:]))))


def exit_model(st: pl.DataFrame, resp: str = "r_either", extra=("nov_read", "nov_infl", "nov_read_next"),
               include_s: bool = False):
    """Exit model among r_prev == 1: logit P(r_t = 0). s_self is a mediator of the erasure effect (an erasure sets
    s -> 0), so the primary model leaves it out (total effect); include_s=True gives the direct-effect variant."""
    d = st.filter(pl.col("r_prev") == 1).with_columns(
        (pl.col("reset_between") & ~pl.col("forced_between")).alias("vol_between"))
    if d.height < 30:
        return None
    y = 1 - d[resp].to_numpy().astype(float)
    if y.sum() < 5 or y.sum() > len(y) - 5:
        return None
    ag = np.unique(d["agent"].to_numpy(), return_inverse=True)[1]
    cols = ["forced_between", "vol_between"] + [f"log1p:{c}" for c in extra] + (["s_self"] if include_s else []) \
        + EXIT_CTRL
    X = _X(d, cols)
    keep = X.std(axis=0) > 0
    keep[:2] = keep[:2]  # report NaN when a reset type never occurs
    r = fit_logit(y, X[:, keep], ag, clusters=d["aday"].to_list())
    out = dict(n=int(len(y)), n_exit=int(y.sum()), n_forced=int(d["forced_between"].sum()),
               n_vol=int(d["vol_between"].sum()))
    j = 0
    for c, k in zip(cols, keep):
        name = c.replace("log1p:", "").replace("log:", "")
        if k:
            sep = abs(r["b"][j]) > 10 or r["se_cl"][j] > 10  # quasi-separation: not estimable
            out[f"b_{name}"] = float("nan") if sep else float(r["b"][j])
            out[f"se_{name}"] = float("nan") if sep else float(r["se_cl"][j])
            j += 1
        else:
            out[f"b_{name}"] = float("nan")
            out[f"se_{name}"] = float("nan")
    return out


def lag_bin(lag_s):
    return np.floor(np.log10(np.maximum(lag_s, 1.0)) / 0.1).astype(np.int64)


def call_bin(cb):
    return np.searchsorted(CALL_BINS, np.asarray(cb), side="right")


def mh_or(y, x, strata):
    """Mantel-Haenszel odds ratio of y for exposure x across strata (log OR)."""
    st = np.unique(strata, return_inverse=True)[1]
    S = st.max() + 1
    n = np.bincount(st, minlength=S).astype(float)
    a = np.bincount(st, weights=(x & y), minlength=S)
    b = np.bincount(st, weights=(x & ~y), minlength=S)
    c = np.bincount(st, weights=(~x & y), minlength=S)
    d = np.bincount(st, weights=(~x & ~y), minlength=S)
    ok = n > 0
    num = np.sum(a[ok] * d[ok] / n[ok])
    den = np.sum(b[ok] * c[ok] / n[ok])
    if num <= 0 or den <= 0:
        return float("nan"), int(np.sum((a + c > 0) & (a + b > 0) & (c + d > 0)))
    inf = (a + b > 0) & (c + d > 0) & (a + c > 0)
    return float(np.log(num / den)), int(inf.sum())


def enrichment(pairs: pl.DataFrame, st: pl.DataFrame, ycol="y", B=200, seed=0, exposure="in_seg",
               restrict=None):
    """MH log OR of a near-copy for u in context (same segment) vs erased, strata agent x lag bin x calls bin.
    Cluster bootstrap over agent-days of the outcome statement."""
    p = pairs
    if restrict is not None:
        p = p.filter(restrict)
    if p.height < 100:
        return None
    meta = st.select("sid", "agent", "aday")
    p = p.join(meta, on="sid", how="inner")
    y = p[ycol].to_numpy().astype(bool)
    x = p[exposure].to_numpy().astype(bool)
    strata = (p["agent"].to_numpy().astype(np.int64) * 10 ** 6 + lag_bin(p["lag_s"].to_numpy()) * 100
              + call_bin(p["calls_between"].to_numpy()))
    lor, n_inf = mh_or(y, x, strata)
    rng = np.random.default_rng(seed)
    ad = np.unique(p["aday"].to_numpy(), return_inverse=True)[1]
    idx_by = [np.where(ad == k)[0] for k in range(ad.max() + 1)]
    bs = []
    for _ in range(B):
        pick = rng.integers(0, len(idx_by), len(idx_by))
        ii = np.concatenate([idx_by[k] for k in pick])
        # make strata distinct per bootstrap copy of an agent-day is unnecessary: strata are agent-level
        v, _ = mh_or(y[ii], x[ii], strata[ii])
        if np.isfinite(v):
            bs.append(v)
    lo, hi = (np.percentile(bs, [2.5, 97.5]) if len(bs) > 20 else (np.nan, np.nan))
    se = float(np.std(bs)) if len(bs) > 20 else float("nan")
    return dict(log_or=lor, lo=float(lo), hi=float(hi), se=se, n_pairs=int(p.height), n_strata_inf=n_inf,
                n_y=int(y.sum()), n_x=int(x.sum()))


def episodes(st: pl.DataFrame, resp="r_either"):
    """Restatement runs (>= 2 consecutive) per agent-day; persistence."""
    out = st.sort("agent", "t")
    r = out[resp].to_numpy().astype(int)
    ad = out["aday"].to_list()
    runs = []
    cur = 0
    for i in range(len(r)):
        if i > 0 and ad[i] != ad[i - 1]:
            if cur >= 2:
                runs.append(cur)
            cur = 0
        if r[i]:
            cur += 1
        else:
            if cur >= 2:
                runs.append(cur)
            cur = 0
    if cur >= 2:
        runs.append(cur)
    rp = out["r_prev"].to_numpy()
    m1 = rp == 1
    m0 = rp == 0
    return dict(rate=float(r.mean()), n_stmt=int(len(r)), n_episodes=len(runs),
                mean_len=float(np.mean(runs)) if runs else float("nan"),
                p_stay=float(r[m1].mean()) if m1.any() else float("nan"),
                p_enter=float(r[m0].mean()) if m0.any() else float("nan"))


def dl_pool(est, se):
    """DerSimonian-Laird random-effects mean, SE, tau^2, I^2."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return dict(mean=float("nan"), se=float("nan"), k=0)
    w = 1 / se ** 2
    m = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - m) ** 2)
    k = len(est)
    tau2 = max(0.0, (Q - (k - 1)) / (np.sum(w) - np.sum(w ** 2) / np.sum(w))) if k > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mm = np.sum(ws * est) / np.sum(ws)
    sem = math.sqrt(1 / np.sum(ws))
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
    return dict(mean=float(mm), se=float(sem), lo=float(mm - 1.96 * sem), hi=float(mm + 1.96 * sem), tau2=float(tau2),
                I2=float(I2), k=int(k), p=float(2 * stats.norm.sf(abs(mm / sem))))
