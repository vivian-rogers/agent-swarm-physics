"""H39 estimators: field (occupancy shift) vs catalytic (escape at fixed occupancy) effects of levers.

Works on synthetic and real data alike. A *unit* is a set of agent-day state sequences (categorical, q states)
concatenated into one array, plus lever events (global minute indices) per class.

Point levers (kicks): episode windows [g+1, g+W] after an event at minute g vs matched control windows
(same agent, same start state, same dwell-age bin, same day third; no kick nearby). Step levers: pre days vs
post days (balanced agent panel), judged against within-goal day-boundary placebos.

Statistics (see the card):
  pi^K, pi^C   stationary distributions of the kicked / control lag-1 transition matrices
  dpi          pi^K - pi^C (signed, per state);  DF = TV(pi^K, pi^C)
  phi          pi^C-weighted SD of delta ln pi (units of T: RMS change in well depth)
  K            ln[ sum_s pi^C_s e^K_s / sum_s pi^C_s e^C_s ], e_s = 1 - T_ss (escape at fixed occupancy)
  ksym         control-traffic-weighted mean of the symmetric log-rate change s_ij
  esc          ln(e^K_s / e^C_s) per state
  docc         transient occupancy over the windows, kicked - control (descriptive)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H39-catalysts-vs-fields"
HDIR = ROOT / "hypotheses/H39-catalysts-vs-fields"
SEED = 20261004

W_DEFAULT = 30          # episode window (min)
QUIET = 30              # quiet minutes required before an episode or a control minute (>= W: no lingering effects)
R_CTRL = 10             # controls per episode
AGE_EDGES = np.array([1, 2, 5, 15])  # dwell-age bins: 1, 2-4, 5-14, >=15
LAMBDA = 1.0            # pseudo-transitions per row (shrinkage toward the unit's pooled T)
MIN_EP = 20             # powered unit threshold (episodes)
THR = 0.10              # effect-size threshold for phi_exc and |K|

# Round 1b (2026-10-04): DQ8 `nulls.lever_design` rules. Round 1 required the whole W-minute window to fit inside the
# agent's present span for episodes and controls (conditioning on future presence); with presence_cut the window only
# needs one transition and is cut at the end of presence (transition counts were already cut there; occupancy now too).
# Past-only eligibility and next-kick cuts for transition statistics are unchanged (they already follow lever_design).
LEVER = {"presence_cut": False}


# =============================================================================== unit container

@dataclass
class Unit:
    """Concatenated agent-day sequences. Segments never share transitions."""
    q: int
    x: np.ndarray                 # int8 states, -1 = missing (content windows)
    seg_start: np.ndarray         # int64
    seg_end: np.ndarray           # int64 (exclusive)
    seg_agent: np.ndarray         # int32
    seg_day: np.ndarray           # int32 (index into a day list)
    third: np.ndarray             # int8 day third of every minute
    events: dict = field(default_factory=dict)   # class -> sorted global indices
    busy: np.ndarray | None = None               # bool: a directed/human kick lands in this minute
    names: list | None = None
    swarm: np.ndarray | None = None              # int8 swarm-activity bin of the other agents at this minute

    def __post_init__(self):
        n = len(self.x)
        self.agent = np.repeat(self.seg_agent, self.seg_end - self.seg_start).astype(np.int32)
        self.day = np.repeat(self.seg_day, self.seg_end - self.seg_start).astype(np.int32)
        self.seg_of = np.repeat(np.arange(len(self.seg_start)), self.seg_end - self.seg_start)
        self.pos = np.arange(n) - self.seg_start[self.seg_of]          # minute within segment
        self.left = self.seg_end[self.seg_of] - 1 - np.arange(n)       # minutes to segment end
        if self.busy is None:
            self.busy = np.zeros(n, bool)
        # transition one-hot cumulative counts: transition (x[g], x[g+1]) stored at g
        q = self.q
        tt = np.full(n, -1, np.int64)
        ok = (self.left >= 1)
        nxt = np.r_[self.x[1:], -1]
        ok &= (self.x >= 0) & (nxt >= 0)
        tt[ok] = self.x[ok].astype(np.int64) * q + nxt[ok]
        self.tt = tt
        oh = np.zeros((n + 1, q * q), np.int32)
        idx = np.flatnonzero(ok)
        oh[idx + 1, tt[idx]] = 1
        self.cum = np.cumsum(oh, axis=0, dtype=np.int32)
        # occupancy cumulative (for transient occupancy)
        oc = np.zeros((n + 1, q), np.int32)
        v = np.flatnonzero(self.x >= 0)
        oc[v + 1, self.x[v]] = 1
        self.ocum = np.cumsum(oc, axis=0, dtype=np.int32)
        # dwell age (run length including this minute)
        same = np.r_[False, (self.x[1:] == self.x[:-1]) & (self.pos[1:] > 0)]
        brk = ~same
        run_id = np.cumsum(brk) - 1
        run_start = np.flatnonzero(brk)
        age = np.arange(n) - run_start[run_id] + 1
        self.age = age.astype(np.int32)
        self.agebin = (np.searchsorted(AGE_EDGES, self.age, side="right") - 1).astype(np.int8)
        self.busy_cum = np.r_[0, np.cumsum(self.busy.astype(np.int32))]
        if self.swarm is None:
            self.swarm = np.zeros(n, np.int8)

    # ------------------------------------------------------------------ windows
    def win_counts(self, g: np.ndarray, W: int, lag: int = 1) -> np.ndarray:
        """Transition counts for transitions starting at g+1 .. g+W-1 (lag 1). Shape (len(g), q*q)."""
        return self.cum[g + W] - self.cum[g + 1]

    def next_busy(self, g: np.ndarray) -> np.ndarray:
        """First busy minute strictly after g (or the segment end)."""
        bi = np.flatnonzero(self.busy)
        j = np.searchsorted(bi, g, side="right")
        nb = np.where(j < len(bi), bi[np.minimum(j, max(len(bi) - 1, 0))] if len(bi) else 0, len(self.x))
        return np.minimum(nb, self.seg_end[self.seg_of[g]])

    def win_counts_trunc(self, g: np.ndarray, W: int) -> np.ndarray:
        """Transitions starting at g+1 .. min(g+W, next busy)-1: the window is cut where the next kick lands."""
        end = np.minimum(g + W, self.next_busy(g))
        end = np.maximum(end, g + 1)
        return self.cum[end] - self.cum[g + 1]

    def win_occ(self, g: np.ndarray, W: int) -> np.ndarray:
        if LEVER["presence_cut"]:
            end = np.minimum(g + W, self.seg_end[self.seg_of[g]] - 1)
            return self.ocum[end + 1] - self.ocum[g + 1]
        return self.ocum[g + W + 1] - self.ocum[g + 1]

    def busy_in(self, lo_off: int, hi_off: int) -> np.ndarray:
        """For every minute g: number of busy minutes in [g+lo_off, g+hi_off], clipped to the segment."""
        n = len(self.x)
        g = np.arange(n)
        lo = np.maximum(g + lo_off, self.seg_start[self.seg_of])
        hi = np.minimum(g + hi_off, self.seg_end[self.seg_of] - 1)
        out = np.zeros(n, np.int32)
        m = hi >= lo
        out[m] = self.busy_cum[hi[m] + 1] - self.busy_cum[lo[m]]
        return out


class SoftUnit(Unit):
    """Unit on soft states (round 1b: Jev v3.1 behavior-state probability vectors, 5-min windows).

    P: (n, q) per-window probabilities (rows sum to 1). Soft transition counts C_ij = p_t(i) p_{t+1}(j) (DQ3: use the
    probability vectors, not the argmax, for Markov statistics). Convention differs from Unit in one place: the
    transition (t-1 -> t) is stored at index t, so with an event placed at the last pre-kick window g the window
    statistics win_counts_trunc(g, W) start with the transition out of the pre-kick window into the kick window.
    Strata (start state, dwell age) use the argmax of window g, which is fully before the kick."""

    def __init__(self, P: np.ndarray, **kw):
        self.P = np.asarray(P, np.float64)
        super().__init__(**kw)

    def __post_init__(self):
        n = len(self.x)
        q = self.q
        self.agent = np.repeat(self.seg_agent, self.seg_end - self.seg_start).astype(np.int32)
        self.day = np.repeat(self.seg_day, self.seg_end - self.seg_start).astype(np.int32)
        self.seg_of = np.repeat(np.arange(len(self.seg_start)), self.seg_end - self.seg_start)
        self.pos = np.arange(n) - self.seg_start[self.seg_of]
        self.left = self.seg_end[self.seg_of] - 1 - np.arange(n)
        if self.busy is None:
            self.busy = np.zeros(n, bool)
        T = np.zeros((n + 1, q * q))
        ok = self.pos >= 1                                   # transition into t from t-1 within the segment
        idx = np.flatnonzero(ok)
        if len(idx):
            T[idx + 1] = (self.P[idx - 1][:, :, None] * self.P[idx][:, None, :]).reshape(len(idx), q * q)
        self.cum = np.cumsum(T, axis=0)
        oc = np.zeros((n + 1, q))
        oc[1:] = self.P
        self.ocum = np.cumsum(oc, axis=0)
        same = np.r_[False, (self.x[1:] == self.x[:-1]) & (self.pos[1:] > 0)]
        brk = ~same
        run_id = np.cumsum(brk) - 1
        run_start = np.flatnonzero(brk)
        self.age = (np.arange(n) - run_start[run_id] + 1).astype(np.int32)
        self.agebin = (np.searchsorted(np.array([1, 2, 3, 6]), self.age, side="right") - 1).astype(np.int8)
        self.busy_cum = np.r_[0, np.cumsum(self.busy.astype(np.int32))]
        if self.swarm is None:
            self.swarm = np.zeros(n, np.int8)
        self.tt = np.full(n, -1, np.int64)


def build_soft_unit(Ps: list[np.ndarray], agents: list[int], days: list[int], thirds: list[np.ndarray], q: int,
                    events: dict | None = None, busy: list[np.ndarray] | None = None,
                    swarm: list[np.ndarray] | None = None) -> SoftUnit:
    """Ps: per agent-day (n_w, q) probability arrays; events: class -> list (per segment) of local window indices
    (already shifted to the last pre-kick window); busy likewise; swarm: per segment int8 bins."""
    lens = np.array([len(p) for p in Ps], np.int64)
    st = np.r_[0, np.cumsum(lens)[:-1]].astype(np.int64)
    en = st + lens
    P = np.concatenate(Ps) if Ps else np.zeros((0, q))
    x = P.argmax(1).astype(np.int8) if len(P) else np.zeros(0, np.int8)
    ev = {}
    for c, per_seg in (events or {}).items():
        gl = [st[k] + np.asarray(a, np.int64)[(np.asarray(a) >= 0) & (np.asarray(a) < lens[k])] for k, a in enumerate(per_seg)]
        ev[c] = np.sort(np.concatenate(gl)) if gl else np.zeros(0, np.int64)
    b = np.concatenate(busy).astype(bool) if busy is not None else None
    sw = np.concatenate(swarm).astype(np.int8) if swarm is not None else None
    return SoftUnit(P, q=q, x=x, seg_start=st, seg_end=en, seg_agent=np.asarray(agents, np.int32),
                    seg_day=np.asarray(days, np.int32), third=np.concatenate(thirds).astype(np.int8), events=ev, busy=b,
                    swarm=sw)


def swarm_bins(seqs, days, offsets, active_states) -> list[np.ndarray]:
    """Fraction of the OTHER present agents of the same day in an active state at each minute, binned
    (<1/3, 1/3-2/3, >2/3). Agents count as present only inside their own (trimmed) segment."""
    days = np.asarray(days)
    out = [None] * len(seqs)
    for d in np.unique(days):
        ks = np.flatnonzero(days == d)
        hi = max(offsets[k] + len(seqs[k]) for k in ks)
        act = np.zeros(hi + 1)
        pres = np.zeros(hi + 1)
        for k in ks:
            a = np.isin(seqs[k], active_states).astype(float)
            act[offsets[k]:offsets[k] + len(seqs[k])] += a
            pres[offsets[k]:offsets[k] + len(seqs[k])] += 1
        for k in ks:
            sl = slice(offsets[k], offsets[k] + len(seqs[k]))
            a = np.isin(seqs[k], active_states).astype(float)
            oth = pres[sl] - 1
            f = np.where(oth > 0, (act[sl] - a) / np.maximum(oth, 1), 0.0)
            out[k] = np.digitize(f, [1 / 3, 2 / 3]).astype(np.int8)
    return out


def build_unit(seqs: list[np.ndarray], agents: list[int], days: list[int], thirds: list[np.ndarray] | None, q: int,
               events: dict | None = None, busy: list[np.ndarray] | None = None, offsets: list[int] | None = None,
               active_states: tuple | None = None) -> Unit:
    """seqs: per agent-day state arrays; events: class -> list (per segment) of local minute arrays.
    With active_states, each minute also gets the swarm-activity bin of the other agents (matching stratum)."""
    lens = np.array([len(s) for s in seqs], np.int64)
    st = np.r_[0, np.cumsum(lens)[:-1]].astype(np.int64)
    en = st + lens
    x = np.concatenate(seqs).astype(np.int8) if seqs else np.zeros(0, np.int8)
    if thirds is None:
        th = np.concatenate([(np.arange(L) * 3 // max(L, 1)).astype(np.int8) for L in lens]) if seqs else np.zeros(0, np.int8)
    else:
        th = np.concatenate(thirds).astype(np.int8)
    ev = {}
    for c, per_seg in (events or {}).items():
        gl = [st[k] + np.asarray(a, np.int64)[(np.asarray(a) >= 0) & (np.asarray(a) < lens[k])] for k, a in enumerate(per_seg)]
        ev[c] = np.sort(np.concatenate(gl)) if gl else np.zeros(0, np.int64)
    b = np.concatenate(busy).astype(bool) if busy is not None else None
    sw = None
    if active_states is not None and seqs:
        offs = list(offsets) if offsets is not None else [0] * len(seqs)
        sw = np.concatenate(swarm_bins(seqs, days, offs, active_states))
    return Unit(q=q, x=x, seg_start=st, seg_end=en, seg_agent=np.asarray(agents, np.int32),
                seg_day=np.asarray(days, np.int32), third=th, events=ev, busy=b, swarm=sw)


# =============================================================================== matrix statistics

def row_norm(C: np.ndarray) -> np.ndarray:
    s = C.sum(axis=-1, keepdims=True)
    return np.where(s > 0, C / np.where(s > 0, s, 1), 1.0 / C.shape[-1])


def stationary(T: np.ndarray) -> np.ndarray:
    """Stationary distribution of a row-stochastic matrix (batched over leading dims)."""
    T = np.asarray(T, float)
    q = T.shape[-1]
    A = np.swapaxes(T, -1, -2) - np.eye(q)
    A = A.copy()
    A[..., -1, :] = 1.0
    b = np.zeros(T.shape[:-1])
    b[..., -1] = 1.0
    try:
        p = np.linalg.solve(A, b[..., None])[..., 0]
    except np.linalg.LinAlgError:
        p = np.full(T.shape[:-1], 1.0 / q)
    p = np.clip(p, 1e-12, None)
    return p / p.sum(axis=-1, keepdims=True)


def shrink(C: np.ndarray, Tpool: np.ndarray, lam: float = LAMBDA) -> np.ndarray:
    return C + lam * Tpool


def effect_stats(CK: np.ndarray, CC: np.ndarray, Tpool: np.ndarray, lam: float = LAMBDA) -> dict:
    """CK, CC: (..., q, q) counts. Returns arrays with the leading batch shape."""
    q = Tpool.shape[-1]
    TK = row_norm(shrink(CK, Tpool, lam))
    TC = row_norm(shrink(CC, Tpool, lam))
    pK, pC = stationary(TK), stationary(TC)
    dpi = pK - pC
    DF = 0.5 * np.abs(dpi).sum(-1)
    dl = np.log(pK) - np.log(pC)
    mdl = (pC * dl).sum(-1, keepdims=True)
    phi = np.sqrt((pC * (dl - mdl) ** 2).sum(-1))
    eK = 1.0 - np.diagonal(TK, axis1=-2, axis2=-1)
    eC = 1.0 - np.diagonal(TC, axis1=-2, axis2=-1)
    eK = np.clip(eK, 1e-9, None)
    eC = np.clip(eC, 1e-9, None)
    K = np.log((pC * eK).sum(-1)) - np.log((pC * eC).sum(-1))
    esc = np.log(eK) - np.log(eC)
    # symmetric part of the log-rate change on each edge, weighted by control traffic
    LK, LC = np.log(np.clip(TK, 1e-12, None)), np.log(np.clip(TC, 1e-12, None))
    d = LK - LC
    s = 0.5 * (d + np.swapaxes(d, -1, -2))
    a = 0.5 * (d - np.swapaxes(d, -1, -2))
    flow = pC[..., :, None] * TC
    w = flow + np.swapaxes(flow, -1, -2)
    off = ~np.eye(q, dtype=bool)
    wsum = (w * off).sum((-1, -2))
    ksym = (w * s * off).sum((-1, -2)) / np.where(wsum > 0, wsum, 1)
    ktilt = (w * np.abs(a) * off).sum((-1, -2)) / np.where(wsum > 0, wsum, 1)
    return dict(piK=pK, piC=pC, dpi=dpi, DF=DF, phi=phi, K=K, esc=esc, ksym=ksym, ktilt=ktilt)


# =============================================================================== point-lever episodes

def strata_keys(U: Unit, g: np.ndarray, s0: np.ndarray | None = None, age: np.ndarray | None = None):
    s0 = U.x[g] if s0 is None else s0
    ab = U.agebin[g] if age is None else age
    sw = U.swarm[g].astype(np.int64)
    k2 = ((U.agent[g].astype(np.int64) * 16 + s0) * 4 + ab) * 3 + sw
    k1 = k2 * 3 + U.third[g]
    k3 = (s0.astype(np.int64) * 4 + ab) * 3 + sw
    return k1, k2, k3


def control_pool(U: Unit, W: int, quiet: int = QUIET):
    """Boolean mask of control-eligible minutes: window inside the segment, valid state, no busy minute in
    [g-quiet, g] (past only: requiring a kick-free *future* would select agents that escaped on their own,
    because the nudger targets agents that stay idle; found in the synthetic null, 2026-10-04)."""
    need = 1 if LEVER["presence_cut"] else W + 1
    ok = (U.left >= need) & (U.x >= 0)
    ok &= U.busy_in(-quiet, 0) == 0
    return ok


def make_index(keys: np.ndarray, members: np.ndarray):
    """Map key -> array of member indices (members are global minute indices)."""
    o = np.argsort(keys, kind="stable")
    ks, ms = keys[o], members[o]
    u, st = np.unique(ks, return_index=True)
    en = np.r_[st[1:], len(ks)]
    return {int(k): ms[a:b] for k, a, b in zip(u, st, en)}


class Matcher:
    """Stratified control sampler with fallbacks k1 -> k2 -> k3."""

    def __init__(self, U: Unit, pool_mask: np.ndarray, s0_override: np.ndarray | None = None):
        idx = np.flatnonzero(pool_mask)
        k1, k2, k3 = strata_keys(U, idx)
        self.maps = [make_index(k1, idx), make_index(k2, idx), make_index(k3, idx)]

    def pools(self, keys):
        """keys: tuple of three arrays for the episodes; returns the pool (array) per episode and level."""
        out, lev = [], []
        for e in range(len(keys[0])):
            p, L = None, -1
            for lvl in range(3):
                cand = self.maps[lvl].get(int(keys[lvl][e]))
                if cand is not None and len(cand) >= 3:
                    p, L = cand, lvl
                    break
            out.append(p)
            lev.append(L)
        return out, np.array(lev)


def sample_controls(pools, rng, R=R_CTRL, exclude=None):
    """Draw R controls (with replacement) from each episode's pool. Returns (n_ep, R) global indices; -1 if none."""
    n = len(pools)
    out = np.full((n, R), -1, np.int64)
    for e, p in enumerate(pools):
        if p is None or len(p) == 0:
            continue
        out[e] = p[rng.integers(0, len(p), R)]
    return out


