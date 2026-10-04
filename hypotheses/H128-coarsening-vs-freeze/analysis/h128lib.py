"""H128 library: active clock, project-count curves from host events, shape fits, freeze time, and the kinetic Potts
quench synthetic on the real skeleton.

Curves (card, Data scheme step 4): on a 15-active-minute grid from the kickoff, N_h (hosts), N_p (distinct hosted
repos), N_p_m (merge-only count: repos whose last host expired or left stay counted), K_eff = 1/sum p_j^2, rho = N_p/N_h.
Death kinds (step 5): merge (last host departs to an occupied repo), hop_new (to a repo born at that moment), finish
(last host expires or leaves).

Shape fits (O1): constant, step, exponential, power law A (t - t_pk + 0.25)^-alpha (and an offset variant) on
[t_pk, H]; BIC with n_eff = fit-window length in active hours (>= 4). Freeze time t_f (O3), decline ratio (O4),
merge share (O5), excess area A_u (O6).

Everything here is codes only (repo names never leave memory; hashed on output by the scheme).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import sys  # noqa: E402
import warnings  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.optimize import curve_fit  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_hosts as RH  # noqa: E402

D = ROOT / "data/processed/H128-coarsening-vs-freeze"
GRID_H = 0.25          # grid step, active hours
HORIZON_H = 20.0       # H (card): min(20 h, active length)
PEAK_WINDOW_H = 8.0    # t_pk searched in the first 8 active h
SNAP_S = 15 * 60       # events <= 15 min outside a window snap to its edge
FREEZE_H = 3.0         # "within hours" (card P2)
TOL_FRAC = 0.15        # t_f tolerance: max(1, 0.15 N_inf)
LAST_FRAC = 0.2        # N_inf = median over the last 20% of the horizon
AU_SPAN_H = 8.0        # A_u integrates over [t_pk, t_pk + 8 h]

NAMED = {35, 39, 40, 42, 51}
FREE = {30, 31, 33, 36, 37, 38, 41}
REPL = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 51]


# ============================================================================================ active clock
class ActiveClock:
    """Concatenated calendar windows of the given (non-holdout) days, from the first window's start."""

    def __init__(self, days: list[str]):
        cal = RH.calendar().filter(pl.col("pt_date").is_in(days)).sort("win_start")
        self.ws = np.array([w.timestamp() for w in cal["win_start"].to_list()])
        self.we = np.array([w.timestamp() for w in cal["win_end"].to_list()])
        self.off = np.concatenate([[0.0], np.cumsum(self.we - self.ws)[:-1]])
        self.total_h = float((self.we - self.ws).sum() / 3600)
        self.days = cal["pt_date"].to_list()
        self.n_drop = 0

    def __call__(self, ts) -> np.ndarray:
        """Active hours for epoch seconds ts (array); NaN when > 15 min outside every window."""
        ts = np.asarray(ts, dtype=float)
        out = np.full(ts.shape, np.nan)
        k = np.searchsorted(self.ws, ts, side="right") - 1
        for i, (t, j) in enumerate(zip(ts, k)):
            if j >= 0 and t <= self.we[j]:
                out[i] = self.off[j] + (t - self.ws[j])
                continue
            # nearest edge: end of window j or start of window j+1
            best = None
            if j >= 0 and t - self.we[j] <= SNAP_S:
                best = self.off[j] + (self.we[j] - self.ws[j])
            if j + 1 < len(self.ws) and self.ws[j + 1] - t <= SNAP_S:
                cand = self.off[j + 1]
                if best is None or (self.ws[j + 1] - t) < (t - self.we[j]):
                    best = cand
            if best is None and j < 0 and len(self.ws) and self.ws[0] - t <= SNAP_S:
                best = 0.0
            if best is not None:
                out[i] = best
        self.n_drop += int(np.isnan(out).sum())
        return out / 3600.0


def epoch(col: pl.Series) -> np.ndarray:
    return col.dt.epoch("us").to_numpy() / 1e6


