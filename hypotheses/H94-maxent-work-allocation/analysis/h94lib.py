"""H94 estimators: max-ent (log-linear) allocation hierarchy on agent x repo quantum tables, KL in bits, floors
(Patefield / parametric / run-preserving persistence), agent-block bootstrap of prices, BE vs MB concentration kappa,
and unfitted cell signatures (breadth, reach, singleton repos)."""
from __future__ import annotations

import math

import numpy as np
import polars as pl
from scipy.stats import random_table

LN2 = math.log(2)
CAP = 20.0


# ================================================================================================ tables
def unit_table(q: pl.DataFrame, own_col: str = "own", labs: dict | None = None):
    """Counts n (A x J), indicators own, room, lab, named (J), agents, repos, and runs (list of (agent_idx, [repo per
    quantum ordered by time]) per agent-day) for one unit's quanta rows."""
    agents = sorted(q["agent"].unique().to_list())
    repos = sorted(q["repo"].unique().to_list())
    ai = {a: k for k, a in enumerate(agents)}
    rj = {r: k for k, r in enumerate(repos)}
    A, J = len(agents), len(repos)
    n = np.zeros((A, J))
    own = np.zeros((A, J))
    room = np.zeros((A, J))
    lab = np.zeros((A, J))
    for a, r, sl in q.select("agent", "repo", "same_lab").iter_rows():
        n[ai[a], rj[r]] += 1
        lab[ai[a], rj[r]] = max(lab[ai[a], rj[r]], float(sl))
    ocol = "owner" if own_col == "own" else "owner_period"
    ow = dict(q.select("repo", ocol).unique(subset="repo").iter_rows())
    orm = dict(q.select("repo", "owner_room").unique(subset="repo").iter_rows())
    am = dict(q.select("agent", "room_mode").unique(subset="agent").iter_rows())
    for r, j in rj.items():
        if ow.get(r) in ai:
            own[ai[ow[r]], j] = 1.0
        for a, i in ai.items():
            if orm.get(r) is not None and am.get(a) is not None and orm[r] == am[a]:
                room[i, j] = 1.0
            if labs is not None and ow.get(r) is not None and labs.get(a) is not None and labs.get(a) == labs.get(ow[r]):
                lab[i, j] = 1.0
    named = np.array([bool(v) for v in q.select("repo", "named").unique(subset="repo").sort("repo")["named"].to_list()])
    runs = []
    for (a, d), g in q.sort("agent", "pt_date", "win").group_by(["agent", "pt_date"], maintain_order=True):
        seq = [rj[r] for r in g["repo"].to_list()]
        rl = []
        for j in seq:
            if rl and rl[-1][0] == j:
                rl[-1][1] += 1
            else:
                rl.append([j, 1])
        runs.append((ai[a], rl))
    return {"n": n, "own": own, "room": room, "lab": lab, "named": named, "agents": agents, "repos": repos, "runs": runs}


# ================================================================================================ max-ent fits
def fit_maxent(n: np.ndarray, feats: list[np.ndarray], tol=1e-9, max_iter=3000, init: np.ndarray | None = None):
    """Log-linear max-ent model with row and column margins and binary features, mu = exp(a_i + b_j + sum l_k f_k),
    fitted by iterative proportional fitting on the margins and on each feature's {f = 1, f = 0} partition (the MLE of
    the exponential family). A warm start from a nested model's solution makes the fitted KL monotone along the
    hierarchy. lambdas (nats) are read off log mu by least squares; |lambda| is capped at CAP for display (a cap means
    quasi-separation: the constraint is (nearly) deterministic)."""
    A, J = n.shape
    N = n.sum()
    r = n.sum(1)
    c = n.sum(0)
    mu = np.full((A, J), N / (A * J)) if init is None else init.astype(float).copy()
    T = [(float((f * n).sum()), f > 0) for f in feats]
    for it in range(max_iter):
        mu *= (r / np.maximum(mu.sum(1), 1e-300))[:, None]
        mu *= (c / np.maximum(mu.sum(0), 1e-300))[None, :]
        for t1, m in T:
            f1 = float(mu[m].sum())
            f0 = float(mu.sum()) - f1
            s1 = max(t1, 1e-12 * N) / max(f1, 1e-300)
            s0 = max(N - t1, 1e-12 * N) / max(f0, 1e-300)
            mu = np.where(m, mu * s1, mu * s0)
        if it % 10 == 0:
            err = max(np.abs(mu.sum(1) - r).max(), np.abs(mu.sum(0) - c).max(),
                      max([abs(float(mu[m].sum()) - t1) for t1, m in T], default=0.0))
            if err < tol * max(N, 1):
                break
    lam = np.zeros(len(feats))
    if feats:
        ok = mu.ravel() > 1e-200
        X = np.zeros((A * J, A + J + len(feats)))
        ii, jj = np.divmod(np.arange(A * J), J)
        X[np.arange(A * J), ii] = 1
        X[np.arange(A * J), A + jj] = 1
        for k, f in enumerate(feats):
            X[:, A + J + k] = f.ravel()
        sol = np.linalg.lstsq(X[ok], np.log(mu.ravel()[ok]), rcond=None)[0]
        lam = np.clip(sol[A + J:], -CAP, CAP)
    return mu, lam