@dataclass
class EpisodeSet:
    g: np.ndarray            # episode start minutes (global)
    ctrl: np.ndarray         # (n_ep, R) control minutes, -1 = none
    s0: np.ndarray
    agebin: np.ndarray
    level: np.ndarray        # matching fallback level used


def episodes_for(U: Unit, cls: str, W: int, quiet: int = QUIET, start_override: dict | None = None):
    """Episodes of class `cls`: event minute g with no busy minute in [g-quiet, g-1] (other than g's own),
    window inside the segment, no other class event in the same minute. Returns sorted g."""
    g = np.unique(U.events.get(cls, np.zeros(0, np.int64)))
    if len(g) == 0:
        return g
    need = 1 if LEVER["presence_cut"] else W + 1
    ok = (U.left[g] >= need) & (U.x[g] >= 0)
    ok &= U.busy_in(-quiet, -1)[g] == 0
    # same-minute events of other classes
    others = [np.unique(v) for c, v in U.events.items()
              if c != cls and c in KICK_CLASSES and c not in COMPONENTS.get(cls, ())]
    if others:
        oth = np.unique(np.concatenate(others))
        ok &= ~np.isin(g, oth)
    return g[ok]


KICK_CLASSES = ("N_tgt", "H_men", "H_und", "A_men", "N_oth")   # N_oth (round 1b): named in a nudge, not its leading @
COMPONENTS = {"H_any": ("H_men", "H_und")}


