"""Core Hawkes machinery for H03: day-blocked realizations, time-varying baselines, MLE, simulation, diagnostics.

Model (one realization per village day d, t in [0, T_d], no carry-over between days):

  lambda_u(t) = c_u * s_{b(t)}                        baseline: unit level x shared within-day shape (30-min bins)
              + sum_k w_k * F_k(t)                    fixed bases: kickoff bumps e^{-t/tau_k} (first day),
                                                      exogenous kernels delta_r * sum_{x<t} e^{-delta_r (t-x)},
                                                      fixed-rate kernel grid beta_m * sum_{j<t} e^{-beta_m (t-t_j)}
              + alpha * beta * sum_{t_j<t} e^{-beta (t-t_j)}     optional free-beta exponential kernel (n = alpha)
              (+ power-law-constrained grid weights alpha_m = n * w_m(theta), w_m ∝ tau_m^-theta)

Units: univariate fits use unit = day (B1/B2), a single unit (B0) or a (day, bin) cell (B3).
Agent-level fits (M3) use unit = (day, agent), with own- and cross-agent kernel grids.

All parameters are optimized in log space with L-BFGS-B and analytic gradients.
"""
from __future__ import annotations

import ctypes
import hashlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import optimize, stats

BIN_S = 1800.0
KICK_TAUS = np.array([1200.0, 7200.0])           # kickoff bump timescales (20 min, 2 h)
EXO_TAUS = np.array([120.0, 600.0, 3600.0])       # exogenous kernel timescales (2, 10, 60 min)
GRID_TAUS = np.array([10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0])  # sum-of-exponentials kernel grid
BETA_MAX = 1.0                                     # kernel timescale >= 1 s (sub-second = logging, see scheme)
BETA_MIN = 1.0 / 20000.0

# ----------------------------------------------------------------------------------------------- C helpers
_C_SRC = r"""
#include <math.h>
#include <limits.h>
/* events sorted by (group, t); A_i = sum_{j<i, same group} e^{-beta(t_i-t_j)}, B_i = sum (t_i-t_j) e^{...} */
void exp_sums(long n, const double* t, const long* g, double beta, double* A, double* B) {
  double a = 0.0, b = 0.0;
  for (long i = 0; i < n; i++) {
    if (i == 0 || g[i] != g[i-1]) { a = 0.0; b = 0.0; }
    else {
      double dt = t[i] - t[i-1];
      double e = exp(-beta * dt);
      b = e * (b + dt * (1.0 + a));
      a = e * (a + 1.0);
    }
    A[i] = a;
    if (B) B[i] = b;
  }
}
/* X_i = sum_{x in same group, x < t_i} e^{-delta (t_i - x)}; events and exo both sorted by (group, time) */
void exo_sums(long n, const double* t, const long* g, long m, const double* x, const long* gx,
              double delta, double* X) {
  long j = 0; double s = 0.0, tref = 0.0; int have = 0; long gcur = LONG_MIN;
  for (long i = 0; i < n; i++) {
    if (g[i] != gcur) { gcur = g[i]; s = 0.0; have = 0; while (j < m && gx[j] < gcur) j++; }
    while (j < m && gx[j] == gcur && x[j] < t[i]) {
      if (have) s *= exp(-delta * (x[j] - tref));
      s += 1.0; tref = x[j]; have = 1; j++;
    }
    X[i] = have ? s * exp(-delta * (t[i] - tref)) : 0.0;
  }
}
/* For events with u[i] >= 0 pick a parent j < i in the same group with prob ∝ e^{-beta (t_i - t_j)}. */
void sample_parents(long n, const double* t, const long* g, double beta, const double* A,
                    const double* u, long* parent) {
  for (long i = 0; i < n; i++) {
    parent[i] = -1;
    if (u[i] < 0.0) continue;
    double target = u[i] * A[i], cum = 0.0; long j = i - 1, last = -1;
    while (j >= 0 && g[j] == g[i]) {
      cum += exp(-beta * (t[i] - t[j])); last = j;
      if (cum >= target) { parent[i] = j; break; }
      j--;
    }
    if (parent[i] < 0) parent[i] = last;
  }
}
"""
_LIB = None


def _lib():
    global _LIB
    if _LIB is not None:
        return _LIB
    h = hashlib.sha1(_C_SRC.encode()).hexdigest()[:10]
    bdir = Path(__file__).resolve().parent / "_build"
    bdir.mkdir(exist_ok=True)
    so = bdir / f"hawkes_{h}.so"
    if not so.exists():
        src = bdir / f"hawkes_{h}.c"
        src.write_text(_C_SRC)
        subprocess.run(["cc", "-O3", "-shared", "-fPIC", "-o", str(so), str(src)], check=True)
    lib = ctypes.CDLL(str(so))
    dp = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
    lp = np.ctypeslib.ndpointer(dtype=np.int64, flags="C_CONTIGUOUS")
    lib.exp_sums.argtypes = [ctypes.c_long, dp, lp, ctypes.c_double, dp, ctypes.c_void_p]
    lib.exo_sums.argtypes = [ctypes.c_long, dp, lp, ctypes.c_long, dp, lp, ctypes.c_double, dp]
    lib.sample_parents.argtypes = [ctypes.c_long, dp, lp, ctypes.c_double, dp, dp, lp]
    _LIB = lib
    return lib


