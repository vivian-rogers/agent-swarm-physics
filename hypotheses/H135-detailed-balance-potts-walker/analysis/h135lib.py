"""H135 library: max-ent fit (H94 rules, re-implemented), co-alive pairs, pair counts and occupancies, the observables
O1-O5, the pair-flip null, and the event-driven walker on a unit's real skeleton (worlds W0, W0M, W1-W4).

No code is imported from another card's folder (STANDARDS 8). Repo/project names arrive hashed from the scheme.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import heapq  # noqa: E402
import math  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import optimize, stats  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H135-detailed-balance-potts-walker"
CAP = 20.0
LNPI_FLOOR = -15.0          # ln pi_i clipped here (quasi-separated cells of capped lambda fits)
PSEUDO = 0.5
TOL15 = math.log(1.5)


# ============================================================================================ max-ent (H94 rules)
def fit_maxent(n: np.ndarray, feats: list[np.ndarray], tol=1e-9, max_iter=3000, init=None):
    """Log-linear max-ent fit with row/column margins and binary features by IPF (H94's estimator, re-implemented)."""
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


def maxent_pi(n, own, room, two_rooms):
    """M2 (own) or M3 (own + room, two-room units) fit; returns mu, lambdas, model name."""
    mu1, _ = fit_maxent(n, [])
    feats = [own] if own.std() > 0 else []
    mu2, l2 = fit_maxent(n, feats, init=mu1) if feats else (mu1, np.array([np.nan]))
    if two_rooms and room.std() > 0 and feats:
        mu3, l3 = fit_maxent(n, [own, room], init=mu2)
        return mu3, {"lam_own": float(l3[0]), "lam_room": float(l3[1])}, "M3"
    return mu2, {"lam_own": float(l2[0]) if len(l2) else np.nan, "lam_room": None}, "M2"


# ============================================================================================ pair tables
def pair_table(hops: pl.DataFrame, T: dict, pi: dict, rank: dict, coalive: set) -> dict:
    """Unordered co-alive pairs (a, b) with a = the older project: n_ab (a -> b), n_ba, T_a, T_b, x = ln(pi_b / pi_a)."""
    cnt = {}
    for s, d in hops.select("src", "dst").iter_rows():
        if s in coalive and d in coalive and s != d:
            cnt[(s, d)] = cnt.get((s, d), 0) + 1
    pairs = {}
    for (s, d), n in cnt.items():
        a, b = (s, d) if rank[s] < rank[d] else (d, s)
        pairs.setdefault((a, b), [0, 0])
        pairs[(a, b)][0 if s == a else 1] += n
    keys = sorted(pairs)
    nab = np.array([pairs[k][0] for k in keys], float)
    nba = np.array([pairs[k][1] for k in keys], float)
    Ta = np.array([T.get(k[0], 0.0) for k in keys], float)
    Tb = np.array([T.get(k[1], 0.0) for k in keys], float)
    x = np.array([math.log(pi[k[1]]) - math.log(pi[k[0]]) for k in keys], float)
    return {"keys": keys, "nab": nab, "nba": nba, "Ta": Ta, "Tb": Tb, "x": x}


def deming_origin(x, y):
    """Orthogonal (Deming, delta = 1) slope through the origin (pairs enter in both orientations)."""
    sxx, syy, sxy = float(x @ x), float(y @ y), float(x @ y)
    if sxy == 0:
        return np.nan
    return ((syy - sxx) + math.sqrt((syy - sxx) ** 2 + 4 * sxy ** 2)) / (2 * sxy)


def r_origin(x, y):
    d = math.sqrt(float(x @ x) * float(y @ y))
    return float(x @ y) / d if d > 0 else np.nan


def o1(P: dict, min_n=4, boot=0, rng=None) -> dict:
    """HH-literal rate test on co-alive pairs with n_ab + n_ba >= min_n."""
    m = (P["nab"] + P["nba"] >= min_n) & (P["Ta"] > 0) & (P["Tb"] > 0)
    k = int(m.sum())
    out = {"n_pairs": k}
    if k < 3:
        out.update({"slope": np.nan, "r": np.nan, "p_r": np.nan, "pass": False})
        return out
    x = P["x"][m]
    yn = np.log((P["nab"][m] + PSEUDO) / (P["nba"][m] + PSEUDO))
    yt = np.log(P["Tb"][m] / P["Ta"][m])          # k_ab / k_ba = (n_ab / T_a) / (n_ba / T_b)
    y = yn + yt
    sl, r = deming_origin(x, y), r_origin(x, y)
    tstat = r * math.sqrt(max(k - 1, 1) / max(1 - r * r, 1e-12)) if np.isfinite(r) else np.nan
    p = float(2 * stats.t.sf(abs(tstat), k - 1)) if np.isfinite(tstat) else np.nan
    both3 = (P["nab"][m] >= 3) & (P["nba"][m] >= 3)
    within = float(np.mean(np.abs(y[both3] - x[both3]) <= TOL15)) if both3.any() else np.nan
    out.update({"slope": sl, "r": r, "p_r": p, "slope_n": deming_origin(x, yn), "slope_T": deming_origin(x, yt),
                "r_n": r_origin(x, yn), "r_T": r_origin(x, yt), "n_both3": int(both3.sum()), "within15": within,
                "pass": bool(np.isfinite(sl) and 0.5 <= sl <= 2 and r > 0 and p < 0.05)})
    if boot:
        rng = rng or np.random.default_rng(0)
        bs, br = [], []
        for _ in range(boot):
            i = rng.integers(0, k, k)
            bs.append(deming_origin(x[i], y[i])); br.append(r_origin(x[i], y[i]))
        out["slope_ci"] = [float(np.nanquantile(bs, .025)), float(np.nanquantile(bs, .975))]
        out["r_ci"] = [float(np.nanquantile(br, .025)), float(np.nanquantile(br, .975))]
    return out


def m_pi(P: dict) -> float:
    """Net max-ent flux: sum (n_ab - n_ba) sign(x) / sum (n_ab + n_ba); positive = toward the higher-pi project."""
    N = P["nab"] + P["nba"]
    s = np.sign(P["x"])
    tot = N[s != 0].sum()
    return float(((P["nab"] - P["nba"]) * s).sum() / tot) if tot > 0 else np.nan


def m2_co(P: dict) -> float:
    """Net age flux on co-alive pairs (a = older): (up - down) / (up + down)."""
    N = (P["nab"] + P["nba"]).sum()
    return float((P["nab"] - P["nba"]).sum() / N) if N > 0 else np.nan


def binom_fit(P: dict) -> dict:
    """n_ab | N ~ Bin(N, q), logit q = theta + beta_pi x, pairs oriented a = older (theta = age flux, beta = pi flux)."""
    N = P["nab"] + P["nba"]
    m = N > 0
    n, N, x = P["nab"][m], N[m], P["x"][m]
    if m.sum() < 3:
        return {"theta": np.nan, "beta": np.nan}

    def nll(b):
        eta = b[0] + b[1] * x
        return -float((n * eta - N * np.logaddexp(0, eta)).sum())
    res = optimize.minimize(nll, np.zeros(2), method="L-BFGS-B", bounds=[(-10, 10), (-10, 10)])
    return {"theta": float(res.x[0]), "beta": float(res.x[1])}


def flip_null(P: dict, n_draw=2000, rng=None) -> dict:
    """Pair-flip null: each pair's N hops split Binomial(1/2)."""
    rng = rng or np.random.default_rng(0)
    N = (P["nab"] + P["nba"]).astype(int)
    s = np.sign(P["x"])
    k = rng.binomial(N[None, :], 0.5, size=(n_draw, len(N)))
    d = 2 * k - N[None, :]
    tot = N.sum()
    totp = N[s != 0].sum()
    mp = (d * s[None, :]).sum(1) / totp if totp else np.full(n_draw, np.nan)
    m2 = d.sum(1) / tot if tot else np.full(n_draw, np.nan)
    return {"m_pi": mp, "m2co": m2}


def p_two(obs, null):
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    if not len(null) or not np.isfinite(obs):
        return np.nan
    return float(min(1.0, 2 * min(np.mean(null >= obs), np.mean(null <= obs)) + 1 / (len(null) + 1)))


# ============================================================================================ O4 heat-bath logit
def choice_rows(hops: pl.DataFrame, avail: dict, lnpi_i: dict) -> list:
    """Per hop: arrays over the choice set (available projects != origin): ln pi_i(b), held-before flag, chosen index,
    origin. Hops whose destination is not in the set are dropped."""
    rows = []
    held = {}
    for a, t, s, d in hops.sort("agent", "t").select("agent", "t", "src", "dst").iter_rows():
        h = held.setdefault(a, {s})
        cs = [p for p, (t0, t1) in avail.items() if t0 <= t <= t1 and p != s]
        if d not in cs:
            cs.append(d)
        lp = np.array([lnpi_i.get((a, p), LNPI_FLOOR) for p in cs])
        hb = np.array([p in h for p in cs], float)
        rows.append((lp, hb, cs.index(d), s, cs))
        h.add(d)
    return rows


def clogit(rows, inter_pairs=None):
    """Conditional logit u = psi ln pi_i(b) + rho held(b) [+ omega_(a,b) for listed ordered pairs]; MLE and SEs."""
    K = 2 + (len(inter_pairs) if inter_pairs else 0)
    ip = {p: k for k, p in enumerate(inter_pairs or [])}
    data = []
    for lp, hb, c, s, cs in rows:
        if len(cs) < 2:
            continue
        X = np.zeros((len(cs), K))
        X[:, 0] = np.maximum(lp, LNPI_FLOOR)
        X[:, 1] = hb
        if ip:
            for j, p in enumerate(cs):
                k = ip.get((s, p))
                if k is not None:
                    X[j, 2 + k] = 1.0
        data.append((X, c))
    if len(data) < 5:
        return None

    def f(b):
        ll, g = 0.0, np.zeros(K)
        for X, c in data:
            u = X @ b
            u = u - u.max()
            e = np.exp(u)
            p = e / e.sum()
            ll += u[c] - math.log(e.sum())
            g += X[c] - p @ X
        return -ll, -g
    bnds = [(-20, 20), (-20, 20)] + [(-10, 10)] * (K - 2)
    res = optimize.minimize(f, np.r_[1.0, 0.0, np.zeros(K - 2)], jac=True, method="L-BFGS-B", bounds=bnds)
    b = res.x
    H = np.zeros((K, K))
    for X, c in data:
        u = X @ b
        p = np.exp(u - u.max())
        p /= p.sum()
        mx = p @ X
        H += (X * p[:, None]).T @ X - np.outer(mx, mx)
    try:
        cov = np.linalg.inv(H + 1e-9 * np.eye(K))
        se = np.sqrt(np.maximum(np.diag(cov), 0))
    except np.linalg.LinAlgError:
        se = np.full(K, np.nan)
    return {"psi": float(b[0]), "rho": float(b[1]), "se_psi": float(se[0]), "se_rho": float(se[1]), "ll": float(-res.fun),
            "n_choice": len(data)}


def o4(hops, avail, lnpi_i, lr=True, min_pair=3) -> dict | None:
    rows = choice_rows(hops, avail, lnpi_i)
    base = clogit(rows)
    if base is None:
        return None
    if lr:
        cnt = {}
        for s, d in hops.select("src", "dst").iter_rows():
            cnt[(s, d)] = cnt.get((s, d), 0) + 1
        ip = sorted(k for k, v in cnt.items() if v >= min_pair)
        if ip:
            full = clogit(rows, ip)
            lrs = 2 * (full["ll"] - base["ll"])
            base.update({"lr": float(lrs), "lr_df": len(ip), "lr_p": float(stats.chi2.sf(max(lrs, 0), len(ip)))})
        else:
            base.update({"lr": np.nan, "lr_df": 0, "lr_p": np.nan})
    return base


# ============================================================================================ random effects
def dersimonian_laird(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) < 2:
        return {"mean": float(est[0]) if len(est) else np.nan, "ci": [np.nan, np.nan], "tau2": np.nan, "k": len(est)}
    w = 1 / se ** 2
    mf = (w * est).sum() / w.sum()
    Q = (w * (est - mf) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    ws = 1 / (se ** 2 + tau2)
    m = (ws * est).sum() / ws.sum()
    s = math.sqrt(1 / ws.sum())
    return {"mean": float(m), "se": s, "ci": [m - 1.96 * s, m + 1.96 * s], "tau2": float(tau2), "k": int(len(est))}


# ============================================================================================ walker
class Skeleton:
    """A unit-channel's real skeleton: agents (own-call times in the unit, first label and its time), project
    availability windows, pi_i (agent x project), age ranks, the observed hop count, and the co-alive set."""

    def __init__(self, calls: dict, first: dict, avail: dict, lnpi: dict, rank: dict, n_hops: int, coalive: set,
                 pi_unit: dict):
        self.projects = sorted(avail)
        self.pidx = {p: k for k, p in enumerate(self.projects)}
        self.a0 = np.array([avail[p][0] for p in self.projects])
        self.a1 = np.array([avail[p][1] for p in self.projects])
        self.rank = np.array([rank[p] for p in self.projects], float)
        self.agents = sorted(a for a in first if a in calls and len(calls[a]))
        self.calls = {a: np.asarray(calls[a], float) for a in self.agents}
        self.first = first
        J = len(self.projects)
        self.lnpi = {a: np.array([lnpi.get((a, p), LNPI_FLOOR) for p in self.projects]) for a in self.agents}
        self.n_hops = n_hops
        self.coalive = coalive
        self.pi_unit = pi_unit
        self.rank_map = rank
        self.J = J


def _hazard_logS(c, gamma, dmax):
    d = np.arange(1, dmax + 1, dtype=float)
    h = 1 / (1 + np.exp(-(c + gamma * np.log(d))))
    return np.cumsum(np.log1p(-np.minimum(h, 1 - 1e-12)))      # logS[d-1] = log P(no update in 1..d)


def simulate(sk: Skeleton, world: str, c: float, rng, gamma=-0.3, lam=1.5, b_hab=2.0, kappa=2.0, sink=1.5):
    """One run. Each agent starts on its real first label at its first-label time; at each later own call it updates
    with probability h(d) = logistic(c + gamma ln d), d = own calls since arrival. Update rules:
      W0  heat-bath: draw j ~ pi_i over the available set (current included); j == current -> stay.
      W0M Metropolis: propose j uniform over available != current; accept with min(1, pi_i(j)/pi_i(cur)).
      W1  age drift: softmax(ln pi_i + b_hab held + lam z_age(t)) over available != current (always hops).
      W2  sink: softmax(ln pi_i + sink ln(occupants_j + 1)).
      W3  cycle: softmax(ln pi_i + b_hab held + kappa [j = age successor of current]).
      W4  habit: softmax(ln pi_i + b_hab held).
    A current project whose window has closed forces a hop at the next call. Returns hops (agent, t, src, dst) and
    occupancy T per (agent, project) in own calls."""
    P = sk.projects
    a0, a1, rk = sk.a0, sk.a1, sk.rank
    allc = max(len(v) for v in sk.calls.values())
    logS = _hazard_logS(c, gamma, allc + 2)
    negS = -logS
    heap = []
    cur, arr_i, held, occ = {}, {}, {}, {}
    T = {}
    hops = []

    def schedule(a, from_i):
        """Next update call index for agent a given the visit started at call index arr_i[a] and no update before
        call from_i (exclusive)."""
        tc = sk.calls[a]
        d0 = from_i - arr_i[a]            # calls already survived since arrival
        base = negS[d0 - 1] if d0 >= 1 else 0.0
        u = -math.log(rng.random())
        k = int(np.searchsorted(negS, base + u, side="left"))   # d = k + 1
        idx = arr_i[a] + k + 1
        # forced exit: first call after the current project's window closed
        j = cur[a]
        if a1[j] < np.inf:
            fi = int(np.searchsorted(tc, a1[j], side="right"))
            if fi <= idx and fi > from_i:
                idx = fi
            elif fi <= from_i:
                idx = from_i + 1
        if idx < len(tc):
            heapq.heappush(heap, (tc[idx], a, idx))

    for a in sk.agents:
        tc = sk.calls[a]
        p0, t0 = sk.first[a]
        if p0 not in sk.pidx:
            continue
        i0 = int(np.searchsorted(tc, t0, side="left"))
        if i0 >= len(tc):
            continue
        cur[a] = sk.pidx[p0]
        arr_i[a] = i0
        held[a] = {cur[a]}
        occ[cur[a]] = occ.get(cur[a], 0) + 1
        schedule(a, i0)

    while heap:
        t, a, idx = heapq.heappop(heap)
        j = cur[a]
        av = np.where((a0 <= t) & (a1 >= t))[0]
        forced = not (a0[j] <= t <= a1[j])
        others = av[av != j]
        if len(others) == 0:
            schedule(a, idx)
            continue
        lp = sk.lnpi[a]
        dest = None
        if world == "W0":
            cand = others if forced else av
            w = np.exp(lp[cand] - lp[cand].max())
            k = cand[rng.choice(len(cand), p=w / w.sum())]
            dest = None if k == j else k
        elif world == "W0M":
            k = others[rng.integers(len(others))]
            if forced or rng.random() < min(1.0, math.exp(lp[k] - lp[j])):
                dest = k
        else:
            u = lp[others].copy()
            if world in ("W1", "W3", "W4"):
                u += b_hab * np.array([o in held[a] for o in others], float)
            if world == "W1":
                r = rk[av]
                z = (rk[others] - r.mean()) / (r.std() if r.std() > 0 else 1.0)
                u += lam * z
            if world == "W3":
                newer = others[rk[others] > rk[j]]
                succ = newer[np.argmin(rk[newer])] if len(newer) else others[np.argmin(rk[others])]
                u += kappa * (others == succ)
            if world == "W2":
                u += sink * np.log(np.array([occ.get(o, 0) for o in others], float) + 1)
            w = np.exp(u - u.max())
            dest = others[rng.choice(len(others), p=w / w.sum())]
        if dest is None:
            schedule(a, idx)
            continue
        T[(a, j)] = T.get((a, j), 0) + (idx - arr_i[a])
        hops.append((a, t, P[j], P[dest]))
        occ[j] -= 1
        occ[dest] = occ.get(dest, 0) + 1
        cur[a] = dest
        arr_i[a] = idx
        held[a].add(dest)
        schedule(a, idx)
    for a, j in cur.items():
        T[(a, j)] = T.get((a, j), 0) + (len(sk.calls[a]) - 1 - arr_i[a])
    H = pl.DataFrame(hops, schema={"agent": pl.Int16, "t": pl.Float64, "src": pl.String, "dst": pl.String}, orient="row")
    Tp = {}
    for (a, j), v in T.items():
        Tp[P[j]] = Tp.get(P[j], 0) + v
    return H, Tp


def calibrate_c(sk: Skeleton, world: str, rng, n=4, **kw) -> float:
    """Bisection on the hazard intercept so the mean hop count matches the observed count."""
    lo, hi = -12.0, 2.0
    target = max(sk.n_hops, 1)
    for _ in range(12):
        mid = (lo + hi) / 2
        m = np.mean([simulate(sk, world, mid, rng, **kw)[0].height for _ in range(n)])
        if m < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def sim_stats(sk: Skeleton, H: pl.DataFrame, Tp: dict, lnpi_i: dict | None = None, avail: dict | None = None,
              with_o4=False, lr=False) -> dict:
    P = pair_table(H, Tp, sk.pi_unit, sk.rank_map, sk.coalive)
    r1 = o1(P)
    bf = binom_fit(P)
    out = {"slope": r1["slope"], "r": r1["r"], "p_r": r1["p_r"], "o1_pass": r1["pass"], "within15": r1.get("within15", np.nan),
           "m_pi": m_pi(P), "m2co": m2_co(P), "theta": bf["theta"], "beta": bf["beta"],
           "n_co_hops": float((P["nab"] + P["nba"]).sum()), "n_pairs4": int(((P["nab"] + P["nba"]) >= 4).sum()),
           "n_hops": H.height}
    fn = flip_null(P, 400, np.random.default_rng(1))
    out["p_flip_mpi"] = p_two(out["m_pi"], fn["m_pi"])
    out["p_flip_m2"] = p_two(out["m2co"], fn["m2co"])
    if with_o4 and lnpi_i is not None and H.height >= 10:
        r4 = o4(H, avail, lnpi_i, lr=lr)
        if r4:
            out.update({"psi": r4["psi"], "rho": r4["rho"], "se_psi": r4["se_psi"], "se_rho": r4["se_rho"],
                        "lr_p": r4.get("lr_p", np.nan)})
    return out
