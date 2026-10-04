"""H10 estimators: agent-window sufficient statistics, noise-deconvolved cumulants, the exponential tilt, and the
P1-P4 test statistics. Used unchanged by synthetic.py (validation), run_pairs.py (real data) and confirm.py.

Conventions
- Statement vectors z (n-d, unit). A segment is a set of statements with (agent, window, day) labels.
- Agent-window (aw) sufficient statistics: count c, S1 = sum z (n), S2 = sum z z^T (n x n), S3[k] = sum (z.u_k)^3 for the
  directions U = [g_hat, u_1 .. u_K] (n x (K+1); u_k orthonormal and orthogonal to g_hat).
- Eligible aw: c >= 2. Eligible agent: >= MIN_WIN eligible windows in the segment.
- Every estimator takes integer frequency weights per aw (bootstrap by resampling days = weights).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import permutations

import numpy as np

MIN_WIN = 6
MIN_STMT = 2


# ----------------------------------------------------------------------------------------------- data containers
@dataclass
class Segment:
    agent: np.ndarray          # (W,) agent code per aw
    day: np.ndarray            # (W,) day index per aw (int)
    win: np.ndarray            # (W,) window id (unique per day x window)
    c: np.ndarray              # (W,) statement count
    S1: np.ndarray             # (W, n)
    S2: np.ndarray             # (W, n, n)
    S3: np.ndarray             # (W, K+1) third power sums along U
    U: np.ndarray              # (n, K+1) directions; column 0 = g_hat
    meta: dict = field(default_factory=dict)

    @property
    def n(self):
        return self.S1.shape[1]


def random_transverse(g: np.ndarray, K: int, rng) -> np.ndarray:
    """U = [g, K random orthonormal directions orthogonal to g]."""
    n = len(g)
    g = g / np.linalg.norm(g)
    A = rng.standard_normal((n, K))
    A -= np.outer(g, g @ A)
    Q, _ = np.linalg.qr(A)
    return np.column_stack([g, Q[:, :K]])


def aggregate(Z: np.ndarray, agent: np.ndarray, day: np.ndarray, win: np.ndarray, U: np.ndarray, meta=None) -> Segment:
    """Statements -> aw sufficient statistics (only aw with >= MIN_STMT statements are kept)."""
    key = np.stack([agent.astype(np.int64), day.astype(np.int64), win.astype(np.int64)], 1)
    uk, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    inv = inv.ravel()
    keep = cnt >= MIN_STMT
    W, n = len(uk), Z.shape[1]
    S1 = np.zeros((W, n))
    np.add.at(S1, inv, Z)
    S2 = np.zeros((W, n, n))
    np.add.at(S2, inv, Z[:, :, None] * Z[:, None, :])
    Y = Z @ U
    S3 = np.zeros((W, U.shape[1]))
    np.add.at(S3, inv, Y ** 3)
    return Segment(uk[keep, 0], uk[keep, 1], uk[keep, 2], cnt[keep].astype(float), S1[keep], S2[keep], S3[keep], U,
                   meta or {})


# ----------------------------------------------------------------------------------------------- per-window projections
def proj_stats(seg: Segment, u_idx=None):
    """Per aw and direction: mean x, within-window unbiased variance s2, unbiased third cumulant k3 (n >= 3 else nan)."""
    U = seg.U if u_idx is None else seg.U[:, u_idx]
    c = seg.c[:, None]
    m1 = (seg.S1 @ U) / c
    m2 = np.einsum("wij,ik,jk->wk", seg.S2, U, U) / c
    m3 = (seg.S3 if u_idx is None else seg.S3[:, u_idx]) / c
    s2 = (m2 - m1 ** 2) * c / (c - 1)
    cm3 = m3 - 3 * m1 * m2 + 2 * m1 ** 3            # biased third central moment
    with np.errstate(invalid="ignore", divide="ignore"):
        k3 = np.where(c >= 3, cm3 * c ** 2 / ((c - 1) * (c - 2)), np.nan)
    return m1, s2, k3


# ----------------------------------------------------------------------------------------------- weighted k-statistics
def _wk(x, w):
    """Frequency-weighted mean, k2, k3, k4 along axis 0 (x: (T, K))."""
    T = w.sum()
    m = (w[:, None] * x).sum(0) / T
    d = x - m
    M2 = (w[:, None] * d ** 2).sum(0) / T
    M3 = (w[:, None] * d ** 3).sum(0) / T
    M4 = (w[:, None] * d ** 4).sum(0) / T
    k2 = M2 * T / (T - 1)
    k3 = M3 * T ** 2 / ((T - 1) * (T - 2)) if T > 2 else np.full_like(m, np.nan)
    k4 = (T ** 2 * ((T + 1) * M4 - 3 * (T - 1) * M2 ** 2) / ((T - 1) * (T - 2) * (T - 3))) if T > 3 else np.full_like(m, np.nan)
    return m, k2, k3, k4


@dataclass
class AgentStats:
    agents: np.ndarray        # (A,)
    T: np.ndarray             # (A,) effective windows
    mu: np.ndarray            # (A, K+1)
    k2: np.ndarray            # (A, K+1) signal variance (noise removed)
    k3: np.ndarray            # (A, K+1)
    k4: np.ndarray            # (A, K+1)
    noise: np.ndarray         # (A, K+1) mean noise variance of a window mean
    gamma: np.ndarray         # (K+1,) pooled standardized skewness
    eta: np.ndarray           # (K+1,) pooled excess kurtosis


def agent_stats(seg: Segment, w=None, agents=None, min_win=MIN_WIN) -> AgentStats:
    w = np.ones(len(seg.c)) if w is None else w
    x, s2, k3w = proj_stats(seg)
    nv = s2 / seg.c[:, None]                           # noise variance of the window mean
    ags = np.unique(seg.agent) if agents is None else np.asarray(agents)
    out = {k: [] for k in ("a", "T", "mu", "k2", "k3", "k4", "nz")}
    for a in ags:
        sel = (seg.agent == a) & (w > 0)
        T = w[sel].sum()
        if T < min_win or sel.sum() < 3:
            continue
        ww = w[sel]
        m, k2, k3, k4 = _wk(x[sel], ww)
        mnv = (ww[:, None] * nv[sel]).sum(0) / T
        # statement-level third cumulant pooled over the agent's windows (n >= 3), mapped to window means: k3_stmt / n^2
        k3s = np.nanmean(np.where(np.isfinite(k3w[sel]), k3w[sel], np.nan), 0)
        k3s = np.where(np.isfinite(k3s), k3s, 0.0)
        c = seg.c[sel][:, None]
        n3 = (ww[:, None] * (k3s / c ** 2)).sum(0) / T
        # kurtosis: heteroscedastic noise adds 3 var(noise var); statement k4 ~ ignored (tiny / n^3)
        vnv = (ww[:, None] * (nv[sel] - mnv) ** 2).sum(0) / T
        out["a"].append(a); out["T"].append(T); out["mu"].append(m)
        out["k2"].append(k2 - mnv); out["k3"].append(k3 - n3); out["k4"].append(k4 - 3 * vnv); out["nz"].append(mnv)
    A = {k: np.array(v) for k, v in out.items()}
    if len(A["a"]) == 0:
        K1 = seg.U.shape[1]
        z = np.zeros((0, K1))
        return AgentStats(np.array([], int), np.array([]), z, z, z, z, z, np.full(K1, np.nan), np.full(K1, np.nan))
    k2p = np.clip(A["k2"], 1e-12, None)
    gamma = A["k3"].sum(0) / (k2p ** 1.5).sum(0)
    eta = A["k4"].sum(0) / (k2p ** 2).sum(0)
    return AgentStats(A["a"], A["T"], A["mu"], A["k2"], A["k3"], A["k4"], A["nz"], gamma, eta)


# ----------------------------------------------------------------------------------------------- swarm level
def swarm_stats(seg: Segment, st: AgentStats, w=None, k2_override=None):
    """Swarm fluctuation variance V (noise removed), V_indep from per-agent k2, R = V / V_indep, g = 1 - 1/R.
    Windows need >= max(2, ceil(A/2)) eligible agents. Returns dict of (K+1,) arrays."""
    w = np.ones(len(seg.c)) if w is None else w
    x, s2, _ = proj_stats(seg)
    nv = s2 / seg.c[:, None]
    idx = {a: i for i, a in enumerate(st.agents)}
    ok = np.array([a in idx for a in seg.agent]) & (w > 0)
    if ok.sum() == 0:
        return None
    ai = np.array([idx.get(a, -1) for a in seg.agent])
    k2 = st.k2 if k2_override is None else k2_override
    dev = x - st.mu[np.clip(ai, 0, None)]
    wins = seg.win
    need = max(2, int(np.ceil(len(st.agents) / 2)))
    dm, nzv, vind, ww = [], [], [], []
    for u in np.unique(wins[ok]):
        sel = ok & (wins == u)
        N = sel.sum()
        if N < need:
            continue
        dm.append(dev[sel].mean(0))
        nzv.append(nv[sel].sum(0) / N ** 2)
        vind.append(np.clip(k2[ai[sel]], 0, None).sum(0) / N ** 2)
        ww.append(w[sel][0])
    if len(dm) < 4:
        return None
    dm, nzv, vind, ww = map(np.array, (dm, nzv, vind, ww))
    T = ww.sum()
    m = (ww[:, None] * dm).sum(0) / T
    var = (ww[:, None] * (dm - m) ** 2).sum(0) / (T - 1)
    V = var - (ww[:, None] * nzv).sum(0) / T
    Vi = (ww[:, None] * vind).sum(0) / T
    with np.errstate(divide="ignore", invalid="ignore"):
        R = V / Vi
        g = 1 - 1 / R
    return {"V": V, "V_indep": Vi, "R": R, "g": g, "n_win": T, "dm": dm[:, 0], "w": ww}


# ----------------------------------------------------------------------------------------------- the tilt
def solve_lambda(D, k2bar, k3bar):
    """Root of D = lam*k2 + lam^2/2*k3 continuous with D/k2 at k3 -> 0 (first order if no real root)."""
    lam1 = D / k2bar
    if not np.isfinite(k3bar) or abs(k3bar) < 1e-15:
        return lam1
    disc = k2bar ** 2 + 2 * k3bar * D
    if disc < 0:
        return lam1
    return (-k2bar + np.sign(k2bar) * np.sqrt(disc)) / k3bar


def tilt_predict(k2, k3, k4, lam):
    """First-order cumulant tilt: dmu = lam k2 + lam^2 k3/2; k2' = k2 + lam k3; k3' = k3 + lam k4."""
    return lam * k2 + 0.5 * lam ** 2 * k3, k2 + lam * k3, k3 + lam * k4


def pair_stats(F: AgentStats, A: AgentStats, gidx=0, shape_pooled=True):
    """Shared agents; Delta_i, lambda, predictions along direction gidx (0 = g_hat)."""
    common = np.intersect1d(F.agents, A.agents)
    fi = np.searchsorted(F.agents, common)
    ai = np.searchsorted(A.agents, common)
    k2F = F.k2[fi, gidx]
    k3F = (F.gamma[gidx] * np.clip(k2F, 0, None) ** 1.5) if shape_pooled else F.k3[fi, gidx]
    k4F = (F.eta[gidx] * np.clip(k2F, 0, None) ** 2) if shape_pooled else F.k4[fi, gidx]
    D = A.mu[ai, gidx] - F.mu[fi, gidx]
    Dbar = D.mean()
    lam = solve_lambda(Dbar, k2F.mean(), k3F.mean())
    dpred, k2pred, k3pred = tilt_predict(k2F, k3F, k4F, lam)
    return {"agents": common, "D": D, "Dbar": Dbar, "lam": lam, "k2F": k2F, "k3F": k3F, "k2A": A.k2[ai, gidx],
            "k3A": A.k3[ai, gidx], "dpred": dpred, "k2pred": k2pred, "k3pred": k3pred,
            "muF": F.mu[fi, gidx], "muA": A.mu[ai, gidx],
            "eps": lam * np.sqrt(max(k2F.mean(), 1e-12))}


def perm_p_r(x, y, rng, n_rand=20000):
    """One-sided permutation p for Pearson r(x, y) > 0 (exact when len <= 8)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return np.nan, np.nan
    xs = (x - x.mean()) / x.std()
    ys = (y - y.mean()) / y.std()
    r0 = float(xs @ ys / len(x))
    if len(x) <= 8:
        P = np.array(list(permutations(range(len(x)))))
    else:
        P = np.argsort(rng.random((n_rand, len(x))), axis=1)
    rs = xs[P] @ ys / len(x)
    return r0, float(np.mean(rs >= r0 - 1e-12))


