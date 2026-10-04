"""H06 core: exact finite-N simulators for neutral cooperative dynamics (Pinero et al. 2025) and its rivals,
the village observation layer, the observables, and simulation-based fitting / model comparison.

Models (individuals = agent slots; species = projects). One model step:
  with prob. mu        : a brand-new species replaces a random individual C            (all models)
  with prob. 1 - mu    : draw A, B, C uniformly (with replacement) and
      'ncd'        C copies A's species iff species(A) != species(B)   (replication needs a partner of another species)
      'hubbell'    C copies A's species                                (Moran / Hubbell neutral drift)
      'conformist' C copies A's species with prob. 1 if species(A) == species(B) (A != B), else with prob. P_D = 0.2
                   (herding: replication is favoured by agreement; per-capita recruitment rises ~5x with share)
The NCD rule gives the birth rate b_n = (1-mu)(n/N)(1-n/N)^2 used in the paper; Hubbell gives (1-mu)(n/N)(1-n/N);
the conformist rule (a kinetic analogue of H11's ferromagnetic Potts coupling) gives (1-mu)(n/N)(1-n/N)[n/N + P_D(1-n/N)].
(A pure 'copy only on agreement' rule is absorbing from singletons, so the herding rival keeps a P_D = 0.2 leak.)

Village observation layer: the simulated population is snapshotted once per 30-min window; each day has the real
number of windows; between consecutive windows k*N model steps are applied (thinned, so k can be fractional); one
window's worth of steps is applied overnight. A boolean mask (T x N) says which agent slots were labelled in which
window; unlabelled slots are hidden exactly as in the data. So every statistic is computed identically on data
and on simulations, and nothing relies on large-N asymptotics.

The two moments used for fitting are the change rate c (label changes per observed within-day transition) and
the novelty fraction f_nov (share of changes that go to a species never observed before in the period). Each
model gets its own (mu, k). Everything else (Simpson lambda, abundance distribution, dominance, singletons,
frequency dependence, infiltration, residence/max-abundance clusters) is an unfitted prediction.
"""
from __future__ import annotations

import math
import os
import warnings
import zlib

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402
from scipy import optimize, special  # noqa: E402

MODELS = ("ncd", "hubbell", "conformist")
P_D = 0.2  # conformist rival: copy probability when A and B disagree


def _seed(*args) -> int:
    """Deterministic seed from arbitrary arguments (Python's hash() of strings is salted per process)."""
    return zlib.crc32(repr(args).encode())


# ------------------------------------------------------------------------------------------------ theory

def mu_B(N: float) -> float:
    """Bimodality boundary (paper): bimodal abundance distribution below mu_B."""
    return math.exp(-2.0) / math.sqrt(2 * math.pi * N)


def mu_L(N: float) -> float:
    """Log-series onset (paper): Hubbell-like log-series above mu_L."""
    return math.sqrt(2.0 / (math.pi * N))


def lambda_star(mu: float, N: float) -> float:
    """Self-consistent Simpson index: 1/mu = sqrt(pi N/2) erfcx(sqrt(N/2)(mu - lambda*)) (large-N theory)."""
    if mu <= 0:
        return float("nan")
    a = math.sqrt(math.pi * N / 2.0)
    s = math.sqrt(N / 2.0)
    f = lambda lam: a * special.erfcx(s * (mu - lam)) - 1.0 / mu
    lo, hi = -5.0, 1.0
    # erfcx is decreasing in its argument -> f increasing in lam
    if f(hi) < 0:
        return 1.0
    if f(lo) > 0:
        lo = -50.0
    try:
        return float(optimize.brentq(f, lo, hi, xtol=1e-10))
    except ValueError:
        return float("nan")


def lambda_star_approx(mu: float, N: float) -> float:
    if mu < mu_B(N):
        v = -math.log(2 * math.pi * N * mu * mu) / N
        return math.sqrt(max(v, 0.0))
    return 1.0 / (N * mu) if mu > mu_L(N) else float("nan")