# ============================================================================================ curves
def curve_from_events(ev: pl.DataFrame, clock: ActiveClock, agents: set | None = None, H: float | None = None,
                      init: dict | None = None, t0_h: float = 0.0) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Project-count curve and death table from host events (kinds birth/recruit/depart/expire/leave; to_repo for
    depart). agents: restrict to these agents (room curves). init: {agent: repo} carried labels at t0_h (NE42 variant).
    t0_h: the kickoff's active time (curve time = active - t0_h); events before t0_h only update the state.
    Returns (curve: t, N_h, N_p, N_p_m, K_eff, rho; deaths: t, repo, kind)."""
    if agents is not None:
        ev = ev.filter(pl.col("agent").is_in(list(agents)))
    ta = clock(epoch(ev["t"])) - t0_h
    ev = ev.with_columns(pl.Series("ta", ta)).filter(pl.col("ta").is_not_nan())
    H = H if H is not None else min(HORIZON_H, clock.total_h - t0_h)
    grid = np.arange(0.0, H + 1e-9, GRID_H)
    host: dict[int, str] = dict(init or {})
    cnt: dict[str, int] = {}
    for a, r in host.items():
        cnt[r] = cnt.get(r, 0) + 1
    finished: set[str] = set()
    rows, deaths = [], []
    gi = 0

    def snap(t):
        hs = [v for v in cnt.values() if v > 0]
        nh = sum(hs)
        alive = {r for r, v in cnt.items() if v > 0}
        npm = len(alive | finished)
        keff = (nh ** 2 / sum(v * v for v in hs)) if nh else 0.0
        rows.append((t, nh, len(alive), npm, keff, (len(alive) / nh) if nh else np.nan,
                     ((len(alive) - 1) / (nh - 1)) if nh >= 2 else np.nan))

    for kind, a, repo, to_repo, t in ev.select("kind", "agent", "repo", "to_repo", "ta").iter_rows():
        while gi < len(grid) and grid[gi] <= t:
            if grid[gi] >= 0:
                snap(grid[gi])
            gi += 1
        if t > H:
            break
        a = int(a)
        if kind in ("birth", "recruit"):
            cnt[repo] = cnt.get(repo, 0) + 1
            host[a] = repo
            finished.discard(repo)
        elif kind in ("depart", "expire", "leave"):
            if host.get(a) != repo:
                continue
            cnt[repo] = cnt.get(repo, 0) - 1
            del host[a]
            if cnt[repo] == 0 and t >= 0:
                if kind == "depart":
                    k = "merge" if cnt.get(to_repo, 0) > 0 else "hop_new"
                else:
                    k = "finish"
                    finished.add(repo)
                deaths.append((t, repo, k, a, to_repo))
    while gi < len(grid):
        snap(grid[gi])
        gi += 1
    cur = pl.DataFrame(rows, schema={"t": pl.Float64, "N_h": pl.Int32, "N_p": pl.Int32, "N_p_m": pl.Int32,
                                      "K_eff": pl.Float64, "rho": pl.Float64, "dw": pl.Float64}, orient="row")
    de = pl.DataFrame(deaths, schema={"t": pl.Float64, "repo": pl.String, "kind": pl.String, "agent": pl.Int16,
                                      "to_repo": pl.String}, orient="row")
    return cur, de


# ============================================================================================ fits
def _bic(rss_mean, k, n_eff):
    rss_mean = max(rss_mean, 1e-6)
    return n_eff * np.log(rss_mean) + k * np.log(n_eff)


def _pow(t, A, alpha):
    return A * t ** (-alpha)


def _powoff(t, Ninf, A, alpha):
    return Ninf + A * t ** (-alpha)


def _exp(t, Ninf, N0, tau):
    return Ninf + (N0 - Ninf) * np.exp(-t / tau)


def fit_shapes(t: np.ndarray, y: np.ndarray, t_pk: float) -> dict:
    """Four (+1) shape fits on the fit window; t, y already restricted to [t_pk, H]."""
    tau = t - t_pk + GRID_H
    n_eff = max(4.0, round(t[-1] - t[0]))
    out = {}
    m = float(y.mean())
    out["constant"] = {"rss": float(np.mean((y - m) ** 2)), "k": 1, "par": {"N": m}}
    # step: grid search over t_s
    best = None
    for i in range(1, len(y)):
        a, b = y[:i].mean(), y[i:].mean()
        r = float(np.mean(np.concatenate([(y[:i] - a) ** 2, (y[i:] - b) ** 2])))
        if best is None or r < best[0]:
            best = (r, float(t[i] - t_pk), float(a), float(b))
    out["step"] = {"rss": best[0], "k": 3, "par": {"t_s": best[1], "N0": best[2], "Ninf": best[3]}}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            p, _ = curve_fit(_exp, tau, y, p0=[y[-1], y[0], 2.0], bounds=([0, 0, 0.05], [200, 400, 200]), maxfev=4000)
            out["exponential"] = {"rss": float(np.mean((y - _exp(tau, *p)) ** 2)), "k": 3,
                                  "par": {"Ninf": p[0], "N0": p[1], "tau": p[2]}}
        except Exception:
            out["exponential"] = {"rss": np.inf, "k": 3, "par": {}}
        try:
            p, _ = curve_fit(_pow, tau, y, p0=[max(y[0], 1.0), 0.3], bounds=([0.01, -2.0], [500, 5.0]), maxfev=4000)
            out["power"] = {"rss": float(np.mean((y - _pow(tau, *p)) ** 2)), "k": 2, "par": {"A": p[0], "alpha": p[1]}}
        except Exception:
            out["power"] = {"rss": np.inf, "k": 2, "par": {}}
        try:
            p, _ = curve_fit(_powoff, tau, y, p0=[y[-1], max(y[0] - y[-1], 0.5), 0.5],
                             bounds=([0, 0, 0.0], [200, 500, 5.0]), maxfev=4000)
            out["power_offset"] = {"rss": float(np.mean((y - _powoff(tau, *p)) ** 2)), "k": 3,
                                   "par": {"Ninf": p[0], "A": p[1], "alpha": p[2]}}
        except Exception:
            out["power_offset"] = {"rss": np.inf, "k": 3, "par": {}}
    for k, v in out.items():
        v["bic"] = float(_bic(v["rss"], v["k"], n_eff)) if np.isfinite(v["rss"]) else np.inf
    main = ["constant", "step", "exponential", "power"]
    sel = min(main, key=lambda k: out[k]["bic"])
    return {"fits": out, "selected": sel, "n_eff": n_eff,
            "dBIC_exp_minus_pow": float(out["exponential"]["bic"] - out["power"]["bic"])}


def alpha_ci(t, y, t_pk, n_boot=500, block_h=2.0, rng=None):
    """2-h moving-block residual bootstrap of the power-law alpha."""
    rng = rng or np.random.default_rng(0)
    tau = t - t_pk + GRID_H
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            p, _ = curve_fit(_pow, tau, y, p0=[max(y[0], 1.0), 0.3], bounds=([0.01, -2.0], [500, 5.0]), maxfev=4000)
        except Exception:
            return (np.nan, np.nan, np.nan)
        fit = _pow(tau, *p)
        res = y - fit
        L = max(1, int(round(block_h / GRID_H)))
        n = len(y)
        al = []
        for _ in range(n_boot):
            idx = []
            while len(idx) < n:
                s = rng.integers(0, max(1, n - L + 1))
                idx.extend(range(s, min(s + L, n)))
            yb = fit + res[np.array(idx[:n])]
            try:
                pb, _ = curve_fit(_pow, tau, yb, p0=p, bounds=([0.01, -2.0], [500, 5.0]), maxfev=2000)
                al.append(pb[1])
            except Exception:
                pass
    if len(al) < 20:
        return (float(p[1]), np.nan, np.nan)
    return (float(p[1]), float(np.percentile(al, 2.5)), float(np.percentile(al, 97.5)))


def curve_stats(cur: pl.DataFrame, deaths: pl.DataFrame | None = None, col: str = "N_p", boot: int = 0,
                rng=None) -> dict:
    H = float(cur["t"].to_numpy()[-1])
    cur = cur.filter(pl.col(col).is_not_nan() & pl.col(col).is_not_null())
    if cur.height < 8:
        return {"testable": False, "why": "fewer than 8 grid points", "class": None}
    t = cur["t"].to_numpy()
    y = cur[col].to_numpy().astype(float)
    pk_mask = t <= PEAK_WINDOW_H
    if not pk_mask.any():
        return {"testable": False, "why": "no hosts in the first 8 h", "class": None}
    if np.nanmax(y[pk_mask]) <= 0 and np.nanmax(y) <= 0:   # dw == 0 throughout: one project from the start
        npk = float(cur["N_p"].to_numpy()[pk_mask].max()); nhpk = int(cur["N_h"].to_numpy()[pk_mask].max())
        return {"testable": bool(nhpk >= 6 and H >= 10), "alpha_fit_ok": False, "H": H, "t_pk": float(t[0]), "N_pk": 0.0,
                "N_h_pk": nhpk, "N_inf": 0.0, "tol": 0.0, "t_f": float(t[0]), "t_f_censored": False, "R_d": 1.0,
                "A_u": 0.0, "selected": "constant", "alpha": None, "alpha_off": None, "tau_exp": None,
                "dBIC_exp_minus_pow": None, "bic": None, "class": "freeze", "c_m": np.nan, "one_project": True,
                "N_p_pk": npk}
    ipk = int(np.nanargmax(np.where(pk_mask, y, -1)))
    t_pk, N_pk = float(t[ipk]), float(y[ipk])
    nh_pk = int(cur["N_h"][ipk])
    last = t >= (1 - LAST_FRAC) * H
    N_inf = float(np.median(y[last]))
    if col in ("rho", "keffr", "dw"):   # A1: densities; one domain's worth = 1 / (median hosts at the end [- 1 for dw])
        nh_end = float(np.median(cur["N_h"].to_numpy()[last]))
        tol = max(1.0 / max(nh_end - (1.0 if col == "dw" else 0.0), 1.0), TOL_FRAC * N_inf)
    else:
        tol = max(1.0, TOL_FRAC * N_inf)
    ok = np.abs(y - N_inf) <= tol
    # t_f: first index after which all ok
    bad = np.where(~ok)[0]
    i_f = 0 if len(bad) == 0 else bad[-1] + 1
    t_f = float(t[i_f]) if i_f < len(t) else np.nan
    censored = bool(np.isnan(t_f) or t_f > (1 - LAST_FRAC) * H)
    w = t >= t_pk
    tw, yw = t[w], y[w]
    sh = fit_shapes(tw, yw, t_pk) if len(tw) >= 8 else None
    span = (t >= t_pk) & (t <= t_pk + AU_SPAN_H)
    if N_pk > N_inf:
        u = (y[span] - N_inf) / (N_pk - N_inf)
        A_u = float(np.sum(u) * GRID_H)
    else:
        A_u = 0.0
    if col in ("rho", "keffr", "dw"):   # testability is judged on the count itself (card rule)
        npk = float(cur["N_p"].to_numpy()[t <= PEAK_WINDOW_H].max())
        nhpk = int(cur["N_h"].to_numpy()[t <= PEAK_WINDOW_H].max())
    else:
        npk, nhpk = N_pk, nh_pk
    out = {"testable": bool(nhpk >= 6 and H >= 10), "alpha_fit_ok": bool(npk >= 4), "N_p_pk": npk, "H": H, "t_pk": t_pk, "N_pk": N_pk,
           "N_h_pk": nh_pk, "N_inf": N_inf, "tol": tol, "t_f": t_f, "t_f_censored": censored, "R_d": N_pk / max(N_inf, 1e-9),
           "A_u": A_u, "selected": sh["selected"] if sh else None,
           "alpha": sh["fits"]["power"]["par"].get("alpha") if sh else None,
           "alpha_off": sh["fits"]["power_offset"]["par"].get("alpha") if sh else None,
           "tau_exp": sh["fits"]["exponential"]["par"].get("tau") if sh else None,
           "dBIC_exp_minus_pow": sh["dBIC_exp_minus_pow"] if sh else None,
           "bic": {k: v["bic"] for k, v in sh["fits"].items()} if sh else None}
    frozen = (not censored) and t_f <= FREEZE_H and out["selected"] != "power"   # A1: no power-law stretch
    slow = censored or t_f > FREEZE_H
    out["class"] = "freeze" if frozen else ("slow" if slow else "fast_other")
    if boot and sh:
        a, lo, hi = alpha_ci(tw, yw, t_pk, n_boot=boot, rng=rng)
        out["alpha_ci"] = [lo, hi]
    if deaths is not None:
        dw = deaths.filter(pl.col("t") >= t_pk)
        n = dw.height
        km = {k: int(dw.filter(pl.col("kind") == k).height) for k in ("merge", "hop_new", "finish")}
        out["deaths"] = km
        out["c_m"] = km["merge"] / n if n else np.nan
    return out


def verdict_free(s: dict, alpha_ok: bool | None) -> str:
    if not s.get("testable"):
        return "descriptive"
    if s["class"] == "freeze":
        return "failed"
    if s["class"] == "slow" and s["selected"] == "power" and (alpha_ok is None or alpha_ok):
        return "supported"
    if s["class"] == "slow":
        return "mixed"
    return "mixed"


def verdict_named(s: dict) -> str:
    if not s.get("testable"):
        return "descriptive"
    if s["class"] == "freeze":
        return "supported"
    if s["selected"] == "power" and (s["t_f_censored"] or s["t_f"] > FREEZE_H):
        return "failed"
    return "mixed"


# ============================================================================================ skeleton + synthetic
def skeleton(goal_no: int):
    """Real skeleton for the synthetic: the period's commits (agent, t, pt_date) with their 30-min window id, calls,
    leave times, days and the clock. No repo names are used by the generator."""
    days = RH.period_days(goal_no)
    calls = RH.load_calls(goal_no, days)
    commits = RH.load_commits(goal_no, days)
    leave = RH.leave_times(goal_no, calls, days)
    cal = RH.calendar().select("pt_date", "win_start")
    c = commits.join(cal, on="pt_date", how="inner").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (30 * 60)).clip(lower_bound=0).cast(pl.Int32).alias("win"))
    wins = (c.group_by("agent", "pt_date", "win").agg(pl.col("t").min().alias("t0")).sort("t0"))
    return {"goal_no": goal_no, "days": days, "calls": calls, "commits": c.drop("win_start"), "wins": wins,
            "leave": leave, "clock": ActiveClock(days)}


def simulate_labels(sk: dict, world: str, rng: np.random.Generator) -> dict:
    """Synthetic repo label per (agent, pt_date, win) under a kinetic Potts quench world."""
    wins = sk["wins"]
    clock = sk["clock"]
    ta = clock(epoch(wins["t0"]))
    agents = sorted(set(wins["agent"].to_list()))
    cur: dict[int, str] = {}
    nxt = [0]

    def new():
        nxt[0] += 1
        return f"s{nxt[0]}"

    target_shared = "T"
    target_own = {a: f"T{a}" for a in agents}
    end_t: dict[str, float] = {}
    born_t: dict[str, float] = {}
    bJ = {"Q0": 4.0, "Q0w": 2.0, "Q1": 4.0, "Q2": 4.0, "Q3": 0.0}[world]
    b_own = 2.0
    lab = {}
    for (a, d, w), t in zip(wins.select("agent", "pt_date", "win").iter_rows(), ta):
        a = int(a)
        t = 0.0 if np.isnan(t) else float(t)
        a_new = -4.0 if t >= 2.0 else -2.0 * t
        if world == "Q3":
            r = cur.get(a)
            if r is None or t >= end_t.get(r, np.inf):
                r = new()
                born_t[r] = t
                end_t[r] = t + rng.exponential(4.0)
            cur[a] = r
            lab[(a, d, w)] = r
            continue
        if a not in cur and world in ("Q0", "Q0w"):
            r = new()
            cur[a] = r
            lab[(a, d, w)] = r
            continue
        others = [v for k, v in cur.items() if k != a]
        n_o = max(len(others), 1)
        opts = sorted(set(others) | ({cur[a]} if a in cur else set()))
        if world == "Q1":
            opts = sorted(set(opts) | {target_shared})
        if world == "Q2":
            opts = sorted(set(opts) | {target_own[a]})
        u = []
        for r in opts:
            s = sum(1 for v in others if v == r) / n_o
            x = bJ * s + (b_own if cur.get(a) == r else 0.0)
            if world == "Q1" and r == target_shared:
                x += 6.0
            if world == "Q2" and r == target_own[a]:
                x += 6.0
            u.append(x)
        opts.append("__new")
        u.append(a_new)
        u = np.array(u)
        p = np.exp(u - u.max())
        p /= p.sum()
        r = opts[rng.choice(len(opts), p=p)]
        if r == "__new":
            r = new()
        cur[a] = r
        lab[(a, d, w)] = r
    return lab


def synthetic_events(sk: dict, lab: dict) -> pl.DataFrame:
    c = sk["commits"]
    keys = list(zip(c["agent"].to_list(), c["pt_date"].to_list(), c["win"].to_list()))
    repo = [lab[(int(a), d, w)] for a, d, w in keys]
    sc = c.with_columns(pl.Series("repo", repo)).select("agent", "repo", "t", "pt_date")
    labels = RH.window_labels(sc, 30)
    return RH.classify_arrivals(RH.replay_events(labels, sk["calls"], E=100, leave_t=sk["leave"]))


def real_events(goal_no: int, tag: bool = True, allow_holdout: bool = False) -> dict:
    """Shared host replay of one period (non-holdout days unless allow_holdout, which only confirm.py sets), with
    arrival tags when tag=True."""
    if tag:
        d = RH.build_period(goal_no, allow_holdout=allow_holdout)
        return {"events": d["events"], "days": d["days"], "calls": d["calls"]}
    days = RH.period_days(goal_no, allow_holdout)
    calls = RH.load_calls(goal_no, days)
    commits = RH.load_commits(goal_no, days)
    leave = RH.leave_times(goal_no, calls, days)
    lab = RH.window_labels(commits, 30)
    ev = RH.classify_arrivals(RH.replay_events(lab, calls, E=100, leave_t=leave))
    return {"events": ev, "days": days, "calls": calls}
