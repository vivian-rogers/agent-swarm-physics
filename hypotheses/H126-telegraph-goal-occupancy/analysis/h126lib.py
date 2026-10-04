"""H126 library: two-state telegraph (and 4-state hyperexponential) hidden Markov models on an irregular call clock.

Data layout for one fit ("Seq"): statements concatenated over sequences (one sequence = one agent x design x segment
run, time-ordered); obs[k] in {0,1} = on-goal label; step[k] = gap to the previous statement of the same sequence
(calls, or minutes for the wall clock; ignored at a sequence start); rg[k] = rate group of the transition INTO
statement k (agent, or segment, or agent x segment); ptr = sequence start offsets (len nseq + 1).

Models
  M2  : per rate group (a, b) = P(off->on), P(on->off) per call; emissions q0 = P(b=1|off), q1 = P(b=1|on).
        P^D = Pi + lam^D (I - Pi), lam = 1 - a - b.   Wall clock: lam = exp(-(a + b) * dt) with rates per minute.
  M4  : off = {off-fast, off-slow}, on = {on-fast, on-slow}. Per rate group base rates (a, b) for the fast sub-states;
        shared ratios ra = a_slow/a_fast, rb = b_slow/b_fast in (0, 1] and entry weights w_off, w_on (probability that
        an entry lands in the fast sub-state). Nests M2 at ra = rb = 1. Dwells are mixtures of two geometrics.
Fits are maximum likelihood (L-BFGS-B on logit / log parameters, numerical gradients). numba is used when available
(`uv run --with numba ...`); the pure-Python fallback gives identical numbers, only slower.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

try:
    from numba import njit
except ImportError:  # pragma: no cover
    def njit(*a, **k):
        if a and callable(a[0]):
            return a[0]
        return lambda f: f


# ============================================================================================ data
@dataclass
class Seq:
    obs: np.ndarray      # int8
    step: np.ndarray     # float64 (calls or minutes)
    rg: np.ndarray       # int64 rate group per statement
    ptr: np.ndarray      # int64 sequence starts
    n_rg: int
    agent: np.ndarray | None = None   # agent id per statement (bookkeeping)
    win: np.ndarray | None = None     # 30-min window id per statement
    c: np.ndarray | None = None       # absolute call index per statement

    @property
    def n(self):
        return len(self.obs)


def make_seq(obs, step, rg, seq_id, n_rg=None, agent=None, win=None, c=None) -> Seq:
    """seq_id: per-statement sequence key (already sorted so that each sequence is contiguous)."""
    seq_id = np.asarray(seq_id)
    brk = np.flatnonzero(np.r_[True, seq_id[1:] != seq_id[:-1]])
    ptr = np.r_[brk, len(seq_id)].astype(np.int64)
    rg = np.asarray(rg, np.int64)
    return Seq(np.asarray(obs, np.int8), np.asarray(step, np.float64), rg, ptr,
               int(n_rg if n_rg is not None else rg.max() + 1), agent, win, c)


def subset(S: Seq, mask: np.ndarray, step_new=None) -> Seq:
    """Keep statements in mask; sequences re-split where kept statements are not contiguous is NOT done: the gap of the
    first kept statement after a dropped block becomes the summed gap only if step_new is given (pass recomputed steps)."""
    idx = np.flatnonzero(mask)
    sid = np.repeat(np.arange(len(S.ptr) - 1), np.diff(S.ptr))[idx]
    st = S.step[idx] if step_new is None else step_new[idx]
    return make_seq(S.obs[idx], st, S.rg[idx], sid, S.n_rg, None if S.agent is None else S.agent[idx],
                    None if S.win is None else S.win[idx], None if S.c is None else S.c[idx])


# ============================================================================================ 2-state likelihood
@njit(cache=True)
def _ll2(obs, step, rg, ptr, a, b, q0, q1, wall):
    tot = 0.0
    for s in range(len(ptr) - 1):
        i0 = ptr[s]
        g = rg[i0]
        p = a[g] / (a[g] + b[g])
        e1 = q1 if obs[i0] == 1 else 1.0 - q1
        e0 = q0 if obs[i0] == 1 else 1.0 - q0
        f1 = p * e1
        f0 = (1.0 - p) * e0
        c = f0 + f1
        if not c > 0.0:
            return -1e300
        tot += math.log(c)
        f0 /= c
        f1 /= c
        for k in range(i0 + 1, ptr[s + 1]):
            g = rg[k]
            p = a[g] / (a[g] + b[g])
            if wall:
                lam = math.exp(-(a[g] + b[g]) * step[k])
            else:
                lam = (1.0 - a[g] - b[g]) ** step[k]
            # P^D rows: from off: [1-p - lam*(-p)... ] -> P(off->on) = p(1-lam); P(on->on) = p + lam(1-p)
            n1 = f0 * p * (1.0 - lam) + f1 * (p + lam * (1.0 - p))
            n0 = f0 + f1 - n1
            e1 = q1 if obs[k] == 1 else 1.0 - q1
            e0 = q0 if obs[k] == 1 else 1.0 - q0
            f1 = n1 * e1
            f0 = n0 * e0
            c = f0 + f1
            if not c > 0.0:
                return -1e300
            tot += math.log(c)
            f0 /= c
            f1 /= c
    return tot


@njit(cache=True)
def _ll2_per_seq(obs, step, rg, ptr, a, b, q0, q1, wall, out):
    for s in range(len(ptr) - 1):
        out[s] = _ll2(obs, step, rg, ptr[s:s + 2], a, b, q0, q1, wall)


def ll2(S: Seq, a, b, q0, q1, wall=False) -> float:
    return float(_ll2(S.obs, S.step, S.rg, S.ptr, np.asarray(a, float), np.asarray(b, float), q0, q1, wall))


def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


def _logit(p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return np.log(p / (1 - p))


def fit2(S: Seq, wall=False, init=None, q_fixed=None, maxiter=400):
    """M2 MLE. Returns dict(a, b, q0, q1, ll, k). Call clock: a, b in (0, 1) with a + b < 1 enforced softly.
    Wall clock: a, b > 0 per minute. q1 > q0 enforced by q1 = q0 + (1 - q0) * sigmoid(.)."""
    G = S.n_rg
    if init is None:
        f = max(min(S.obs.mean(), 0.9), 0.02)
        a0 = np.full(G, 0.05 * f / 0.5)
        b0 = np.full(G, 0.08)
        if wall:
            a0, b0 = a0 / 5.0, b0 / 5.0
        q00, q10 = 0.05, 0.6
    else:
        a0, b0, q00, q10 = (np.asarray(init["a"], float), np.asarray(init["b"], float), init["q0"], init["q1"])

    def unpack(x):
        if wall:
            a, b = np.clip(np.exp(x[:G]), 1e-9, 1e3), np.clip(np.exp(x[G:2 * G]), 1e-9, 1e3)
        else:
            a, b = _sig(x[:G]), _sig(x[G:2 * G])
        if q_fixed is not None:
            q0, q1 = q_fixed
        else:
            q0 = _sig(x[2 * G])
            q1 = q0 + (1 - q0) * _sig(x[2 * G + 1])
        return a, b, q0, q1

    def nll(x):
        a, b, q0, q1 = unpack(x)
        if not wall and np.any(a + b >= 0.999):
            return 1e12
        v = _ll2(S.obs, S.step, S.rg, S.ptr, a, b, q0, q1, wall)
        return -v if (np.isfinite(v) and v > -1e299) else 1e12

    if wall:
        x0 = np.r_[np.log(a0), np.log(b0)]
    else:
        x0 = np.r_[_logit(a0), _logit(b0)]
    if q_fixed is None:
        x0 = np.r_[x0, _logit(q00), _logit((q10 - q00) / (1 - q00))]
    best = None
    starts = [x0]
    if init is None:  # a second start with slow dynamics
        xs = x0.copy()
        if wall:
            xs[:2 * G] = xs[:2 * G] - 1.5
        else:
            xs[:2 * G] = _logit(_sig(xs[:2 * G]) / 4)
        starts.append(xs)
    for xs in starts:
        r = minimize(nll, xs, method="L-BFGS-B", options=dict(maxiter=maxiter))
        if best is None or r.fun < best.fun:
            best = r
    a, b, q0, q1 = unpack(best.x)
    k = 2 * G + (0 if q_fixed is not None else 2)
    return dict(a=a, b=b, q0=float(q0), q1=float(q1), ll=float(-best.fun), k=k, ok=bool(best.success))


# ============================================================================================ 4-state likelihood
@njit(cache=True)
def _mat4(a, b, ra, rb, woff, won):
    # states: 0 off-fast, 1 off-slow, 2 on-fast, 3 on-slow
    P = np.zeros((4, 4))
    ex = np.array([a, a * ra, b, b * rb])
    for s in range(4):
        P[s, s] = 1.0 - ex[s]
        if s < 2:
            P[s, 2] += ex[s] * won
            P[s, 3] += ex[s] * (1.0 - won)
        else:
            P[s, 0] += ex[s] * woff
            P[s, 1] += ex[s] * (1.0 - woff)
    return P


@njit(cache=True)
def _matpow(P, d):
    R = np.eye(4)
    B = P.copy()
    while d > 0:
        if d & 1:
            R = R @ B
        B = B @ B
        d >>= 1
    return R


@njit(cache=True)
def _stat4c(a, b, ra, rb, woff, won):
    # closed form by flux balance: equal flux F into and out of each macro-state
    v = np.array([woff / a, (1.0 - woff) / (a * ra), won / b, (1.0 - won) / (b * rb)])
    return v / v.sum()


@njit(cache=True)
def _ll4(obs, rg, ptr, uid, ug, ud, a, b, ra, rb, woff, won, q0, q1):
    G = len(a)
    tot = 0.0
    Ps = np.zeros((G, 4, 4))
    pis = np.zeros((G, 4))
    for g in range(G):
        Ps[g] = _mat4(a[g], b[g], ra, rb, woff, won)
        pis[g] = _stat4c(a[g], b[g], ra, rb, woff, won)
    U = len(ug)
    Mt = np.zeros((U, 4, 4))
    for u in range(U):
        if u > 0 and ug[u] == ug[u - 1]:
            Mt[u] = Mt[u - 1] @ _matpow(Ps[ug[u]], ud[u] - ud[u - 1])
        else:
            Mt[u] = _matpow(Ps[ug[u]], ud[u])
    em1 = np.array([q0, q0, q1, q1])
    f = np.zeros(4)
    n = np.zeros(4)
    for s in range(len(ptr) - 1):
        i0 = ptr[s]
        g = rg[i0]
        for j in range(4):
            e = em1[j] if obs[i0] == 1 else 1.0 - em1[j]
            f[j] = pis[g, j] * e
        c = f.sum()
        if not c > 0.0:
            return -1e300
        tot += math.log(c)
        f /= c
        for k in range(i0 + 1, ptr[s + 1]):
            u = uid[k]
            for j in range(4):
                acc = 0.0
                for i in range(4):
                    acc += f[i] * Mt[u, i, j]
                e = em1[j] if obs[k] == 1 else 1.0 - em1[j]
                n[j] = acc * e
            c = n[0] + n[1] + n[2] + n[3]
            if not c > 0.0:
                return -1e300
            tot += math.log(c)
            for j in range(4):
                f[j] = n[j] / c
    return tot


def _uids(S: Seq):
    key = S.rg.astype(np.int64) * 10_000_000 + S.step.astype(np.int64)
    uk, uid = np.unique(key, return_inverse=True)
    return uid.astype(np.int64), (uk // 10_000_000).astype(np.int64), (uk % 10_000_000).astype(np.int64)


def dwell_cv(rate, r, w):
    """CV of a mixture of two geometric dwells: exit prob `rate` w.p. w, `rate*r` w.p. 1-w (per call)."""
    m = lambda be: 1 / be  # noqa: E731
    s2 = lambda be: (2 - be) / be ** 2  # noqa: E731
    b1, b2 = rate, rate * r
    mu = w * m(b1) + (1 - w) * m(b2)
    ex2 = w * s2(b1) + (1 - w) * s2(b2)
    return math.sqrt(max(ex2 - mu ** 2, 0)) / mu


def fit4(S: Seq, init2=None, maxiter=400):
    """M4 MLE with per-rate-group base rates and shared shape. init2: an M2 fit to start from (fast = slow)."""
    G = S.n_rg
    if init2 is None:
        init2 = fit2(S)
    # start: fast sub-state 3x faster than the M2 rate, slow 3x slower, weights 0.5 -> mean about the M2 mean
    a0 = np.clip(np.asarray(init2["a"]) * 1.8, 1e-4, 0.45)
    b0 = np.clip(np.asarray(init2["b"]) * 1.8, 1e-4, 0.45)

    def unpack(x):
        a, b = _sig(x[:G]), _sig(x[G:2 * G])
        ra, rb, woff, won = np.clip(_sig(x[2 * G:2 * G + 4]), 1e-6, 1 - 1e-6)
        q0 = _sig(x[2 * G + 4])
        q1 = q0 + (1 - q0) * _sig(x[2 * G + 5])
        return a, b, ra, rb, woff, won, q0, q1

    def nll(x):
        a, b, ra, rb, woff, won, q0, q1 = unpack(x)
        if np.any(a * (1 + 0) >= 0.999) or np.any(b >= 0.999):
            return 1e12
        v = _ll4(S.obs, S.rg, S.ptr, uid, ug, ud, a, b, ra, rb, woff, won, q0, q1)
        return -v if (np.isfinite(v) and v > -1e299) else 1e12

    uid, ug, ud = _uids(S)
    q0, q1 = init2["q0"], init2["q1"]
    starts = []
    for r0, w0 in ((0.15, 0.6), (0.6, 0.5)):
        starts.append(np.r_[_logit(a0), _logit(b0), _logit(np.array([r0, r0, w0, w0])), _logit(q0),
                            _logit((q1 - q0) / (1 - q0))])
    # nested start (exactly M2): ra = rb = 1 - eps
    starts.append(np.r_[_logit(np.asarray(init2["a"])), _logit(np.asarray(init2["b"])),
                        _logit(np.array([0.999, 0.999, 0.5, 0.5])), _logit(q0), _logit((q1 - q0) / (1 - q0))])
    best = None
    for xs in starts:
        r = minimize(nll, xs, method="L-BFGS-B", options=dict(maxiter=maxiter))
        if best is None or r.fun < best.fun:
            best = r
    a, b, ra, rb, woff, won, q0, q1 = unpack(best.x)
    cv_on = dwell_cv(float(np.median(b)), float(rb), float(won))
    cv_off = dwell_cv(float(np.median(a)), float(ra), float(woff))
    return dict(a=a, b=b, ra=float(ra), rb=float(rb), woff=float(woff), won=float(won), q0=float(q0), q1=float(q1),
                ll=float(-best.fun), k=2 * G + 6, cv_on=cv_on, cv_off=cv_off, ok=bool(best.success))


def fit4p(S: Seq, f2, maxiter=300):
    """Profile M4 (used for the shape test): per-group base rates are the M2 fit's rates times shared scales
    (sa, sb); shared shape (ra, rb, woff, won) and emissions are free. Nests M2 at sa = sb = 1, ra = rb = 1.
    8 free parameters, so it is cheap enough for parametric bootstraps."""
    a2, b2 = np.asarray(f2["a"], float), np.asarray(f2["b"], float)
    uid, ug, ud = _uids(S)

    def unpack(x):
        sa, sb = np.exp(x[0]), np.exp(x[1])
        ra, rb, woff, won = np.clip(_sig(x[2:6]), 1e-6, 1 - 1e-6)
        q0 = _sig(x[6])
        q1 = q0 + (1 - q0) * _sig(x[7])
        return np.clip(a2 * sa, 1e-7, 0.99), np.clip(b2 * sb, 1e-7, 0.99), ra, rb, woff, won, q0, q1

    def nll(x):
        a, b, ra, rb, woff, won, q0, q1 = unpack(x)
        v = _ll4(S.obs, S.rg, S.ptr, uid, ug, ud, a, b, ra, rb, woff, won, q0, q1)
        return -v if (np.isfinite(v) and v > -1e299) else 1e12

    q0, q1 = f2["q0"], f2["q1"]
    qx = [_logit(q0), _logit((q1 - q0) / (1 - q0))]
    starts = [np.r_[0.0, 0.0, _logit(np.array([0.999, 0.999, 0.5, 0.5])), qx],
              np.r_[np.log(1.8), np.log(1.8), _logit(np.array([0.15, 0.15, 0.6, 0.6])), qx]]
    best = None
    for xs in starts:
        r = minimize(nll, xs, method="L-BFGS-B", options=dict(maxiter=maxiter))
        if best is None or r.fun < best.fun:
            best = r
    a, b, ra, rb, woff, won, q0, q1 = unpack(best.x)
    cv_on = dwell_cv(float(np.median(b)), float(rb), float(won))
    cv_off = dwell_cv(float(np.median(a)), float(ra), float(woff))
    return dict(a=a, b=b, ra=float(ra), rb=float(rb), woff=float(woff), won=float(won), q0=float(q0), q1=float(q1),
                ll=float(-best.fun), k=len(a2) * 2 + 6, cv_on=cv_on, cv_off=cv_off, ok=bool(best.success))


def ll4(S: Seq, f) -> float:
    uid, ug, ud = _uids(S)
    return float(_ll4(S.obs, S.rg, S.ptr, uid, ug, ud, np.asarray(f["a"], float), np.asarray(f["b"], float), f["ra"],
                      f["rb"], f["woff"], f["won"], f["q0"], f["q1"]))


# ============================================================================================ simulation
@njit(cache=True)
def _sim2(step, rg, ptr, a, b, q0, q1, u, v, wall, obs, lat):
    for s in range(len(ptr) - 1):
        i0, i1 = ptr[s], ptr[s + 1]
        g = rg[i0]
        p = a[g] / (a[g] + b[g])
        x = 1 if u[i0] < p else 0
        lat[i0] = x
        for k in range(i0 + 1, i1):
            g = rg[k]
            p = a[g] / (a[g] + b[g])
            if wall:
                lam = math.exp(-(a[g] + b[g]) * step[k])
            else:
                lam = (1.0 - a[g] - b[g]) ** step[k]
            p1 = p + lam * (1.0 - p) if x == 1 else p * (1.0 - lam)
            x = 1 if u[k] < p1 else 0
            lat[k] = x
    for k in range(len(obs)):
        if lat[k] == 1:
            obs[k] = 1 if v[k] < q1 else 0
        else:
            obs[k] = 1 if v[k] < q0 else 0


def simulate2(S: Seq, a, b, q0, q1, rng, wall=False):
    """Latent telegraph on S's real observation skeleton -> (obs, latent)."""
    obs = np.empty(S.n, np.int8)
    lat = np.empty(S.n, np.int8)
    _sim2(S.step, S.rg, S.ptr, np.asarray(a, float), np.asarray(b, float), float(q0), float(q1), rng.random(S.n),
          rng.random(S.n), wall, obs, lat)
    return obs, lat


