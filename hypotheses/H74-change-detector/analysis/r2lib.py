"""H74 round 2 helpers (card: "Round 2 (2026-10-05)"): heavy-tailed baselines, leave-one-period-out (LOPO) conformal
thresholds, alarm evaluation at a fixed false-alarm rate, the format presence/retirement rule and a family DiD.

Round 1 code (h74lib.py) is unchanged; this module only adds functions, so round 1 reproduces exactly.
"""
from __future__ import annotations

import math

import numpy as np
import polars as pl

ALPHA = 0.02          # target per-day FAR per channel
B_Q, BMIN_Q = 30, 10  # empirical-quantile baseline (R3, primary)
B_G, BMIN_G = 10, 5   # Gaussian trailing z (round 1 and variant L)

# D counters (R1): transform and floors per score type
D2_FEATURES = ["n_bookends", "n_nudges", "n_human", "documented_hours", "window_min", "js_share"]
TRANSFORM = {"n_bookends": "log1p", "n_nudges": "log1p", "n_human": "log1p", "window_min": "log",
             "documented_hours": None, "js_share": None}
FLOOR_LQ = {"n_bookends": 0.1, "n_nudges": 0.1, "n_human": 0.1, "window_min": 0.1, "documented_hours": 0.5,
            "js_share": 0.01}


def transform(name: str, x: np.ndarray) -> np.ndarray:
    t = TRANSFORM.get(name)
    x = np.asarray(x, float)
    if t == "log1p":
        return np.log1p(np.clip(x, 0, None))
    if t == "log":
        return np.log(np.clip(x, 1e-3, None))
    if t == "logit":
        p = np.clip(x, 1e-3, 1 - 1e-3)
        return np.log(p / (1 - p))
    return x


# ------------------------------------------------------------------------------------------------ baselines
def _consistency(k: int, reps: int = 20000, seed: int = 7) -> float:
    rng = np.random.default_rng(seed)
    x = np.sort(rng.normal(size=(reps, k)), axis=1)[:, 1:-1]
    return float(x.std(axis=1, ddof=1).mean())


C_K = {k: _consistency(k) for k in range(BMIN_G, B_G + 1)}


def gauss_z(x: np.ndarray, floor: float) -> np.ndarray:
    """Signed robust trailing z (round 1's rule: previous <= 10 non-missing values, trimmed SD / c_k, floor)."""
    z = np.full(x.size, np.nan)
    hist: list[float] = []
    for t in range(x.size):
        if np.isfinite(x[t]) and len(hist) >= BMIN_G:
            b = np.array(hist[-B_G:])
            sd = np.sort(b)[1:-1].std(ddof=1) / C_K[len(b)]
            z[t] = (x[t] - np.median(b)) / max(sd, floor)
        if np.isfinite(x[t]):
            hist.append(float(x[t]))
    return z


def quant_e(x: np.ndarray, floor: float, B: int = B_Q, bmin: int = BMIN_Q) -> np.ndarray:
    """Signed empirical-quantile exceedance against the previous <= B non-missing values (>= bmin):
    e = (x - Q50)/(Q90 - Q50) above the median, -(Q50 - x)/(Q50 - Q10) below; denominators floored."""
    e = np.full(x.size, np.nan)
    hist: list[float] = []
    for t in range(x.size):
        if np.isfinite(x[t]) and len(hist) >= bmin:
            b = np.array(hist[-B:])
            q10, q50, q90 = np.quantile(b, [0.1, 0.5, 0.9])
            if x[t] >= q50:
                e[t] = (x[t] - q50) / max(q90 - q50, floor)
            else:
                e[t] = -(q50 - x[t]) / max(q50 - q10, floor)
        if np.isfinite(x[t]):
            hist.append(float(x[t]))
    return e


def feature_scores(raw: dict[str, np.ndarray], kind: str, floors_g: dict | None = None) -> dict[str, np.ndarray]:
    """|score| per feature for score type G (raw, Gaussian, round-1 floors), L (transformed, Gaussian) or Q."""
    out = {}
    for f, x in raw.items():
        if kind == "G":
            out[f] = np.abs(gauss_z(np.asarray(x, float), (floors_g or {}).get(f, 0.05)))
        elif kind == "L":
            out[f] = np.abs(gauss_z(transform(f, x), FLOOR_LQ.get(f, 0.1)))
        elif kind == "Q":
            out[f] = np.abs(quant_e(transform(f, x), FLOOR_LQ.get(f, 0.1)))
        else:
            raise ValueError(kind)
    return out


def nanmax_stack(d: dict[str, np.ndarray]) -> tuple[np.ndarray, list]:
    names = list(d)
    Z = np.vstack([d[k] for k in names])
    allnan = np.all(np.isnan(Z), 0)
    with np.errstate(all="ignore"):
        m = np.where(allnan, np.nan, np.nanmax(np.where(np.isnan(Z), -np.inf, Z), 0))
        arg = np.argmax(np.where(np.isnan(Z), -np.inf, Z), 0)
    return m, [None if a else names[k] for k, a in zip(arg, allnan)]


