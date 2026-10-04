"""H18 fitting library: uptake models for pending messages, with agent x day propensities.

Model (card, "Uptake model"): P(r_{tau j} = 1) = 1 - exp(-theta_c * S_u), S_u = sum over j's pending messages of h_m,
c = agent x day cluster, log theta_c ridge-penalized toward the period mean (sigma = 1.5). Fitted by profile
likelihood: an inner vectorized Newton solves every log theta_c given the shape parameters; an outer bounded
L-BFGS-B (finite differences) optimizes the 1-3 shape parameters.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import numpy as np
import polars as pl
from scipy.optimize import minimize

SIGMA_U = 1.5      # ridge on log theta_c around the period mean
SIGMA_G = 3.0      # weak ridge on the mention log-factor gamma (keeps it finite when no mention units)
K_BINS = [(1, 1), (2, 2), (3, 4), (5, 8), (9, 16), (17, 32), (33, 64), (65, 10**9)]
K_LABELS = ["1", "2", "3-4", "5-8", "9-16", "17-32", "33-64", "65+"]


# ----------------------------------------------------------------------------------------------- data
class Units:
    """Scored (event, sender) units with their per-message detail."""

    def __init__(self, ev: pl.DataFrame, pend: pl.DataFrame, id_col: str, resp_col: str = "resp"):
        """ev: talks or wakes (id_col, agent, pt_date, k, block); pend: pending rows (id_col, sender, rank, ment_i,
        scored, resp...)."""
        p = pend.filter(pl.col("scored")).join(ev.select(id_col, "agent", "pt_date", "k", "block"), on=id_col)
        p = p.sort(id_col, "sender", "rank")
        u = (p.group_by([id_col, "sender"], maintain_order=True)
             .agg(pl.col("agent").first(), pl.col("pt_date").first(), pl.col("k").first(), pl.col("block").first(),
                  pl.col(resp_col).max().alias("r"), (~pl.col("ment_i")).sum().alias("n0"),
                  pl.col("ment_i").sum().alias("nM"), pl.len().alias("nj"), pl.col("rank").min().alias("rmin")))
        u = u.with_row_index("uid")
        p = p.join(u.select(id_col, "sender", "uid"), on=[id_col, "sender"])
        self.df = u
        self.r = u["r"].cast(pl.Float64).to_numpy()
        self.k = u["k"].cast(pl.Float64).to_numpy()
        self.n0 = u["n0"].cast(pl.Float64).to_numpy()
        self.nM = u["nM"].cast(pl.Float64).to_numpy()
        self.nj = u["nj"].to_numpy()
        self.block = u["block"].to_numpy()
        days = u["pt_date"].to_numpy()
        self.days = np.unique(days)
        self.day = np.searchsorted(self.days, days)
        agents = u["agent"].to_numpy()
        self.agent = agents
        key = agents.astype(np.int64) * 10000 + self.day
        self.ckeys, self.c = np.unique(key, return_inverse=True)
        self.ac_keys, self.ac = np.unique(agents, return_inverse=True)   # agent-only clusters
        self.m_uid = p["uid"].to_numpy()
        self.m_rank = p["rank"].cast(pl.Float64).to_numpy()
        self.m_ment = p["ment_i"].cast(pl.Float64).to_numpy()
        self.n = len(self.r)
        self.n_mention_units = int((self.nM > 0).sum())
        self.eng = np.zeros(self.n)

    def subset(self, mask: np.ndarray) -> "Units":
        s = object.__new__(Units)
        idx = np.where(mask)[0]
        remap = -np.ones(self.n, dtype=np.int64)
        remap[idx] = np.arange(len(idx))
        mm = remap[self.m_uid] >= 0
        for a in ("r", "k", "n0", "nM", "nj", "block", "day", "agent", "c", "ac", "eng"):
            setattr(s, a, getattr(self, a)[idx])
        s.days, s.ckeys, s.ac_keys = self.days, self.ckeys, self.ac_keys
        s.m_uid, s.m_rank, s.m_ment = remap[self.m_uid[mm]], self.m_rank[mm], self.m_ment[mm]
        s.n = len(idx)
        s.n_mention_units = int((s.nM > 0).sum())
        s.df = None
        return s

    def resample_days(self, rng, with_messages: bool = False) -> "Units":
        """Day-level bootstrap: duplicated days become distinct clusters."""
        nd = len(self.days)
        draw = rng.integers(nd, size=nd)
        by_day = [np.where(self.day == d)[0] for d in range(nd)]
        parts, cl = [], []
        for i, d in enumerate(draw):
            parts.append(by_day[d])
            cl.append(np.full(len(by_day[d]), i))
        idx = np.concatenate(parts)
        rep = np.concatenate(cl)
        s = object.__new__(Units)
        for a in ("r", "k", "n0", "nM", "nj", "block", "agent", "ac", "eng"):
            setattr(s, a, getattr(self, a)[idx])
        s.day = rep
        s.days = np.arange(nd)
        key = s.agent.astype(np.int64) * 10000 + rep
        s.ckeys, s.c = np.unique(key, return_inverse=True)
        s.ac_keys = self.ac_keys
        # messages: expand (m_uid is sorted, so each unit's messages are contiguous)
        if with_messages:
            starts = np.searchsorted(self.m_uid, np.arange(self.n))
            lens = np.searchsorted(self.m_uid, np.arange(self.n), side="right") - starts
            L = lens[idx]
            tot = int(L.sum())
            offs = np.cumsum(L) - L
            sel = np.arange(tot) - np.repeat(offs, L) + np.repeat(starts[idx], L)
            s.m_uid = np.repeat(np.arange(len(idx)), L)
            s.m_rank, s.m_ment = self.m_rank[sel], self.m_ment[sel]
        else:
            s.m_uid = s.m_rank = s.m_ment = np.zeros(0)
        s.n = len(idx)
        s.n_mention_units = int((s.nM > 0).sum())
        s.df = None
        return s


# ----------------------------------------------------------------------------------------------- models
def _sig(x):
    return 1.0 / (1.0 + math.exp(-x))


MODELS = {
    # name: (param names, initial, bounds)
    "const": (["g"], [1.0], [(-6, 6)]),
    "inv": (["g"], [1.0], [(-6, 6)]),
    "sat": (["g", "logk0"], [1.0, 0.5], [(-6, 6), (-6, 6)]),
    "pow": (["g", "beta"], [1.0, 0.5], [(-6, 6), (-2, 3)]),
    "rec": (["g", "lrho"], [1.0, 1.0], [(-6, 6), (-6, 8)]),
    "recbud": (["g", "lrho"], [1.0, 1.0], [(-6, 6), (-6, 8)]),
    "bypass": (["g", "beta", "betaM"], [1.0, 0.5, 0.5], [(-6, 6), (-2, 3), (-2, 3)]),
    # post-hoc (2026-10-03, after the placebo diagnostic): engagement = i mentioned j at its previous talk turn
    "pow_eng": (["g", "beta", "delta"], [1.0, 0.5, 1.0], [(-6, 6), (-2, 3), (-6, 6)]),
    "const_eng": (["g", "delta"], [1.0, 1.0], [(-6, 6), (-6, 6)]),
    # post-hoc (2026-10-03): recency x saturating k, independent rho and k0 (does k matter at fixed rank?)
    "recsat": (["g", "lrho", "logk0"], [1.0, 1.0, 0.5], [(-6, 6), (-6, 8), (-6, 6)]),
}


def shape(model: str, th, U: Units) -> np.ndarray:
    g = th[0]
    eg = math.exp(g)
    w = U.n0 + eg * U.nM
    if model == "const":
        return w
    if model == "inv":
        return w / U.k
    if model == "sat":
        k0 = math.exp(th[1])
        return w * (1 + k0) / (k0 + U.k)
    if model == "pow":
        return w * U.k ** (-th[1])
    if model == "bypass":
        return U.n0 * U.k ** (-th[1]) + eg * U.nM * U.k ** (-th[2])
    if model == "pow_eng":
        return w * U.k ** (-th[1]) * np.exp(th[2] * U.eng)
    if model == "const_eng":
        return w * np.exp(th[1] * U.eng)
    rho = _sig(th[1])
    mw = rho ** (U.m_rank - 1.0) * np.where(U.m_ment > 0, eg, 1.0)
    s = np.bincount(U.m_uid, weights=mw, minlength=U.n)
    if model == "rec":
        return s
    if model == "recsat":
        k0 = math.exp(th[2])
        return s * (1 + k0) / (k0 + U.k)
    if model == "recbud":
        Z = (1 - rho ** U.k) / (1 - rho) if rho < 1 - 1e-12 else U.k
        return s / Z
    raise ValueError(model)


def _ll_terms(lam, r):
    lam = np.maximum(lam, 1e-300)
    return r * np.log(-np.expm1(-lam)) - (1 - r) * lam


def inner(S, r, c, nc, u0=None, iters=60):
    """Newton for log theta_c given S (vectorized over clusters). Returns u, mu, penalized loglik."""
    u = np.zeros(nc) if u0 is None else u0.copy()
    mu = u.mean() if u0 is not None else math.log(max(1e-6, r.mean()) / max(1e-9, np.mean(S)))
    if u0 is None:
        u[:] = mu
    inv_s2 = 1.0 / SIGMA_U ** 2
    for _ in range(iters):
        lam = np.exp(u[c]) * S
        lam = np.maximum(lam, 1e-300)
        A = np.where(lam > 1e-8, lam / np.expm1(lam), 1.0 - lam / 2)
        B = np.where(lam > 1e-8, lam / -np.expm1(-lam), 1.0 + lam / 2)
        gu = r * A - (1 - r) * lam
        hu = r * A * (1 - B) - (1 - r) * lam
        g = np.bincount(c, weights=gu, minlength=nc) - (u - mu) * inv_s2
        h = np.bincount(c, weights=hu, minlength=nc) - inv_s2
        step = np.clip(-g / h, -3, 3)
        u = u + step
        mu = u.mean()
        if np.max(np.abs(step)) < 1e-7:
            break
    lam = np.exp(u[c]) * S
    ll = _ll_terms(lam, r).sum() - 0.5 * inv_s2 * ((u - mu) ** 2).sum()
    return u, mu, ll


def fit(model: str, U: Units, cluster: str = "agentday", start=None):
    names, init, bounds = MODELS[model]
    c = U.c if cluster == "agentday" else U.ac
    nc = int(c.max()) + 1 if len(c) else 0
    state = {"u": None}

    def negpl(th):
        S = shape(model, th, U)
        S = np.maximum(S, 1e-300)
        u, mu, ll = inner(S, U.r, c, nc, state["u"])
        state["u"], state["mu"] = u, mu
        return -(ll - 0.5 * th[0] ** 2 / SIGMA_G ** 2)

    x0 = np.array(start if start is not None else init, dtype=float)
    best = None
    for x in [x0] + ([np.array(init, float)] if start is not None else []):
        res = minimize(negpl, x, method="L-BFGS-B", bounds=bounds, options={"maxiter": 200})
        if best is None or res.fun < best.fun:
            best = res
    S = np.maximum(shape(model, best.x, U), 1e-300)
    u, mu, ll = inner(S, U.r, c, nc, None)
    out = dict(model=model, params=dict(zip(names, map(float, best.x))), ll=float(_ll_terms(np.exp(u[c]) * S, U.r).sum()),
               pll=float(-best.fun), n=int(U.n), k_params=len(names), u=u, mu=float(mu), cluster=cluster)
    out["aic"] = 2 * out["k_params"] - 2 * out["ll"]
    return out


def predict(model: str, fitres: dict, U: Units, cluster_keys_train, U_test: Units) -> np.ndarray:
    """P(r=1) for test units, using the training propensities (period mean for unseen clusters)."""
    th = [fitres["params"][n] for n in MODELS[model][0]]
    S = np.maximum(shape(model, th, U_test), 1e-300)
    if fitres["cluster"] == "agentday":
        keys_test = U_test.ckeys[U_test.c]
    else:
        keys_test = U_test.ac_keys[U_test.ac]
    pos = np.searchsorted(cluster_keys_train, keys_test)
    pos = np.clip(pos, 0, len(cluster_keys_train) - 1)
    found = cluster_keys_train[pos] == keys_test
    u = np.where(found, fitres["u_full"][pos], fitres["mu"])
    lam = np.exp(u) * S
    return -np.expm1(-lam)


def cv(models, U: Units, scheme: str = "block", n_folds_day: int = 5, seed: int = 0):
    """Held-out log-likelihood per unit. scheme 'block': within-day time blocks (agent x day propensities);
    'day': day-blocked folds (agent propensities). Returns {model: per-unit held-out ll array}."""
    if scheme == "block":
        folds = U.block.copy()
        cluster = "agentday"
    else:
        rng = np.random.default_rng(seed)
        perm = rng.permutation(len(U.days))
        dfold = np.empty(len(U.days), dtype=int)
        dfold[perm] = np.arange(len(U.days)) % min(n_folds_day, len(U.days))
        folds = dfold[U.day]
        cluster = "agent"
    out = {m: np.full(U.n, np.nan) for m in models}
    for f in np.unique(folds):
        tr, te = folds != f, folds == f
        if tr.sum() < 20 or te.sum() == 0:
            continue
        Utr, Ute = U.subset(tr), U.subset(te)
        # remap train clusters to their global keys
        keys_all = U.ckeys if cluster == "agentday" else U.ac_keys
        ctr = Utr.c if cluster == "agentday" else Utr.ac
        uniq = np.unique(ctr)
        remap = -np.ones(int(ctr.max()) + 1, dtype=np.int64)
        remap[uniq] = np.arange(len(uniq))
        if cluster == "agentday":
            Utr.c = remap[Utr.c]
        else:
            Utr.ac = remap[Utr.ac]
        keys_train = keys_all[uniq]
        for m in models:
            fr = fit(m, Utr, cluster=cluster)
            fr["u_full"] = fr["u"]
            p = predict(m, fr, Utr, keys_train, Ute)
            p = np.clip(p, 1e-12, 1 - 1e-12)
            out[m][te] = Ute.r * np.log(p) + (1 - Ute.r) * np.log(1 - p)
    return out


def paired_day_boot(ll_a, ll_b, day, B=1000, seed=1):
    """Bootstrap over days of the per-unit mean difference ll_a - ll_b; returns (mean, lo, hi, frac>0)."""
    ok = ~np.isnan(ll_a) & ~np.isnan(ll_b)
    d = (ll_a - ll_b)[ok]
    dd = day[ok]
    days = np.unique(dd)
    sums = np.array([d[dd == x].sum() for x in days])
    cnts = np.array([(dd == x).sum() for x in days])
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        i = rng.integers(len(days), size=len(days))
        bs.append(sums[i].sum() / max(1, cnts[i].sum()))
    bs = np.array(bs)
    return float(d.mean()), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975)), float((bs > 0).mean())


# ----------------------------------------------------------------------------------------------- S elasticity
def s_elasticity(S: np.ndarray, k: np.ndarray, c: np.ndarray):
    """Poisson regression log E[S] = u_c + eps * log k with ridge-penalized agent x day effects. Returns eps."""
    x = np.log(k.astype(float))
    nc = int(c.max()) + 1
    inv_s2 = 1 / SIGMA_U ** 2

    def prof(eps):
        u = np.full(nc, math.log(max(S.mean(), 1e-3)))
        mu = u.mean()
        for _ in range(60):
            m = np.exp(u[c] + eps * x)
            g = np.bincount(c, weights=S - m, minlength=nc) - (u - mu) * inv_s2
            h = -np.bincount(c, weights=m, minlength=nc) - inv_s2
            st = np.clip(-g / h, -3, 3)
            u += st
            mu = u.mean()
            if np.abs(st).max() < 1e-8:
                break
        m = np.exp(u[c] + eps * x)
        return -(np.sum(S * np.log(np.maximum(m, 1e-300)) - m) - 0.5 * inv_s2 * ((u - mu) ** 2).sum())

    res = minimize(lambda e: prof(e[0]), [0.3], method="L-BFGS-B", bounds=[(-3, 3)])
    return float(res.x[0])


def kbin(k):
    k = np.asarray(k)
    out = np.full(k.shape, -1)
    for i, (lo, hi) in enumerate(K_BINS):
        out[(k >= lo) & (k <= hi)] = i
    return out