def simulate4(S: Seq, a, b, ra, rb, woff, won, q0, q1, rng):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    obs = np.empty(S.n, np.int8)
    lat = np.empty(S.n, np.int8)
    cache = {}
    for s in range(len(S.ptr) - 1):
        i0, i1 = S.ptr[s], S.ptr[s + 1]
        g = S.rg[i0]
        pi = _stat4c(a[g], b[g], ra, rb, woff, won)
        x = rng.choice(4, p=pi / pi.sum())
        lat[i0] = x
        for k in range(i0 + 1, i1):
            g = S.rg[k]
            d = int(S.step[k])
            key = (g, d)
            if key not in cache:
                cache[key] = _matpow(_mat4(a[g], b[g], ra, rb, woff, won), d)
            row = cache[key][x]
            x = rng.choice(4, p=np.clip(row, 0, None) / np.clip(row, 0, None).sum())
            lat[k] = x
    on = lat >= 2
    v = rng.random(S.n)
    obs[:] = np.where(on, v < q1, v < q0)
    return obs, on.astype(np.int8)


# ============================================================================================ observables
def raw_runs(S: Seq):
    """Raw runs of equal labels per sequence, length in calls (next run start - this run start); edge runs flagged.
    Returns arrays (label, length_calls, censored)."""
    lab, ln, cen = [], [], []
    if S.c is not None:
        cabs = S.c.astype(float)
    else:
        cabs = np.cumsum(np.where(np.isin(np.arange(S.n), S.ptr[:-1]), 0, S.step))
    for s in range(len(S.ptr) - 1):
        i0, i1 = S.ptr[s], S.ptr[s + 1]
        o = S.obs[i0:i1]
        cc = cabs[i0:i1]
        brk = np.flatnonzero(np.r_[True, o[1:] != o[:-1]])
        for j, st in enumerate(brk):
            en = brk[j + 1] if j + 1 < len(brk) else None
            if en is None:
                lab.append(o[st]); ln.append(np.nan); cen.append(True)
            else:
                lab.append(o[st]); ln.append(cc[en] - cc[st]); cen.append(j == 0)
    return np.array(lab), np.array(ln, float), np.array(cen)