def loao(D, k2, k3):
    """Leave-one-agent-out squared errors: tilt (one lambda) vs uniform translation."""
    n = len(D)
    et, eu = [], []
    for i in range(n):
        m = np.arange(n) != i
        lam = solve_lambda(D[m].mean(), k2[m].mean(), k3[m].mean())
        et.append((D[i] - (lam * k2[i] + 0.5 * lam ** 2 * k3[i])) ** 2)
        eu.append((D[i] - D[m].mean()) ** 2)
    return float(np.mean(et)), float(np.mean(eu))


# ----------------------------------------------------------------------------------------------- matrix version (P4)
def agent_cov(seg: Segment, w=None, agents=None, min_win=MIN_WIN, return_devs=False):
    """Per-agent noise-corrected window covariance C_i (n x n) and mean vector; returns (agents, mu (A,n), C (A,n,n))."""
    w = np.ones(len(seg.c)) if w is None else w
    xm = seg.S1 / seg.c[:, None]
    noise = (seg.S2 - seg.c[:, None, None] * xm[:, :, None] * xm[:, None, :]) / (seg.c - 1)[:, None, None] / seg.c[:, None, None]
    ags = np.unique(seg.agent) if agents is None else np.asarray(agents)
    out_a, out_m, out_C, devs, dw = [], [], [], [], []
    for a in ags:
        sel = (seg.agent == a) & (w > 0)
        T = w[sel].sum()
        if T < min_win or sel.sum() < 3:
            continue
        ww = w[sel]
        mu = (ww[:, None] * xm[sel]).sum(0) / T
        d = xm[sel] - mu
        C = np.einsum("t,ti,tj->ij", ww, d, d) / (T - 1) - np.einsum("t,tij->ij", ww, noise[sel]) / T
        out_a.append(a); out_m.append(mu); out_C.append(C); devs.append(d); dw.append(ww)
    if return_devs:
        return (np.array(out_a), np.array(out_m), np.array(out_C),
                (np.vstack(devs) if devs else np.zeros((0, seg.n)), np.concatenate(dw) if dw else np.zeros(0)))
    return np.array(out_a), np.array(out_m), np.array(out_C)


