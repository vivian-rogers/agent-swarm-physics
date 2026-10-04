"""H106 library: size-matched culture vectors, split-half reliability, the finite-size decorrelation fit and the
synthetic worlds (no text; holdout already dropped by infra/shared/culture_vectors.py and scheme/build.py).

Residuals follow H81 (Amendment A1) through the shared module infra/shared/culture_vectors.py: exogenous directions
projected (`projectors`), personal vectors = two-way agent + goal fixed effects on the agent's other goals of the
regime (`personal_vectors(method="fe")`), r_{i,b} = Pi (vbar_{i,b} - mu_i^{(-G)}). H81's simulator (variance_scales,
simulate) is re-implemented here with an N-dependent OU rate (no import from H81's folder; STANDARDS §8).

Model (card O3): s~_{bb'} = A exp(-Lambda_{bb'}) + s_inf, Lambda = k6 * |I(a_b') - I(a_b)|, I(a) = int (N(x)/6)^alpha dx.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402
from scipy.stats import t as tdist  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import culture_vectors as CVM  # noqa: E402

CV = ROOT / "data/processed/shared/culture_vectors"
OUT = ROOT / "data/processed/H106-slow-mode-finite-size"
GEMINI_25 = 6
M_SUB = 4
N_REF = 6.0
NE04 = "2025-09-05"
NE08 = "2025-12-10"
NE27 = "2025-08-18"


# ------------------------------------------------------------------------------------------------- loading
def load(model: str, variant: str, regime: str, drop_agents: frozenset = frozenset()):
    ad = pl.read_parquet(CV / "agentdays.parquet").with_row_index("row")
    X = np.load(CV / f"vecs_{model}_{variant}.npy").astype(np.float64)
    ad = ad.filter((pl.col("regime") == regime) & ~pl.col("agent").is_in(list(drop_agents)))
    aday = pl.read_parquet(OUT / "aday.parquet")
    ad = ad.join(aday, on="pt_date", how="left")
    assert ad["a"].null_count() == 0 and not ad["holdout"].any()
    blocks = pl.read_parquet(OUT / f"blocks_{regime}.parquet")
    return ad, X[ad["row"].to_numpy()], blocks


def projectors(model: str, regime: str, ad: pl.DataFrame, use_human: bool = True) -> dict:
    V = np.load(CV / f"dirs_{model}.npz")["V"]
    idx = json.loads((CV / f"dirs_index_{model}.json").read_text())
    goals = sorted(set(ad["goal_no"].to_list()))
    abg = {g: sorted(set(ad.filter(pl.col("goal_no") == g)["agent"].to_list())) for g in goals}
    return CVM.projectors(V, idx, regime, goals, abg, use_human)


class Panel:
    """Index arrays of one regime's eligible agent-days and its block table."""

    def __init__(self, ad: pl.DataFrame, blocks: pl.DataFrame, P: dict, n_mode: str = "active"):
        self.agent = ad["agent"].to_numpy().astype(int)
        self.goal = ad["goal_no"].to_numpy().astype(int)
        self.a = ad["a"].to_numpy().astype(float)
        self.date = ad["pt_date"].to_list()
        self.n_stat = ad["n_stat"].to_numpy().astype(float)
        bl = blocks["block"].to_list()
        bid = {b: k for k, b in enumerate(bl)}
        keep = np.array([b in bid for b in ad["block"].to_list()])
        assert keep.all()
        self.block = np.array([bid[b] for b in ad["block"].to_list()])
        self.nb = len(bl)
        self.block_name = bl
        self.block_goal = blocks["goal_no"].to_numpy().astype(int)
        self.block_a = blocks["a_b"].to_numpy().astype(float)
        self.block_mid = blocks["mid_day"].to_numpy().astype(float)
        self.block_first = blocks["first_day"].to_list()
        self.block_ndays = blocks["n_days"].to_numpy().astype(float)
        self.block_N = (blocks["N_b"] if n_mode == "active" else blocks["n_members"].cast(pl.Float64)).to_numpy()
        self.P = P
        self.Pi = np.stack([P.get((g, a), P[(g, -1)]) for g, a in zip(self.goal, self.agent)])
        # odd/even half of each agent-day: rank of its day among the block's distinct days
        self.half = np.zeros(len(self.agent), int)
        for b in range(self.nb):
            m = self.block == b
            days = np.unique(self.a[m])
            rk = {d: k for k, d in enumerate(days)}
            self.half[m] = np.array([rk[d] % 2 for d in self.a[m]])


