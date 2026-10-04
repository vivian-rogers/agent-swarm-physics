"""H42 engine: multivariate Hawkes fits with read-out kernels on the recipient's call clock.

One realization = one (unit, village day); agent i is at risk on its span [first call start, last call end] minus masked
village-off gaps. Intensity (H03's B2a baseline and fixed-timescale grids; all amplitudes >= 0):

  lambda_i(t) = c_{i,d} s_{b(t)} + sum_k w_k F_k,i(t)

Columns F_k are built once per unit and channel; a spec is a subset of columns. Because every kernel timescale is fixed,
lambda is linear in w, so the fit is H03's L-BFGS-B in log space with analytic gradients.

TALK columns (events = agent chat messages):
  kick_*   goal-kickoff bump (first goal day), tau 20 min / 2 h
  hum_*, aut_*  human / automated (nudge + bookend) items read by i, exponential from the read-out call start, 2/10/60 min
  own      own call clock: pulse f_i(t - c_k*) after i's latest receiving call start (log-normal talk delay of agent i)
  self_*   i's own previous messages, exp grid 10..3000 s
  A_*      exponential from posting time s, room-aware ledger pairs (fast grid 10..300 s)       [spec A]
  H_*      same kernel, room-blind: every message by any other agent that day (H03's M3 set)  [spec A_H03]
  Ag_*     f_i(t - c_k*) * sum_{read items, s < c_k*} exp(-(c_k* - s)/tau): wall-clock decay since arrival, at calls [A_g]
  B_b      f_i(t - c_k*) * (1/M_b) * #items read at calls k* - m, m in call-index bin b             [spec B]
  Bt_*     exponential from the read-out call start r (fast grid)                                    [spec B_t]
ACTIVITY columns (events = call records t_first): kick, hum/aut (onset after the read-out call's record), self_* and
  wake_* (own calls / own wake calls, 10..1000 s), Av_*/Ai_* (visible messages / invisible non-talk calls of others,
  from s) [A], Bv_*/Bi_* (onset after i's read-out / next call record) [B].
"""
from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import optimize, special  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H42-readout-hawkes-kernel"

# H03's C recursions, imported read-only under a unique module name (avoids sys.path collisions)
_spec = importlib.util.spec_from_file_location(
    "h03_hawkes_core", ROOT / "hypotheses/H03-self-excited-criticality/analysis/hawkes_core.py")
hc03 = importlib.util.module_from_spec(_spec)
import sys as _sys  # noqa: E402
_sys.modules["h03_hawkes_core"] = hc03
_spec.loader.exec_module(hc03)

BIN_S = 1800.0
KICK_TAUS = (1200.0, 7200.0)
EXO_TAUS = (120.0, 600.0, 3600.0)
SELF_TAUS = (10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0)
ACT_SELF_TAUS = (10.0, 30.0, 100.0, 300.0, 1000.0)
CROSS_TAUS = (10.0, 30.0, 100.0, 300.0)
B_BINS = ((0, 0), (1, 1), (2, 3), (4, 7), (8, 15))
EPS = 1e-3

# ----------------------------------------------------------------------------------------------- C helper (weighted)
_C = r"""
#include <math.h>
#include <limits.h>
/* X_i = sum_{j: gx_j == g_i, x_j < t_i} w_j exp(-beta (t_i - x_j)); events sorted by (g,t), sources by (gx,x) */
void wexp_sums(long n, const double* t, const long* g, long m, const double* x, const long* gx, const double* w,
               double beta, double* X) {
  long j = 0; double s = 0.0, tref = 0.0; int have = 0; long gcur = LONG_MIN;
  for (long i = 0; i < n; i++) {
    if (g[i] != gcur) { gcur = g[i]; s = 0.0; have = 0; while (j < m && gx[j] < gcur) j++; }
    while (j < m && gx[j] == gcur && x[j] < t[i]) {
      if (have) s *= exp(-beta * (x[j] - tref));
      s += w[j]; tref = x[j]; have = 1; j++;
    }
    X[i] = have ? s * exp(-beta * (t[i] - tref)) : 0.0;
  }
}
"""
_LIB = None


def _lib():
    global _LIB
    if _LIB is None:
        h = hashlib.sha1(_C.encode()).hexdigest()[:10]
        bdir = HERE / "_build"
        bdir.mkdir(exist_ok=True)
        so = bdir / f"h42_{h}.so"
        if not so.exists():
            src = bdir / f"h42_{h}.c"
            src.write_text(_C)
            subprocess.run(["cc", "-O3", "-shared", "-fPIC", "-o", str(so), str(src)], check=True)
        lib = ctypes.CDLL(str(so))
        dp = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
        lp = np.ctypeslib.ndpointer(dtype=np.int64, flags="C_CONTIGUOUS")
        lib.wexp_sums.argtypes = [ctypes.c_long, dp, lp, ctypes.c_long, dp, lp, dp, ctypes.c_double, dp]
        _LIB = lib
    return _LIB


def wexp(t, g, x, gx, w, beta):
    """sum_{x<t, same group} w e^{-beta(t-x)} at each event; inputs need not be sorted (sorted internally)."""
    n = len(t)
    out = np.zeros(n)
    if n == 0 or len(x) == 0:
        return out
    oe = np.lexsort((t, g))
    os_ = np.lexsort((x, gx))
    X = np.empty(n)
    _lib().wexp_sums(n, np.ascontiguousarray(t[oe], np.float64), np.ascontiguousarray(g[oe], np.int64), len(x),
                     np.ascontiguousarray(x[os_], np.float64), np.ascontiguousarray(gx[os_], np.int64),
                     np.ascontiguousarray(w[os_], np.float64), float(beta), X)
    out[oe] = X
    return out


def exp_comp(u, a, b, beta):
    """integral over [a, b] of beta e^{-beta (t - u)} 1[t > u]."""
    lo = np.maximum(u, a)
    return np.where(u < b, np.exp(-beta * (lo - u)) - np.exp(-beta * np.maximum(b - u, 0.0)), 0.0)


# ----------------------------------------------------------------------------------------------- data
@dataclass
class Unit:
    unit_id: str
    goal: int
    regime: str
    days: pl.DataFrame
    calls: pl.DataFrame
    talk: pl.DataFrame
    items: pl.DataFrame
    mask: pl.DataFrame
    spans: pl.DataFrame = None

    @property
    def n_days(self):
        return len(self.days)


