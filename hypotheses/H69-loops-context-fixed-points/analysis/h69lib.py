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


# ============================================================================ round 2 (2026-10-05)
R1_COLS = ["log1p:o_ctx", "log1p:U_k", "log1p:k_ctx"]


def attach_r2(st: pl.DataFrame, tok: pl.DataFrame) -> pl.DataFrame:
    """Join round-2 token covariates (r2_tokens.parquet) to a statement frame. U_k = own tool tokens / 1000.
    dose_prev = seg_dose of the previous statement's segment (the own tokens an erasure between t-1 and t removed);
    cap_prev = cap hits on calls in (call of t-1, call of t] (NE22)."""
    st = st.join(tok, on="sid", how="left").with_columns((pl.col("U") / 1000).alias("U_k"))
    st = st.sort("agent", "t").with_columns(
        pl.col("seg_dose").shift(1).over("agent", "pt_date").alias("dose_prev"),
        (pl.col("cap_cum") - pl.col("cap_cum").shift(1).over("agent", "pt_date")).alias("cap_prev"))
    return st


def logit_terms(d: pl.DataFrame, y: np.ndarray, cols: list[str]) -> dict:
    """Agent-effect logit with agent-day cluster SEs; returns {name: (b, se)}, n."""
    ag = np.unique(d["agent"].to_numpy(), return_inverse=True)[1]
    X = _X(d, cols)
    keep = X.std(axis=0) > 0
    r = fit_logit(y, X[:, keep], ag, clusters=d["aday"].to_list())
    out, j = {}, 0
    for c, k in zip(cols, keep):
        name = c.split(":")[-1]
        if k:
            bad = abs(r["b"][j]) > 10 or r["se_cl"][j] > 10
            out[name] = (float("nan"), float("nan")) if bad else (float(r["b"][j]), float(r["se_cl"][j]))
            j += 1
        else:
            out[name] = (float("nan"), float("nan"))
    return dict(terms=out, n=int(len(y)), n_y=int(y.sum()))


def r1_onset(st: pl.DataFrame, resp="r_either", fill="ctx_pos", with_U=True):
    """R1 onset: log(1+O), log(1+U/1000), log(1+K) + round-1 controls; fill = ctx_pos (round 1) or P (log P)."""
    d = st.filter((pl.col("r_prev") == 0) & pl.col("U_k").is_not_null())
    if d.height < 50 or d[resp].sum() < 10:
        return None
    ctrl = [c for c in ONSET_CTRL if c != "log1p:ctx_pos"] + (["log1p:ctx_pos"] if fill == "ctx_pos" else ["log:P"])
    cols = (R1_COLS if with_U else ["log1p:o_ctx", "log1p:k_ctx"]) + ctrl
    return logit_terms(d, d[resp].to_numpy().astype(float), cols)


def r2_exit_dose(st: pl.DataFrame, resp="r_either"):
    """R2a exit: round-1 primary exit model plus erasure x centered dose (dose of the erased segment)."""
    d = st.filter(pl.col("r_prev") == 1).with_columns(
        (pl.col("reset_between") & ~pl.col("forced_between")).alias("vol_between"))
    er = d["reset_between"].fill_null(False).to_numpy()
    dose = d["dose_prev"].to_numpy().astype(float)
    ok = ~er | np.isfinite(dose)
    d = d.filter(pl.Series(ok))
    er = er[ok]
    dose = dose[ok]
    if d.height < 30 or er.sum() < 10:
        return None
    mu = float(np.nanmean(dose[er]))
    d = d.with_columns(pl.Series("dose_c", np.where(er, dose - mu, 0.0)))
    y = 1 - d[resp].to_numpy().astype(float)
    cols = ["forced_between", "vol_between", "dose_c", "log1p:nov_read", "log1p:nov_infl", "log1p:nov_read_next"] \
        + EXIT_CTRL
    r = logit_terms(d, y, cols)
    r.update(n_erasure=int(er.sum()), dose_mean=mu, dose_sd=float(np.nanstd(dose[er])))
    return r


def r2_onset_dose(st: pl.DataFrame, resp="r_either"):
    d = st.filter(pl.col("r_prev") == 0)
    er = d["reset_between"].fill_null(False).to_numpy()
    dose = d["dose_prev"].to_numpy().astype(float)
    ok = ~er | np.isfinite(dose)
    d = d.filter(pl.Series(ok))
    er, dose = er[ok], dose[ok]
    if d.height < 50 or er.sum() < 10 or d[resp].sum() < 10:
        return None
    mu = float(np.nanmean(dose[er]))
    d = d.with_columns(pl.Series("dose_c", np.where(er, dose - mu, 0.0)),
                       pl.Series("erased", er.astype(float)))
    cols = ["erased", "dose_c", "log1p:n_prev_day", "log:lag_prev_s", "log:calls_prev", "log1p:n_read"]
    r = logit_terms(d, d[resp].to_numpy().astype(float), cols)
    r.update(n_erasure=int(er.sum()))
    return r


