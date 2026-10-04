"""Shared null library (DQ8): surrogates, placebo designs and parametric nulls, each with a documented size
calibration on simulator output (simulate.py). Every null here is a function of plain arrays, so hypotheses can call
it on real data and on synthetic data alike.

Surrogates (per-day arrays, T_d x N, agents in columns)
  crossday(days, rng)              agent i's day d <- the same agent's day (d + c_i) mod D (balanced offsets), aligned
                                   by minute of the day, wrapped / truncated to the target day's length. Keeps daily
                                   profiles, the operator schedule and autocorrelation; breaks same-day co-movement.
                                   (H12's primary null; H05's choice for entropy production.)
  circshift(days, rng)             independent circular shift per agent and day (misaligns daily profiles).
  block_shift(days, minutes, rng)  independent circular shift per agent within each (day, 30-min block) (H25/H38 N1).
  joint=[...] on all three         extra per-day arrays (reasons, talk spins) shifted with the same offsets.
  room_relabel(rooms, rng)         agents swap whole room trajectories (columns permuted): room sizes preserved at
                                   every time (H26's N2).
Placebo designs
  placebo_dates(event, dates, ...)            dates matched on weekday (the Monday effect), >= `gap` active days away.
  lever_design(kicks, act, ...)               episodes and controls eligible on PAST information only, both arms cut at
                                              the agent's next kick (H39's rule); future_kick_free=True gives the
                                              biased variant (documentation / tests only).
  crossday_message_placebo(sender, day, tod)  the same sender's message on another day at a matched time of day (H29).
Parametric
  fit_ordinal / simulate_ordinal / agent_field_null   H37's ordered-logit agent-field null for signed reply graphs
                                   (speaker and target fields, no pair structure), copied from
                                   hypotheses/H37-stance-spins/analysis/calibrate.py (Amendment 2).
  sign_shuffle(J, rng)             H37's sign-shuffle null on a residual signed pair matrix (magnitudes kept, signs
                                   permuted): anti-conservative under agent fields (size table).
  label_permutation(y, rng)        stance labels permuted across replies.
Statistics (used in the calibration; reusable)
  stat_cw_gain       pooled equal-time loop gain g = 1 - 1/VR, agents centered within (day, 30-min block) (H02/H19/H25)
  stat_lambda1       top eigenvalue of the equal-time correlation matrix (H12)
  stat_room_excess   within-room minus cross-room pair correlation of agent-window content deviations (H26-like)
  stat_event_step    mean over agents of (k active days after - k before) a date
  stat_signed        faction score 1 - 2f of the residual signed graph (spectral split + greedy) and the count of
                     significantly negative pairs (BH q = 0.1) (H37-like)
  stat_message_pull  cos(next statement, seen message) minus cos(next statement, placebo message) (H29-like)
  stall_mask         H25's null-calibrated platform-stall mask (runs of all-silent minutes longer than chance)
  explained_silence_mask  H38's stall rule: joint silence (K <= 1) explained by recorded silence reasons
  all_present_window H38's operator rule: minutes in which every agent present that day is in its span
Size calibration
  calibrate(reps, n_surr, ...)     false-positive rate at alpha = 0.05 for every (null, statistic) under null
                                   dynamics with village nuisances (schedules, shared fields, day edges, stalls,
                                   weekday effects, state-dependent kick targeting, agent fields, content drives),
                                   plus power columns. Writes infra/data-quality/null_sizes.json and
                                   data/processed/shared/null_sizes.parquet (+ provenance).
  Usage: uv run python infra/shared/nulls.py --calibrate [--reps 100] [--surr 49] [--workers 2]
Docs: infra/data-quality/simulator_and_nulls.md (size table, bands). Tests: infra/shared/tests/test_nulls.py.
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import datetime as dt  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parents[1]
SH = ROOT / "data/processed/shared"
SIZES_JSON = ROOT / "infra/data-quality/null_sizes.json"
ALPHA = 0.05


# ============================================================================================ p-values, bands
def pvalue(obs: float, null: np.ndarray, side: str = "greater") -> float:
    """Monte Carlo p-value (1 + #{null >= obs}) / (1 + n); side 'two' doubles the smaller tail (capped at 1)."""
    null = np.asarray(null, float)
    null = null[np.isfinite(null)]
    if not np.isfinite(obs) or len(null) == 0:
        return float("nan")
    hi = (1 + np.sum(null >= obs)) / (1 + len(null))
    if side == "greater":
        return float(hi)
    lo = (1 + np.sum(null <= obs)) / (1 + len(null))
    if side == "less":
        return float(lo)
    return float(min(1.0, 2 * min(hi, lo)))


def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def size_band(reps: int, alpha: float = ALPHA) -> tuple:
    """Acceptance band for an empirical size at `reps` replicates: the central 95% binomial range around alpha."""
    from scipy.stats import binom
    return (float(binom.ppf(0.025, reps, alpha) / reps), float(binom.ppf(0.975, reps, alpha) / reps))


# ============================================================================================ surrogates
def _as_list(days):
    return [np.asarray(x) for x in days]


def crossday(days: list, rng: np.random.Generator, joint: list | None = None):
    """Agent i's day d <- agent i's day (d + c_i) mod D, c_i = a balanced permutation of (0..N-1) mod D; aligned by
    minute index from the day's start, wrapped circularly when the source is shorter, truncated when longer.
    days: list of (T_d x N) arrays. joint: optional list of further lists shifted identically. D = 1 returns copies."""
    days = _as_list(days)
    D = len(days)
    N = days[0].shape[1]
    c = rng.permutation(np.arange(N) % D) if D > 1 else np.zeros(N, int)

    def apply(dl):
        out = []
        for d in range(D):
            T = dl[d].shape[0]
            Y = np.empty_like(dl[d])
            for i in range(N):
                src = dl[(d + c[i]) % D]
                Y[:, i] = src[np.arange(T) % src.shape[0], i]
            out.append(Y)
        return out
    res = apply(days)
    if joint:
        return res, [apply(_as_list(j)) for j in joint]
    return res


def circshift(days: list, rng: np.random.Generator, joint: list | None = None):
    """Independent circular shift per agent within each day (shift drawn uniformly over the day length)."""
    days = _as_list(days)
    shifts = [rng.integers(0, max(d.shape[0], 1), d.shape[1]) for d in days]

    def apply(dl):
        out = []
        for d, X in enumerate(dl):
            T, N = X.shape[0], X.shape[1]
            idx = (np.arange(T)[:, None] - shifts[d][None, :]) % T
            out.append(X[idx, np.arange(N)[None, :]])
        return out
    res = apply(days)
    if joint:
        return res, [apply(_as_list(j)) for j in joint]
    return res


def block_shift(days: list, minutes: list, rng: np.random.Generator, block_min: int = 30, joint: list | None = None):
    """Independent circular shift (>= 1) per agent within each (day, block) of `block_min` minutes (H38's N1)."""
    days = _as_list(days)
    plan = []
    for X, m in zip(days, minutes):
        blk = np.asarray(m) // block_min
        segs = [np.flatnonzero(blk == b) for b in np.unique(blk)]
        plan.append([(ix, rng.integers(1, len(ix), X.shape[1]) if len(ix) > 1 else np.zeros(X.shape[1], int))
                     for ix in segs])

    def apply(dl):
        out = []
        for X, pl_ in zip(dl, plan):
            Y = np.empty_like(X)
            N = X.shape[1]
            for ix, sh in pl_:
                L = len(ix)
                ar = (np.arange(L)[:, None] - sh[None, :]) % L
                Y[ix] = X[ix][ar, np.arange(N)[None, :]]
            out.append(Y)
        return out
    res = apply(days)
    if joint:
        return res, [apply(_as_list(j)) for j in joint]
    return res


def room_relabel(rooms: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """rooms: (N,) or (T x N) room codes. Agents swap whole room trajectories (a column permutation), which keeps the
    room sizes at every time; returns the relabeled array."""
    rooms = np.asarray(rooms)
    perm = rng.permutation(rooms.shape[-1])
    return rooms[..., perm]


# ============================================================================================ placebo designs
def placebo_dates(event_date: str, dates: list, match_weekday: bool = True, gap: int = 3,
                  exclude: list | None = None) -> list:
    """Placebo dates for an event study: active dates (sorted ISO strings) with the event's weekday (if matched),
    at least `gap` active days away from the event and from every date in `exclude`, and with `gap` active days on
    both sides inside the timeline (so the step statistic is defined)."""
    dates = sorted(dates)
    pos = {d: i for i, d in enumerate(dates)}
    wd = dt.date.fromisoformat(event_date).weekday()
    bad = {pos[event_date]} if event_date in pos else set()
    for x in exclude or []:
        if x in pos:
            bad.add(pos[x])
    out = []
    for d in dates:
        i = pos[d]
        if i < gap or i + gap > len(dates):
            continue
        if any(abs(i - b) < gap for b in bad):
            continue
        if match_weekday and dt.date.fromisoformat(d).weekday() != wd:
            continue
        out.append(d)
    return out


def placebo_test(obs: float, placebo: np.ndarray) -> float:
    """Two-sided t prediction-interval p-value of obs against placebo values (exchangeable placebo draws)."""
    from scipy.stats import t as tdist
    x = np.asarray(placebo, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 3 or not np.isfinite(obs):
        return float("nan")
    s = x.std(ddof=1)
    if s <= 0:
        return float("nan")
    z = (obs - x.mean()) / (s * math.sqrt(1 + 1 / n))
    return float(2 * tdist.sf(abs(z), n - 1))


def lever_design(kicks: list, act: list, W: int = 20, quiet: int = 30, R: int = 10,
                 age_edges=(1, 2, 5, 10, 15, 30), rng: np.random.Generator | None = None,
                 future_kick_free: bool = False, present: list | None = None, cut: str = "none") -> dict:
    """Point-lever episodes vs matched controls (H39's rule).

    kicks: per day, a list of (minute_row, agent) kick events; act: per day (T x N) bool activity.
    Episode: a kick to an inactive agent with no kick to it in the previous `quiet` minutes; outcome = the agent's mean
    activity over (m, m + W] (intention to treat: kick now vs not now), cut at the end of the day / presence.
    Controls: minutes of the same agent with the same state (inactive) and inactivity-age bin, no kick to it in
    [m - quiet, m] (PAST information only), outcome measured the same way.
    cut="next_kick" also cuts both arms at the agent's next kick. That is right for hazard (transition-rate)
    estimators (H39's K), but for window means it is state-dependent censoring when the kicker targets agents that
    stay idle (controls that stay idle get kicked and cut, so their later activity is lost): biased, documented in
    the size table (lever_controls_past_cut).
    future_kick_free=True additionally requires controls to stay kick-free over (m, m + W]: the biased variant that
    H39 found manufactures effects when the kicker targets agents that stay idle.
    present: per day (T x N) bool, the agent is present (between its first and last record of the day). Episodes and
    controls must be present, and outcome windows are cut at the end of presence: minutes before an agent's first or
    after its last record are inactive by construction, and matching on them fakes an effect (H17's grid-idle trap;
    the calibration shows p < 0.05 in most null replicates without this mask).
    Returns dict(y_ep, y_ctrl (mean over R controls), day (episode day index), n_ep)."""
    rng = rng or np.random.default_rng(0)
    y_ep, y_ct, dayix, agix = [], [], [], []
    edges = np.asarray(age_edges)
    for d, (kl, A) in enumerate(zip(kicks, act)):
        T, N = A.shape
        P = np.ones((T, N), bool) if present is None else np.asarray(present[d], bool)
        last_p = np.where(P.any(0), T - 1 - np.argmax(P[::-1], 0), -1)
        kmask = np.zeros((T, N), bool)
        for m, i in kl:
            if 0 <= m < T:
                kmask[m, i] = True
        # inactivity age
        age = np.zeros((T, N), int)
        for t in range(T):
            age[t] = np.where(A[t], 0, (age[t - 1] + 1) if t else 1)
        abin = np.searchsorted(edges, age, side="right")
        # next kick strictly after t (per agent)
        nxt = np.full((T + 1, N), T, int)
        for t in range(T - 1, -1, -1):
            nxt[t] = np.where(kmask[t], t, nxt[t + 1])
        nxt_after = nxt[np.minimum(np.arange(T) + 1, T)]
        cs = np.vstack([np.zeros((1, N)), np.cumsum(kmask, 0)])
        csA = np.vstack([np.zeros((1, N)), np.cumsum(A, 0)])

        def outcome(m, i):
            e = min(T - 1, m + W, last_p[i])
            if cut == "next_kick":
                e = min(e, nxt_after[m, i] - 1)
            if e <= m:
                return np.nan
            return (csA[e + 1, i] - csA[m + 1, i]) / (e - m)
        past_free = np.zeros((T, N), bool)
        for t in range(T):
            a = max(0, t - quiet)
            past_free[t] = (cs[t + 1] - cs[a]) == 0
        fut_free = np.zeros((T, N), bool)
        for t in range(T):
            b = min(T, t + W + 1)
            fut_free[t] = (cs[b] - cs[t + 1]) == 0
        elig = past_free & ~A & P & (np.arange(T)[:, None] + 1 < T)
        if future_kick_free:
            elig &= fut_free
        for m, i in kl:
            if not (0 <= m < T) or A[m, i] or not P[m, i]:
                continue
            a = max(0, m - quiet)
            if cs[m, i] - cs[a, i] > 0:   # another kick in [m - quiet, m - 1]
                continue
            ye = outcome(m, i)
            if not np.isfinite(ye):
                continue
            pool = np.flatnonzero(elig[:, i] & (abin[:, i] == abin[m, i]))
            pool = pool[pool != m]
            if len(pool) < 3:
                continue
            pick = pool[rng.integers(0, len(pool), R)]
            yc = np.array([outcome(int(t), i) for t in pick])
            yc = yc[np.isfinite(yc)]
            if len(yc) == 0:
                continue
            y_ep.append(ye)
            y_ct.append(yc.mean())
            dayix.append(d)
            agix.append(i)
    return {"y_ep": np.array(y_ep), "y_ctrl": np.array(y_ct), "day": np.array(dayix, int), "agent": np.array(agix, int),
            "n_ep": len(y_ep)}


def cluster_boot_test(diff: np.ndarray, cluster: np.ndarray, B: int = 500, rng=None) -> tuple:
    """Mean of `diff` with a cluster bootstrap: returns (mean, lo95, hi95, two-sided p). p uses the bootstrap SE with a
    t reference on (clusters - 1) df. Use many clusters (agent-days, not days): with ~6 day clusters the bootstrap SE
    is too small and the test is anti-conservative (calibration, 2026-10-04)."""
    rng = rng or np.random.default_rng(0)
    diff = np.asarray(diff, float)
    cluster = np.asarray(cluster)
    ok = np.isfinite(diff)
    diff, cluster = diff[ok], cluster[ok]
    if len(diff) < 3:
        return (np.nan, np.nan, np.nan, np.nan)
    u, inv = np.unique(cluster, return_inverse=True)
    s = np.bincount(inv, diff, len(u))
    c = np.bincount(inv, None, len(u))
    est = s.sum() / c.sum()
    if len(u) < 3:
        return (est, np.nan, np.nan, np.nan)
    idx = rng.integers(0, len(u), (B, len(u)))
    bs = s[idx].sum(1) / np.maximum(c[idx].sum(1), 1)
    lo, hi = np.quantile(bs, [0.025, 0.975])
    se = bs.std(ddof=1)
    from scipy.stats import t as tdist
    p = float(2 * tdist.sf(abs(est) / se, len(u) - 1)) if se > 0 else np.nan
    return (float(est), float(lo), float(hi), p)


def crossday_message_placebo(sender: np.ndarray, day: np.ndarray, tod_s: np.ndarray, rng: np.random.Generator,
                             tol_s: float = 1800.0) -> np.ndarray:
    """For each message k: a random message by the same sender on a different day whose time of day is within
    tol_s of k's (H29's cross-day placebo). Returns indices (-1 where none exists)."""
    sender, day, tod_s = np.asarray(sender), np.asarray(day), np.asarray(tod_s, float)
    out = np.full(len(sender), -1, np.int64)
    for s in np.unique(sender):
        ix = np.flatnonzero(sender == s)
        for k in ix:
            c = ix[(day[ix] != day[k]) & (np.abs(tod_s[ix] - tod_s[k]) <= tol_s)]
            if len(c):
                out[k] = int(rng.choice(c))
    return out


# ============================================================================================ parametric (H37)
def fit_ordinal(spk, tgt, y, N, lam: float = 0.1):
    """Ordered logit P(y <= k) = sigmoid(c_k - a_speaker - b_target), y in {0, 1, 2} (-, 0, +), L2 penalty lam on
    the fields; returns ((c1, c2), a, b, success). Copied from H37 calibrate.py (Amendment 2, 2026-10-04)."""
    from scipy.optimize import minimize

    def unpack(th):
        c1 = th[0]
        c2 = c1 + np.exp(th[1])
        a = np.r_[0, th[2:N + 1]]
        b = np.r_[0, th[N + 1:]]
        return c1, c2, a, b

    def nll(th):
        c1, c2, a, b = unpack(th)
        eta = a[spk] + b[tgt]
        F1 = 1 / (1 + np.exp(-(c1 - eta)))
        F2 = 1 / (1 + np.exp(-(c2 - eta)))
        p = np.where(y == 0, F1, np.where(y == 1, F2 - F1, 1 - F2))
        p = np.clip(p, 1e-12, 1)
        f1 = F1 * (1 - F1)
        f2 = F2 * (1 - F2)
        d_eta = np.where(y == 0, -f1 / p, np.where(y == 1, (-f2 + f1) / p, f2 / p))
        d_c1 = np.where(y == 0, f1 / p, np.where(y == 1, -f1 / p, 0))
        d_c2 = np.where(y == 1, f2 / p, np.where(y == 2, -f2 / p, 0))
        ga = np.bincount(spk, d_eta, N)[1:]
        gb = np.bincount(tgt, d_eta, N)[1:]
        g = -np.r_[d_c1.sum() + d_c2.sum(), d_c2.sum() * (c2 - c1), ga, gb]
        th_f = th[2:]
        return -np.log(p).sum() + lam * (th_f ** 2).sum(), g + np.r_[0, 0, 2 * lam * th_f]
    th0 = np.r_[-2.5, np.log(3.0), np.zeros(2 * (N - 1))]
    r = minimize(nll, th0, jac=True, method="L-BFGS-B")
    c1, c2, a, b = unpack(r.x)
    return (c1, c2), a, b, bool(r.success)


def simulate_ordinal(spk, tgt, c, a, b, rng) -> np.ndarray:
    eta = a[spk] + b[tgt]
    u = rng.logistic(size=len(eta)) + eta
    return np.where(u < c[0], -1.0, np.where(u < c[1], 0.0, 1.0))


def agent_field_null(spk, tgt, s, N, R: int, rng):
    """Generator of R replicate signed label sets (-1/0/+1) from the fitted agent-field ordered logit."""
    c, a, b, _ = fit_ordinal(spk, tgt, (np.asarray(s) + 1).astype(int), N)
    for _ in range(R):
        yield simulate_ordinal(spk, tgt, c, a, b, rng)


def label_permutation(s: np.ndarray, rng) -> np.ndarray:
    """The anti-conservative 'sign shuffle': labels permuted across replies (destroys agent fields)."""
    return rng.permutation(np.asarray(s))


# ============================================================================================ statistics
def stat_cw_gain(days: list, minutes: list, block_min: int = 30, valid: list | None = None) -> float:
    """Pooled equal-time loop gain g = 1 - 1/VR, VR = sum_t (sum_i X_it)^2 / sum_t sum_i X_it^2, X = spins centered
    per agent within (day, block); blocks with < 5 kept minutes dropped. valid: optional per-day row masks."""
    num = den = 0.0
    for k, (S, m) in enumerate(zip(days, minutes)):
        S = np.asarray(S, float)
        m = np.asarray(m)
        if valid is not None:
            S, m = S[valid[k]], m[valid[k]]
        blk = m // block_min
        for b in np.unique(blk):
            X = S[blk == b]
            if len(X) < 5:
                continue
            X = X - X.mean(0)
            num += (X.sum(1) ** 2).sum()
            den += (X * X).sum()
    return float(1 - den / num) if num > 0 else float("nan")


def stat_lambda1(days: list, valid: list | None = None) -> float:
    X = np.concatenate([np.asarray(S, float)[valid[k]] if valid is not None else np.asarray(S, float)
                        for k, S in enumerate(days)], 0)
    sd = X.std(0)
    X = X[:, sd > 0]
    if X.shape[1] < 2:
        return float("nan")
    Z = (X - X.mean(0)) / X.std(0)
    return float(np.linalg.eigvalsh(Z.T @ Z / len(Z))[-1])


def stat_room_excess(X: np.ndarray, rooms: np.ndarray) -> float:
    """X: N x W x d agent-window vectors (NaN = none); rooms: W x N. Each agent's mean over its windows is removed and
    its deviations scaled to unit mean square; rho(w) pair products <r_i, r_j> are averaged over same-room and
    cross-room pairs (room at the window). Returns rho_within - rho_cross."""
    N, W, d = X.shape
    has = np.isfinite(X).all(2)
    R = np.where(has[..., None], X, 0.0)
    cnt = has.sum(1)
    mu = R.sum(1) / np.maximum(cnt, 1)[:, None]
    R = np.where(has[..., None], R - mu[:, None], 0.0)
    ms = (R ** 2).sum((1, 2)) / np.maximum(cnt, 1)
    R = R / np.sqrt(np.where(ms > 0, ms, 1))[:, None, None]
    sw = cw_ = nw = nc = 0.0
    iu = np.triu_indices(N, 1)
    for w in range(W):
        h = has[:, w]
        if h.sum() < 2:
            continue
        G = R[:, w] @ R[:, w].T
        pair = h[:, None] & h[None, :]
        same = rooms[w][:, None] == rooms[w][None, :]
        P = pair[iu]
        S_ = same[iu]
        g = G[iu]
        sw += g[P & S_].sum()
        nw += (P & S_).sum()
        cw_ += g[P & ~S_].sum()
        nc += (P & ~S_).sum()
    if nw == 0 or nc == 0:
        return float("nan")
    return float(sw / nw - cw_ / nc)


def stat_event_step(daily: np.ndarray, e: int, k: int = 3) -> float:
    """daily: D x N per-day values (NaN = absent); e: event day index. Mean over agents of after - before."""
    a = np.nanmean(daily[e:e + k], 0)
    b = np.nanmean(daily[e - k:e], 0)
    return float(np.nanmean(a - b))


def _residual_matrix(spk, tgt, s, N, nmin: int = 3):
    """Additive two-way fit s ~ mu + a_speaker + b_target (alternating means), residual pair means (both
    directions pooled), pairs with < nmin replies NaN. Returns (J (N x N), counts, residuals)."""
    s = np.asarray(s, float)
    a = np.zeros(N)
    b = np.zeros(N)
    mu = s.mean()
    for _ in range(20):
        a = np.bincount(spk, s - mu - b[tgt], N) / np.maximum(np.bincount(spk, None, N), 1)
        b = np.bincount(tgt, s - mu - a[spk], N) / np.maximum(np.bincount(tgt, None, N), 1)
    r = s - mu - a[spk] - b[tgt]
    lo, hi = np.minimum(spk, tgt), np.maximum(spk, tgt)
    key = lo * N + hi
    S = np.bincount(key, r, N * N).reshape(N, N)
    C = np.bincount(key, None, N * N).reshape(N, N)
    J = np.where(C >= nmin, S / np.maximum(C, 1), np.nan)
    J = np.where(np.isnan(J), J.T, J)
    return J, C + C.T, r, key


def stat_signed(spk, tgt, s, N, q: float = 0.1, nmin: int = 3) -> tuple:
    """(faction score 1 - 2f, n significantly negative pairs). Faction score: best two-camp split x of the residual
    signed graph (leading-eigenvector start + greedy single flips), sum_{i<j} J_ij x_i x_j / sum |J_ij|.
    Negative pairs: per-pair one-sample t-test of residuals < 0, Benjamini-Hochberg at q."""
    from scipy.stats import t as tdist
    J, C, r, key = _residual_matrix(spk, tgt, s, N, nmin)
    score = faction_score_matrix(J)
    if not np.isfinite(score):
        return (float("nan"), 0)
    # per-pair tests
    u = np.unique(key)
    pv = []
    for kk in u:
        rr = r[key == kk]
        if len(rr) < max(nmin, 2):
            continue
        sd = rr.std(ddof=1)
        if sd <= 0:
            continue
        tt = rr.mean() / (sd / math.sqrt(len(rr)))
        pv.append(tdist.cdf(tt, len(rr) - 1))
    pv = np.sort(np.array(pv))
    m = len(pv)
    nsig = 0
    if m:
        ok = pv <= q * np.arange(1, m + 1) / m
        nsig = int(np.flatnonzero(ok).max() + 1) if ok.any() else 0
    return (score, nsig)


def residual_pair_matrix(spk, tgt, s, N, nmin: int = 3) -> np.ndarray:
    """Residual signed pair matrix (two-way additive fit removed; pairs with < nmin replies NaN)."""
    return _residual_matrix(spk, tgt, s, N, nmin)[0]


def sign_shuffle(J: np.ndarray, rng) -> np.ndarray:
    """H37's sign-shuffle null for a signed pair matrix: magnitudes kept, signs permuted across observed pairs."""
    A = np.nan_to_num(np.asarray(J, float))
    N = A.shape[0]
    iu = np.triu_indices(N, 1)
    v = A[iu]
    obs = v != 0
    sg = np.sign(v[obs])
    v2 = v.copy()
    v2[obs] = np.abs(v[obs]) * rng.permutation(sg)
    B = np.zeros_like(A)
    B[iu] = v2
    return B + B.T


def faction_score_matrix(J: np.ndarray) -> float:
    """1 - 2f of the best two-camp split of a signed matrix (leading-eigenvector start + greedy single flips)."""
    A = np.nan_to_num(np.asarray(J, float))
    np.fill_diagonal(A, 0)
    A = (A + A.T) / 2
    N = A.shape[0]
    tot = np.abs(np.triu(A, 1)).sum()
    if tot <= 0:
        return float("nan")
    w, V = np.linalg.eigh(A)
    x = np.where(V[:, -1] >= 0, 1.0, -1.0)
    best = x @ A @ x / 2
    improved = True
    while improved:
        improved = False
        for i in range(N):
            delta = -2 * x[i] * (A[i] @ x)
            if delta > 1e-12:
                x[i] = -x[i]
                best += delta
                improved = True
    return float(best / tot)


def message_pull_rows(t_s, agent, vec, day, window_s: float = 1800.0, placebo: np.ndarray | None = None):
    """Per statement n (agent i): mean cos(x_n, x_m) over statements m by others in (t_n - window_s, t_n) on the same
    day, minus the same over their placebo messages (placebo[m] >= 0). Returns (diff per statement, day)."""
    t_s, agent, day = np.asarray(t_s, float), np.asarray(agent), np.asarray(day)
    V = np.asarray(vec, float)
    V = V / np.linalg.norm(V, axis=1, keepdims=True)
    o = np.lexsort((t_s, day))
    diffs, dd, aa = [], [], []
    for n in o:
        sel = np.flatnonzero((day == day[n]) & (t_s < t_s[n]) & (t_s > t_s[n] - window_s) & (agent != agent[n]))
        if placebo is not None:
            sel = sel[placebo[sel] >= 0]
        if len(sel) == 0:
            continue
        real = V[sel] @ V[n]
        plac = V[placebo[sel]] @ V[n]
        diffs.append(real.mean() - plac.mean())
        dd.append(day[n])
        aa.append(agent[n])
    return np.array(diffs), np.array(dd), np.array(aa)


def explained_silence_mask(act: np.ndarray, reasons: np.ndarray, present: np.ndarray, min_present: int = 3,
                           strict: bool = False) -> np.ndarray:
    """H38's stall rule (outages.py): joint silence K <= 1 among present agents on a day with >= min_present present,
    explained when >= half (strict: all but one) of the silent present agents have a recorded reason (> 0).
    act, reasons, present: T x N. Returns (T,) mask (True = explained joint silence)."""
    act = np.asarray(act, bool)
    pres_day = np.asarray(present, bool).any(0)
    n_present = int(pres_day.sum())
    K = (act & pres_day[None, :]).sum(1)
    sil = ~act & pres_day[None, :]
    nrec = (sil & (np.asarray(reasons) > 0)).sum(1)
    n_sil = n_present - K
    js = (K <= 1) & (n_present >= min_present)
    expl = (nrec >= n_sil - 1) if strict else (2 * nrec >= n_sil)
    return js & expl


def all_present_window(present: np.ndarray) -> np.ndarray:
    """H38's operator rule: minutes in which every agent present that day is between its first and last record."""
    P = np.asarray(present, bool)
    day_pres = P.any(0)
    if not day_pres.any():
        return np.zeros(P.shape[0], bool)
    return P[:, day_pres].all(1)


def stall_mask(any_event: np.ndarray, rng: np.random.Generator | None = None, n_surr: int = 50, q: float = 0.95,
               min_len: int = 3) -> np.ndarray:
    """H25's platform-stall mask (hypotheses/H25-criticality-dial/analysis/dial.py: find_stalls): runs of minutes
    with no agent event that are longer than the q-quantile of the longest all-silent run under whole-day circular
    shifts of each agent. any_event: T x N bool. Returns a (T,) mask (True = stall)."""
    A = np.asarray(any_event, bool)
    T, N = A.shape
    if rng is None:
        rng = np.random.default_rng(int(A.sum()) * 1000003 + T * 101 + N)
    if T == 0 or N == 0:
        return np.zeros(T, bool)

    def runs(x):
        if not x.any():
            return np.zeros(0, int), np.zeros(0, int)
        d = np.diff(np.r_[0, x.astype(np.int8), 0])
        st, en = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
        return st, en - st
    mx = np.zeros(n_surr)
    for k in range(n_surr):
        sh = rng.integers(0, T, N)
        idx = (np.arange(T)[:, None] + sh[None, :]) % T
        s = ~A[idx, np.arange(N)].any(1)
        _, L = runs(s)
        mx[k] = L.max() if L.size else 0
    Lstar = int(max(min_len, math.floor(np.quantile(mx, q)) + 1))
    st, L = runs(~A.any(1))
    mask = np.zeros(T, bool)
    for a, l in zip(st, L):
        if l >= Lstar:
            mask[a:a + l] = True
    return mask


# ============================================================================================ calibration
CAL_UNITS = ["12a", "13", "20c", "26", "35", "38a", "40", "41", "42b", "51c"]


_SK_CACHE: dict = {}


def _skeletons(units=None, toy_fallback=True):
    import simulate as SIM
    key = tuple(units or CAL_UNITS)
    if key in _SK_CACHE:
        return _SK_CACHE[key]
    out = []
    for u in units or CAL_UNITS:
        try:
            out.append(SIM.extract_skeleton(u))
        except Exception:
            continue
    if not out and toy_fallback:
        out = [SIM.toy_skeleton(N=10, n_days=5, seed=s) for s in range(4)]
    _SK_CACHE[key] = out
    return out


ACT_SCENARIOS = {
    # name: models for simulate(); J = 0 everywhere except the power column
    "indep": lambda SIM: {},
    "indep_flat": lambda SIM: {"activity": SIM.ActivityModel(profile="flat")},
    "fast_field": lambda SIM: {"activity": SIM.ActivityModel(fields=SIM.Fields(global_sd=0.6, global_tau=10))},
    "slow_field": lambda SIM: {"activity": SIM.ActivityModel(fields=SIM.Fields(global_sd=0.6, global_tau=120,
                                                                                tod_amp=0.4))},
    "day_edge": lambda SIM: {"edge": SIM.EdgeDrive(jitter=2, burst_min=10, burst_h=1.0)},
    "stalls": lambda SIM: {"stalls": SIM.StallModel(pi=0.05, free_prob=0.3)},
    "power_J0.5": lambda SIM: {"activity": SIM.ActivityModel(J=0.5)},
}


def _act_job(args):
    """Activity statistics under three preprocessing variants: raw (whole-day grid), trim (all-present window), and
    trim_h38mask (trim + H38's explained joint silences removed). Rows are removed before surrogates are drawn."""
    scen, rep, n_surr, seed = args
    import simulate as SIM
    rng = np.random.default_rng(seed)
    sks = _skeletons()
    sk = sks[rep % len(sks)]
    sim = SIM.simulate(sk, seed=seed, **ACT_SCENARIOS[scen](SIM))
    keep = np.any(np.vstack([ds.span.any(0) for ds in sim.days]), 0)
    raw = [np.where(ds.act, 1.0, -1.0)[:, keep] for ds in sim.days]
    mins = [d.minutes for d in sk.days]
    variants = {"raw": [np.ones(len(m), bool) for m in mins],
                "trim": [all_present_window(ds.span[:, keep]) for ds in sim.days]}
    variants["trim_h38mask"] = [v & ~explained_silence_mask(ds.act[:, keep], ds.reasons[:, keep], ds.span[:, keep])
                                for v, ds in zip(variants["trim"], sim.days)]
    rows = []
    for vn, vm in variants.items():
        days = [S[m] for S, m in zip(raw, vm) if m.sum() >= 10]
        mm = [mi[m] for mi, m in zip(mins, vm) if m.sum() >= 10]
        if not days:
            continue
        stats = {"cw_gain": lambda Y: stat_cw_gain(Y, mm)}
        if vn != "trim_h38mask":
            stats["lambda1"] = lambda Y: stat_lambda1(Y)
        obs = {k: f(days) for k, f in stats.items()}
        nulls = {"crossday": lambda: crossday(days, rng), "circshift": lambda: circshift(days, rng),
                 "block_shift": lambda: block_shift(days, mm, rng)}
        for nn, f in nulls.items():
            if nn == "crossday" and len(days) < 2:
                continue
            vals = {k: [] for k in stats}
            for _ in range(n_surr):
                Y = f()
                for k, g in stats.items():
                    vals[k].append(g(Y))
            for k in stats:
                rows.append({"null": nn, "statistic": f"{k}_{vn}", "scenario": scen, "rep": rep, "unit": sk.unit_id,
                             "p": pvalue(obs[k], np.array(vals[k]), "greater")})
    return rows


def _room_job(args):
    scen, rep, n_surr, seed = args
    import simulate as SIM
    rng = np.random.default_rng(seed)
    sk = SIM.toy_skeleton(N=12, n_days=5, T=240, n_rooms=2, stmt_rate=2.0, seed=1000 + rep)
    cm = {"indep": SIM.ContentModel(),
          "global_drive": SIM.ContentModel(sigma_G=0.6, A_tod=0.4),
          "room_drive": SIM.ContentModel(sigma_R=0.8),
          "power_J0.4": SIM.ContentModel(J=0.4, scope="room")}[scen]
    sim = SIM.simulate(sk, seed=seed, content=cm)
    X, dayix, rooms = sim.content_panel()
    obs = stat_room_excess(X, rooms)
    null = [stat_room_excess(X, room_relabel(rooms, rng)) for _ in range(n_surr)]
    return [{"null": "room_relabel", "statistic": "room_excess", "scenario": scen, "rep": rep, "unit": sk.unit_id,
             "p": pvalue(obs, np.array(null), "greater")}]


def _event_job(args):
    scen, rep, n_surr, seed = args
    import simulate as SIM
    rng = np.random.default_rng(seed)
    sk = SIM.toy_skeleton(N=8, n_days=80, T=90, seed=2000 + rep, nudge_rate=0, mention_rate=0, call_gap_min=30)
    f = {"indep": SIM.Fields(day_sd=0.15),
         "monday": SIM.Fields(day_sd=0.15, weekday={0: 0.5}),
         "power_step": SIM.Fields(day_sd=0.15)}[scen]
    am = SIM.ActivityModel(fields=f)
    sim = SIM.simulate(sk, seed=seed, activity=am)
    daily = np.stack([ds.act.mean(0) for ds in sim.days])
    dates = [d.pt_date for d in sk.days]
    mondays = [i for i, d in enumerate(sk.days) if d.weekday == 0 and 3 <= i <= len(dates) - 3]
    e = int(rng.choice(mondays))
    if scen == "power_step":
        daily[e:] += 0.08
    rows = []
    for k_ in (1, 3):
        obs = stat_event_step(daily, e, k=k_)
        for nn, match in (("placebo_dates_weekday", True), ("placebo_dates_any", False)):
            pd_ = placebo_dates(dates[e], dates, match_weekday=match, gap=3)
            pv = np.array([stat_event_step(daily, dates.index(x), k=k_) for x in pd_])
            rows.append({"null": nn, "statistic": f"event_step_k{k_}", "scenario": scen, "rep": rep,
                         "unit": sk.unit_id, "p": placebo_test(obs, pv), "n_placebo": len(pd_)})
    return rows


def _lever_job(args):
    scen, rep, n_surr, seed = args
    import simulate as SIM
    rng = np.random.default_rng(seed)
    sk = SIM.toy_skeleton(N=10, n_days=6, T=240, seed=3000 + rep, nudge_rate=0, mention_rate=0)
    h = 1.0 if scen == "power_h1" else 0.0
    km = SIM.KickModel(effects={"nudge": (h, 2, 20)}, source="idle", rate=0.04, idle_min=10)
    sim = SIM.simulate(sk, seed=seed, kicks=km)
    kicks = [[] for _ in sk.days]
    di = {d.pt_date: k for k, d in enumerate(sk.days)}
    for (pt, m, i, kind, hh, dl, du) in sim.kick_truth:
        kicks[di[pt]].append((m, i))
    act = [ds.act for ds in sim.days]
    pres = [ds.span for ds in sim.days]
    rows = []
    for nn, fut, pm, cut in (("lever_controls_past", False, pres, "none"), ("lever_controls_future", True, pres, "none"),
                             ("lever_controls_past_cut", False, pres, "next_kick"),
                             ("lever_controls_past_nopresence", False, None, "none")):
        r = lever_design(kicks, act, W=20, quiet=30, rng=np.random.default_rng(seed + 1), future_kick_free=fut,
                         present=pm, cut=cut)
        est, lo, hi, p = cluster_boot_test(r["y_ep"] - r["y_ctrl"], r["day"] * 1000 + r["agent"], B=400, rng=rng)
        rows.append({"null": nn, "statistic": "lever_effect", "scenario": scen, "rep": rep, "unit": sk.unit_id,
                     "p": p, "n_ep": r["n_ep"]})
    return rows


def _signed_job(args):
    scen, rep, n_surr, seed = args
    rng = np.random.default_rng(seed)
    sparse = scen == "sparse"
    N, n, conc, nmin = (20, 600, 0.5, 1) if sparse else (10, 1500, 1.5, 3)
    act = rng.dirichlet(np.ones(N) * conc)
    spk = rng.choice(N, n, p=act)
    tgt = rng.choice(N, n, p=act)
    bad = spk == tgt
    while bad.any():
        tgt[bad] = rng.choice(N, bad.sum(), p=act)
        bad = spk == tgt
    a = rng.normal(0, 0.6, N)
    b = rng.normal(0, 0.6, N)
    eta = a[spk] + b[tgt]
    if scen == "power_camps":
        xi = rng.permutation(np.r_[np.ones(N // 2), -np.ones(N - N // 2)])
        eta = eta + 0.6 * xi[spk] * xi[tgt]
    u = rng.logistic(size=n) + eta
    s = np.where(u < -2.0, -1.0, np.where(u < 1.2, 0.0, 1.0))
    obs = stat_signed(spk, tgt, s, N, nmin=nmin)
    rows = []
    null_af = [stat_signed(spk, tgt, x, N, nmin=nmin) for x in agent_field_null(spk, tgt, s, N, n_surr, rng)]
    null_lp = [stat_signed(spk, tgt, label_permutation(s, rng), N, nmin=nmin) for _ in range(n_surr)]
    Jr = residual_pair_matrix(spk, tgt, s, N, nmin=nmin)
    null_ss = [faction_score_matrix(sign_shuffle(Jr, rng)) for _ in range(n_surr)]
    rows.append({"null": "sign_shuffle", "statistic": "signed_faction", "scenario": scen, "rep": rep,
                 "unit": "synthetic", "p": pvalue(obs[0], np.array(null_ss), "greater")})
    rows.append({"null": "fdr_direct", "statistic": "signed_negpairs", "scenario": scen, "rep": rep,
                 "unit": "synthetic", "p": 0.0 if obs[1] >= 1 else 1.0})  # per-pair BH q=0.1: any pair flagged
    for nn, nl in (("agent_field", null_af), ("label_permutation", null_lp)):
        rows.append({"null": nn, "statistic": "signed_faction", "scenario": scen, "rep": rep, "unit": "synthetic",
                     "p": pvalue(obs[0], np.array([x[0] for x in nl]), "greater")})
        rows.append({"null": nn, "statistic": "signed_negpairs", "scenario": scen, "rep": rep, "unit": "synthetic",
                     "p": pvalue(obs[1], np.array([x[1] for x in nl], float), "greater")})
    return rows


def _pull_job(args):
    scen, rep, n_surr, seed = args
    import simulate as SIM
    rng = np.random.default_rng(seed)
    sk = SIM.toy_skeleton(N=8, n_days=6, T=240, stmt_rate=2.5, seed=4000 + rep)
    cm = {"indep": SIM.ContentModel(phi=0.0),
          "ou_drift": SIM.ContentModel(phi=0.85),
          "day_drive": SIM.ContentModel(phi=0.0, sigma_G=0.8),
          "power_degroot": SIM.ContentModel(kind="degroot", alpha=0.5, innov=0.05)}[scen]
    sim = SIM.simulate(sk, seed=seed, content=cm)
    t, ag, V, dd = [], [], [], []
    for k, ds in enumerate(sim.days):
        s = ds.stmts
        t.append(s["t_s"])
        ag.append(s["agent"])
        V.append(s["vec"])
        dd.append(np.full(len(s["agent"]), k))
    t, ag, V, dd = np.concatenate(t), np.concatenate(ag), np.vstack(V), np.concatenate(dd)
    rows = []
    for nn in ("crossday_message_placebo", "sameday_message_placebo"):
        if nn.startswith("crossday"):
            plc = crossday_message_placebo(ag, dd, t, rng, tol_s=1800)
        else:  # same sender, same day, a random other time (>= 1 h away): ignores recency / time-of-day drift
            plc = np.full(len(ag), -1, np.int64)
            for k in range(len(ag)):
                c = np.flatnonzero((ag == ag[k]) & (dd == dd[k]) & (np.abs(t - t[k]) >= 3600))
                if len(c):
                    plc[k] = int(rng.choice(c))
        diff, day, rec = message_pull_rows(t, ag, V, dd, window_s=1800, placebo=plc)
        # day clusters: recipients on a day share the same sender messages (recipient-day clusters gave 0.12 under
        # the null); few clusters, so the t(D - 1) reference in cluster_boot_test matters
        est, lo, hi, p = cluster_boot_test(diff, day, B=400, rng=rng)
        rows.append({"null": nn, "statistic": "message_pull", "scenario": scen, "rep": rep, "unit": sk.unit_id,
                     "p": p})
    return rows


FAMILIES = {
    "activity": (_act_job, list(ACT_SCENARIOS)),
    "room": (_room_job, ["indep", "global_drive", "room_drive", "power_J0.4"]),
    "event": (_event_job, ["indep", "monday", "power_step"]),
    "lever": (_lever_job, ["indep", "power_h1"]),
    "signed": (_signed_job, ["indep", "sparse", "power_camps"]),
    "pull": (_pull_job, ["indep", "ou_drift", "day_drive", "power_degroot"]),
}

KNOWN = {  # (null, statistic, scenario) -> the documented trap this cell reproduces
    ("block_shift", "cw_gain_raw", "indep"): "H38/H17: whole-day grids include staggered day edges and absent minutes",
    ("circshift", "cw_gain_raw", "indep"): "H38/H17: whole-day grids include staggered day edges and absent minutes",
    ("block_shift", "cw_gain_trim", "day_edge"): "H38: synchronized starts and start-up bursts fake coupling",
    ("block_shift", "cw_gain_trim", "stalls"): "H38/H25: platform stalls fake coupling unless masked",
    ("crossday", "cw_gain_trim", "stalls"): "H38/H25: platform stalls fake coupling unless masked",
    ("circshift", "cw_gain_trim", "slow_field"): "H05/H12: within-day circular shifts misalign shared daily drives",
    ("crossday", "cw_gain_trim", "fast_field"): "H25/H34: a shared field is not coupling; no surrogate removes it",
    ("block_shift", "cw_gain_trim", "fast_field"): "H25/H34: a shared field is not coupling; no surrogate removes it",
    ("crossday", "lambda1_trim", "indep"): "H12: lambda1 over a unit includes the shared real schedule",
    ("room_relabel", "room_excess", "room_drive"): "H26: room-specific drives look like within-room coupling",
    ("placebo_dates_any", "event_step_k1", "monday"): "Monday effect: unmatched placebo dates",
    ("lever_controls_future", "lever_effect", "indep"): "H39: kick-free-future controls manufacture an effect",
    ("lever_controls_past_nopresence", "lever_effect", "indep"): "H17: grid 'idle' before/after the agent's day is absence",
    ("lever_controls_past_cut", "lever_effect", "indep"): "H39: window means cut at the next kick = state-dependent censoring",
    ("fdr_direct", "signed_negpairs", "indep"): "H37: per-pair FDR is anti-conservative under agent fields",
    ("fdr_direct", "signed_negpairs", "sparse"): "H37: per-pair FDR is anti-conservative under agent fields",
    ("sign_shuffle", "signed_faction", "sparse"): "H37: sign-shuffle nulls are anti-conservative (not reproduced here)",
    ("crossday_message_placebo", "message_pull", "day_drive"): "H29: day-level shared drive passes the cross-day placebo",
    ("sameday_message_placebo", "message_pull", "ou_drift"): "H29: recency confound (content similarity decays with age)",
}


def calibrate(reps: int = 100, n_surr: int = 49, workers: int = 2, families=None, seed: int = 20261004,
              write: bool = True):
    import polars as pl
    jobs = []
    rng = np.random.default_rng(seed)
    fams = families or list(FAMILIES)
    for fam in fams:
        fn, scens = FAMILIES[fam]
        for sc in scens:
            nrep = reps if not sc.startswith("power") else max(20, reps // 2)
            for r in range(nrep):
                jobs.append((fam, (sc, r, n_surr, int(rng.integers(1 << 31)))))
    t0 = time.time()
    rows = []
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=min(workers, 2)) as ex:
            futs = [ex.submit(FAMILIES[f][0], a) for f, a in jobs]
            for k, fu in enumerate(futs):
                rows += fu.result()
                if (k + 1) % 100 == 0:
                    print(f"  {k + 1}/{len(futs)} jobs, {time.time() - t0:.0f}s", flush=True)
    else:
        for f, a in jobs:
            rows += FAMILIES[f][0](a)
    df = pl.DataFrame(rows, infer_schema_length=None)
    tab = (df.filter(pl.col("p").is_not_nan() & pl.col("p").is_not_null())
           .group_by("null", "statistic", "scenario")
           .agg(pl.len().alias("reps"), (pl.col("p") <= ALPHA).sum().alias("n_reject")).sort("statistic", "null", "scenario"))
    out = []
    for r in tab.iter_rows(named=True):
        fpr = r["n_reject"] / r["reps"]
        lo, hi = wilson(r["n_reject"], r["reps"])
        band = size_band(r["reps"])
        power = r["scenario"].startswith("power")
        status = ("power" if power else "calibrated" if fpr <= band[1] else "anti-conservative")
        out.append({**r, "rate": fpr, "ci_lo": lo, "ci_hi": hi, "band_hi": band[1], "n_surr": n_surr,
                    "kind": "power" if power else "size", "status": status,
                    "known_trap": KNOWN.get((r["null"], r["statistic"], r["scenario"]))})
    res = pl.DataFrame(out)
    if families and write and (SH / "null_sizes.parquet").exists():   # partial rerun: merge into the existing table
        old = pl.read_parquet(SH / "null_sizes.parquet")
        old = old.filter(~pl.col("statistic").is_in(res["statistic"].unique().implode()))
        res = pl.concat([old, res], how="diagonal_relaxed").sort("statistic", "null", "scenario")
    meta = {"alpha": ALPHA, "reps": reps, "n_surr": n_surr, "seed": seed, "elapsed_s": round(time.time() - t0, 1),
            "units": CAL_UNITS, "families": fams,
            "band_rule": "calibrated if the empirical size <= the 97.5% binomial quantile at nominal alpha for the "
                         "cell's replicates (0.10 at 100 reps); anti-conservative otherwise",
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    if write:
        SIZES_JSON.write_text(json.dumps({"meta": meta, "table": res.to_dicts()}, indent=1, default=float))
        res.write_parquet(SH / "null_sizes.parquet", compression="zstd")
        from common import write_provenance
        write_provenance("null_sizes", ["(simulated on skeletons of) activity_bins_fixed", "states_min", "rooms_timeline",
                                        "kicks_classified", "stall_minutes", "reasons", "embeddings/statements",
                                        "project_states", "call_windows", "chat_core", "calendar", "period_units"],
                         {**meta, "built_by_function": "infra/shared/nulls.py --calibrate"})
        prov = json.loads((SH / "_provenance.json").read_text())
        prov["null_sizes"]["built_by"] = "infra/shared/nulls.py"
        (SH / "_provenance.json").write_text(json.dumps(prov, indent=1))
    return res, meta


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--surr", type=int, default=49)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--families", default="")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    if a.calibrate:
        import polars as pl
        res, meta = calibrate(a.reps, a.surr, a.workers, [f for f in a.families.split(",") if f] or None,
                              write=not a.no_write)
        with pl.Config(tbl_rows=200, tbl_cols=20, tbl_width_chars=250, float_precision=3):
            print(res.select("statistic", "null", "scenario", "reps", "rate", "ci_lo", "ci_hi", "status", "known_trap"))
        print(meta)