def load_unit(unit_id: str, goal: int | None = None, root: Path | None = None) -> Unit:
    if goal is None:
        goal = int("".join(ch for ch in unit_id if ch.isdigit()))
    g = (DATA if root is None else root) / f"G{goal:02d}"
    f = pl.col("unit_id") == unit_id
    days = pl.read_parquet(g / "days.parquet").filter(f).sort("day")
    calls = pl.read_parquet(g / "calls.parquet").filter(f)
    talk = pl.read_parquet(g / "talk.parquet").filter(f)
    items = pl.read_parquet(g / "items.parquet").filter(f)
    mask = pl.read_parquet(g / "mask.parquet").filter(f)
    u = Unit(unit_id, goal, days["regime"][0], days, calls, talk, items, mask)
    T = dict(zip(days["day"].to_list(), days["T"].to_list()))
    sp = (calls.group_by("day", "agent").agg(pl.col("t_call").min().alias("a"),
                                             pl.max_horizontal("t_end", "t_first").max().alias("b"))
          .with_columns(pl.col("a").clip(0.0), pl.struct("day", "b").map_elements(
              lambda r: min(r["b"], T[r["day"]]), return_dtype=pl.Float64).alias("b"))
          .filter(pl.col("b") > pl.col("a") + 60.0).sort("day", "agent"))
    u.spans = sp
    return u


def list_units() -> pl.DataFrame:
    """Non-holdout units with H42 extracts, with eligibility flags."""
    pa = pl.read_parquet(ROOT / "data/processed/shared/period_affordances.parquet").filter(~pl.col("holdout"))
    rows = []
    for r in pa.iter_rows(named=True):
        g = DATA / f"G{r['goal_no']:02d}"
        if not (g / "days.parquet").exists():
            continue
        t = pl.scan_parquet(g / "talk.parquet").filter(pl.col("unit_id") == r["unit_id"]).select(pl.len()).collect().item()
        c = pl.scan_parquet(g / "calls.parquet").filter(pl.col("unit_id") == r["unit_id"])
        na = c.select(pl.col("agent").n_unique()).collect().item()
        nc = c.select(pl.len()).collect().item()
        nd = pl.scan_parquet(g / "days.parquet").filter(pl.col("unit_id") == r["unit_id"]).select(pl.len()).collect().item()
        rows.append({"unit_id": r["unit_id"], "goal_no": r["goal_no"], "regime": r["regime"], "mode": r["mode"],
                     "n_days": nd, "n_agents": na, "n_talk": t, "n_calls": nc, "n_rooms": r["n_rooms"],
                     "eligible": (na >= 3) and (t >= 50), "cv": (na >= 3) and (t >= 50) and nd >= 2})
    return pl.DataFrame(rows)


# ----------------------------------------------------------------------------------------------- design
@dataclass
class Design:
    """Events x columns, per-day compensators, baseline units and exposures."""
    names: list
    F: np.ndarray            # n x K
    Zd: np.ndarray           # D x K compensator per day
    ev_day: np.ndarray       # n
    ev_unit: np.ndarray      # n (agent-day unit index)
    ev_bin: np.ndarray       # n
    L: np.ndarray            # U x Kb exposure (s)
    unit_day: np.ndarray     # U
    unit_agent: np.ndarray   # U
    D: int
    meta: dict = field(default_factory=dict)
    bw: np.ndarray = None   # per-event baseline weight (pulse value in the call-clock world)

    def cols(self, prefixes):
        return [k for k, nm in enumerate(self.names) if any(nm == p or nm.startswith(p + "_") for p in prefixes)]


def _spans_arrays(u: Unit, trim: float = 0.0):
    sp = u.spans
    key = {(d, a): k for k, (d, a) in enumerate(zip(sp["day"].to_list(), sp["agent"].to_list()))}
    a = sp["a"].to_numpy() + trim
    b = sp["b"].to_numpy() - trim
    return key, a, b


def _exposure(u: Unit, key, a, b):
    """U x Kb exposure of each agent-day span by 30-min bin, minus masked gaps."""
    Tmax = float(u.days["T"].max())
    Kb = int(np.ceil(Tmax / BIN_S)) + 1
    U = len(a)
    L = np.zeros((U, Kb))
    edges = BIN_S * np.arange(Kb + 1)
    mk = {d: (g["m0"].to_numpy(), g["m1"].to_numpy()) for (d,), g in u.mask.group_by(["day"])} if len(u.mask) else {}
    days = np.array([k[0] for k in key])
    for k in range(U):
        lo, hi = a[k], b[k]
        if hi <= lo:
            continue
        L[k] = np.clip(np.minimum(hi, edges[1:]) - np.maximum(lo, edges[:-1]), 0, None)
        if days[k] in mk:
            for m0, m1 in zip(*mk[days[k]]):
                L[k] -= np.clip(np.minimum(min(hi, m1), edges[1:]) - np.maximum(max(lo, m0), edges[:-1]), 0, None)
    return np.clip(L, 0, None), days


def _in_mask(u: Unit, day, t):
    out = np.zeros(len(t), bool)
    for (d,), g in (u.mask.group_by(["day"]) if len(u.mask) else []):
        sel = day == d
        m0, m1 = g["m0"].to_numpy(), g["m1"].to_numpy()
        k = np.searchsorted(m0, t[sel], side="right") - 1
        out[sel] = (k >= 0) & (t[sel] < m1[np.maximum(k, 0)])
    return out


class Grids:
    """Per (day, agent) receiving-call grids for read-out assignment and pulses."""

    def __init__(self, u: Unit, variant: str = "point"):
        col = {"point": "t_call", "lo": "t_lo", "hi": "t_hi"}[variant]
        rc = u.calls.filter(pl.col("recv")).sort("day", "agent", col)
        self.g = {}
        self.first = {}
        self.cls = {}
        self.rf = {}
        self.rc = {}
        for (d, a), grp in rc.group_by(["day", "agent"], maintain_order=True):
            tc = grp[col].to_numpy().astype(np.float64)
            tc = np.maximum.accumulate(tc)            # bounds can cross; keep the grid monotone
            self.g[(d, a)] = tc
            self.first[(d, a)] = grp["t_first"].to_numpy().astype(np.float64)
            # call class known before the call reads anything: {chat, cu} x {wake, other}
            self.cls[(d, a)] = (2 * (grp["ctx_mode"].to_numpy() == "cu") + grp["wake"].to_numpy()).astype(np.int64)
            self.rf[(d, a)] = grp["reset_forced"].to_numpy()
            self.rc[(d, a)] = (grp["reset_consol"].to_numpy() & ~grp["reset_forced"].to_numpy())
        allc = u.calls.sort("day", "agent", "t_call")
        self.all = {(d, a): (grp["t_call"].to_numpy(), grp["t_first"].to_numpy())
                    for (d, a), grp in allc.group_by(["day", "agent"], maintain_order=True)}

    def readout(self, day, rec, s):
        """index of the recipient's first receiving call with start > s (-1 if none), its start and its record time."""
        k = np.full(len(s), -1, np.int64)
        r = np.full(len(s), np.nan)
        rf = np.full(len(s), np.nan)
        df = pl.DataFrame({"d": day, "a": rec, "i": np.arange(len(s))})
        for (d, a), grp in df.group_by(["d", "a"]):
            g = self.g.get((d, a))
            if g is None:
                continue
            idx = grp["i"].to_numpy()
            kk = np.searchsorted(g, s[idx], side="right")
            ok = kk < len(g)
            k[idx[ok]] = kk[ok]
            r[idx[ok]] = g[kk[ok]]
            rf[idx[ok]] = self.first[(d, a)][kk[ok]]
        return k, r, rf