def kl_bits(n: np.ndarray, mu: np.ndarray) -> float:
    N = n.sum()
    m = n > 0
    p = n[m] / N
    qm = mu[m] / mu.sum()
    return float((p * np.log(p / qm)).sum() / LN2)


def hierarchy(t: dict, two_rooms: bool) -> dict:
    n = t["n"]
    N = n.sum()
    A, J = n.shape
    out = {"N": float(N), "A": A, "J": J}
    mu0 = np.full_like(n, N / (A * J))
    out["D0"] = kl_bits(n, mu0)
    mu1, _ = fit_maxent(n, [])
    out["D1"] = kl_bits(n, mu1)
    mu2, l2 = fit_maxent(n, [t["own"]], init=mu1)
    out["D2"] = kl_bits(n, mu2)
    out["lam_own"] = float(l2[0])
    if two_rooms and t["room"].std() > 0:
        mu3, l3 = fit_maxent(n, [t["own"], t["room"]], init=mu2)
        out["D3"] = kl_bits(n, mu3)
        out["lam_room"] = float(l3[1])
        out["lam_own3"] = float(l3[0])
    else:
        mu3 = mu2
        out["D3"] = out["D2"]
        out["lam_room"] = None
    mul, ll = fit_maxent(n, [t["own"], t["lab"]], init=mu2) if t["lab"].std() > 0 else (mu2, [l2[0], 0.0])
    out["D2_lab"] = kl_bits(n, mul)
    out["lam_lab"] = float(ll[1])
    out["_mu"] = {"M1": mu1, "M2": mu2, "M3": mu3}
    return out


# ================================================================================================ floors
def patefield_floor(n, draws=200, rng=None):
    rng = rng or np.random.default_rng(0)
    r = n.sum(1).astype(int)
    c = n.sum(0).astype(int)
    rt = random_table(r, c, seed=rng)
    vals = []
    for _ in range(draws):
        x = rt.rvs().astype(float)
        mu, _ = fit_maxent(x, [], max_iter=50)
        vals.append(kl_bits(x, mu))
    return float(np.mean(vals)), float(np.quantile(vals, 0.95))


def _refit_D(x, t, level, two_rooms):
    feats = [] if level == 1 else ([t["own"]] if (level == 2 or not two_rooms) else [t["own"], t["room"]])
    keep_r = x.sum(1) > 0
    keep_c = x.sum(0) > 0
    xs = x[np.ix_(keep_r, keep_c)]
    fs = [f[np.ix_(keep_r, keep_c)] for f in feats]
    mu, lam = fit_maxent(xs, fs, max_iter=1000)
    return kl_bits(xs, mu), (float(lam[0]) if len(lam) else None)


def parametric_floor(mu, t, level, two_rooms, draws=200, rng=None):
    rng = rng or np.random.default_rng(1)
    N = int(round(mu.sum()))
    p = (mu / mu.sum()).ravel()
    vals = []
    for _ in range(draws):
        x = rng.multinomial(N, p).reshape(mu.shape).astype(float)
        vals.append(_refit_D(x, t, level, two_rooms)[0])
    return float(np.mean(vals)), float(np.quantile(vals, 0.95))