def pn_theory(mu: float, N: int) -> np.ndarray:
    """Asymptotic steady-state abundance distribution P_n, n = 1..N (normalized)."""
    lam = lambda_star(mu, N)
    n = np.arange(1, N + 1, dtype=float)
    lp = n * np.log1p(-mu) - np.log(n) - (n - N * lam) ** 2 / (2 * N)
    p = np.exp(lp - lp.max())
    return p / p.sum()


# ------------------------------------------------------------------------------------------------ simulator

def _steps(s, next_id, mu, model, rng, n_steps, p_apply=1.0):
    """Apply n_steps vectorized model steps to the R x N state s (in place)."""
    R, N = s.shape
    r = np.arange(R)
    if n_steps <= 0:
        return
    A = rng.integers(0, N, (n_steps, R))
    B = rng.integers(0, N, (n_steps, R)) if model != "conformist" else (A + rng.integers(1, N, (n_steps, R))) % N
    C = rng.integers(0, N, (n_steps, R))
    U = rng.random((n_steps, R))
    U2 = rng.random((n_steps, R)) if model == "conformist" else None
    act = rng.random((n_steps, R)) < p_apply if p_apply < 1.0 else None
    for t in range(n_steps):
        a, b, c, u = A[t], B[t], C[t], U[t]
        sA = s[r, a]
        nov = u < mu
        if model == "ncd":
            cp = s[r, b] != sA
        elif model == "hubbell":
            cp = np.ones(R, bool)
        else:
            cp = (s[r, b] == sA) | (U2[t] < P_D)
        cp &= ~nov
        if act is not None:
            nov &= act[t]
            cp &= act[t]
        if cp.any():
            s[r[cp], c[cp]] = sA[cp]
        if nov.any():
            idx = r[nov]
            s[idx, c[nov]] = next_id[idx]
            next_id[idx] += 1


def burn_in_steps(N: int, mu: float) -> int:
    return int(min(300_000, max(3_000, 6 * N / max(mu, 1e-6), 4 * N * N)))


def burn(model: str, N: int, mu: float, R: int, seed: int):
    rng = np.random.default_rng(seed)
    s = np.tile(np.arange(N, dtype=np.int64), (R, 1))
    nid = np.full(R, N, dtype=np.int64)
    total = burn_in_steps(N, mu)
    chunk = 2000
    done = 0
    while done < total:
        m = min(chunk, total - done)
        _steps(s, nid, mu, model, rng, m)
        done += m
    return s, nid


def observe(model: str, s0, nid0, mu: float, k: float, day: np.ndarray, seed: int):
    """Run the observation phase from a burned-in state; returns snaps (R, T, N) of species ids."""
    rng = np.random.default_rng(seed)
    s, nid = s0.copy(), nid0.copy()
    R, N = s.shape
    T = len(day)
    lam = k * N
    M = max(1, int(math.ceil(lam)))
    p = lam / M
    snaps = np.empty((R, T, N), dtype=np.int64)
    for t in range(T):
        snaps[:, t] = s
        if t + 1 < T:
            _steps(s, nid, mu, model, rng, M, p_apply=p)  # within-day step, or one window's worth overnight
    return snaps


def mask_snaps(snaps, mask):
    lab = snaps.copy()
    lab[:, ~mask] = -1
    return lab


# ------------------------------------------------------------------------------------------------ moments (vectorized)

