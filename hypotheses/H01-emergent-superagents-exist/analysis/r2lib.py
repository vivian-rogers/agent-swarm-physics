"""H01 round 2 estimators: effective superagents in Kolchinsky-Wolpert terms on a substrate of agents.

Shared by analysis/r2_synthetic.py (axis F) and analysis/r2_run.py (real data). Definitions: the card's
"Round 2 formal setup (2026-10-04)", items F1-F9. Thread use is capped at 2 before numpy is imported.

Data model (one unit of analysis = one goal period or sub-unit), class `Period`:
  bins          nB active 30-min bins; day_of_bin[nB], pos_of_bin[nB]
  agents        write-active agent codes (index a = 0..nA-1)
  projects      project ids (index k = 0..nP-1)
  vec[(a, k)]   bool[nB]: agent a wrote (strict) on project k in bin b      (sparse dict over nonzero pairs)
  Wn[nA, nP]    period write counts
  any_w[nA, nB] bool: agent a wrote anything in bin b
  yh[nB]        bool: a human / automated message or a kickoff fell in bin b
  active[nA, nD] bool: agent a acted on day d (any action), used by continuity designs
Units are member index arrays; R_G (shared artifacts) is recomputed for every member set by one rule (F3).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import itertools  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
# Reuse H15's natural-scramble estimators by import (kal counterfactual, unit-pooled placebo, DL meta).
sys.path.insert(0, str(ROOT / "hypotheses/H15-semantic-information-scrambles/analysis"))
sys.path.insert(0, str(ROOT / "hypotheses/H15-semantic-information-scrambles/scheme"))
import h15lib  # noqa: E402,F401

LN2 = math.log(2.0)
SHARE_RULE = 0.5     # R_G: projects with >= 50% of their period writes by members (F3)
MIN_PROJ_WRITES = 3


# ============================================================================ data container
@dataclass
class Period:
    name: str
    regime: str
    day_of_bin: np.ndarray
    pos_of_bin: np.ndarray
    agents: list
    projects: list
    vec: dict
    Wn: np.ndarray
    any_w: np.ndarray
    yh: np.ndarray
    active: np.ndarray
    days: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    @property
    def nB(self):
        return len(self.day_of_bin)

    @property
    def nA(self):
        return len(self.agents)

    def __post_init__(self):
        self.proj_of = {}
        for (a, k) in self.vec:
            self.proj_of.setdefault(a, []).append(k)
        self.tot_k = self.Wn.sum(0)
        self.act_a = self.Wn.sum(1)
        # within-day transition mask (b -> b+1 same day)
        self.trans = np.zeros(self.nB, bool)
        if self.nB > 1:
            self.trans[:-1] = self.day_of_bin[:-1] == self.day_of_bin[1:]
        self.day_slices = []
        for d in np.unique(self.day_of_bin):
            idx = np.flatnonzero(self.day_of_bin == d)
            self.day_slices.append((int(idx[0]), int(idx[-1]) + 1))

    # ---------------------------------------------------------------- unit construction (F3, F4)
    def shared_artifacts(self, members) -> np.ndarray:
        m = np.asarray(members, int)
        own = self.Wn[m].sum(0)
        return np.flatnonzero((self.tot_k >= MIN_PROJ_WRITES) & (own >= SHARE_RULE * self.tot_k) & (own > 0))

    def member_series(self, members, R=None):
        """s_i(b) for each member restricted to R_G; returns (S[n, nB] bool, R)."""
        R = self.shared_artifacts(members) if R is None else R
        Rs = set(int(k) for k in R)
        S = np.zeros((len(members), self.nB), bool)
        for j, a in enumerate(members):
            for k in self.proj_of.get(int(a), []):
                if k in Rs:
                    S[j] |= self.vec[(int(a), k)]
        return S, R

    def env_series(self, members) -> np.ndarray:
        mask = np.ones(self.nA, bool)
        mask[np.asarray(members, int)] = False
        yw = self.any_w[mask].any(0) if mask.any() else np.zeros(self.nB, bool)
        return (yw.astype(np.int8) * 2 + self.yh.astype(np.int8)).astype(np.int8)

    def unit_xy(self, members):
        S, R = self.member_series(members)
        return S.any(0), self.env_series(members), S, R


# ============================================================================ information theory
def _H_counts(c: np.ndarray, mm: bool = True) -> float:
    n = c.sum()
    if n <= 0:
        return 0.0
    p = c[c > 0] / n
    h = float(-(p * np.log2(p)).sum())
    if mm:
        h += (len(p) - 1) / (2 * n * LN2)
    return h


def cond_entropy(target: np.ndarray, cond: np.ndarray, n_t: int, n_c: int, mm: bool = True) -> float:
    """H(T | C) for small integer alphabets, Miller-Madow corrected within each condition."""
    tab = np.zeros((n_c, n_t))
    np.add.at(tab, (cond, target), 1)
    n = tab.sum()
    if n == 0:
        return 0.0
    return float(sum(tab[c].sum() / n * _H_counts(tab[c], mm) for c in range(n_c) if tab[c].sum() > 0))


def individuality(x: np.ndarray, y: np.ndarray, trans: np.ndarray, mm: bool = True) -> dict:
    """F7a. A* = I(x';x|y), E = I(x';y|x), P = I(x';x,y), H = H(x'), iota = A*/H (bits)."""
    idx = np.flatnonzero(trans)
    if len(idx) < 8:
        return {"n": int(len(idx)), "A": np.nan, "E": np.nan, "P": np.nan, "H": np.nan, "iota": np.nan}
    xn = x[idx + 1].astype(int)
    xc = x[idx].astype(int)
    yc = y[idx].astype(int)
    Hx = _H_counts(np.bincount(xn, minlength=2), mm)
    H_y = cond_entropy(xn, yc, 2, 4, mm)
    H_x = cond_entropy(xn, xc, 2, 2, mm)
    H_xy = cond_entropy(xn, xc * 4 + yc, 2, 8, mm)
    A = H_y - H_xy
    E = H_x - H_xy
    P = Hx - H_xy
    iota = A / Hx if Hx > 1e-9 else np.nan
    return {"n": int(len(idx)), "A": float(A), "E": float(E), "P": float(P), "H": float(Hx), "iota": float(iota),
            "rate": float(x.mean())}


# ============================================================================ R4: composition null, local maxima
class NullCache:
    """Random same-size groups of write-active agents, with their activity and individuality (F7a)."""

    def __init__(self, P: Period, n_draw: int = 1500, seed: int = 0):
        self.P = P
        self.n_draw = n_draw
        self.rng = np.random.default_rng(seed)
        self.cache: dict[int, tuple[np.ndarray, np.ndarray]] = {}
        self.pool = np.flatnonzero(P.act_a > 0)

    def draws(self, n: int):
        if n not in self.cache:
            acts, iot = [], []
            if n >= len(self.pool):
                self.cache[n] = (np.array([]), np.array([]))
                return self.cache[n]
            for _ in range(self.n_draw):
                m = self.rng.choice(self.pool, n, replace=False)
                x, y, _, _ = self.P.unit_xy(m)
                r = individuality(x, y, self.P.trans)
                acts.append(self.P.act_a[m].sum())
                iot.append(r["iota"])
            self.cache[n] = (np.asarray(acts, float), np.asarray(iot, float))
        return self.cache[n]

    def z(self, n: int, act: float, iota: float):
        acts, iot = self.draws(n)
        if len(acts) == 0 or not np.isfinite(iota):
            return np.nan, np.nan, np.nan
        ok = np.isfinite(iot)
        acts, iot = acts[ok], iot[ok]
        sel = (acts >= 0.5 * act) & (acts <= 1.5 * act)
        if sel.sum() < 50:
            sel = np.zeros(len(acts), bool)
            sel[np.argsort(np.abs(acts - act))[:100]] = True
        v = iot[sel]
        sd = v.std(ddof=1)
        if sd <= 1e-9:
            return np.nan, float(v.mean()), float(sd)
        return float((iota - v.mean()) / sd), float(v.mean()), float(sd)


def composition_excess(P: Period, members, nc: NullCache):
    x, y, S, R = P.unit_xy(members)
    r = individuality(x, y, P.trans)
    z, mu, sd = nc.z(len(members), P.act_a[np.asarray(members, int)].sum(), r["iota"])
    r.update({"z": z, "null_mu": mu, "null_sd": sd, "n_members": len(members), "n_R": int(len(R))})
    return r


def local_max(P: Period, members, nc: NullCache, z0: float, max_add: int = 40):
    """Is the unit's composition excess >= that of every one-member addition / removal? Returns (is_max, frac_beaten)."""
    if not np.isfinite(z0):
        return None, np.nan
    m = list(int(a) for a in members)
    neigh = []
    if len(m) > 1:
        for a in m:
            neigh.append([b for b in m if b != a])
    others = [int(a) for a in nc.pool if int(a) not in m]
    for a in others[:max_add]:
        neigh.append(m + [a])
    zs = []
    for g in neigh:
        x, y, _, _ = P.unit_xy(g)
        r = individuality(x, y, P.trans)
        z, _, _ = nc.z(len(g), P.act_a[np.asarray(g, int)].sum(), r["iota"])
        if np.isfinite(z):
            zs.append(z)
    if not zs:
        return None, np.nan
    zs = np.asarray(zs)
    return bool((z0 >= zs).all()), float((z0 >= zs).mean())