def persistence_floor(mu, t, level, two_rooms, draws=200, rng=None):
    """Run-preserving null: every run of consecutive same-repo quanta in an agent-day keeps its length; its repo is
    drawn from the fitted max-ent row conditional P_k(j | i)."""
    rng = rng or np.random.default_rng(2)
    P = mu / mu.sum(1, keepdims=True)
    cum = np.cumsum(P, 1)
    vals = []
    A, J = mu.shape
    for _ in range(draws):
        x = np.zeros((A, J))
        for i, rl in t["runs"]:
            u = rng.random(len(rl))
            js = np.minimum(np.searchsorted(cum[i], u * cum[i, -1]), J - 1)
            for (_, L), j in zip(rl, js):
                x[i, j] += L
        vals.append(_refit_D(x, t, level, two_rooms)[0])
    return float(np.mean(vals)), float(np.quantile(vals, 0.95))


def persistence_signatures(mu, t, draws=200, rng=None):
    """Breadth, top-3 reach and singleton repos expected under the run-preserving null with row conditionals from mu
    (A1: the analytic signatures assume independent quanta and read run clumping as specialization)."""
    rng = rng or np.random.default_rng(5)
    n = t["n"]
    A, J = n.shape
    P = mu / mu.sum(1, keepdims=True)
    cum = np.cumsum(P, 1)
    br = np.zeros(A)
    sing = []
    top = np.argsort(-n.sum(0))[: max(1, min(3, J))]
    reach_top = []
    for _ in range(draws):
        x = np.zeros((A, J))
        for i, rl in t["runs"]:
            u = rng.random(len(rl))
            js = np.minimum(np.searchsorted(cum[i], u * cum[i, -1]), J - 1)
            for (_, L), j in zip(rl, js):
                x[i, j] += L
        br += (x > 0).sum(1)
        sing.append(int(((x > 0).sum(0) == 1).sum()))
        reach_top.append(float((x[:, top] > 0).sum()))
    br /= draws
    obs_b = (n > 0).sum(1)
    return {"breadth_ratio_persist": float(np.mean(obs_b / np.maximum(br, 1e-12))),
            "singletons_persist": float(np.mean(sing)),
            "reach_top3_ratio_persist": float((n[:, top] > 0).sum() / max(np.mean(reach_top), 1e-12))}


def agent_bootstrap_lambda(t, draws=200, rng=None, feats_key=("own",)):
    rng = rng or np.random.default_rng(3)
    n = t["n"]
    A = n.shape[0]
    vals = []
    for _ in range(draws):
        idx = rng.integers(0, A, A)
        x = n[idx]
        fs = [t[k][idx] for k in feats_key]
        keep_c = x.sum(0) > 0
        x = x[:, keep_c]
        fs = [f[:, keep_c] for f in fs]
        if any(f.std() == 0 for f in fs):
            continue
        _, lam = fit_maxent(x, fs, max_iter=1000)
        vals.append(float(lam[0]))
    if not vals:
        return None, None
    return float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))


# ================================================================================================ concentration
def entropy_bits(c):
    c = np.asarray(c, float)
    c = c[c > 0]
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def kappa(c, draws=500, rng=None):
    """kappa = (H_MB - H_obs)/(H_MB - H_BE) at the observed K repos (all nonempty) and N quanta."""
    rng = rng or np.random.default_rng(4)
    c = np.asarray([x for x in c if x > 0], float)
    K = len(c)
    N = int(c.sum())
    if K < 3 or N <= K + 2:
        return {"kappa": None, "K": K, "N": N}
    hmb, hbe = [], []
    for _ in range(draws):
        hmb.append(entropy_bits(1 + rng.multinomial(N - K, np.full(K, 1 / K))))
        cuts = np.sort(rng.choice(np.arange(1, N), K - 1, replace=False))
        hbe.append(entropy_bits(np.diff(np.r_[0, cuts, N])))
    Hmb, Hbe, Ho = float(np.mean(hmb)), float(np.mean(hbe)), entropy_bits(c)
    k = (Hmb - Ho) / (Hmb - Hbe) if Hmb > Hbe else None
    # sampling band of kappa under BE (neutral): 2.5-97.5% of (Hmb - H_be_draw)/(Hmb - Hbe)
    band = [float(np.quantile([(Hmb - h) / (Hmb - Hbe) for h in hbe], q)) for q in (0.025, 0.975)]
    return {"kappa": k, "K": K, "N": N, "H_obs": Ho, "H_MB": Hmb, "H_BE": Hbe, "be_band": band}


