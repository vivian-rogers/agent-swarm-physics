"""Semantic-information channel table (HH307): kappa_c = Delta V_c / I_c, in commits per bit, by channel.

First used by H70 (the artifact row, 2026-10-04). Written so that other channels (history search, kickoff, human
messages, memory size at erasure) can be added later by building an event frame with the same columns.

Event frame (one row per scramble event or matched placebo):
    cluster   resampling unit for the bootstrap (e.g. "agent|pt_date")
    stratum   permutation stratum for the information floor (e.g. "agent|period"); also the fixed-effect group
    scramble  bool: True = the context was erased (forced erasure, night); False = matched placebo (context intact)
    X         int: the allocation after the event (e.g. repo id of the first work commit in the window; -1 = none)
    S         int: the channel's pointer (e.g. repo named by the channel; -1 = none)
    open      bool: the channel was used / points at the agent's own artifact
    V         float: viability (e.g. work commits in the 20 calls after the event)
    V_pre     float: pre-event output (covariate)

Quantities (all in bits or commits per window):
    I_c   = MI_MM(X; S) - mean_perm MI_MM(X; S_perm), S permuted within stratum (agent identity carries no bits);
            computed on scramble events (stored information that survives the erasure).
    dV_c  = open x scramble interaction in a Poisson pseudo-ML with stratum x arm fixed effects (see did_value):
            dV_rel = exp(b2) - 1 (proportional, scale-free), dV = commits per window it adds after a scramble.
    kappa = dV_c / I_c, bootstrap over clusters (paired draws for numerator and denominator).
Miller-Madow: H_MM = H_plugin + (m - 1) / (2 N ln 2) bits, m = occupied bins.

Identification (round 3, 2026-10-04; H87 Amendment A1): kappa_row returns `identified` = the I interval's lower bound
is above 0.02 bits. Order two channels by kappa only when both are identified; a row that is not identified gets kappa
"n.i." and is placed by its dV ("kappa ~ 0" if the dV CI includes 0, else "unresolved"). Even identified, kappa is
unstable while I < ~0.05 bits (raw ratios gave false orderings in 32% of H87's synthetic replicates at ~0.02 bits).

Information intervals (round 3): `I_ci` is the round-2 cluster bootstrap (percentile, recentred on the point estimate,
because duplicated clusters inflate plug-in MI by ~+0.08 bits in every draw; a textbook bias correction with that
bootstrap bias drives coverage to ~0). It stays the default and is bit-identical to round 2. `I_ci_jk` adds a
delete-one-cluster jackknife SE with a normal interval around the same point estimate. Coverage of nominal 95% intervals
(`--coverage`, infra/data-quality/semantic_kappa_coverage.json; 100 replicates, 60 at real counts, B = 40):
  real NE41 counts, I = 0 to 0.09 bits: bootstrap 0.967 at every level, jackknife 0.967-0.983;
  dense 1-bit self-check world (I = 1.05): bootstrap 0.89 (Miller-Madow leaves +0.023 bits), jackknife 0.93;
  dense I = 0 / 0.21: bootstrap 0.99 / 0.96, jackknife 1.00 / 1.00.
The 0.75-0.80 seen in round 2's self-check was 20 replicates (binomial SE ~0.09) of that 1-bit world.
In sparse tables (< ~2 scramble events per occupied (X, S) cell) the permutation floor over-corrects and I is biased
toward 0 (-0.30 bits at a planted 0.58, -1.08 at 2.25; both intervals cover <= 0.14): `I_sparse` flags it, and no interval repairs it.

Self-check: uv run python infra/shared/semantic_kappa.py --verify     (planted bits and DiD; round-2 fields unchanged)
Coverage:   uv run python infra/shared/semantic_kappa.py --coverage   (slow: ~15 min; writes the JSON above)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

LN2 = math.log(2)


# ---------------------------------------------------------------------------------------------- information
def _codes(a: np.ndarray) -> np.ndarray:
    return np.unique(np.asarray(a), return_inverse=True)[1]


def entropy_mm(counts: np.ndarray) -> float:
    c = counts[counts > 0].astype(float)
    n = c.sum()
    if n == 0:
        return 0.0
    p = c / n
    return float(-(p * np.log2(p)).sum() + (len(c) - 1) / (2 * n * LN2))


def mi_mm(x: np.ndarray, y: np.ndarray) -> float:
    """Plug-in mutual information in bits with Miller-Madow corrections on the three entropies."""
    if len(x) == 0:
        return float("nan")
    xc, yc = _codes(x), _codes(y)
    ny = yc.max() + 1
    joint = np.bincount(xc * ny + yc)
    return entropy_mm(np.bincount(xc)) + entropy_mm(np.bincount(yc)) - entropy_mm(joint)


def permute_within(s: np.ndarray, strata: np.ndarray, rng) -> np.ndarray:
    out = s.copy()
    order = np.argsort(strata, kind="stable")
    st = strata[order]
    cuts = np.flatnonzero(np.diff(st)) + 1
    for blk in np.split(order, cuts):
        if len(blk) > 1:
            out[blk] = s[rng.permutation(blk)]
    return out


class _JkEntropy:
    """Miller-Madow entropy of one code column, with fast delete-a-cluster recomputation (counts updated locally)."""

    def __init__(self, codes: np.ndarray):
        self.codes = codes
        self.c = np.bincount(codes).astype(float)
        nz = self.c[self.c > 0]
        self.n = float(self.c.sum())
        self.m = int(len(nz))
        self.slogc = float((nz * np.log2(nz)).sum())

    def without(self, rows: np.ndarray | None) -> float:
        n, m, sl = self.n, self.m, self.slogc
        if rows is not None and len(rows):
            b, k = np.unique(self.codes[rows], return_counts=True)
            old = self.c[b]
            new = old - k
            pos = new > 0
            sl += float(-(old * np.log2(old)).sum() + (new[pos] * np.log2(new[pos])).sum())
            m -= int((~pos).sum())
            n -= float(k.sum())
        if n <= 0:
            return 0.0
        return math.log2(n) - sl / n + (m - 1) / (2 * n * LN2)


def _mi_loo(xc: np.ndarray, sc: np.ndarray, members: list) -> tuple[float, np.ndarray]:
    jc = xc * (int(sc.max()) + 1) + sc
    ex, es, ej = _JkEntropy(xc), _JkEntropy(sc), _JkEntropy(_codes(jc))
    full = ex.without(None) + es.without(None) - ej.without(None)
    loo = np.array([ex.without(r) + es.without(r) - ej.without(r) for r in members])
    return full, loo


def mi_jackknife(x, s, strata, clusters, n_perm: int = 20, rng=None) -> dict:
    """Delete-one-cluster jackknife of I = MI_MM(X; S) - mean_perm MI_MM(X; S_perm) (round-3 consolidation, 2026-10-04).

    The permutation floor uses `n_perm` fixed within-stratum permutations of S on the full data; deleting a cluster
    deletes its rows from the data and from every permuted copy (common random numbers), so the floor is a fixed
    function of the sample. Returns the jackknife bias, the jackknife SE (cluster-robust; no duplicated clusters, so
    none of the bootstrap's duplication inflation) and the leave-one-out values."""
    rng = rng or np.random.default_rng(1)
    x, s = np.asarray(x), np.asarray(s)
    xc, sc, stc, cl = _codes(x), _codes(s), _codes(strata), _codes(clusters)
    order = np.argsort(cl, kind="stable")
    members = np.split(order, np.flatnonzero(np.diff(cl[order])) + 1)
    n = len(members)
    if n < 3 or len(x) == 0:
        return {"I_full": float("nan"), "bias": float("nan"), "se": float("nan"), "n_clusters": n}
    raw, raw_loo = _mi_loo(xc, sc, members)
    fl, fl_loo = 0.0, np.zeros(n)
    for _ in range(n_perm):
        f, fo = _mi_loo(xc, _codes(permute_within(sc, stc, rng)), members)
        fl += f / n_perm
        fl_loo += fo / n_perm
    full, loo = raw - fl, raw_loo - fl_loo
    return {"I_full": float(full), "bias": float((n - 1) * (loo.mean() - full)),
            "se": float(math.sqrt((n - 1) / n * ((loo - loo.mean()) ** 2).sum())), "n_clusters": n}


def mi_corrected(x, s, strata, n_perm: int = 200, rng=None) -> dict:
    """MI minus its within-stratum permutation floor; permutation p (one-sided, I_obs >= I_perm)."""
    rng = rng or np.random.default_rng(0)
    x, s, strata = np.asarray(x), np.asarray(s), _codes(strata)
    raw = mi_mm(x, s)
    perm = np.array([mi_mm(x, permute_within(s, strata, rng)) for _ in range(n_perm)])
    return {"I": float(raw - perm.mean()), "I_raw": float(raw), "I_floor": float(perm.mean()),
            "p_perm": float((1 + np.sum(perm >= raw)) / (1 + n_perm)), "n": int(len(x))}


# ---------------------------------------------------------------------------------------------- value
def _within(a: np.ndarray, g: np.ndarray) -> np.ndarray:
    sums = np.bincount(g, weights=a)
    cnt = np.bincount(g)
    return a - (sums / np.maximum(cnt, 1))[g]


def poisson_fe(V: np.ndarray, X: np.ndarray, groups: np.ndarray, iters: int = 50) -> np.ndarray:
    """Poisson pseudo-ML of log E[V] = alpha_group + X beta, with the group effects concentrated out.
    Groups whose V sums to 0 carry no information and are dropped. Returns beta."""
    g = _codes(groups)
    tot = np.bincount(g, weights=V)
    keep = tot[g] > 0
    V, X, g = V[keep], X[keep], g[keep]
    beta = np.full(X.shape[1], np.nan)
    if len(V) < 5:
        return beta
    g = _codes(g)
    tot = np.bincount(g, weights=V)
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = X @ beta
        e = np.exp(eta - eta.max())
        den = np.bincount(g, weights=e)
        mu = e * (tot / den)[g]
        w = mu
        xbar = np.column_stack([np.bincount(g, weights=w * X[:, j]) / np.bincount(g, weights=w)
                                for j in range(X.shape[1])])[g]
        Xc = X - xbar
        score = Xc.T @ (V - mu)
        H = (Xc * w[:, None]).T @ Xc
        try:
            step = np.linalg.solve(H, score)
        except np.linalg.LinAlgError:
            return np.full(X.shape[1], np.nan)
        if not np.all(np.isfinite(step)):
            return np.full(X.shape[1], np.nan)
        beta = beta + np.clip(step, -2, 2)
        if np.max(np.abs(step)) < 1e-8:
            break
    return beta


def did_value(V, open_, scramble, strata, V_pre=None, relative: bool = True) -> dict:
    """Value of an open channel: the open x scramble interaction with stratum x arm fixed effects.

    relative=True (default): Poisson pseudo-ML, log E[V] = FE(stratum x arm) + b1 open + b2 open x scramble
    (+ b3 log(1 + V_pre)). dV_rel = exp(b2) - 1: the extra *proportional* gain of an open channel after a scramble,
    beyond its gain at the placebo. Scale-free, so a multiplicative "reading precedes writing" effect cancels even
    when the scramble itself lowers V. dV (commits per window) = mean V of open scramble events x (1 - exp(-b2)).
    relative=False: additive DiD on V (biased under multiplicative effects when the arms differ in mean V)."""
    V = np.asarray(V, float)
    o = np.asarray(open_, float)
    s = np.asarray(scramble, float)
    g = _codes(strata)
    nan = {"dV": float("nan"), "dV_rel": float("nan"), "open_placebo": float("nan"), "scramble": float("nan")}
    if relative:
        ga = g * 2 + (s > 0).astype(int)
        cols = [o, o * s] + ([np.log1p(np.clip(np.asarray(V_pre, float), 0, None))] if V_pre is not None else [])
        X = np.column_stack(cols)
        ok = np.isfinite(V) & np.all(np.isfinite(X), axis=1)
        if ok.sum() < 10 or o[ok].std() == 0:
            return nan
        b = poisson_fe(V[ok], X[ok], ga[ok])
        if not np.all(np.isfinite(b[:2])) or np.max(np.abs(b[:2])) > 20:
            return nan
        vs = float(np.nanmean(V[(s > 0) & (o > 0)])) if ((s > 0) & (o > 0)).any() else float("nan")
        return {"dV": float(vs * (1 - np.exp(-b[1]))), "dV_rel": float(np.exp(b[1]) - 1),
                "open_placebo": float(np.exp(b[0]) - 1), "scramble": float("nan")}
    cols = [o, s, o * s] + ([np.asarray(V_pre, float)] if V_pre is not None else [])
    X = np.column_stack([_within(c, g) for c in cols])
    y = _within(V, g)
    keep = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    if keep.sum() < 10:
        return nan
    beta = np.linalg.lstsq(X[keep], y[keep], rcond=None)[0]
    vs = float(np.nanmean(V[s > 0]))
    return {"dV": float(beta[2]), "dV_rel": float(beta[2] / vs) if vs > 0 else float("nan"),
            "open_placebo": float(beta[0]), "scramble": float(beta[1])}


def scramble_cost(V, scramble, strata, V_pre=None) -> dict:
    """Cost of the erasure itself (context row): Poisson pseudo-ML log E[V] = FE(stratum) + b scramble (+ log1p V_pre).
    cost_rel = 1 - exp(b) (share of output lost); cost (commits per window) = mean V of placebo events x cost_rel."""
    V = np.asarray(V, float)
    s = np.asarray(scramble, float)
    cols = [s] + ([np.log1p(np.clip(np.asarray(V_pre, float), 0, None))] if V_pre is not None else [])
    X = np.column_stack(cols)
    ok = np.isfinite(V) & np.all(np.isfinite(X), axis=1)
    if ok.sum() < 10:
        return {"cost": float("nan"), "cost_rel": float("nan")}
    b = poisson_fe(V[ok], X[ok], _codes(strata)[ok])
    rel = float(1 - np.exp(b[0])) if np.isfinite(b[0]) and abs(b[0]) < 20 else float("nan")
    return {"cost": float(np.nanmean(V[s == 0]) * rel), "cost_rel": rel}


# ---------------------------------------------------------------------------------------------- the row
MIN_I_IDENT = 0.02     # Amendment A1 (H87): a row is identified when its I CI lower bound exceeds this
I_STABLE = 0.05        # below ~0.05 bits the ratio kappa = dV / I is unstable (H87 synthetic)
SPARSE_PER_CELL = 2.0  # scramble events per occupied (X, S) cell below which I is biased toward 0 (see I_sparse)


def kappa_row(ev: dict, n_perm: int = 200, B: int = 300, n_perm_boot: int = 10, seed: int = 0,
              min_I: float = 0.02, min_I_ident: float = MIN_I_IDENT, jackknife: bool = True,
              n_perm_jk: int = 20) -> dict:
    """One channel's row. ev: dict of numpy arrays with the module-docstring columns.

    Information is computed on scramble events only; the value on scramble + placebo events. Bootstrap: clusters
    resampled with replacement (the same draws for I and dV), with the permutation floor recomputed per draw.

    Round-3 additions (2026-10-04). Every earlier field is unchanged and bit-identical (the additions use their own
    random stream, so H70/H87 numbers reproduce):
      identified   Amendment A1 (H87): I_ci lower bound > min_I_ident (0.02 bits). Order kappa between two rows only
                   when both are identified; a row that is not identified gets kappa "n.i." and is placed by its dV.
                   kappa is also unstable while I < ~0.05 bits (I_STABLE): read kappa_ci, not the point ratio.
      I_se_jk, I_ci_jk   delete-one-cluster jackknife SE (mi_jackknife) and the normal interval I +- 1.96 SE_jk
                   (centred on the unchanged point estimate). identified_jk applies A1 to it. Coverage (synthetic, see
                   `coverage`) matches the bootstrap at real counts and is closer to nominal in a dense 1-bit world.
      I_bc, I_ci_jk_bc   jackknife bias-corrected I and its interval (diagnostic: it over-corrects at ~1 bit).
      n_per_cell, I_sparse   scramble events per occupied (X, S) cell; I_sparse = n_per_cell < 2: the permutation
                   floor then over-corrects and I is biased toward 0 (no interval fixes this)."""
    rng = np.random.default_rng(seed)
    sc = np.asarray(ev["scramble"], bool)
    xs, ss, sts = np.asarray(ev["X"])[sc], np.asarray(ev["S"])[sc], np.asarray(ev["stratum"])[sc]
    info = mi_corrected(xs, ss, sts, n_perm=n_perm, rng=rng)
    val = did_value(ev["V"], ev["open"], sc, ev["stratum"], ev.get("V_pre"))
    cl = _codes(ev["cluster"])
    ncl = cl.max() + 1
    members = np.split(np.argsort(cl, kind="stable"), np.flatnonzero(np.diff(np.sort(cl))) + 1)
    Ib, Vb, Kb, Rb = [], [], [], []
    for _ in range(B):
        pick = rng.integers(0, ncl, size=ncl)
        idx = np.concatenate([members[j] for j in pick])
        # duplicated clusters keep their original stratum (fixed effects stay at the stratum level, as in the point
        # estimate; relabelling per copy would turn the stratum FE into cluster FE)
        st = np.asarray(ev["stratum"])[idx]
        scb = sc[idx]
        xb, sb = np.asarray(ev["X"])[idx][scb], np.asarray(ev["S"])[idx][scb]
        stb = np.asarray(ev["stratum"])[idx][scb]
        raw = mi_mm(xb, sb)
        fl = np.mean([mi_mm(xb, permute_within(sb, _codes(stb), rng)) for _ in range(n_perm_boot)])
        ib = raw - fl
        dvb = did_value(np.asarray(ev["V"])[idx], np.asarray(ev["open"])[idx], scb, st,
                        None if ev.get("V_pre") is None else np.asarray(ev["V_pre"])[idx])
        vb = dvb["dV"]
        Rb.append(dvb["dV_rel"])
        Ib.append(ib)
        Vb.append(vb)
    Ib, Vb = np.array(Ib), np.array(Vb)
    # duplicated clusters inflate plug-in MI in every draw: remove the bootstrap bias before intervals and ratios
    Ib = Ib - (np.nanmean(Ib) - info["I"])
    Kb = np.where(Ib > min_I, Vb / np.where(Ib > min_I, Ib, 1.0), np.nan)

    def ci(a):
        a = a[np.isfinite(a)]
        return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) > 10 else [None, None]

    kap = val["dV"] / info["I"] if info["I"] > min_I else float("nan")
    Vs = np.asarray(ev["V"], float)
    I_ci = ci(Ib)
    extra = {"identified": bool(I_ci[0] is not None and I_ci[0] > min_I_ident),
             "identified_rule": f"I_ci lower > {min_I_ident} bits (H87 A1)"}
    if jackknife:
        jk = mi_jackknife(xs, ss, sts, np.asarray(ev["cluster"])[sc], n_perm=n_perm_jk,
                          rng=np.random.default_rng([seed, 31337]))
        I_bc = info["I"] - jk["bias"]
        lo, hi = info["I"] - 1.96 * jk["se"], info["I"] + 1.96 * jk["se"]
        extra.update({"I_se_jk": jk["se"], "I_ci_jk": [float(lo), float(hi)],
                      "identified_jk": bool(np.isfinite(lo) and lo > min_I_ident),
                      "I_bc": float(I_bc), "I_ci_jk_bc": [float(I_bc - 1.96 * jk["se"]), float(I_bc + 1.96 * jk["se"])]})
    if len(xs):
        ncell = len(np.unique(_codes(xs) * (int(_codes(ss).max()) + 1) + _codes(ss)))
        extra["n_per_cell"] = float(len(xs) / ncell)
        extra["I_sparse"] = bool(len(xs) / ncell < SPARSE_PER_CELL)
    return {**info, "I_ci": I_ci, "I_se": float(np.nanstd(Ib)), **extra,
            "dV": val["dV"], "dV_ci": ci(Vb), "dV_se": float(np.nanstd(Vb)), "open_placebo": val["open_placebo"],
            "dV_rel": val["dV_rel"], "dV_rel_ci": ci(np.array(Rb)), "dV_rel_se": float(np.nanstd(Rb)),
            "kappa": float(kap), "kappa_ci": ci(Kb), "kappa_undefined_share": float(np.mean(~np.isfinite(Kb))),
            "V_mean_placebo": float(np.nanmean(Vs[~sc])) if (~sc).any() else float("nan"),
            "V_mean_scramble": float(np.nanmean(Vs[sc])),
            "open_share_scramble": float(np.mean(np.asarray(ev["open"], bool)[sc])),
            "open_share_placebo": float(np.mean(np.asarray(ev["open"], bool)[~sc])) if (~sc).any() else float("nan"),
            "n_scramble": int(sc.sum()), "n_placebo": int((~sc).sum()), "n_clusters": int(ncl), "B": B}