def window_occupancy(obs, agent, win, min_n=2):
    """H105 agent-window spin: sigma = 1 if >= half of the agent's >= 2 statements in the window are on-goal.
    Returns (mean sigma over eligible agent-windows, n eligible)."""
    key = agent.astype(np.int64) * 100000 + win.astype(np.int64)
    u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    s = np.bincount(inv, weights=obs.astype(float))
    ok = cnt >= min_n
    if ok.sum() == 0:
        return np.nan, 0
    sig = (s[ok] / cnt[ok]) >= 0.5
    return float(sig.mean()), int(ok.sum())


# ============================================================================================ loading
def load_stmts(path):
    import polars as pl
    return pl.read_parquet(path)


def design_seq(df, variant="bge", dedupe=True, min_stmt=30, rg_mode="agent", seg_split=False, clock="call",
               min_seg=20, obs=None):
    """Build a Seq from one design's statements (a polars frame from stmts.parquet).
    rg_mode: 'agent' (per-agent rates), 'shared' (one rate group), 'seg' (rate group = segment; F/A, D/O),
    'agent_seg'. seg_split: sequences are broken at segment changes (kickoff designs; NE38).
    Steps are recomputed from the call index c (or minutes from t) after filtering, so dropped statements fold into gaps.
    Returns (Seq, meta dict with agents, segs, fold, day)."""
    import polars as pl
    d = df
    if dedupe:
        d = d.filter(~pl.col("dup"))
    d = d.sort("agent", "t")
    if seg_split:
        cnt = d.group_by("agent", "seg").len()
        okk = cnt.filter(pl.col("len") >= min_seg).group_by("agent").len().filter(pl.col("len") == cnt["seg"].n_unique())
        d = d.filter(pl.col("agent").is_in(okk["agent"].implode()))
    else:
        cnt = d.group_by("agent").len().filter(pl.col("len") >= min_stmt)
        d = d.filter(pl.col("agent").is_in(cnt["agent"].implode()))
    if d.height == 0:
        return None, None
    agents = np.sort(d["agent"].unique().to_numpy())
    amap = {int(a): i for i, a in enumerate(agents)}
    ag = d["agent"].to_numpy()
    segs = sorted(d["seg"].unique().to_list())
    smap = {s: i for i, s in enumerate(segs)}
    sg = np.array([smap[s] for s in d["seg"].to_list()])
    ai = np.array([amap[int(a)] for a in ag])
    if rg_mode == "agent":
        rg, nrg = ai, len(agents)
    elif rg_mode == "shared":
        rg, nrg = np.zeros(len(ai), int), 1
    elif rg_mode == "seg":
        rg, nrg = sg, len(segs)
    else:
        rg, nrg = ai * len(segs) + sg, len(agents) * len(segs)
    seq_key = ai * 10 + (sg if seg_split else 0)
    c = d["c"].to_numpy().astype(float)
    tmin = d["t"].dt.epoch("us").to_numpy() / 6e7
    x = c if clock == "call" else tmin
    step = np.r_[0.0, np.diff(x)]
    first = np.r_[True, seq_key[1:] != seq_key[:-1]]
    step[first] = 0.0
    step = np.maximum(step, 0.0)
    days = d["pt_date"].to_list()
    ud = {dd: i for i, dd in enumerate(sorted(set(days)))}
    day = np.array([ud[dd] for dd in days])
    o = d[f"b_{variant}"].to_numpy() if obs is None else obs
    win = day.astype(np.int64) * 1000 + d["win30"].to_numpy().astype(np.int64)
    S = make_seq(o, step, rg, seq_key, nrg, agent=ag, win=win, c=c)
    return S, dict(agents=agents, segs=segs, day=day, seg=sg, ai=ai, tmin=tmin, c=c, seq_key=seq_key, frame=d)