def project(pan: Panel, X: np.ndarray) -> np.ndarray:
    return np.einsum("nij,nj->ni", pan.Pi, X)


def residuals(pan: Panel, X: np.ndarray, weights=None, method: str = "fe"):
    """Rows (agent, block): r_{i,b} and the odd/even-day half residuals (NaN when the agent lacks that half)."""
    Xp = project(pan, X)
    w = np.ones(len(Xp)) if weights is None else weights
    mu = CVM.personal_vectors(pan.agent, pan.goal, Xp, w if weights is not None else None, method=method)
    keys = {}
    for k in range(len(Xp)):
        if (pan.agent[k], pan.goal[k]) in mu:
            keys.setdefault((pan.agent[k], pan.block[k]), []).append(k)
    A, B, R, Rh = [], [], [], []
    for (a, b), ks in keys.items():
        ks = np.array(ks)
        g = pan.goal[ks[0]]
        Pi = pan.P.get((g, a), pan.P[(g, -1)])
        m_ = mu[(a, g)]
        vbar = (Xp[ks] * w[ks, None]).sum(0) / w[ks].sum()
        hh = []
        for h in (0, 1):
            kh = ks[pan.half[ks] == h]
            hh.append(Pi @ ((Xp[kh] * w[kh, None]).sum(0) / w[kh].sum() - m_) if len(kh) else np.full(Xp.shape[1], np.nan))
        A.append(a); B.append(b); R.append(Pi @ (vbar - m_)); Rh.append(hh)
    return np.array(A), np.array(B), np.array(R), np.array(Rh)


# ------------------------------------------------------------------------------------------------- culture vectors
def draw_subsets(A, B, nb, rng, D=50, m=M_SUB, full=False):
    """sel[b]: (D, m) row indices of A/B/R (None if the block has < m members). full=True: one 'draw' = all members."""
    sel = []
    for b in range(nb):
        rows = np.flatnonzero(B == b)
        if full:
            sel.append(rows[None, :] if len(rows) >= 3 else None)
        elif len(rows) < m:
            sel.append(None)
        else:
            sel.append(np.stack([rng.choice(rows, m, replace=False) for _ in range(D)]))
    return sel


def culture_vectors(R, Rh, sel, block_goal):
    """U (nb, D, d), U_half (nb, D, 2, d), centered per draw on the goal-equal-weight mean of the block vectors."""
    nb = len(sel)
    Dn = max(s.shape[0] for s in sel if s is not None)
    d = R.shape[1]
    U = np.full((nb, Dn, d), np.nan); Uh = np.full((nb, Dn, 2, d), np.nan)
    for b, s in enumerate(sel):
        if s is None:
            continue
        if s.shape[0] == 1 and Dn > 1:          # full roster: replicate the single vector
            s = np.repeat(s, Dn, axis=0)
        U[b] = R[s].mean(1)
        H = Rh[s]                                # (D, m, 2, d)
        cnt = (~np.isnan(H[..., 0])).sum(1)      # (D, 2)
        mh = np.nanmean(H, axis=1) if H.shape[1] else H[:, 0]
        mh[cnt < 2] = np.nan
        Uh[b] = mh
    ok = ~np.isnan(U[:, 0, 0])
    goals = np.unique(block_goal[ok])
    cen = np.mean([U[ok & (block_goal == g)].mean(0) for g in goals], axis=0)   # (D, d)
    U[ok] -= cen[None]
    Uh[ok] -= cen[None, :, None, :]
    return U, Uh, ok


def _unit(Z):
    n = np.linalg.norm(Z, axis=-1, keepdims=True)
    return Z / np.where(n > 0, n, np.nan)


def pair_similarity(U, ok):
    Un = _unit(U)
    Un = np.where(np.isnan(Un), 0.0, Un)
    S = np.einsum("bdk,cdk->bc", Un, Un) / U.shape[1]
    S[~ok] = np.nan; S[:, ~ok] = np.nan
    return S


