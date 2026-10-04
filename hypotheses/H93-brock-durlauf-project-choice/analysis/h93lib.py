"""H93 estimators: conditional logit (McFadden) with share coupling, fields, habit and repo fixed effects; cross-fitted
fitness offset; DerSimonian-Laird pooling; Brock-Durlauf mean-field fixed points and their count.

All fits are per choice table `lt` (event x option rows from scheme/h93scheme.long_table).
"""
from __future__ import annotations

import math

import numpy as np
import polars as pl

MODELS = {
    "M0": ["s"],
    "M1": ["s", "named"],
    "M2": ["s", "named", "prev"],
    "M3a": ["s", "named", "prev", "fe_cf"],
    "M3b": ["s", "prev"],            # + repo fixed effects (named absorbed)
    "M4": ["s", "named", "prev", "logcum"],
    "R3": ["logn1", "named", "prev", "logcum"],  # neutral copying form log(1 + n), on the validated M4 base (A1)
    "SPLIT_room": ["s_in", "s_out", "named", "prev", "logcum"],
    "SPLIT_lab": ["s_same", "s_cross", "named", "prev", "logcum"],
    "SPLIT_seen": ["s_seen", "s_unseen", "named", "prev", "logcum"],
    "M4_nonamed": ["s", "prev", "logcum"],     # kickoff-free placebo: named options removed from the choice sets
    "SPLIT_read": ["s_read", "s_noread", "named", "prev", "logcum"],   # A2 (post hoc): ledger reads of others' links only
}
SHARE = {"M0": "s", "M1": "s", "M2": "s", "M3a": "s", "M3b": "s", "M4": "s", "R3": "logn1"}


def add_features(lt: pl.DataFrame, n_folds: int = 4) -> pl.DataFrame:
    """logn1 and the cross-fitted fitness offset fe_cf = log((k_j(-f) + 0.5) / (a_j(-f) + 1)): the option's empirical
    choice rate on the other time folds of the same unit (k chosen, a offered). NEW gets 0."""
    lt = lt.with_columns(pl.col("n").cast(pl.Float64).log1p().alias("logn1"))
    k = lt.group_by("unit", "opt", "fold").agg(pl.col("chosen").sum().alias("k"), pl.len().alias("a"))
    tot = k.group_by("unit", "opt").agg(pl.col("k").sum().alias("K"), pl.col("a").sum().alias("A"))
    k = k.join(tot, on=["unit", "opt"]).with_columns(
        ((pl.col("K") - pl.col("k") + 0.5) / (pl.col("A") - pl.col("a") + 1.0)).log().alias("fe_cf"))
    lt = lt.join(k.select("unit", "opt", "fold", "fe_cf"), on=["unit", "opt", "fold"], how="left")
    return lt.with_columns(pl.when(pl.col("new")).then(0.0).otherwise(pl.col("fe_cf")).alias("fe_cf"))


def design(lt: pl.DataFrame, cols: list[str], fe: bool = False, unit_new: bool = True):
    """X (rows x p), names, chosen (bool), group starts (sorted by eid)."""
    lt = lt.sort("eid")
    X = [lt[c].cast(pl.Float64).to_numpy() for c in cols]
    names = list(cols)
    units = sorted(lt["unit"].unique().to_list())
    if unit_new and len(units) > 1:
        for u in units:
            X.append(((lt["new"]) & (lt["unit"] == u)).cast(pl.Float64).to_numpy())
            names.append(f"new[{u}]")
    else:
        X.append(lt["new"].cast(pl.Float64).to_numpy())
        names.append("new")
    nfe = 0
    if fe:
        opts = lt.filter(~pl.col("new"))["opt"].unique().sort().to_list()
        ix = {o: k for k, o in enumerate(opts)}
        oi = np.array([ix.get(o, -1) for o in lt["opt"].to_list()])
        F = np.zeros((lt.height, len(opts)))
        m = oi >= 0
        F[np.where(m)[0], oi[m]] = 1.0
        X = np.column_stack(X + [F]) if X else F
        names += [f"fe[{o}]" for o in opts]
        nfe = len(opts)
    else:
        X = np.column_stack(X)
    eid = lt["eid"].to_numpy()
    starts = np.r_[0, np.flatnonzero(np.diff(eid)) + 1]
    y = lt["chosen"].to_numpy().astype(bool)
    return X, names, y, starts, nfe