def moments(lab: np.ndarray, day: np.ndarray):
    """Change rate c and novelty fraction f_nov for an (R, T, N) or (T, N) label array (-1 = missing)."""
    one = lab.ndim == 2
    if one:
        lab = lab[None]
    R, T, N = lab.shape
    same = day[:-1] == day[1:]
    a, b = lab[:, :-1], lab[:, 1:]
    tr = (a >= 0) & (b >= 0) & same[None, :, None]
    ch = tr & (a != b)
    # first observed window of each species per replicate
    tt = np.broadcast_to(np.arange(T)[None, :, None], lab.shape)
    rr = np.broadcast_to(np.arange(R)[:, None, None], lab.shape)
    ok = lab >= 0
    key_r, key_s, key_t = rr[ok], lab[ok], tt[ok]
    first = {}
    # vectorized min first-window per (r, species)
    order = np.lexsort((key_t, key_s, key_r))
    kr, ks, kt = key_r[order], key_s[order], key_t[order]
    newgrp = np.r_[True, (kr[1:] != kr[:-1]) | (ks[1:] != ks[:-1])]
    fr, fs, ft = kr[newgrp], ks[newgrp], kt[newgrp]
    # novelty of a change at transition t -> t+1: species b first observed at window t+1
    first = np.full(lab.shape, -1, dtype=np.int64)
    # map: for each (r, t, n) with label, its species' first window
    big = (fr.astype(np.int64) << 40) + fs.astype(np.int64)
    key_all = (rr.astype(np.int64) << 40) + np.where(ok, lab, 0)
    idx = np.searchsorted(big, key_all.ravel()).reshape(lab.shape)
    idx = np.clip(idx, 0, len(big) - 1)
    first = np.where(ok, ft[idx], -1)
    nov = ch & (first[:, 1:] == np.arange(1, T)[None, :, None])
    n_tr = tr.sum((1, 2)).astype(float)
    n_ch = ch.sum((1, 2)).astype(float)
    n_nov = nov.sum((1, 2)).astype(float)
    c = np.divide(n_ch, n_tr, out=np.full(R, np.nan), where=n_tr > 0)
    f = np.divide(n_nov, n_ch, out=np.full(R, np.nan), where=n_ch > 0)
    if one:
        return float(c[0]), float(f[0]), int(n_tr[0]), int(n_ch[0]), int(n_nov[0])
    return c, f


# ------------------------------------------------------------------------------------------------ observables

STAT_NAMES = ("lam", "xmax", "single", "rich", "beta", "infil", "dbic2", "copyfrac")
# lam      mean Simpson index sum_i (n_i/n_obs)^2 over windows with >= 2 labelled agents
# xmax     mean share of the most abundant species
# single   fraction of species occurrences (species x window) with abundance 1
# rich     mean number of species per labelled agent (S / n_obs)
# beta     frequency dependence: conditional-logit slope of P(recruit to i) proportional to x_i exp(beta x_i)
#          (Hubbell 0; NCD negative, rare species recruit more per capita; conformist positive)
# infil    fraction of novel species that reach the core abundance m_core within the period
# dbic2    BIC(1 cluster) - BIC(2 clusters) of a diagonal Gaussian mixture on (log residence, log max abundance)
# copyfrac fraction of non-novel changes whose new label is held by another labelled agent at the previous window


BETA_PRIOR_SD = 5.0  # weak ridge prior on beta (MAP), so perfect separation with few events stays finite


def _beta_mle(events):
    """events: list of (x_choices array, chosen index). Maximize sum log[x_c e^{b x_c} / sum_j x_j e^{b x_j}]
    - b^2 / (2 * BETA_PRIOR_SD^2)  (MAP with a weak Gaussian prior)."""
    if len(events) < 3:
        return float("nan"), float("nan"), len(events)
    X = [e[0] for e in events]
    cidx = [e[1] for e in events]
    xc = np.array([x[c] for x, c in zip(X, cidx)])
    lens = np.array([len(x) for x in X])
    xs = np.concatenate(X)
    lx = np.log(xs)
    seg = np.repeat(np.arange(len(X)), lens)
    b = 0.0
    for _ in range(50):
        z = lx + b * xs
        zmax = np.maximum.reduceat(z, np.r_[0, np.cumsum(lens)[:-1]])
        w = np.exp(z - zmax[seg])
        W = np.bincount(seg, w)
        m1 = np.bincount(seg, w * xs) / W
        m2 = np.bincount(seg, w * xs * xs) / W
        g = float(np.sum(xc - m1)) - b / BETA_PRIOR_SD ** 2
        h = float(np.sum(m2 - m1 * m1)) + 1.0 / BETA_PRIOR_SD ** 2
        if h <= 1e-12:
            return float("nan"), float("nan"), len(events)
        step = g / h
        step = max(-5.0, min(5.0, step))
        b += step
        if abs(step) < 1e-7:
            break
        if abs(b) > 60:
            break
    se = 1.0 / math.sqrt(h) if h > 0 else float("nan")
    return float(np.clip(b, -60, 60)), se, len(events)