def shift_excess(P: Period, members, n_draw: int = 200, seed: int = 0):
    """Substrate (coordination) excess: iota minus its mean under within-day rotation of each member's series."""
    rng = np.random.default_rng(seed)
    S, R = P.member_series(members)
    y = P.env_series(members)
    x = S.any(0)
    r0 = individuality(x, y, P.trans)
    if not np.isfinite(r0["iota"]) or len(members) < 2:
        return {"iota": r0["iota"], "shift_mu": np.nan, "shift_sd": np.nan, "excess": np.nan, "z": np.nan}
    vals = []
    for _ in range(n_draw):
        Sx = np.zeros_like(S)
        for (lo, hi) in P.day_slices:
            L = hi - lo
            for j in range(S.shape[0]):
                Sx[j, lo:hi] = np.roll(S[j, lo:hi], rng.integers(0, L)) if L > 1 else S[j, lo:hi]
        vals.append(individuality(Sx.any(0), y, P.trans)["iota"])
    vals = np.asarray(vals, float)
    vals = vals[np.isfinite(vals)]
    mu, sd = float(vals.mean()), float(vals.std(ddof=1))
    return {"iota": r0["iota"], "shift_mu": mu, "shift_sd": sd, "excess": float(r0["iota"] - mu),
            "z": float((r0["iota"] - mu) / sd) if sd > 1e-9 else np.nan}


