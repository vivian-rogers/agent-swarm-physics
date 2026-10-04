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

Self-check: uv run python infra/shared/semantic_kappa.py --verify   (planted bits and planted DiD recovered)
"""
from __future__ import annotations

import math
import sys

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
def kappa_row(ev: dict, n_perm: int = 200, B: int = 300, n_perm_boot: int = 10, seed: int = 0,
              min_I: float = 0.02) -> dict:
    """One channel's row. ev: dict of numpy arrays with the module-docstring columns.

    Information is computed on scramble events only; the value on scramble + placebo events. Bootstrap: clusters
    resampled with replacement (the same draws for I and dV), with the permutation floor recomputed per draw."""
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
    return {**info, "I_ci": ci(Ib), "I_se": float(np.nanstd(Ib)),
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


def verify(reps: int = 20) -> bool:
    """Planted bits and planted DiD over `reps` seeds: |bias| < 0.05; coverage >= 0.7 (I, B = 40) and >= 0.8 (dV)."""
    ok = True
    for p_ret, dv in ((0.0, 0.0), (0.7, 0.0), (0.7, 0.5)):
        I_hat, V_hat, cI, cV = [], [], 0, 0
        for k in range(reps):
            ev, true_I = _synthetic(p_ret=p_ret, dv=dv, seed=100 + k)
            r = kappa_row(ev, n_perm=30, B=40, n_perm_boot=4, seed=k)
            I_hat.append(r["I"])
            V_hat.append(r["dV_rel"])
            cI += r["I_ci"][0] <= true_I <= r["I_ci"][1]
            cV += r["dV_rel_ci"][0] <= dv <= r["dV_rel_ci"][1]
        bI, bV = np.mean(I_hat) - true_I, np.mean(V_hat) - dv
        good = abs(bI) < 0.05 and abs(bV) < 0.05 and cI / reps >= 0.7 and cV / reps >= 0.8
        print(f"planted I {true_I:.3f}: bias {bI:+.3f}, coverage {cI / reps:.2f} | planted relative dV {dv}: bias "
              f"{bV:+.3f}, coverage {cV / reps:.2f} (reading x1.3 in both arms, scramble x0.7) {'OK' if good else 'FAIL'}")
        ok &= good
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    print(__doc__)