def lw_alpha(devs, w):
    """Ledoit-Wolf shrinkage intensity toward (tr S / n) I from frequency-weighted deviation vectors."""
    T = w.sum()
    if T < 3:
        return 1.0
    S = np.einsum("t,ti,tj->ij", w, devs, devs) / T
    n = S.shape[0]
    mI = np.trace(S) / n * np.eye(n)
    d2 = ((S - mI) ** 2).sum()
    b2 = (w * (((devs[:, :, None] * devs[:, None, :]) - S) ** 2).sum((1, 2))).sum() / T ** 2
    return float(min(1.0, b2 / d2)) if d2 > 0 else 1.0


def shrink(C, alpha):
    n = C.shape[0]
    Cs = (C + C.T) / 2
    return (1 - alpha) * Cs + alpha * np.trace(Cs) / n * np.eye(n)


def cosine(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-300))


def p4_stats(aF, muF, CF, aA, muA, g, rng, n_rot=1000, C_placebo=None, alpha=0.0):
    common = np.intersect1d(aF, aA)
    fi = np.searchsorted(aF, common); ai = np.searchsorted(aA, common)
    dmu = (muA[ai] - muF[fi]).mean(0)
    C = shrink(CF[fi].mean(0), alpha)
    p = C @ g
    out = {"cos_g": cosine(dmu, g), "cos_Cg": cosine(dmu, p), "cos_Cg_g": cosine(p, g), "alpha": alpha,
           "cos_Cg_raw": cosine(dmu, CF[fi].mean(0) @ g)}
    out["D"] = out["cos_Cg"] - out["cos_g"]
    ev, _ = np.linalg.eigh((C + C.T) / 2)
    n = len(g)
    rot = []
    for _ in range(n_rot):
        Q, R = np.linalg.qr(rng.standard_normal((n, n)))
        Q = Q * np.sign(np.diag(R))
        rot.append(cosine(dmu, (Q * ev) @ (Q.T @ g)))
    rot = np.array(rot)
    out["rot_p95"] = float(np.quantile(rot, 0.95))
    out["rot_p"] = float((rot >= out["cos_Cg"]).mean())
    if C_placebo is not None:
        out["cos_Cplacebo"] = [cosine(dmu, shrink(Cp, alpha) @ g) for Cp in C_placebo]
    out["dmu"] = dmu
    return out