# ============================================================================ coarse-grainings (F3)
def greedy_modularity(Wsym: np.ndarray) -> list[list[int]]:
    """Clauset-Newman-Moore greedy agglomeration on a small weighted undirected graph (networkx is not installed)."""
    n = Wsym.shape[0]
    W = Wsym.astype(float).copy()
    np.fill_diagonal(W, 0)
    m2 = W.sum()
    if m2 <= 0:
        return [[i] for i in range(n)]
    comms = {i: [i] for i in range(n)}
    k = W.sum(1)

    def Q(cs):
        q = 0.0
        for c in cs:
            c = np.asarray(c)
            q += W[np.ix_(c, c)].sum() / m2 - (k[c].sum() / m2) ** 2
        return q

    cur = list(comms.values())
    best_q, best = Q(cur), [list(c) for c in cur]
    while len(cur) > 1:
        bq, bpair = -1e9, None
        for i, j in itertools.combinations(range(len(cur)), 2):
            a, b = np.asarray(cur[i]), np.asarray(cur[j])
            if W[np.ix_(a, b)].sum() <= 0:
                continue
            dq = 2 * (W[np.ix_(a, b)].sum() / m2 - (k[a].sum() / m2) * (k[b].sum() / m2))
            if dq > bq:
                bq, bpair = dq, (i, j)
        if bpair is None:
            break
        i, j = bpair
        merged = cur[i] + cur[j]
        cur = [c for t, c in enumerate(cur) if t not in (i, j)] + [merged]
        q = Q(cur)
        if q > best_q:
            best_q, best = q, [list(c) for c in cur]
    return best


def crews(P: Period, min_writers: int = 2, min_writes: int = 10, min_member_writes: int = 2):
    out, seen = [], set()
    for k in range(len(P.projects)):
        if P.tot_k[k] < min_writes:
            continue
        mem = tuple(sorted(int(a) for a in np.flatnonzero(P.Wn[:, k] >= min_member_writes)))
        if len(mem) < min_writers or mem in seen:
            continue
        seen.add(mem)
        out.append({"members": list(mem), "seed_project": P.projects[k]})
    return out


# ============================================================================ R5: KW stored / observed semantic information
def set_partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in set_partitions(rest):
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i + 1:]
        yield [[first]] + part


PARTS4 = list(set_partitions([0, 1, 2, 3]))   # 15 coarse-grainings f of the y alphabet


def _mi_joint(p: np.ndarray) -> float:
    """I(X;Y) in bits for a joint table p[x, y]."""
    px, py = p.sum(1, keepdims=True), p.sum(0, keepdims=True)
    m = p > 0
    return float((p[m] * np.log2(p[m] / (px @ py)[m])).sum())


