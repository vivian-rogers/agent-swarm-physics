"""H50 estimator library: transfer functions (Part A), hop-indexed responses (Part B), and the
field/coupling decomposition (Part C: C1 minute-grid co-movement, C2 read-out gate).

The same functions run on synthetic worlds (analysis/synthetic.py) and on real units (scheme/build.py output),
so every real-data number has a synthetic recovery check.

A "unit" is a dict of numpy arrays (times in seconds since BASE, float64):
  name, regime
  day_t0[D], day_t1[D]      grid start / end per day (calendar window -15 min / +5 min)
  N                          number of agents (internal indices 0..N-1); agent_codes[N] optional
  calls: agent, day, tc, tl, talk, act, first, low       (sorted by agent, then tc; summary calls removed)
  msgs:  t, day, sender, room                            peer agent chat messages
  mpairs: msg, rec, (optional) ment                      (message, recipient) visibility pairs (who could read it)
  inputs: t, day, kind, (targets as list)                exogenous inputs; kind codes in KINDS
  ipairs: inp, rec, tgt                                  (input, recipient, recipient is a named target)
  plat:  t, day, agent                                   platform (infrastructure-error) onsets
"""
from __future__ import annotations

import numpy as np

KINDS = ["resume", "pause", "edge", "human", "nudge"]   # exogenous message-like inputs (edge = day start without a bookend)
K = {k: i for i, k in enumerate(KINDS)}
SWARM_CLASSES = ["edge_on", "pause", "human", "nudge", "platform"]  # Part A classes (edge_on = resume or day start)
AGENT_CLASSES = ["edge_on", "pause", "human_me", "human_other", "nudge_me", "nudge_by", "plat_own", "plat_swarm"]
KEYMUL = 1.0e8      # composite key agent*KEYMUL + t (t < 1e8 s since BASE)
LAGS = np.arange(-10, 61)          # Part A FIR lags (minutes)
HOPS = np.arange(-5, 11)           # Part B hops