def r2_cap_exit(st: pl.DataFrame, resp="r_either"):
    """R2b: exit among loop statements with a 200-event cap hit since the previous statement (counts + OR)."""
    d = st.filter(pl.col("r_prev") == 1)
    cap = (d["cap_prev"].fill_null(0) > 0).to_numpy()
    out = dict(n_loop=int(d.height), n_cap=int(cap.sum()))
    if cap.sum() >= 20:
        d = d.with_columns(pl.Series("cap", cap.astype(float)))
        y = 1 - d[resp].to_numpy().astype(float)
        out.update(logit_terms(d, y, ["cap", "forced_between", "log:calls_prev", "log:lag_prev_s",
                                      "log1p:n_prev_day"]))
    return out


def mh_boot(y, x, strata, clusters, B=200, seed=0):
    """MH log OR with a cluster bootstrap (clusters: agent-days of the outcome statement)."""
    lor, n_inf = mh_or(y, x, strata)
    rng = np.random.default_rng(seed)
    cl = np.unique(clusters, return_inverse=True)[1]
    idx_by = [np.where(cl == k)[0] for k in range(cl.max() + 1)] if len(cl) else []
    bs = []
    for _ in range(B):
        pick = rng.integers(0, len(idx_by), len(idx_by))
        ii = np.concatenate([idx_by[k] for k in pick])
        v, _ = mh_or(y[ii], x[ii], strata[ii])
        if np.isfinite(v):
            bs.append(v)
    ok = len(bs) > 20 and np.isfinite(lor)  # no interval when the point estimate is not estimable
    lo, hi = np.percentile(bs, [2.5, 97.5]) if ok else (np.nan, np.nan)
    return dict(log_or=lor, lo=float(lo), hi=float(hi), se=float(np.std(bs)) if ok else float("nan"),
                n=int(len(y)), n_y=int(y.sum()), n_x=int(x.sum()), n_xy=int((x & y).sum()), n_strata_inf=n_inf)


def base_strata(p: pl.DataFrame) -> np.ndarray:
    return (p["agent"].to_numpy().astype(np.int64) * 10 ** 6 + lag_bin(p["lag_s"].to_numpy()) * 100
            + call_bin(p["calls_between"].to_numpy()))


def cu_bin(c_u):
    c = np.nan_to_num(np.asarray(c_u, float), nan=0.0)
    return np.where(c <= 0, 0, np.where(c < 0.5, 1, 2))


def prior_bin(n):
    return np.minimum(np.asarray(n), 2)


def r3_stats(e: pl.DataFrame, ycol="y", thr=0.5, B=200, seed=0):
    """R3 on erased pairs with containment (c_t, c_u): P1 in_mem OR; P2 new_mem vs not-in-memory and the
    salience-stratified in_mem OR; within-source OR (strata = source u x lag bin; amendment R2-A3)."""
    e = e.filter(pl.col("c_t").is_not_nan())
    if e.height < 200:
        return None
    y = e[ycol].to_numpy().astype(bool)
    ct = e["c_t"].to_numpy()
    cu = np.nan_to_num(e["c_u"].to_numpy(), nan=0.0)
    inm = ct >= thr
    newm = inm & (cu < thr)
    S = base_strata(e)
    cl = e["aday"].to_numpy()
    out = dict(n_pairs=int(e.height), n_copies=int(y.sum()), share_in_mem=float(inm.mean()),
               share_in_mem_copies=float(inm[y].mean()) if y.any() else float("nan"))
    out["P1"] = mh_boot(y, inm, S, cl, B, seed)
    keep = ~(inm & ~newm)  # drop old_mem
    out["P2_new"] = mh_boot(y[keep], newm[keep], S[keep], cl[keep], B, seed + 1)
    S2 = S * 10 + cu_bin(cu) * 3 + prior_bin(e["prior_copies"].to_numpy())
    out["P2_strat"] = mh_boot(y, inm, S2, cl, B, seed + 2)
    Su = e["sid_u"].to_numpy().astype(np.int64) * 100 + lag_bin(e["lag_s"].to_numpy())
    out["within_u"] = mh_boot(y, inm, Su, cl, B, seed + 3)
    out["within_u_discordant"] = int(pl.DataFrame({"u": e["sid_u"], "m": inm}).group_by("u").agg(
        pl.col("m").n_unique()).filter(pl.col("m") > 1).height)
    return out