def split_half(Uh, ok):
    """rel_b = mean over draws of cos(odd, even); R_b = Spearman-Brown."""
    c = np.nansum(_unit(Uh[:, :, 0]) * _unit(Uh[:, :, 1]), axis=-1)
    valid = ~np.isnan(Uh[:, :, 0, 0]) & ~np.isnan(Uh[:, :, 1, 0])
    rel = np.where(valid.sum(1) > 0, (c * valid).sum(1) / np.maximum(valid.sum(1), 1), np.nan)
    rel[~ok] = np.nan
    Rsb = 2 * rel / (1 + np.clip(rel, -0.95, None))
    return rel, Rsb


def smooth_reliability(Rsb, N, ndays, ok):
    m = ok & ~np.isnan(Rsb) & (ndays >= 2)
    Xd = np.column_stack([np.ones(m.sum()), np.log(N[m]), np.log(ndays[m])])
    beta, *_ = np.linalg.lstsq(Xd, Rsb[m], rcond=None)
    Xa = np.column_stack([np.ones(len(N)), np.log(N), np.log(np.maximum(ndays, 1))])
    return np.clip(Xa @ beta, 0.05, 1.0), beta


def overlap(A, sel, nb):
    """J[b,c] = mean over draws of (shared agents between the two subsets) / m."""
    agents = np.unique(A); ai = {a: k for k, a in enumerate(agents)}
    Dn = max(s.shape[0] for s in sel if s is not None)
    M = np.zeros((nb, Dn, len(agents)))
    m = None
    for b, s in enumerate(sel):
        if s is None:
            continue
        ss = np.repeat(s, Dn, axis=0) if s.shape[0] == 1 and Dn > 1 else s
        m = ss.shape[1]
        for d in range(Dn):
            M[b, d, [ai[x] for x in A[ss[d]]]] = 1
    return np.einsum("bda,cda->bc", M, M) / (Dn * (m or 1))


# ------------------------------------------------------------------------------------------------- pairs and fit
def pairs(pan: Panel, S, ok, Rhat=None, J=None, time="active", restrict=None):
    """Cross-goal pairs: columns b, c, t_b, t_c, N_b, N_c, s, s_dis, J, w (goal-pair weight)."""
    tb = pan.block_a if time == "active" else pan.block_mid
    rows = []
    for b in range(pan.nb):
        for c in range(b + 1, pan.nb):
            if not (ok[b] and ok[c]) or pan.block_goal[b] == pan.block_goal[c]:
                continue
            if restrict is not None and not (restrict[b] and restrict[c]):
                continue
            s = S[b, c]
            sd = s / np.sqrt(Rhat[b] * Rhat[c]) if Rhat is not None else np.nan
            rows.append((b, c, tb[b], tb[c], pan.block_N[b], pan.block_N[c], s, sd,
                         J[b, c] if J is not None else np.nan,
                         min(pan.block_goal[b], pan.block_goal[c]) * 1000 + max(pan.block_goal[b], pan.block_goal[c])))
    T = np.array(rows, dtype=float).reshape(-1, 10)
    if len(T):
        _, inv, cnt = np.unique(T[:, 9], return_inverse=True, return_counts=True)
        T[:, 9] = 1.0 / cnt[inv]
    return T


class RateGrid:
    """N(t) interpolated between block points; cumulative I(t) = int (N/6)^alpha exp(delta_seg) dt on a grid."""

    def __init__(self, t_pts, N_pts, seg_bounds=(), step=0.25):
        o = np.argsort(t_pts)
        self.tp, self.Np = np.asarray(t_pts)[o], np.asarray(N_pts)[o]
        self.grid = np.arange(self.tp.min(), self.tp.max() + step, step)
        self.Ng = np.interp(self.grid, self.tp, self.Np)
        self.seg = np.searchsorted(np.asarray(seg_bounds), self.grid, side="right") if len(seg_bounds) else np.zeros(len(self.grid), int)
        self.lnN = np.log(self.Ng / N_REF)

    def I(self, t, alpha, deltas=None):
        f = np.exp(alpha * self.lnN)
        if deltas is not None:
            f = f * np.exp(np.concatenate([[0.0], deltas])[self.seg])
        cum = np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(self.grid))])
        return np.interp(t, self.grid, cum)

    def mean_rate_factor(self, alpha):
        return float(np.mean(np.exp(alpha * self.lnN)))