def lognorm_params(u: Unit, grids: Grids):
    """Per-agent log-normal talk delay (message time - its call start on the grid)."""
    out = {}
    pooled = []
    for (d, a), grp in u.talk.group_by(["day", "agent"]):
        g = grids.g.get((d, a))
        if g is None:
            continue
        t = grp["t"].to_numpy()
        k = np.searchsorted(g, t, side="right") - 1
        dl = t[k >= 0] - g[k[k >= 0]]
        out.setdefault(a, []).extend(np.log(np.maximum(dl, 0.5)).tolist())
        pooled.extend(np.log(np.maximum(dl, 0.5)).tolist())
    def par(v):
        v = np.asarray(v)
        mu = float(np.median(v))
        q = np.percentile(v, [25, 75])
        sig = float(np.clip((q[1] - q[0]) / 1.349, 0.3, 2.0))
        return mu, sig
    pp = par(pooled) if pooled else (np.log(9.0), 0.7)
    return {a: (par(v) if len(v) >= 5 else pp) for a, v in out.items()}, pp


def ln_pdf(x, mu, sig):
    x = np.maximum(x, 1e-9)
    return np.exp(-0.5 * ((np.log(x) - mu) / sig) ** 2) / (x * sig * np.sqrt(2 * np.pi))


def ln_cdf(x, mu, sig):
    x = np.maximum(x, 1e-9)
    return 0.5 * (1 + special.erf((np.log(x) - mu) / (sig * np.sqrt(2))))


def _base_design(u: Unit, ev_day, ev_agent, trim):
    key, a, b = _spans_arrays(u, trim)
    L, udays = _exposure(u, key, a, b)
    unit = np.array([key.get((d, ag), -1) for d, ag in zip(ev_day, ev_agent)], np.int64)
    return key, a, b, L, unit


PULSE_EPS = 0.05          # pulse = (1 - eps) log-normal(talk delay) + eps Exp(mean 120 s): robust to long tool calls
PULSE_TAIL = 120.0


def pulse_pdf(x, mu, sig):
    return (1 - PULSE_EPS) * ln_pdf(x, mu, sig) + PULSE_EPS * np.exp(-np.maximum(x, 0) / PULSE_TAIL) / PULSE_TAIL


def pulse_cdf(x, mu, sig):
    return (1 - PULSE_EPS) * ln_cdf(x, mu, sig) + PULSE_EPS * (1 - np.exp(-np.maximum(x, 0) / PULSE_TAIL))