def coarse_grain(p: np.ndarray, part) -> np.ndarray:
    """KW stored intervention p^f(x, y) = p(y) p(x | f(y))."""
    q = np.zeros_like(p)
    py = p.sum(0)
    for cell in part:
        c = list(cell)
        pc = py[c].sum()
        if pc <= 0:
            continue
        px_c = p[:, c].sum(1) / pc
        for y in c:
            q[:, y] = px_c * py[y]
    return q


@dataclass
class Kernel:
    Kx: np.ndarray   # [x, y, x']
    Ky: np.ndarray   # [y, x, y']
    nx: np.ndarray   # transition counts out of (x, y)


def fit_kernel(trans_list, alpha: float = 0.5, prior: Kernel | None = None, prior_w: float = 8.0) -> Kernel:
    """Factorized Markov kernel on z = (x, y): K_x(x'|x,y) K_y(y'|y,x). trans_list: arrays (x, y, x', y')."""
    cx = np.zeros((2, 4, 2))
    cy = np.zeros((4, 2, 4))
    for (x0, y0, x1, y1) in trans_list:
        np.add.at(cx, (x0, y0, x1), 1)
        np.add.at(cy, (y0, x0, y1), 1)
    raw_n = cx.sum(-1).copy()
    if prior is not None:
        cx = cx + prior_w * prior.Kx
        cy = cy + prior_w * prior.Ky
    Kx = (cx + alpha) / (cx + alpha).sum(-1, keepdims=True)
    Ky = (cy + alpha) / (cy + alpha).sum(-1, keepdims=True)
    return Kernel(Kx, Ky, raw_n)


def propagate(p0: np.ndarray, K: Kernel, tau: int, observed_scramble: bool = False) -> float:
    """V = mean_{h=1..tau} P(x_h = 1) starting from p0[x, y]."""
    p = p0.copy()
    v = 0.0
    for _ in range(tau):
        if observed_scramble:
            # X no longer reads the current y beyond its correlation with x (KW observed intervention)
            px = p.sum(1, keepdims=True)
            pyx = np.where(px > 0, p / np.maximum(px, 1e-15), 0.25)
            Kx = np.einsum("xy,xyz->xz", pyx, K.Kx)[:, None, :].repeat(4, 1)
        else:
            Kx = K.Kx
        # p'(x', y') = sum_{x,y} p(x,y) Kx(x'|x,y) Ky(y'|y,x)
        p = np.einsum("xy,xyu,yxv->uv", p, Kx, K.Ky)
        v += p[1].sum()
    return v / tau


def transitions_from_units(units_xy, trans: np.ndarray, tau: int):
    """Pooled within-day transitions and start-of-horizon (x, y) pairs (bins with >= tau bins left in the day)."""
    T, starts = [], []
    for (x, y, day) in units_xy:
        idx = np.flatnonzero(trans)
        if len(idx):
            T.append(np.stack([x[idx].astype(int), y[idx].astype(int), x[idx + 1].astype(int),
                               y[idx + 1].astype(int)], 1))
        # starts: bin b such that b+tau is the same day
        nB = len(x)
        ok = np.zeros(nB, bool)
        if nB > tau:
            ok[:-tau] = day[:-tau] == day[tau:]
        s = np.flatnonzero(ok)
        if len(s):
            starts.append(np.stack([x[s].astype(int), y[s].astype(int)], 1))
    T = np.concatenate(T) if T else np.zeros((0, 4), int)
    S = np.concatenate(starts) if starts else np.zeros((0, 2), int)
    return T, S