def run_point(U: Unit, cls: str, W: int = W_DEFAULT, B: int = 300, P: int = 200, seed: int = SEED,
              Tpool: np.ndarray | None = None, g_override: np.ndarray | None = None,
              s0_override: np.ndarray | None = None, age_override: np.ndarray | None = None,
              pool_mask: np.ndarray | None = None, quiet: int = QUIET, keep_draws: bool = False,
              keep_states: list | None = None) -> dict:
    """Full point-lever analysis for one unit and class: estimate, day bootstrap, placebo null.

    Transition statistics (pi, phi, K) use windows truncated at the next busy minute in BOTH arms (the hazard
    of an agent that has had exactly one kick vs none; unbiased when kicks depend only on the past). The
    transient occupancy (docc) uses untruncated windows in both arms (intention to treat: kick now vs not now)."""
    rng = np.random.default_rng(seed)
    q = U.q
    if Tpool is None:
        Cp = U.cum[-1].reshape(q, q).astype(float)
        Tpool = row_norm(Cp + 1e-3)
    g = episodes_for(U, cls, W, quiet) if g_override is None else np.asarray(g_override, np.int64)
    res = dict(cls=cls, W=W, n_ep=int(len(g)), q=q)
    if len(g) < 3:
        res["status"] = "too few episodes"
        return res
    if pool_mask is None:
        pool_mask = control_pool(U, W, quiet)
    M = Matcher(U, pool_mask)
    s0 = U.x[g] if s0_override is None else np.asarray(s0_override)
    ab = U.agebin[g] if age_override is None else np.asarray(age_override)
    keys = strata_keys(U, g, s0, ab)
    pools, lev = M.pools(keys)
    keep = np.array([p is not None for p in pools])
    g, s0, ab, lev = g[keep], s0[keep], ab[keep], lev[keep]
    pools = [p for p in pools if p is not None]
    res["n_ep"] = int(len(g))
    res["match_levels"] = np.bincount(lev, minlength=3).tolist()
    if len(g) < 3:
        res["status"] = "too few matched episodes"
        return res
    ctrl = sample_controls(pools, rng)
    q0 = q
    ks = np.arange(q0) if keep_states is None else np.asarray(keep_states)

    def sub(C):   # restrict (n, q0*q0) counts to the kept states (the chain conditional on staying among them)
        if keep_states is None:
            return C
        return C.reshape(len(C), q0, q0)[:, ks][:, :, ks].reshape(len(C), -1)

    def subo(O):
        return O if keep_states is None else O[:, ks]
    if keep_states is not None:
        q = len(ks)
        Tpool = row_norm(Tpool[np.ix_(ks, ks)])
        res["keep_states"] = [int(k) for k in ks]
    CKe = sub(U.win_counts_trunc(g, W).astype(float))                        # (n_ep, q*q)
    CCe = sub(U.win_counts_trunc(ctrl.ravel(), W).astype(float)).reshape(len(g), -1, q * q).mean(1)
    OKe = subo(U.win_occ(g, W).astype(float))
    OCe = subo(U.win_occ(ctrl.ravel(), W).astype(float)).reshape(len(g), -1, q).mean(1)
    est = effect_stats(CKe.sum(0).reshape(q, q), CCe.sum(0).reshape(q, q), Tpool)
    occK, occC = OKe.sum(0) / OKe.sum(), OCe.sum(0) / OCe.sum()
    res.update({k: (v.tolist() if isinstance(v, np.ndarray) else float(v)) for k, v in est.items()})
    res["docc"] = (occK - occC).tolist()
    res["n_trans_kick"] = float(CKe.sum())
    res["n_trans_ctrl"] = float(CCe.sum())
    res["win_len_kick"] = float(np.mean(np.minimum(g + W, U.next_busy(g)) - g))
    res["s0_mix"] = np.bincount(s0, minlength=q0).tolist()
    res["n_days"] = int(len(np.unique(U.day[g])))
    res["n_agents"] = int(len(np.unique(U.agent[g])))
    res["busy_in_window_mean"] = float(np.mean(U.busy_in(1, W)[g]))
    # ---------------- day-block bootstrap
    days = U.day[g]
    ud, dinv = np.unique(days, return_inverse=True)
    Mb = np.zeros((B, len(g)))
    for b in range(B):
        cnt = np.bincount(rng.integers(0, len(ud), len(ud)), minlength=len(ud))
        Mb[b] = cnt[dinv]
    bs = effect_stats((Mb @ CKe).reshape(B, q, q), (Mb @ CCe).reshape(B, q, q), Tpool)
    for k in ("K", "phi", "DF", "ksym"):
        res[f"{k}_boot_se"] = float(np.std(bs[k]))
        res[f"{k}_ci"] = np.percentile(bs[k], [2.5, 97.5]).tolist()
    for k in ("dpi", "esc"):
        res[f"{k}_boot_se"] = np.std(bs[k], axis=0).tolist()
        res[f"{k}_ci"] = np.percentile(bs[k], [2.5, 97.5], axis=0).tolist()
    bo = (Mb @ OKe) / (Mb @ OKe).sum(1, keepdims=True) - (Mb @ OCe) / (Mb @ OCe).sum(1, keepdims=True)
    res["docc_ci"] = np.percentile(bo, [2.5, 97.5], axis=0).tolist()
    if keep_draws:
        res["_boot"] = {k: bs[k] for k in ("K", "phi", "dpi", "esc")}
    # ---------------- placebo episodes: pseudo-episodes from each real episode's own pool
    pl_phi, pl_K, pl_DF, pl_dpi, pl_esc, pl_docc = [], [], [], [], [], []
    for p in range(P):
        pe = np.array([pp[rng.integers(0, len(pp))] for pp in pools])
        pc = sample_controls(pools, rng)
        A = sub(U.win_counts_trunc(pe, W).astype(float)).sum(0).reshape(q, q)
        Cc = sub(U.win_counts_trunc(pc.ravel(), W).astype(float)).reshape(len(pe), -1, q * q).mean(1).sum(0).reshape(q, q)
        st = effect_stats(A, Cc, Tpool)
        oK = subo(U.win_occ(pe, W).astype(float)).sum(0)
        oC = subo(U.win_occ(pc.ravel(), W).astype(float)).reshape(len(pe), -1, q).mean(1).sum(0)
        pl_docc.append(oK / oK.sum() - oC / oC.sum())
        pl_phi.append(float(st["phi"]))
        pl_K.append(float(st["K"]))
        pl_DF.append(float(st["DF"]))
        pl_dpi.append(st["dpi"])
        pl_esc.append(st["esc"])
    pl_phi, pl_K, pl_DF = np.array(pl_phi), np.array(pl_K), np.array(pl_DF)
    pl_dpi, pl_esc, pl_docc = np.array(pl_dpi), np.array(pl_esc), np.array(pl_docc)
    res["placebo"] = dict(phi_med=float(np.median(pl_phi)), phi_p95=float(np.percentile(pl_phi, 95)),
                          K_med=float(np.median(pl_K)), K_p025=float(np.percentile(pl_K, 2.5)),
                          K_p975=float(np.percentile(pl_K, 97.5)), K_sd=float(np.std(pl_K)),
                          DF_med=float(np.median(pl_DF)), dpi_sd=np.std(pl_dpi, 0).tolist(),
                          esc_sd=np.std(pl_esc, 0).tolist(), docc_sd=np.std(pl_docc, 0).tolist())
    phi = res["phi"]
    res["p_F"] = float((1 + np.sum(pl_phi >= phi)) / (P + 1))
    res["p_DF"] = float((1 + np.sum(pl_DF >= res["DF"])) / (P + 1))
    dev = np.abs(pl_K - np.median(pl_K))
    res["p_K"] = float((1 + np.sum(dev >= abs(res["K"] - np.median(pl_K)))) / (P + 1))
    res["p_docc"] = [float((1 + np.sum(np.abs(pl_docc[:, s]) >= abs(res["docc"][s]))) / (P + 1)) for s in range(q)]
    res["p_dpi"] = [float((1 + np.sum(np.abs(pl_dpi[:, s] - np.median(pl_dpi[:, s]))
                                      >= abs(res["dpi"][s] - np.median(pl_dpi[:, s])))) / (P + 1)) for s in range(q)]
    res["phi_exc"] = float(math.sqrt(max(phi ** 2 - np.median(pl_phi ** 2), 0.0)))
    if keep_draws:
        res["_boot"]["phi_exc"] = np.sqrt(np.clip(bs["phi"] ** 2 - np.median(pl_phi ** 2), 0, None))
    res["rho"] = float(abs(res["K"]) / (abs(res["K"]) + res["phi_exc"] + 1e-12))
    res["status"] = "ok" if len(g) >= MIN_EP else "underpowered"
    return res


