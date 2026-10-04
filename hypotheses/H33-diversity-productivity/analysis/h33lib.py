"""H33 analysis library: two-way FE by alternating projections, CR1 cluster SEs, natural cubic splines,
Simonsohn's two-lines test with the Robin Hood breakpoint, quadratic vertex, day-blocked CV, DerSimonian-Laird.

Used by synthetic.py, evaluate.py and confirm.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h33common as C  # noqa: E402,F401  (thread caps)

import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402


# ------------------------------------------------------------------------------------------ fixed effects
def codes(*arrs):
    """Integer codes for one or more label arrays (combined)."""
    keys = list(zip(*[np.asarray(a).tolist() for a in arrs])) if len(arrs) > 1 else np.asarray(arrs[0]).tolist()
    _, inv = np.unique(np.array([str(k) for k in keys]), return_inverse=True)
    return inv


def demean(X: np.ndarray, groups: list[np.ndarray], tol: float = 1e-9, maxit: int = 1000) -> np.ndarray:
    """Project out several sets of fixed effects (alternating projections). X: n or n x k."""
    X = np.array(X, dtype=np.float64, copy=True)
    one = X.ndim == 1
    if one:
        X = X[:, None]
    cnts = [np.bincount(g) for g in groups]
    for _ in range(maxit):
        delta = 0.0
        for g, c in zip(groups, cnts):
            for j in range(X.shape[1]):
                m = np.bincount(g, weights=X[:, j], minlength=len(c)) / np.maximum(c, 1)
                X[:, j] -= m[g]
                delta = max(delta, float(np.abs(m).max()))
        if delta < tol:
            break
    return X[:, 0] if one else X


def ols_cr(y: np.ndarray, X: np.ndarray, cl: np.ndarray):
    """OLS on already-demeaned data with CR1 cluster-robust covariance. Returns beta, V, resid, G."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    G = int(cl.max()) + 1
    S = np.zeros((G, X.shape[1]))
    np.add.at(S, cl, X * e[:, None])
    n, k = X.shape
    Gu = len(np.unique(cl))
    adj = Gu / max(Gu - 1, 1) * (n - 1) / max(n - k, 1)
    V = adj * XtX_inv @ (S.T @ S) @ XtX_inv
    return b, V, e, Gu


def pval(b, se, G=None):
    z = b / se if se > 0 else np.nan
    if G is not None and G < 50:
        return float(2 * stats.t.sf(abs(z), G - 1)), float(z)
    return float(2 * stats.norm.sf(abs(z))), float(z)


# ------------------------------------------------------------------------------------------ spline
def ns_knots(x, df):
    qs = np.linspace(0.05, 0.95, df + 1)
    return np.quantile(x, qs)


def ns_basis(x, knots):
    """Natural cubic spline basis without intercept (len(knots) - 1 columns: x, then nonlinear terms)."""
    x = np.asarray(x, dtype=np.float64)
    K = len(knots)

    def d(k):
        return (np.clip(x - knots[k], 0, None) ** 3 - np.clip(x - knots[-1], 0, None) ** 3) / (knots[-1] - knots[k])
    cols = [x] + [d(k) - d(K - 2) for k in range(K - 2)]
    return np.column_stack(cols)


# ------------------------------------------------------------------------------------------ design helper
class Design:
    """Holds FE groups, clusters and demeaned controls for repeated fits on the same rows."""

    def __init__(self, groups: list[np.ndarray], cluster: np.ndarray, controls: np.ndarray | None):
        self.groups = groups
        self.cl = codes(cluster)
        self.Z = demean(controls, groups) if controls is not None and controls.size else None

        self._cache = {}

    def dm(self, M, key=None):
        if key is not None:
            if key not in self._cache:
                self._cache[key] = demean(M, self.groups)
            return self._cache[key]
        return demean(M, self.groups)

    def fit(self, y_dm, X_dm):
        X_dm = X_dm[:, None] if X_dm.ndim == 1 else X_dm
        X = X_dm if self.Z is None else np.column_stack([X_dm, self.Z])
        return ols_cr(y_dm, X, self.cl)


def quad_test(D: Design, y_dm, x, x_dm=None):
    X = D.dm(np.column_stack([x, x ** 2]), key=("quad", hash(np.asarray(x, np.float64).tobytes())))
    b, V, e, G = D.fit(y_dm, X)
    se2 = float(np.sqrt(V[1, 1]))
    p2, z2 = pval(b[1], se2, G)
    vertex = float(-b[0] / (2 * b[1])) if b[1] != 0 else np.nan
    return {"b1": float(b[0]), "b2": float(b[1]), "se2": se2, "p2": p2, "vertex": vertex}


