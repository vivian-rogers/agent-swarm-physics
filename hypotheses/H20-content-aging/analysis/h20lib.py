"""H20 core: agent-day states, two-time correlations, aging slope, model fits, swarm generative model.

Card: hypotheses/H20-content-aging/README.md (Observables O1-O7, Null / baseline).
Conventions: day index k = d - 1 (0-based); t_w = d = k + 1; tau = d' - d (active days unless a clock is given).
"""
from __future__ import annotations

import sys
import dataclasses
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h20common as hc  # noqa: E402,F401  (sets thread limits)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402

EPS = 1e-12


# ----------------------------------------------------------------------------------------------
# Period data
# ----------------------------------------------------------------------------------------------
@dataclass
class Period:
    g: int
    regime: str
    T: int                       # number of active days covered (max d with data)
    agents: np.ndarray           # agent codes (A,)
    wk_gap: np.ndarray           # (T,) bool: gap > 36 h before day k
    d_cal: np.ndarray            # (T,) calendar-day number of day k
    pt_dates: list
    a_idx: np.ndarray            # statement -> agent index
    k_idx: np.ndarray            # statement -> day index
    kind: np.ndarray             # statement kind ('chat' / 'intent')
    Z: np.ndarray                # statements x 64, whitened (float32)
    goal_dirs: dict = field(default_factory=dict)   # n -> (village ĝ (n,), {agent_idx: (m, n) agent-goal dirs})
    held: np.ndarray | None = None  # (T,) bool: day is holdout (confirmation only)


def load_period(g: int, statements: pl.DataFrame | None = None, Z64: np.ndarray | None = None,
                days: pl.DataFrame | None = None, allow_holdout: bool = False) -> Period:
    """Load one goal period from data/processed/H20-content-aging (non-holdout data only)."""
    if statements is None:
        statements = pl.read_parquet(hc.OUT / "statements.parquet").with_row_index("row")
    if Z64 is None:
        Z64 = np.load(hc.OUT / "stmt_w64.npy", mmap_mode="r")
    if days is None:
        days = pl.read_parquet(hc.OUT / "days.parquet")
    st = statements.filter(pl.col("goal_no") == g)
    if "row" not in st.columns:
        raise ValueError("statements need a row index")
    if not allow_holdout:
        hc.assert_not_holdout(st["goal_no"].to_list(), st["pt_date"].to_list())
    dd = days.filter(pl.col("goal_no") == g).sort("d")
    T = int(st["d"].max())
    dd = dd.filter(pl.col("d") <= T)
    agents = np.array(sorted(st["agent"].unique().to_list()))
    amap = {a: i for i, a in enumerate(agents)}
    a_idx = np.array([amap[a] for a in st["agent"].to_list()], dtype=np.int32)
    k_idx = (st["d"].to_numpy() - 1).astype(np.int32)
    Z = np.asarray(Z64[st["row"].to_numpy()], dtype=np.float32)
    P = Period(g=g, regime=st["regime"][0], T=T, agents=agents, wk_gap=dd["weekend_gap"].to_numpy().astype(bool),
               d_cal=dd["d_cal"].to_numpy().astype(float), pt_dates=dd["pt_date"].to_list(), a_idx=a_idx, k_idx=k_idx,
               kind=st["kind"].to_numpy(), Z=Z, held=dd["holdout"].to_numpy().astype(bool))
    P.goal_dirs = load_goal_dirs(g, P.regime, agents)
    return P


def load_goal_dirs(g: int, regime: str, agents: np.ndarray, dims=(16, 32, 64)) -> dict:
    """ĝ = unit(unit(W goal) + unit(mean_rooms unit(W kickoff))) per dim; agent goals (#51) per agent."""
    meta = pl.read_parquet(hc.OUT / "goal_dirs.parquet")
    raw = np.load(hc.OUT / "goal_raw.npy")
    out = {}
    m = meta.filter(pl.col("goal_no") == g)
    for n in dims:
        W = hc.common.load_whitener(regime, n)
        gv = m.filter(pl.col("kind") == "goal")["row"].to_list()
        kv = m.filter(pl.col("kind") == "kickoff")["row"].to_list()
        parts = []
        if gv:
            parts.append(_unit(W(raw[gv]).mean(0)))
        if kv:
            parts.append(_unit(np.mean([_unit(x) for x in W(raw[kv])], axis=0)))
        ghat = _unit(np.sum(parts, axis=0)) if parts else None
        ag = {}
        for i, a in enumerate(agents):
            rows = m.filter((pl.col("kind") == "agent_goal") & (pl.col("agent") == int(a)))["row"].to_list()
            if rows:
                ag[i] = np.array([_unit(x) for x in W(raw[rows])])
        out[n] = (ghat, ag)
    return out


def _unit(x):
    x = np.asarray(x, dtype=np.float64)
    return x / max(np.linalg.norm(x), EPS)


