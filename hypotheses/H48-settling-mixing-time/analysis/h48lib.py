"""H48 core: read-out coverage, read-out Markov chains and their mixing times, time-respecting DeGroot, settling fits.

Card: hypotheses/H48-settling-mixing-time/README.md (Observables). Conventions:
  a = active hours since the period's kickoff (scheme/h48common.active_hours_fast)
  W_ij = j's messages read by i per active hour (ledger-read, weighted); rows are readers.
  "block" = the agents of one kickoff room (>= 3 roster agents); cross-block pairs are unreachable by the
  ledger's visibility rule (agents read only their own room).
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h48common as hc  # noqa: E402,F401  (sets thread limits)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.linalg import expm  # noqa: E402

EPS = 1e-12


def _load_module(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod            # dataclasses need the module registered
    spec.loader.exec_module(mod)
    return mod


_H31 = None
_H54E = None
_H20 = None


def h31lib():
    """H31's lambda_2 functions (read-only import)."""
    global _H31
    if _H31 is None:
        _H31 = _load_module("h31lib_ro", hc.ROOT / "hypotheses/H31-consensus-time-spectral-gap/analysis/h31lib.py")
    return _H31


def h54est():
    global _H54E
    if _H54E is None:
        p = hc.ROOT / "hypotheses/H54-kickoff-quench-target/analysis"
        sys.path.insert(1, str(p))
        _H54E = _load_module("h54est_ro", p / "h54est.py")
    return _H54E


def h20lib():
    global _H20
    if _H20 is None:
        p = hc.ROOT / "hypotheses/H20-content-aging/analysis"
        _H20 = _load_module("h20lib_ro", p / "h20lib.py")
    return _H20


# ============================================================================================ data
def load_period(g: int, base: Path = hc.OUT, suffix: str = "") -> dict:
    def rd(name):
        return pl.read_parquet(base / f"{name}{suffix}.parquet").filter(pl.col("goal_no") == g)
    P = {"g": g, "calls": rd("calls"), "reads": rd("reads"), "msgs": rd("msgs"), "roster": rd("roster"),
         "stmts": rd("stmts")}
    per = pl.read_parquet(base / f"periods{suffix}.parquet").filter(pl.col("goal_no") == g)
    P["meta"] = per.row(0, named=True)
    return P


def day_ends(g: int, allow_holdout: bool = False) -> np.ndarray:
    """Active hours since kickoff at the end of each active day (from the calendar)."""
    days = hc.period_days(g, allow_holdout)
    t0 = hc.kickoff_t0(g, allow_holdout)
    we = days["win_end"].dt.epoch("us").to_numpy()
    return hc.active_hours_fast(we, days["pt_date"].to_numpy(), g, allow_holdout, t0)


def blocks_of(roster: pl.DataFrame, min_size: int = 3) -> dict:
    """Kickoff-room blocks among day-1 roster agents: {room: [agents]} for rooms with >= min_size agents."""
    r = roster.filter(pl.col("on_day1") & pl.col("room0").is_not_null())
    out = {}
    for room, ags in r.group_by("room0").agg(pl.col("agent")).iter_rows():
        if len(ags) >= min_size:
            out[int(room)] = sorted(int(a) for a in ags)
    return dict(sorted(out.items()))


# ============================================================================================ coverage
def pair_cover_times(reads: pl.DataFrame, agents: list[int], k: int = 1) -> np.ndarray:
    """(N, N) active time at which reader i has read >= k post-kickoff messages of sender j (inf if never)."""
    N = len(agents)
    pos = {a: n for n, a in enumerate(agents)}
    T = np.full((N, N), np.inf)
    r = reads.filter(pl.col("reader").is_in(agents) & pl.col("sender").is_in(agents)).sort("a_read")
    if r.height == 0:
        return T
    g = (r.group_by("reader", "sender", maintain_order=True)
         .agg(pl.col("a_read").sort().slice(k - 1, 1).first().alias("tk")))
    for i, j, t in g.iter_rows():
        if t is not None:
            T[pos[int(i)], pos[int(j)]] = float(t)
    np.fill_diagonal(T, np.nan)
    return T