def dl_pool(est, se) -> dict:
    """DerSimonian-Laird random-effects pool of per-period estimates."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"est": float("nan"), "lo": float("nan"), "hi": float("nan"), "k": 0, "tau": float("nan")}
    w = 1 / se ** 2
    m = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - m) ** 2)
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - (len(est) - 1)) / c) if c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mm = np.sum(ws * est) / np.sum(ws)
    s = math.sqrt(1 / np.sum(ws))
    return {"est": float(mm), "lo": float(mm - 1.96 * s), "hi": float(mm + 1.96 * s), "se": float(s),
            "k": int(len(est)), "tau": float(math.sqrt(tau2))}


# ---------------------------------------------------------------------------------------------- self-check
def _synthetic(n_agents=12, n_per=300, K=5, p_ret=0.7, dv=0.0, read_bias=0.3, seed=1):
    """Agents with K repos; X = S (own repo) w.p. p_ret else a random repo; V ~ Poisson(2 * 0.7^scramble *
    (1 + read_bias*open) * (1 + dv*open*scramble)): a multiplicative world where the scramble lowers V and reading
    raises V in both arms. Returns the event frame and the planted I(X;S) within agent (bits)."""
    rng = np.random.default_rng(seed)
    rows = {k: [] for k in ("cluster", "stratum", "scramble", "X", "S", "open", "V", "V_pre")}
    for a in range(n_agents):
        for i in range(n_per):
            s = rng.integers(0, K) + 10 * a
            x = s if rng.random() < p_ret else rng.integers(0, K) + 10 * a
            sc = bool(i % 2)
            op = bool(rng.random() < 0.5)
            lam = 2.0 * (0.7 if sc else 1.0) * (1 + read_bias * op) * (1 + dv * (op and sc))
            v = float(rng.poisson(lam))
            for k, val in zip(rows, (f"{a}|{i // 20}", str(a), sc, x, s, op, v, rng.normal(2, 1))):
                rows[k].append(val)
    q = p_ret + (1 - p_ret) / K
    h_xs = -(q * math.log2(q) + (1 - q) * math.log2((1 - q) / (K - 1)))
    return {k: np.array(v) for k, v in rows.items()}, math.log2(K) - h_xs


def _synthetic_real(p_ret: float, seed: int, n_strata: int = 139, q0: float = 0.69, block: int = 8):
    """Information-only world at the real NE41 artifact-row counts (H70 F events with an artifact): 139 agent-period
    strata, lognormal sizes (median 48 erasures), 1-5 repos per stratum with skewed Dirichlet shares, X = -1 (no work
    commit; one shared code) w.p. q0 = 0.69, else X = S w.p. p_ret, else a draw from the stratum's repo shares;
    clusters = blocks of 8 consecutive events (agent-days). The design (sizes, repos, shares) is fixed across seeds.
    Returns (frame with scramble = True everywhere, exact target I = MI(X;S) - MI under within-stratum independence)."""
    def mi_tab(P):
        P = P / P.sum()
        px, ps = P.sum(1, keepdims=True), P.sum(0, keepdims=True)
        m = P > 0
        return float((P[m] * np.log2(P[m] / (px @ ps)[m])).sum())
    rng, design = np.random.default_rng(seed), np.random.default_rng(7)
    n = np.maximum(5, np.round(design.lognormal(math.log(48), 1.1, n_strata))).astype(int)
    Kw = design.choice([1, 2, 3, 4, 5], size=n_strata, p=[0.2, 0.3, 0.25, 0.15, 0.1])
    shares = [design.dirichlet(np.full(k, 0.7)) for k in Kw]
    off = np.concatenate([[0], np.cumsum(Kw)])
    P, Pci = np.zeros((off[-1] + 1, off[-1])), np.zeros((off[-1] + 1, off[-1]))
    X, S, st, cl = [], [], [], []
    for w in range(n_strata):
        pw, k = shares[w], Kw[w]
        joint = np.zeros((k + 1, k))
        joint[0] = q0 * pw
        joint[1:] = (1 - q0) * (p_ret * np.diag(pw) + (1 - p_ret) * np.outer(pw, pw))
        joint *= n[w] / n.sum()
        rows, cols = np.r_[0, 1 + off[w] + np.arange(k)], off[w] + np.arange(k)
        P[np.ix_(rows, cols)] += joint
        Pci[np.ix_(rows, cols)] += np.outer(joint.sum(1), joint.sum(0)) / joint.sum()
        s = rng.choice(k, size=n[w], p=pw)
        x = np.where(rng.random(n[w]) < q0, -1, np.where(rng.random(n[w]) < p_ret, s, rng.choice(k, size=n[w], p=pw)))
        X.append(np.where(x < 0, -1, x + 1000 * w))
        S.append(s + 1000 * w)
        st.append(np.full(n[w], w))
        cl.append(w * 10000 + np.arange(n[w]) // block)
    X, S, st, cl = map(np.concatenate, (X, S, st, cl))
    return {"X": X, "S": S, "stratum": st, "cluster": cl, "scramble": np.ones(len(X), bool)}, mi_tab(P) - mi_tab(Pci)


def _synthetic_sparse(p_ret: float, seed: int):
    """Sparse world: 12 agents x 60 events (30 scrambles), 20 repos each (< 1 scramble per joint cell)."""
    ev, true_I = _synthetic(n_agents=12, n_per=60, K=20, p_ret=p_ret, seed=seed)
    return ev, true_I


def info_intervals(ev: dict, n_perm: int = 30, B: int = 40, n_perm_boot: int = 4, seed: int = 0,
                   n_perm_jk: int = 20) -> dict:
    """The information part of kappa_row alone (same random stream for the bootstrap, so I and I_ci equal kappa_row's
    with the same arguments): the round-2 recentred percentile interval and the round-3 jackknife interval."""
    rng = np.random.default_rng(seed)
    sc = np.asarray(ev["scramble"], bool)
    X, S, ST = np.asarray(ev["X"]), np.asarray(ev["S"]), np.asarray(ev["stratum"])
    xs, ss, sts = X[sc], S[sc], ST[sc]
    info = mi_corrected(xs, ss, sts, n_perm=n_perm, rng=rng)
    cl = _codes(ev["cluster"])
    ncl = cl.max() + 1
    members = np.split(np.argsort(cl, kind="stable"), np.flatnonzero(np.diff(np.sort(cl))) + 1)
    Ib = []
    for _ in range(B):
        idx = np.concatenate([members[j] for j in rng.integers(0, ncl, size=ncl)])
        scb = sc[idx]
        xb, sb, stb = X[idx][scb], S[idx][scb], ST[idx][scb]
        Ib.append(mi_mm(xb, sb) - np.mean([mi_mm(xb, permute_within(sb, _codes(stb), rng)) for _ in range(n_perm_boot)]))
    Ib = np.array(Ib)
    Ib = Ib - (np.nanmean(Ib) - info["I"])
    jk = mi_jackknife(xs, ss, sts, np.asarray(ev["cluster"])[sc], n_perm=n_perm_jk,
                      rng=np.random.default_rng([seed, 31337]))
    I_bc = info["I"] - jk["bias"]
    ncell = len(np.unique(_codes(xs) * (int(_codes(ss).max()) + 1) + _codes(ss)))
    return {"I": info["I"], "I_ci": [float(np.percentile(Ib, 2.5)), float(np.percentile(Ib, 97.5))],
            "I_bc": I_bc, "I_ci_jk_bc": [I_bc - 1.96 * jk["se"], I_bc + 1.96 * jk["se"]], "I_se_jk": jk["se"],
            "I_ci_jk": [info["I"] - 1.96 * jk["se"], info["I"] + 1.96 * jk["se"]],
            "I_se_boot": float(Ib.std()), "n_per_cell": len(xs) / ncell}


def coverage(reps: int = 100, reps_real: int = 60, B: int = 40, out: Path | None = None) -> dict:
    """Coverage of the nominal 95% information intervals, old (bootstrap, recentred percentile) vs new (jackknife),
    in three synthetic worlds: dense (the self-check world, K = 5 repos, 150 scrambles per agent), real counts
    (_synthetic_real) and sparse (_synthetic_sparse). Slow at real counts (~3 min per level at B = 40)."""
    worlds = [("dense", lambda p, s: _synthetic(p_ret=p, seed=s), (0.0, 0.3, 0.7), reps),
              ("real_counts", _synthetic_real, (0.0, 0.1, 0.3, 0.6), reps_real),
              ("sparse", _synthetic_sparse, (0.0, 0.3, 0.7), reps)]
    res = {"B": B, "n_perm": 30, "n_perm_boot": 4, "n_perm_jk": 20, "worlds": {}}
    for name, gen, levels, R in worlds:
        for p in levels:
            rec = []
            for k in range(R):
                ev, true_I = gen(p, 5000 + k)
                r = info_intervals(ev, B=B, seed=k)
                rec.append((r["I"], r["I_bc"], r["I_ci"][0] <= true_I <= r["I_ci"][1],
                            r["I_ci_jk"][0] <= true_I <= r["I_ci_jk"][1], r["I_se_boot"], r["I_se_jk"],
                            r["n_per_cell"], r["I_ci_jk_bc"][0] <= true_I <= r["I_ci_jk_bc"][1]))
            a = np.array(rec, float)
            row = {"true_I": true_I, "reps": R, "bias_I": float(a[:, 0].mean() - true_I), "sd_I": float(a[:, 0].std()),
                   "bias_I_bc": float(a[:, 1].mean() - true_I), "cov_old": float(a[:, 2].mean()),
                   "cov_jk": float(a[:, 3].mean()), "cov_jk_bc": float(a[:, 7].mean()), "se_boot": float(a[:, 4].mean()), "se_jk": float(a[:, 5].mean()),
                   "n_per_cell": float(a[:, 6].mean())}
            res["worlds"][f"{name}_p{p}"] = row
            print(f"{name:12s} p_ret {p}: true I {true_I:.4f} bias {row['bias_I']:+.4f} (jk-corrected "
                  f"{row['bias_I_bc']:+.4f}) sd {row['sd_I']:.4f} | coverage old {row['cov_old']:.3f} jk "
                  f"{row['cov_jk']:.3f} jk_bc {row['cov_jk_bc']:.3f} | se boot {row['se_boot']:.4f} jk {row['se_jk']:.4f} | "
                  f"{row['n_per_cell']:.1f} per cell", flush=True)
    if out is not None:
        out.write_text(json.dumps(res, indent=1))
    return res


def _round2_module():
    """The round-2 semantic_kappa (git c14110f), loaded read-only, to show the old fields are unchanged."""
    import importlib.util
    import subprocess
    import tempfile
    root = Path(__file__).resolve().parents[2]
    src = subprocess.run(["git", "-C", str(root), "show", "c14110f:infra/shared/semantic_kappa.py"],
                         capture_output=True, text=True, check=True).stdout
    tmp = Path(tempfile.mkdtemp()) / "semantic_kappa_round2.py"
    tmp.write_text(src)
    spec = importlib.util.spec_from_file_location("semantic_kappa_round2", tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify(reps: int = 20) -> bool:
    """(1) Planted bits and planted DiD over `reps` seeds (round-2 check, unchanged thresholds): |bias| < 0.05; coverage
    >= 0.7 (I, B = 40) and >= 0.8 (dV); the jackknife interval is reported next to it. (2) Every round-2 field of
    kappa_row is bit-identical to the round-2 module (git c14110f) on 3 synthetic frames. (3) `identified` follows A1."""
    ok = True
    for p_ret, dv in ((0.0, 0.0), (0.7, 0.0), (0.7, 0.5)):
        I_hat, V_hat, cI, cJ, cV = [], [], 0, 0, 0
        for k in range(reps):
            ev, true_I = _synthetic(p_ret=p_ret, dv=dv, seed=100 + k)
            r = kappa_row(ev, n_perm=30, B=40, n_perm_boot=4, seed=k)
            I_hat.append(r["I"])
            V_hat.append(r["dV_rel"])
            cI += r["I_ci"][0] <= true_I <= r["I_ci"][1]
            cJ += r["I_ci_jk"][0] <= true_I <= r["I_ci_jk"][1]
            cV += r["dV_rel_ci"][0] <= dv <= r["dV_rel_ci"][1]
            ok &= r["identified"] == bool(r["I_ci"][0] is not None and r["I_ci"][0] > MIN_I_IDENT)
        bI, bV = np.mean(I_hat) - true_I, np.mean(V_hat) - dv
        good = abs(bI) < 0.05 and abs(bV) < 0.05 and cI / reps >= 0.7 and cV / reps >= 0.8
        print(f"planted I {true_I:.3f}: bias {bI:+.3f}, coverage {cI / reps:.2f} (jackknife {cJ / reps:.2f}) | planted "
              f"relative dV {dv}: bias {bV:+.3f}, coverage {cV / reps:.2f} (reading x1.3 in both arms, scramble x0.7) "
              f"{'OK' if good else 'FAIL'}")
        ok &= good
    try:
        old = _round2_module()
    except Exception as e:  # noqa: BLE001
        print("round-2 module not available:", e)
        return False
    same = True
    for k, (p_ret, dv) in enumerate(((0.0, 0.0), (0.3, 0.2), (0.7, 0.5))):
        ev, _ = _synthetic(p_ret=p_ret, dv=dv, seed=900 + k)
        a = old.kappa_row(ev, n_perm=30, B=30, n_perm_boot=4, seed=k)
        b = kappa_row(ev, n_perm=30, B=30, n_perm_boot=4, seed=k)
        same &= all(json.dumps(a[key]) == json.dumps(b[key]) for key in a)
    print(f"round-2 fields bit-identical to git c14110f on 3 frames: {same}")
    return bool(ok and same)


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    if "--coverage" in sys.argv:
        out = Path(__file__).resolve().parents[1] / "data-quality/semantic_kappa_coverage.json"
        coverage(out=out)
        print("->", out)
        sys.exit(0)
    print(__doc__)