def kw_from(T: np.ndarray, S: np.ndarray, tau: int, prior: Kernel | None = None, frac: float = 0.9) -> dict:
    if len(T) < 20 or len(S) < 10:
        return {"ok": False, "n_trans": int(len(T))}
    K = fit_kernel([(T[:, 0], T[:, 1], T[:, 2], T[:, 3])], prior=prior)
    p0 = np.zeros((2, 4))
    np.add.at(p0, (S[:, 0], S[:, 1]), 1)
    p0 /= p0.sum()
    I = _mi_joint(p0)
    V = propagate(p0, K, tau)
    full = np.outer(p0.sum(1), p0.sum(0))
    Vf = propagate(full, K, tau)
    dV = V - Vf
    curve = []
    for part in PARTS4:
        q = coarse_grain(p0, part)
        curve.append((_mi_joint(q), propagate(q, K, tau), len(part)))
    S_st = np.nan
    if dV > 0:
        okc = [c for c in curve if c[1] - Vf >= frac * dV]
        S_st = min(c[0] for c in okc) if okc else I
    Vobs = propagate(p0, K, tau, observed_scramble=True)
    # positivity: share of the scrambled mass on cells with < 5 transitions
    low = K.nx < 5
    pos = float(full[low].sum())
    # transfer entropy Y->X and Pinsker envelope
    xn, xc, yc = T[:, 2], T[:, 0], T[:, 1]
    te = cond_entropy(xn, xc, 2, 2) - cond_entropy(xn, xc * 4 + yc, 2, 8)
    return {"ok": True, "n_trans": int(len(T)), "n_start": int(len(S)), "I": I, "V": V, "V_full": Vf, "dV_st": dV,
            "S_st": S_st, "eta": (S_st / I) if (np.isfinite(S_st) and I > 1e-12) else np.nan,
            "kappa": dV / I if I > 1e-12 else np.nan, "pinsker": math.sqrt(max(I, 0) * LN2 / 2),
            "dV_obs": V - Vobs, "TE": te, "positivity_low_mass": pos, "curve": curve,
            "V_emp_check": None}


def kw_semantic(units_xy, trans: np.ndarray, tau: int = 4, prior: Kernel | None = None, n_boot: int = 200,
                seed: int = 0) -> dict:
    """KW stored and observed semantic information for a coarse-graining in one period (F7b), with a cluster
    bootstrap over unit-days."""
    T, S = transitions_from_units(units_xy, trans, tau)
    est = kw_from(T, S, tau, prior)
    if not est.get("ok"):
        return est
    # empirical model check: mean x over the next tau bins from start bins vs model V
    emp = []
    for (x, y, day) in units_xy:
        nB = len(x)
        ok = np.zeros(nB, bool)
        if nB > tau:
            ok[:-tau] = day[:-tau] == day[tau:]
        for s in np.flatnonzero(ok):
            emp.append(x[s + 1:s + tau + 1].mean())
    est["V_emp"] = float(np.mean(emp)) if emp else np.nan
    # two-step Chapman-Kolmogorov error for x
    est["ck_err"] = ck_error(units_xy, trans, prior)
    # bootstrap over unit-days
    rng = np.random.default_rng(seed)
    clusters = []
    for (x, y, day) in units_xy:
        for d in np.unique(day):
            m = day == d
            clusters.append((x[m], y[m], day[m]))
    boots = {"dV_st": [], "dV_obs": [], "I": [], "eta": []}
    for _ in range(n_boot):
        pick = rng.integers(0, len(clusters), len(clusters))
        sub = [clusters[i] for i in pick]
        tr = [np.ones(len(c[0]), bool) for c in sub]
        for t in tr:
            t[-1] = False
        Tb, Sb = [], []
        for (c, t) in zip(sub, tr):
            T1, S1 = transitions_from_units([c], t, tau)
            Tb.append(T1)
            Sb.append(S1)
        Tb = np.concatenate(Tb)
        Sb = np.concatenate(Sb)
        r = kw_from(Tb, Sb, tau, prior)
        if r.get("ok"):
            for k in boots:
                boots[k].append(r[k])
    for k, v in boots.items():
        v = np.asarray(v, float)
        v = v[np.isfinite(v)]
        if len(v) >= 20:
            est[k + "_lo"], est[k + "_hi"] = float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))
            est[k + "_se"] = float(v.std(ddof=1))
    est.pop("curve_raw", None)
    return est


def ck_error(units_xy, trans, prior=None) -> float:
    """Mean |P2_model(x_{b+2}=1 | x_b, y_b) - P2_emp| over (x, y) cells with >= 10 two-step samples."""
    T, _ = transitions_from_units(units_xy, trans, 1)
    if len(T) < 30:
        return np.nan
    K = fit_kernel([(T[:, 0], T[:, 1], T[:, 2], T[:, 3])], prior=prior)
    cnt = np.zeros((2, 4, 2))
    for (x, y, day) in units_xy:
        nB = len(x)
        if nB < 3:
            continue
        ok = (day[:-2] == day[2:])
        s = np.flatnonzero(ok)
        np.add.at(cnt, (x[s].astype(int), y[s].astype(int), x[s + 2].astype(int)), 1)
    errs = []
    for xx in range(2):
        for yy in range(4):
            n = cnt[xx, yy].sum()
            if n < 10:
                continue
            p0 = np.zeros((2, 4))
            p0[xx, yy] = 1
            p1 = np.einsum("xy,xyu,yxv->uv", p0, K.Kx, K.Ky)
            p2 = np.einsum("xy,xyu,yxv->uv", p1, K.Kx, K.Ky)
            errs.append(abs(p2[1].sum() - cnt[xx, yy, 1] / n))
    return float(np.mean(errs)) if errs else np.nan