def reach_times(reads: pl.DataFrame, agents: list[int], t_src: float = 0.0) -> np.ndarray:
    """Time-respecting reachability: R[j, i] = earliest active time at which information from j's post-kickoff
    output can have reached i along read paths (R[j, j] = t_src). A read (i reads s's message posted at a_msg, at
    a_read) carries every source j with R[j, s] <= a_msg."""
    N = len(agents)
    pos = {a: n for n, a in enumerate(agents)}
    R = np.full((N, N), np.inf)
    np.fill_diagonal(R, t_src)
    r = reads.filter(pl.col("reader").is_in(agents) & pl.col("sender").is_in(agents)).sort("a_read")
    if r.height == 0:
        return R
    ii = np.array([pos[int(x)] for x in r["reader"].to_list()])
    ss = np.array([pos[int(x)] for x in r["sender"].to_list()])
    am = r["a_msg"].to_numpy().astype(float)
    ar = r["a_read"].to_numpy().astype(float)
    for n in range(len(ii)):
        i, s = ii[n], ss[n]
        m = R[:, s] <= am[n]
        if m.any():
            col = R[:, i]
            upd = m & (col > ar[n])
            if upd.any():
                col[upd] = ar[n]
                if np.isfinite(R).all():
                    break
    return R


def coverage_stats(T: np.ndarray, mask: np.ndarray, qs=(0.5, 0.9, 0.99)) -> dict:
    """Coverage-time quantiles over the pairs in mask (off-diagonal). inf = right-censored."""
    v = np.sort(T[mask & ~np.eye(len(T), dtype=bool)].ravel())
    v = v[~np.isnan(v)]
    n = len(v)
    out = {"n_pairs": n, "share_ever": float(np.isfinite(v).mean()) if n else np.nan}
    for q in qs:
        if n == 0:
            out[f"T{int(round(q * 100))}"] = np.nan
            continue
        k = int(math.ceil(q * n)) - 1
        out[f"T{int(round(q * 100))}"] = float(v[k])
    return out


def coverage_curve(T: np.ndarray, mask: np.ndarray, grid: np.ndarray) -> np.ndarray:
    v = T[mask & ~np.eye(len(T), dtype=bool)].ravel()
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return np.full(len(grid), np.nan)
    v = np.sort(v)
    return np.searchsorted(v, grid, side="right") / len(v)


def same_block_mask(agents: list[int], blocks: dict) -> np.ndarray:
    lab = np.full(len(agents), -1)
    for b, ags in blocks.items():
        for a in ags:
            if a in agents:
                lab[agents.index(a)] = b
    M = (lab[:, None] == lab[None, :]) & (lab[:, None] >= 0)
    np.fill_diagonal(M, False)
    return M


# ============================================================================================ rates and graphs
def window_rates(calls: pl.DataFrame, reads: pl.DataFrame, agents: list[int], a1: float, a0: float = 0.0) -> dict:
    """Per-agent call rate, reading-turn rate (calls with >= 1 new agent item from roster agents), read rate and
    median inter-call interval in [a0, a1) (active hours)."""
    H = max(a1 - a0, EPS)
    c = calls.filter(pl.col("agent").is_in(agents) & (pl.col("a") >= a0) & (pl.col("a") < a1))
    r = reads.filter(pl.col("reader").is_in(agents) & pl.col("sender").is_in(agents) & (pl.col("a_read") >= a0)
                     & (pl.col("a_read") < a1))
    rt = r.group_by("reader").agg(pl.col("turn_id").n_unique().alias("n_rt"), pl.len().alias("n_reads"))
    cc = c.group_by("agent").agg(pl.len().alias("n_calls"), pl.col("a").sort().diff().median().alias("ici"))
    d = {a: {"calls": 0, "rt": 0, "reads": 0, "ici": np.nan} for a in agents}
    for a, n, ici in cc.iter_rows():
        d[int(a)]["calls"] = n
        d[int(a)]["ici"] = ici if ici is not None else np.nan
    for a, nrt, nr in rt.iter_rows():
        d[int(a)]["rt"] = nrt
        d[int(a)]["reads"] = nr
    call = np.array([d[a]["calls"] / H for a in agents])
    u = np.array([d[a]["rt"] / H for a in agents])
    rr = np.array([d[a]["reads"] / H for a in agents])
    ici = np.array([d[a]["ici"] for a in agents], float)
    return {"call_rate": call, "u": u, "read_rate": rr, "ici_h": ici}