def spline_fit(D: Design, y_dm, x, df=4, grid_n=200):
    kn = ns_knots(x, df)
    B = ns_basis(x, kn)
    b, V, e, G = D.fit(y_dm, D.dm(B, key=("spline", df, hash(np.asarray(x, np.float64).tobytes()))))
    k = B.shape[1]
    lo, hi = np.quantile(x, [0.05, 0.95])
    grid = np.linspace(lo, hi, grid_n)
    Bg = ns_basis(grid, kn)
    f = Bg @ b[:k]
    im = int(np.argmax(f))
    dB = Bg[im][None, :] - Bg
    se_diff = np.sqrt(np.einsum("ij,jk,ik->i", dB, V[:k, :k], dB))
    flat_grid = (f[im] - f) <= se_diff
    fx = B @ b[:k]
    dBx = ns_basis(np.array([grid[im]]), kn) - B
    se_x = np.sqrt(np.einsum("ij,jk,ik->i", dBx, V[:k, :k], dBx))
    flat_obs = x[(f[im] - fx) <= se_x]
    p10, p90 = np.quantile(x, [0.10, 0.90])
    return {"grid": grid, "f": f - f[im], "se": se_diff, "x_max": float(grid[im]),
            "interior": bool(p10 < grid[im] < p90), "flat_obs": flat_obs, "flat_grid": flat_grid,
            "beta": b[:k], "V": V[:k, :k], "knots": kn}


def interrupted(D: Design, y_dm, x, xc):
    hi = (x >= xc).astype(np.float64)
    xl = (x - xc) * (1 - hi)
    xh = (x - xc) * hi
    X = D.dm(np.column_stack([xl, xh, hi]))
    b, V, e, G = D.fit(y_dm, X)
    s1, s2 = float(np.sqrt(V[0, 0])), float(np.sqrt(V[1, 1]))
    p1, z1 = pval(b[0], s1, G)
    p2, z2 = pval(b[1], s2, G)
    return {"xc": float(xc), "b1": float(b[0]), "se1": s1, "p1": p1, "z1": z1, "b2": float(b[1]), "se2": s2,
            "p2": p2, "z2": z2, "n_lo": int((x < xc).sum()), "n_hi": int((x >= xc).sum()), "G": G}


def two_lines(D: Design, y_dm, x, df=4, sp=None):
    """Simonsohn (2018) two-lines test with the Robin Hood breakpoint."""
    sp = sp or spline_fit(D, y_dm, x, df)
    flat = sp["flat_obs"] if len(sp["flat_obs"]) >= 5 else x
    xc0 = float(np.median(flat))
    r0 = interrupted(D, y_dm, x, xc0)
    z1, z2 = abs(r0["z1"]), abs(r0["z2"])
    q = z2 / (z1 + z2) if (z1 + z2) > 0 else 0.5
    xc = float(np.quantile(flat, q))
    lo, hi = np.quantile(x, [0.02, 0.98])
    xc = float(np.clip(xc, lo, hi))
    r = interrupted(D, y_dm, x, xc)
    r["xc0"] = xc0
    r["x_max"] = sp["x_max"]
    r["interior"] = sp["interior"]
    r["u_supported"] = bool(r["b1"] > 0 and r["b2"] < 0 and r["p1"] < 0.05 and r["p2"] < 0.05)
    return r, sp


def quad_supported(q, x):
    p10, p90 = np.quantile(x, [0.10, 0.90])
    return bool(q["b2"] < 0 and q["p2"] < 0.05 and p10 < q["vertex"] < p90)


# ------------------------------------------------------------------------------------------ meta-analysis
def dersimonian_laird(b, se):
    b, se = np.asarray(b, float), np.asarray(se, float)
    ok = np.isfinite(b) & np.isfinite(se) & (se > 0)
    b, se = b[ok], se[ok]
    k = len(b)
    if k < 2:
        return {"k": k, "est": float(b[0]) if k else np.nan, "se": float(se[0]) if k else np.nan, "p": np.nan, "tau2": np.nan, "I2": np.nan}
    w = 1 / se ** 2
    bf = (w * b).sum() / w.sum()
    Q = (w * (b - bf) ** 2).sum()
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    ws = 1 / (se ** 2 + tau2)
    est = (ws * b).sum() / ws.sum()
    s = np.sqrt(1 / ws.sum())
    return {"k": k, "est": float(est), "se": float(s), "p": float(2 * stats.norm.sf(abs(est / s))), "tau2": float(tau2),
            "I2": float(max(0.0, (Q - (k - 1)) / Q)) if Q > 0 else 0.0}


# ------------------------------------------------------------------------------------------ fixed-effect recovery / CV
def fe_values(r: np.ndarray, groups: list[np.ndarray], maxit=1000, tol=1e-10):
    """Additive FE estimates (one array per group set) explaining r = sum_g a_g[group] + e."""
    a = [np.zeros(int(g.max()) + 1) for g in groups]
    cnts = [np.bincount(g) for g in groups]
    res = r.astype(np.float64).copy()
    for _ in range(maxit):
        delta = 0.0
        for j, (g, c) in enumerate(zip(groups, cnts)):
            m = np.bincount(g, weights=res, minlength=len(c)) / np.maximum(c, 1)
            a[j] += m
            res -= m[g]
            delta = max(delta, float(np.abs(m).max()))
        if delta < tol:
            break
    return a