def kw_day_landscape(x0: np.ndarray, y0: np.ndarray, v: np.ndarray, shrink: float = 2.0, frac: float = 0.9) -> dict:
    """Day-level landscape variant: v(x0, y0) = E[V_adv(d+1) | x0, y0] by shrunken cell means; KW stored quantities
    by reweighting (the 'landscape trick'): dV = sum (p - p_x p_y) v = E_p[(1 - e^{-PMI}) v]."""
    if len(v) < 30:
        return {"ok": False, "n": int(len(v))}
    p = np.zeros((2, 4))
    np.add.at(p, (x0, y0), 1)
    p /= p.sum()
    gm = float(v.mean())
    land = np.full((2, 4), gm)
    for a in range(2):
        for b in range(4):
            m = (x0 == a) & (y0 == b)
            land[a, b] = (v[m].sum() + shrink * gm) / (m.sum() + shrink)
    V = float((p * land).sum())
    full = np.outer(p.sum(1), p.sum(0))
    Vf = float((full * land).sum())
    dV = V - Vf
    I = _mi_joint(p)
    S_st = np.nan
    if dV > 0:
        okc = [(_mi_joint(q), float((q * land).sum())) for q in (coarse_grain(p, part) for part in PARTS4)]
        okc = [c for c in okc if c[1] - Vf >= frac * dV]
        S_st = min(c[0] for c in okc) if okc else I
    return {"ok": True, "n": int(len(v)), "I": I, "V": V, "V_full": Vf, "dV_st": dV, "S_st": S_st,
            "eta": S_st / I if (np.isfinite(S_st) and I > 1e-12) else np.nan, "pinsker": math.sqrt(max(I, 0) * LN2 / 2)}


# ============================================================================ R6: night continuity
def night_continuity(P: Period, crew_list, wrote_day: np.ndarray, n_perm: int = 500, seed: int = 0) -> dict:
    """F7d. wrote_day[a, k, d] bool (agent a wrote project k on day d). Continuity of crew members across nights vs a
    null that permutes the day-(d+1) project sets among agents active on both days."""
    rng = np.random.default_rng(seed)
    nD = wrote_day.shape[2]
    hits, n_tot = 0, 0
    null_hits = np.zeros(n_perm)
    per_pair = []
    for d in range(nD - 1):
        both = np.flatnonzero(P.active[:, d] & P.active[:, d + 1])
        if len(both) < 3:
            continue
        nxt = wrote_day[both, :, d + 1]           # [n_both, nP]
        pos = {int(a): j for j, a in enumerate(both)}
        Hm = np.zeros((len(both), len(crew_list)), bool)
        Ms = []
        for g, c in enumerate(crew_list):
            R = c["R"]
            if len(R) == 0:
                Ms.append([])
                continue
            Hm[:, g] = nxt[:, R].any(1)
            M = [pos[int(a)] for a in c["members"] if int(a) in pos and wrote_day[int(a), R, d].any()]
            Ms.append(M)
        tot = sum(len(M) for M in Ms)
        if tot == 0:
            continue
        h = sum(Hm[M, g].sum() for g, M in enumerate(Ms))
        hits += h
        n_tot += tot
        for t in range(n_perm):
            perm = rng.permutation(len(both))
            null_hits[t] += sum(Hm[perm[M], g].sum() for g, M in enumerate(Ms) if M)
        per_pair.append((d, int(h), int(tot)))
    if n_tot == 0:
        return {"ok": False}
    C = hits / n_tot
    Cn = null_hits / n_tot
    return {"ok": True, "C": float(C), "C_null": float(Cn.mean()), "dC": float(C - Cn.mean()),
            "p": float((Cn >= C).mean()), "n": int(n_tot), "pairs": per_pair}