def read_graph(reads: pl.DataFrame, agents: list[int], a1: float, a0: float = 0.0) -> np.ndarray:
    pos = {a: n for n, a in enumerate(agents)}
    N = len(agents)
    W = np.zeros((N, N))
    r = reads.filter(pl.col("reader").is_in(agents) & pl.col("sender").is_in(agents) & (pl.col("a_read") >= a0)
                     & (pl.col("a_read") < a1)).group_by("reader", "sender").len()
    for i, j, n in r.iter_rows():
        W[pos[int(i)], pos[int(j)]] += n
    np.fill_diagonal(W, 0.0)
    return W / max(a1 - a0, EPS)


def generator(W: np.ndarray, kind: str, u: np.ndarray | None = None) -> np.ndarray:
    """Read-out chain generator (rows = readers). batch: Q_ij = u_i W_ij / sum_k W_ik; count: Q = W - diag(W 1)."""
    A = W.copy()
    np.fill_diagonal(A, 0.0)
    d = A.sum(1)
    if kind == "batch":
        Pm = np.where(d[:, None] > 0, A / np.maximum(d, EPS)[:, None], 0.0)
        Q = (u[:, None] if u is not None else 1.0) * Pm
    elif kind == "count":
        Q = A
    else:
        raise ValueError(kind)
    Q = Q - np.diag(Q.sum(1))
    return Q


def mixing_times(Q: np.ndarray, eps: float = 0.25, grid=None) -> np.ndarray:
    """Per-start TV mixing time t_i = min{t : TV(e_i e^{Qt}, e_i e^{Q inf}) <= eps}; inf if never on the grid."""
    N = len(Q)
    if N < 2:
        return np.full(N, np.nan)
    ev = np.linalg.eigvals(Q)
    rates = -ev.real
    nz = rates[rates > 1e-9]
    if len(nz) == 0:
        return np.full(N, np.inf)
    lam_min = nz.min()
    Pinf = expm(Q * (60.0 / lam_min))
    if grid is None:
        grid = np.geomspace(1e-3, max(1e4, 100.0 / lam_min), 240)
    t_mix = np.full(N, np.inf)
    prev_tv = np.ones(N)
    for k, t in enumerate(grid):
        tv = 0.5 * np.abs(expm(Q * t) - Pinf).sum(1)
        hit = (tv <= eps) & ~np.isfinite(t_mix)
        if hit.any():
            if k == 0:
                t_mix[hit] = t
            else:
                # log-linear interpolation between grid points
                t_prev = grid[k - 1]
                f = np.clip((prev_tv[hit] - eps) / np.maximum(prev_tv[hit] - tv[hit], EPS), 0, 1)
                t_mix[hit] = np.exp(np.log(t_prev) + f * (np.log(t) - np.log(t_prev)))
        prev_tv = tv
        if np.isfinite(t_mix).all():
            break
    return t_mix


def relaxation_rate(Q: np.ndarray) -> float:
    rates = np.sort(-np.linalg.eigvals(Q).real)
    nz = rates[rates > 1e-9]
    return float(nz.min()) if len(nz) else 0.0


