"""H25 distance-to-criticality dial: a per-day, per-channel loop gain g and T/T_c = 1/g from logs.

Self-contained (numpy + polars only, no project imports) so it can run on any multi-agent swarm's logs.

The physics (mean-field Curie-Weiss, physics-models/01-inverse-ising):
    H = -(J0 / 2N) (sum_i s_i)^2 - sum_i h_i(t) s_i
    linear response:      dM = sum_j q_j beta dh_j / (1 - g),   q_j = 1 - m_j^2,  g = beta J0 qbar   (loop gain)
    fluctuation-dissipation: Var(sum_i s_i) = sum_i q_i / (1 - g)  and  sum_i Var(s_i) = sum_i q_i
    =>  VR = Var(sum_i s_i) / sum_i Var(s_i) = 1 / (1 - g),   g = 1 - 1/VR,   T/T_c = 1/g  (h = 0: g = beta J0 = T_c/T)
VR is the observed collective susceptibility over the independent-agent susceptibility: the amplification a push on
one agent gets from the swarm's feedback (1 + g + g^2 + ...). g -> 1 is criticality (runaway cascades, lock-in).
g is exact for equilibrium Curie-Weiss with heterogeneous fields; for kinetic or delayed coupling VR still diverges at
the same instability, but values below 1 map onto the model's coupling through a model-dependent curve (calibrate on
simulations: hypotheses/H25-criticality-dial/analysis/synthetic.py). Equal-time 1-min statistics see only the fast
part of the feedback.

Channels (never pool them; they can move in opposite directions):
    activity  s_i(t) = +1 if agent i did anything in minute t, else -1
    talk      s_i(t) = +1 if agent i posted a message in minute t, else -1
    content   s_i(w) = mean unit statement vector of agent i in window w (mean-field O(n); g = beta J0 / n)

Drives (fields) removed before the ratio is taken:
    binary channels: each agent's mean is removed within 30-min blocks of the day (daily schedule, slow drives);
                     platform stalls (runs in which nobody emits any event, longer than chance) are masked.
    content:         each agent's day mean (all directions: the day's goal field and the agent's own field) and the
                     span of the day's exogenous (operator/human) messages are removed; optional extra directions.
                     Statement-sampling noise is removed from the independent term by a method-of-moments
                     correction (each agent's within-window statement scatter).

Typical use on another swarm (see the __main__ demo at the bottom):
    spins = spins_from_events(events, agent="agent", t="t", is_talk="is_talk", day_start_hour=0, tz="UTC")
    dial  = compute_dial(spins, statements=stmts, statement_vectors=V, exo_statements=ops, exo_vectors=E)
    dial  # one row per (day, channel): g, 90% interval, VR (amplification), T/T_c, null ceiling, alarm band
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import polars as pl

MIN_BLOCK_N = 5      # minutes; blocks with fewer valid minutes are dropped (H02/H19 rule)
MIN_LAST_BLOCK = 10  # a day's last block shorter than this is merged into the previous one (H02/H19 rule)
BANDS = ((1 / 3, "green"), (2 / 3, "amber"), (1.01, "red"))  # by the upper 90% bound of g: amplification < 1.5, < 3, >= 3
# Bootstrap intervals over within-day segments are too narrow at village sample sizes (synthetic z-SD 1.3-1.5 with
# real day lengths and populations; hypotheses/H25-criticality-dial/analysis/synthetic.py). Intervals and SEs are
# widened by this factor, which restores ~90% coverage on simulated Curie-Weiss, fast-Hawkes and O(n) swarms.
# Recalibrate it with synthetic swarms that share your logs' sampling before trusting the intervals elsewhere.
SE_INFLATE = 1.5


# ----------------------------------------------------------------------------- small utilities
def _runs(x: np.ndarray):
    """Start indices and lengths of runs of True in a 1-D boolean array."""
    x = np.asarray(x, bool)
    if not x.any():
        return np.zeros(0, int), np.zeros(0, int)
    d = np.diff(np.r_[0, x.astype(np.int8), 0])
    st, en = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    return st, en - st


def _blocks(minute: np.ndarray, block_min: int) -> np.ndarray:
    blk = (np.asarray(minute) // block_min).astype(np.int64)
    if blk.size and blk.max() > blk.min():
        last = blk.max()
        if (blk == last).sum() < MIN_LAST_BLOCK:
            blk[blk == last] = blk[blk < last].max()
    return blk


def _roll_index(starts: np.ndarray, lens: np.ndarray, n_cols: int, rng: np.random.Generator) -> np.ndarray:
    """Row-index matrix (T x n_cols) that circularly shifts every column independently inside every segment."""
    parts = []
    for a, L in zip(starts, lens):
        r = rng.integers(0, L, size=n_cols)
        parts.append(a + (np.arange(L)[:, None] + r[None, :]) % L)
    return np.concatenate(parts, axis=0)


def band(hi: float) -> str:
    if not np.isfinite(hi):
        return "n/a"
    for thr, name in BANDS:
        if hi < thr:
            return name
    return "red"


# ----------------------------------------------------------------------------- stalls
def find_stalls(any_event: np.ndarray, minute: np.ndarray, rng: np.random.Generator | None = None, n_surr: int = 50,
                q: float = 0.95, min_len: int = 3) -> tuple[np.ndarray, int]:
    """Platform stalls: runs of minutes in which no agent emits any event, longer than chance.

    any_event: T x N bool (agent emitted any event in the minute; include idle/pause events).
    Threshold: the q-quantile of the longest all-silent run in n_surr surrogates in which each agent's own event series
    is circularly shifted over the whole day (keeps each agent's silences, misaligns them). Returns (mask, L*) where
    mask marks stall minutes and runs of length >= L* count as stalls. With rng=None the surrogates are seeded from the
    data itself, so the same day always gets the same threshold (reproducible dials)."""
    A = np.asarray(any_event, bool)
    if rng is None:
        rng = np.random.default_rng(int(A.sum()) * 1000003 + A.shape[0] * 101 + A.shape[1])
    T = A.shape[0]
    if T == 0 or A.shape[1] == 0:
        return np.zeros(T, bool), min_len
    silent = ~A.any(1)
    mx = np.zeros(n_surr)
    for k in range(n_surr):
        idx = _roll_index(np.array([0]), np.array([T]), A.shape[1], rng)
        s = ~A[idx, np.arange(A.shape[1])].any(1)
        _, L = _runs(s)
        mx[k] = L.max() if L.size else 0
    Lstar = int(max(min_len, math.floor(np.quantile(mx, q)) + 1))
    st, L = _runs(silent)
    mask = np.zeros(T, bool)
    for a, l in zip(st, L):
        if l >= Lstar:
            mask[a:a + l] = True
    return mask, Lstar


# ----------------------------------------------------------------------------- binary channels
@dataclass
class BinaryResult:
    VR: float
    g: float
    se: float
    lo: float
    hi: float
    q_bar: float
    null_mean: float
    null_q95: float
    p_null: float
    N: int
    T: int
    n_seg: int


def _suffstats(X: np.ndarray, seg: np.ndarray):
    M = X.sum(1)
    num_t, den_t = M * M, (X * X).sum(1)
    u, inv = np.unique(seg, return_inverse=True)
    return np.bincount(inv, num_t, len(u)), np.bincount(inv, den_t, len(u)), inv


def binary_day(S: np.ndarray, minute: np.ndarray, valid: np.ndarray | None = None, center: np.ndarray | None = None,
               block_min: int = 30, seg_min: int = 10, n_boot: int = 300, n_null: int = 100,
               rng: np.random.Generator | None = None, inflate: float = SE_INFLATE) -> BinaryResult | None:
    """Equal-time Curie-Weiss loop gain for one day of +-1 spins.

    S: T x N (+1/-1), minute: T minute-of-day indices (sorted), valid: T bool (False = masked, e.g. stalls).
    center: optional T x N expected spins (e.g. a cross-fitted time-of-day profile); if None, each agent's mean is
    removed within block_min blocks (H02/H19 convention). Error bars: bootstrap over seg_min segments (sums of squared
    block-centered deviations are additive over segments), widened by `inflate` (see SE_INFLATE). Null: each agent
    circularly shifted within each block."""
    rng = rng or np.random.default_rng(0)
    S = np.asarray(S, float)
    minute = np.asarray(minute)
    if valid is not None:
        S, minute = S[valid], minute[valid]
        if center is not None:
            center = np.asarray(center, float)[valid]
    T, N = S.shape
    if N < 2 or T < 2 * MIN_BLOCK_N:
        return None
    blk = _blocks(minute, block_min)
    ub, cnt = np.unique(blk, return_counts=True)
    okb = np.isin(blk, ub[cnt >= MIN_BLOCK_N])
    S, minute, blk = S[okb], minute[okb], blk[okb]
    if center is not None:
        center = center[okb]
    if S.shape[0] < 2 * MIN_BLOCK_N:
        return None
    order = np.lexsort((minute, blk))
    S, minute, blk = S[order], minute[order], blk[order]
    ub, starts, lens = np.unique(blk, return_index=True, return_counts=True)
    if center is None:
        inv = np.repeat(np.arange(len(ub)), lens)
        sums = np.zeros((len(ub), N))
        np.add.at(sums, inv, S)
        X = S - (sums / lens[:, None])[inv]
    else:
        X = S - center[order]
    var_i = (X * X).mean(0)
    keep = var_i > 1e-12
    X = X[:, keep]
    if X.shape[1] < 2:
        return None
    seg = blk * 100000 + minute // seg_min
    num, den, _ = _suffstats(X, seg)
    VR = num.sum() / den.sum()
    g = 1 - 1 / VR
    nseg = len(num)
    idx = rng.integers(0, nseg, size=(n_boot, nseg))
    gb = 1 - den[idx].sum(1) / num[idx].sum(1)
    q05, q95 = np.quantile(gb, [0.05, 0.95])
    lo, hi = g - inflate * (g - q05), min(1.0, g + inflate * (q95 - g))
    gn = np.empty(n_null)
    for k in range(n_null):
        ridx = _roll_index(starts, lens, X.shape[1], rng)
        Xs = X[ridx, np.arange(X.shape[1])]
        M = Xs.sum(1)
        gn[k] = 1 - den.sum() / (M * M).sum()
    # q_bar: mean single-spin variance (H02's q) within blocks, for beta*J0 = g / q_bar
    return BinaryResult(VR=float(VR), g=float(g), se=float(inflate * gb.std(ddof=1)), lo=float(lo), hi=float(hi),
                        q_bar=float(var_i[keep].mean()), null_mean=float(gn.mean()), null_q95=float(np.quantile(gn, 0.95)),
                        p_null=float((1 + (gn >= g).sum()) / (1 + n_null)), N=int(X.shape[1]), T=int(X.shape[0]), n_seg=int(nseg))


# ----------------------------------------------------------------------------- content channel (mean-field O(n))
@dataclass
class ContentResult:
    VR: float
    g: float
    se: float
    lo: float
    hi: float
    null_mean: float
    null_q95: float
    p_null: float
    N: int
    W: int
    n_stmt: int
    k_removed: int


def _orth_basis(dirs: list[np.ndarray], d: int, tol: float = 1e-6) -> np.ndarray:
    D = [np.atleast_2d(x) for x in dirs if x is not None and np.size(x)]
    if not D:
        return np.zeros((d, 0))
    D = np.vstack(D).T  # d x k
    U, s, _ = np.linalg.svd(D, full_matrices=False)
    return U[:, s > tol * max(1.0, s.max())]


def exo_directions(E: np.ndarray | None, k: int = 5) -> np.ndarray | None:
    """Leading directions (k x d) spanned by a day's exogenous message vectors (uncentered SVD)."""
    if E is None or len(E) == 0:
        return None
    E = np.asarray(E, float)
    _, s, Vt = np.linalg.svd(E, full_matrices=False)
    return Vt[:min(k, (s > 1e-8).sum())]


VR_FLOOR = 0.05  # VR <= 0 (noise) is floored, not dropped: dropping would select days with positive g


def _pair_vr(G, C, Tn, sig):
    """VR = 1 + (N-1) * mean_pairs(c_ij) / mean_pairs((sig_i + sig_j)/2), pairwise-complete over windows.

    G: N x N sums over shared windows of <r_i, r_j>; C: shared window counts; Tn: windows per agent; sig: each agent's
    noise-corrected signal variance (sum over dims). c_ij is corrected for centering on different window sets:
    E[(x_w - xbar_A)(y_w - ybar_B)] = cov (1 - 1/a - 1/b + c/(ab))."""
    N = len(Tn)
    a, b = Tn[:, None].astype(float), Tn[None, :].astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        k = 1 - 1 / a - 1 / b + C / (a * b)
        cij = G / (C * k)
    ok = (C >= 2) & np.isfinite(cij) & ~np.eye(N, dtype=bool) & np.isfinite(sig)[:, None] & np.isfinite(sig)[None, :]
    if ok.sum() == 0:
        return np.nan, np.nan
    sp = 0.5 * (sig[:, None] + sig[None, :])
    den = sp[ok].mean()
    if not den > 0:
        return np.nan, np.nan
    rho = cij[ok].mean() / den
    return max(VR_FLOOR, 1 + (N - 1) * rho), rho


def content_day(U: np.ndarray, agent: np.ndarray, window: np.ndarray, remove_dirs: np.ndarray | None = None,
                n_boot: int = 300, n_null: int = 100, min_windows: int = 3, method: str = "moment",
                rng: np.random.Generator | None = None, inflate: float = SE_INFLATE) -> ContentResult | None:
    """Mean-field O(n) loop gain for one day of statement vectors.

    U: n_stmt x d unit statement vectors (centered/whitened upstream), in time order; agent, window: per-statement ids.
    remove_dirs: k x d directions projected out first (exogenous field, cross-fitted habitual directions).
    Each agent's day mean is removed in all directions (constant fields of any dimension). The independent-agent term
    is corrected for statement-sampling noise, which would otherwise dilute g:
      method="moment" (default): signal_i = Var_w(window mean) - nu_i * mean_w(1/k_iw), with nu_i the agent's pooled
                                 within-window statement scatter (method of moments; uses every statement);
      method="split":            signal_i = covariance between odd- and even-statement half means (H01's P9 device;
                                 noisier, kept for comparison)."""
    rng = rng or np.random.default_rng(0)
    U = np.asarray(U, float)
    d = U.shape[1]
    k_removed = 0
    if remove_dirs is not None and np.size(remove_dirs):
        Q = _orth_basis([remove_dirs], d)
        k_removed = Q.shape[1]
        U = U - (U @ Q) @ Q.T
    ag_u, ag = np.unique(agent, return_inverse=True)
    w_u, w = np.unique(window, return_inverse=True)
    N, W = len(ag_u), len(w_u)
    if W < 3:
        return None
    cell = ag * W + w
    rank = np.zeros(len(cell), int)
    seen: dict[int, int] = {}
    for t, c in enumerate(cell):
        rank[t] = seen.get(c, 0)
        seen[c] = rank[t] + 1
    K = np.bincount(cell, minlength=N * W).reshape(N, W).astype(float)
    S = np.zeros((N * W, d)); np.add.at(S, cell, U); S = S.reshape(N, W, d)
    SS = np.bincount(cell, (U * U).sum(1), minlength=N * W).reshape(N, W)
    ev = rank % 2 == 0
    KA = np.bincount(cell[ev], minlength=N * W).reshape(N, W).astype(float)
    KB = np.bincount(cell[~ev], minlength=N * W).reshape(N, W).astype(float)
    SA = np.zeros((N * W, d)); np.add.at(SA, cell[ev], U[ev]); SA = SA.reshape(N, W, d)
    SB = np.zeros((N * W, d)); np.add.at(SB, cell[~ev], U[~ev]); SB = SB.reshape(N, W, d)
    keep = ((K >= 1).sum(1) >= min_windows) & ((K >= 2).sum(1) >= 1)
    if keep.sum() < 3:
        return None
    K, S, SS, KA, KB, SA, SB = (x[keep] for x in (K, S, SS, KA, KB, SA, SB))
    N = int(keep.sum())

    def stats(Kx, Sx, SSx, KAx, KBx, SAx, SBx):
        h = Kx >= 1
        Tn = h.sum(1).astype(float)
        okA = Tn >= 2
        if okA.sum() < 3:
            return np.nan
        if not okA.all():
            Kx, Sx, SSx, KAx, KBx, SAx, SBx, h, Tn = (x[okA] for x in (Kx, Sx, SSx, KAx, KBx, SAx, SBx, h, Tn))
        V = np.where(h[..., None], Sx / np.maximum(Kx, 1)[..., None], 0.0)
        mu = V.sum(1) / Tn[:, None]
        R = np.where(h[..., None], V - mu[:, None], 0.0)
        G = np.einsum("iwd,jwd->ij", R, R)
        Cn = h.astype(float) @ h.T.astype(float)
        if method == "split":
            h2 = (KAx >= 1) & (KBx >= 1)
            T2 = h2.sum(1).astype(float)
            A = np.where(h2[..., None], SAx / np.maximum(KAx, 1)[..., None], 0.0)
            B = np.where(h2[..., None], SBx / np.maximum(KBx, 1)[..., None], 0.0)
            with np.errstate(divide="ignore", invalid="ignore"):
                muA = A.sum(1) / T2[:, None]; muB = B.sum(1) / T2[:, None]
            RA = np.where(h2[..., None], A - muA[:, None], 0.0); RB = np.where(h2[..., None], B - muB[:, None], 0.0)
            sig = np.where(T2 >= 2, np.einsum("iwd,iwd->i", RA, RB) / np.maximum(T2 - 1, 1), np.nan)
        else:
            tv = np.einsum("iwd,iwd->i", R, R) / (Tn - 1)
            scat = SSx - Kx * np.einsum("iwd,iwd->iw", V, V)      # within-window statement scatter
            dof = np.where(Kx >= 2, Kx - 1, 0).sum(1)
            pooled = scat[Kx >= 2].sum() / max(np.where(Kx >= 2, Kx - 1, 0).sum(), 1)
            nu = np.where(dof > 0, np.where(Kx >= 2, scat, 0).sum(1) / np.maximum(dof, 1), pooled)
            inv_k = np.where(h, 1 / np.maximum(Kx, 1), 0).sum(1) / Tn
            sig = tv - nu * inv_k
        vr, _ = _pair_vr(G, Cn, Tn, sig)
        return vr

    base = (K, S, SS, KA, KB, SA, SB)
    VR = stats(*base)
    if not np.isfinite(VR):
        return None
    g = 1 - 1 / VR
    gb = []
    for _ in range(n_boot):
        idx = rng.integers(0, W, size=W)
        v = stats(*(x[:, idx] for x in base))
        if np.isfinite(v):
            gb.append(1 - 1 / v)
    gb = np.array(gb) if gb else np.array([np.nan])
    gn = []
    rows = np.arange(N)[:, None]
    for _ in range(n_null):  # null: each agent's window sequence circularly shifted (breaks cross-agent alignment)
        ix = (np.arange(W)[None, :] + rng.integers(0, W, size=N)[:, None]) % W
        v = stats(*(x[rows, ix] for x in base))
        if np.isfinite(v):
            gn.append(1 - 1 / v)
    gn = np.array(gn) if gn else np.array([np.nan])
    good = np.isfinite(gb)
    q05, q95 = (np.quantile(gb[good], [0.05, 0.95]) if good.sum() > 10 else (np.nan, np.nan))
    lo, hi = g - inflate * (g - q05), min(1.0, g + inflate * (q95 - g))
    return ContentResult(VR=float(VR), g=float(g), se=float(inflate * np.std(gb[good], ddof=1)) if good.sum() > 2 else np.nan,
                         lo=float(lo), hi=float(hi), null_mean=float(np.nanmean(gn)), null_q95=float(np.nanquantile(gn, 0.95)),
                         p_null=float((1 + (gn >= g).sum()) / (1 + len(gn))), N=N, W=int(W), n_stmt=int(K.sum()),
                         k_removed=int(k_removed))


# ----------------------------------------------------------------------------- multi-scale diagnostic
def vr_scale(S: np.ndarray, minute: np.ndarray, valid: np.ndarray | None = None, delta: int = 5, block_min: int = 60):
    """Coarse-grained variance ratio: spins averaged over delta-minute windows, centered within block_min blocks.

    Returns (g_short, g_long): 1 - 1/VR and 1 - 1/sqrt(VR). For linear (AR or Hawkes) dynamics the long-window
    count VR tends to 1/(1 - g_DC)^2, so g_long estimates the DC loop gain when delta >> coupling delays; at
    delta = 1 min g_short is the equal-time dial. A diagnostic for delayed coupling, not a dial (few samples/day)."""
    S = np.asarray(S, float); minute = np.asarray(minute)
    if valid is not None:
        S, minute = S[valid], minute[valid]
    key = minute // delta
    u, inv = np.unique(key, return_inverse=True)
    cnt = np.bincount(inv)
    Xc = np.zeros((len(u), S.shape[1])); np.add.at(Xc, inv, S)
    full = cnt >= max(1, int(0.8 * delta))
    Xc, u = Xc[full] / cnt[full][:, None], u[full]
    blk = (u * delta) // block_min
    num = den = 0.0
    for b in np.unique(blk):
        X = Xc[blk == b]
        if len(X) < 3:
            continue
        X = X - X.mean(0)
        num += (X.sum(1) ** 2).sum(); den += (X * X).sum()
    if den <= 0:
        return np.nan, np.nan
    VR = num / den
    return 1 - 1 / VR, (1 - 1 / np.sqrt(VR)) if VR > 0 else np.nan


# ----------------------------------------------------------------------------- inputs from raw logs
def spins_from_events(events: pl.DataFrame, agent: str = "agent", t: str = "t", is_talk: str | None = "is_talk",
                      day_start_hour: int = 0, tz: str = "UTC", bin_s: int = 60, day: str | None = None) -> pl.DataFrame:
    """Turn an event log into minute spins.

    events: one row per agent event with columns agent, t (datetime), is_talk (bool; message posted). Each day's grid
    runs from its first to its last event; every agent seen that day gets a row per minute.
    Returns day, minute, agent, active, talk, any_event (active = any event; supply idle/heartbeat events as non-talk
    events if the platform logs them: they make the stall detector specific)."""
    e = events.with_columns(pl.col(t).dt.convert_time_zone(tz).alias("_tl"))
    if day is None:
        e = e.with_columns((pl.col("_tl") - pl.duration(hours=day_start_hour)).dt.date().cast(pl.String).alias("day"))
    else:
        e = e.rename({day: "day"})
    first = e.group_by("day").agg(pl.col(t).min().alias("_t0"), pl.col(t).max().alias("_t1"))
    e = e.join(first, on="day").with_columns(((pl.col(t) - pl.col("_t0")).dt.total_seconds() // bin_s).cast(pl.Int32).alias("minute"))
    talk_expr = pl.col(is_talk).cast(pl.Boolean) if is_talk else pl.lit(False)
    ev = e.group_by("day", "minute", agent).agg(talk_expr.any().alias("talk"), pl.len().alias("_n"))
    grid = (first.with_columns(pl.int_ranges(0, ((pl.col("_t1") - pl.col("_t0")).dt.total_seconds() // bin_s + 1).cast(pl.Int32)).alias("minute"))
            .explode("minute").select("day", "minute"))
    ags = e.select("day", agent).unique()
    out = (grid.join(ags, on="day").join(ev, on=["day", "minute", agent], how="left")
           .with_columns(pl.col("_n").is_not_null().alias("active"), pl.col("talk").fill_null(False))
           .with_columns(pl.col("active").alias("any_event")).drop("_n").rename({agent: "agent"}))
    return out.sort("day", "minute", "agent")


def fit_whitener(V: np.ndarray, dim: int = 32):
    """Center, PCA-whiten to `dim` dimensions and re-normalize statement vectors (embedding anisotropy, model 11).
    Fit on a training slice of the logs; returns a function mapping raw vectors to unit vectors."""
    V = np.asarray(V, float)
    mu = V.mean(0)
    _, s, Vt = np.linalg.svd(V - mu, full_matrices=False)
    U, w = Vt[:dim].T, (s[:dim] ** 2) / len(V)

    def W(x):
        z = ((np.asarray(x, float) - mu) @ U) / np.sqrt(w)
        return z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-12)
    return W


# ----------------------------------------------------------------------------- the dial
def compute_dial(minute_spins: pl.DataFrame | None, statements: pl.DataFrame | None = None,
                 statement_vectors: np.ndarray | None = None, exo_statements: pl.DataFrame | None = None,
                 exo_vectors: np.ndarray | None = None, channels=("activity", "talk", "content"),
                 stall: str = "auto", external_mask: pl.DataFrame | None = None, block_min: int = 30, seg_min: int = 10,
                 content_win_min: int = 30, n_exo_dirs: int = 5, extra_dirs: dict | None = None,
                 min_agents: int = 3, min_active_min: int = 10, min_talk_min: int = 5,
                 n_boot: int = 300, n_null: int = 100, seed: int = 0) -> pl.DataFrame:
    """Daily distance-to-criticality dial, one row per (day, channel).

    minute_spins: columns day, minute (int, minutes since the day's start), agent, active (bool), talk (bool) and
        optionally any_event (bool; any logged event incl. idle/heartbeats; defaults to active). One row per agent and
        minute of the day's grid (spins_from_events builds it).
    statements: columns day, minute (float), agent; row-aligned with statement_vectors (n x d, already centered and
        whitened, e.g. with fit_whitener; each row is re-normalized here). Optional `window` column overrides
        minute // content_win_min.
    exo_statements / exo_vectors: the same for exogenous messages (operator, humans, bots); their span per day is the
        time-varying field projected out of the content channel (at most n_exo_dirs directions).
    stall: "auto" (null-calibrated platform stalls masked), "none", "lull" (drop minutes with <= 1 active agent;
        biased, see synthetic validation), or "external" (use external_mask: columns day, minute, masked).
    extra_dirs: optional {day: k x d array} of further directions to remove from content (e.g. cross-fitted).
    Returns columns: day, channel, N, T, stall_min, VR, g, se, lo, hi (90%), null_mean, null_q95, p_null, q_bar,
        bJ0, amp (= VR), T_over_Tc (= 1/g), T_over_Tc_lo, T_over_Tc_hi, band (green/amber/red by the upper bound), flag.
    """
    rng = np.random.default_rng(seed)
    rows = []
    days = []
    if minute_spins is not None:
        days = sorted(minute_spins["day"].unique().to_list())
    if statements is not None:
        days = sorted(set(days) | set(statements["day"].unique().to_list()))
    for dday in days:
        stall_min, Lstar = 0, None
        if minute_spins is not None and {"activity", "talk"} & set(channels):
            d = minute_spins.filter(pl.col("day") == dday)
            if "any_event" not in d.columns:
                d = d.with_columns(pl.col("active").alias("any_event"))
            if d.height:
                minutes = np.sort(d["minute"].unique().to_numpy())
                agents_all = sorted(d["agent"].unique().to_list())
                piv = {c: d.pivot(on="agent", index="minute", values=c).sort("minute") for c in ("active", "talk", "any_event")}
                A = {c: piv[c].select([str(a) if str(a) in piv[c].columns else a for a in agents_all]).fill_null(False).to_numpy().astype(bool)
                     for c in piv}
                mnt = piv["active"]["minute"].to_numpy()
                nact, ntalk = A["active"].sum(0), A["talk"].sum(0)
                valid = np.ones(len(mnt), bool)
                if stall == "auto":
                    popm = nact >= min_active_min
                    m, Lstar = find_stalls(A["any_event"][:, popm], mnt)
                    valid &= ~m
                elif stall == "lull":
                    valid &= A["active"][:, nact >= min_active_min].sum(1) >= 2
                elif stall == "external" and external_mask is not None:
                    em = external_mask.filter((pl.col("day") == dday) & pl.col("masked"))["minute"].to_numpy()
                    valid &= ~np.isin(mnt, em)
                stall_min = int((~valid).sum())
                for ch, col, thr in (("activity", "active", min_active_min), ("talk", "talk", min_talk_min)):
                    if ch not in channels:
                        continue
                    pop = (nact if ch == "activity" else ntalk) >= thr
                    base = {"day": dday, "channel": ch, "N": int(pop.sum()), "T": int(valid.sum()), "stall_min": stall_min,
                            "stall_Lstar": Lstar}
                    if pop.sum() < min_agents:
                        rows.append({**base, "flag": "too_few_agents"}); continue
                    S = np.where(A[col][:, pop], 1.0, -1.0)
                    r = binary_day(S, mnt, valid=valid, block_min=block_min, seg_min=seg_min, n_boot=n_boot,
                                   n_null=n_null, rng=rng)
                    if r is None:
                        rows.append({**base, "flag": "too_short"}); continue
                    rows.append({**base, "N": r.N, "T": r.T, "VR": r.VR, "g": r.g, "se": r.se, "lo": r.lo, "hi": r.hi,
                                 "null_mean": r.null_mean, "null_q95": r.null_q95, "p_null": r.p_null, "q_bar": r.q_bar,
                                 "bJ0": r.g / r.q_bar if r.q_bar > 0 else np.nan, "flag": "ok"})
        if statements is not None and statement_vectors is not None and "content" in channels:
            sel = (statements["day"] == dday).to_numpy()
            base = {"day": dday, "channel": "content", "stall_min": stall_min}
            if sel.sum() < 6:
                rows.append({**base, "flag": "too_few_statements"}); continue
            st = statements.filter(pl.col("day") == dday).with_row_index("_r")
            V = np.asarray(statement_vectors, float)[sel]
            V = V / np.maximum(np.linalg.norm(V, axis=1, keepdims=True), 1e-12)
            win = st["window"].to_numpy() if "window" in st.columns else (st["minute"].to_numpy() // content_win_min).astype(int)
            order = np.lexsort((st["minute"].to_numpy(), win, st["agent"].to_numpy()))
            dirs = []
            if exo_statements is not None and exo_vectors is not None:
                es = (exo_statements["day"] == dday).to_numpy()
                if es.any():
                    dirs.append(exo_directions(np.asarray(exo_vectors, float)[es], n_exo_dirs))
            if extra_dirs and dday in extra_dirs:
                dirs.append(extra_dirs[dday])
            dirs = [x for x in dirs if x is not None and np.size(x)]
            rd = np.vstack(dirs) if dirs else None
            r = content_day(V[order], st["agent"].to_numpy()[order], win[order], remove_dirs=rd, n_boot=n_boot,
                            n_null=n_null, rng=rng)
            if r is None:
                rows.append({**base, "flag": "too_few_agents"}); continue
            rows.append({**base, "N": r.N, "T": r.W, "VR": r.VR, "g": r.g, "se": r.se, "lo": r.lo, "hi": r.hi,
                         "null_mean": r.null_mean, "null_q95": r.null_q95, "p_null": r.p_null, "n_stmt": r.n_stmt,
                         "k_removed": r.k_removed, "flag": "ok"})
    out = pl.DataFrame(rows, infer_schema_length=None)
    if "g" not in out.columns:
        return out
    out = out.with_columns(
        pl.col("VR").alias("amp"),
        pl.when(pl.col("g") > 0).then(1 / pl.col("g")).otherwise(float("inf")).alias("T_over_Tc"),
        pl.when(pl.col("hi") > 0).then(1 / pl.col("hi")).otherwise(float("inf")).alias("T_over_Tc_lo"),
        pl.when(pl.col("lo") > 0).then(1 / pl.col("lo")).otherwise(float("inf")).alias("T_over_Tc_hi"),
        pl.col("hi").map_elements(band, return_dtype=pl.String).alias("band"))
    return out


# ----------------------------------------------------------------------------- period aggregation
def aggregate_days(g: np.ndarray, se: np.ndarray) -> dict:
    """Fixed-effect and DerSimonian-Laird random-effects mean of daily dials; Cochran's Q, I^2, p."""
    from scipy import stats
    g, se = np.asarray(g, float), np.asarray(se, float)
    ok = np.isfinite(g) & np.isfinite(se) & (se > 0)
    g, se = g[ok], se[ok]
    k = len(g)
    if k == 0:
        return {"k": 0}
    w = 1 / se ** 2
    fe = float((w * g).sum() / w.sum())
    se_fe = float(np.sqrt(1 / w.sum()))
    if k == 1:
        return {"k": 1, "fe": fe, "se_fe": se_fe, "re": fe, "se_re": se_fe, "tau2": 0.0, "Q": 0.0, "p_Q": np.nan, "I2": 0.0}
    Q = float((w * (g - fe) ** 2).sum())
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (k - 1)) / c)
    wr = 1 / (se ** 2 + tau2)
    re = float((wr * g).sum() / wr.sum())
    return {"k": k, "fe": fe, "se_fe": se_fe, "re": re, "se_re": float(np.sqrt(1 / wr.sum())), "tau2": float(tau2),
            "Q": Q, "p_Q": float(stats.chi2.sf(Q, k - 1)), "I2": float(max(0.0, (Q - (k - 1)) / Q)) if Q > 0 else 0.0,
            "median": float(np.median(g))}


# ----------------------------------------------------------------------------- demo
if __name__ == "__main__":
    # A toy swarm: 8 agents, 3 days of 4 h, mean-field coupled activity (Gibbs sampling of Curie-Weiss per minute).
    rng = np.random.default_rng(1)
    N, Tm, bJ = 8, 240, 0.5
    rows = []
    for dd in range(3):
        s = rng.choice([-1, 1], N)
        for t in range(Tm):
            h = -0.3 + 0.4 * np.sin(2 * np.pi * t / Tm)  # daily schedule
            for _ in range(2):
                for i in range(N):
                    loc = h + bJ * (s.sum() - s[i]) / N
                    s[i] = 1 if rng.random() < 1 / (1 + np.exp(-2 * loc)) else -1
            for i in range(N):
                rows.append({"day": f"d{dd}", "minute": t, "agent": i, "active": bool(s[i] > 0),
                             "talk": bool(s[i] > 0 and rng.random() < 0.2)})
    spins = pl.DataFrame(rows)
    print(compute_dial(spins, channels=("activity",), stall="none", n_boot=200, n_null=50)
          .select("day", "channel", "N", "T", "g", "lo", "hi", "null_q95", "T_over_Tc", "band"))