def _seg_logsumexp(u, starts):
    mx = np.maximum.reduceat(u, starts)
    rep = np.repeat(mx, np.diff(np.r_[starts, len(u)]))
    s = np.add.reduceat(np.exp(u - rep), starts)
    return mx + np.log(s), rep


def clogit_fit(X, y, starts, ridge=None, max_iter=100, tol=1e-9):
    """Newton-Raphson MLE with step halving. ridge: per-parameter L2 penalty vector (or None)."""
    n, p = X.shape
    th = np.zeros(p)
    lens = np.diff(np.r_[starts, n])
    seg = np.repeat(np.arange(len(starts)), lens)
    R = np.zeros(p) if ridge is None else np.asarray(ridge, float)

    def stats(th):
        u = X @ th
        lse, _ = _seg_logsumexp(u, starts)
        ll = float(u[y].sum() - lse.sum()) - 0.5 * float(R @ (th * th))
        pr = np.exp(u - lse[seg])
        xb = np.add.reduceat(X * pr[:, None], starts)          # E x per event
        g = X[y].sum(0) - xb.sum(0) - R * th
        Xw = X * np.sqrt(pr)[:, None]
        H = Xw.T @ Xw - xb.T @ xb + np.diag(R)                   # observed information
        return ll, g, H, pr
    ll, g, H, pr = stats(th)
    it = 0
    for it in range(max_iter):
        try:
            step = np.linalg.solve(H + 1e-10 * np.eye(p), g)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(H, g, rcond=None)[0]
        t = 1.0
        while True:
            ll2, g2, H2, pr2 = stats(th + t * step)
            if ll2 >= ll - 1e-12 or t < 1e-6:
                break
            t /= 2
        th = th + t * step
        conv = abs(ll2 - ll) < tol
        ll, g, H, pr = ll2, g2, H2, pr2
        if conv:
            break
    try:
        cov = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        cov = np.linalg.pinv(H)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    ok = bool(np.all(np.isfinite(th)) and np.max(np.abs(th[: min(p, 8)])) < 50)
    return {"theta": th, "se": se, "cov": cov, "ll": ll, "iters": it + 1, "ok": ok, "pr": pr}


def fit(lt: pl.DataFrame, model: str, unit_new: bool = True, fe_ridge: float = 0.1, drop_blind: bool = False):
    if drop_blind and "blind" in lt.columns:
        lt = lt.filter(~pl.col("blind").fill_null(False))
    cols = MODELS[model]
    fe = model == "M3b"
    X, names, y, starts, nfe = design(lt, cols, fe=fe, unit_new=unit_new)
    # drop all-zero non-FE columns (e.g. no named option in the table)
    keep = [k for k in range(X.shape[1]) if np.any(X[:, k] != 0) or names[k].startswith("fe[")]
    if fe:
        keep = [k for k in keep if not names[k].startswith("fe[") or X[y, k].sum() > 0 or True]
    X = X[:, keep]
    names = [names[k] for k in keep]
    ridge = np.array([fe_ridge if nm.startswith("fe[") else 0.0 for nm in names]) if fe else None
    r = clogit_fit(X, y, starts, ridge=ridge)
    out = {"model": model, "names": names, "theta": r["theta"].tolist(), "se": r["se"].tolist(), "ll": r["ll"],
           "n_events": int(len(starts)), "n_rows": int(X.shape[0]), "ok": r["ok"], "iters": r["iters"],
           "k": int(sum(1 for nm in names if not nm.startswith("fe[")))}
    sh = SHARE.get(model)
    if sh and sh in names:
        k = names.index(sh)
        out["gamma"] = float(r["theta"][k]); out["gamma_se"] = float(r["se"][k])
        out["gamma_lo"] = out["gamma"] - 1.96 * out["gamma_se"]; out["gamma_hi"] = out["gamma"] + 1.96 * out["gamma_se"]
    out["_cov"] = r["cov"]
    return out