# ============================================================================================ time-respecting DeGroot
def degroot_tr(calls: pl.DataFrame, reads: pl.DataFrame, agents: list[int], blocks: dict, alpha: float = 0.1,
               d: int = 8, reps: int = 4, seed: int = 0, a_max: float | None = None, burn_h: float = 0.5) -> dict:
    """DeGroot batch-mean averaging at reading calls on the real read sequence (senders' state at read time).
    Returns bulk (within-block disagreement to 1/e), worst (max-agent disagreement to 1/e), and the asymptotic
    decay rate gamma (slope of ln D after burn-in; H31's gamma_tr analogue at this alpha)."""
    pos = {a: n for n, a in enumerate(agents)}
    lab = np.full(len(agents), -1)
    for b, ags in blocks.items():
        for a in ags:
            if a in pos:
                lab[pos[a]] = b
    keep = [a for a in agents if lab[pos[a]] >= 0]
    if len(keep) < 3:
        return {"bulk": np.nan, "worst": np.nan, "gamma": np.nan}
    r = reads.filter(pl.col("reader").is_in(keep) & pl.col("sender").is_in(keep))
    if a_max is not None:
        r = r.filter(pl.col("a_read") <= a_max)
    r = r.sort("a_read", "turn_id")
    if r.height == 0:
        return {"bulk": np.inf, "worst": np.inf, "gamma": 0.0}
    tid = r["turn_id"].to_numpy()
    ii = np.array([pos[int(x)] for x in r["reader"].to_list()])
    ss = np.array([pos[int(x)] for x in r["sender"].to_list()])
    tt = r["a_read"].to_numpy().astype(float)
    starts = np.r_[0, np.flatnonzero(np.diff(tid) != 0) + 1]
    ends = np.r_[starts[1:], len(tid)]
    rng = np.random.default_rng(seed)
    sel = np.array([lab[pos[a]] >= 0 for a in agents])
    labs = lab[sel]
    idx_sel = np.flatnonzero(sel)
    res_b, res_w, res_g = [], [], []
    for _ in range(reps):
        X = rng.standard_normal((len(agents), d))

        def disagree(X):
            tot, worst = 0.0, []
            for b in np.unique(labs):
                m = idx_sel[labs == b]
                dev = ((X[m] - X[m].mean(0)) ** 2).sum(1)
                tot += dev.sum()
                worst.append(dev)
            return tot, np.concatenate(worst)
        D0, w0 = disagree(X)
        w0m = w0.mean()
        tb = tw = np.inf
        logD, tlog = [], []
        for s0, e0 in zip(starts, ends):
            i = ii[s0]
            X[i] = (1 - alpha) * X[i] + alpha * X[ss[s0:e0]].mean(0)
            Dt, wt = disagree(X) if (len(logD) % 1 == 0) else (None, None)
            t = tt[s0]
            if not np.isfinite(tb) and Dt <= D0 / math.e:
                tb = t
            if not np.isfinite(tw) and wt.max() <= w0m / math.e:
                tw = t
            logD.append(math.log(max(Dt / D0, 1e-300)))
            tlog.append(t)
            if np.isfinite(tb) and np.isfinite(tw) and logD[-1] < -12:
                break
        tlog, logD = np.array(tlog), np.array(logD)
        m = (tlog > burn_h) & (logD > -12)
        g = float(-np.polyfit(tlog[m], logD[m], 1)[0]) if m.sum() >= 10 and np.ptp(tlog[m]) > 0 else np.nan
        res_b.append(tb)
        res_w.append(tw)
        res_g.append(g)
    return {"bulk": float(np.median(res_b)), "worst": float(np.median(res_w)), "gamma": float(np.nanmedian(res_g))
            if np.isfinite(res_g).any() else np.nan}