def exp_sums(t, g, beta, want_b=False):
    n = len(t)
    A = np.empty(n)
    B = np.empty(n) if want_b else None
    _lib().exp_sums(n, t, g, float(beta), A, B.ctypes.data if want_b else None)
    return (A, B) if want_b else A


def exo_sums(t, g, x, gx, delta):
    X = np.empty(len(t))
    _lib().exo_sums(len(t), t, g, len(x), x, gx, float(delta), X)
    return X


def sample_parents(t, g, beta, A, u):
    parent = np.empty(len(t), dtype=np.int64)
    _lib().sample_parents(len(t), t, g, float(beta), A, u, parent)
    return parent


def exp_sums_reference(t, g, beta):
    """Slow O(n^2) reference used by the unit test."""
    A = np.zeros(len(t)); B = np.zeros(len(t))
    for i in range(len(t)):
        for j in range(i):
            if g[j] == g[i]:
                A[i] += np.exp(-beta * (t[i] - t[j])); B[i] += (t[i] - t[j]) * np.exp(-beta * (t[i] - t[j]))
    return A, B


# ----------------------------------------------------------------------------------------------- data
@dataclass
class Day:
    t: np.ndarray            # sorted event times (s since window start)
    agent: np.ndarray        # agent codes (int)
    T: float                 # window length
    first: bool              # goal's first day (kickoff bump)
    x: np.ndarray            # exogenous message times (may be < 0)
    active: np.ndarray       # agent codes active this day (>= 1 agent event of any kind)


def make_days(events, exo, days, event_set: str) -> dict[int, Day]:
    """events/exo/days: polars frames from the H03 processed folder. event_set in {'TALK', 'ALL'}."""
    import polars as pl
    ev = events.filter(pl.col("talk")) if event_set == "TALK" else events.filter(pl.col("turn_first"))
    act = events.group_by("day_id").agg(pl.col("agent").unique().sort())
    act = {r[0]: np.asarray(r[1], dtype=np.int64) for r in act.iter_rows()}
    evg = {k[0]: v for k, v in ev.sort("day_id", "t_s").partition_by("day_id", as_dict=True).items()}
    exg = {k[0]: v for k, v in exo.sort("day_id", "t_s").partition_by("day_id", as_dict=True).items()}
    out = {}
    for r in days.iter_rows(named=True):
        d = r["day_id"]
        e = evg.get(d)
        t = e["t_s"].to_numpy().astype(np.float64) if e is not None else np.zeros(0)
        a = e["agent"].to_numpy().astype(np.int64) if e is not None else np.zeros(0, np.int64)
        xx = exg[d]["t_s"].to_numpy().astype(np.float64) if d in exg else np.zeros(0)
        xx = xx[xx <= r["T_s"]]
        out[d] = Day(t=t, agent=a, T=float(r["T_s"]), first=bool(r["first_day"]), x=xx,
                     active=act.get(d, np.zeros(0, np.int64)))
    return out


@dataclass
class Spec:
    baseline: str = "B2"         # B0 | B1 | B2 | B3 | B2a (agent-level)
    exo: bool = True
    kick: bool = True
    kernel: str = "exp"          # exp (free beta) | grid | powerlaw | none | selfcross (agent-level grid)
    grid_taus: np.ndarray = field(default_factory=lambda: GRID_TAUS.copy())
    beta_min: float = BETA_MIN   # slowest allowed kernel rate (tau_max = 1/beta_min)
    cell_s: float = BIN_S        # B3 cell width