# ----------------------------------------------------------------------------------------------- bootstrap weights
def day_weights(seg: Segment, rng):
    days = np.unique(seg.day)
    pick = rng.choice(days, size=len(days), replace=True)
    cnt = {d: 0 for d in days}
    for d in pick:
        cnt[d] += 1
    return np.array([cnt[d] for d in seg.day], float)


def stouffer(ps):
    from scipy.stats import norm
    ps = np.clip(np.asarray([p for p in ps if np.isfinite(p)]), 1e-6, 1 - 1e-6)
    if len(ps) == 0:
        return np.nan
    return float(norm.sf(norm.isf(ps).sum() / np.sqrt(len(ps))))


# ----------------------------------------------------------------------------------------------- one full pair analysis
def analyze_pair(F: Segment, A: Segment, rng, n_boot=300, n_rot=1000, C_placebo=None, with_p4=True, with_boot=True):
    """All P1-P4 statistics for one free -> assigned pair (both segments share U, column 0 = g_hat)."""
    g = F.U[:, 0]
    sF, sA = agent_stats(F), agent_stats(A)
    ps = pair_stats(sF, sA)
    res = {"N": len(ps["agents"]), "Dbar": ps["Dbar"], "lam": ps["lam"], "eps": ps["eps"],
           "gammaF": float(sF.gamma[0]), "gammaA": float(sA.gamma[0]), "etaF": float(sF.eta[0]), "etaA": float(sA.eta[0])}
    # P1
    r, p = perm_p_r(ps["k2F"], ps["D"], rng)
    et, eu = loao(ps["D"], ps["k2F"], ps["k3F"])
    res.update({"P1_r": r, "P1_p": p, "P1_mse_tilt": et, "P1_mse_trans": eu, "P1_D": ps["D"].tolist(),
                "P1_k2F": ps["k2F"].tolist(), "P1_dpred": ps["dpred"].tolist(), "agents": ps["agents"].tolist()})
    # R2 on cross-split (odd windows -> regressors, even windows -> free-week mean in Delta)
    odd = (F.win % 2 == 1).astype(float)
    sFo, sFe = agent_stats(F, w=odd, min_win=3), agent_stats(F, w=1 - odd, min_win=3)
    cm = np.intersect1d(np.intersect1d(sFo.agents, sFe.agents), sA.agents)
    if len(cm) >= 3:
        Do = sA.mu[np.searchsorted(sA.agents, cm), 0] - sFe.mu[np.searchsorted(sFe.agents, cm), 0]
        muo = sFo.mu[np.searchsorted(sFo.agents, cm), 0]
        k2o = sFo.k2[np.searchsorted(sFo.agents, cm), 0]
        res["R2_slope_muF"] = float(np.polyfit(muo, Do, 1)[0]) if np.std(muo) > 0 else np.nan
        res["R2_r_k2_cross"] = float(np.corrcoef(k2o, Do)[0, 1]) if np.std(k2o) > 0 else np.nan
    # P2 along g and transverse
    num, den = ps["k2A"].sum(), ps["k2pred"].sum()
    res["P2_rho"] = float(np.log(num / den)) if num > 0 and den > 0 else np.nan
    res["P2_rho_gauss"] = float(np.log(num / ps["k2F"].sum())) if num > 0 and ps["k2F"].sum() > 0 else np.nan
    rt = []
    for k in range(1, F.U.shape[1]):
        q = pair_stats(sF, sA, gidx=k)
        a_, b_ = q["k2A"].sum(), q["k2F"].sum()
        rt.append(np.log(a_ / b_) if a_ > 0 and b_ > 0 else np.nan)
    res["P2_rho_perp"] = float(np.nanmedian(rt)) if rt else np.nan
    res["P2_k3_pred"] = float(ps["k3pred"].sum()); res["P2_k3_obs"] = float(ps["k3A"].sum())
    # P3 and swarm
    wF, wA = swarm_stats(F, sF), swarm_stats(A, sA)
    if wF is not None and wA is not None:
        res.update({"gF": float(wF["g"][0]), "gA": float(wA["g"][0]), "RF": float(wF["R"][0]), "RA": float(wA["R"][0]),
                    "gF_perp": float(np.nanmedian(wF["g"][1:])), "gA_perp": float(np.nanmedian(wA["g"][1:])),
                    "VF": float(wF["V"][0]), "VA": float(wA["V"][0])})
        res["dg"] = res["gA"] - res["gF"]
        # swarm-level P2: V_A,pred = R_F * V_indep(A composition, predicted k2)
        k2pred_full = sA.k2.copy()
        idxA = {a: i for i, a in enumerate(sA.agents)}
        for a, kp in zip(ps["agents"], ps["k2pred"]):
            k2pred_full[idxA[a], 0] = kp
        wAp = swarm_stats(A, sA, k2_override=k2pred_full)
        if wAp is not None and wF["R"][0] > 0 and wA["V"][0] > 0:
            res["P2swarm_rho"] = float(np.log(wA["V"][0] / (wF["R"][0] * wAp["V_indep"][0])))
    # P4
    if with_p4:
        aF, mF, CF, (dv, dw) = agent_cov(F, return_devs=True)
        aA, mA, _ = agent_cov(A)
        q = p4_stats(aF, mF, CF, aA, mA, g, rng, n_rot=n_rot, C_placebo=C_placebo, alpha=lw_alpha(dv, dw))
        res.update({f"P4_{k}": v for k, v in q.items() if k != "dmu"})
    # bootstrap (days resampled within each segment)
    if with_boot and n_boot > 0:
        bs = {k: [] for k in ("Dbar", "lam", "P2_rho", "P2_rho_perp", "dg", "P4_D", "P1_r", "gF", "gA", "P2swarm_rho")}
        for _ in range(n_boot):
            b = analyze_pair_weighted(F, A, day_weights(F, rng), day_weights(A, rng), with_p4=with_p4)
            for k in bs:
                bs[k].append(b.get(k, np.nan))
        for k, v in bs.items():
            v = np.array(v, float)
            res[f"{k}_ci90"] = [float(np.nanquantile(v, 0.05)), float(np.nanquantile(v, 0.95))] if np.isfinite(v).sum() > 10 else [np.nan, np.nan]
    return res