# =============================================================================== step levers

def seg_counts(U: Unit) -> np.ndarray:
    """Per-segment transition counts (n_seg, q*q)."""
    c = U.cum[U.seg_end] - U.cum[U.seg_start]
    return c.astype(float)


def run_step(Upre: Unit, Upost: Unit, B: int = 300, seed: int = SEED, Tpool: np.ndarray | None = None,
             keep_draws: bool = False) -> dict:
    """Step lever: pre (control) vs post (kicked); agent-block bootstrap over the balanced panel."""
    rng = np.random.default_rng(seed)
    q = Upre.q
    cpre, cpost = seg_counts(Upre), seg_counts(Upost)
    agents = np.union1d(Upre.seg_agent, Upost.seg_agent)
    A = len(agents)
    ai_pre = np.searchsorted(agents, Upre.seg_agent)
    ai_post = np.searchsorted(agents, Upost.seg_agent)
    Apre = np.zeros((A, q * q))
    Apost = np.zeros((A, q * q))
    np.add.at(Apre, ai_pre, cpre)
    np.add.at(Apost, ai_post, cpost)
    if Tpool is None:
        Tpool = row_norm((Apre.sum(0) + Apost.sum(0)).reshape(q, q) + 1e-3)
    est = effect_stats(Apost.sum(0).reshape(q, q), Apre.sum(0).reshape(q, q), Tpool)
    res = {k: (v.tolist() if isinstance(v, np.ndarray) else float(v)) for k, v in est.items()}
    res["n_agents"] = int(A)
    res["n_trans_pre"] = float(Apre.sum())
    res["n_trans_post"] = float(Apost.sum())
    Mb = np.zeros((B, A))
    for b in range(B):
        Mb[b] = np.bincount(rng.integers(0, A, A), minlength=A)
    bs = effect_stats((Mb @ Apost).reshape(B, q, q), (Mb @ Apre).reshape(B, q, q), Tpool)
    for k in ("K", "phi", "DF", "ksym"):
        res[f"{k}_boot_se"] = float(np.std(bs[k]))
        res[f"{k}_ci"] = np.percentile(bs[k], [2.5, 97.5]).tolist()
    for k in ("dpi", "esc"):
        res[f"{k}_ci"] = np.percentile(bs[k], [2.5, 97.5], axis=0).tolist()
    if keep_draws:
        res["_boot"] = {k: bs[k] for k in ("K", "phi", "dpi")}
    return res