def _gmm_dbic(P, n_iter=60, var_floor=0.02, seed=0):
    """BIC(1) - BIC(2) for a 2-D diagonal Gaussian mixture (positive favours two clusters)."""
    n = len(P)
    if n < 8:
        return float("nan")
    mu1, v1 = P.mean(0), np.maximum(P.var(0), var_floor)
    ll1 = float(np.sum(-0.5 * (np.log(2 * np.pi * v1) + (P - mu1) ** 2 / v1)))
    bic1 = -2 * ll1 + 4 * math.log(n)
    best = -np.inf
    # deterministic inits: split on each coordinate's median, and extremes
    inits = []
    for d in range(2):
        med = np.median(P[:, d])
        lo, hi = P[P[:, d] <= med], P[P[:, d] > med]
        if len(lo) >= 2 and len(hi) >= 2:
            inits.append((lo.mean(0), hi.mean(0)))
    if not inits:
        return 0.0
    for m_a, m_b in inits:
        mu = np.array([m_a, m_b])
        var = np.array([v1, v1])
        pi = np.array([0.5, 0.5])
        ll = -np.inf
        for _ in range(n_iter):
            lp = np.stack([np.log(pi[j]) + np.sum(-0.5 * (np.log(2 * np.pi * var[j]) + (P - mu[j]) ** 2 / var[j]), 1)
                           for j in range(2)], 1)
            mx = lp.max(1, keepdims=True)
            lse = mx[:, 0] + np.log(np.exp(lp - mx).sum(1))
            new = float(lse.sum())
            r = np.exp(lp - lse[:, None])
            nk = r.sum(0) + 1e-9
            pi = nk / n
            mu = (r.T @ P) / nk[:, None]
            var = np.maximum((r.T @ (P ** 2)) / nk[:, None] - mu ** 2, var_floor)
            if new - ll < 1e-6:
                ll = new
                break
            ll = new
        best = max(best, ll)
    bic2 = -2 * best + 9 * math.log(n)
    return float(bic1 - bic2)