def coef(res: dict, name: str):
    if name not in res["names"]:
        return None, None
    k = res["names"].index(name)
    return res["theta"][k], res["se"][k]


def dl_pool(ests, ses):
    """DerSimonian-Laird random-effects pool: (est, se, lo, hi, tau2)."""
    e = np.array([x for x, s in zip(ests, ses) if s and np.isfinite(s) and s > 0], float)
    s = np.array([s for x, s in zip(ests, ses) if s and np.isfinite(s) and s > 0], float)
    if len(e) == 0:
        return None
    if len(e) == 1:
        return {"est": float(e[0]), "se": float(s[0]), "lo": float(e[0] - 1.96 * s[0]), "hi": float(e[0] + 1.96 * s[0]),
                "tau2": 0.0, "k": 1}
    w = 1 / s ** 2
    mu = (w * e).sum() / w.sum()
    Q = (w * (e - mu) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (len(e) - 1)) / c) if c > 0 else 0.0
    ws = 1 / (s ** 2 + tau2)
    mu = (ws * e).sum() / ws.sum()
    se = math.sqrt(1 / ws.sum())
    return {"est": float(mu), "se": se, "lo": float(mu - 1.96 * se), "hi": float(mu + 1.96 * se), "tau2": float(tau2),
            "k": int(len(e))}


def testable(lt: pl.DataFrame, min_events=30, min_existing=10) -> bool:
    ev = lt.group_by("eid").agg(pl.len().alias("k"), (pl.col("chosen") & ~pl.col("new")).any().alias("ex"))
    ev = ev.filter(pl.col("k") >= 2)
    return ev.height >= min_events and int(ev["ex"].sum()) >= min_existing


# ================================================================================================ Brock-Durlauf fixed points
def bd_fields(lt: pl.DataFrame, res: dict, unit: str | None = None):
    """Per-agent option fields at the end of the table: h_ij = b_named named_j + b_own home_ij (+ fe_j), NEW field
    alpha_new. Returns (H [agents x options], h_new, options, agents)."""
    if unit is not None:
        lt = lt.filter(pl.col("unit") == unit)
    opts = sorted(lt.filter(~pl.col("new"))["opt"].unique().to_list())
    agents = sorted(lt["agent"].unique().to_list())
    named = dict(lt.filter(~pl.col("new")).group_by("opt").agg(pl.col("named").max()).iter_rows())
    lcum = dict(lt.filter(~pl.col("new")).group_by("opt").agg(pl.col("logcum").max()).iter_rows())
    bc = coef(res, "logcum")[0] or 0.0
    home = set(map(tuple, lt.filter(pl.col("prev") | pl.col("chosen")).filter(~pl.col("new")).select("agent", "opt").rows()))
    bn = coef(res, "named")[0] or 0.0
    bo = coef(res, "prev")[0] or 0.0
    newnames = [nm for nm in res["names"] if nm.startswith("new")]
    an = res["theta"][res["names"].index(newnames[-1])] if newnames else 0.0
    if unit is not None and f"new[{unit}]" in res["names"]:
        an = res["theta"][res["names"].index(f"new[{unit}]")]
    fe = {nm[3:-1]: th for nm, th in zip(res["names"], res["theta"]) if nm.startswith("fe[")}
    H = np.zeros((len(agents), len(opts)))
    for jj, o in enumerate(opts):
        H[:, jj] += bn * float(bool(named.get(o))) + fe.get(o, 0.0) + bc * float(lcum.get(o, 0.0))
        for ii, a in enumerate(agents):
            if (a, o) in home:
                H[ii, jj] += bo
    return H, an, opts, agents


