"""H21 two-sublattice ("antiferromagnet") statistics on agent content vectors.

Everything here is data-source agnostic: it takes whitened statement vectors X (n x D) plus a statement table
and returns order parameters, null distributions and recoveries. Used by synthetic.py (axis F), g12_analysis.py
(real data, G12) and confirm_g34.py (locked holdout, not run).

Conventions (see ../README.md, "Observables")
- Statement table columns: debate (int), agent (int), team (+1 Gov / -1 Opp / 0 judge or bench), phase
  ('pre' | 'deb' | 'post'), t (float seconds), and optionally lab.
- Sublattice A = Government (eps = +1), B = Opposition (eps = -1). The judge is never on a sublattice.
- Spin of agent i in a window: s_i = unit(v_i - c), v_i = mean of i's (agent-centred) statement vectors in the
  window, c = mean of v over the window's debaters ("debate-centring" removes the uniform/topic component).
- Agent-centring subtracts each agent's mean over the whole goal period: removes the agent/family field h_i,
  which is legitimate because team assignments rotate across debates.
"""
from __future__ import annotations

import itertools
import math

import numpy as np


# ------------------------------------------------------------------------------------------------ basics
def unit(v, axis=-1):
    v = np.asarray(v, dtype=np.float64)
    n = np.linalg.norm(v, axis=axis, keepdims=True)
    return v / np.where(n > 0, n, 1.0)


def agent_center(X, agents):
    """Subtract each agent's mean statement vector (over the rows given)."""
    Xc = np.array(X, dtype=np.float64, copy=True)
    for a in np.unique(agents):
        m = agents == a
        Xc[m] -= Xc[m].mean(0)
    return Xc


def window_means(X, agents, mask, min_n=1, weights=None):
    """Mean vector per agent over rows in `mask`. Returns (agent_ids, V, counts)."""
    idx = np.flatnonzero(mask)
    ids, V, cnt = [], [], []
    for a in np.unique(agents[idx]):
        r = idx[agents[idx] == a]
        if len(r) < min_n:
            continue
        w = None if weights is None else weights[r]
        ids.append(int(a))
        V.append(np.average(X[r], axis=0, weights=w))
        cnt.append(len(r))
    D = X.shape[1]
    return np.array(ids, dtype=int), (np.array(V) if V else np.zeros((0, D))), np.array(cnt, dtype=int)


def spins(V, center=True):
    """Debate-centre (optional) and normalise the agents' window means."""
    V = np.asarray(V, dtype=np.float64)
    if center and len(V):
        V = V - V.mean(0)
    return unit(V)


# ------------------------------------------------------------------------------------------------ partitions
def partitions(n, kA):
    """All distinct two-block partitions of n sites with block sizes (kA, n-kA), as eps arrays (+1 = block A).

    Statistics used here are invariant under swapping A and B, so when kA == n - kA each unordered partition is
    listed once (site 0 fixed in A)."""
    kB = n - kA
    out = []
    for A in itertools.combinations(range(n), kA):
        if kA == kB and 0 not in A:
            continue
        e = -np.ones(n, dtype=int)
        e[list(A)] = 1
        out.append(e)
    return out


def canon(eps):
    """Canonical form of a partition (swap-invariant when blocks are equal size)."""
    e = np.asarray(eps)
    if (e == 1).sum() == (e == -1).sum() and e[0] == -1:
        e = -e
    return tuple(int(x) for x in e)


# ------------------------------------------------------------------------------------------------ order parameters
def delta_stat(S, eps):
    """Within-team minus cross-team mean cosine of unit spins S (k x D). AF / two-sublattice order: > 0."""
    G = S @ S.T
    k = len(eps)
    iu = np.triu_indices(k, 1)
    same = (eps[iu[0]] == eps[iu[1]])
    g = G[iu]
    if same.sum() == 0 or (~same).sum() == 0:
        return np.nan
    return g[same].mean() - g[~same].mean()