def fold_seq(S: Seq, meta, fold, clock="call"):
    """Statements on days with day % 2 == fold; steps recomputed from the absolute clock (gaps span removed days)."""
    mask = (meta["day"] % 2) == fold
    x = meta["c"] if clock == "call" else meta["tmin"]
    idx = np.flatnonzero(mask)
    key = meta["seq_key"][idx]
    xx = x[idx]
    step = np.r_[0.0, np.diff(xx)]
    first = np.r_[True, key[1:] != key[:-1]]
    step[first] = 0.0
    S2 = make_seq(S.obs[idx], np.maximum(step, 0), S.rg[idx], key, S.n_rg, S.agent[idx], S.win[idx], S.c[idx])
    return S2


# ============================================================================================ the unit pipeline
def restrict_agents(S: Seq, meta, keep_ai):
    """Keep statements of agents (agent indices) in keep_ai; rate groups re-indexed."""
    keep_ai = np.asarray(sorted(keep_ai))
    mask = np.isin(meta["ai"], keep_ai)
    remap = -np.ones(S.n_rg, np.int64)
    remap[keep_ai] = np.arange(len(keep_ai))
    idx = np.flatnonzero(mask)
    m2 = {k: (v[idx] if isinstance(v, np.ndarray) and len(v) == S.n else v) for k, v in meta.items() if k != "frame"}
    m2["ai"] = remap[meta["ai"][idx]]
    m2["agents"] = meta["agents"][keep_ai]
    m2["seq_key"] = m2["ai"] * 10 + (meta["seq_key"][idx] % 10)
    S2 = make_seq(S.obs[idx], S.step[idx], remap[S.rg[idx]], m2["seq_key"], len(keep_ai), S.agent[idx], S.win[idx],
                  S.c[idx])
    return S2, m2