def label_stats(lab: np.ndarray, day: np.ndarray, m_core: int | None = None) -> dict:
    """All observables for one (T, N) label array (-1 = missing)."""
    T, N = lab.shape
    obs = lab >= 0
    nobs = obs.sum(1)
    if m_core is None:
        med = np.median(nobs[nobs > 0]) if (nobs > 0).any() else 2
        m_core = max(2, int(round(0.25 * med)))
    lam, xmax, rich = [], [], []
    single = occ = 0
    hist = np.zeros(N + 1)
    first, last, maxab = {}, {}, {}
    counts_t = []
    for t in range(T):
        labs = lab[t][obs[t]]
        if len(labs) == 0:
            counts_t.append({})
            continue
        u, cnt = np.unique(labs, return_counts=True)
        d = dict(zip(u.tolist(), cnt.tolist()))
        counts_t.append(d)
        for sp, c in d.items():
            if sp not in first:
                first[sp] = t
            last[sp] = t
            if c > maxab.get(sp, 0):
                maxab[sp] = c
        np.add.at(hist, cnt, 1)
        occ += len(cnt)
        single += int((cnt == 1).sum())
        if len(labs) >= 2:
            x = cnt / len(labs)
            lam.append(float((x * x).sum()))
            xmax.append(float(x.max()))
            rich.append(len(cnt) / len(labs))
    # recruitment events (conditional logit) and copy-consistency
    events = []
    n_copy = n_nc = 0
    seen = set()
    for t in range(T - 1):
        seen.update(counts_t[t].keys())
        if day[t] != day[t + 1]:
            continue
        nt = nobs[t]
        if nt < 2:
            continue
        for a in np.flatnonzero(obs[t] & obs[t + 1]):
            o, nw = lab[t, a], lab[t + 1, a]
            if o == nw or nw not in seen:
                continue
            d = dict(counts_t[t])
            d[o] = d.get(o, 0) - 1  # the focal agent's own old species is not a choice
            if d.get(nw, 0) <= 0:
                n_nc += 1
                continue
            n_copy += 1
            ch = [sp for sp, c in d.items() if c > 0 and sp != o]
            x = np.array([counts_t[t][sp] / nt for sp in ch])
            events.append((x, ch.index(nw)))
    beta, beta_se, n_ev = _beta_mle(events)
    # infiltration and residence / max abundance
    novel = [sp for sp, t0 in first.items() if t0 > 0]
    infil = (np.mean([maxab[sp] >= m_core for sp in novel]) if len(novel) >= 3 else float("nan"))
    if first:
        P = np.array([[math.log(last[sp] - first[sp] + 1), math.log(maxab[sp])] for sp in first])
        dbic = _gmm_dbic(P)
    else:
        dbic = float("nan")
    out = {
        "lam": float(np.mean(lam)) if lam else float("nan"),
        "xmax": float(np.mean(xmax)) if xmax else float("nan"),
        "single": single / occ if occ else float("nan"),
        "rich": float(np.mean(rich)) if rich else float("nan"),
        "beta": beta, "beta_se": beta_se, "n_events": n_ev,
        "infil": float(infil), "n_novel": len(novel), "m_core": m_core,
        "dbic2": dbic,
        "copyfrac": n_copy / (n_copy + n_nc) if (n_copy + n_nc) else float("nan"),
        "n_species": len(first),
        "hist": hist,
        "res_max": [(last[sp] - first[sp] + 1, maxab[sp], first[sp]) for sp in first],
    }
    return out


def stats_matrix(labs: np.ndarray, day: np.ndarray, m_core: int | None = None):
    """Statistics for each replicate of an (R, T, N) label array -> (R, len(STAT_NAMES)) and the P_n histograms."""
    R = labs.shape[0]
    M = np.full((R, len(STAT_NAMES)), np.nan)
    H = np.zeros((R, labs.shape[2] + 1))
    for r in range(R):
        st = label_stats(labs[r], day, m_core)
        M[r] = [st[k] for k in STAT_NAMES]
        H[r] = st["hist"]
    return M, H


# ------------------------------------------------------------------------------------------------ fitting

MU_GRID = np.geomspace(0.002, 0.6, 14)       # moment-only fit grid (secondary)
K_GRID = np.geomspace(0.02, 4.0, 12)
PMU_GRID = np.geomspace(0.002, 0.7, 20)      # profile synthetic-likelihood grid (primary, amendment 1)
PK_GRID = np.geomspace(0.02, 5.0, 14)
FIT_NAMES = ("c", "f") + STAT_NAMES[:7]      # statistics in the synthetic likelihood (copyfrac is an audit only)


def full_stats(labs: np.ndarray, day: np.ndarray, m_core=None):
    """(R, 9) matrix over FIT_NAMES, the P_n histograms, and copyfrac."""
    Ms, H = stats_matrix(labs, day, m_core)
    c, f = moments(labs, day)
    return np.column_stack([c, f, Ms[:, :7]]), H, Ms[:, 7]