def loao_frame(V, eps, i):
    """Leave-one-agent-out frame for site i, built from the OTHER agents only.

    c = mean of the others' raw window vectors; the others' spins are unit(V_j - c); the axis is
    unit(mean_{A minus i} s - mean_{B minus i} s). Centring on a mean that includes i would leak i into its own
    axis (a positive bias of ~0.05 in sigma under the null at G12's design); excluding i removes it."""
    keep = np.arange(len(eps)) != i
    c = V[keep].mean(0)
    So = unit(V[keep] - c)
    eo = eps[keep]
    a = np.zeros(V.shape[1])
    if (eo == 1).any():
        a = a + So[eo == 1].mean(0)
    if (eo == -1).any():
        a = a - So[eo == -1].mean(0)
    return c, unit(a)


def loao_sigma(V, eps, V_eval=None):
    """Staggered projection sigma_i = eps_i * unit(v_i - c_{-i}) . a_{-i}, frame and axis from the other agents.

    V: raw (agent-centred, NOT debate-centred) window means. V_eval (optional): vectors projected instead of V
    (e.g. post-verdict means), in the same frame."""
    V_eval = V if V_eval is None else V_eval
    out = []
    for i in range(len(eps)):
        c, a = loao_frame(V, eps, i)
        out.append(eps[i] * (unit(V_eval[i] - c) @ a))
    return np.array(out)


def team_axis(S, eps):
    return unit(S[eps == 1].mean(0) - S[eps == -1].mean(0))


def debate_stats(V, eps):
    """Per-debate stats for the true partition plus every alternative partition (for nulls and recovery).

    V: raw agent-centred window means of the debaters (debate-centring is done here)."""
    S = spins(V)
    kA = int((eps == 1).sum())
    parts = partitions(len(eps), kA)
    D_all = np.array([delta_stat(S, e) for e in parts])
    M_all = np.array([loao_sigma(V, e).mean() for e in parts])
    truth = canon(eps)
    ti = [canon(e) for e in parts].index(truth)
    order = np.argsort(-D_all)
    rank = int(np.flatnonzero(order == ti)[0]) + 1
    return {"delta": D_all[ti], "ms": M_all[ti], "delta_all": D_all, "ms_all": M_all, "true_idx": ti,
            "n_part": len(parts), "rank": rank, "recovered": rank == 1, "best_eps": parts[order[0]]}


# ------------------------------------------------------------------------------------------------ nulls
def poisson_binomial_sf(k, ps):
    """P(sum of independent Bernoulli(ps) >= k)."""
    dist = np.zeros(len(ps) + 1)
    dist[0] = 1.0
    for p in ps:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    return float(dist[k:].sum())


def perm_null(per_debate, key_all, n_draw=20000, rng=None):
    """Pooled (mean over debates) null of a statistic under independent uniform re-partition of each debate."""
    rng = np.random.default_rng(rng)
    tot = np.zeros(n_draw)
    for d in per_debate:
        vals = d[key_all]
        tot += vals[rng.integers(0, len(vals), n_draw)]
    return tot / len(per_debate)


def p_upper(obs, null):
    null = np.asarray(null)
    return float((1 + np.sum(null >= obs - 1e-12)) / (1 + len(null)))


def p_lower(obs, null):
    null = np.asarray(null)
    return float((1 + np.sum(null <= obs + 1e-12)) / (1 + len(null)))


def random_rotation(D, rng):
    Q, R = np.linalg.qr(rng.standard_normal((D, D)))
    return Q * np.sign(np.diag(R))


def rotation_null(windows, n_draw=1000, rng=None, center=True):
    """Per-agent random rotation null (model 11): one orthogonal Q_a per agent for the whole period, applied to
    the agent-centred window means; destroys cross-agent alignment, keeps each agent's own trajectory.

    windows: list of dicts with 'agents' (ids), 'V' (raw agent-centred window means), 'eps'.
    Returns arrays (pooled delta, pooled m_s) over draws."""
    rng = np.random.default_rng(rng)
    agents = sorted({int(a) for w in windows for a in w["agents"]})
    D = windows[0]["V"].shape[1]
    out_d, out_m = np.zeros(n_draw), np.zeros(n_draw)
    for b in range(n_draw):
        Q = {a: random_rotation(D, rng) for a in agents}
        ds, ms = [], []
        for w in windows:
            V = np.stack([Q[int(a)] @ v for a, v in zip(w["agents"], w["V"])])
            S = spins(V, center)
            ds.append(delta_stat(S, w["eps"]))
            ms.append(loao_sigma(V, w["eps"]).mean())
        out_d[b], out_m[b] = np.nanmean(ds), np.mean(ms)
    return out_d, out_m