def cv_day_blocked(y, x, controls, au, day, k=5, seed=0, spline_df=4):
    """5-fold day-blocked CV. Held-out loss uses within-held-out-day centering (the day FE of an unseen day is
    unknown and is the same nuisance for every model). Returns mean squared error per model."""
    rng = np.random.default_rng(seed)
    udays = np.unique(day)
    fold_of_day = dict(zip(udays, rng.permutation(np.arange(len(udays)) % k)))
    fold = np.array([fold_of_day[d] for d in day])
    kn = ns_knots(x, spline_df)
    feats = {"fe_controls": np.zeros((len(x), 0)), "linear": x[:, None], "quadratic": np.column_stack([x, x ** 2]),
             "spline": ns_basis(x, kn)}
    sse = {m: 0.0 for m in feats}
    nobs = 0
    for f in range(k):
        tr, te = fold != f, fold == f
        au_tr = set(au[tr].tolist())
        te = te & np.array([a in au_tr for a in au])
        if te.sum() == 0:
            continue
        g_tr = [codes(au[tr]), codes(day[tr])]
        au_map = {a: i for i, a in enumerate(np.unique(au[tr].astype(str)))}
        for m, F in feats.items():
            X = np.column_stack([F, controls]) if controls is not None else F
            Xtr, ytr = X[tr], y[tr]
            if X.shape[1]:
                b = np.linalg.lstsq(demean(Xtr, g_tr), demean(ytr, g_tr), rcond=None)[0]
            else:
                b = np.zeros(0)
            r = ytr - (Xtr @ b if X.shape[1] else 0)
            a_au, _ = fe_values(r, g_tr)
            pred = (X[te] @ b if X.shape[1] else 0) + a_au[[au_map[str(a)] for a in au[te]]]
            # centre within held-out day
            dte = day[te]
            _, di = np.unique(dte, return_inverse=True)
            cnt = np.bincount(di)
            yc = y[te] - (np.bincount(di, weights=y[te]) / cnt)[di]
            pc = pred - (np.bincount(di, weights=pred) / cnt)[di]
            sse[m] += float(((yc - pc) ** 2).sum())
        nobs += int(te.sum())
    return {m: v / max(nobs, 1) for m, v in sse.items()} | {"n": nobs}


# ------------------------------------------------------------------------------------------ data
def eligibility(ad, x_col: str = "pr10", y_col: str | None = None):
    """The card's pre-registered period eligibility rule, applied to an agent_day frame. Round 1b: the output share is
    computed on the primary outcome (work commits) and units before #30 are excluded (ambiguous zeros)."""
    import polars as pl
    y_col = y_col or C.Y_PRIMARY
    x = ad.filter(pl.col(x_col).is_not_null() & (pl.col("goal_no") >= C.MIN_GOAL))
    per = x.group_by("unit").agg(pl.len().alias("n_ad"), (pl.col(y_col) > 0).mean().alias("share_w"),
                                 pl.col("regime").first(), pl.col("agent").n_unique().alias("n_agents"),
                                 pl.col("pt_date").n_unique().alias("n_days"))
    ag = x.group_by("unit", "agent").len().filter(pl.col("len") >= 3).group_by("unit").len().rename({"len": "agents3"})
    per = per.join(ag, on="unit", how="left").with_columns(pl.col("agents3").fill_null(0))
    return per.with_columns(((pl.col("n_ad") >= 30) & (pl.col("agents3") >= 4) & (pl.col("share_w") >= 0.2)).alias("eligible"))


def load_pooled(x_col: str = "pr10", y_col: str = "writes", units=None, root=None, guard: bool = True):
    """Eligible-unit agent-days with x defined. Returns the frame plus arrays: x, y = log1p(count), controls
    (log raw chat, log1p engaged minutes), au (agent x unit code), day code.
    root=None: exploratory tables (eligibility.parquet); otherwise eligibility is recomputed on root's tables."""
    import polars as pl
    if root is None:
        el = pl.read_parquet(C.OUT / "eligibility.parquet").filter("eligible")["unit"].to_list()
        ad = C.load_agent_day()
    else:
        ad = C.load_agent_day(root)
        el = eligibility(ad).filter("eligible")["unit"].to_list()
    if units is not None:
        el = [u for u in el if u in units]
    ad = ad.filter(pl.col("unit").is_in(el) & pl.col(x_col).is_not_null()).sort("pt_date", "agent")
    if guard:
        C.refuse_holdout(ad["pt_date"].unique().to_list(), "analysis rows")
    x = ad[x_col].to_numpy().astype(np.float64)
    y = np.log1p(ad[y_col].to_numpy().astype(np.float64))
    Z = np.column_stack([np.log(ad["n_chat_raw"].to_numpy().astype(np.float64)),
                         np.log1p(ad["engaged_min"].to_numpy().astype(np.float64))])
    au = codes(ad["agent"].to_numpy(), ad["unit"].to_numpy())
    day = codes(ad["pt_date"].to_numpy())
    return ad, x, y, Z, au, day