def judge_step(res: dict, placebo: list[dict]) -> dict:
    """Percentiles of a step's phi and K in a placebo list; field/catalyst flags."""
    ph = np.array([p["phi"] for p in placebo])
    Ks = np.array([p["K"] for p in placebo])
    out = dict(n_placebo=int(len(ph)))
    if len(ph) < 5:
        out["status"] = "too few placebos"
        return out
    out["phi_pct"] = float(np.mean(ph < res["phi"]) * 100)
    out["K_pct"] = float(np.mean(Ks < res["K"]) * 100)
    out["phi_p95"] = float(np.percentile(ph, 95))
    out["K_p025"], out["K_p975"] = (float(np.percentile(Ks, 2.5)), float(np.percentile(Ks, 97.5)))
    out["phi_exc"] = float(math.sqrt(max(res["phi"] ** 2 - np.median(ph ** 2), 0)))
    out["field"] = bool(res["phi"] > out["phi_p95"] and out["phi_exc"] >= THR)
    out["catalyst"] = bool((res["K"] > out["K_p975"] or res["K"] < out["K_p025"]) and abs(res["K"]) >= THR)
    out["cls"] = classify(out["field"], out["catalyst"])
    # one-sided empirical p for phi, two-sided for K
    out["p_F"] = float((1 + np.sum(ph >= res["phi"])) / (len(ph) + 1))
    med = np.median(Ks)
    out["p_K"] = float((1 + np.sum(np.abs(Ks - med) >= abs(res["K"] - med))) / (len(Ks) + 1))
    return out