def predicted_window_occupancy(Sb: Seq, f, rng, n_sim=100):
    vals = []
    for _ in range(n_sim):
        o, _ = simulate2(Sb, f["a"], f["b"], f["q0"], f["q1"], rng)
        vals.append(window_occupancy(o, Sb.agent, Sb.win)[0])
    vals = np.array(vals)
    return float(np.nanmean(vals)), np.nanpercentile(vals, [5, 95])


def fit2a(S: Seq, qmode="fixed", wall=False):
    """Per-agent M2. qmode 'free': emissions free jointly with the per-agent rates; 'fixed': emissions taken from the
    shared-rate fit (M2s) on the same data, then per-agent rates fitted with emissions held (two-stage)."""
    if qmode == "free":
        return fit2(S, wall=wall)
    Ss = Seq(S.obs, S.step, np.zeros(S.n, np.int64), S.ptr, 1)
    fs = fit2(Ss, wall=wall)
    init = dict(a=np.full(S.n_rg, fs["a"][0]), b=np.full(S.n_rg, fs["b"][0]), q0=fs["q0"], q1=fs["q1"])
    f = fit2(S, wall=wall, init=init, q_fixed=(fs["q0"], fs["q1"]))
    f["shared"] = fs
    return f


def evaluate_unit(S: Seq, meta, rng, n_sim=100, do_wall=True, min_fold=10, qmode="fixed"):
    """Card observables for one unit (per-agent rates). Agents with < min_fold statements in either day fold are
    dropped first, so every held-out rate group was fitted. Returns a dict."""
    ai = meta["ai"]
    day = meta["day"]
    keep = [i for i in range(S.n_rg) if ((ai == i) & (day % 2 == 0)).sum() >= min_fold
            and ((ai == i) & (day % 2 == 1)).sum() >= min_fold]
    out = dict(n_agents_in=int(S.n_rg))
    if len(keep) < 3 or len(np.unique(day)) < 2:
        out["eligible"] = False
        return out
    S, meta = restrict_agents(S, meta, keep)
    out.update(eligible=True, n_agents=len(keep), n_stmt=int(S.n), f_on=float(S.obs.mean()))
    f2 = fit2a(S, qmode)
    f2s = fit2(make_seq(S.obs, S.step, np.zeros(S.n, int), meta["seq_key"], 1))
    f4 = fit4p(S, f2)
    pdw_i = f2["a"] / (f2["a"] + f2["b"])
    w = np.bincount(S.rg, minlength=S.n_rg).astype(float)
    out.update(q0=f2["q0"], q1=f2["q1"], ll2=f2["ll"], ll4=f4["ll"], cv_on=f4["cv_on"], cv_off=f4["cv_off"],
               ra=f4["ra"], rb=f4["rb"], won=f4["won"], woff=f4["woff"],
               p_dw=float(np.sum(pdw_i * w) / w.sum()), tau_on_med=float(np.median(1 / f2["b"])),
               tau_off_med=float(np.median(1 / f2["a"])), a_i=f2["a"].tolist(), b_i=f2["b"].tolist(),
               agents=[int(x) for x in meta["agents"]],
               a_s=float(f2s["a"][0]), b_s=float(f2s["b"][0]), q0_s=f2s["q0"], q1_s=f2s["q1"],
               p_dw_s=float(f2s["a"][0] / (f2s["a"][0] + f2s["b"][0])))
    # raw runs (P6, P7)
    lab, ln, cen = raw_runs(S)
    okr = ~cen & np.isfinite(ln)
    on_r, off_r = ln[okr & (lab == 1)], ln[okr & (lab == 0)]
    out.update(raw_on_med=float(np.median(on_r)) if len(on_r) else np.nan,
               raw_off_med=float(np.median(off_r)) if len(off_r) else np.nan,
               raw_on_mean=float(np.mean(on_r)) if len(on_r) else np.nan,
               raw_off_mean=float(np.mean(off_r)) if len(off_r) else np.nan, n_raw_on=int(len(on_r)))
    out["p_rawrun"] = (out["raw_on_mean"] / (out["raw_on_mean"] + out["raw_off_mean"])
                       if len(on_r) and len(off_r) else np.nan)
    pw, nw = window_occupancy(S.obs, S.agent, S.win)
    out.update(p_win=pw, n_win=nw)
    # two-fold held-out (P1, P2, P5)
    dll4, dllw, rho, nn = 0.0, 0.0, [], 0
    pobs, ppred = [], []
    for fold in (0, 1):
        Sa = fold_seq(S, meta, fold)
        Sb = fold_seq(S, meta, 1 - fold)
        fa2 = fit2a(Sa, qmode)
        fa4 = fit4p(Sa, fa2)
        dll4 += ll4(Sb, fa4) - ll2(Sb, fa2["a"], fa2["b"], fa2["q0"], fa2["q1"])
        nn += Sb.n
        if do_wall:
            Saw = fold_seq(S, meta, fold, clock="wall")
            Sbw = fold_seq(S, meta, 1 - fold, clock="wall")
            faw = fit2a(Saw, qmode, wall=True)
            dllw += ll2(Sb, fa2["a"], fa2["b"], fa2["q0"], fa2["q1"]) - ll2(Sbw, faw["a"], faw["b"], faw["q0"], faw["q1"],
                                                                              wall=True)
        po, _ = window_occupancy(Sb.obs, Sb.agent, Sb.win)
        pp, band = predicted_window_occupancy(Sb, fa2, rng, n_sim)
        pobs.append(po)
        ppred.append(pp)
        rho.append(math.log(po / pp) if po > 0 and pp > 0 else np.nan)
    out.update(dll4_held=dll4 / nn, dllw_held=(dllw / nn) if do_wall else np.nan, rho_p=float(np.nanmean(rho)),
               rho_p_folds=rho, p_win_obs_folds=pobs, p_win_pred_folds=ppred)
    out["_fit2"] = f2
    out["_S"] = S
    out["_meta"] = meta
    return out