def analyze_pair_weighted(F, A, wF, wA, with_p4=True):
    """Point statistics under bootstrap weights (no permutation / rotation nulls)."""
    sF, sA = agent_stats(F, w=wF), agent_stats(A, w=wA)
    out = {}
    if len(np.intersect1d(sF.agents, sA.agents)) < 3:
        return out
    ps = pair_stats(sF, sA)
    out["Dbar"], out["lam"] = ps["Dbar"], ps["lam"]
    if np.std(ps["k2F"]) > 0:
        out["P1_r"] = float(np.corrcoef(ps["k2F"], ps["D"])[0, 1])
    num, den = ps["k2A"].sum(), ps["k2pred"].sum()
    out["P2_rho"] = float(np.log(num / den)) if num > 0 and den > 0 else np.nan
    rt = []
    for k in range(1, F.U.shape[1]):
        q = pair_stats(sF, sA, gidx=k)
        a_, b_ = q["k2A"].sum(), q["k2F"].sum()
        rt.append(np.log(a_ / b_) if a_ > 0 and b_ > 0 else np.nan)
    out["P2_rho_perp"] = float(np.nanmedian(rt))
    swF, swA = swarm_stats(F, sF, w=wF), swarm_stats(A, sA, w=wA)
    if swF is not None and swA is not None:
        out["gF"], out["gA"] = float(swF["g"][0]), float(swA["g"][0])
        out["dg"] = out["gA"] - out["gF"]
        k2pred_full = sA.k2.copy()
        idxA = {a: i for i, a in enumerate(sA.agents)}
        for a, kp in zip(ps["agents"], ps["k2pred"]):
            k2pred_full[idxA[a], 0] = kp
        wAp = swarm_stats(A, sA, w=wA, k2_override=k2pred_full)
        if wAp is not None and swF["R"][0] > 0 and swA["V"][0] > 0:
            out["P2swarm_rho"] = float(np.log(swA["V"][0] / (swF["R"][0] * wAp["V_indep"][0])))
    if with_p4:
        g = F.U[:, 0]
        aF, mF, CF, (dv, dw) = agent_cov(F, w=wF, return_devs=True)
        aA, mA, _ = agent_cov(A, w=wA)
        cm = np.intersect1d(aF, aA)
        if len(cm) >= 2:
            fi, ai = np.searchsorted(aF, cm), np.searchsorted(aA, cm)
            dmu = (mA[ai] - mF[fi]).mean(0)
            C = shrink(CF[fi].mean(0), lw_alpha(dv, dw))
            out["P4_D"] = cosine(dmu, C @ g) - cosine(dmu, g)
    return out