# ============================================================================ R6/R8: event-time designs at minute resolution
def event_profile(event_t: np.ndarray, series_t: np.ndarray, pre=(-10.0, -5.0), post=(0.0, 5.0)) -> tuple:
    """Counts of series events in [t+post) and [t+pre) for each event time t (minutes on a common clock)."""
    series_t = np.sort(series_t)
    def cnt(lo, hi):
        return np.searchsorted(series_t, event_t + hi, "left") - np.searchsorted(series_t, event_t + lo, "left")
    return cnt(*post).astype(float), cnt(*pre).astype(float)


def rotate_times(t: np.ndarray, day_bounds: list[tuple[float, float]], rng) -> np.ndarray:
    """Rotate event times within their day window by one random offset per day (keeps counts, breaks alignment)."""
    out = t.copy()
    for (lo, hi) in day_bounds:
        m = (t >= lo) & (t < hi)
        if m.any():
            L = hi - lo
            out[m] = lo + ((t[m] - lo + rng.uniform(0, L)) % L)
    return out


def spillover(events: list[dict], n_rot: int = 200, seed: int = 0, pre=(-10.0, -5.0), post=(0.0, 5.0)) -> dict:
    """events: per (crew, member) dicts with keys t_cons (member's forced consolidations), w_self (member's writes on
    R_G), w_other (other members' writes on R_G), day_bounds. Difference-in-differences of post - pre counts at real
    vs rotated consolidation times. Returns self and others' effects and base rates (per 5 min)."""
    rng = np.random.default_rng(seed)
    real = {"self": [], "other": []}
    base = {"self": [], "other": []}
    rot = {"self": np.zeros(n_rot), "other": np.zeros(n_rot)}
    n_ev = 0
    for e in events:
        t = np.asarray(e["t_cons"], float)
        # A1.3: edge trimming (no consolidation can fall in a day's first minutes, so untrimmed rotated events whose
        # pre-window starts before the day get spurious post - pre > 0); same rule for real and rotated times
        keep = np.zeros(len(t), bool)
        for (lo, hi) in e["day_bounds"]:
            keep |= (t >= lo - pre[0]) & (t < hi - post[1])
        t = t[keep]
        if len(t) == 0:
            continue
        n_ev += len(t)
        for key, s in (("self", e["w_self"]), ("other", e["w_other"])):
            s = np.asarray(s, float)
            po, pr = event_profile(t, s, pre, post)
            real[key].append((po - pr).sum())
            # base rate: writes per 5 min of window time
            tot_min = sum(hi - lo for lo, hi in e["day_bounds"])
            base[key].append(len(s) / max(tot_min, 1) * 5 * len(t))
            for r in range(n_rot):
                tr = rotate_times(t, [(lo - pre[0], hi - post[1]) for lo, hi in e["day_bounds"]], rng)
                po2, pr2 = event_profile(tr, s, pre, post)
                rot[key][r] += (po2 - pr2).sum()
    if n_ev == 0:
        return {"ok": False}
    out = {"ok": True, "n_events": int(n_ev)}
    for key in ("self", "other"):
        R = float(np.sum(real[key]))
        B = float(np.sum(base[key]))
        eff = (R - rot[key].mean()) / n_ev
        sd = rot[key].std(ddof=1) / n_ev
        out[key] = {"effect_per_event": eff, "z": eff / sd if sd > 0 else np.nan,
                    "base_per_event": B / n_ev, "rel": eff / (B / n_ev) if B > 0 else np.nan,
                    "p_two": float((np.abs(rot[key] - rot[key].mean()) >= abs(R - rot[key].mean())).mean())}
    return out


def stouffer(zs) -> tuple[float, float]:
    from scipy.stats import norm
    z = np.asarray([v for v in zs if np.isfinite(v)], float)
    if len(z) == 0:
        return np.nan, np.nan
    Z = z.sum() / math.sqrt(len(z))
    return float(Z), float(norm.sf(Z))