# ------------------------------------------------------------------------------------------------ generic vs motion-specific
def generic_axes(windows):
    """Cross-debate ('generic') Gov-minus-Opp axis for each debate, fitted on the OTHER debates only (from their
    debate-centred unit spins S).

    Captures rhetoric shared by every Government (proposing) vs Opposition (opposing) side, plus any leftover
    role vocabulary. Motion-specific stance is what remains after projecting it out."""
    diffs = [w["S"][w["eps"] == 1].mean(0) - w["S"][w["eps"] == -1].mean(0) for w in windows]
    tot = np.sum(diffs, axis=0)
    return [unit(tot - d) for d in diffs]


def project_out(V, a):
    """Remove direction a from raw vectors (linear, so it commutes with debate-centring)."""
    a = unit(a)
    return V - np.outer(V @ a, a)


# ------------------------------------------------------------------------------------------------ fluctuations
def sublattice_fluct(series):
    """Staggered vs uniform fluctuations from time-binned sublattice magnetisations along a fixed axis.

    series: list (one per debate) of (mA, mB) arrays over time bins where both blocks spoke.
    Returns rho = corr(dA, dB) of within-debate demeaned series, chi_s/chi_u = Var(dA-dB)/Var(dA+dB),
    and the linear two-block mean-field AF loop gain K_AF = -rho (attenuated by measurement noise)."""
    dA, dB = [], []
    for mA, mB in series:
        if len(mA) < 2:
            continue
        dA.append(mA - mA.mean())
        dB.append(mB - mB.mean())
    if not dA:
        return {"rho": np.nan, "chi_ratio": np.nan, "K_AF": np.nan, "n_bins": 0}
    dA, dB = np.concatenate(dA), np.concatenate(dB)
    rho = float(np.corrcoef(dA, dB)[0, 1]) if dA.std() > 0 and dB.std() > 0 else np.nan
    chi = float(np.var(dA - dB) / np.var(dA + dB)) if np.var(dA + dB) > 0 else np.nan
    return {"rho": rho, "chi_ratio": chi, "K_AF": -rho, "n_bins": int(len(dA))}


def fluct_perm_null(series, n_draw=5000, rng=None):
    """Null for rho: permute the B bins within each debate (breaks temporal pairing, keeps marginals)."""
    rng = np.random.default_rng(rng)
    out = np.zeros(n_draw)
    for b in range(n_draw):
        out[b] = sublattice_fluct([(mA, rng.permutation(mB)) for mA, mB in series])["rho"]
    return out


# ------------------------------------------------------------------------------------------------ bootstrap
def boot_ci(vals, n=5000, rng=None, stat=np.mean, alpha=0.05):
    rng = np.random.default_rng(rng)
    vals = np.asarray(vals, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return (np.nan, np.nan)
    b = np.array([stat(vals[rng.integers(0, len(vals), len(vals))]) for _ in range(n)])
    return (float(np.quantile(b, alpha / 2)), float(np.quantile(b, 1 - alpha / 2)))


def ratio_boot_ci(num, den, n=5000, rng=None, alpha=0.05):
    rng = np.random.default_rng(rng)
    num, den = np.asarray(num, float), np.asarray(den, float)
    k = len(num)
    b = []
    for _ in range(n):
        r = rng.integers(0, k, k)
        d = den[r].mean()
        b.append(num[r].mean() / d if d != 0 else np.nan)
    b = np.array(b)
    b = b[np.isfinite(b)]
    return (float(np.quantile(b, alpha / 2)), float(np.quantile(b, 1 - alpha / 2)))


def n_partitions(n, kA):
    kB = n - kA
    c = math.comb(n, kA)
    return c // 2 if kA == kB else c