class Bank:
    """Simulation bank for one observation layout (mask, day): moments on a (mu, k) grid per model, and full
    statistics at the fitted point."""

    def __init__(self, mask: np.ndarray, day: np.ndarray, seed: int = 0, R_fit: int = 48, m_core: int | None = None):
        self.mask, self.day = mask.astype(bool), np.asarray(day)
        nobs = self.mask.sum(1)
        self.m_core = m_core if m_core is not None else max(2, int(round(0.25 * np.median(nobs[nobs > 0])))) if (nobs > 0).any() else 2
        self.N = mask.shape[1]
        self.seed = seed
        self.R_fit = R_fit
        self.burned = {}
        self.grid = {}

    def _burned(self, model, mu, R, tag=0):
        key = (model, float(mu), R, tag)
        if key not in self.burned:
            self.burned[key] = burn(model, self.N, mu, R, seed=_seed(self.seed, model, round(mu, 8), R, tag))
        return self.burned[key]

    def moment_grid(self, model):
        if model in self.grid:
            return self.grid[model]
        C = np.full((len(MU_GRID), len(K_GRID)), np.nan)
        F = np.full_like(C, np.nan)
        Cs = np.full_like(C, np.nan)
        Fs = np.full_like(C, np.nan)
        for i, mu in enumerate(MU_GRID):
            s0, n0 = self._burned(model, mu, self.R_fit)
            for j, k in enumerate(K_GRID):
                snaps = observe(model, s0, n0, mu, k, self.day, seed=_seed(self.seed, model, i, j))
                c, f = moments(mask_snaps(snaps, self.mask), self.day)
                with np.errstate(all="ignore"), warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    C[i, j], F[i, j] = np.nanmean(c), np.nanmean(f)
                    Cs[i, j], Fs[i, j] = np.nanstd(c), np.nanstd(f)
        self.grid[model] = (C, F, Cs, Fs)
        return self.grid[model]

    def fit(self, model, c_obs, f_obs):
        """Minimum standardized distance on a bilinearly refined (log mu, log k) grid."""
        C, F, Cs, Fs = self.moment_grid(model)
        lm, lk = np.log(MU_GRID), np.log(K_GRID)
        # refine by interpolation on a finer grid
        fm = np.linspace(lm[0], lm[-1], 80)
        fk = np.linspace(lk[0], lk[-1], 80)
        from scipy.interpolate import RegularGridInterpolator as RGI
        def interp(Z):
            Zf = np.where(np.isfinite(Z), Z, np.nanmean(Z))
            return RGI((lm, lk), Zf)(np.stack(np.meshgrid(fm, fk, indexing="ij"), -1))
        Ci, Fi, Csi, Fsi = interp(C), interp(F), interp(Cs), interp(Fs)
        d = ((Ci - c_obs) / np.maximum(Csi, 0.01)) ** 2 + ((Fi - f_obs) / np.maximum(Fsi, 0.01)) ** 2
        i, j = np.unravel_index(np.nanargmin(d), d.shape)
        return float(np.exp(fm[i])), float(np.exp(fk[j])), float(d[i, j])

    # ---- primary: profile synthetic likelihood over the (mu, k) grid using all 9 statistics (amendment 1)
    def full_grid(self, model, R=80):
        key = ("full", model)
        if key in self.grid:
            return self.grid[key]
        G = np.full((len(PMU_GRID), len(PK_GRID), R, len(FIT_NAMES)), np.nan)
        for i, mu in enumerate(PMU_GRID):
            s0, n0 = burn(model, self.N, mu, R, seed=_seed(self.seed, model, "pg", i, R))
            for j, k in enumerate(PK_GRID):
                snaps = observe(model, s0, n0, mu, k, self.day, seed=_seed(self.seed, model, "pgo", i, j))
                F, _, _ = full_stats(mask_snaps(snaps, self.mask), self.day, self.m_core)
                G[i, j] = F
        self.grid[key] = G
        return G

    def profile(self, model, t_obs):
        """Best grid cell by Gaussian synthetic log-likelihood of t_obs (len 9); returns (mu, k, ll_grid, (i, j))."""
        G = self.full_grid(model)
        best, arg = -np.inf, (0, 0)
        L = np.full(G.shape[:2], np.nan)
        for i in range(G.shape[0]):
            for j in range(G.shape[1]):
                ll, _ = synth_loglik(t_obs, G[i, j])
                L[i, j] = ll
                if np.isfinite(ll) and ll > best:
                    best, arg = ll, (i, j)
        return float(PMU_GRID[arg[0]]), float(PK_GRID[arg[1]]), L, arg

    def predictive(self, model, mu, k, R=300, tag=1, m_core=None):
        s0, n0 = burn(model, self.N, mu, R, seed=_seed(self.seed, model, round(mu, 8), R, tag))
        snaps = observe(model, s0, n0, mu, k, self.day, seed=_seed(self.seed, model, "pred", tag))
        labs = mask_snaps(snaps, self.mask)
        M, H = stats_matrix(labs, self.day, m_core if m_core is not None else self.m_core)
        c, f = moments(labs, self.day)
        return M, H, c, f, labs

    def fresh(self, model, mu, k, R=300, tag=1):
        """Fresh simulations at a fitted point: (R, 9) FIT_NAMES matrix, histograms, copyfrac, raw labels."""
        s0, n0 = burn(model, self.N, mu, R, seed=_seed(self.seed, model, "fresh", round(mu, 8), R, tag))
        snaps = observe(model, s0, n0, mu, k, self.day, seed=_seed(self.seed, model, "fresho", round(k, 8), tag))
        labs = mask_snaps(snaps, self.mask)
        F, H, cf = full_stats(labs, self.day, self.m_core)
        return F, H, cf, labs