# ----------------------------------------------------------------------------------------------
# Agent-day states (O1) and variants (O4)
# ----------------------------------------------------------------------------------------------
def agent_day_stats(Z, a_idx, k_idx, A, T, n_min=hc.MIN_STMTS):
    """Sufficient statistics per agent-day: xbar (A,T,n), v (A,T), n (A,T), valid (A,T)."""
    key = a_idx.astype(np.int64) * T + k_idx
    order = np.argsort(key, kind="stable")
    ks = key[order]
    starts = np.r_[0, np.flatnonzero(np.diff(ks)) + 1]
    sums = np.add.reduceat(Z[order], starts, axis=0)
    R = np.add.reduceat((Z[order] ** 2).sum(1), starts)
    cnt = np.diff(np.r_[starts, ks.size])
    nd = Z.shape[1]
    X = np.zeros((A * T, nd)); Rr = np.zeros(A * T); n = np.zeros(A * T)
    X[ks[starts]] = sums; Rr[ks[starts]] = R; n[ks[starts]] = cnt
    X = X.reshape(A, T, nd); Rr = Rr.reshape(A, T); n = n.reshape(A, T)
    valid = n >= n_min
    with np.errstate(invalid="ignore", divide="ignore"):
        xbar = np.where(n[..., None] > 0, X / np.maximum(n, 1)[..., None], 0.0)
        v = np.where(n > 1, (Rr - n * (xbar ** 2).sum(-1)) / (n * np.maximum(n - 1, 1)), np.nan)
    xbar[~valid] = 0.0
    v = np.where(valid, v, 0.0)
    return xbar, v, n, valid


def transform(P: Period, variant: str = "raw", n: int = 32, rng=None):
    """Statement transform -> (Zt, a_idx, k_idx). variants: raw, g (field removed), chat."""
    Zn = P.Z[:, :n]
    Zn = Zn / np.maximum(np.linalg.norm(Zn, axis=1, keepdims=True), EPS)
    a_idx, k_idx = P.a_idx, P.k_idx
    if variant == "g":
        ghat, ag = P.goal_dirs[n]
        Zp = Zn.copy()
        for i in range(len(P.agents)):
            vecs = [ghat] if ghat is not None else []
            if i in ag:
                vecs += list(ag[i])
            if not vecs:
                continue
            Q, _ = np.linalg.qr(np.array(vecs).T)   # n x m orthonormal basis of the goal subspace
            s = a_idx == i
            Zp[s] = Zn[s] - (Zn[s] @ Q) @ Q.T
        Zn = Zp
    elif variant == "chat":
        s = P.kind == "chat"
        Zn, a_idx, k_idx = Zn[s], a_idx[s], k_idx[s]
    elif variant != "raw":
        raise ValueError(variant)
    return Zn, a_idx, k_idx


def states(P: Period, variant="raw", n=32, n_min=hc.MIN_STMTS):
    Zn, a_idx, k_idx = transform(P, variant, n)
    return agent_day_stats(Zn, a_idx, k_idx, len(P.agents), P.T, n_min)


def rarefied_states(P: Period, n=32, m=8, rng=None):
    """Rarefy to m statements per agent-day (agent-days with >= m statements)."""
    rng = rng or np.random.default_rng(hc.SEED)
    Zn, a_idx, k_idx = transform(P, "raw", n)
    key = a_idx.astype(np.int64) * P.T + k_idx
    perm = rng.permutation(key.size)
    order = perm[np.argsort(key[perm], kind="stable")]
    ks = key[order]
    starts = np.r_[0, np.flatnonzero(np.diff(ks)) + 1]
    rank = np.arange(ks.size) - np.repeat(starts, np.diff(np.r_[starts, ks.size]))
    keep = order[rank < m]
    return agent_day_stats(Zn[keep], a_idx[keep], k_idx[keep], len(P.agents), P.T, n_min=m)


def common_removed(xbar, v, valid):
    """V-c: x_i - mean of the other valid agents that day (needs >= 2 others)."""
    N = valid.sum(0).astype(float)
    tot = (xbar * valid[..., None]).sum(0)
    vt = (v * valid).sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        others = (tot[None] - xbar) / np.maximum(N - 1, 1)[None, :, None]
        xt = xbar - others
        vti = v + (vt[None] - v) / np.maximum(N - 1, 1)[None] ** 2
    ok = valid & (N >= 3)[None]
    xt[~ok] = 0.0
    return xt, np.where(ok, vti, 0.0), ok


def swarm_mean(xbar, v, valid, subset=None):
    """O3: the swarm mean as a single unit (1, T, n). subset: boolean mask over agents (roster-stable variant)."""
    if subset is not None:
        valid = valid & subset[:, None]
    N = valid.sum(0).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        m = (xbar * valid[..., None]).sum(0) / np.maximum(N, 1)[:, None]
        vm = (v * valid).sum(0) / np.maximum(N, 1) ** 2
    ok = N >= 2
    m[~ok] = 0.0
    return m[None], np.where(ok, vm, 0.0)[None], ok[None]