class Dataset:
    """Assembles the design for a list of day keys (repeats allowed: bootstrap copies are separate realizations)."""

    def __init__(self, daymap: dict[int, Day], keys, spec: Spec):
        self.spec = spec
        days = [daymap[k] for k in keys]
        D = len(days)
        self.D = D
        self.keys = list(keys)
        self.T = np.array([d.T for d in days])
        self.first = np.array([d.first for d in days])
        self.m = np.array([max(len(d.active), 1) for d in days], dtype=float)
        n_per = np.array([len(d.t) for d in days])
        self.n = int(n_per.sum())
        self.t = np.concatenate([d.t for d in days]) if self.n else np.zeros(0)
        self.day = np.repeat(np.arange(D), n_per).astype(np.int64)
        self.agent = np.concatenate([d.agent for d in days]) if self.n else np.zeros(0, np.int64)
        self.u = self.T[self.day] - self.t
        Kb = int(np.ceil(self.T.max() / BIN_S))
        self.Kb_all = Kb
        L = np.clip(self.T[:, None] - BIN_S * np.arange(Kb)[None, :], 0, BIN_S)
        self.L = L
        self.bin = np.minimum((self.t // BIN_S).astype(np.int64), Kb - 1)
        x_list = [d.x for d in days]
        self.x = np.concatenate(x_list) if x_list else np.zeros(0)
        self.gx = np.repeat(np.arange(D), [len(v) for v in x_list]).astype(np.int64)
        self.n_exo_in = int((self.x >= 0).sum())
        agent_level = spec.baseline == "B2a"
        self.agent_level = agent_level

        # ---- baseline units
        b = spec.baseline
        if b == "B0":
            self.unit = np.zeros(self.n, np.int64); self.Lu = self.T.sum()[None, None]; self.shape = False
            self.ubin = np.zeros(self.n, np.int64)
        elif b == "B1":
            self.unit = self.day.copy(); self.Lu = self.T[:, None]; self.shape = False
            self.ubin = np.zeros(self.n, np.int64)
        elif b == "B2":
            self.unit = self.day.copy(); self.Lu = L; self.shape = True; self.ubin = self.bin
        elif b == "B3":
            cw = spec.cell_s
            Kc = int(np.ceil(self.T.max() / cw))
            Lc = np.clip(self.T[:, None] - cw * np.arange(Kc)[None, :], 0, cw)
            cell = self.day * Kc + np.minimum((self.t // cw).astype(np.int64), Kc - 1)
            valid = (Lc.ravel() > 0)
            idx = -np.ones(D * Kc, np.int64); idx[valid] = np.arange(valid.sum())
            self.unit = idx[cell]; self.Lu = Lc.ravel()[valid][:, None]; self.shape = False
            self.ubin = np.zeros(self.n, np.int64)
            self.Kc, self.Lc = Kc, Lc
        elif b == "B2a":
            # unit = (day, active agent)
            pairs = [(i, a) for i, d in enumerate(days) for a in d.active]
            self.unit_day = np.array([p[0] for p in pairs], np.int64)
            self.unit_agent = np.array([p[1] for p in pairs], np.int64)
            key = {p: k for k, p in enumerate(pairs)}
            self.unit = np.array([key[(dd, aa)] for dd, aa in zip(self.day, self.agent)], np.int64)
            self.Lu = L[self.unit_day]; self.shape = True; self.ubin = self.bin
        else:
            raise ValueError(b)
        self.U = self.Lu.shape[0]
        self.Kb = self.Lu.shape[1] if self.shape else 1

        # ---- fixed bases: columns F (n x K) and compensators Z (K)
        mult = self.m if agent_level else np.ones(D)    # how many units each day's shared term reaches
        cols, Z, names = [], [], []
        if spec.kick and self.first.any():
            for tau in KICK_TAUS:
                cols.append(np.where(self.first[self.day], np.exp(-self.t / tau), 0.0))
                Z.append(float((mult * self.first * tau * (1 - np.exp(-self.T / tau))).sum()))
                names.append(f"kick_{int(tau)}")
        if spec.exo and len(self.x):
            for tau in EXO_TAUS:
                dlt = 1.0 / tau
                X = exo_sums(self.t, self.day, self.x, self.gx, dlt) if self.n else np.zeros(0)
                cols.append(dlt * X)
                Gx = np.exp(-dlt * np.maximum(0, -self.x)) - np.exp(-dlt * (self.T[self.gx] - self.x))
                Z.append(float((mult[self.gx] * Gx).sum()))
                names.append(f"exo_{int(tau)}")
        self.n_fixed_nonkernel = len(cols)
        self.grid_cols = []
        if spec.kernel in ("grid", "powerlaw"):
            for tau in spec.grid_taus:
                bt = 1.0 / tau
                cols.append(bt * exp_sums(self.t, self.day, bt)); Z.append(float((1 - np.exp(-bt * self.u)).sum()))
                names.append(f"ker_{int(tau)}")
        elif spec.kernel == "selfcross":
            # sort by (day, agent, t) for own sums
            order = np.lexsort((self.t, self.agent, self.day))
            gown = (self.day * 1000 + self.agent)[order]
            for kind in ("self", "cross"):
                for tau in spec.grid_taus:
                    bt = 1.0 / tau
                    tot = exp_sums(self.t, self.day, bt)
                    own = np.empty(self.n); own[order] = exp_sums(self.t[order], gown, bt)
                    col = own if kind == "self" else np.maximum(tot - own, 0.0)
                    cols.append(bt * col)
                    G = 1 - np.exp(-bt * self.u)
                    Z.append(float(G.sum() if kind == "self" else ((self.m[self.day] - 1) * G).sum()))
                    names.append(f"{kind}_{int(tau)}")
        self.F = np.column_stack(cols) if cols else np.zeros((self.n, 0))
        self.Z = np.array(Z)
        self.names = names
        self.K = self.F.shape[1]
        self.free_beta = spec.kernel == "exp"
        self.powerlaw = spec.kernel == "powerlaw"
        if self.powerlaw:
            self.pl_slice = slice(self.n_fixed_nonkernel, self.K)
            self.logtau = np.log(spec.grid_taus)

    # ------------------------------------------------------------------ parameter layout
    def layout(self):
        sl = {}
        i = 0
        sl["c"] = slice(i, i + self.U); i += self.U
        sl["s"] = slice(i, i + (self.Kb - 1 if self.shape else 0)); i += (self.Kb - 1 if self.shape else 0)
        nk = self.n_fixed_nonkernel if self.powerlaw else self.K
        sl["w"] = slice(i, i + nk); i += nk
        if self.free_beta:
            sl["ab"] = slice(i, i + 2); i += 2
        if self.powerlaw:
            sl["pl"] = slice(i, i + 2); i += 2
        return sl, i

    def init_params(self, beta0=1 / 120.0, alpha0=0.3):
        sl, P = self.layout()
        p = np.zeros(P)
        cnt = np.bincount(self.unit, minlength=self.U).astype(float)
        Ltot = self.Lu.sum(1)
        rate = np.where(cnt > 0, 0.5 * cnt / np.maximum(Ltot, 1.0), 1e-10)
        p[sl["c"]] = np.log(np.maximum(rate, 1e-12))
        if self.shape:
            occ = (self.Lu.sum(0) > 0)
            p[sl["s"]] = np.where(occ[1:], 0.0, -15.0)
        mrate = self.n / max(self.T.sum() * (self.m.mean() if self.agent_level else 1.0), 1.0)
        w0 = []
        for nm in self.names[: (self.n_fixed_nonkernel if self.powerlaw else self.K)]:
            if nm.startswith("kick"):
                w0.append(0.2 * mrate)
            elif nm.startswith("exo"):
                w0.append(0.05)
            else:
                w0.append(alpha0 / max(len(self.spec.grid_taus), 1) / (2 if self.spec.kernel == "selfcross" else 1))
        p[sl["w"]] = np.log(np.maximum(w0, 1e-12))
        if self.free_beta:
            p[sl["ab"]] = [np.log(alpha0), np.log(beta0)]
        if self.powerlaw:
            p[sl["pl"]] = [np.log(alpha0), 0.5]
        return p

    def bounds(self):
        sl, P = self.layout()
        lo = np.full(P, -30.0); hi = np.full(P, 5.0)
        lo[sl["c"]] = -40.0; hi[sl["c"]] = 5.0
        if self.shape:
            lo[sl["s"]] = -25.0; hi[sl["s"]] = 10.0
        if self.free_beta:
            a, b = sl["ab"].start, sl["ab"].start + 1
            lo[a], hi[a] = -20.0, np.log(5.0)
            lo[b], hi[b] = np.log(self.spec.beta_min), np.log(BETA_MAX)
        if self.powerlaw:
            a, th = sl["pl"].start, sl["pl"].start + 1
            lo[a], hi[a] = -20.0, np.log(5.0)
            lo[th], hi[th] = -3.0, 3.0
        return list(zip(lo, hi))

    # ------------------------------------------------------------------ likelihood
    def components(self, p):
        sl, _ = self.layout()
        c = np.exp(p[sl["c"]])
        s = np.concatenate([[1.0], np.exp(p[sl["s"]])]) if self.shape else np.ones(1)
        w = np.exp(p[sl["w"]])
        if self.powerlaw:
            n_, th = np.exp(p[sl["pl"]][0]), p[sl["pl"]][1]
            ww = np.exp(-th * self.logtau); ww /= ww.sum()
            w = np.concatenate([w, n_ * ww])
        return c, s, w

    def loglik(self, p, grad=True):
        sl, P = self.layout()
        c, s, w = self.components(p)
        sb = s[self.ubin] if self.shape else 1.0
        mu = c[self.unit] * sb
        lam = mu + (self.F @ w if self.K else 0.0)
        Ls = self.Lu @ s if self.shape else self.Lu[:, 0]
        comp = c @ Ls + (self.Z @ w if self.K else 0.0)
        if self.free_beta:
            a, b = np.exp(p[sl["ab"]])
            A, B = exp_sums(self.t, self.day, b, want_b=True)
            eb = np.exp(-b * self.u)
            lam = lam + a * b * A
            comp += a * (1 - eb).sum()
        if np.any(lam <= 0):
            lam = np.maximum(lam, 1e-300)
        ll = np.log(lam).sum() - comp
        if not grad:
            return ll
        r = 1.0 / lam
        g = np.zeros(P)
        g[sl["c"]] = c * (np.bincount(self.unit, weights=sb * r, minlength=self.U) - Ls)
        if self.shape:
            gs = np.bincount(self.ubin, weights=c[self.unit] * r, minlength=self.Kb) - c @ self.Lu
            g[sl["s"]] = s[1:] * gs[1:]
        gw = (self.F.T @ r - self.Z) if self.K else np.zeros(0)
        if self.powerlaw:
            nk = self.n_fixed_nonkernel
            g[sl["w"]] = w[:nk] * gw[:nk]
            gm = gw[nk:]
            n_, th = np.exp(p[sl["pl"]][0]), p[sl["pl"]][1]
            ww = np.exp(-th * self.logtau); ww /= ww.sum()
            dw = ww * (-self.logtau + (ww * self.logtau).sum())
            g[sl["pl"].start] = n_ * (ww * gm).sum()
            g[sl["pl"].start + 1] = n_ * (dw * gm).sum()
        else:
            g[sl["w"]] = w * gw
        if self.free_beta:
            g[sl["ab"].start] = a * (b * (A * r).sum() - (1 - eb).sum())
            g[sl["ab"].start + 1] = b * (a * ((A - b * B) * r).sum() - a * (self.u * eb).sum())
        return ll, g

    def fit(self, p0=None, beta_starts=None, maxiter=None, fixed=None, extra_starts=None):
        """fixed: boolean mask of parameters held at their start value (p0 or init)."""
        if self.n == 0:
            return None
        if maxiter is None:
            maxiter = 12000 if self.agent_level else 4000
        starts = []
        if p0 is not None:
            starts.append(p0)
        if extra_starts:
            starts.extend(extra_starts)
        if self.free_beta and beta_starts is not None:
            for b0 in beta_starts:
                st = self.init_params(beta0=b0)
                if fixed is not None and p0 is not None:
                    st[fixed] = p0[fixed]
                starts.append(st)
        if not starts:
            starts.append(self.init_params())
        best = None
        bnds0 = self.bounds()
        for st in starts:
            bnds = list(bnds0)
            st = np.clip(st, [b[0] for b in bnds], [b[1] for b in bnds])
            if fixed is not None:
                for i in np.flatnonzero(fixed):
                    bnds[i] = (st[i], st[i])
            f = lambda q: tuple(-v / self.n for v in self.loglik(q))
            res = optimize.minimize(f, st, jac=True, method="L-BFGS-B", bounds=bnds,
                                    options={"maxiter": maxiter, "maxfun": maxiter * 2, "ftol": 1e-12, "gtol": 1e-7})
            ll = -res.fun * self.n
            if best is None or ll > best[1]:
                best = (res.x, ll, res)
        return FitResult(self, best[0], best[1], best[2])


def transfer_params(src: "FitResult", dst: Dataset, fresh_levels=True):
    """Map a fitted parameter vector onto another Dataset with the same Spec (different days/units).

    Unit levels c are re-initialized from counts (they are per-day nuisance parameters); the shape s, the
    fixed-basis weights (matched by name), and kernel parameters are copied. Returns (p, mask_of_non_c).
    """
    sd, dd = src.ds, dst
    ssl, _ = sd.layout()
    dsl, P = dd.layout()
    p = dd.init_params()
    if dd.shape and sd.shape:
        s_src = np.concatenate([[0.0], src.p[ssl["s"]]])
        occ = sd.Lu.sum(0) > 0
        med = float(np.median(s_src[occ])) if occ.any() else 0.0
        b = np.arange(1, dd.Kb)
        # bins the source never covered (e.g. a test day with a longer window) get the median shape value
        p[dsl["s"]] = np.where(b < sd.Kb, s_src[np.minimum(b, sd.Kb - 1)], med)
    nk_s = sd.n_fixed_nonkernel if sd.powerlaw else sd.K
    nk_d = dd.n_fixed_nonkernel if dd.powerlaw else dd.K
    wmap = dict(zip(sd.names[:nk_s], src.p[ssl["w"]]))
    p[dsl["w"]] = [wmap.get(nm, -30.0) for nm in dd.names[:nk_d]]
    if dd.free_beta:
        p[dsl["ab"]] = src.p[ssl["ab"]]
    if dd.powerlaw:
        p[dsl["pl"]] = src.p[ssl["pl"]]
    mask = np.ones(P, bool)
    mask[dsl["c"]] = False
    return p, mask


def profile_ci_n(fit: "FitResult", level_chi2=3.841):
    """Profile-likelihood CI for n = alpha of a free-beta exponential fit (event-level uncertainty)."""
    from scipy.optimize import brentq
    ds = fit.ds
    sl, P = ds.layout()
    ia = sl["ab"].start
    a_hat = np.exp(fit.p[ia])
    mask = np.zeros(P, bool); mask[ia] = True

    def prof(a):
        p = fit.p.copy(); p[ia] = np.log(a)
        return ds.fit(p0=p, fixed=mask).ll

    def h(a):
        return 2 * (fit.ll - prof(a)) - level_chi2

    lo = hi = np.nan
    try:
        a_lo = 1e-4
        lo = brentq(h, a_lo, a_hat * 0.999, xtol=1e-3) if h(a_lo) > 0 else 0.0
    except Exception:
        pass
    try:
        a_hi = min(4.9, max(2 * a_hat, a_hat + 1.0))
        hi = brentq(h, a_hat * 1.001, a_hi, xtol=1e-3) if h(a_hi) > 0 else np.inf  # censored
    except Exception:
        pass
    return float(lo), float(hi)


def eval_heldout(src: "FitResult", daymap, test_keys):
    """Held-out log-likelihood: refit only the per-unit levels c on the test days, everything else fixed."""
    ds = Dataset(daymap, test_keys, src.ds.spec)
    if ds.n == 0:
        return 0.0, 0
    p, mask = transfer_params(src, ds)
    if ds.shape:
        # MLE puts s_b -> 0 on within-day bins with no training events; floor the transferred shape at 1/20 of
        # its median (same for Hawkes and Poisson) so a test event in such a bin is not scored at ~zero rate
        sl, _ = ds.layout()
        full = np.concatenate([[0.0], p[sl["s"]]])
        p[sl["s"]] = np.maximum(p[sl["s"]], np.median(full) - np.log(20.0))
    f = ds.fit(p0=p, fixed=mask)
    return f.ll, ds.n


@dataclass
class FitResult:
    ds: Dataset
    p: np.ndarray
    ll: float
    res: object

    def summary(self) -> dict:
        ds = self.ds
        sl, P = ds.layout()
        c, s, w = ds.components(self.p)
        out = {"ll": self.ll, "n_events": ds.n, "n_params": P, "converged": bool(self.res.success),
               "n_days": ds.D}
        for nm, val in zip(ds.names, w):
            out[nm] = float(val)
        if ds.free_beta:
            a, b = np.exp(self.p[sl["ab"]])
            out["n"] = float(a); out["beta"] = float(b); out["tau_s"] = float(1 / b)
        elif ds.spec.kernel in ("grid", "powerlaw"):
            kw = w[ds.n_fixed_nonkernel:]
            out["n"] = float(kw.sum())
            out["n_fast300"] = float(kw[ds.spec.grid_taus <= 300].sum())
            out["tau_mean_s"] = float((kw * ds.spec.grid_taus).sum() / max(kw.sum(), 1e-300))
            if ds.powerlaw:
                out["theta"] = float(self.p[sl["pl"]][1])
        elif ds.spec.kernel == "selfcross":
            M = len(ds.spec.grid_taus)
            kw = w[ds.n_fixed_nonkernel:]
            ws, wc = kw[:M], kw[M:]
            mbar1 = float((ds.m[ds.day] - 1).mean()) if ds.n else 0.0
            out["n_self"] = float(ws.sum()); out["n_c_pair"] = float(wc.sum())
            out["n_cross"] = float(wc.sum() * mbar1); out["n"] = out["n_self"] + out["n_cross"]
            out["m_bar"] = mbar1 + 1
            fast = ds.spec.grid_taus <= 300
            out["n_self_fast300"] = float(ws[fast].sum())
            out["n_cross_fast300"] = float(wc[fast].sum() * mbar1)
            out["tau_self_s"] = float((ws * ds.spec.grid_taus).sum() / max(ws.sum(), 1e-300))
            out["tau_cross_s"] = float((wc * ds.spec.grid_taus).sum() / max(wc.sum(), 1e-300))
            for tau, a_, b_ in zip(ds.spec.grid_taus, ws, wc):
                out[f"self_{int(tau)}"] = float(a_); out[f"cross_{int(tau)}"] = float(b_)
        else:
            out["n"] = 0.0
        out["exo_total"] = float(sum(v for k, v in zip(ds.names, w) if k.startswith("exo")))
        return out

    def intensity_parts(self):
        """Per-event (mu, exo+kick, kernel) intensities and the kernel sums A (univariate)."""
        ds = self.ds
        sl, _ = ds.layout()
        c, s, w = ds.components(self.p)
        sb = s[ds.ubin] if ds.shape else 1.0
        mu = c[ds.unit] * sb
        nk = ds.n_fixed_nonkernel
        fixed = ds.F[:, :nk] @ w[:nk] if nk else np.zeros(ds.n)
        if ds.free_beta:
            a, b = np.exp(self.p[sl["ab"]])
            A = exp_sums(ds.t, ds.day, b)
            ker = a * b * A
        else:
            ker = ds.F[:, nk:] @ w[nk:] if ds.K > nk else np.zeros(ds.n)
            A = None
        return mu, fixed, ker, A

    def rescaled_intervals(self):
        """Time-rescaling: compensator increments between consecutive events of each day (univariate fits)."""
        ds = self.ds
        assert not ds.agent_level
        sl, _ = ds.layout()
        c, s, w = ds.components(self.p)
        # baseline cumulative: per-event closed form on 30-min bins
        wgrid, Kg = BIN_S, ds.Kb_all
        if ds.spec.baseline == "B3":
            wgrid, Kg = ds.spec.cell_s, ds.Kc
            valid = ds.Lc.ravel() > 0
            mu_db = np.zeros(ds.D * Kg); mu_db[valid] = c
            mu_db = mu_db.reshape(ds.D, Kg)
        elif ds.shape:
            mu_db = c[:, None] * s[None, :]
            if mu_db.shape[1] < ds.Kb_all:
                mu_db = np.pad(mu_db, ((0, 0), (0, ds.Kb_all - mu_db.shape[1])))
        elif ds.spec.baseline == "B1":
            mu_db = np.repeat(c[:, None], ds.Kb_all, 1)
        else:
            mu_db = np.full((ds.D, ds.Kb_all), c[0])
        cum_full = np.concatenate([np.zeros((ds.D, 1)), np.cumsum(mu_db * wgrid, 1)], 1)
        b_ = np.minimum((ds.t // wgrid).astype(np.int64), Kg - 1)
        lam_base = cum_full[ds.day, b_] + mu_db[ds.day, b_] * (ds.t - b_ * wgrid)
        Lam = lam_base.copy()
        k = 0
        if ds.spec.kick and ds.first.any():
            for tau in KICK_TAUS:
                Lam += np.where(ds.first[ds.day], w[k] * tau * (1 - np.exp(-ds.t / tau)), 0.0); k += 1
        if ds.spec.exo and len(ds.x):
            for tau in EXO_TAUS:
                dlt = 1 / tau
                X = exo_sums(ds.t, ds.day, ds.x, ds.gx, dlt)
                # sum_{x<t} [e^{-dlt max(0,-x)}] - X(t)
                pre = np.zeros(ds.n)
                for d in range(ds.D):
                    xs = ds.x[ds.gx == d]
                    if len(xs) == 0:
                        continue
                    sel = ds.day == d
                    contrib = np.exp(-dlt * np.maximum(0, -xs))
                    cs = np.concatenate([[0], np.cumsum(contrib)])
                    pre[sel] = cs[np.searchsorted(xs, ds.t[sel], side="left")]
                Lam += w[k] * (pre - X); k += 1
        if ds.free_beta:
            a, b = np.exp(self.p[sl["ab"]])
            A = exp_sums(ds.t, ds.day, b)
            first_idx = np.r_[0, np.flatnonzero(np.diff(ds.day)) + 1]
            rank = np.arange(ds.n) - np.repeat(first_idx, np.diff(np.r_[first_idx, ds.n]))
            Lam += a * (rank - A)
        elif ds.K > ds.n_fixed_nonkernel:
            first_idx = np.r_[0, np.flatnonzero(np.diff(ds.day)) + 1]
            rank = np.arange(ds.n) - np.repeat(first_idx, np.diff(np.r_[first_idx, ds.n]))
            for j, tau in enumerate(ds.spec.grid_taus):
                A = exp_sums(ds.t, ds.day, 1 / tau)
                Lam += w[ds.n_fixed_nonkernel + j] * (rank - A)
        new_day = np.r_[True, np.diff(ds.day) != 0]
        prev = np.r_[0.0, Lam[:-1]]
        prev[new_day] = 0.0
        return Lam - prev


def ks_exp1(z):
    r = stats.kstest(z, "expon")
    return float(r.statistic), float(r.pvalue)


# ----------------------------------------------------------------------------------------------- simulation
def _trunc_exp(rng, rate, lo, hi):
    """Samples from Exp(rate) truncated to [lo, hi] (arrays)."""
    u = rng.random(len(lo))
    a = np.exp(-rate * lo); b = np.exp(-rate * hi)
    return -np.log(a - u * (a - b)) / rate


def simulate_univariate(fit: FitResult, rng, n_override=None, beta_override=None, base_scale=1.0,
                        exo_scale=1.0, mu_db_override=None, bin_override=None, kick_scale=None):
    """Simulate pooled event days from a fitted univariate model (B2/B1/B0/B3 baseline, kick, exo, exp kernel).

    Returns dict day_index -> sorted event times. mu_db_override: (D, K) piecewise baseline on bins of bin_override s.
    """
    ds = fit.ds
    sl, _ = ds.layout()
    c, s, w = ds.components(fit.p)
    if ds.free_beta:
        a, b = np.exp(fit.p[sl["ab"]])
    else:
        a, b = 0.0, 1.0
    if n_override is not None:
        a = n_override
    if beta_override is not None:
        b = beta_override
    out = {}
    kick_scale = base_scale if kick_scale is None else kick_scale
    binw = BIN_S if bin_override is None else bin_override
    for d in range(ds.D):
        T = ds.T[d]
        if mu_db_override is not None:
            mu_b = mu_db_override[d]
        elif ds.spec.baseline == "B2":
            mu_b = c[d] * s[: ds.Kb]
        elif ds.spec.baseline == "B1":
            mu_b = np.full(ds.Kb_all, c[d])
        elif ds.spec.baseline == "B0":
            mu_b = np.full(ds.Kb_all, c[0])
        else:
            raise ValueError("simulate from B3 not supported; pass mu_db_override")
        nb = int(np.ceil(T / binw))
        mu_b = np.asarray(mu_b)[:nb] * base_scale
        lens = np.clip(T - binw * np.arange(nb), 0, binw)
        cnt = rng.poisson(mu_b * lens)
        ts = [np.repeat(binw * np.arange(nb), cnt) + rng.random(cnt.sum()) * np.repeat(lens, cnt)]
        k = 0
        if ds.spec.kick and ds.first.any():
            for tau in KICK_TAUS:
                if ds.first[d]:
                    nk = rng.poisson(w[k] * tau * (1 - np.exp(-T / tau)) * kick_scale)
                    ts.append(_trunc_exp(rng, 1 / tau, np.zeros(nk), np.full(nk, T)))
                k += 1
        if ds.spec.exo and len(ds.x):
            xs = ds.x[ds.gx == d]
            for tau in EXO_TAUS:
                dlt = 1 / tau
                if len(xs):
                    lo = np.maximum(0, -xs); hi = T - xs
                    G = np.exp(-dlt * lo) - np.exp(-dlt * hi)
                    nk = rng.poisson(w[k] * G * exo_scale)
                    par = np.repeat(xs, nk)
                    ts.append(par + _trunc_exp(rng, dlt, np.repeat(lo, nk), np.repeat(hi, nk)))
                k += 1
        gen = np.concatenate(ts)
        allt = [gen]
        while len(gen) and a > 0:
            nk = rng.poisson(a, len(gen))
            par = np.repeat(gen, nk)
            ch = par + rng.exponential(1 / b, len(par))
            gen = ch[ch <= T]
            allt.append(gen)
        out[d] = np.sort(np.concatenate(allt))
    return out


def daymap_from_sim(fit: FitResult, sim: dict[int, np.ndarray], template: dict[int, Day]) -> dict:
    ds = fit.ds
    out = {}
    for d, key in enumerate(ds.keys):
        tpl = template[key]
        out[d] = Day(t=sim[d], agent=np.zeros(len(sim[d]), np.int64), T=tpl.T, first=tpl.first, x=tpl.x,
                     active=tpl.active)
    return out


# ----------------------------------------------------------------------------------------------- cascades
def reconstruct_cascades(fit: FitResult, rng, n_samples=5):
    """Sample branching trees from the fitted M1 model; returns cascade sizes (pooled over samples)."""
    ds = fit.ds
    sl, _ = ds.layout()
    mu, fixed, ker, A = fit.intensity_parts()
    lam = mu + fixed + ker
    a, b = np.exp(fit.p[sl["ab"]])
    sizes = []
    for _ in range(n_samples):
        trig = rng.random(ds.n) < ker / lam
        u = np.where(trig, rng.random(ds.n), -1.0)
        parent = sample_parents(ds.t, ds.day, b, A, u)
        root = np.where(parent >= 0, parent, np.arange(ds.n))
        for _ in range(200):
            nr = root[root]
            if np.array_equal(nr, root):
                break
            root = nr
        sizes.append(np.bincount(root, minlength=ds.n)[parent < 0])
    return np.concatenate(sizes)


def borel_pmf(s, n):
    from scipy.special import gammaln
    s = np.asarray(s, float)
    return np.exp(-n * s + (s - 1) * np.log(n * s) - gammaln(s + 1))


def burst_sizes(t, day, gap):
    """Model-free bursts: consecutive events (same day) separated by gaps <= gap."""
    if len(t) == 0:
        return np.zeros(0, int)
    brk = np.r_[True, (np.diff(t) > gap) | (np.diff(day) != 0)]
    ids = np.cumsum(brk) - 1
    return np.bincount(ids)