# ----------------------------------------------------------------------------------------------- verdict rules (card)
LN15 = np.log(1.5)


def verdict_P1(r, p, mse_t, mse_u):
    if not np.isfinite(r):
        return "n/a"
    if r > 0 and mse_t < mse_u:
        return "supported"
    if r <= 0:
        return "failed"
    return "mixed"


def verdict_P2(rho, ci):
    if not np.isfinite(rho) or not np.all(np.isfinite(ci)):
        return "n/a"
    if ci[0] <= 0 <= ci[1] and abs(rho) < LN15:
        return "supported"
    if (ci[0] > 0 or ci[1] < 0) and abs(rho) >= LN15:
        return "failed (" + ("R4 dispersal" if rho > 0 else "R3 cooling") + ")"
    return "inconclusive"


def verdict_P3(dg, ci):
    if not np.isfinite(dg) or not np.all(np.isfinite(ci)):
        return "n/a"
    if ci[0] <= 0 <= ci[1]:
        return "supported"
    if abs(dg) >= 0.2:
        return "failed"
    return "inconclusive"


def verdict_P4(D, ci, cos_Cg, rot_p95):
    if not np.isfinite(D):
        return "n/a"
    if ci[0] > 0 and cos_Cg > rot_p95:
        return "supported"
    if D <= 0:
        return "failed"
    return "inconclusive"


def verdict_pair(v1, v2, v3=None, v4=None):
    """Amendment 1: the pair verdict rests on P1 and P2 only (P3, P4 descriptive); P2 may be n/a (non-perturbative)."""
    if v1 == "failed" or v2.startswith("failed"):
        return "failed"
    if v1 == "supported" and v2 == "supported":
        return "supported"
    return "mixed"