# ============================================================================================ settling fits
def exp_plateau_fit(t, y, w=None, tau_lo: float = 0.25, tau_hi: float | None = None, n_grid: int = 80) -> dict | None:
    """Weighted y = A_inf + (A_0 - A_inf) exp(-(t - t_min)/tau) on a geometric tau grid (H54's estimator form, with
    weights). BIC vs constant and linear; 'detected' = dBIC(const - exp) >= 2, decaying, tau below the grid top."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    w = np.ones_like(y) if w is None else np.asarray(w, float)
    m = np.isfinite(y) & np.isfinite(t) & (w > 0)
    t, y, w = t[m], y[m], w[m]
    n = len(y)
    if n < 5:
        return None
    t0 = t.min()
    span = max(t.max() - t0, 1e-6)
    tau_hi = tau_hi or 4 * span
    sw = np.sqrt(w / w.mean())
    best = None
    grid = np.geomspace(tau_lo, tau_hi, n_grid)
    for tau in grid:
        e = np.exp(-(t - t0) / tau)
        X = np.column_stack([np.ones(n), e])
        c, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
        rss = float((((y - X @ c) * sw) ** 2).sum())
        if best is None or rss < best[0]:
            best = (rss, tau, c)
    rss_e, tau, c = best
    ybar = np.average(y, weights=w)
    rss_c = float((((y - ybar) * sw) ** 2).sum())
    Xl = np.column_stack([np.ones(n), t])
    cl, *_ = np.linalg.lstsq(Xl * sw[:, None], y * sw, rcond=None)
    rss_l = float((((y - Xl @ cl) * sw) ** 2).sum())

    def bic(rss, k):
        return n * math.log(max(rss, 1e-12) / n) + k * math.log(n)
    A_inf, A_0 = float(c[0]), float(c[0] + c[1])
    out = {"tau": float(tau), "A_inf": A_inf, "A_0": A_0, "bic_exp": bic(rss_e, 3), "bic_const": bic(rss_c, 1),
           "bic_lin": bic(rss_l, 2), "n": n, "span": span, "at_top": bool(tau >= grid[-2]),
           "at_bottom": bool(tau <= grid[1])}
    out["dbic"] = out["bic_const"] - out["bic_exp"]
    out["detected"] = bool(out["dbic"] >= 2 and A_0 > A_inf and not out["at_top"])
    return out


def unit(x, axis=-1):
    x = np.asarray(x, dtype=np.float64)
    n = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.where(n > 0, n, 1.0)


def bin_vectors(a: np.ndarray, agent: np.ndarray, Z: np.ndarray, width: float, a_max: float, n_min: int = 2):
    """Agent x bin unit mean vectors. Returns bins (mid times), list of (agents_idx, V) per bin."""
    nb = int(math.ceil(a_max / width))
    b = np.floor(a / width).astype(int)
    ok = (a >= 0) & (b < nb)
    out = []
    for k in range(nb):
        m = ok & (b == k)
        if not m.any():
            out.append((np.array([], int), np.zeros((0, Z.shape[1]))))
            continue
        ags = agent[m]
        zz = Z[m]
        ua, inv, cnt = np.unique(ags, return_inverse=True, return_counts=True)
        S = np.zeros((len(ua), Z.shape[1]))
        np.add.at(S, inv, zz)
        keep = cnt >= n_min
        out.append((ua[keep], unit(S[keep] / cnt[keep, None])))
    mids = (np.arange(nb) + 0.5) * width
    return mids, out


# ============================================================================================ cross-period LOPO
def _loo_resid(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Exact leave-one-out residuals of OLS y ~ X (hat-matrix identity e_i / (1 - h_ii)); nan where h_ii ~ 1."""
    XtX = X.T @ X
    try:
        Xi = np.linalg.pinv(XtX)
    except np.linalg.LinAlgError:
        return np.full(len(y), np.nan)
    beta = Xi @ X.T @ y
    e = y - X @ beta
    h = np.einsum("ij,jk,ik->i", X, Xi, X)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(h < 1 - 1e-9, e / (1 - h), np.nan)
    return r