def fit_rate(T, grid: RateGrid, col=7, kind="primary", n_seg=1, starts=(-1.0, 0.0, 1.0), x0=None):
    """Weighted NLS. kind: primary (A, ln k6, alpha, s_inf on s_dis); free_amp (+ beta on raw s); overlap (+ beta_J);
    two_rate (NE27: ln k_pre, ln k_post split at grid break: n_seg=2, alpha fixed 0). Returns dict."""
    ok = ~np.isnan(T[:, col])
    if kind == "free_amp":
        ok = ~np.isnan(T[:, 6]); col = 6
    if kind == "overlap":
        ok &= ~np.isnan(T[:, 8])
    T = T[ok]
    if len(T) < 8:
        return {"ok": False}
    y = T[:, col]; sw = np.sqrt(T[:, 9]); tb, tc = T[:, 2], T[:, 3]
    Nbar = np.sqrt(T[:, 4] * T[:, 5])

    def unpack(p):
        d = {"A": p[0], "lnk": p[1], "alpha": p[2], "s_inf": p[3]}
        k = 4
        if kind == "free_amp":
            d["beta"] = p[k]; k += 1
        if kind == "overlap":
            d["beta_J"] = p[k]; k += 1
        d["deltas"] = p[k:k + n_seg - 1] if n_seg > 1 else None
        return d

    def model(p):
        d = unpack(p)
        lam = np.exp(d["lnk"]) * np.abs(grid.I(tc, d["alpha"], d["deltas"]) - grid.I(tb, d["alpha"], d["deltas"]))
        amp = d["A"] * (np.exp(d["beta"] * np.log(Nbar / N_REF)) if kind == "free_amp" else 1.0)
        out = amp * np.exp(-lam) + d["s_inf"]
        if kind == "overlap":
            out = out + d["beta_J"] * T[:, 8]
        return out

    lo = [0.0, np.log(0.002), -4.0, -0.5]; hi = [3.0, np.log(2.0), 4.0, 0.5]
    if kind == "free_amp":
        lo.append(-4.0); hi.append(4.0)
    if kind == "overlap":
        lo.append(-2.0); hi.append(2.0)
    lo += [-4.0] * (n_seg - 1); hi += [4.0] * (n_seg - 1)
    if kind == "two_rate":
        lo[2], hi[2] = -1e-9, 1e-9
    best = None
    for k, a0 in enumerate(starts if x0 is None else [None]):
        if x0 is not None:
            p0 = np.clip(np.asarray(x0, float), np.array(lo) + 1e-9, np.array(hi) - 1e-9)
        else:
            p0 = [0.3, np.log(0.05), a0 if kind != "two_rate" else 0.0, -0.05]
            if kind == "free_amp":
                p0.append(0.0)
            if kind == "overlap":
                p0.append(0.0)
            p0 += [0.0] * (n_seg - 1)
        try:
            r = least_squares(lambda p: sw * (model(p) - y), p0, bounds=(lo, hi), method="trf", max_nfev=400)
        except Exception:  # noqa: BLE001
            continue
        if best is None or r.cost < best.cost:
            best = r
    if best is None:
        return {"ok": False}
    d = unpack(best.x)
    return {"ok": True, "A": float(d["A"]), "k6": float(np.exp(d["lnk"])), "alpha": float(d["alpha"]),
            "s_inf": float(d["s_inf"]), "beta": float(d.get("beta", np.nan)), "beta_J": float(d.get("beta_J", np.nan)),
            "deltas": [float(x) for x in d["deltas"]] if d["deltas"] is not None else [],
            "x": best.x.tolist(), "cost": float(best.cost), "n_pairs": int(len(T))}