def bootstrap_shape_null(S: Seq, meta, f2, rng, B=30, qmode="fixed"):
    """N0: simulate the fitted M2 (per-agent) on the real skeleton; recompute the held-out dLL(M4p - M2) per statement
    and the M4p CVs."""
    vals, cvs = [], []
    for _ in range(B):
        o, _ = simulate2(S, f2["a"], f2["b"], f2["q0"], f2["q1"], rng)
        Sx = Seq(o, S.step, S.rg, S.ptr, S.n_rg, S.agent, S.win, S.c)
        d, nn = 0.0, 0
        for fold in (0, 1):
            Sa = fold_seq(Sx, meta, fold)
            Sb = fold_seq(Sx, meta, 1 - fold)
            fa2 = fit2a(Sa, qmode)
            fa4 = fit4p(Sa, fa2)
            d += ll4(Sb, fa4) - ll2(Sb, fa2["a"], fa2["b"], fa2["q0"], fa2["q1"])
            nn += Sb.n
        vals.append(d / nn)
    return np.array(vals)


def p1_verdict(dll4, null_vals, cv_on, cv_off):
    """Card P1: exponential unless dLL exceeds the null 95th percentile AND a CV >= 2 (heavy-tailed)."""
    q95 = float(np.percentile(null_vals, 95))
    exceed = dll4 > q95
    heavy = max(cv_on, cv_off) >= 2
    if exceed and heavy:
        return "heavy", q95
    return "exponential", q95


def fit_segments(S: Seq):
    """M2 with rate groups = segments (rg already = segment index); returns fit."""
    return fit2(S)


def seg_bootstrap(df_frame, build, rng, B=200):
    """Agent-cluster bootstrap for segment-rate contrasts. build(frame) -> Seq with rg = segment (0 = first segment,
    1 = second). Returns array of (dln_a, dln_b)."""
    import polars as pl
    df_frame = df_frame.with_columns(pl.col("agent").cast(pl.Int32))
    agents = df_frame["agent"].unique().to_numpy()
    out = []
    for _ in range(B):
        pick = rng.choice(agents, len(agents), replace=True)
        parts = []
        for j, a in enumerate(pick):
            parts.append(df_frame.filter(pl.col("agent") == a).with_columns(pl.lit(int(1000 + j), dtype=pl.Int32).alias("agent")))
        fr = pl.concat(parts)
        S = build(fr)
        if S is None:
            continue
        f = fit2(S)
        out.append((math.log(f["a"][1] / f["a"][0]), math.log(f["b"][1] / f["b"][0])))
    return np.array(out)