# ============================================================================ grid
def make_grid(U):
    """Per day: activity A[N,M], talk T[N,M] (call logged in minute), span mask S[N,M] (first..last call), present[N]."""
    c = U["calls"]
    out = []
    for d in range(len(U["day_t0"])):
        t0, t1 = U["day_t0"][d], U["day_t1"][d]
        M = int(np.ceil((t1 - t0) / 60.0))
        A = np.zeros((U["N"], M), np.float32)
        T = np.zeros((U["N"], M), np.float32)
        S = np.zeros((U["N"], M), bool)
        sel = c["day"] == d
        ag, tl, tc = c["agent"][sel], c["tl"][sel], c["tc"][sel]
        m = np.clip(((tl - t0) // 60).astype(int), 0, M - 1)
        a = c["act"][sel]
        A[ag[a], m[a]] = 1
        tk = c["talk"][sel]
        T[ag[tk], m[tk]] = 1
        present = np.zeros(U["N"], bool)
        for i in np.unique(ag):
            mi = np.clip(((tc[ag == i] - t0) // 60).astype(int), 0, M - 1)
            ml = m[ag == i]
            lo, hi = min(mi.min(), ml.min()), max(mi.max(), ml.max())
            S[i, lo:hi + 1] = True
            present[i] = True
        out.append(dict(A=A, T=T, S=S, present=present, M=M, t0=t0))
    return out


def minute_counts(t, day, d, t0, M, weights=None):
    sel = day == d
    m = ((t[sel] - t0) // 60).astype(int)
    ok = (m >= 0) & (m < M)
    x = np.zeros(M, np.float32)
    np.add.at(x, m[ok], 1.0 if weights is None else weights[sel][ok])
    return x


def swarm_inputs(U, grid):
    """Part A input series per day: [len(SWARM_CLASSES), M] counts per minute (posting time)."""
    inp, pl = U["inputs"], U["plat"]
    res = []
    for d, g in enumerate(grid):
        M, t0 = g["M"], g["t0"]
        X = np.zeros((len(SWARM_CLASSES), M), np.float32)
        for kname, ci in (("resume", 0), ("edge", 0), ("pause", 1), ("human", 2), ("nudge", 3)):
            sel = inp["kind"] == K[kname]
            X[ci] += minute_counts(inp["t"][sel], inp["day"][sel], d, t0, M)
        X[4] = minute_counts(pl["t"], pl["day"], d, t0, M)
        res.append(X)
    return res


def agent_inputs(U, grid):
    """C1 exposures per day: [len(AGENT_CLASSES), N, M]."""
    inp, ip, pl = U["inputs"], U["ipairs"], U["plat"]
    res = []
    kind_p = inp["kind"][ip["inp"]]
    t_p = inp["t"][ip["inp"]]
    d_p = inp["day"][ip["inp"]]
    for d, g in enumerate(grid):
        M, t0, N = g["M"], g["t0"], U["N"]
        X = np.zeros((len(AGENT_CLASSES), N, M), np.float32)
        # broadcast inputs (edges, pause): everyone present that day
        for kname, ci in (("resume", 0), ("edge", 0), ("pause", 1)):
            sel = inp["kind"] == K[kname]
            x = minute_counts(inp["t"][sel], inp["day"][sel], d, t0, M)
            X[ci] += x[None, :]
        sd = d_p == d
        m = ((t_p[sd] - t0) // 60).astype(int)
        ok = (m >= 0) & (m < M)
        rec, tgt, kd = ip["rec"][sd][ok], ip["tgt"][sd][ok], kind_p[sd][ok]
        m = m[ok]
        for kname, c_me, c_other in (("human", 2, 3), ("nudge", 4, 5)):
            s1 = (kd == K[kname]) & tgt
            np.add.at(X[c_me], (rec[s1], m[s1]), 1.0)
            s2 = (kd == K[kname]) & ~tgt
            np.add.at(X[c_other], (rec[s2], m[s2]), 1.0)
        sd = pl["day"] == d
        m = ((pl["t"][sd] - t0) // 60).astype(int)
        ok = (m >= 0) & (m < M)
        np.add.at(X[6], (pl["agent"][sd][ok], m[ok]), 1.0)
        tot = X[6].sum(0)
        X[7] = tot[None, :] - X[6]
        res.append(X)
    return res


def peer_series(U, grid):
    """Per day [N, M]: chat messages by others that agent i could read (posting minute)."""
    ms, mp = U["msgs"], U["mpairs"]
    res = []
    t_p, d_p = ms["t"][mp["msg"]], ms["day"][mp["msg"]]
    for d, g in enumerate(grid):
        M, t0 = g["M"], g["t0"]
        X = np.zeros((U["N"], M), np.float32)
        sd = d_p == d
        m = ((t_p[sd] - t0) // 60).astype(int)
        ok = (m >= 0) & (m < M)
        np.add.at(X, (mp["rec"][sd][ok], m[ok]), 1.0)
        res.append(X)
    return res


# ============================================================================ Part A: swarm FIR
def _lagmat(x, lags):
    """x [M] -> [M, len(lags)] with column k = x[m - lag]."""
    M = len(x)
    out = np.zeros((M, len(lags)), np.float64)
    for j, L in enumerate(lags):
        if L >= 0:
            out[L:, j] = x[:M - L] if L < M else 0
        else:
            out[:M + L, j] = x[-L:]
    return out


def swarm_output(grid, which="A"):
    ys = []
    for g in grid:
        n = max(g["present"].sum(), 1)
        ys.append(g[which].sum(0) / n)
    return ys


def fir_stats(ys, Xs, lags=LAGS):
    """Per-day sufficient statistics (within-day demeaned) for the joint FIR."""
    st = []
    for y, X in zip(ys, Xs):
        if len(y) < 30:
            st.append(None)
            continue
        Z = np.hstack([_lagmat(X[c], lags) for c in range(X.shape[0])])
        Z = Z - Z.mean(0, keepdims=True)
        yy = (y - y.mean()).astype(np.float64)
        st.append((Z.T @ Z, Z.T @ yy, float(yy @ yy), Z, yy))
    return st


def smooth_penalty(nc, nl, ridge=1e-3):
    D = np.diff(np.eye(nl), 2, axis=0)
    P1 = D.T @ D + ridge * np.eye(nl)
    return np.kron(np.eye(nc), P1)


def fir_fit(st, nc, lags=LAGS, lams=(0.1, 1, 10, 100, 1000), w=None):
    """Joint ridge FIR with second-difference penalty; lambda by leave-one-day-out CV. Returns g[nc, nl], lam."""
    nl = len(lags)
    P = smooth_penalty(nc, nl)
    days = [i for i, s in enumerate(st) if s is not None]
    if w is None:
        w = np.ones(len(st))
    XtX = sum(w[i] * st[i][0] for i in days)
    Xty = sum(w[i] * st[i][1] for i in days)
    best, blam = np.inf, lams[0]
    if len(days) >= 3 and len(lams) > 1:
        for lam in lams:
            err = 0.0
            for i in days:
                b = np.linalg.solve(XtX - st[i][0] + lam * P, Xty - st[i][1])
                r = st[i][4] - st[i][3] @ b
                err += r @ r
            if err < best:
                best, blam = err, lam
    b = np.linalg.solve(XtX + blam * P, Xty)
    return b.reshape(nc, nl), blam


def fir_boot(st, nc, lam, nboot=200, seed=0, lags=LAGS):
    rng = np.random.default_rng(seed)
    days = np.array([i for i, s in enumerate(st) if s is not None])
    nl = len(lags)
    P = smooth_penalty(nc, nl)
    out = []
    for _ in range(nboot):
        w = np.bincount(rng.choice(days, len(days)), minlength=len(st)).astype(float)
        XtX = sum(w[i] * st[i][0] for i in days if w[i] > 0)
        Xty = sum(w[i] * st[i][1] for i in days if w[i] > 0)
        out.append(np.linalg.solve(XtX + lam * P, Xty).reshape(nc, nl))
    return np.array(out)


def kernel_metrics(g, lags=LAGS, w_read_min=None):
    """Dead time, gain, decay, corner frequency, pre-trend and ringing of one FIR kernel g[lags]."""
    g = np.asarray(g, float)
    pos = lags >= 0
    gp = g[pos]
    cum = np.cumsum(gp)
    c30 = cum[:31]
    iext = int(np.argmax(np.abs(c30)))
    ext = c30[iext]
    sgn = np.sign(ext) if ext != 0 else 1.0
    dead = int(np.argmax(sgn * c30 >= 0.1 * abs(ext))) if abs(ext) > 0 else np.nan
    ipk = int(np.argmax(sgn * gp[:31]))
    pk = gp[ipk]
    sm = np.convolve(gp, np.ones(3) / 3, mode="same")
    after = np.where(sgn * sm[ipk + 1:] < abs(pk) / np.e)[0]
    decay = float(after[0] + 1) if len(after) else np.nan
    f = np.linspace(0, 0.5, 251)
    H = np.array([np.sum(gp * np.exp(-2j * np.pi * fr * np.arange(len(gp)))) for fr in f])
    corner = np.nan
    if abs(H[0]) > 1e-12:
        r = np.abs(H) / abs(H[0])
        below = np.where(r < 1 / np.sqrt(2))[0]
        corner = float(f[below[0]]) if len(below) else np.nan
    post = sgn * gp[ipk + 1:61]
    ring = float(post.min() / abs(pk)) if len(post) and pk != 0 else np.nan
    out = dict(G30=float(cum[30]), G60=float(cum[60]) if len(cum) > 60 else float(cum[-1]),
               dead_min=float(dead), peak_min=float(ipk), peak=float(pk), decay_min=decay,
               corner_cpm=corner, corner_period_min=(1 / corner if corner and corner > 0 else np.nan),
               pre=float(g[~pos].sum()), ring=ring)
    if w_read_min:
        out["dead_cc"] = float(dead) / w_read_min if dead == dead else np.nan
    return out


def fir_freq(g, lags=LAGS, f=None):
    if f is None:
        f = np.linspace(0, 0.5, 129)
    H = np.array([np.sum(g * np.exp(-2j * np.pi * fr * lags)) for fr in f])
    return f, H


# ============================================================================ Part A: Welch coherence / phase
def welch_sums(ys, Xs, nseg=128, step=64):
    """Accumulate Sxx, Syy, Sxy per input class over day segments. Returns dict of sums (poolable)."""
    nc = Xs[0].shape[0]
    win = np.hanning(nseg)
    Sxx = np.zeros((nc, nseg // 2 + 1))
    Syy = np.zeros(nseg // 2 + 1)
    Sxy = np.zeros((nc, nseg // 2 + 1), complex)
    nsegs = 0
    for y, X in zip(ys, Xs):
        M = len(y)
        if M < nseg // 2:
            continue
        starts = list(range(0, max(M - nseg, 0) + 1, step)) if M >= nseg else [0]
        for s0 in starts:
            yy = y[s0:s0 + nseg].astype(float)
            xx = X[:, s0:s0 + nseg].astype(float)
            L = len(yy)
            yy = (yy - yy.mean()) * win[:L]
            xx = (xx - xx.mean(1, keepdims=True)) * win[None, :L]
            Y = np.fft.rfft(yy, nseg)
            Xf = np.fft.rfft(xx, nseg, axis=1)
            Syy += np.abs(Y) ** 2
            Sxx += np.abs(Xf) ** 2
            Sxy += np.conj(Xf) * Y[None, :]
            nsegs += 1
    return dict(Sxx=Sxx, Syy=Syy, Sxy=Sxy, n=nsegs, f=np.fft.rfftfreq(nseg, 1.0))


def welch_summary(ws, bands=((0, 1 / 60), (1 / 60, 1 / 15), (1 / 15, 1 / 4), (1 / 4, 0.5))):
    f = ws["f"]
    coh = np.abs(ws["Sxy"]) ** 2 / (ws["Sxx"] * ws["Syy"][None, :] + 1e-30)
    H = ws["Sxy"] / (ws["Sxx"] + 1e-30)
    out = []
    for c in range(coh.shape[0]):
        row = {}
        for bi, (lo, hi) in enumerate(bands):
            sel = (f > lo) & (f <= hi) & (f > 0)
            # band coherence from band-summed spectra (more stable than mean of ratios)
            sxy = ws["Sxy"][c, sel].sum()
            row[f"coh_b{bi}"] = float(np.abs(sxy) ** 2 / (ws["Sxx"][c, sel].sum() * ws["Syy"][sel].sum() + 1e-30))
            row[f"gain_b{bi}"] = float(np.abs(H[c, sel]).mean())
        # group delay over the lowest 15 non-zero frequencies (periods >= ~8.5 min) from unwrapped phase
        sel = (f > 0) & (f <= 1 / 8.5)
        ph = np.unwrap(np.angle(ws["Sxy"][c, sel]))
        if sel.sum() >= 3:
            wts = np.abs(ws["Sxy"][c, sel])
            A = np.vstack([f[sel], np.ones(sel.sum())]).T
            sl = np.linalg.lstsq(A * wts[:, None], ph * wts, rcond=None)[0][0]
            row["group_delay_min"] = float(-sl / (2 * np.pi))
        out.append(row)
    return out, coh, H


# ============================================================================ event-call machinery
def call_keys(U):
    c = U["calls"]
    return c["agent"].astype(np.float64) * KEYMUL + c["tc"]


def readout_index(U, keys, t_e, rec):
    """Index of the recipient's first call with tc > t_e (hop 1), or -1 if not the same agent+day."""
    c = U["calls"]
    idx = np.searchsorted(keys, rec.astype(np.float64) * KEYMUL + t_e, side="right")
    n = len(keys)
    ok = idx < n
    idx_c = np.minimum(idx, n - 1)
    ok &= c["agent"][idx_c] == rec
    return np.where(ok, idx, -1)


def hop_table(U, keys, t_e, d_e, rec, outcome, hops=HOPS):
    """Outcome at hops for each pair: returns Y [P, H] float (nan where invalid)."""
    c = U["calls"]
    i1 = readout_index(U, keys, t_e, rec)
    n = len(keys)
    Y = np.full((len(t_e), len(hops)), np.nan, np.float32)
    for j, h in enumerate(hops):
        idx = i1 + h - 1
        ok = (i1 >= 0) & (idx >= 0) & (idx < n)
        idc = np.clip(idx, 0, n - 1)
        ok &= (c["agent"][idc] == rec) & (c["day"][idc] == d_e)
        if h <= 0:
            ok &= ~c["first"][idc] | (h == 0)
        Y[ok, j] = outcome[idc[ok]]
    return Y, i1


def day_sums_hops(Y, d_e, D):
    """Per-day sums and counts per hop: [D, H] each (nan-aware)."""
    s = np.zeros((D, Y.shape[1]))
    n = np.zeros((D, Y.shape[1]))
    v = ~np.isnan(Y)
    for j in range(Y.shape[1]):
        np.add.at(s[:, j], d_e[v[:, j]], Y[v[:, j], j])
        np.add.at(n[:, j], d_e[v[:, j]], 1)
    return s, n


def placebo_times(U, t_e, d_e, rng, lo=300.0, hi=1800.0):
    """Shift each event by +-U[lo,hi] s, reflected into its day's grid window."""
    sh = rng.uniform(lo, hi, len(t_e)) * rng.choice([-1, 1], len(t_e))
    tp = t_e + sh
    a, b = U["day_t0"][d_e] + 900, U["day_t1"][d_e] - 300   # calendar window (grid minus padding)
    tp = np.where(tp < a, 2 * a - tp, tp)
    tp = np.where(tp > b, 2 * b - tp, tp)
    return np.clip(tp, a, b)


def rd_rows(U, keys, t_e, d_e, rec, W=120.0, donut=2.0, k=1):
    """Expand pairs into (pair, call) rows for the k-th boundary RD: anchor calls a of the recipient with
    |t_call(a) - t_e| <= W (same agent and day); the outcome call is c = a + k - 1 (same agent and day).
    s = t_call(a) - t_e. For k = 1 this compares the read-out call (s > 0) with the in-flight call (s < 0);
    for k > 1 it compares hop k with hop k-1, so the jumps are increments of the hop kernel."""
    c = U["calls"]
    n = len(keys)
    base = rec.astype(np.float64) * KEYMUL
    lo = np.searchsorted(keys, base + t_e - W, side="left")
    hi = np.searchsorted(keys, base + t_e + W, side="left")
    cnt = hi - lo
    P = np.repeat(np.arange(len(t_e)), cnt)
    off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
    a = np.repeat(lo, cnt) + off
    s = c["tc"][a] - t_e[P]
    ok = (c["agent"][a] == rec[P]) & (c["day"][a] == d_e[P]) & (np.abs(s) >= donut)
    idx = a + (k - 1)
    ok &= idx < n
    idc = np.minimum(idx, n - 1)
    ok &= (c["agent"][idc] == rec[P]) & (c["day"][idc] == d_e[P]) & ~c["first"][np.minimum(a, n - 1)]
    return P[ok], idc[ok], s[ok]


def rd_day_stats(P, idx, s, d_e, outcome, D):
    """Per day, per side (0 left, 1 right): n, sum s, sum s^2, sum y, sum s*y -> array [D, 2, 5]."""
    y = outcome[idx].astype(float)
    side = (s >= 0).astype(int)
    dd = d_e[P]
    st = np.zeros((D, 2, 5))
    for k, v in enumerate((np.ones_like(s), s, s * s, y, s * y)):
        np.add.at(st[:, :, k], (dd, side), v)
    return st


def _ll_intercepts(st):
    """Local-linear intercepts at s=0 for both sides from summed stats [2,5]; also side means."""
    out = []
    for side in (0, 1):
        n, s1, s2, y1, sy = st[side]
        det = n * s2 - s1 * s1
        if n < 5 or det <= 0:
            out.append((np.nan, np.nan))
            continue
        a = (s2 * y1 - s1 * sy) / det
        out.append((a, y1 / n))
    return out


def rd_summary(st_real, st_pl, w=None):
    """Jump J (placebo-corrected), raw jump, placebo jump, X- and X+ (placebo-corrected side means), kappa."""
    if w is None:
        w = np.ones(st_real.shape[0])
    R = np.tensordot(w, st_real, axes=1)
    Q = np.tensordot(w, st_pl, axes=1)
    (aL, mL), (aR, mR) = _ll_intercepts(R)
    (pL, qL), (pR, qR) = _ll_intercepts(Q)
    Jraw, Jpl = aR - aL, pR - pL
    J = Jraw - Jpl
    Xp, Xm = mR - qR, mL - qL
    base = 0.5 * (qL + qR)
    Ep = aR - base - Jpl / 2          # placebo-corrected right limit excess
    Em = aL - base + Jpl / 2          # placebo-corrected left limit excess
    kap = J / Ep if (Ep == Ep and abs(Ep) > 1e-9) else np.nan
    return dict(J=J, J_raw=Jraw, J_pl=Jpl, Xp=Xp, Xm=Xm, Ep=Ep, Em=Em, kappa=kap, base=base, meanR=mR, meanL=mL)


def blocks(U, t_e, d_e, min_days=3):
    """Resampling blocks for the bootstrap: days if the events span >= min_days days, else 1-hour blocks of the
    day window (short units). Returns (blk per event, number of blocks)."""
    D = len(U["day_t0"])
    if len(np.unique(d_e)) >= min_days:
        return d_e.astype(np.int64), D
    h = np.clip(((t_e - U["day_t0"][d_e]) // 3600).astype(np.int64), 0, 47)
    return d_e.astype(np.int64) * 48 + h, D * 48


def boot_days(D, nboot, rng, days_ok=None):
    days = np.arange(D) if days_ok is None else np.asarray(days_ok)
    for _ in range(nboot):
        yield np.bincount(rng.choice(days, len(days)), minlength=D).astype(float)


def gate_test(U, keys, t_e, d_e, rec, outcomes: dict, W=120.0, nboot=200, seed=1, n_pl=2, k=1):
    """C2: read-out jump per outcome (k-th boundary), with placebo (n_pl shifted copies) and day bootstrap."""
    rng = np.random.default_rng(seed)
    blk, D = blocks(U, t_e, d_e)
    P, idx, s = rd_rows(U, keys, t_e, d_e, rec, W, k=k)
    pl = []
    for _ in range(n_pl):
        tp = placebo_times(U, t_e, d_e, rng)
        pl.append(rd_rows(U, keys, tp, d_e, rec, W, k=k))
    res = {}
    days_ok = np.unique(blk)
    for name, y in outcomes.items():
        sr = rd_day_stats(P, idx, s, blk, y, D)
        sp = sum(rd_day_stats(pp, ii, ss, blk, y, D) for pp, ii, ss in pl) / n_pl
        est = rd_summary(sr, sp)
        bs = [rd_summary(sr, sp, w) for w in boot_days(D, nboot, rng, days_ok)]
        for kk in ("J", "J_raw", "J_pl", "Xp", "Xm", "Ep", "Em", "kappa"):
            v = np.array([b[kk] for b in bs], float)
            v = v[np.isfinite(v)]
            est[kk + "_lo"] = float(np.percentile(v, 2.5)) if len(v) > 10 else np.nan
            est[kk + "_hi"] = float(np.percentile(v, 97.5)) if len(v) > 10 else np.nan
            est[kk + "_se"] = float(np.std(v)) if len(v) > 10 else np.nan
        est["boot_J"] = np.array([b["J"] for b in bs], float)
        est["n_rows"] = int(len(P))
        est["n_pairs"] = int(len(np.unique(P)))
        res[name] = est
    return res


def hop_response(U, keys, t_e, d_e, rec, outcomes: dict, nboot=200, seed=2, hops=HOPS, n_pl=2):
    """Part B: placebo-corrected hop profile r(h) per outcome with day-bootstrap CIs; read-out delay quantiles."""
    rng = np.random.default_rng(seed)
    blk, D = blocks(U, t_e, d_e)
    res = {}
    tps = [placebo_times(U, t_e, d_e, rng) for _ in range(n_pl)]
    i1_cache = None
    for name, y in outcomes.items():
        Yr, i1 = hop_table(U, keys, t_e, d_e, rec, y, hops)
        i1_cache = i1
        sr, nr = day_sums_hops(Yr, blk, D)
        sp = np.zeros_like(sr)
        npl = np.zeros_like(nr)
        for tp in tps:
            Yp, _ = hop_table(U, keys, tp, d_e, rec, y, hops)
            a, b = day_sums_hops(Yp, blk, D)
            sp += a
            npl += b

        def prof(w):
            R = (w[:, None] * sr).sum(0) / np.maximum((w[:, None] * nr).sum(0), 1)
            Q = (w[:, None] * sp).sum(0) / np.maximum((w[:, None] * npl).sum(0), 1)
            return R - Q, R, Q
        r, R, Q = prof(np.ones(D))
        bs = np.array([prof(w)[0] for w in boot_days(D, nboot, rng, np.unique(blk))])
        res[name] = dict(r=r, rate=R, base=Q, lo=np.percentile(bs, 2.5, 0), hi=np.percentile(bs, 97.5, 0),
                         se=bs.std(0), n=nr.sum(0))
    c = U["calls"]
    ok = i1_cache >= 0
    dl = c["tc"][i1_cache[ok]] - t_e[ok]
    res["readout_delay_s"] = dict(q10=float(np.percentile(dl, 10)) if ok.any() else np.nan,
                                  q50=float(np.percentile(dl, 50)) if ok.any() else np.nan,
                                  q90=float(np.percentile(dl, 90)) if ok.any() else np.nan, n=int(ok.sum()))
    return res


def onset_hop(rr, hops=HOPS, alpha_lo="lo"):
    """First hop >= 1 whose CI lower bound > 0 (positive response), else nan."""
    for j, h in enumerate(hops):
        if h >= 1 and rr[alpha_lo][j] > 0:
            return int(h)
    return np.nan


# ============================================================================ C1: equal-time co-movement decomposition
def tent_basis(lags, knots):
    B = np.zeros((len(knots), len(lags)))
    for b, k in enumerate(knots):
        left = knots[b - 1] if b > 0 else k - 1
        right = knots[b + 1] if b < len(knots) - 1 else k + 1
        for j, L in enumerate(lags):
            if left < L <= k:
                B[b, j] = (L - left) / (k - left)
            elif k < L < right:
                B[b, j] = (right - L) / (right - k)
            if L == k:
                B[b, j] = 1.0
    return B


EXO_LAGS = np.arange(-10, 61)
EXO_KNOTS = [-10, -5, -2, 0, 1, 2, 3, 5, 8, 12, 18, 25, 35, 45, 60]
PEER_LAGS = np.arange(-10, 31)
PEER_KNOTS = [-10, -5, -3, -2, -1, 0, 1, 2, 3, 5, 8, 12, 18, 25, 30]


def conv_basis(x, lags, B):
    """x [N, M] -> [nb, N, M]: sum_k B_b(k) x[m-k]."""
    kmin = lags[0]
    N, M = x.shape
    out = np.zeros((B.shape[0], N, M), np.float32)
    for b in range(B.shape[0]):
        ker = B[b]
        for i in range(N):
            if not x[i].any():
                continue
            cc = np.convolve(x[i], ker)
            # y[m] = cc[m - kmin]
            if kmin <= 0:
                seg = cc[-kmin:-kmin + M]
                out[b, i, :len(seg)] = seg
            else:
                seg = cc[:M - kmin]
                out[b, i, kmin:kmin + len(seg)] = seg
    return out


def c1_masks(grid, variant):
    """Agent-minute mask per day: span (within own first..last call), full (day-present agents, whole window),
    trim (minutes where every day-present agent is within its span)."""
    ms = []
    for g in grid:
        if variant == "span":
            m = g["S"].copy()
        elif variant == "full":
            m = np.repeat(g["present"][:, None], g["M"], 1)
        elif variant == "trim":
            allin = g["S"][g["present"]].all(0) if g["present"].any() else np.zeros(g["M"], bool)
            m = g["present"][:, None] & allin[None, :]
        ms.append(m)
    return ms


def comove(E, mask):
    """S = sum_m[(sum e)^2 - sum e^2] / sum_m sum e^2 and per-pair rho = S-numerator / sum (n_m-1) sum e^2."""
    num = den = den2 = 0.0
    for e, m in zip(E, mask):
        ee = np.where(m, e, 0.0)
        s = ee.sum(0)
        q = (ee ** 2).sum(0)
        n = m.sum(0)
        num += float((s ** 2 - q).sum())
        den += float(q.sum())
        den2 += float(((n - 1).clip(0) * q).sum())
    return num / den if den > 0 else np.nan, num / den2 if den2 > 0 else np.nan


def _c1_prepare(grid, Xexo, Xpeer, which, variant, lag_peer):
    masks = c1_masks(grid, variant)
    Bx = tent_basis(EXO_LAGS, EXO_KNOTS)
    plags = np.arange(1, 31) if lag_peer else PEER_LAGS
    pknots = [1, 2, 3, 5, 8, 12, 18, 25, 30] if lag_peer else PEER_KNOTS
    Bp = tent_basis(plags, pknots)
    E, Zx, Zp = [], [], []
    for d, g in enumerate(grid):
        Y = g[which].astype(np.float64)
        m = masks[d]
        e = np.zeros_like(Y)
        for i in range(Y.shape[0]):
            if m[i].sum() > 0:
                e[i, m[i]] = Y[i, m[i]] - Y[i, m[i]].mean()
        E.append(e)
        zx = np.concatenate([conv_basis(Xexo[d][c], EXO_LAGS, Bx) for c in range(Xexo[d].shape[0])], 0)
        zp = conv_basis(Xpeer[d], plags, Bp)
        for Z in (zx, zp):
            for i in range(Y.shape[0]):
                if m[i].sum() > 0:
                    Z[:, i, m[i]] -= Z[:, i, m[i]].mean(1, keepdims=True)
                Z[:, i, ~m[i]] = 0
        Zx.append(zx)
        Zp.append(zp)
    return masks, E, Zx, Zp, Bx, Bp


def _fit_resid(Zs, E, ridge=1e-3):
    nb = Zs[0].shape[0]
    XtX = sum(np.einsum("bnm,cnm->bc", Z, Z, optimize=True).astype(np.float64) for Z in Zs)
    Xty = sum(np.einsum("bnm,nm->b", Z, e, optimize=True) for Z, e in zip(Zs, E))
    tr = np.trace(XtX)
    if tr <= 0:
        return [e.copy() for e in E], np.zeros(nb)
    lam = ridge * tr / nb
    beta = np.linalg.solve(XtX + lam * np.eye(nb), Xty)
    return [e - np.einsum("b,bnm->nm", beta, Z) for Z, e in zip(Zs, E)], beta


def c1_decompose(grid, Xexo, Xpeer, which="A", variant="span", nnull=5, seed=3, lag_peer=True):
    """Equal-time co-movement S and what measured exogenous inputs explain (in-sample fit of shared FIR kernels,
    smooth tent basis; f_F), against a null with each day's inputs circularly shifted (f_F_null). Optionally a
    strictly lagged peer term (lags 1-30 min; f_lag). Field and coupling interact (coupling amplifies field-driven
    co-movement), so shares need not add up."""
    masks, E, Zx, Zp, Bx, Bp = _c1_prepare(grid, Xexo, Xpeer, which, variant, lag_peer)
    S_raw, rho_raw = comove(E, masks)
    RF, bF = _fit_resid(Zx, E)
    S_F, rho_F = comove(RF, masks)
    RFP, bFP = _fit_resid([np.concatenate([a, b], 0) for a, b in zip(Zx, Zp)], E)
    S_FP, _ = comove(RFP, masks)
    rng = np.random.default_rng(seed)
    nulls = []
    for _ in range(nnull):
        Zs = []
        for zx, m in zip(Zx, masks):
            M = zx.shape[2]
            sh = int(rng.integers(30, M - 30)) if M > 60 else 0
            z2 = np.roll(zx, sh, axis=2)
            z2[:, ~m] = 0
            Zs.append(z2)
        Rn, _ = _fit_resid(Zs, E)
        nulls.append(comove(Rn, masks)[0])
    S_null = float(np.mean(nulls)) if nulls else np.nan
    ok = S_raw is not None and S_raw == S_raw and S_raw > 0
    out = dict(S_raw=S_raw, rho_raw=rho_raw, S_F=S_F, rho_F=rho_F, S_FP=S_FP,
               f_F=(S_raw - S_F) / S_raw if ok else np.nan,
               f_F_null=(S_raw - S_null) / S_raw if ok else np.nan,
               f_F_null_sd=float(np.std([(S_raw - x) / S_raw for x in nulls])) if ok and nulls else np.nan,
               f_lag=(S_F - S_FP) / S_raw if ok else np.nan,
               kern_exo=(bF.reshape(-1, len(EXO_KNOTS)) @ Bx), kern_peer=(bFP[-Bp.shape[0]:] @ Bp),
               resid_F=RF, masks=masks, E=E)
    return out
    return out


def gate_kernel(U, keys, t_e, d_e, rec, y, K=6, W=20.0, nboot=200, seed=5, n_pl=2):
    """Hop kernel of the gated (causal) response: delta(h) = sum_{q<=h} jump_q, from successive boundary RDs.
    Returns jumps, cumulative kernel and bootstrap CIs (bootstrap per boundary, combined assuming independence
    of the day resamples is avoided by using a common day-weight draw)."""
    rng = np.random.default_rng(seed)
    blk, D = blocks(U, t_e, d_e)
    days_ok = np.unique(blk)
    tps = [placebo_times(U, t_e, d_e, rng) for _ in range(n_pl)]
    stats = []
    for k in range(1, K + 1):
        P, idx, s = rd_rows(U, keys, t_e, d_e, rec, W, k=k)
        sr = rd_day_stats(P, idx, s, blk, y, D)
        sp = sum(rd_day_stats(*rd_rows(U, keys, tp, d_e, rec, W, k=k), blk, y, D) for tp in tps) / n_pl
        stats.append((sr, sp))
    jumps = np.array([rd_summary(sr, sp)["J"] for sr, sp in stats])
    W_ = list(boot_days(D, nboot, rng, days_ok))
    bj = np.array([[rd_summary(sr, sp, w)["J"] for sr, sp in stats] for w in W_])
    cum = np.cumsum(jumps)
    bc = np.cumsum(bj, 1)
    return dict(jumps=jumps, kernel=cum, j_lo=np.nanpercentile(bj, 2.5, 0), j_hi=np.nanpercentile(bj, 97.5, 0),
                k_lo=np.nanpercentile(bc, 2.5, 0), k_hi=np.nanpercentile(bc, 97.5, 0), k_se=np.nanstd(bc, 0),
                total=float(cum.sum()), total_lo=float(np.nanpercentile(bc.sum(1), 2.5)),
                total_hi=float(np.nanpercentile(bc.sum(1), 97.5)))


def median_call_interval(U):
    """Median start-to-start interval of consecutive calls of the same agent-day, excluding pause calls."""
    c = U["calls"]
    dt = np.diff(c["tc"])
    same = (np.diff(c["agent"]) == 0) & (np.diff(c["day"]) == 0) & c["act"][:-1]
    return float(np.median(dt[same])) if same.any() else np.nan


def mean_readout_wait(U):
    """E[Delta^2] / (2 E[Delta]) over all within-day call intervals (renewal residual wait), seconds."""
    c = U["calls"]
    dt = np.diff(c["tc"])
    same = (np.diff(c["agent"]) == 0) & (np.diff(c["day"]) == 0)
    d = dt[same]
    return float((d ** 2).mean() / (2 * d.mean())) if len(d) else np.nan


def cf_coupling_series(U, grid, keys, t_e, d_e, rec, delta, which="T"):
    """Counterfactual: expected coupling-caused outcome per agent-minute, from the gated hop kernel delta[h-1]
    applied to every (message, recipient) read-out: call c1+h-1 gets +delta[h-1]; mapped to the call's logged minute.
    Returns per-day arrays [N, M] (expected caused talk calls, or act calls)."""
    c = U["calls"]
    n = len(keys)
    i1 = readout_index(U, keys, t_e, rec)
    out = [np.zeros((U["N"], g["M"]), np.float64) for g in grid]
    for h, dv in enumerate(delta, start=1):
        if dv == 0:
            continue
        idx = i1 + h - 1
        ok = (i1 >= 0) & (idx < n)
        idc = np.minimum(idx, n - 1)
        ok &= (c["agent"][idc] == rec) & (c["day"][idc] == d_e)
        idc = idc[ok]
        dd = c["day"][idc]
        for d in np.unique(dd):
            sel = dd == d
            m = ((c["tl"][idc[sel]] - grid[d]["t0"]) // 60).astype(int)
            m = np.clip(m, 0, grid[d]["M"] - 1)
            np.add.at(out[d], (c["agent"][idc[sel]], m), dv)
    return out


def cf_share(grid, cf, which="T", variant="span"):
    """Share of equal-time co-movement (agent-day demeaned) removed by subtracting the counterfactual series."""
    masks = c1_masks(grid, variant)
    E0, E1 = [], []
    for g, y_cf, m in zip(grid, cf, masks):
        Y = g[which].astype(np.float64)
        Y1 = Y - y_cf
        e0 = np.zeros_like(Y)
        e1 = np.zeros_like(Y)
        for i in range(Y.shape[0]):
            if m[i].sum() > 0:
                e0[i, m[i]] = Y[i, m[i]] - Y[i, m[i]].mean()
                e1[i, m[i]] = Y1[i, m[i]] - Y1[i, m[i]].mean()
        E0.append(e0)
        E1.append(e1)
    S0, _ = comove(E0, masks)
    S1, _ = comove(E1, masks)
    return dict(S=S0, S_cf=S1, f_C=(S0 - S1) / S0 if S0 and S0 > 0 else np.nan)


def cf_share_resid(resid, masks, cf):
    """S of residuals (e.g. after the field fit) before and after subtracting the agent-day-demeaned CF series."""
    E1 = []
    for e, m, y in zip(resid, masks, cf):
        e1 = e.copy()
        for i in range(e.shape[0]):
            if m[i].sum() > 0:
                yy = y[i, m[i]]
                e1[i, m[i]] = e[i, m[i]] - (yy - yy.mean())
        E1.append(e1)
    S0, _ = comove(resid, masks)
    S1, _ = comove(E1, masks)
    return dict(S=S0, S_cf=S1)


def floats(d):
    return {k: float(v) for k, v in d.items() if isinstance(v, (int, float, np.floating, np.integer))}


def gate_stats(U, keys, t_e, d_e, rec, y, K=4, W=20.0, n_pl=2, seed=11):
    """Per-day RD sufficient statistics for boundaries 1..K (real, placebo): list of (sr [D,2,5], sp [D,2,5]).
    Day axes of different units can be concatenated to pool units (days are distinct)."""
    rng = np.random.default_rng(seed)
    D = len(U["day_t0"])
    tps = [placebo_times(U, t_e, d_e, rng) for _ in range(n_pl)]
    out = []
    for k in range(1, K + 1):
        P, idx, s = rd_rows(U, keys, t_e, d_e, rec, W, k=k)
        sr = rd_day_stats(P, idx, s, d_e, y, D)
        sp = sum(rd_day_stats(*rd_rows(U, keys, tp, d_e, rec, W, k=k), d_e, y, D) for tp in tps) / n_pl
        out.append((sr, sp))
    return out


def kernel_from_stats(stats, nboot=400, seed=12):
    """Pooled hop kernel from (possibly concatenated) per-day stats."""
    rng = np.random.default_rng(seed)
    D = stats[0][0].shape[0]
    days_ok = np.where(stats[0][0][:, :, 0].sum(1) > 0)[0]
    jumps = np.array([rd_summary(sr, sp)["J"] for sr, sp in stats])
    summ1 = rd_summary(*stats[0])
    if len(days_ok) < 2:
        return dict(jumps=jumps, j_lo=np.full(len(stats), np.nan), j_hi=np.full(len(stats), np.nan), n_days=len(days_ok),
                    Ep=summ1["Ep"], Em=summ1["Em"], kappa=summ1["kappa"], base=summ1["base"])
    bj = np.array([[rd_summary(sr, sp, w)["J"] for sr, sp in stats] for w in boot_days(D, nboot, rng, days_ok)])
    return dict(jumps=jumps, j_lo=np.nanpercentile(bj, 2.5, 0), j_hi=np.nanpercentile(bj, 97.5, 0),
                j_se=np.nanstd(bj, 0), n_days=int(len(days_ok)), n_rows=float(stats[0][0][:, :, 0].sum()),
                Ep=summ1["Ep"], Em=summ1["Em"], kappa=summ1["kappa"], base=summ1["base"])


def concat_stats(list_of_stats):
    K = min(len(s) for s in list_of_stats)
    return [(np.concatenate([s[k][0] for s in list_of_stats], 0), np.concatenate([s[k][1] for s in list_of_stats], 0))
            for k in range(K)]


def gap_trigger(U, keys, t_e, rec, min_gap=30.0, win=30.0):
    """Message-triggered call starts: for (message, recipient) pairs where the message arrives while the recipient is
    between calls (after its in-flight call's logged end, gap >= min_gap), the share of next calls starting within
    `win` s of the message vs the share expected for a uniformly placed arrival (win / gap). Returns arrays per pair:
    real indicator, expected, gap length, in-flight kind flags."""
    c = U["calls"]
    i1 = readout_index(U, keys, t_e, rec)
    n = len(keys)
    h0 = i1 - 1
    ok = (i1 >= 0) & (h0 >= 0)
    h0c = np.clip(h0, 0, n - 1)
    i1c = np.clip(i1, 0, n - 1)
    ok &= (c["agent"][h0c] == rec) & (c["day"][h0c] == c["day"][i1c])
    gap_start = c["tl"][h0c]
    G = c["tc"][i1c] - gap_start
    ok &= (t_e > gap_start) & (G >= min_gap)
    dlt = c["tc"][i1c] - t_e
    real = (dlt < win).astype(float)
    expd = np.minimum(win / np.maximum(G, 1e-9), 1.0)
    return dict(ok=ok, real=real, exp=expd, G=G, chat=c["chat"][h0c] if "chat" in c else np.zeros(n, bool)[h0c],
                wait=c["wait"][h0c] if "wait" in c else np.zeros(n, bool)[h0c],
                pause=c["pause"][h0c] if "pause" in c else (~c["act"])[h0c], day=c["day"][i1c])