def jackknife(T, grid, pan, fit, key="alpha", **kw):
    """Delete-one-goal jackknife of fit[key]; returns se, ci (t, n-1 df), values."""
    gb = pan.block_goal
    goals = np.unique(np.concatenate([gb[T[:, 0].astype(int)], gb[T[:, 1].astype(int)]]))
    vals = []
    for g in goals:
        keep = (gb[T[:, 0].astype(int)] != g) & (gb[T[:, 1].astype(int)] != g)
        f = fit_rate(T[keep], grid, x0=fit["x"], **kw)
        if f["ok"]:
            vals.append(f[key] if key != "lnk_diff" else f["deltas"][0])
    vals = np.array(vals); n = len(vals)
    if n < 3:
        return {"se": np.nan, "lo": np.nan, "hi": np.nan, "n_goals": n}
    se = float(np.sqrt((n - 1) / n * ((vals - vals.mean()) ** 2).sum()))
    est = fit[key] if key != "lnk_diff" else fit["deltas"][0]
    q = float(tdist.ppf(0.975, n - 1))
    return {"se": se, "lo": float(est - q * se), "hi": float(est + q * se), "n_goals": n, "vals": vals.tolist()}


# ------------------------------------------------------------------------------------------------- synthetic
def variance_scales(pan: Panel, X: np.ndarray):
    """H81's sampling facts: covariances of agent, goal and block parts of the projected vectors; residual rows."""
    Xp = project(pan, X)
    agents = np.unique(pan.agent)
    a_mean = {a: Xp[pan.agent == a].mean(0) for a in agents}
    E1 = Xp - np.stack([a_mean[a] for a in pan.agent])
    goals = np.unique(pan.goal)
    g_mean = {g: E1[pan.goal == g].mean(0) for g in goals}
    E2 = E1 - np.stack([g_mean[g] for g in pan.goal])
    b_mean = {b: E2[pan.block == b].mean(0) for b in np.unique(pan.block)}
    E3 = E2 - np.stack([b_mean[b] for b in pan.block])
    return {"Sa": np.cov(np.stack(list(a_mean.values())).T), "Sg": np.cov(np.stack(list(g_mean.values())).T),
            "Sb": np.cov(np.stack(list(b_mean.values())).T), "E": E3}


def _mvn(rng, S, n):
    w, V = np.linalg.eigh((S + S.T) / 2); w = np.clip(w, 0, None)
    return rng.standard_normal((n, len(w))) * np.sqrt(w) @ V.T


def simulate(pan: Panel, sc: dict, rng, grid: RateGrid, share=0.0, k_mean=1 / 17.9, alpha=0.0, drift=0.0,
             depth=0.0, alpha_break=None):
    """S0 (share 0); D (alpha 0); M (alpha -1); H (-0.5): OU slow mode per block with integrated rate
    k(t) = c (N(t)/6)^alpha, c set so the mean rate over the regime equals k_mean. drift: H81's S2 individual drift.
    depth: agent-day noise SD x (N_b/6)^depth (normalized to mean 1). alpha_break: (t_break, k_pre/k_mean, k_post/k_mean)
    for a step in the rate (NE27 checks)."""
    agents = np.unique(pan.agent); goals = np.unique(pan.goal)
    a = dict(zip(agents, _mvn(rng, sc["Sa"], len(agents))))
    g = dict(zip(goals, _mvn(rng, sc["Sg"], len(goals)) * np.sqrt(1 - share)))
    bf = _mvn(rng, sc["Sb"], pan.nb)
    X = np.stack([a[x] for x in pan.agent]) + np.stack([g[x] for x in pan.goal]) + bf[pan.block]
    if share > 0:
        c = k_mean / grid.mean_rate_factor(alpha)
        Ib = grid.I(pan.block_a, alpha)
        order = np.argsort(pan.block_a)
        z = _mvn(rng, sc["Sg"], pan.nb) * np.sqrt(share)
        u = np.zeros_like(z); prev = None
        for k in order:
            if prev is None:
                u[k] = z[k]
            else:
                rho = np.exp(-c * (Ib[k] - Ib[prev]))
                u[k] = rho * u[prev] + np.sqrt(1 - rho ** 2) * z[k]
            prev = k
        X = X + u[pan.block]
    if drift > 0:
        dirs = dict(zip(agents, _mvn(rng, sc["Sg"], len(agents)) * np.sqrt(drift * 3)))
        for ag in agents:
            m = pan.agent == ag
            t = pan.a[m]; s = (t - t.min()) / max(t.max() - t.min(), 1) * 2 - 1
            X[m] += s[:, None] * dirs[ag]
    E = sc["E"][rng.permutation(len(sc["E"]))]
    if depth:
        f = (pan.block_N[pan.block] / N_REF) ** depth
        E = E * (f / f.mean())[:, None]
    return X + E