# ------------------------------------------------------------------------------------------------ calibration
def conformal_threshold(train: np.ndarray, alpha: float = ALPHA) -> float:
    """The ceil((1-alpha)(n+1))-th smallest training score; +inf if that rank exceeds n. Alarm iff score > threshold."""
    t = np.sort(train[np.isfinite(train)])
    n = t.size
    k = math.ceil((1 - alpha) * (n + 1))
    return float("inf") if k > n or n == 0 else float(t[k - 1])


def lopo_thresholds(score: np.ndarray, period: np.ndarray, placebo: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    """Per-day threshold calibrated on the placebo days of all other goal periods."""
    th = np.full(score.size, np.nan)
    cache = {}
    for g in np.unique(period):
        if g not in cache:
            cache[g] = conformal_threshold(score[placebo & (period != g)], alpha)
        th[period == g] = cache[g]
    return th


def lopo_alarm(score: np.ndarray, period: np.ndarray, placebo: np.ndarray, alpha: float = ALPHA):
    th = lopo_thresholds(score, period, placebo, alpha)
    with np.errstate(invalid="ignore"):
        return np.where(np.isfinite(score), score > th, False), th


# ------------------------------------------------------------------------------------------------ evaluation
def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


class Frame:
    """Day skeleton for evaluation: scored days, calendar positions, placebo pools, regimes, events."""

    def __init__(self, days: pl.DataFrame, cal_days: list[str], events: pl.DataFrame):
        self.days = days
        self.dl = days["pt_date"].to_list()
        self.T = len(self.dl)
        self.cal_days = cal_days
        self.cal_pos = {d: i for i, d in enumerate(cal_days)}
        self.day_pos = {d: i for i, d in enumerate(self.dl)}
        self.cpos = np.array([self.cal_pos[d] for d in self.dl])
        self.period = days["goal_no"].to_numpy().astype(int)
        self.regime = np.array(days["regime"].to_list())
        self.monday = (days["weekday"].to_numpy() == 1)
        self.events = events
        cent = np.array(sorted({self.cal_pos[d] for d in events["day0"].drop_nulls().to_list() if d in self.cal_pos}))
        dist = np.min(np.abs(self.cpos[:, None] - cent[None, :]), 1)
        self.dist = dist
        elig = days["has_baseline"].to_numpy() & ~days["gap_return"].to_numpy()
        self.eligible = elig
        self.P2 = elig & (dist >= 2)
        self.P3 = elig & (dist >= 3)
        self.ev = events.filter(~pl.col("held0") & pl.col("day0").is_in(self.dl))
        # day index -> calendar-window neighbours (scored days only)
        self.nbr = [[self.day_pos[self.cal_days[c + o]] for o in (-1, 0, 1)
                     if 0 <= c + o < len(cal_days) and self.cal_days[c + o] in self.day_pos] for c in self.cpos]

    def window_any(self, alarm: np.ndarray) -> np.ndarray:
        return np.array([bool(np.any(alarm[n])) for n in self.nbr])

    def class_hits(self, alarm: np.ndarray, cls_list, rng=None, n_rand: int = 2000, label_map=None) -> dict:
        """Hit (any alarm on day -1..+1) per class; random-date p (same regime, eligible days)."""
        w = self.window_any(alarm)
        pools = {r: np.where(self.eligible & (self.regime == r))[0] for r in np.unique(self.regime)}
        out = {}
        for cls in cls_list:
            names = label_map.get(cls, [cls]) if label_map else [cls]
            e = self.ev.filter(pl.col("cls").is_in(names))
            if e.height == 0:
                continue
            idx = np.array([self.day_pos[d] for d in e["day0"].to_list()])
            hits = w[idx]
            h = float(hits.mean())
            r = {"n": int(idx.size), "k": int(hits.sum()), "hit": h, "ci": list(wilson(int(hits.sum()), int(idx.size))),
                 "events": [{"event": a, "day0": d, "cls": c, "label": lab[:80], "hit": bool(x)}
                            for a, d, c, lab, x in zip(e["event"].to_list(), e["day0"].to_list(), e["cls"].to_list(),
                                                       e["label"].to_list(), hits)]}
            if rng is not None:
                regs = self.regime[idx]
                draws = np.column_stack([pools[g][rng.integers(0, pools[g].size, n_rand)] for g in regs])
                rh = w[draws].mean(1)
                r["p_rand"] = float((1 + np.sum(rh >= h)) / (1 + n_rand))
                r["rand_mean"] = float(rh.mean())
            out[cls] = r
        return out

    def far(self, alarm: np.ndarray) -> dict:
        w = self.window_any(alarm)
        res = {}
        for nm, pool in (("P2", self.P2), ("P3", self.P3)):
            k, n = int(alarm[pool].sum()), int(pool.sum())
            km, nm_ = int(alarm[pool & self.monday].sum()), int((pool & self.monday).sum())
            res[nm] = {"k": k, "n": n, "per_day": k / n if n else None, "ci": list(wilson(k, n)),
                       "monday": [km, nm_], "other": [k - km, n - nm_]}
        res["P3"]["window"] = float(w[self.P3].mean())
        res["n_alarm_days"] = int(alarm.sum())
        return res


# ------------------------------------------------------------------------------------------------ presence rule (R2)
def presence_retire(n: np.ndarray, k: np.ndarray, need_present: int = 8, look: int = 10, pmax: float = 0.01,
                    nmin: int = 3) -> np.ndarray:
    """Retirement alarms for one marker over scored days. n: answers per day, k: answers with the marker.
    Alarm on day t (n[t] >= nmin) if the marker was present on >= need_present of the previous `look` scored days,
    k[t] == 0, (1 - s)^n[t] <= pmax with s the pooled baseline share, and the previous scored day was not already an
    absence alarm or absence (first day of an absence only)."""
    sc = np.where(n >= nmin)[0]
    out = np.zeros(n.size, bool)
    for j, t in enumerate(sc):
        if j < look:
            continue
        prev = sc[j - look:j]
        pres = (k[prev] > 0).sum()
        if pres < need_present or k[t] > 0 or k[sc[j - 1]] == 0:
            continue
        s = k[prev].sum() / max(n[prev].sum(), 1)
        if (1 - s) ** n[t] <= pmax:
            out[t] = True
    return out


def presence_appear(n: np.ndarray, k: np.ndarray, kag: np.ndarray, max_present: int = 2, look: int = 10,
                    kmin: int = 3, agmin: int = 2, nmin: int = 3) -> np.ndarray:
    sc = np.where(n >= nmin)[0]
    out = np.zeros(n.size, bool)
    for j, t in enumerate(sc):
        if j < look:
            continue
        prev = sc[j - look:j]
        if (k[prev] > 0).sum() <= max_present and k[t] >= kmin and kag[t] >= agmin and k[sc[j - 1]] < kmin:
            out[t] = True
    return out


def presence_retire_acc(n: np.ndarray, k: np.ndarray, rho: float, need_present: int = 8, look: int = 10,
                        pcum: float = 1e-3, nmin: int = 3) -> np.ndarray:
    """Amendment R2-A1 (after the synthetic study, before real data): retirement evidence accumulates over
    consecutive absent scored days. At the first absent day after a present day, the baseline must show the marker on
    >= need_present of the previous `look` scored days; the pooled share s is then frozen. Each absent day adds
    log P(0 | n_t; beta-binomial with share s and intra-day correlation rho). Alarm on the first day the sum is
    <= log(pcum); the run resets when the marker reappears."""
    from scipy.special import betaln
    kap = 1.0 / max(rho, 1e-6) - 1.0
    sc = np.where(n >= nmin)[0]
    out = np.zeros(n.size, bool)
    run = None  # (a, b, logp, fired)
    for j, t in enumerate(sc):
        if k[t] > 0:
            run = None
            continue
        if run is None:
            if j < look:
                continue
            prev = sc[j - look:j]
            if (k[prev] > 0).sum() < need_present or k[sc[j - 1]] == 0:
                continue
            s = k[prev].sum() / max(n[prev].sum(), 1)
            run = [s * kap, (1 - s) * kap, 0.0, False]
        a, b = run[0], run[1]
        run[2] += betaln(a, b + n[t]) - betaln(a, b)
        if not run[3] and run[2] <= np.log(pcum):
            out[t] = True
            run[3] = True
    return out


def persist2(x: np.ndarray) -> np.ndarray:
    """Two-day persistence score dated on the second day: p(t) = min(x(t-1), x(t)) over consecutive scored days."""
    out = np.full(x.size, np.nan)
    out[1:] = np.fmin(x[:-1], x[1:])
    out[1:][np.isnan(x[:-1]) | np.isnan(x[1:])] = np.nan
    return out


# Amendment R2-A1: the monitor's D channel (counters only, log + Gaussian trailing z, two-day persistence)
D3_FEATURES = ["n_bookends", "n_nudges", "n_human"]
STALL_FEATURES = ["documented_hours", "window_min", "js_share"]


def d3_channel(raw: dict[str, np.ndarray]) -> tuple[np.ndarray, list, dict]:
    fs = feature_scores({f: raw[f] for f in D3_FEATURES}, "L")
    ps = {f: persist2(v) for f, v in fs.items()}
    D, arg = nanmax_stack(ps)
    return D, arg, ps
