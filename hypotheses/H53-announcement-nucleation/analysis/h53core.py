"""H53 estimators, shared by the synthetic validation, the real-data run and the confirmatory script.

Inputs are the scheme tables (seeds, recipients) or synthetic copies with simulated adoption times in a_label.
Every function is pure (no file I/O) except loaders.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.optimize import minimize  # noqa: E402
from scipy.special import gammaln, digamma  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h53lib import FU_S, H_S, LOOKBACK_S, OUT, SHIFTS_MIN  # noqa: E402,F401

MIN_SUS = 3          # eligible seed: >= 3 susceptible in-room roster recipients
MIN_SEEDS = 10       # replication-eligible period: >= 10 eligible seeds
RIVALS = ["lN", "lU", "lstat", "human", "share", "tod", "first30"]


def load(out: Path = OUT):
    return pl.read_parquet(out / "seeds.parquet"), pl.read_parquet(out / "recipients.parquet")


# ============================================================================ preparation
def prep(seeds: pl.DataFrame, rec: pl.DataFrame, variant: str = "label", c_mult: float | None = 1.0,
         c_fixed: float | None = None, unc: str = "u0", H: float = H_S, age_col: str = "age_s") -> tuple[pl.DataFrame, pl.DataFrame]:
    """Flags per recipient and counts per seed.
    variant: adoption variant (label/action/mention/commit) used for the outcome; susceptibility always uses `label`
    (or `mention` for the mention variant). c: receptive window = c_mult * cyc_s, or c_fixed seconds.
    unc: u0 (no other-project mention in 30 min), u2 (<= 2), none."""
    a_out = f"a_{variant}"
    a_sus = "a_mention" if variant == "mention" else "a_label"
    r = rec.join(seeds.select("sid", "a_seed", "a_gend", "censored"), on="sid", how="left")
    win = (pl.col("cyc_s") * c_mult) if c_fixed is None else pl.lit(float(c_fixed))
    uexpr = {"u0": pl.col("n_other30") == 0, "u2": pl.col("n_other30") <= 2, "none": pl.lit(True)}[unc]
    r = r.with_columns(
        (pl.col(a_sus).is_null() | (pl.col(a_sus) >= pl.col("a_seed"))).alias("sus"),
        uexpr.alias("unc"),
        (pl.col(age_col).is_not_null() & (pl.col(age_col) <= win)).alias("timely"),
    )
    r = r.with_columns((pl.col("sus") & pl.col("in_room")).alias("sus_in"))
    r = r.with_columns((pl.col("sus_in") & pl.col("unc") & pl.col("timely")).alias("recept"),
                       (pl.col(a_out).is_not_null() & (pl.col(a_out) > pl.col("a_seed")) & (pl.col(a_out) <= pl.col("a_seed") + H)).alias("adopt_H"))
    agg = r.group_by("sid").agg(
        (pl.col("sus_in")).sum().alias("N_sus"),
        (pl.col("sus_in") & pl.col("unc")).sum().alias("U"),
        pl.col("recept").sum().alias("R"),
        (pl.col("sus_in") & pl.col("adopt_H")).sum().alias("S"),
        (pl.col("sus") & ~pl.col("in_room")).sum().alias("N_out"),
        (pl.col("sus") & ~pl.col("in_room") & pl.col("adopt_H")).sum().alias("S_out"),
    )
    s = seeds.join(agg, on="sid", how="left").with_columns(pl.col("N_sus", "U", "R", "S", "N_out", "S_out").fill_null(0))
    s = s.with_columns(pl.col("N_sus").log1p().alias("lN"), pl.col("U").log1p().alias("lU"), pl.col("R").log1p().alias("lR"),
                       pl.col("instr").fill_null(0).log1p().alias("lstat"), pl.col("human").cast(pl.Float64).alias("human_f"),
                       (pl.col("tod") * 1.0).alias("tod"), (pl.col("tod") < 0.125).cast(pl.Float64).alias("first30"),
                       pl.col("share").fill_null(0.0))
    s = s.with_columns(pl.col("human_f").alias("human"))
    s = s.with_columns(((pl.col("N_sus") >= MIN_SUS) & ~pl.col("censored")).alias("eligible"))
    return s, r


def eligible_periods(s: pl.DataFrame) -> list[int]:
    c = s.filter(pl.col("eligible")).group_by("goal_no").len()
    return sorted(c.filter(pl.col("len") >= MIN_SEEDS)["goal_no"].to_list())


# ============================================================================ NB2 regression with period fixed effects
def _nb_unpack(theta, G, K):
    return theta[:G], theta[G:G + K], theta[G + K]


def nb_fit(y, X, gi, G, theta0=None, offset=None, ridge_tau=None):
    """NB2 with group intercepts (gi in 0..G-1), slopes on X (n x K) and log-dispersion. Returns theta, loglik.
    ridge_tau: partial pooling of the group intercepts toward a common mean mu (penalty (a_g - mu)^2 / 2 tau^2; card
    exception (d)); None = plain fixed effects. theta layout: [a_1..a_G, b_1..b_K, log phi] (+ mu if ridge)."""
    y = np.asarray(y, float)
    X = np.zeros((len(y), 0)) if X is None else np.asarray(X, float)
    K = X.shape[1]
    off = np.zeros(len(y)) if offset is None else offset
    rid = ridge_tau is not None
    if theta0 is None:
        m = np.array([y[gi == g].mean() if (gi == g).any() else 0.0 for g in range(G)])
        theta0 = np.concatenate([np.log(m + 0.05), np.zeros(K), [0.0]] + ([[np.log(y.mean() + 0.05)]] if rid else []))

    def f(th):
        a, b, lphi = _nb_unpack(th, G, K)
        lphi = np.clip(lphi, -8, 6)
        r = np.exp(-lphi)
        eta = a[gi] + X @ b + off
        mu = np.exp(np.clip(eta, -30, 30))
        ll = gammaln(y + r) - gammaln(r) - gammaln(y + 1) + r * np.log(r / (r + mu)) + y * np.log(mu / (r + mu) + 1e-300)
        de = r * (y - mu) / (r + mu)
        dr = digamma(y + r) - digamma(r) + np.log(r / (r + mu)) + 1 - (y + r) / (r + mu)
        ga = np.bincount(gi, weights=de, minlength=G)
        gb = X.T @ de
        gl = np.sum(dr) * (-r)
        obj = -ll.sum()
        grad = -np.concatenate([ga, gb, [gl]])
        if rid:
            m0 = th[-1]
            dev = a - m0
            obj += 0.5 * (dev ** 2).sum() / ridge_tau ** 2
            grad[:G] += dev / ridge_tau ** 2
            grad = np.concatenate([grad, [-dev.sum() / ridge_tau ** 2]])
        return obj, grad

    res = minimize(f, theta0, jac=True, method="L-BFGS-B", options=dict(maxiter=2000))
    th = res.x[:-1] if rid else res.x
    return th, float(nb_loglik_obs(th, y, X, gi, G, offset).sum())


def nb_loglik_obs(theta, y, X, gi, G, offset=None):
    K = 0 if X is None else X.shape[1]
    a, b, lphi = _nb_unpack(theta, G, K)
    r = np.exp(-np.clip(lphi, -8, 6))
    eta = a[gi] + (X @ b if K else 0) + (0 if offset is None else offset)
    mu = np.exp(np.clip(eta, -30, 30))
    return gammaln(y + r) - gammaln(r) - gammaln(y + 1) + r * np.log(r / (r + mu)) + y * np.log(mu / (r + mu) + 1e-300)


def nb_scores(theta, y, X, gi, G):
    """Per-observation score vectors (for cluster-robust SEs)."""
    K = X.shape[1]
    a, b, lphi = _nb_unpack(theta, G, K)
    r = np.exp(-np.clip(lphi, -8, 6))
    mu = np.exp(np.clip(a[gi] + X @ b, -30, 30))
    de = r * (y - mu) / (r + mu)
    dr = (digamma(y + r) - digamma(r) + np.log(r / (r + mu)) + 1 - (y + r) / (r + mu)) * (-r)
    S = np.zeros((len(y), G + K + 1))
    S[np.arange(len(y)), gi] = de
    S[:, G:G + K] = X * de[:, None]
    S[:, -1] = dr
    return S


def num_hessian(fun, th, eps=1e-4):
    n = len(th)
    H = np.zeros((n, n))
    g0 = fun(th)
    for i in range(n):
        e = np.zeros(n); e[i] = eps
        H[:, i] = (fun(th + e) - g0) / eps
    return (H + H.T) / 2


def nb_robust_se(theta, y, X, gi, G, cl):
    """Cluster-robust sandwich SEs for the slopes."""
    K = X.shape[1]

    def grad(th):
        return nb_scores(th, y, X, gi, G).sum(0)
    Hm = -num_hessian(grad, theta)
    try:
        Hinv = np.linalg.pinv(Hm)
    except np.linalg.LinAlgError:
        return np.full(K, np.nan)
    S = nb_scores(theta, y, X, gi, G)
    _, inv = np.unique(cl, return_inverse=True)
    Sc = np.zeros((inv.max() + 1, S.shape[1]))
    np.add.at(Sc, inv, S)
    V = Hinv @ (Sc.T @ Sc) @ Hinv
    return np.sqrt(np.clip(np.diag(V)[G:G + K], 0, None))


MODELS = {
    "M0": [], "M_N": ["lN"], "M_U": ["lU"], "M_R": ["lR"], "M_status": ["lstat", "human"], "M_share": ["share"],
    "M_tod": ["tod", "first30"], "M_full": ["lN", "lU", "lstat", "human", "share", "tod", "first30"],
    "M_full+R": ["lN", "lU", "lstat", "human", "share", "tod", "first30", "lR"],
}


def design(s: pl.DataFrame, cols, fe: str = "goal_no"):
    gk = s[fe].to_numpy()
    _, gi = np.unique(gk, return_inverse=True)
    X = np.column_stack([s[c].to_numpy().astype(float) for c in cols]) if cols else np.zeros((s.height, 0))
    return s["S"].to_numpy().astype(float), X, gi, int(gi.max() + 1)


def seed_models(s: pl.DataFrame, cv: str = "lodo", nfold: int = 5, models=MODELS, robust=True, fe="goal_no", rng=None, ridge_tau=None):
    """Fit every model (period FE) on eligible seeds; day-blocked CV log score per seed; slopes with day-cluster SEs.
    cv: 'lodo' (leave one active day out) or 'kfold' (days hashed into nfold folds)."""
    s = s.filter(pl.col("eligible")).sort("sid")
    day = (s["goal_no"].cast(pl.String) + "_" + s["pt_date"]).to_numpy()
    udays, dix = np.unique(day, return_inverse=True)
    if cv == "lodo":
        folds = dix
    else:
        rng = rng or np.random.default_rng(0)
        perm = rng.permutation(len(udays))
        folds = (perm % nfold)[dix]
    out = {}
    cvll = {}
    for name, cols in models.items():
        y, X, gi, G = design(s, cols, fe)
        th, ll = nb_fit(y, X, gi, G, ridge_tau=ridge_tau)
        se = nb_robust_se(th, y, X, gi, G, dix) if (robust and X.shape[1]) else np.full(X.shape[1], np.nan)
        out[name] = dict(cols=cols, coef=th[G:G + X.shape[1]].tolist(), se=se.tolist(), ll=ll, n=int(len(y)),
                         phi=float(np.exp(th[-1])))
        # CV
        lls = np.full(len(y), np.nan)
        for f in np.unique(folds):
            te = folds == f
            tr = ~te
            gtr = np.unique(gi[tr])
            okte = te & np.isin(gi, gtr)
            if not okte.any():
                continue
            m = {g: i for i, g in enumerate(gtr)}
            gi_tr = np.array([m[g] for g in gi[tr]])
            th_tr, _ = nb_fit(y[tr], X[tr], gi_tr, len(gtr), ridge_tau=ridge_tau)
            gi_te = np.array([m[g] for g in gi[okte]])
            lls[okte] = nb_loglik_obs(th_tr, y[okte], X[okte], gi_te, len(gtr))
        cvll[name] = lls
    keep = np.all(np.isfinite(np.column_stack(list(cvll.values()))), axis=1)
    for name in models:
        out[name]["cv_ll"] = float(np.nansum(cvll[name][keep]))
    goals = s["goal_no"].to_numpy()
    return out, {k: v[keep] for k, v in cvll.items()}, goals[keep]


def cv_compare(cvll: dict, goals: np.ndarray, a: str, b: str, nboot: int = 2000, rng=None):
    """Summed CV log-score difference a - b, with a period-cluster bootstrap 90% CI."""
    rng = rng or np.random.default_rng(1)
    d = cvll[a] - cvll[b]
    ug = np.unique(goals)
    per = np.array([d[goals == g].sum() for g in ug])
    bs = np.array([per[rng.integers(0, len(ug), len(ug))].sum() for _ in range(nboot)])
    return dict(diff=float(d.sum()), lo90=float(np.quantile(bs, 0.05)), hi90=float(np.quantile(bs, 0.95)),
                n_periods_pos=int((per > 0).sum()), n_periods=int(len(per)), median_period=float(np.median(per)),
                per_period={int(g): float(v) for g, v in zip(ug, per)})


# ============================================================================ agent-level conditional Poisson (Breslow)
def agent_table(s: pl.DataFrame, r: pl.DataFrame, variant: str = "label") -> pl.DataFrame:
    """Susceptible in-room recipients of eligible seeds who read the seed within H and have a full follow-up.
    y = adopts X within FU after its own read-out. clu = period-day cluster of the seed."""
    a_out = f"a_{variant}"
    el = s.filter(pl.col("eligible")).select("sid", pl.col("pt_date").alias("seed_day"))
    t = r.join(el, on="sid", how="inner").filter(pl.col("sus_in") & pl.col("a_read").is_not_null()
                                                 & (pl.col("a_read") <= pl.col("a_seed") + H_S)
                                                 & (pl.col("a_read") + FU_S <= pl.col("a_gend")))
    t = t.with_columns((pl.col(a_out).is_not_null() & (pl.col(a_out) >= pl.col("a_seed")) & (pl.col(a_out) <= pl.col("a_read") + FU_S)).cast(pl.Float64).alias("y"),
                       pl.col("calls30").cast(pl.Float64).log1p().alias("lcalls"), pl.col("talk30").cast(pl.Float64).alias("talk"),
                       pl.col("timely").cast(pl.Float64).alias("x_timely"), pl.col("unc").cast(pl.Float64).alias("x_unc"),
                       (pl.col("timely") & pl.col("unc")).cast(pl.Float64).alias("x_recept"),
                       (pl.col("goal_no").cast(pl.String) + "_" + pl.col("seed_day")).alias("clu"))
    return t


def cpois_fit(y, X, strata, beta0=None, iters=50):
    """Breslow conditional Poisson / Cox-with-ties partial likelihood stratified by `strata`. Returns beta, cov (model), ll."""
    _, si = np.unique(strata, return_inverse=True)
    S = si.max() + 1
    d = np.bincount(si, weights=y, minlength=S)
    use = d[si] > 0
    y, X, si = y[use], X[use], si[use]
    _, si = np.unique(si, return_inverse=True)
    S = si.max() + 1 if len(si) else 0
    d = np.bincount(si, weights=y, minlength=S)
    K = X.shape[1]
    b = np.zeros(K) if beta0 is None else beta0.copy()
    ll_old = -np.inf
    for _ in range(iters):
        eta = np.clip(X @ b, -30, 30)
        w = np.exp(eta)
        sw = np.bincount(si, weights=w, minlength=S)
        swx = np.zeros((S, K)); np.add.at(swx, si, X * w[:, None])
        ll = float((y * eta).sum() - (d * np.log(sw)).sum())
        mx = swx / sw[:, None]
        g = X.T @ y - (d[:, None] * mx).sum(0)
        Hs = np.zeros((K, K))
        for k in range(K):
            for l in range(k, K):
                sxx = np.bincount(si, weights=w * X[:, k] * X[:, l], minlength=S)
                v = (d * (sxx / sw - mx[:, k] * mx[:, l])).sum()
                Hs[k, l] = Hs[l, k] = v
        try:
            step = np.linalg.solve(Hs + 1e-9 * np.eye(K), g)
        except np.linalg.LinAlgError:
            break
        b = b + step
        if abs(ll - ll_old) < 1e-8:
            break
        ll_old = ll
    cov = np.linalg.pinv(Hs) if K else np.zeros((0, 0))
    return b, cov, ll, (y, X, si, d)


def cpois_robust(b, aux, cl):
    """Cluster-robust SE for the conditional Poisson (score per stratum, clustered)."""
    y, X, si, d = aux
    S = si.max() + 1
    w = np.exp(np.clip(X @ b, -30, 30))
    sw = np.bincount(si, weights=w, minlength=S)
    swx = np.zeros((S, X.shape[1])); np.add.at(swx, si, X * w[:, None])
    mx = swx / sw[:, None]
    # per-stratum score
    sy = np.zeros((S, X.shape[1])); np.add.at(sy, si, X * y[:, None])
    sc = sy - d[:, None] * mx
    Hs = np.zeros((X.shape[1],) * 2)
    for k in range(X.shape[1]):
        for l in range(X.shape[1]):
            sxx = np.bincount(si, weights=w * X[:, k] * X[:, l], minlength=S)
            Hs[k, l] = (d * (sxx / sw - mx[:, k] * mx[:, l])).sum()
    Hinv = np.linalg.pinv(Hs)
    _, inv = np.unique(cl, return_inverse=True)
    C = np.zeros((inv.max() + 1, X.shape[1])); np.add.at(C, inv, sc)
    V = Hinv @ (C.T @ C) @ Hinv
    return np.sqrt(np.clip(np.diag(V), 0, None))


def agent_rr(t: pl.DataFrame, xcols=("x_timely", "x_unc", "lcalls", "talk"), extra_fe: str | None = None):
    """Pooled RR for each covariate (seed strata), period-day cluster-robust 95% CI. extra_fe: add dummies (e.g. agent)."""
    if t.height == 0 or t["y"].sum() == 0:
        return dict(n=int(t.height), n_adopt=0)
    y = t["y"].to_numpy(); X = np.column_stack([t[c].to_numpy().astype(float) for c in xcols])
    cols = list(xcols)
    if extra_fe:
        lv = np.unique(t[extra_fe].to_numpy())
        D = (t[extra_fe].to_numpy()[:, None] == lv[None, 1:]).astype(float)
        X = np.column_stack([X, D]); cols += [f"{extra_fe}_{v}" for v in lv[1:]]
    keepc = [i for i in range(X.shape[1]) if np.std(X[:, i]) > 0]
    X = X[:, keepc]; cols = [cols[i] for i in keepc]
    strata = t["sid"].to_numpy()
    clu = t["clu"].to_numpy()
    b, cov, ll, aux = cpois_fit(y, X, strata)
    # cluster of each used stratum
    _, si_all = np.unique(strata, return_inverse=True)
    d_all = np.bincount(si_all, weights=y)
    use = d_all[si_all] > 0
    _, si_use = np.unique(si_all[use], return_inverse=True)
    clu_use = clu[use]
    first = np.zeros(si_use.max() + 1, dtype=int)
    first[si_use[::-1]] = np.arange(len(si_use))[::-1]
    se = cpois_robust(b, aux, clu_use[first])
    res = dict(n=int(t.height), n_adopt=int(y.sum()), n_strata=int(si_use.max() + 1), ll=float(ll))
    for i, c in enumerate(cols):
        if extra_fe and c.startswith(extra_fe + "_"):
            continue
        res[c] = dict(rr=float(np.exp(b[i])), lo=float(np.exp(b[i] - 1.96 * se[i])), hi=float(np.exp(b[i] + 1.96 * se[i])),
                      beta=float(b[i]), se=float(se[i]))
    return res


# ============================================================================ shared-field diagnostics
def field_diagnostics(s: pl.DataFrame, r: pl.DataFrame, variant: str = "label"):
    a_out = f"a_{variant}"
    el = s.filter(pl.col("eligible")).select("sid")
    x = r.join(el, on="sid", how="inner")
    # F1: in-room agents not adopted before a_seed - 2h; adoptions in [-30,0) vs (0,30] min
    f1 = x.filter(pl.col("in_room") & (pl.col(a_out).is_null() | (pl.col(a_out) >= pl.col("a_seed") - 7200)))
    dlt = (pl.col(a_out) - pl.col("a_seed"))
    pre = f1.filter((dlt >= -1800) & (dlt < 0)).height
    post = f1.filter((dlt > 0) & (dlt <= 1800)).height
    ev = f1.filter(pl.col(a_out).is_not_null() & (dlt >= -7200) & (dlt <= 7200)).select(((dlt // 900).cast(pl.Int32)).alias("bin"))
    curve = ev.group_by("bin").len().sort("bin")
    # F2: other-room vs same-room adoption probability within H (multi-room seeds only)
    multi = x.filter(~pl.col("in_room") & pl.col("sus")).select("sid").unique()
    xm = x.join(multi, on="sid", how="inner").filter(pl.col("sus"))
    p_in = xm.filter(pl.col("in_room"))["adopt_H"].mean() if xm.filter(pl.col("in_room")).height else None
    p_out = xm.filter(~pl.col("in_room"))["adopt_H"].mean() if xm.filter(~pl.col("in_room")).height else None
    # F3: adopters within H (in-room, susceptible) whose first read of any link to X came after adoption or never
    ad = x.filter(pl.col("sus_in") & pl.col("adopt_H"))
    if "t_flread" in ad.columns and ad.height:
        tcol = f"t_{variant}"
        unexp = ad.filter(pl.col("t_flread").is_null() | (pl.col("t_flread") > pl.col(tcol))).height / ad.height
    else:
        unexp = None
    # F4: late readers (age > 600 s) adopting within FU of read-out: share in the first 3 calls vs uniform expectation
    lr = x.filter(pl.col("sus_in") & (pl.col("age_s") > 600) & pl.col("k_adopt").is_not_null() & pl.col("n_fu").is_not_null()
                  & (pl.col("k_adopt") >= 1) & (pl.col("k_adopt") <= pl.col("n_fu")) & (pl.col("n_fu") >= 1))
    if lr.height:
        obs = (lr["k_adopt"] <= 3).mean()
        exp = (lr["n_fu"].clip(upper_bound=None).map_elements(lambda n: min(3, n) / n, return_dtype=pl.Float64)).mean()
        f4 = dict(n=lr.height, obs=float(obs), exp=float(exp), ratio=float(obs / exp) if exp else None)
    else:
        f4 = dict(n=0)
    return dict(F1=dict(pre=pre, post=post, ratio=(post / pre) if pre else (float("inf") if post else None),
                        curve={int(b): int(n) for b, n in curve.iter_rows()}),
                F2=dict(p_in=p_in, p_out=p_out, ratio=(p_out / p_in) if (p_in and p_out is not None) else None, n_seeds=multi.height),
                F3=dict(unexposed=unexp, n=ad.height), F4=f4)


# ============================================================================ shifted pseudo-seed slopes (lead/lag placebo)
def shift_slopes(s: pl.DataFrame, r: pl.DataFrame, c_mult: float = 1.0, adjust_N: bool = True):
    """Slope of S on log(1+R_delta) (period FE NB, + log(1+N_sus) if adjust_N) for R computed from read-out ages at
    pseudo-seed times a_seed + delta (same susceptible / uncommitted set)."""
    res = {}
    el = s.filter(pl.col("eligible"))
    for dmin in (0,) + tuple(SHIFTS_MIN):
        col = f"age_sh{dmin:+d}"
        rr = r.with_columns((pl.col("sus_in") & pl.col("unc") & pl.col(col).is_not_null() & (pl.col(col) <= pl.col("cyc_s") * c_mult)).alias("rd"))
        Rd = rr.group_by("sid").agg(pl.col("rd").sum().alias("Rd"))
        x = el.join(Rd, on="sid", how="left").with_columns(pl.col("Rd").fill_null(0).log1p().alias("lRd"))
        cols = ["lRd", "lN"] if adjust_N else ["lRd"]
        y, X, gi, G = design(x, cols)
        th, ll = nb_fit(y, X, gi, G)
        day = (x["goal_no"].cast(pl.String) + "_" + x["pt_date"]).to_numpy()
        se = nb_robust_se(th, y, X, gi, G, day)
        res[dmin] = dict(beta=float(th[G]), se=float(se[0]), lo=float(th[G] - 1.96 * se[0]), hi=float(th[G] + 1.96 * se[0]))
    return res


# ============================================================================ meta-analysis
def dersimonian_laird(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0.01) & (se < 10)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return dict(k=0)
    w = 1 / se ** 2
    fe = (w * est).sum() / w.sum()
    Q = (w * (est - fe) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    wr = 1 / (se ** 2 + tau2)
    re = (wr * est).sum() / wr.sum()
    sre = np.sqrt(1 / wr.sum())
    return dict(k=int(len(est)), re=float(re), lo=float(re - 1.96 * sre), hi=float(re + 1.96 * sre), tau2=float(tau2), Q=float(Q))


def auc_within(s: pl.DataFrame, col: str, pos: pl.Expr, neg: pl.Expr):
    """Within-period AUC (pairs compared only within a period; ties 0.5)."""
    num = den = 0.0
    for (g,), d in s.group_by(["goal_no"]):
        a = d.filter(pos)[col].to_numpy().astype(float)
        b = d.filter(neg)[col].to_numpy().astype(float)
        if len(a) == 0 or len(b) == 0:
            continue
        diff = a[:, None] - b[None, :]
        num += (diff > 0).sum() + 0.5 * (diff == 0).sum()
        den += diff.size
    return dict(auc=num / den if den else None, n_pairs=int(den))