# ============================================================================ amendment A1 (after the synthetic, before real data)
def alloc_individuality(P: Period, members, mm: bool = True) -> dict:
    """iota_alloc: how much the rest of the unit's state tells each member's next state beyond the member's own past
    and the environment, pooled over members: I(s_i(b+1); x_{G\\i}(b) | s_i(b), y_i(b)) / H(s_i(b+1)).
    y_i = (a non-member wrote anything, human/automated message). The unit acting on its parts through the shared
    artifact and channel (members re-acquire the artifact the others are on); zero for independent members."""
    S, R = P.member_series(members)
    if len(members) < 2 or len(R) == 0:
        return {"iota_alloc": np.nan, "TE_alloc": np.nan, "n": 0}
    y = P.env_series(members)
    idx = np.flatnonzero(P.trans)
    tn, sc, oc, yc = [], [], [], []
    for j in range(len(members)):
        others = np.delete(S, j, 0).any(0)
        tn.append(S[j, idx + 1]); sc.append(S[j, idx]); oc.append(others[idx]); yc.append(y[idx])
    tn = np.concatenate(tn).astype(int); sc = np.concatenate(sc).astype(int)
    oc = np.concatenate(oc).astype(int); yc = np.concatenate(yc).astype(int)
    if len(tn) < 16 or tn.sum() == 0:
        return {"iota_alloc": np.nan, "TE_alloc": np.nan, "n": int(len(tn))}
    h1 = cond_entropy(tn, sc * 4 + yc, 2, 8, mm)
    h2 = cond_entropy(tn, (sc * 4 + yc) * 2 + oc, 2, 16, mm)
    Hs = _H_counts(np.bincount(tn, minlength=2), mm)
    te = h1 - h2
    return {"TE_alloc": float(te), "iota_alloc": float(te / Hs) if Hs > 1e-9 else np.nan, "n": int(len(tn))}


class NullCacheAlloc(NullCache):
    """Random activity-matched same-size groups for iota_alloc (R_G recomputed by the F3 rule)."""

    def draws(self, n: int):
        if n not in self.cache:
            acts, iot = [], []
            if n >= len(self.pool):
                self.cache[n] = (np.array([]), np.array([]))
                return self.cache[n]
            for _ in range(self.n_draw):
                m = self.rng.choice(self.pool, n, replace=False)
                acts.append(self.P.act_a[m].sum())
                iot.append(alloc_individuality(self.P, m)["iota_alloc"])
            self.cache[n] = (np.asarray(acts, float), np.asarray(iot, float))
        return self.cache[n]


def alloc_shift(P: Period, members, n_draw: int = 100, seed: int = 0) -> dict:
    """iota_alloc against within-day rotation of each member's series (keeps own persistence, breaks alignment)."""
    rng = np.random.default_rng(seed)
    S, R = P.member_series(members)
    r0 = alloc_individuality(P, members)
    if not np.isfinite(r0["iota_alloc"]):
        return {"iota_alloc": np.nan, "shift_mu": np.nan, "z": np.nan}
    y = P.env_series(members)
    idx = np.flatnonzero(P.trans)
    vals = []
    for _ in range(n_draw):
        Sx = np.zeros_like(S)
        for (lo, hi) in P.day_slices:
            L = hi - lo
            for j in range(S.shape[0]):
                Sx[j, lo:hi] = np.roll(S[j, lo:hi], rng.integers(0, L)) if L > 1 else S[j, lo:hi]
        tn, sc, oc, yc = [], [], [], []
        for j in range(len(members)):
            others = np.delete(Sx, j, 0).any(0)
            tn.append(Sx[j, idx + 1]); sc.append(Sx[j, idx]); oc.append(others[idx]); yc.append(y[idx])
        tn = np.concatenate(tn).astype(int); sc = np.concatenate(sc).astype(int)
        oc = np.concatenate(oc).astype(int); yc = np.concatenate(yc).astype(int)
        Hs = _H_counts(np.bincount(tn, minlength=2))
        te = cond_entropy(tn, sc * 4 + yc, 2, 8) - cond_entropy(tn, (sc * 4 + yc) * 2 + oc, 2, 16)
        vals.append(te / Hs if Hs > 1e-9 else np.nan)
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    mu, sd = float(v.mean()), float(v.std(ddof=1))
    return {"iota_alloc": r0["iota_alloc"], "shift_mu": mu, "excess": r0["iota_alloc"] - mu,
            "z": float((r0["iota_alloc"] - mu) / sd) if sd > 1e-9 else np.nan}


def simulate_kernel_chain(K: Kernel, p0: np.ndarray, n_units: int, n_days: int, bins_per_day: int, rng) -> list:
    """Draw (x, y, day) series from a known factorized kernel (for estimator recovery tests)."""
    out = []
    for _ in range(n_units):
        xs, ys, ds = [], [], []
        for d in range(n_days):
            c = rng.choice(8, p=p0.reshape(-1))
            x, y = divmod(c, 4)
            for b in range(bins_per_day):
                xs.append(x); ys.append(y); ds.append(d)
                x1 = int(rng.random() < K.Kx[x, y, 1])
                y1 = rng.choice(4, p=K.Ky[y, x])
                x, y = x1, y1
        out.append((np.array(xs), np.array(ys), np.array(ds)))
    return out