# ================================================================================================ signatures
def signatures(t, mu):
    """Unfitted cell statistics under a fitted max-ent table, assuming independent quanta: agent breadth (mean over
    agents of observed / predicted distinct repos), reach of the top-3 repos (observed / predicted distinct agents) and
    the singleton-repo count."""
    n = t["n"]
    r = n.sum(1)
    P = mu / mu.sum(1, keepdims=True)
    q = 1 - (1 - P) ** r[:, None]          # P(agent i touches repo j at least once)
    b_obs = (n > 0).sum(1)
    b_pred = q.sum(1)
    reach_obs = (n > 0).sum(0)
    reach_pred = q.sum(0)
    single_pred = 0.0
    for j in range(n.shape[1]):
        qj = q[:, j]
        none_but = np.prod(1 - qj)
        single_pred += sum(qj[i] * none_but / max(1 - qj[i], 1e-300) for i in range(len(qj)))
    top = np.argsort(-n.sum(0))[: max(1, min(3, n.shape[1]))]
    return {"breadth_ratio": float(np.mean(b_obs / np.maximum(b_pred, 1e-12))),
            "cells_ratio": float(b_obs.sum() / b_pred.sum()) if b_pred.sum() else None,
            "reach_ratio_top3": float(reach_obs[top].sum() / reach_pred[top].sum()) if reach_pred[top].sum() else None,
            "singletons_obs": int((reach_obs == 1).sum()), "singletons_pred": float(single_pred)}


def run_counts(t) -> np.ndarray:
    """Work episodes per repo: runs of consecutive same-repo quanta within an agent-day."""
    c = np.zeros(t["n"].shape[1])
    for _, rl in t["runs"]:
        for j, _L in rl:
            c[j] += 1
    return c


def unit_analysis(q: pl.DataFrame, two_rooms: bool, draws=200, seed=0, own_col="own", labs=None) -> dict:
    t = unit_table(q, own_col, labs)
    rng = np.random.default_rng(seed)
    h = hierarchy(t, two_rooms)
    mus = h.pop("_mu")
    f1 = patefield_floor(t["n"], draws, rng)
    f2 = parametric_floor(mus["M2"], t, 2, two_rooms, draws, rng)
    f3 = parametric_floor(mus["M3"], t, 3, two_rooms, draws, rng) if two_rooms and h.get("lam_room") is not None else f2
    p1 = persistence_floor(mus["M1"], t, 1, two_rooms, draws, rng)
    p2 = persistence_floor(mus["M2"], t, 2, two_rooms, draws, rng)
    p3 = persistence_floor(mus["M3"], t, 3, two_rooms, draws, rng) if two_rooms and h.get("lam_room") is not None else p2
    lo, hi = agent_bootstrap_lambda(t, draws, rng)
    rc = run_counts(t)
    kap = kappa(rc, rng=rng)                                   # primary: episodes (runs) per repo (A1)
    kap_nn = kappa(rc[~t["named"]], rng=rng) if t["named"].any() else kap
    kap_q = kappa(t["n"].sum(0), rng=rng)                      # variant: quanta per repo
    sig1 = signatures(t, mus["M1"])
    sig2 = signatures(t, mus["M2"])
    sig2.update(persistence_signatures(mus["M2"], t, draws, rng))
    sig1.update(persistence_signatures(mus["M1"], t, draws, rng))
    D1c = h["D1"] - f1[0]
    out = {**h, "floor1": f1[0], "floor1_95": f1[1], "floor2": f2[0], "floor2_95": f2[1], "floor3": f3[0],
           "pfloor1": p1[0], "pfloor1_95": p1[1], "pfloor2": p2[0], "pfloor2_95": p2[1], "pfloor3": p3[0],
           "lam_own_lo": lo, "lam_own_hi": hi,
           "own_share": (h["D1"] - h["D2"]) / h["D1"] if h["D1"] > 0 else None,
           "room_share": (h["D2"] - h["D3"]) / h["D1"] if h["D1"] > 0 else None,
           "resid_share": (h["D3"] - f3[0]) / h["D1"] if h["D1"] > 0 else None,
           "resid_share_persist": (h["D3"] - p3[0]) / h["D1"] if h["D1"] > 0 else None,
           "D1_minus_floor": D1c,
           "kappa": kap, "kappa_no_named": kap_nn, "kappa_quanta": kap_q, "runs": float(rc.sum()), "named_repos": int(t["named"].sum()),
           "sig_M1": sig1, "sig_M2": sig2}
    return out