# ------------------------------------------------------------------------------------------------ model comparison

def synth_loglik(t_obs: np.ndarray, M: np.ndarray, cols=None, shrink=0.2):
    """Gaussian synthetic log-likelihood (Wood 2010) of an observed statistic vector under simulated M (R x p).
    Columns with NaN in the observation are dropped; covariance shrunk toward its diagonal."""
    cols = list(range(M.shape[1])) if cols is None else list(cols)
    cols = [c for c in cols if np.isfinite(t_obs[c]) and np.isfinite(M[:, c]).mean() > 0.8]
    if not cols:
        return float("nan"), []
    X = M[:, cols]
    X = X[np.isfinite(X).all(1)]
    if len(X) < 10:
        return float("nan"), cols
    m = X.mean(0)
    S = np.cov(X, rowvar=False).reshape(len(cols), len(cols))
    D = np.diag(np.diag(S))
    S = (1 - shrink) * S + shrink * D + 1e-6 * np.eye(len(cols))
    dlt = t_obs[cols] - m
    sign, logdet = np.linalg.slogdet(S)
    ll = -0.5 * (dlt @ np.linalg.solve(S, dlt) + logdet + len(cols) * math.log(2 * math.pi))
    return float(ll), cols


def ppc_p(t_obs: float, sims: np.ndarray) -> float:
    """Two-sided posterior-predictive p-value of an observed statistic among simulations."""
    s = sims[np.isfinite(sims)]
    if not np.isfinite(t_obs) or len(s) < 10:
        return float("nan")
    lo = (np.sum(s <= t_obs) + 1) / (len(s) + 1)
    hi = (np.sum(s >= t_obs) + 1) / (len(s) + 1)
    return float(min(1.0, 2 * min(lo, hi)))


def joint_ppc(t_obs: np.ndarray, M: np.ndarray, shrink=0.2):
    """Joint posterior-predictive p-value: share of simulated rows whose Mahalanobis distance (under the
    simulations' shrunk Gaussian) is at least the observation's. Small p = the model cannot produce the
    observed combination of statistics (amendment 3)."""
    cols = [c for c in range(M.shape[1]) if np.isfinite(t_obs[c]) and np.isfinite(M[:, c]).mean() > 0.8]
    if not cols:
        return float("nan")
    X = M[:, cols]
    X = X[np.isfinite(X).all(1)]
    if len(X) < 20:
        return float("nan")
    m = X.mean(0)
    S = np.cov(X, rowvar=False).reshape(len(cols), len(cols))
    S = (1 - shrink) * S + shrink * np.diag(np.diag(S)) + 1e-6 * np.eye(len(cols))
    Si = np.linalg.inv(S)
    d = t_obs[cols] - m
    d2o = float(d @ Si @ d)
    D = X - m
    d2 = np.einsum("ij,jk,ik->i", D, Si, D)
    return float((np.sum(d2 >= d2o) + 1) / (len(d2) + 1))