def build_talk(u: Unit, world: str = "pr", variant: str = "point", trim: float = 0.0,
               items_override: pl.DataFrame | None = None, only_cross: bool = False, base: Design | None = None,
               specs=None, internals: bool = False) -> Design:
    """TALK design.

    world 'pr' (pre-registered): continuous baseline, continuous self/exo/kick, own call-clock pulse column; cross
                 families A, H, Ag, B, Bt.
    world 'A'  (amendment 1, H03 world): no call clock; continuous baseline, self, exo (from posting time), kick;
                 cross A, H, Bt.
    world 'B'  (amendment 1, call-clock world): baseline, self, exo and kick all expressed as pulses at i's calls
                 (lambda = f_i(t - c_k*) x [c s + gated terms]); cross B, Ag (gated) and A (continuous, hybrid C).
    items_override: agent items (day, recipient, sender, s) for nulls; read-outs recomputed with the same rule.
    """
    if specs is None:
        specs = {"pr": ("A", "H", "Ag", "B", "Bt"), "A": ("A", "H", "Bt"), "B": ("B", "Ag", "A")}[world]
    grids = Grids(u, variant)
    tk = u.talk.sort("day", "agent", "t")
    ev_day0 = tk["day"].to_numpy().astype(np.int64)
    ev_ag0 = tk["agent"].to_numpy().astype(np.int64)
    ev_t0 = tk["t"].to_numpy().astype(np.float64)
    key, a, b = _spans_arrays(u, trim)
    Lt, _ = _exposure(u, key, a, b)
    unit = np.array([key.get((d, x), -1) for d, x in zip(ev_day0, ev_ag0)], np.int64)
    keep = unit >= 0
    keep[keep] &= (ev_t0[keep] >= a[unit[keep]]) & (ev_t0[keep] <= b[unit[keep]])
    keep &= ~_in_mask(u, ev_day0, ev_t0)
    U = len(a)
    u_day = np.array([k[0] for k in key], np.int64)
    u_ag = np.array([k[1] for k in key], np.int64)
    gid = {(d, x): k for k, (d, x) in enumerate(zip(u_day, u_ag))}
    D = u.n_days
    lnp, lnpool = lognorm_params(u, grids)
    G = {}
    CLS = {}
    RF = {}
    for k in range(U):
        g = grids.g.get((u_day[k], u_ag[k]))
        if g is None or len(g) == 0:
            G[k] = None
            continue
        inr = (g >= a[k] - 1e-6) & (g <= b[k])
        gg = g[inr]
        if len(gg) == 0:
            G[k] = None
            continue
        e = np.minimum(np.append(gg[1:], np.inf), b[k])
        mu, sg = lnp.get(u_ag[k], lnpool)
        G[k] = (gg, e, pulse_cdf(np.maximum(e - gg, 0), mu, sg), mu, sg)
        CLS[k] = grids.cls[(u_day[k], u_ag[k])][inr]
        RF[k] = (grids.rf[(u_day[k], u_ag[k])][inr], grids.rc[(u_day[k], u_ag[k])][inr])
    # current call k* and pulse value of each event
    kst0 = np.full(len(ev_t0), -1, np.int64)
    pul0 = np.zeros(len(ev_t0))
    for k in range(U):
        if G[k] is None:
            continue
        sel = np.where((unit == k) & keep)[0]
        if len(sel) == 0:
            continue
        gg, e, Fm, mu, sg = G[k]
        ks = np.searchsorted(gg, ev_t0[sel], side="right") - 1
        ok = ks >= 0
        kst0[sel[ok]] = ks[ok]
        pul0[sel[ok]] = pulse_pdf(ev_t0[sel[ok]] - gg[ks[ok]], mu, sg)
    if world == "B":
        keep &= kst0 >= 0          # an event before the agent's first receiving call cannot be expressed
    ev_day, ev_ag, ev_t, ev_u = ev_day0[keep], ev_ag0[keep], ev_t0[keep], unit[keep]
    kstar, pulse = kst0[keep], pul0[keep]
    n = len(ev_t)
    g_ev = ev_day * 1000 + ev_ag
    cols, Zs, names = [], [], []

    def add(name, col, zday):
        names.append(name); cols.append(col); Zs.append(zday)

    def zsum(day_of_src, comp):
        return np.bincount(day_of_src, weights=comp, minlength=D)

    def gated(src_by_unit, tau, inclusive=False):
        """per event: pulse * sum_{x < c_k*} e^{-(c_k* - x)/tau}; per day: sum_k Fm_k * (same at c_k)."""
        col = np.zeros(n); z = np.zeros(D)
        for k, xs in src_by_unit.items():
            if G[k] is None or len(xs) == 0:
                continue
            gg, e, Fm, mu, sg = G[k]
            tq = gg + (1e-6 if inclusive else 0.0)
            Gk = wexp(tq, np.zeros(len(gg), np.int64), np.sort(xs), np.zeros(len(xs), np.int64), np.ones(len(xs)),
                      1 / tau)
            z[u_day[k]] += (Fm * Gk).sum()
            evs = np.where(ev_u == k)[0]
            col[evs] = pulse[evs] * Gk[kstar[evs]]
        return col, z

    # baseline: continuous (time exposure) or pulse-gated (pulse mass exposure)
    if world == "B":
        # baseline level per (agent-day, call class): exposure = pulse mass of that class's calls per 30-min bin
        Kb = Lt.shape[1]
        NC = 4
        Lb = np.zeros((U * NC, Kb))
        ev_cls = np.zeros(n, np.int64)
        for k in range(U):
            if G[k] is not None:
                gg, e, Fm, mu, sg = G[k]
                bins = np.minimum((gg // BIN_S).astype(np.int64), Kb - 1)
                for c_ in range(NC):
                    m_ = CLS[k] == c_
                    if m_.any():
                        Lb[k * NC + c_] = np.bincount(bins[m_], weights=Fm[m_], minlength=Kb)[:Kb]
                evs = np.where(ev_u == k)[0]
                ev_cls[evs] = CLS[k][kstar[evs]]
        L, bw = Lb, pulse.copy()
        base_unit = ev_u * NC + ev_cls
        base_day, base_ag = np.repeat(u_day, NC), np.repeat(u_ag, NC)
    else:
        L, bw = Lt, np.ones(n)
        base_unit, base_day, base_ag = ev_u, u_day, u_ag

    if not only_cross:
        fg = u.days.filter(pl.col("first_goal_day"))["day"].to_list()
        if fg:
            for tau in KICK_TAUS:
                if world == "B":
                    col = np.zeros(n); z = np.zeros(D)
                    for k in range(U):
                        if u_day[k] in fg and G[k] is not None:
                            gg, e, Fm, mu, sg = G[k]
                            z[u_day[k]] += (Fm * np.exp(-gg / tau)).sum()
                            evs = np.where(ev_u == k)[0]
                            col[evs] = pulse[evs] * np.exp(-gg[kstar[evs]] / tau)
                else:
                    col = np.where(np.isin(ev_day, fg), np.exp(-ev_t / tau), 0.0)
                    z = np.zeros(D)
                    for k in range(U):
                        if u_day[k] in fg:
                            z[u_day[k]] += tau * (np.exp(-a[k] / tau) - np.exp(-b[k] / tau))
                add(f"kick_{int(tau)}", col, z)
        ex = u.items.filter(pl.col("kind") != "agent")
        if len(ex):
            ed = ex["day"].to_numpy().astype(np.int64); er = ex["recipient"].to_numpy().astype(np.int64)
            es = ex["s"].to_numpy().astype(np.float64)
            k1, r, _ = grids.readout(ed, er, es)
            for fam, kinds in (("hum", ["human"]), ("aut", ["nudge", "pause_resume", "automated_other"])):
                sel = np.isin(ex["kind"].to_numpy(), kinds) & (k1 >= 0)
                uk = np.array([gid.get((d, x), -1) for d, x in zip(ed[sel], er[sel])], np.int64)
                okk = uk >= 0
                if okk.sum() == 0:
                    continue
                onset = (es if world == "A" else r)[sel][okk]
                ukk = uk[okk]
                gx = u_day[ukk] * 1000 + u_ag[ukk]
                for tau in EXO_TAUS:
                    bt = 1 / tau
                    if world == "B":
                        col, z = gated({k: onset[ukk == k] for k in np.unique(ukk)}, tau, inclusive=True)
                        add(f"{fam}_{int(tau)}", col, z)
                    else:
                        add(f"{fam}_{int(tau)}", bt * wexp(ev_t, g_ev, onset, gx, np.ones(len(onset)), bt),
                            zsum(u_day[ukk], exp_comp(onset, a[ukk], b[ukk], bt)))
        if world == "pr":
            z = np.zeros(D)
            for k in range(U):
                if G[k] is not None:
                    z[u_day[k]] += G[k][2].sum()
            add("own", pulse.copy(), z)
        for tau in SELF_TAUS:
            bt = 1 / tau
            if world == "B":
                col, z = gated({k: ev_t[ev_u == k] for k in np.unique(ev_u)}, tau)
                add(f"self_{int(tau)}", col, z)
            else:
                add(f"self_{int(tau)}", bt * wexp(ev_t, g_ev, ev_t, g_ev, np.ones(n), bt),
                    zsum(ev_day, exp_comp(ev_t, a[ev_u], b[ev_u], bt)))

    # ---- cross families: other agents' messages read by i on the same day
    ag = items_override if items_override is not None else u.items.filter(pl.col("kind") == "agent")
    ag = ag.filter(pl.col("sender") != pl.col("recipient"))
    sd = ag["day"].to_numpy().astype(np.int64); sr = ag["recipient"].to_numpy().astype(np.int64)
    ss = ag["s"].to_numpy().astype(np.float64)
    uk = np.array([gid.get((d, x), -1) for d, x in zip(sd, sr)], np.int64)
    k1 = np.full(len(ss), -1, np.int64)
    r = np.full(len(ss), np.nan)
    for k in np.unique(uk[uk >= 0]):
        if G[k] is None:
            continue
        sel = np.where(uk == k)[0]
        kk = np.searchsorted(G[k][0], ss[sel], side="right")
        okk = kk < len(G[k][0])
        k1[sel[okk]] = kk[okk]
        r[sel[okk]] = G[k][0][kk[okk]]
    ok = k1 >= 0
    sd, sr, ss, k1, r, uk = sd[ok], sr[ok], ss[ok], k1[ok], r[ok], uk[ok]
    gx = sd * 1000 + sr
    meta = {"n_events": n, "n_pairs": int(len(ss)), "n_msgs": int(len(u.talk)),
            "readout_lag_med": float(np.median(r - ss)) if len(ss) else np.nan,
            "readout_lag_q90": float(np.quantile(r - ss, 0.9)) if len(ss) else np.nan,
            "readout_lag_mean": float(np.mean(r - ss)) if len(ss) else np.nan,
            "recipients_per_msg": float(len(ss) / max(len(u.talk), 1))}
    if "A" in specs:
        for tau in CROSS_TAUS:
            bt = 1 / tau
            add(f"A_{int(tau)}", bt * wexp(ev_t, g_ev, ss, gx, np.ones(len(ss)), bt),
                zsum(u_day[uk], exp_comp(ss, a[uk], b[uk], bt)))
    if "Bt" in specs:
        for tau in CROSS_TAUS:
            bt = 1 / tau
            add(f"Bt_{int(tau)}", bt * wexp(ev_t, g_ev, r, gx, np.ones(len(r)), bt),
                zsum(u_day[uk], exp_comp(r, a[uk], b[uk], bt)))
    if "B" in specs:
        nb = len(B_BINS)
        colB = np.zeros((n, nb)); zB = np.zeros((D, nb))
        for k in np.unique(uk):
            if G[k] is None:
                continue
            gg, e, Fm, mu, sg = G[k]
            K = len(gg)
            nk = np.bincount(k1[uk == k], minlength=K).astype(float)[:K]
            cs = np.concatenate([[0.0], np.cumsum(nk)])
            idx = np.arange(K)
            evs = np.where(ev_u == k)[0]
            evs = evs[kstar[evs] >= 0]
            for bi, (m0, m1) in enumerate(B_BINS):
                hi = np.clip(idx - m0 + 1, 0, K); lo = np.clip(idx - m1, 0, K)
                Nb = (cs[hi] - cs[lo]) / (m1 - m0 + 1)
                zB[u_day[k], bi] += (Fm * Nb).sum()
                colB[evs, bi] = pulse[evs] * Nb[kstar[evs]]
        for bi, (m0, m1) in enumerate(B_BINS):
            add(f"B_{m0}", colB[:, bi], zB[:, bi])
    if "Ag" in specs:
        for tau in CROSS_TAUS:
            col, z = gated({k: ss[uk == k] for k in np.unique(uk)}, tau)
            add(f"Ag_{int(tau)}", col, z)
    if "H" in specs and items_override is None:
        md = u.talk["day"].to_numpy().astype(np.int64); ma = u.talk["agent"].to_numpy().astype(np.int64)
        mt = u.talk["t"].to_numpy().astype(np.float64)
        extra = u.items.filter((pl.col("kind") == "agent") & ~pl.col("sender").is_in(u.talk["agent"].unique().implode()))
        if len(extra):
            ex1 = extra.unique(["day", "sender", "s"])
            md = np.concatenate([md, ex1["day"].to_numpy()]); ma = np.concatenate([ma, ex1["sender"].to_numpy()])
            mt = np.concatenate([mt, ex1["s"].to_numpy()])
        for tau in CROSS_TAUS:
            bt = 1 / tau
            tot = wexp(ev_t, ev_day, mt, md, np.ones(len(mt)), bt)
            own = wexp(ev_t, g_ev, mt, md * 1000 + ma, np.ones(len(mt)), bt)
            z = np.zeros(D)
            for d in range(D):
                ks = np.where(u_day == d)[0]
                sel = md == d
                if len(ks) == 0 or sel.sum() == 0:
                    continue
                C = exp_comp(mt[sel][:, None], a[ks][None, :], b[ks][None, :], bt)
                C[ma[sel][:, None] == u_ag[ks][None, :]] = 0.0
                z[d] = C.sum()
            add(f"H_{int(tau)}", bt * np.maximum(tot - own, 0.0), z)

    F = np.column_stack(cols) if cols else np.zeros((n, 0))
    Zd = np.column_stack(Zs) if Zs else np.zeros((D, 0))
    if base is not None and only_cross:
        keepc = [k for k, nm in enumerate(base.names) if colfam(nm) not in CROSS_PREFIX]
        F = np.column_stack([base.F[:, keepc], F])
        Zd = np.column_stack([base.Zd[:, keepc], Zd])
        names = [base.names[k] for k in keepc] + names
    ev_bin = np.minimum((ev_t // BIN_S).astype(np.int64), L.shape[1] - 1)
    if internals:
        meta.update(_G=G, _RF=RF, _kstar=kstar, _pulse=pulse, _ev_u=ev_u, _gid=gid, _u_day=u_day, _u_ag=u_ag,
                    _items=(sd, sr, ss, k1, uk))
    return Design(names, F, Zd, ev_day, base_unit, ev_bin, L, base_day, base_ag, D, meta, bw)


# ----------------------------------------------------------------------------------------------- activity design
def build_act(u: Unit, items_override=None, inv_override=None, only_cross=False, base: Design | None = None,
              trim: float = 0.0) -> Design:
    grids = Grids(u, "point")
    cl = u.calls.sort("day", "agent", "t_first")
    ev_day0 = cl["day"].to_numpy().astype(np.int64)
    ev_ag0 = cl["agent"].to_numpy().astype(np.int64)
    ev_t0 = cl["t_first"].to_numpy().astype(np.float64)
    wake0 = cl["wake"].to_numpy()
    talk0 = cl["talk"].to_numpy()
    key, a, b, L, unit = _base_design(u, ev_day0, ev_ag0, trim)
    keep = unit >= 0
    keep[keep] &= (ev_t0[keep] >= a[unit[keep]]) & (ev_t0[keep] <= b[unit[keep]])
    keep &= ~_in_mask(u, ev_day0, ev_t0)
    ev_day, ev_ag, ev_t, ev_u, wake = ev_day0[keep], ev_ag0[keep], ev_t0[keep], unit[keep], wake0[keep]
    n = len(ev_t)
    D = u.n_days
    g_ev = ev_day * 1000 + ev_ag
    u_day = np.array([k[0] for k in key], np.int64)
    u_ag = np.array([k[1] for k in key], np.int64)
    gid = {(d, x): k for k, (d, x) in enumerate(zip(u_day, u_ag))}
    cols, Zs, names = [], [], []

    def add(name, col, zday):
        names.append(name); cols.append(col); Zs.append(zday)

    def zsum(day_of_src, comp):
        return np.bincount(day_of_src, weights=comp, minlength=D)

    if not only_cross:
        fg = u.days.filter(pl.col("first_goal_day"))["day"].to_list()
        if fg:
            for tau in KICK_TAUS:
                col = np.where(np.isin(ev_day, fg), np.exp(-ev_t / tau), 0.0)
                z = np.zeros(D)
                for k in range(len(a)):
                    if u_day[k] in fg:
                        z[u_day[k]] += tau * (np.exp(-a[k] / tau) - np.exp(-b[k] / tau))
                add(f"kick_{int(tau)}", col, z)
        ex = u.items.filter(pl.col("kind") != "agent")
        if len(ex):
            ed = ex["day"].to_numpy().astype(np.int64); er = ex["recipient"].to_numpy().astype(np.int64)
            k1, r, rf = grids.readout(ed, er, ex["s"].to_numpy().astype(np.float64))
            for fam, kinds in (("hum", ["human"]), ("aut", ["nudge", "pause_resume", "automated_other"])):
                sel = np.isin(ex["kind"].to_numpy(), kinds) & (k1 >= 0)
                uk = np.array([gid.get((d, x), -1) for d, x in zip(ed[sel], er[sel])], np.int64)
                okk = uk >= 0
                if okk.sum() == 0:
                    continue
                xs, gx, ukk = rf[sel][okk] + EPS, (ed[sel] * 1000 + er[sel])[okk], uk[okk]
                for tau in EXO_TAUS:
                    bt = 1 / tau
                    add(f"{fam}_{int(tau)}", bt * wexp(ev_t, g_ev, xs, gx, np.ones(len(xs)), bt),
                        zsum(u_day[ukk], exp_comp(xs, a[ukk], b[ukk], bt)))
        for fam, srcmask in (("self", np.ones(n, bool)), ("wake", wake)):
            xs, gx = ev_t[srcmask], g_ev[srcmask]
            for tau in ACT_SELF_TAUS:
                bt = 1 / tau
                add(f"{fam}_{int(tau)}", bt * wexp(ev_t, g_ev, xs, gx, np.ones(len(xs)), bt),
                    zsum(ev_day[srcmask], exp_comp(xs, a[ev_u[srcmask]], b[ev_u[srcmask]], bt)))
    # visible: agent items
    ag = items_override if items_override is not None else u.items.filter(pl.col("kind") == "agent")
    ag = ag.filter(pl.col("sender") != pl.col("recipient"))
    sd = ag["day"].to_numpy().astype(np.int64); sr = ag["recipient"].to_numpy().astype(np.int64)
    ss = ag["s"].to_numpy().astype(np.float64)
    k1, r, rf = grids.readout(sd, sr, ss)
    uk = np.array([gid.get((d, x), -1) for d, x in zip(sd, sr)], np.int64)
    ok = (k1 >= 0) & (uk >= 0)
    ss, rf, uk, gx = ss[ok], rf[ok] + EPS, uk[ok], (sd * 1000 + sr)[ok]
    for tau in CROSS_TAUS:
        bt = 1 / tau
        add(f"Av_{int(tau)}", bt * wexp(ev_t, g_ev, ss, gx, np.ones(len(ss)), bt),
            zsum(u_day[uk], exp_comp(ss, a[uk], b[uk], bt)))
        add(f"Bv_{int(tau)}", bt * wexp(ev_t, g_ev, rf, gx, np.ones(len(rf)), bt),
            zsum(u_day[uk], exp_comp(rf, a[uk], b[uk], bt)))
    # invisible: other agents' non-talk calls (room-blind)
    if inv_override is not None:
        iv_day, iv_ag, iv_t = inv_override
    else:
        nt = ~talk0 & keep
        iv_day, iv_ag, iv_t = ev_day0[nt], ev_ag0[nt], ev_t0[nt]
    for tau in CROSS_TAUS:
        bt = 1 / tau
        tot = wexp(ev_t, ev_day, iv_t, iv_day, np.ones(len(iv_t)), bt)
        own = wexp(ev_t, g_ev, iv_t, iv_day * 1000 + iv_ag, np.ones(len(iv_t)), bt)
        z = np.zeros(D)
        for d in range(D):
            ks = np.where(u_day == d)[0]
            sel = np.where(iv_day == d)[0]
            if len(ks) == 0 or len(sel) == 0:
                continue
            for j0 in range(0, len(sel), 20000):
                sj = sel[j0:j0 + 20000]
                C = exp_comp(iv_t[sj][:, None], a[ks][None, :], b[ks][None, :], bt)
                C[iv_ag[sj][:, None] == u_ag[ks][None, :]] = 0.0
                z[d] += C.sum()
        add(f"Ai_{int(tau)}", bt * np.maximum(tot - own, 0.0), z)
    # invisible, read-out placed: count others' non-talk calls since i's previous call start, onset after i's
    # next call record (first call with t_call > s)
    zBi = np.zeros((D, len(CROSS_TAUS))); colBi = np.zeros((n, len(CROSS_TAUS)))
    for k in range(len(a)):
        d, i = u_day[k], u_ag[k]
        if (d, i) not in grids.all:
            continue
        tc, tf = grids.all[(d, i)]
        sel = (iv_day == d) & (iv_ag != i)
        if sel.sum() == 0:
            continue
        kk = np.searchsorted(tc, iv_t[sel], side="right")
        kk = kk[kk < len(tc)]
        if len(kk) == 0:
            continue
        cnt = np.bincount(kk, minlength=len(tc)).astype(float)
        on = tf + EPS
        nzi = cnt > 0
        evs = np.where(ev_u == k)[0]
        for qi, tau in enumerate(CROSS_TAUS):
            bt = 1 / tau
            colBi[evs, qi] = bt * wexp(ev_t[evs], np.zeros(len(evs), np.int64), on[nzi],
                                       np.zeros(nzi.sum(), np.int64), cnt[nzi], bt)
            zBi[d, qi] += (cnt[nzi] * exp_comp(on[nzi], a[k], b[k], bt)).sum()
    for qi, tau in enumerate(CROSS_TAUS):
        add(f"Bi_{int(tau)}", colBi[:, qi], zBi[:, qi])
    F = np.column_stack(cols)
    Zd = np.column_stack(Zs)
    if base is not None and only_cross:
        keepc = [k for k, nm in enumerate(base.names) if nm.split("_")[0] not in ("Av", "Bv", "Ai", "Bi")]
        F = np.column_stack([base.F[:, keepc], F]); Zd = np.column_stack([base.Zd[:, keepc], Zd])
        names = [base.names[k] for k in keepc] + names
    ev_bin = np.minimum((ev_t // BIN_S).astype(np.int64), L.shape[1] - 1)
    return Design(names, F, Zd, ev_day, ev_u, ev_bin, L, u_day, u_ag, D, {"n_events": n, "n_pairs": int(len(ss))})


# ----------------------------------------------------------------------------------------------- specs
TALK_BASE = ("kick", "hum", "aut", "own", "self")
TALK_SPECS = {"S0": TALK_BASE, "A": TALK_BASE + ("A",), "A_H03": TALK_BASE + ("H",), "A_g": TALK_BASE + ("Ag",),
              "B": TALK_BASE + ("B",), "B_t": TALK_BASE + ("Bt",), "C": TALK_BASE + ("A", "B")}
W_BASE = ("kick", "hum", "aut", "self")
WORLD_A_SPECS = {"S0": W_BASE, "A": W_BASE + ("A",), "A_H03": W_BASE + ("H",), "B_t": W_BASE + ("Bt",)}
WORLD_B_SPECS = {"S0": W_BASE, "B": W_BASE + ("B",), "A_g": W_BASE + ("Ag",), "C": W_BASE + ("B", "A"),
                 "C_g": W_BASE + ("B", "Ag")}
ACT_BASE = ("kick", "hum", "aut", "self", "wake")
ACT_SPECS = {"S0": ACT_BASE, "A": ACT_BASE + ("Av", "Ai"), "B": ACT_BASE + ("Bv", "Bi"),
             "C": ACT_BASE + ("Av", "Ai", "Bv", "Bi")}
CROSS_PREFIX = ("A", "H", "Ag", "B", "Bt", "Av", "Ai", "Bv", "Bi")
SELF_PREFIX = ("self", "wake")
EXO_PREFIX = ("kick", "hum", "aut", "own")


def colfam(name):
    return name.split("_")[0]


# ----------------------------------------------------------------------------------------------- fitting
@dataclass
class Fit:
    spec: str
    cols: list
    names: list
    p: np.ndarray
    ll: float
    n: int
    days: list
    Kb: int
    U_sel: np.ndarray

    def weights(self):
        return dict(zip(self.names, np.exp(self.p[len(self.U_sel) + self.Kb - 1:])))


class Problem:
    """A design restricted to a set of days and columns."""

    def __init__(self, ds: Design, cols, days):
        self.ds = ds
        days = list(days)
        self.days = days
        em = np.isin(ds.ev_day, days)
        self.F = ds.F[em][:, cols]
        self.Z = ds.Zd[days][:, cols].sum(0)
        self.cols = list(cols)
        um = np.isin(ds.unit_day, days)
        self.U_sel = np.where(um)[0]
        remap = -np.ones(len(ds.unit_day), np.int64)
        remap[self.U_sel] = np.arange(len(self.U_sel))
        self.unit = remap[ds.ev_unit[em]]
        self.bin = ds.ev_bin[em]
        self.bw = ds.bw[em] if ds.bw is not None else np.ones(int(em.sum()))
        self.L = ds.L[self.U_sel]
        self.Kb = ds.L.shape[1]
        self.n = int(em.sum())
        self.U = len(self.U_sel)
        self.K = len(cols)

    def unpack(self, p):
        c = np.exp(p[:self.U])
        s = np.concatenate([[1.0], np.exp(p[self.U:self.U + self.Kb - 1])])
        w = np.exp(p[self.U + self.Kb - 1:])
        return c, s, w

    def loglik(self, p, grad=True):
        c, s, w = self.unpack(p)
        mu = c[self.unit] * s[self.bin] * self.bw
        lam = mu + (self.F @ w if self.K else 0.0)
        lam = np.maximum(lam, 1e-300)
        Ls = self.L @ s
        ll = np.log(lam).sum() - c @ Ls - (self.Z @ w if self.K else 0.0)
        if not grad:
            return ll
        r = 1.0 / lam
        g = np.empty_like(p)
        g[:self.U] = c * (np.bincount(self.unit, weights=s[self.bin] * self.bw * r, minlength=self.U) - Ls)
        gs = np.bincount(self.bin, weights=c[self.unit] * self.bw * r, minlength=self.Kb) - c @ self.L
        g[self.U:self.U + self.Kb - 1] = s[1:] * gs[1:]
        if self.K:
            g[self.U + self.Kb - 1:] = w * (self.F.T @ r - self.Z)
        return ll, g

    def init(self, w0=None):
        cnt = np.bincount(self.unit, minlength=self.U).astype(float)
        Lt = self.L.sum(1)
        rate = np.where(cnt > 0, 0.5 * cnt / np.maximum(Lt, 1.0), 1e-9)
        occ = self.L.sum(0) > 0
        p = np.concatenate([np.log(np.maximum(rate, 1e-12)), np.where(occ[1:], 0.0, -15.0),
                            np.log(np.full(self.K, 1e-3)) if w0 is None else np.log(np.maximum(w0, 1e-12))])
        return p

    def bounds(self):
        return [(-40.0, 5.0)] * self.U + [(-25.0, 10.0)] * (self.Kb - 1) + [(-25.0, 8.0)] * self.K

    def fit(self, p0=None, maxiter=4000, fixed=None):
        p0 = self.init() if p0 is None else p0
        bnds = self.bounds()
        if fixed is not None:
            bnds = [(v, v) if f else bd for v, f, bd in zip(p0, fixed, bnds)]
        res = optimize.minimize(lambda p: tuple(-x for x in self.loglik(p)), p0, jac=True, method="L-BFGS-B",
                                bounds=bnds, options={"maxiter": maxiter, "maxfun": maxiter * 2, "ftol": 1e-12,
                                                      "gtol": 1e-7})
        return res.x, -res.fun


def fit_spec(ds: Design, spec_cols: dict, spec: str, days=None, warm: Fit | None = None, maxiter=4000,
             restart: bool = True) -> Fit:
    days = list(range(ds.D)) if days is None else list(days)
    cols = ds.cols(spec_cols[spec])
    pr = Problem(ds, cols, days)
    p0 = pr.init()
    if warm is not None:
        wmap = warm.weights()
        p0[:pr.U + pr.Kb - 1] = warm.p[:pr.U + pr.Kb - 1] if len(warm.U_sel) == pr.U else p0[:pr.U + pr.Kb - 1]
        p0[pr.U + pr.Kb - 1:] = [np.log(max(wmap.get(ds.names[k], 1e-3), 1e-12)) for k in cols]
    p, ll = pr.fit(p0, maxiter=maxiter)
    # second start from the default init if warm-started (guards against a poor basin)
    if warm is not None and restart:
        p2, ll2 = pr.fit(pr.init(), maxiter=maxiter)
        if ll2 > ll:
            p, ll = p2, ll2
    return Fit(spec, cols, [ds.names[k] for k in cols], p, ll, pr.n, days, pr.Kb, pr.U_sel)


def branching(ds: Design, f: Fit) -> dict:
    """compensator shares per family: offspring per event."""
    w = np.exp(f.p[len(f.U_sel) + f.Kb - 1:])
    Z = ds.Zd[f.days][:, f.cols].sum(0)
    contrib = w * Z
    out = {"n_events": f.n}
    fams = {}
    for nm, v in zip(f.names, contrib):
        fams[colfam(nm)] = fams.get(colfam(nm), 0.0) + v
    for k, v in fams.items():
        out[f"n_{k}"] = v / max(f.n, 1)
    out["n_cross"] = sum(v for k, v in fams.items() if k in CROSS_PREFIX) / max(f.n, 1)
    out["n_self"] = sum(v for k, v in fams.items() if k in SELF_PREFIX) / max(f.n, 1)
    out["n_exo"] = sum(v for k, v in fams.items() if k in ("kick", "hum", "aut")) / max(f.n, 1)
    out["n_own"] = fams.get("own", 0.0) / max(f.n, 1)
    out["weights"] = {nm: float(x) for nm, x in zip(f.names, w)}
    out["contrib"] = {nm: float(x / max(f.n, 1)) for nm, x in zip(f.names, contrib)}
    return out


def heldout(ds: Design, f: Fit, test_days) -> tuple[float, int]:
    """Refit only the agent-day levels on the test days (H03's convention); returns (ll, n)."""
    pr = Problem(ds, f.cols, test_days)
    if pr.n == 0:
        return 0.0, 0
    trU = len(f.U_sel)
    s_tr = np.concatenate([[0.0], f.p[trU:trU + f.Kb - 1]])
    tr_pr = Problem(ds, f.cols, f.days)
    occ = tr_pr.L.sum(0) > 0
    med = float(np.median(s_tr[occ])) if occ.any() else 0.0
    s_new = np.where(occ, s_tr, med)
    s_new = np.maximum(s_new, med - np.log(20.0))
    p = pr.init()
    p[pr.U:pr.U + pr.Kb - 1] = s_new[1:]
    p[pr.U + pr.Kb - 1:] = f.p[trU + f.Kb - 1:]
    fixed = np.zeros(len(p), bool)
    fixed[pr.U:] = True
    p2, ll = pr.fit(p, fixed=fixed, maxiter=2000)
    return ll, pr.n


def folds_for(D: int, seed: int = 0):
    if D <= 6:
        return [[d] for d in range(D)]
    rng = np.random.default_rng(seed)
    return [sorted(x.tolist()) for x in np.array_split(rng.permutation(D), 5)]


def cv(ds: Design, spec_cols: dict, specs, seed=0, train_fits=None):
    """Day-blocked held-out log-likelihood for each spec; returns {spec: (ll_sum, n_sum)}."""
    out = {s: [0.0, 0] for s in specs}
    D = ds.D
    if D < 2:
        return None
    for fold in folds_for(D, seed):
        train = [d for d in range(D) if d not in fold]
        base = None
        for s in specs:
            f = fit_spec(ds, spec_cols, s, train, warm=base if s != "S0" else None, restart=False)
            if s == "S0":
                base = f
            ll, n = heldout(ds, f, fold)
            out[s][0] += ll
            out[s][1] += n
    return out


# ----------------------------------------------------------------------------------------------- nulls
def shift_items(u: Unit, rng, lo=300.0, hi=1800.0):
    """circularly shift every sender's messages within the day by its own offset; same (message, recipient) pairs."""
    ag = u.items.filter(pl.col("kind") == "agent")
    T = dict(zip(u.days["day"].to_list(), u.days["T"].to_list()))
    keys = ag.select("day", "sender").unique().sort("day", "sender")
    off = rng.uniform(lo, hi, len(keys)) * rng.choice([-1, 1], len(keys))
    keys = keys.with_columns(pl.Series("off", off))
    ag = ag.join(keys, on=["day", "sender"])
    Tc = np.array([T[d] for d in ag["day"].to_list()], dtype=np.float64)
    s = np.mod(ag["s"].to_numpy() + ag["off"].to_numpy(), Tc)
    return ag.with_columns(pl.Series("s", s)).drop("off"), keys


def shift_inv(u: Unit, keys, rng):
    """shift others' non-talk calls (activity invisible family) by the sender offsets."""
    cl = u.calls.filter(~pl.col("talk"))
    T = dict(zip(u.days["day"].to_list(), u.days["T"].to_list()))
    kk = keys.rename({"sender": "agent"})
    cl = cl.join(kk, on=["day", "agent"], how="left")
    miss = cl["off"].is_null().to_numpy()
    off = cl["off"].to_numpy().copy()
    off[miss] = rng.uniform(300, 1800, miss.sum()) * rng.choice([-1, 1], miss.sum())
    Tc = np.array([T[d] for d in cl["day"].to_list()])
    t = np.mod(cl["t_first"].to_numpy() + off, Tc)
    return cl["day"].to_numpy().astype(np.int64), cl["agent"].to_numpy().astype(np.int64), t


def dayblock_items(u: Unit, k: int):
    """recipient i on day d receives the messages it received on day (d + k) mod D (same time since window start)."""
    ag = u.items.filter(pl.col("kind") == "agent")
    D = u.n_days
    T = dict(zip(u.days["day"].to_list(), u.days["T"].to_list()))
    out = ag.with_columns(((pl.col("day") - k) % D).cast(pl.Int16).alias("day"))
    Tc = np.array([T[d] for d in out["day"].to_list()], dtype=np.float64)
    out = out.filter(pl.Series(out["s"].to_numpy() < Tc))
    return out