# ------------------------------------------------------------------------------------------------- one pipeline pass
def pipeline(pan: Panel, X, rng, D=50, variants=("V1",), grid=None, weights=None, seg_bounds=None, jack=True,
             restrict_ne27=None, placebo_breaks=()):
    """Run the estimators on one data set. Returns dict of results by variant."""
    A, B, R, Rh = residuals(pan, X, weights)
    out = {}
    sel = draw_subsets(A, B, pan.nb, rng, D)
    U, Uh, ok = culture_vectors(R, Rh, sel, pan.block_goal)
    S = pair_similarity(U, ok)
    rel, Rsb = split_half(Uh, ok)
    Rhat, beta_rel = smooth_reliability(Rsb, pan.block_N, pan.block_ndays, ok)
    grid = grid or RateGrid(pan.block_a, pan.block_N)
    J = overlap(A, sel, pan.nb) if "V4" in variants else None
    T = pairs(pan, S, ok, Rhat, J)
    out["reliability"] = {"beta_lnN": float(beta_rel[1]), "beta_lndays": float(beta_rel[2]), "intercept": float(beta_rel[0]),
                          "mean_rel": float(np.nanmean(rel[ok])), "n_blocks": int(ok.sum())}
    if "V1" in variants:
        f = fit_rate(T, grid)
        if f["ok"] and jack:
            f["jk"] = jackknife(T, grid, pan, f)
        out["V1"] = f
        out["_T"] = T
    if "V2" in variants:
        out["V2"] = fit_rate(T, grid, kind="free_amp")
    if "V4" in variants:
        out["V4"] = fit_rate(T, grid, kind="overlap")
    if "V3" in variants:
        self_ = draw_subsets(A, B, pan.nb, rng, full=True)
        U3, Uh3, ok3 = culture_vectors(R, Rh, self_, pan.block_goal)
        S3 = pair_similarity(U3, ok3)
        _, Rsb3 = split_half(Uh3, ok3)
        Rhat3, _ = smooth_reliability(Rsb3, pan.block_N, pan.block_ndays, ok3)
        out["V3"] = fit_rate(pairs(pan, S3, ok3, Rhat3), grid)
    if "V5" in variants and seg_bounds is not None:
        g5 = RateGrid(pan.block_a, pan.block_N, seg_bounds)
        out["V5"] = fit_rate(T, g5, n_seg=len(seg_bounds) + 1)
    if restrict_ne27 is not None:
        out["NE27"] = ne27_fit(pan, S, ok, Rhat, restrict_ne27, jack=jack)
        out["NE27_placebo"] = {}
        for nm, (t_break, restr) in placebo_breaks:
            out["NE27_placebo"][nm] = ne27_fit(pan, S, ok, Rhat, (t_break, restr), jack=False)
    return out


def ne27_fit(pan, S, ok, Rhat, spec, jack=True):
    """Two-rate fit (alpha 0) with a rate step at t_break: delta = ln(k_post / k_pre)."""
    t_break, restr = spec
    T = pairs(pan, S, ok, Rhat, restrict=restr)
    g = RateGrid(pan.block_a[restr & ok], pan.block_N[restr & ok], seg_bounds=(t_break,))
    f = fit_rate(T, g, kind="two_rate", n_seg=2)
    if f["ok"]:
        f["dlnk"] = f["deltas"][0]
        if jack:
            f["jk"] = jackknife(T, g, pan, f, key="lnk_diff", kind="two_rate", n_seg=2)
        Nb = pan.block_N
        pre = restr & ok & (pan.block_a < t_break); post = restr & ok & (pan.block_a >= t_break)
        f["N_pre"] = float(Nb[pre].mean()); f["N_post"] = float(Nb[post].mean())
        f["magnet_pred"] = float(-np.log(f["N_post"] / f["N_pre"]))
    return f