def r3_lowerbound(p: pl.DataFrame, ycol="y", thr=0.5, B=200, seed=0):
    """R3-P3: in-context enrichment vs erased-not-in-memory sources minus vs all erased sources (log ORs), joint
    agent-day bootstrap. p: all pairs (in_seg true or erased with c_t)."""
    p = p.filter(pl.col("in_seg") | pl.col("c_t").is_not_nan())
    y = p[ycol].to_numpy().astype(bool)
    x = p["in_seg"].to_numpy().astype(bool)
    notmem = x | (np.nan_to_num(p["c_t"].to_numpy(), nan=0.0) < thr)
    S = base_strata(p)
    a, _ = mh_or(y, x, S)
    b, _ = mh_or(y[notmem], x[notmem], S[notmem])
    rng = np.random.default_rng(seed)
    cl = np.unique(p["aday"].to_numpy(), return_inverse=True)[1]
    idx_by = [np.where(cl == k)[0] for k in range(cl.max() + 1)]
    bs = []
    for _ in range(B):
        ii = np.concatenate([idx_by[k] for k in rng.integers(0, len(idx_by), len(idx_by))])
        va, _ = mh_or(y[ii], x[ii], S[ii])
        jj = ii[notmem[ii]]
        vb, _ = mh_or(y[jj], x[jj], S[jj])
        if np.isfinite(va) and np.isfinite(vb):
            bs.append(vb - va)
    ok = len(bs) > 20
    lo, hi = np.percentile(bs, [2.5, 97.5]) if ok else (np.nan, np.nan)
    return dict(lor_all=a, lor_notmem=b, diff=b - a, lo=float(lo), hi=float(hi),
                se=float(np.std(bs)) if ok else float("nan"))


def r3_frame(pr: pl.DataFrame, mem: pl.DataFrame, s: pl.DataFrame) -> pl.DataFrame:
    """All pairs with containment for erased ones (c_t NaN for in-context pairs) and t's agent / agent-day."""
    p = pr.join(mem.select("sid", "sid_u", "prior_copies", "c_t", "c_u", "lines_added_between"),
                on=["sid", "sid_u"], how="left")
    p = p.with_columns(pl.col("c_t").fill_null(float("nan")), pl.col("c_u").fill_null(float("nan")),
                       pl.col("prior_copies").fill_null(0))
    return p.join(s.select("sid", "agent", "aday"), on="sid", how="inner")


def posthoc_exit_mem(st: pl.DataFrame, mem: pl.DataFrame, resp="r_either", thr=0.5):
    """POST HOC (2026-10-05, after the R3 result): exit model with erasure x (previous statement's content in the
    memory at t). The previous statement t-1 of a loop is the erased source u of the pair (t, t-1) when an erasure
    lies between them; c_t is its containment in M_t."""
    s2 = st.sort("agent", "t").with_columns(pl.col("sid").shift(1).over("agent", "pt_date").alias("sid_prev"))
    d = s2.filter(pl.col("r_prev") == 1).join(
        mem.select("sid", pl.col("sid_u").alias("sid_prev"), "c_t"), on=["sid", "sid_prev"], how="left")
    er = d["reset_between"].fill_null(False).to_numpy()
    c = d["c_t"].fill_null(float("nan")).to_numpy()
    known = ~er | np.isfinite(c)
    d = d.filter(pl.Series(known)).with_columns(
        (pl.col("reset_between") & ~pl.col("forced_between")).alias("vol_between"))
    er = er[known]
    inm = np.where(er, np.nan_to_num(c[known], nan=0.0) >= thr, False)
    if d.height < 30 or er.sum() < 10 or inm.sum() < 3:
        return dict(n=int(d.height), n_erasure=int(er.sum()), n_erasure_inmem=int(inm.sum()))
    d = d.with_columns(pl.Series("erased_inmem", inm.astype(float)), pl.Series("erased", er.astype(float)))
    y = 1 - d[resp].to_numpy().astype(float)
    r = logit_terms(d, y, ["erased", "erased_inmem"] + EXIT_CTRL)
    r.update(n_erasure=int(er.sum()), n_erasure_inmem=int(inm.sum()),
             exit_rate_erased_inmem=float(y[inm].mean()), exit_rate_erased_notmem=float(y[er & ~inm].mean()),
             exit_rate_no_erasure=float(y[~er].mean()))
    return r