# ----------------------------------------------------------------------------------------------
# Two-time correlation (O2) and entries
# ----------------------------------------------------------------------------------------------
def two_time(xbar, v, valid):
    """Agent-averaged C(d, d') (ratio of sums) and the number of agents per entry."""
    S = (xbar ** 2).sum(-1) - v
    Q = np.einsum("adk,aek->ade", xbar, xbar)
    M = (valid[:, :, None] & valid[:, None, :]).astype(float)
    num = (Q * M).sum(0)
    Sd = np.where(valid, S, 0.0)
    den1 = (Sd[:, :, None] * M).sum(0)
    den2 = (Sd[:, None, :] * M).sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        C = np.where((den1 > 0) & (den2 > 0), num / np.sqrt(np.abs(den1 * den2)), np.nan)
    return C, M.sum(0)


def per_agent_C(xbar, v, valid):
    S = (xbar ** 2).sum(-1) - v
    Q = np.einsum("adk,aek->ade", xbar, xbar)
    ok = valid & (S > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        Ci = Q / np.sqrt(np.abs(S[:, :, None] * S[:, None, :]))
    Ci[~(ok[:, :, None] & ok[:, None, :])] = np.nan
    return Ci


def cross_agent_C(xbar, v, valid):
    """Cross-agent two-time function (i != j), normalized by agent mean signal a_i a_j (for null fitting)."""
    S = (xbar ** 2).sum(-1) - v
    a2 = np.array([np.nanmean(np.where(valid[i], S[i], np.nan)) if valid[i].any() else np.nan for i in range(len(S))])
    a = np.sqrt(np.clip(np.nan_to_num(a2, nan=0.0), 0, None))
    xs = xbar * valid[..., None]
    tot = xs.sum(0)                                   # (T, n)
    full = tot @ tot.T                                # sum over all i, j
    selfp = np.einsum("adk,aek->de", xs, xs)          # i == j terms
    num = full - selfp
    w = valid * a[:, None]
    wt = w.sum(0)
    den = np.outer(wt, wt) - np.einsum("ad,ae->de", w, w)
    cnt = np.outer(valid.sum(0), valid.sum(0)) - np.einsum("ad,ae->de", valid.astype(float), valid.astype(float))
    with np.errstate(invalid="ignore", divide="ignore"):
        Cx = np.where(den > 0, num / den, np.nan)
    return Cx, cnt


def entries(C, npair, wk_gap, clock=None, tw_min=2, tau_max=None, tw_max=None, include_same=False):
    """Upper-triangle entries as arrays: tw, tau, c, w, nwk, d1, d2 (0-based day indices).
    clock: (T,) times for each day (default: active-day index d = k + 1)."""
    T = C.shape[0]
    d1, d2 = np.triu_indices(T, 0 if include_same else 1)
    t = np.arange(1, T + 1, dtype=float) if clock is None else np.asarray(clock, float)
    tw, tau = t[d1], t[d2] - t[d1]
    cw = np.cumsum(wk_gap.astype(int))
    nwk = cw[d2] - cw[d1]
    c = C[d1, d2]; w = npair[d1, d2]
    sel = np.isfinite(c) & (w > 0) & (d1 + 1 >= tw_min)
    if tau_max is not None:
        sel &= (d2 - d1) <= tau_max
    if tw_max is not None:
        sel &= (d1 + 1) <= tw_max
    return dict(tw=tw[sel], tau=tau[sel], c=c[sel], w=w[sel], nwk=nwk[sel].astype(float), d1=d1[sel], d2=d2[sel],
                lag=(d2 - d1)[sel])


def tau_max_for(T):
    return max(1, (T - 1) // 2)


# ----------------------------------------------------------------------------------------------
# Aging slope (O5)
# ----------------------------------------------------------------------------------------------
def aging_slope(E, use_wk=True, lag_key="lag"):
    """WLS of c on lag fixed effects + log tw (+ nwk). Returns (A, beta_wk, n_entries)."""
    lag = E[lag_key]
    if lag.size < 2:
        return np.nan, np.nan, int(lag.size)
    ok = np.zeros(lag.size, bool)
    for L in np.unique(lag):
        s = lag == L
        if np.unique(E["tw"][s]).size >= 2:
            ok |= s
    if ok.sum() < 2:
        return np.nan, np.nan, int(ok.sum())
    lag_u = np.unique(lag[ok])
    X = [(lag[ok] == L).astype(float) for L in lag_u]
    X.append(np.log(E["tw"][ok]))
    has_wk = False
    if use_wk:
        X2 = np.column_stack(X + [E["nwk"][ok]])
        if np.linalg.matrix_rank(X2) == X2.shape[1]:
            X = X + [E["nwk"][ok]]
            has_wk = True
    X = np.column_stack(X)
    sw = np.sqrt(E["w"][ok])
    beta, *_ = np.linalg.lstsq(X * sw[:, None], E["c"][ok] * sw, rcond=None)
    A = beta[len(lag_u)]
    bwk = beta[-1] if has_wk else np.nan
    return float(A), float(bwk), int(ok.sum())


def slope_set(C, npair, P_wk, T, clock=None):
    """All O5 statistics from one C matrix: A, beta_wk, A_early, A_late, K."""
    tm = tau_max_for(T)
    E = entries(C, npair, P_wk, tw_min=2, tau_max=tm)
    A, bwk, ne = aging_slope(E)
    Ee = entries(C, npair, P_wk, tw_min=2, tau_max=2, tw_max=4)
    Ae, _, _ = aging_slope(Ee)
    if E["tw"].size:
        med = np.median(E["tw"])
        El = {k: v[E["tw"] >= med] for k, v in E.items()}
        Al, _, _ = aging_slope(El)
    else:
        Al = np.nan
    K = kickoff_transient(C)
    return dict(A=A, bwk=bwk, n_entries=ne, A_early=Ae, A_late=Al, K=K)


def kickoff_transient(C, taus=(1, 2, 3)):
    vals = []
    for t in taus:
        if 1 + t < C.shape[0]:
            a, b = C[1, 1 + t], C[0, t]
            if np.isfinite(a) and np.isfinite(b):
                vals.append(a - b)
    return float(np.mean(vals)) if vals else np.nan


# ----------------------------------------------------------------------------------------------
# Models (O6)
# ----------------------------------------------------------------------------------------------
def boxcox(t, mu):
    t = np.asarray(t, float)
    if abs(1.0 - mu) < 1e-6:
        return np.log(t)
    return (t ** (1.0 - mu) - 1.0) / (1.0 - mu)


def pred_M0(p, tw, tau):
    q, a, lt = p
    return q + a * np.exp(-tau / np.exp(lt))


def pred_M0b(p, tw, tau):
    q, a1, lt1, a2, lt2 = p
    return q + a1 * np.exp(-tau / np.exp(lt1)) + a2 * np.exp(-tau / np.exp(lt2))


def pred_M1(p, tw, tau):
    q, a, lt, mu = p
    return q + a * np.exp(-(boxcox(tw + tau, mu) - boxcox(tw, mu)) / np.exp(lt))


def pred_MQ(p, tw, tau):
    q, a, lt, lb2, ltq, kap = p
    b2, tq = np.exp(lb2), np.exp(ltq)
    t1, t2 = tw, tw + tau
    num = q + a * np.exp(-tau / np.exp(lt)) + kap * b2 * np.exp(-(t1 + t2 - 2) / tq)
    den = np.sqrt((1 + b2 * np.exp(-2 * (t1 - 1) / tq)) * (1 + b2 * np.exp(-2 * (t2 - 1) / tq)))
    return num / den


LT_LO, LT_HI = np.log(0.05), np.log(2000.0)
MODELS = {
    "M0": (pred_M0, [(-1, 1.5), (-1, 2), (LT_LO, LT_HI)],
           [[0.3, 0.3, np.log(2)], [0.1, 0.5, np.log(10)], [0.5, 0.2, np.log(0.5)]]),
    "M0b": (pred_M0b, [(-1, 1.5), (-1, 2), (LT_LO, np.log(3.0)), (-1, 2), (np.log(1.0), LT_HI)],
            [[0.2, 0.2, np.log(0.5), 0.2, np.log(10)], [0.3, 0.3, np.log(1), 0.1, np.log(30)]]),
    "M1": (pred_M1, [(-1, 1.5), (-1, 2), (LT_LO, LT_HI), (-3, 3)],
           [[0.3, 0.3, np.log(2), 0.0], [0.3, 0.3, np.log(1), 0.5], [0.2, 0.4, np.log(0.5), 1.0],
            [0.1, 0.5, np.log(10), 0.5], [0.3, 0.3, np.log(3), -0.5]]),
    "MQ": (pred_MQ, [(-1, 1.5), (-1, 2), (LT_LO, LT_HI), (np.log(1e-3), np.log(50)), (np.log(0.2), np.log(100)), (0, 1)],
           [[0.3, 0.3, np.log(2), np.log(0.3), np.log(2), 0.0], [0.3, 0.3, np.log(2), np.log(0.3), np.log(2), 1.0],
            [0.3, 0.3, np.log(3), np.log(1.0), np.log(5), 0.5]]),
}


def fit_model(name, E, x0=None, quick=False):
    f, bounds, starts = MODELS[name]
    if quick and x0 is not None:
        starts = starts[:1]
    lo = np.array([b[0] for b in bounds]); hi = np.array([b[1] for b in bounds])
    sw = np.sqrt(E["w"])
    tw, tau, c = E["tw"], E["tau"], E["c"]

    def res(p):
        return (f(p, tw, tau) - c) * sw

    best = None
    cand = ([x0] if x0 is not None else []) + starts
    for s in cand:
        s = np.clip(np.asarray(s, float), lo + 1e-9, hi - 1e-9)
        try:
            r = least_squares(res, s, bounds=(lo, hi), method="trf", max_nfev=400)
        except Exception:
            continue
        if best is None or r.cost < best.cost:
            best = r
    return best.x, float(2 * best.cost)


def predict(name, p, E):
    return MODELS[name][0](p, E["tw"], E["tau"])


def model_toeplitz_fit(E):
    """MT: free stationary model, one mean per lag (weighted)."""
    out = {}
    for L in np.unique(E["lag"]):
        s = E["lag"] == L
        out[L] = np.average(E["c"][s], weights=E["w"][s])
    return out


def lodo_cv(E, models=("M0", "M0b", "MQ", "M1", "MT"), full_fits=None, quick=True):
    """Leave-one-day-out CV: drop every entry involving day k, fit on the rest, predict them. Weighted SSE."""
    days = np.unique(np.r_[E["d1"], E["d2"]])
    sse = {m: 0.0 for m in models}
    wsum = 0.0
    full_fits = dict(full_fits or {})
    for m in models:
        if m != "MT" and m not in full_fits:
            full_fits[m] = fit_model(m, E)[0]
    for k in days:
        te = (E["d1"] == k) | (E["d2"] == k)
        tr = ~te
        if tr.sum() < 8 or te.sum() == 0:
            continue
        Etr = {kk: vv[tr] for kk, vv in E.items()}
        Ete = {kk: vv[te] for kk, vv in E.items()}
        wsum += Ete["w"].sum()
        for m in models:
            if m == "MT":
                tab = model_toeplitz_fit(Etr)
                glob = np.average(Etr["c"], weights=Etr["w"])
                pr = np.array([tab.get(L, glob) for L in Ete["lag"]])
            else:
                p, _ = fit_model(m, Etr, x0=full_fits.get(m), quick=quick)
                pr = predict(m, p, Ete)
            sse[m] += float((Ete["w"] * (pr - Ete["c"]) ** 2).sum())
    return {m: sse[m] / max(wsum, EPS) for m in models}


# ----------------------------------------------------------------------------------------------
# Swarm generative model (null and alternatives)
# ----------------------------------------------------------------------------------------------
@dataclass
class SwarmModel:
    """Latent day state of agent i on day k, in units of the agent's signal scale a_i:
    mu_ik / a_i = sqrt(q) [sqrt(gs) G + sqrt(1-gs) h_i] + sum_c sqrt(r_c) [sqrt(rs) U_c(k) + sqrt(1-rs) u_ic(k)]
                  + sqrt(e) [sqrt(es) H(k) + sqrt(1-es) eta_ik] + transient
    with OU components U_c, u_ic in effective time s(t) (Box-Cox clock with exponent mu; mu = 0 stationary),
    each of correlation exp(-|s(t) - s(t')| / tau_c). e = 1 - q - sum r_c.
    Optional: trap (renewal) private dynamics; deterministic drift along a direction (field drift);
    a kickoff transient of variance b2 decaying with tau_q (correlated across days with weight kap)."""
    q: float = 0.4
    r: tuple = (0.35,)
    tau: tuple = (3.0,)
    gs: float = 0.5
    rs: float = 0.4
    es: float = 0.2
    mu: float = 0.0
    trap_x: float | None = None      # Pareto exponent for a trap-model private component (replaces OU u_i)
    trap_tmin: float = 0.5
    b2: float = 0.0
    tau_q: float = 1.0
    kap: float = 0.0
    drift: float = 0.0               # amplitude^2 of a shared deterministic drift along ĝ: g(t) = (1 - exp(-t/tau_g))
    tau_g: float = 5.0
    Rs: object = None                # Amendment 2: square-root shape (n x n) of the shared latent components (None = isotropic)
    Rp: object = None                # ... of the private latent components

    @property
    def e(self):
        return max(0.0, 1.0 - self.q - sum(self.r))


def _draw(rng, shape, n, R=None):
    """Random vectors with E|x|^2 = 1: isotropic N(0, I/n), or N(0, R R^T / n) for a shape factor R."""
    g = rng.standard_normal(shape + (n,)) / np.sqrt(n)
    return g if R is None else g @ R.T


def _ou_path(times, tau, n, rng, shape_prefix=(), R=None):
    """Vector OU with unit total variance (E|x|^2 = 1) sampled at increasing times."""
    T = len(times)
    out = np.empty(shape_prefix + (T, n))
    x = _draw(rng, shape_prefix, n, R)
    out[..., 0, :] = x
    for k in range(1, T):
        rho = np.exp(-(times[k] - times[k - 1]) / tau)
        x = rho * x + np.sqrt(max(1 - rho * rho, 0.0)) * _draw(rng, shape_prefix, n, R)
        out[..., k, :] = x
    return out


def _trap_path(A, T, n, x, tmin, rng):
    """Bouchaud trap model per agent: renewal with Pareto(x) dwell times from t = 0 (kickoff);
    day k covers (k, k + 1]; the day state is the time-weighted mean of the trap directions."""
    out = np.zeros((A, T, n))
    for i in range(A):
        t = 0.0
        cur = rng.standard_normal(n) / np.sqrt(n)
        events = []
        while t < T + 1:
            dwell = tmin * (rng.pareto(x) + 1.0)
            events.append((t, t + dwell, cur))
            t += dwell
            cur = rng.standard_normal(n) / np.sqrt(n)
        for (a, b, vec) in events:
            k0, k1 = int(np.floor(a)), int(np.ceil(b))
            for k in range(max(k0, 0), min(k1, T)):
                ov = min(b, k + 1) - max(a, k)
                if ov > 0:
                    out[i, k] += ov * vec
        # renormalize to unit expected variance: mean of m iid unit vectors has variance sum(w^2); rescale per day
    return out


def simulate_states(model: SwarmModel, design, rng, n=32, ghat=None, clock=None):
    """Generate (xbar, v, valid) for a design: dict with valid (A,T) bool, v_true (A,T), df (A,T), a (A,) signal scale.
    clock: (T,) times (default active-day d = 1..T). Returns arrays shaped like the real ones."""
    valid = design["valid"]
    A, T = valid.shape
    t = np.arange(1, T + 1, dtype=float) if clock is None else np.asarray(clock, float)
    s = boxcox(t, model.mu)
    lat = np.zeros((A, T, n))
    # static
    Rs, Rp = model.Rs, model.Rp
    G = _draw(rng, (), n, Rs)
    h = _draw(rng, (A,), n, Rp)
    lat += np.sqrt(model.q) * (np.sqrt(model.gs) * G[None, None] + np.sqrt(1 - model.gs) * h[:, None])
    # relaxing components
    for rc, tc in zip(model.r, model.tau):
        U = _ou_path(s, tc, n, rng, R=Rs)
        if model.trap_x is not None:
            u = _trap_path(A, T, n, model.trap_x, model.trap_tmin, rng)
            if Rp is not None:
                u = u @ Rp.T
            u /= np.sqrt(np.maximum((u ** 2).sum(-1, keepdims=True).mean(), EPS))
        else:
            u = _ou_path(s, tc, n, rng, (A,), R=Rp)
        lat += np.sqrt(rc) * (np.sqrt(model.rs) * U[None] + np.sqrt(1 - model.rs) * u)
    # daily white
    H = _draw(rng, (T,), n, Rs)
    eta = _draw(rng, (A, T), n, Rp)
    lat += np.sqrt(model.e) * (np.sqrt(model.es) * H[None] + np.sqrt(1 - model.es) * eta)
    # kickoff transient (shared direction for the correlated part)
    if model.b2 > 0:
        amp = np.sqrt(model.b2) * np.exp(-(t - 1) / model.tau_q)
        Kd = rng.standard_normal((A, n)) / np.sqrt(n)
        Kn = rng.standard_normal((A, T, n)) / np.sqrt(n)
        lat += amp[None, :, None] * (np.sqrt(model.kap) * Kd[:, None] + np.sqrt(1 - model.kap) * Kn)
    # deterministic drift along ĝ (shared)
    if model.drift > 0:
        g = ghat if ghat is not None else _unit(rng.standard_normal(n))
        lat += np.sqrt(model.drift) * (1 - np.exp(-t / model.tau_g))[None, :, None] * g[None, None]
    a = design["a"][:, None, None]
    vt = design["v_true"]
    noise = rng.standard_normal((A, T, n)) * np.sqrt(np.maximum(vt, 0) / n)[..., None]
    xbar = a * lat + noise
    df = np.maximum(design["df"], 1)
    vhat = vt * rng.chisquare(df) / df
    xbar[~valid] = 0.0
    return xbar, np.where(valid, vhat, 0.0), valid


def design_from_states(xbar, v, valid, n_counts, ndim):
    """Sampling design of a real (or variant) dataset: valid mask, noise variances, dof, agent signal scale."""
    S = (xbar ** 2).sum(-1) - v
    a2 = np.array([np.mean(S[i][valid[i]]) if valid[i].any() else 0.0 for i in range(len(S))])
    a = np.sqrt(np.clip(a2, 1e-4, None))
    df = np.where(valid, (np.maximum(n_counts, 2) - 1) * ndim, 1)
    return dict(valid=valid.copy(), v_true=v.copy(), df=df, a=a)


def fit_null_model(C, npair, Cx, cntx, wk_gap, T, two_scale=False):
    """Fit the stationary swarm model: per-agent C (t_w >= 2) -> q, r, tau; cross-agent C -> shares."""
    E = entries(C, npair, wk_gap, tw_min=2)
    if two_scale:
        p, _ = fit_model("M0b", E)
        q, a1, lt1, a2, lt2 = p
        r = (max(a1, 0.0), max(a2, 0.0)); tau = (np.exp(lt1), np.exp(lt2))
    else:
        p, _ = fit_model("M0", E)
        q, a, lt = p
        r = (max(a, 0.0),); tau = (np.exp(lt),)
    q = float(np.clip(q, 0.0, 0.98))
    rsum = sum(r)
    if q + rsum > 0.99:
        sc = (0.99 - q) / max(rsum, EPS)
        r = tuple(x * sc for x in r)
    e = max(0.0, 1 - q - sum(r))
    # shares from cross-agent function: Cx(d,e) = q gs + sum r_c rs rho_c + e es 1[same day]
    Ex = entries(Cx, cntx, wk_gap, tw_min=2, include_same=True)
    gs = rs = es = 0.0
    if Ex["c"].size > 3:
        rho = sum(rc * np.exp(-Ex["tau"] / tc) for rc, tc in zip(r, tau)) / max(sum(r), EPS)
        same = (Ex["tau"] == 0).astype(float)
        Xd = np.column_stack([np.full(Ex["c"].size, q), sum(r) * rho, e * same])
        sw = np.sqrt(Ex["w"])
        from scipy.optimize import lsq_linear
        sol = lsq_linear(Xd * sw[:, None], Ex["c"] * sw, bounds=(0, 1))
        gs, rs, es = [float(x) for x in sol.x]
    return SwarmModel(q=q, r=tuple(float(x) for x in r), tau=tuple(float(x) for x in tau), gs=gs, rs=rs, es=es)


# ----------------------------------------------------------------------------------------------
# Meta-analysis
# ----------------------------------------------------------------------------------------------
def dersimonian_laird(y, se):
    y = np.asarray(y, float); se = np.asarray(se, float)
    ok = np.isfinite(y) & np.isfinite(se) & (se > 0)
    y, se = y[ok], se[ok]
    k = y.size
    if k == 0:
        return dict(mean=np.nan, se=np.nan, tau2=np.nan, I2=np.nan, k=0, p=np.nan)
    w = 1 / se ** 2
    ybar = (w * y).sum() / w.sum()
    Qs = (w * (y - ybar) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Qs - (k - 1)) / c) if k > 1 and c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mean = (ws * y).sum() / ws.sum()
    sem = np.sqrt(1 / ws.sum())
    I2 = max(0.0, (Qs - (k - 1)) / Qs) if Qs > 0 and k > 1 else 0.0
    from scipy.stats import norm
    return dict(mean=float(mean), se=float(sem), tau2=float(tau2), I2=float(I2), k=int(k),
                p=float(2 * norm.sf(abs(mean / sem))))


# ----------------------------------------------------------------------------------------------
# Bundled statistics and the parametric-bootstrap test
# ----------------------------------------------------------------------------------------------
def stats_bundle(xbar, v, valid, wk_gap, T, stable=None, with_derived=True):
    """O5 statistics for one dataset: agent-averaged (A, bwk, A_early, A_late, K), common-removed (A_c),
    swarm mean (A_m), roster-stable swarm mean (A_ms)."""
    C, npair = two_time(xbar, v, valid)
    out = slope_set(C, npair, wk_gap, T)
    if with_derived:
        xc, vc, okc = common_removed(xbar, v, valid)
        Cc, nc = two_time(xc, vc, okc)
        out["A_c"] = slope_set(Cc, nc, wk_gap, T)["A"]
        m, vm, okm = swarm_mean(xbar, v, valid)
        Cm, nm = two_time(m, vm, okm)
        out["A_m"] = slope_set(Cm, nm, wk_gap, T)["A"]
        if stable is not None and stable.sum() >= 2:
            m, vm, okm = swarm_mean(xbar, v, valid, subset=stable)
            Cm, nm = two_time(m, vm, okm)
            out["A_ms"] = slope_set(Cm, nm, wk_gap, T)["A"]
    return out


def stable_subset(valid, frac=0.8):
    T = valid.shape[1]
    return valid.sum(1) >= frac * T


def null_distribution(model, design, wk_gap, T, B, rng, ndim=32, stable=None, with_derived=True, clock=None):
    rows = []
    for _ in range(B):
        xb, vv, ok = simulate_states(model, design, rng, n=ndim, clock=clock)
        rows.append(stats_bundle(xb, vv, ok, wk_gap, T, stable=stable, with_derived=with_derived))
    keys = rows[0].keys()
    return {k: np.array([r[k] for r in rows], float) for k in keys}


def p_upper(obs, null):
    null = null[np.isfinite(null)]
    if not np.isfinite(obs) or null.size == 0:
        return np.nan
    return float((1 + (null >= obs).sum()) / (1 + null.size))


def p_lower(obs, null):
    null = null[np.isfinite(null)]
    if not np.isfinite(obs) or null.size == 0:
        return np.nan
    return float((1 + (null <= obs).sum()) / (1 + null.size))


def alt_model(null_model: SwarmModel, mu: float, T: int):
    """The mu-aging reference at the fitted nuisance parameters: Box-Cox clock, tau rescaled so the
    mean local relaxation time over t in [2, T] matches the stationary fit."""
    t = np.arange(2, max(T, 3) + 1, dtype=float)
    sc = np.mean(t ** mu)
    import dataclasses
    return dataclasses.replace(null_model, mu=mu, tau=tuple(x / sc for x in null_model.tau))


def project_states(xbar, v, valid, ghat):
    """State-level V-g for the synthetic: project agent-day means off ĝ (isotropic noise loses 1/n of its variance)."""
    g = _unit(ghat)
    xp = xbar - (xbar @ g)[..., None] * g
    n = xbar.shape[-1]
    return xp, v * (1 - 1 / n), valid


def count_design(g: int, statements: pl.DataFrame | None = None, days: pl.DataFrame | None = None):
    """Counts-only sampling design of a period: n (A,T), valid, wk_gap, d_cal (no embeddings read)."""
    if statements is None:
        statements = pl.read_parquet(hc.OUT / "statements.parquet")
    if days is None:
        days = pl.read_parquet(hc.OUT / "days.parquet")
    st = statements.filter(pl.col("goal_no") == g)
    T = int(st["d"].max())
    agents = sorted(st["agent"].unique().to_list())
    amap = {a: i for i, a in enumerate(agents)}
    cnt = st.group_by("agent", "d").len()
    n = np.zeros((len(agents), T))
    for a, d, c in cnt.iter_rows():
        n[amap[a], d - 1] = c
    dd = days.filter((pl.col("goal_no") == g) & (pl.col("d") <= T)).sort("d")
    return dict(n=n, valid=n >= hc.MIN_STMTS, wk_gap=dd["weekend_gap"].to_numpy().astype(bool),
                d_cal=dd["d_cal"].to_numpy().astype(float), T=T, A=len(agents))


# ----------------------------------------------------------------------------------------------
# Amendment 2: anisotropic latent shapes (post hoc, after the real-data calibration check)
# ----------------------------------------------------------------------------------------------
def shape_factor(Cov, n, shrink=0.05):
    """Square-root factor R with R R^T / n = normalized (trace-1) covariance, shrunk toward isotropic."""
    w, U = np.linalg.eigh((Cov + Cov.T) / 2)
    w = np.clip(w, 0, None)
    if w.sum() <= 0:
        return None, float(n)
    w = w / w.sum()
    w = (1 - shrink) * w + shrink / n
    neff = 1.0 / (w ** 2).sum()
    R = np.sqrt(n) * (U * np.sqrt(w)) @ U.T
    return R, float(neff)


def estimate_shapes(xbar, v, valid, shrink=0.05):
    """Shared shape: covariance of swarm-mean day deviations; private shape: covariance of each agent's
    deviations from the swarm mean, around the agent's own period mean. Noise covariance (isotropic, trace v)
    subtracted. Used only to shape the null's latent draws (not for C)."""
    n = xbar.shape[-1]
    m, vm, okm = swarm_mean(xbar, v, valid)
    M = m[0][okm[0]]
    if M.shape[0] >= 3:
        Ms = M - M.mean(0)
        Cs = Ms.T @ Ms / max(M.shape[0] - 1, 1) - np.mean(vm[0][okm[0]]) / n * np.eye(n)
    else:
        Cs = np.eye(n)
    devs, vs = [], []
    for i in range(len(xbar)):
        ok = valid[i] & okm[0]
        if ok.sum() < 2:
            continue
        d = xbar[i][ok] - m[0][ok]
        devs.append(d - d.mean(0)); vs.append(v[i][ok])
    if devs:
        D = np.vstack(devs)
        Cp = D.T @ D / max(D.shape[0] - len(devs), 1) - np.mean(np.concatenate(vs)) / n * np.eye(n)
    else:
        Cp = np.eye(n)
    Rs, ns = shape_factor(Cs, n, shrink)
    Rp, npv = shape_factor(Cp, n, shrink)
    return Rs, Rp, ns, npv


def model_meta(m: SwarmModel):
    """JSON-safe description of a SwarmModel (shape factors summarized by their effective dimension)."""
    d = {k: v for k, v in dataclasses.asdict(m).items() if k not in ("Rs", "Rp")}
    for k in ("Rs", "Rp"):
        R = getattr(m, k)
        if R is None:
            d[f"neff_{k[1]}"] = None
        else:
            w = np.linalg.eigvalsh(R @ R.T / R.shape[0])
            w = np.clip(w, 0, None); w = w / w.sum()
            d[f"neff_{k[1]}"] = float(1 / (w ** 2).sum())
    return d