def unit_class(r: dict) -> str:
    """Single-unit rule (Amendment A1): field = placebo p_F < 0.05 and phi_exc >= THR;
    catalyst = K bootstrap CI excluding 0 and |K| >= THR."""
    if r.get("status") not in ("ok", "underpowered") or "p_F" not in r:
        return "n/a"
    f = r["p_F"] < 0.05 and r["phi_exc"] >= THR
    c = (r["K_ci"][0] > 0 or r["K_ci"][1] < 0) and abs(r["K"]) >= THR
    return classify(f, c)


def classify(field_: bool, cat: bool) -> str:
    return {(True, True): "both", (True, False): "field", (False, True): "catalyst", (False, False): "neither"}[(bool(field_), bool(cat))]


# =============================================================================== pooling across units

def dl_meta(est: np.ndarray, se: np.ndarray) -> dict:
    """DerSimonian-Laird random-effects pooling."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    m = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[m], se[m]
    k = len(est)
    if k == 0:
        return dict(k=0)
    w = 1 / se ** 2
    fe = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - fe) ** 2)
    tau2 = max(0.0, (Q - (k - 1)) / (np.sum(w) - np.sum(w ** 2) / np.sum(w))) if k > 1 else 0.0
    wr = 1 / (se ** 2 + tau2)
    re = np.sum(wr * est) / np.sum(wr)
    sre = math.sqrt(1 / np.sum(wr))
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
    return dict(k=int(k), est=float(re), se=float(sre), ci=[float(re - 1.96 * sre), float(re + 1.96 * sre)],
                tau2=float(tau2), I2=float(I2), z=float(re / sre), p=float(2 * (1 - _ncdf(abs(re / sre)))))


def _ncdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _nppf(p):
    # Acklam-free: use bisection on erf (adequate for p in (1e-6, 1-1e-6))
    lo, hi = -10.0, 10.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _ncdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def stouffer(pvals) -> float:
    p = np.clip(np.asarray(pvals, float), 1e-6, 1 - 1e-6)
    if len(p) == 0:
        return float("nan")
    z = np.array([_nppf(1 - x) for x in p])
    Z = z.sum() / math.sqrt(len(z))
    return float(1 - _ncdf(Z))


def class_verdict(units: list[dict]) -> dict:
    """Pre-registered class rule over powered point-lever units."""
    pw = [u for u in units if u.get("status") == "ok"]
    out = dict(n_units=len(units), n_powered=len(pw))
    if not pw:
        out["cls"] = "n/a (no powered unit)"
        return out
    pF = [u["p_F"] for u in pw]
    out["stouffer_pF"] = stouffer(pF)
    out["share_pF05"] = float(np.mean(np.array(pF) < 0.05))
    out["phi_exc_mean"] = float(np.mean([u["phi_exc"] for u in pw]))
    # Amendment A1 (2026-10-04, after the synthetic validation, before any real data): effect-size floor
    field_ = (out["stouffer_pF"] < 0.01) and (out["share_pF05"] >= 1 / 3) and (out["phi_exc_mean"] >= THR)
    mk = dl_meta([u["K"] for u in pw], [u["K_boot_se"] for u in pw])
    out["K_meta"] = mk
    signs = np.sign([u["K"] for u in pw])
    same = float(np.mean(signs == np.sign(mk.get("est", 0)))) if mk.get("k") else 0.0
    out["K_same_sign_share"] = same
    cat = bool(mk.get("k") and (mk["ci"][0] > 0 or mk["ci"][1] < 0) and abs(mk["est"]) >= THR and same >= 2 / 3)
    out["field"], out["catalyst"] = bool(field_), cat
    out["cls"] = classify(field_, cat)
    out["bonferroni_field"] = bool(out["stouffer_pF"] < 0.05 / 28)
    out["bonferroni_cat"] = bool(mk.get("k") and mk["p"] < 0.05 / 28)
    q = len(pw[0]["dpi"])
    out["dpi_meta"] = [dl_meta([u["dpi"][s] for u in pw], [u["dpi_boot_se"][s] for u in pw]) for s in range(q)]
    out["esc_meta"] = [dl_meta([u["esc"][s] for u in pw], [u["esc_boot_se"][s] for u in pw]) for s in range(q)]
    out["phi_exc_median"] = float(np.median([u["phi_exc"] for u in pw]))
    out["phi_exc_mean"] = float(np.mean([u["phi_exc"] for u in pw]))
    ke = abs(mk.get("est", 0.0))
    out["rho"] = float(ke / (ke + out["phi_exc_mean"] + 1e-12))
    return out


def class_probabilities(units: list[dict], rng, R: int = 2000) -> dict:
    """Bootstrap over powered units (each unit draws one of its own bootstrap replicates if kept, else a
    normal draw from its SE). Classify each replicate with the effect-size thresholds."""
    pw = [u for u in units if u.get("status") == "ok"]
    if not pw:
        return {}
    cnt = {"field": 0, "catalyst": 0, "both": 0, "neither": 0}
    for _ in range(R):
        pick = rng.integers(0, len(pw), len(pw))
        Ks, ph, ws = [], [], []
        for i in pick:
            u = pw[i]
            if "_boot" in u:
                j = rng.integers(0, len(u["_boot"]["K"]))
                Ks.append(float(u["_boot"]["K"][j]))
                ph.append(float(u["_boot"]["phi_exc"][j]))
            else:
                Ks.append(rng.normal(u["K"], u["K_boot_se"]))
                ph.append(max(0.0, rng.normal(u["phi_exc"], u["phi_boot_se"])))
            ws.append(1 / max(u["K_boot_se"], 1e-3) ** 2)
        ws = np.array(ws)
        Kp = float(np.sum(ws * np.array(Ks)) / ws.sum())
        php = float(np.sum(ws * np.array(ph)) / ws.sum())
        cnt[classify(php >= THR, abs(Kp) >= THR)] += 1
    return {k: v / R for k, v in cnt.items()}


# =============================================================================== io helpers

def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        raise TypeError(type(o))

    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if not str(k).startswith("_")}
        if isinstance(o, list):
            return [strip(v) for v in o]
        return o
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(strip(obj), indent=1, default=conv))