def lopo_rmse(y: np.ndarray, x: np.ndarray | None, groups: np.ndarray | None = None, slope: float | None = None):
    """Leave-one-period-out RMSE of y (log tau) predicted by a + b x (b free, or fixed = slope), optionally with
    group (regime) intercepts; x = None gives the constant model (group means if groups given). Exact LOO via the
    hat matrix (identical to refitting without each period). Returns rmse, LOO predictions."""
    y = np.asarray(y, float)
    n = len(y)
    cols = []
    if groups is None:
        cols.append(np.ones(n))
    else:
        for lv in np.unique(groups):
            cols.append((groups == lv).astype(float))
    yy = y.copy()
    if x is not None:
        x = np.asarray(x, float)
        if slope is None:
            if np.ptp(x) > 0:
                cols.append(x)
        else:
            yy = y - slope * x
    X = np.column_stack(cols)
    r = _loo_resid(yy, X)
    pred = y - r
    ok = np.isfinite(r)
    return float(np.sqrt(np.mean(r[ok] ** 2))), pred


def _rmse_perm_simple(y: np.ndarray, Xp: np.ndarray) -> np.ndarray:
    """Vectorized exact LOO RMSE of y ~ 1 + x for many permuted x (rows of Xp)."""
    n = len(y)
    xb = Xp.mean(1, keepdims=True)
    dx = Xp - xb
    sxx = (dx ** 2).sum(1, keepdims=True)
    yb = y.mean()
    b = (dx * (y - yb)).sum(1, keepdims=True) / np.where(sxx > 0, sxx, np.nan)
    e = (y - yb) - b * dx
    h = 1.0 / n + dx ** 2 / np.where(sxx > 0, sxx, np.nan)
    r = e / (1 - h)
    return np.sqrt(np.nanmean(r ** 2, axis=1))


def lopo_compare(y, x, groups=None, n_perm: int = 2000, seed: int = 0, slope=None):
    """RMSE of the predictor model, of the constant, relative gain, and a permutation p (x shuffled across periods;
    within groups when groups are given)."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    r0, _ = lopo_rmse(y, None, groups)
    r1, pred = lopo_rmse(y, x, groups, slope)
    gain = 1 - r1 / r0
    rng = np.random.default_rng(seed)
    if groups is None and slope is None:
        Xp = np.vstack([rng.permutation(x) for _ in range(n_perm)])
        gp = 1 - _rmse_perm_simple(y, Xp) / r0
        cnt = int(np.sum(gp >= gain - 1e-12))
    else:
        cnt = 0
        for _ in range(n_perm):
            if groups is None:
                xp = rng.permutation(x)
            else:
                xp = x.copy()
                for lv in np.unique(groups):
                    m = groups == lv
                    xp[m] = rng.permutation(x[m])
            rp, _ = lopo_rmse(y, xp, groups, slope)
            cnt += (1 - rp / r0) >= gain - 1e-12
    b = np.polyfit(x, y, 1)[0] if np.ptp(x) > 0 else np.nan
    return {"rmse": r1, "rmse0": r0, "gain": gain, "p_perm": (cnt + 1) / (n_perm + 1), "slope": float(b),
            "n": int(len(y)), "pred": pred}


def holm(ps: dict) -> dict:
    items = sorted(ps.items(), key=lambda kv: kv[1])
    m = len(items)
    out, run = {}, 0.0
    for r, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - r) * p))
        out[k] = run
    return out


# ============================================================================================ S1 estimator
def s1_series(a: np.ndarray, agent: np.ndarray, Z: np.ndarray, k: np.ndarray, D: np.ndarray, a_max: float,
              width: float = 1.0, n_min: int = 2, min_agents: int = 3):
    """Kickoff excess per active-hour bin: mean_i cos(v_ib, k) - mean_q mean_i cos(v_ib, D_q)."""
    mids, bins = bin_vectors(a, agent, Z, width, a_max, n_min)
    ex, na = np.full(len(mids), np.nan), np.zeros(len(mids))
    for b, (ags, V) in enumerate(bins):
        if len(ags) < min_agents:
            continue
        ex[b] = float((V @ k).mean() - (V @ D.T).mean())
        na[b] = len(ags)
    return mids, ex, na


def s1_fit(a, agent, Z, k, D, a_max, width=1.0):
    mids, ex, na = s1_series(a, agent, Z, k, D, a_max, width)
    f = exp_plateau_fit(mids, ex, na)
    return f, (mids, ex, na)