def bd_map(m, H, hnew, g):
    U = H + g * m[None, :]
    mx = np.maximum(U.max(1), hnew)
    E = np.exp(U - mx[:, None])
    Z = E.sum(1) + np.exp(hnew - mx)
    P = E / Z[:, None]
    return P.mean(0), P


def bd_fixed_points(H, hnew, g, n_random=20, rng=None, corners=8, tol=1e-10, max_iter=20000):
    """Stable fixed points of m = <softmax(h + g m)> from uniform, corner and random starts. Returns list of (m, top)."""
    rng = rng or np.random.default_rng(0)
    K = H.shape[1]
    if K == 0:
        return []
    starts = [np.full(K, 1.0 / (K + 1))]
    order = np.argsort(-H.mean(0))
    for jj in order[:corners]:
        m0 = np.full(K, 0.1 / K)
        m0[jj] = 0.9
        starts.append(m0)
    for _ in range(n_random):
        starts.append(rng.dirichlet(np.ones(K + 1))[:K])
    found = []
    eta = min(0.5, 1.0 / (1.0 + abs(g) / 4.0))   # damping: keeps the iteration contractive for strongly negative g
    for m in starts:
        for _ in range(max_iter):
            f, P = bd_map(m, H, hnew, g)
            m2 = (1 - eta) * m + eta * f
            if np.abs(m2 - m).sum() < tol:
                m = m2
                break
            m = m2
        f, P = bd_map(m, H, hnew, g)
        if np.abs(f - m).sum() > 1e-6:
            continue  # not converged
        # stability under logit (best-response) dynamics dm/dt = F(m) - m: Re(eig(dF/dm)) < 1
        Jm = g * (np.diag(P.mean(0)) - (P.T @ P) / P.shape[0])
        lam = np.linalg.eigvals(Jm) if K <= 400 else np.array([np.abs(Jm).sum(1).max()])
        if float(np.max(lam.real)) >= 1.0:
            continue
        if all(np.abs(m - q).sum() > 0.05 for q, _ in found):
            found.append((m.copy(), float(m.max())))
    return found


def p_multi(lt, res, unit=None, draws=200, seed=0):
    """Parametric-bootstrap probability of >= 2 stable BD fixed points at the fit (main parameters drawn from their
    sampling distribution; FE fixed)."""
    rng = np.random.default_rng(seed)
    names = res["names"]
    main = [k for k, nm in enumerate(names) if not nm.startswith("fe[")]
    cov = np.asarray(res["_cov"])[np.ix_(main, main)]
    th0 = np.asarray(res["theta"])
    H0, an0, opts, agents = bd_fields(lt, res, unit)
    fp0 = bd_fixed_points(H0, an0, res.get("gamma", 0.0), rng=rng)
    cnt = 0
    tot = 0
    try:
        L = np.linalg.cholesky(cov + 1e-12 * np.eye(len(main)))
    except np.linalg.LinAlgError:
        L = np.diag(np.sqrt(np.clip(np.diag(cov), 0, None)))
    for _ in range(draws):
        th = th0.copy()
        th[main] = th0[main] + L @ rng.standard_normal(len(main))
        r2 = dict(res)
        r2["theta"] = th.tolist()
        H, an, _, _ = bd_fields(lt, r2, unit)
        g = th[names.index("s")] if "s" in names else 0.0
        fps = bd_fixed_points(H, an, g, n_random=6, rng=rng, corners=6, tol=1e-9, max_iter=4000)
        tot += 1
        cnt += len(fps) >= 2
    return {"n_fp": len(fp0), "tops": [t for _, t in fp0], "p_multi": cnt / max(tot, 1), "K": len(opts), "N": len(agents)}
