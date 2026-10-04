"""H43 library: second-kick marginal effects vs read-out spacing, measured from the receiving call.

One estimator, used identically by the synthetic validation (`synthetic.py`), the per-period replication
(`run_period.py`), the native tests (`run_native.py`) and the confirmatory script (`confirm.py`).

Inputs (all as polars DataFrames, real or synthetic):
  calls   turn_id, agent, pt_date, unit_id, kind_c (call_windows kind code), talk, first_of_day, t_call, t_end (epoch s),
          nN, nH, nA (kick items read by the call; see scheme/build.py)
  states  pt_date, minute, agent, lump4_min (0 work, 1 chat, 2 idle, 3 consolidate), in_span, present
  writes  agent, t (epoch s)
  cal     pt_date, win_start (epoch s), win_end (epoch s)
Definitions (card, "Observables"):
  idle call       kind in {pause, wait} and not talking; active call = any other non-summary call
  idle at read    previous call of the agent-day idle, or >= 180 s between its end and this call's start
  primer          receiving call with a class-c kick, no other class at the same call, no N/H/A read in the previous 30 min
  second kick     next class-c receiving call after a primer (same agent-day, <= 240 min), spacing delta = t_call difference
  O1 escape       a sustained active run (>= 3 consecutive active calls) starts within 15 min (idle-at-read rows only)
  O2 talk         a talk call within 5 min
  O3 write        a write event within 30 min
  cut             both arms censored at the next receiving call with a kick of class c, N or H, and at the agent-day end
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H43-kick-refractory-window"
HDIR = ROOT / "hypotheses/H43-kick-refractory-window"
HOLDOUT = json.loads((ROOT / "hypotheses/holdout.json").read_text())
SEED = 20261004

CLASSES = ("N", "H", "A")             # base classes (quiet rule and "any kick" use these)
KCOL = {"N": "nN", "H": "nH", "A": "nA"}
ALL_CLASSES = ("N", "H", "A", "D")     # D = directed: nudge, human naming the agent, or @-mention (G38 gate test)
IDLE_KINDS = (2, 3)            # pause, wait (call_windows kind codes, scheme/build.py KINDS)
GAP_IDLE_S = 180.0
QUIET_S = 1800.0               # lever-episode quiet period (H39)
OTHER_S = 600.0                # "other-class kick in the previous 10 min" covariate
TALK_LOOK_S = 300.0
MAX_DELTA_MIN = 240.0
DELTA_EDGES = np.array([0.0, 2, 5, 15, 30, 60, 120, 240])
DELTA_LABELS = ["0-2", "2-5", "5-15", "15-30", "30-60", "60-120", "120-240"]
WIN = {"O1": 15, "O2": 5, "O3": 30, "O2c": 1, "O1a": 15}
# O2c: the receiving call itself talks (immediate next action). O1a (post hoc sensitivity, A6): any active call within
# 15 min, so a glance (wake, look, pause again) counts as escape, as on H39's minute grid.
RUN_MIN = 3
EPI_IDLE_RUN = 3               # launched episode ends at the first idle run >= 3 min
EFFECTIVE_MIN = 15.0           # primer effective = O1 escape within 15 min
CUT = {"N": ("N", "H"), "H": ("N", "H"), "A": ("N", "H", "A"), "D": ("N", "H", "A")}
N_CTRL = 10
MIN_AGENT_CTRL = 5
B_BOOT = 300
STATUS = {"act": 0, "noeff": 1, "in": 2, "post": 3}
STATUS_NAMES = {v: k for k, v in STATUS.items()}


# =============================================================================== utilities

def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H43-kick-refractory-window"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def is_holdout(pt_date: str, goal_no) -> bool:
    if goal_no is not None and int(goal_no) in set(HOLDOUT["goal_periods_held_out"]):
        return True
    return any(w["start"] <= pt_date < w["end"] for w in HOLDOUT["ne_windows"])


def jdump(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()]
        if isinstance(o, float):
            return None if not np.isfinite(o) else o
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        return o
    path.write_text(json.dumps(conv(obj), indent=1))


def load_real(goal_no: int, date_from: str | None = None, date_to: str | None = None, units: list[str] | None = None):
    """Non-holdout calls/states/writes/calendar for one goal period (optionally a date range [from, to) or units)."""
    calls = pl.read_parquet(OUT / "calls.parquet").filter(pl.col("goal_no") == goal_no)
    if date_from:
        calls = calls.filter(pl.col("pt_date") >= date_from)
    if date_to:
        calls = calls.filter(pl.col("pt_date") < date_to)
    if units:
        calls = calls.filter(pl.col("unit_id").is_in(units))
    days = sorted(calls["pt_date"].unique().to_list())
    assert not any(is_holdout(d, goal_no) for d in days), "holdout day in exploratory load"
    states = (pl.scan_parquet(SH / "states_min.parquet")
              .filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
              .select("pt_date", "minute", "agent", "lump4_min", "in_span", "present").collect())
    writes = pl.read_parquet(OUT / "writes.parquet").filter(pl.col("pt_date").is_in(days)).select("agent", "t")
    cal = (pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days))
           .select("pt_date", (pl.col("win_start").dt.epoch("us") / 1e6).alias("win_start"),
                   (pl.col("win_end").dt.epoch("us") / 1e6).alias("win_end")))
    return calls, states, writes, cal


# =============================================================================== preparation

def _ffill(x: np.ndarray, grp: np.ndarray) -> np.ndarray:
    """Forward-fill NaNs within contiguous groups."""
    n = len(x)
    idx = np.where(np.isnan(x), -1, np.arange(n))
    starts = np.r_[0, np.flatnonzero(grp[1:] != grp[:-1]) + 1]
    out = np.full(n, np.nan)
    for s, e in zip(starts, np.r_[starts[1:], n]):
        ii = np.maximum.accumulate(idx[s:e])
        ok = ii >= 0
        out[s:e][ok] = x[ii[ok]]
    return out


def _next_time(key_q: np.ndarray, key_ev: np.ndarray, t_ev: np.ndarray, strict: bool) -> np.ndarray:
    """For sorted event keys (group*1e7 + seconds), the time of the first event at/after (or strictly after) the query."""
    side = "right" if strict else "left"
    j = np.searchsorted(key_ev, key_q, side)
    out = np.full(len(key_q), np.nan)
    ok = j < len(key_ev)
    out[ok] = t_ev[j[ok]]
    return out


def _next_same(key_q: np.ndarray, key_ev: np.ndarray, t_ev: np.ndarray, strict: bool) -> np.ndarray:
    """Time of the first event at/after (strict: after) each query, within the same agent-day; inf if none."""
    j = np.searchsorted(key_ev, key_q, "right" if strict else "left")
    out = np.full(len(key_q), np.inf)
    ok = j < len(key_ev)
    jj = j[ok]
    same = np.floor(key_ev[jj] / 1e7) == np.floor(key_q[ok] / 1e7)
    v = np.full(ok.sum(), np.inf)
    v[same] = t_ev[jj[same]]
    out[ok] = v
    return out


def _count_in(key_ev: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """Number of events with key in [lo, hi)."""
    return np.searchsorted(key_ev, hi, "left") - np.searchsorted(key_ev, lo, "left")


class Prep:
    """Per-call arrays for one period (calls sorted by agent, pt_date, t_call)."""

    def __init__(self, calls: pl.DataFrame, states: pl.DataFrame, writes: pl.DataFrame, cal: pl.DataFrame):
        c = calls.sort("agent", "pt_date", "t_call")
        self.c = c
        n = c.height
        self.n = n
        self.agent = c["agent"].to_numpy().astype(np.int64)
        self.pt_date = c["pt_date"].to_numpy()
        gkey = (c["agent"].cast(pl.Utf8) + "|" + c["pt_date"]).to_numpy()
        first = np.r_[True, gkey[1:] != gkey[:-1]]
        self.grp = np.cumsum(first) - 1
        days = sorted(set(self.pt_date.tolist()))
        self.days = days
        dmap = {d: i for i, d in enumerate(days)}
        self.day = np.array([dmap[d] for d in self.pt_date], np.int64)
        units = sorted(set(c["unit_id"].to_list()))
        self.units = units
        umap = {u: i for i, u in enumerate(units)}
        self.unit = np.array([umap[u] for u in c["unit_id"].to_list()], np.int64)
        self.t = c["t_call"].to_numpy().astype(float)
        self.tend = c["t_end"].to_numpy().astype(float)
        kind = c["kind_c"].to_numpy()
        self.talk = c["talk"].to_numpy().astype(bool)
        self.first_of_day = c["first_of_day"].to_numpy().astype(bool)
        self._cut_cache = {}
        self.k = {cl: c[KCOL[cl]].to_numpy().astype(np.int64) for cl in CLASSES}
        hm = c["nHm"].to_numpy().astype(np.int64) if "nHm" in c.columns else np.zeros(n, np.int64)
        self.k["D"] = self.k["N"] + hm + self.k["A"]
        self.k_hund = self.k["H"] - hm
        self.anyk = (self.k["N"] + self.k["H"] + self.k["A"]) > 0
        idle = np.isin(kind, IDLE_KINDS) & ~self.talk
        self.idle_call = idle
        active = ~idle
        self.active = active
        g = self.grp
        newg = np.r_[True, g[1:] != g[:-1]]
        self.has_prev = ~newg
        prev_end = np.r_[np.nan, self.tend[:-1]]
        gap = self.t - prev_end
        prev_idle = np.r_[False, idle[:-1]]
        boundary = newg | prev_idle | (gap >= GAP_IDLE_S)        # a fresh state starts at this call
        self.idle_at_read = self.has_prev & (prev_idle | (gap >= GAP_IDLE_S))
        # idle age: time since the end of the last active call before this one (same agent-day)
        last_act_end = _ffill(np.where(active, self.tend, np.nan), g)
        last_act_end = np.r_[np.nan, last_act_end[:-1]]
        last_act_end[newg] = np.nan
        gstart_t = self.t[np.r_[np.flatnonzero(newg)]][np.cumsum(newg) - 1]
        self.gstart_t = gstart_t
        self.idle_age = np.where(np.isnan(last_act_end), self.t - gstart_t, self.t - last_act_end)
        # active-run start: first active call after a boundary
        rs = np.where(active & boundary, self.t, np.nan)
        rs_f = _ffill(np.where(active, rs, np.nan), g)
        rs_f[~active] = np.nan
        prev_rs = np.r_[np.nan, rs_f[:-1]]
        prev_rs[newg] = np.nan
        self.act_age = np.where(np.isnan(prev_rs), 0.0, self.t - prev_rs)
        # sustained run starts: active run start whose run has >= RUN_MIN calls without a boundary
        run_id = np.cumsum(boundary | ~active)
        same1 = np.r_[run_id[1:] == run_id[:-1], False] & np.r_[active[1:], False]
        same2 = np.r_[same1[1:], False] & same1
        sustained = active & boundary & (same2 if RUN_MIN == 3 else same1)
        self.gt = g.astype(float) * 1e7 + (self.t - gstart_t)       # sortable within-day key (s)
        self.rs3_key, self.rs3_t = self.gt[sustained], self.t[sustained]
        self.talk_key, self.talk_t = self.gt[self.talk], self.t[self.talk]
        self.act_key, self.act_t = self.gt[active], self.t[active]
        self.kick_key = {cl: self.gt[self.k[cl] > 0] for cl in ALL_CLASSES}
        self.kick_t = {cl: self.t[self.k[cl] > 0] for cl in ALL_CLASSES}
        self.any_key = self.gt[self.anyk]
        # day end per group
        gend = np.zeros(g.max() + 1)
        np.maximum.at(gend, g, self.t)
        self.day_end = gend[g]
        # writes (per agent, by key in this agent-day)
        self.write_next = np.full(n, np.nan)
        if writes.height:
            w = writes.sort("agent", "t")
            for a in np.unique(self.agent):
                wt = w.filter(pl.col("agent") == int(a))["t"].to_numpy()
                if len(wt) == 0:
                    continue
                m = self.agent == a
                j = np.searchsorted(wt, self.t[m], "left")
                v = np.full(m.sum(), np.nan)
                ok = j < len(wt)
                v[ok] = wt[j[ok]]
                self.write_next[m] = v
        self.writes_per_agentday = (writes.height / max(1, g.max() + 1)) if writes.height else 0.0
        # calendar: day third and minute index
        cal_d = {r["pt_date"]: (r["win_start"], r["win_end"]) for r in cal.iter_rows(named=True)}
        ws = np.array([cal_d[d][0] for d in self.pt_date])
        we = np.array([cal_d[d][1] for d in self.pt_date])
        self.win_start = ws
        frac = np.clip((self.t - ws) / np.maximum(we - ws, 60.0), 0, 0.999)
        self.third = (frac * 3).astype(np.int64)
        self.minute = np.floor((self.t - ws) / 60.0).astype(np.int64)
        self._states(states)

    def _states(self, states: pl.DataFrame):
        """Swarm-activity tercile (others non-idle in the previous minute) and launched-episode end lookup."""
        s = states.filter(pl.col("present") & pl.col("in_span"))
        agg = s.group_by("pt_date", "minute").agg(pl.len().alias("np"), (pl.col("lump4_min") != 2).sum().alias("na"))
        me = s.select("pt_date", "minute", "agent", (pl.col("lump4_min") != 2).cast(pl.Int32).alias("me"))
        q = pl.DataFrame({"i": np.arange(self.n), "pt_date": self.pt_date,
                          "minute": (self.minute - 1).astype(np.int64), "agent": self.agent})
        q = (q.join(agg.with_columns(pl.col("minute").cast(pl.Int64)), on=["pt_date", "minute"], how="left")
             .join(me.with_columns(pl.col("minute").cast(pl.Int64), pl.col("agent").cast(pl.Int64)),
                   on=["pt_date", "minute", "agent"], how="left")
             .with_columns(pl.col("np").fill_null(0), pl.col("na").fill_null(0),
                           pl.col("me").is_not_null().cast(pl.Int32).alias("pres"), pl.col("me").fill_null(0))
             .with_columns(((pl.col("na") - pl.col("me")) / (pl.col("np") - pl.col("pres")).clip(1, None)).alias("share"))
             .sort("i"))
        share = q["share"].to_numpy()
        self.swarm = np.where(share < 1 / 3, 0, np.where(share < 2 / 3, 1, 2)).astype(np.int64)
        # episode end: per (pt_date, agent), first minute m' >= m starting an idle run >= EPI_IDLE_RUN
        self.epi = {}
        full = states.sort("pt_date", "agent", "minute")
        for (d, a), gdf in full.group_by(["pt_date", "agent"]):
            mins = gdf["minute"].to_numpy().astype(np.int64)
            if len(mins) == 0:
                continue
            L = int(mins.max()) + 1
            idle = np.ones(L + EPI_IDLE_RUN, bool)
            ok = gdf["present"].to_numpy() & gdf["in_span"].to_numpy()
            nonidle = (gdf["lump4_min"].to_numpy() != 2) & ok
            idle[mins[nonidle]] = False
            run = np.ones(L, bool)
            for k in range(EPI_IDLE_RUN):
                run &= idle[k:k + L]
            nxt = np.full(L + 1, L, np.int64)
            for m in range(L - 1, -1, -1):
                nxt[m] = m if run[m] else nxt[m + 1]
            self.epi[(d, int(a))] = nxt

    def episode_end(self, i: int, t_esc: float) -> tuple[float, float]:
        """Launched episode starting at escape time t_esc for the agent-day of call i: (length min, end epoch s)."""
        nxt = self.epi.get((self.pt_date[i], int(self.agent[i])))
        m0 = int(np.floor((t_esc - self.win_start[i]) / 60.0))
        if nxt is None or m0 < 0:
            return np.nan, np.nan
        m0 = min(m0, len(nxt) - 1)
        m1 = nxt[m0]
        if m1 == m0:   # escape minute already idle-ish on the minute grid: look from the next minute
            m1 = nxt[min(m0 + 1, len(nxt) - 1)]
        L = max(m1 - m0, 1)
        return float(L), float(self.win_start[i] + 60.0 * (m0 + L))

    # ------------------------------------------------------------------ outcomes
    def cut_arrays(self, cl: str):
        if cl not in self._cut_cache:
            keys = np.concatenate([self.kick_key[c] for c in CUT[cl]])
            ts = np.concatenate([self.kick_t[c] for c in CUT[cl]])
            o = np.argsort(keys, kind="stable")
            self._cut_cache[cl] = (keys[o], ts[o])
        return self._cut_cache[cl]

    def outcomes(self, idx: np.ndarray, cl: str) -> dict:
        """Event time (min; inf = none) and cut time (min) for O1/O2/O3 at calls idx, with class-cl cutting."""
        q = self.gt[idx]
        t0 = self.t[idx]
        ck, ct = self.cut_arrays(cl)
        tc = _next_same(q, ck, ct, strict=True)
        cut = np.minimum((tc - t0) / 60.0, (self.day_end[idx] - t0) / 60.0 + 1.0 / 60)
        out = {}
        for name, (kk, tt) in {"O1": (self.rs3_key, self.rs3_t), "O2": (self.talk_key, self.talk_t),
                               "O1a": (self.act_key, self.act_t)}.items():
            te = _next_same(q, kk, tt, strict=False)
            out[name] = ((te - t0) / 60.0, cut)
        out["O2c"] = (np.where(self.talk[idx], 0.0, np.inf), np.full(len(idx), 1.0))
        wn = self.write_next[idx]
        ev3 = np.where(np.isfinite(wn) & (wn <= self.day_end[idx] + 60), (wn - t0) / 60.0, np.inf)
        out["O3"] = (ev3, cut)
        return out


def _next_key(key_q, key_ev, strict):
    side = "right" if strict else "left"
    j = np.searchsorted(key_ev, key_q, side)
    out = np.full(len(key_q), np.inf)
    ok = j < len(key_ev)
    out[ok] = key_ev[j[ok]]
    return out


# =============================================================================== design: primers, second kicks, controls

def age_bin(P: Prep, idx: np.ndarray) -> np.ndarray:
    ia = P.idle_age[idx] / 60.0
    aa = P.act_age[idx] / 60.0
    idle_b = np.digitize(ia, [3, 10, 30])           # 0..3
    act_b = 4 + np.digitize(aa, [3, 15])            # 4..6
    return np.where(P.idle_at_read[idx], idle_b, act_b)


def covariates(P: Prep, idx: np.ndarray, cl: str) -> dict:
    q = P.gt[idx]
    talk5 = (_count_in(P.talk_key, q - TALK_LOOK_S, q) > 0).astype(np.int64)
    others = [c for c in CLASSES if c != cl] if cl != "D" else ["H"]
    other = np.sort(np.concatenate([P.kick_key[c] for c in others]))
    oth10 = (_count_in(other, q - OTHER_S, q) > 0).astype(np.int64)
    return {"unit": P.unit[idx], "read": P.idle_at_read[idx].astype(np.int64), "age": age_bin(P, idx),
            "talk5": talk5, "third": P.third[idx], "swarm": P.swarm[idx], "oth10": oth10}


LEVELS = [("agent", ["unit", "read", "age", "talk5", "third", "swarm", "oth10", "x1", "x2"]),
          ("pool", ["unit", "read", "age", "talk5", "third", "swarm", "oth10", "x1", "x2"]),
          ("pool", ["unit", "read", "age", "talk5", "oth10", "x1", "x2"]),
          ("pool", ["unit", "read", "age", "x1", "x2"])]


def _key(cov: dict, fields: list[str]) -> np.ndarray:
    k = np.zeros(len(cov["unit"]), np.int64)
    for f in fields:
        k = k * 64 + cov.get(f, np.zeros_like(k)).astype(np.int64)
    return k


def strata_assign(cov_t: dict, cov_c: dict, agent_t: np.ndarray, agent_c: np.ndarray):
    """Exact strata with fallbacks. Each treated row gets the first level whose stratum holds >= need controls
    (same agent: >= MIN_AGENT_CTRL; pooled: >= 1). Returns (t_level, t_key, control keys per level)."""
    nt = len(agent_t)
    t_lev = np.full(nt, -1, np.int64)
    t_key = np.full(nt, -1, np.int64)
    ckeys = []
    todo = np.ones(nt, bool)
    for li, (mode, fields) in enumerate(LEVELS):
        kt = _key(cov_t, fields)
        kc = _key(cov_c, fields)
        if mode == "agent":
            kt = kt * 64 + agent_t
            kc = kc * 64 + agent_c
        ckeys.append(kc)
        if not todo.any() or len(kc) == 0:
            continue
        ks = np.sort(kc)
        cnt = np.searchsorted(ks, kt, "right") - np.searchsorted(ks, kt, "left")
        need = MIN_AGENT_CTRL if mode == "agent" else 1
        ok = todo & (cnt >= need)
        t_lev[ok] = li
        t_key[ok] = kt[ok]
        todo &= ~ok
    return t_lev, t_key, ckeys


def build_design(P: Prep, cl: str, rng=None, quiet_s: float = QUIET_S, idle_only_gate: bool = False) -> dict:
    """Primers, E1 controls, second kicks and E2 controls for class cl, with their strata (Family objects)."""
    elig = P.has_prev & ~P.first_of_day
    kc = P.k[cl] > 0
    if cl == "D":
        pure = kc & (P.k_hund == 0)
    else:
        pure = kc & ((P.k["N"] + P.k["H"] + P.k["A"]) == P.k[cl])
    q = P.gt
    quiet = _count_in(P.any_key, q - quiet_s, q) == 0
    primer = np.flatnonzero(elig & pure & quiet)
    e1c = np.flatnonzero(elig & ~P.anyk & quiet)
    out = {"class": cl, "n_kick_calls": int(kc.sum()), "n_primers": len(primer)}
    if len(primer) == 0:
        return out
    # primer effectiveness and launched episode (idle-at-read primers)
    oc_p = P.outcomes(primer, cl)
    ev1 = oc_p["O1"][0]
    eff = P.idle_at_read[primer] & (ev1 <= EFFECTIVE_MIN)
    t_esc = P.t[primer] + ev1 * 60.0
    L = np.full(len(primer), np.nan)
    ep_end = np.full(len(primer), np.nan)
    for j in np.flatnonzero(eff):
        L[j], ep_end[j] = P.episode_end(primer[j], t_esc[j])
    # second kicks: the next class-cl receiving call after each primer, same agent-day, within 240 min
    kk, kt = P.kick_key[cl], P.kick_t[cl]
    t_next = _next_same(q[primer], kk, kt, strict=True)
    win_end = np.fmin(t_next, P.t[primer] + MAX_DELTA_MIN * 60.0)
    # map second-kick calls back to indices
    sec_idx, sec_p = [], []
    gidx = {}
    for j, p in enumerate(primer):
        if not np.isfinite(t_next[j]) or t_next[j] > P.t[p] + MAX_DELTA_MIN * 60.0:
            continue
        g = P.grp[p]
        if g not in gidx:
            gidx[g] = np.flatnonzero(P.grp == g)
        gi = gidx[g]
        s = gi[np.searchsorted(P.t[gi], t_next[j])]
        if pure[s] and elig[s]:
            sec_idx.append(s)
            sec_p.append(j)
    sec_idx = np.array(sec_idx, np.int64)
    sec_p = np.array(sec_p, np.int64)
    # E2 control pool: calls after a primer, before its window end, with no kick read
    pool_idx, pool_p = [], []
    for j, p in enumerate(primer):
        g = P.grp[p]
        if g not in gidx:
            gidx[g] = np.flatnonzero(P.grp == g)
        gi = gidx[g]
        a = np.searchsorted(P.t[gi], P.t[p], "right")
        b = np.searchsorted(P.t[gi], win_end[j], "left")
        cand = gi[a:b]
        cand = cand[~P.anyk[cand] & elig[cand]]
        pool_idx.append(cand)
        pool_p.append(np.full(len(cand), j))
    pool_idx = np.concatenate(pool_idx) if pool_idx else np.zeros(0, np.int64)
    pool_p = np.concatenate(pool_p) if pool_p else np.zeros(0, np.int64)

    def status(idx, pj):
        tt = P.t[idx]
        ir = P.idle_at_read[primer[pj]]
        e = eff[pj]
        st = np.full(len(idx), STATUS["act"])
        st[ir] = STATUS["noeff"]
        esc = ir & e & (t_esc[pj] < tt)
        st[esc & (tt < ep_end[pj])] = STATUS["in"]
        st[esc & (tt >= ep_end[pj])] = STATUS["post"]
        return st

    # ---- E1 matching
    cov_t = covariates(P, primer, cl)
    cov_c = covariates(P, e1c, cl)
    for cv in (cov_t, cov_c):
        cv["x1"] = np.zeros(len(cv["unit"]), np.int64)
        cv["x2"] = np.zeros(len(cv["unit"]), np.int64)
    out.update({"primer": primer, "e1c": e1c, "eff": eff, "L": L, "ev1_primer": ev1,
                "batched": P.k[cl][primer] >= 2,
                "fam1": Family(P, cl, "e1", primer, cov_t, e1c, cov_c)})
    # ---- batched: dose >= 2 vs dose 1 primers
    d2 = np.flatnonzero(P.k[cl][primer] >= 2)
    d1 = np.flatnonzero(P.k[cl][primer] == 1)
    if len(d2) and len(d1):
        cb_t = {k: v[d2] for k, v in cov_t.items()}
        cb_c = {k: v[d1] for k, v in cov_t.items()}
        out.update({"bat_t": primer[d2], "bat_c": primer[d1],
                    "famb": Family(P, cl, "bat", primer[d2], cb_t, primer[d1], cb_c)})
    # ---- E2 matching
    if len(sec_idx) and len(pool_idx):
        d_t = (P.t[sec_idx] - P.t[primer[sec_p]]) / 60.0
        d_c = (P.t[pool_idx] - P.t[primer[pool_p]]) / 60.0
        b_t = np.clip(np.digitize(d_t, DELTA_EDGES[1:-1], right=True), 0, len(DELTA_LABELS) - 1)
        b_c = np.clip(np.digitize(d_c, DELTA_EDGES[1:-1], right=True), 0, len(DELTA_LABELS) - 1)
        s_t = status(sec_idx, sec_p)
        s_c = status(pool_idx, pool_p)
        c2t = covariates(P, sec_idx, cl)
        c2c = covariates(P, pool_idx, cl)
        c2t["x1"], c2t["x2"] = b_t, s_t
        c2c["x1"], c2c["x2"] = b_c, s_c
        out.update({"sec": sec_idx, "sec_p": sec_p, "pool": pool_idx, "pool_p": pool_p,
                    "fam2": Family(P, cl, "e2", sec_idx, c2t, pool_idx, c2c),
                    "d_t": d_t, "bin_t": b_t, "st_t": s_t, "bin_c": b_c, "st_c": s_c, "d_c": d_c})
    return out


# =============================================================================== estimation

def _arm_arrays(P: Prep, idx: np.ndarray, cl: str, oname: str, weights: np.ndarray, day: np.ndarray, nd: int):
    """Per-day weighted (events, at-risk) arrays, shape (nd, W)."""
    W = WIN[oname]
    oc = P.outcomes(idx, cl)[oname]
    ev, cut = oc
    j = np.arange(W)[None, :]
    atrisk = (cut[:, None] > j) & (ev[:, None] >= j)
    event = atrisk & (np.floor(ev)[:, None] == j) & (ev[:, None] < cut[:, None])
    E = np.zeros((nd, W))
    R = np.zeros((nd, W))
    np.add.at(E, day, event * weights[:, None])
    np.add.at(R, day, atrisk * weights[:, None])
    return E, R


def _F(E: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Cumulative incidence over the window from pooled hazards; E, R (..., W)."""
    h = np.where(R > 0, E / np.maximum(R, 1e-12), 0.0)
    return 1.0 - np.prod(1.0 - h, axis=-1)


EFFECT = "lnhr"   # primary effect scale: pooled log hazard ratio over the window ("rd" = risk difference F_T - F_C)


def _lnhr(ET, RT, EC, RC):
    """Pooled per-minute log hazard ratio over the window (0.5 continuity correction on events)."""
    et, rt, ec, rc = ET.sum(-1), RT.sum(-1), EC.sum(-1), RC.sum(-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log((et + 0.5) / rt) - np.log((ec + 0.5) / rc)


class Family:
    """Treated calls, their control pool and exact strata (with fallbacks); outcome matrices cached per outcome."""

    def __init__(self, P: Prep, cl: str, name: str, t_idx, cov_t, c_idx, cov_c):
        self.P, self.cl, self.name = P, cl, name
        self.t_idx, self.c_idx = t_idx, c_idx
        self.t_lev, self.t_key, self.ckeys = strata_assign(cov_t, cov_c, P.agent[t_idx], P.agent[c_idx])
        self._cache = {}

    def mats(self, which: str, o: str):
        """(event, at-risk) matrices (n x W, float32) and day index for treated ('t') or controls ('c')."""
        k = (which, o)
        if k not in self._cache:
            idx = self.t_idx if which == "t" else self.c_idx
            W = WIN[o]
            ev, cut = self.P.outcomes(idx, self.cl)[o]
            j = np.arange(W)[None, :]
            atrisk = (cut[:, None] > j) & (ev[:, None] >= j)
            event = atrisk & (np.floor(ev)[:, None] == j) & (ev[:, None] < cut[:, None])
            self._cache[k] = (event.astype(np.float32), atrisk.astype(np.float32), self.P.day[idx])
        return self._cache[k]

    def cell(self, o: str, sel: np.ndarray | None = None) -> "Cell":
        sel = np.ones(len(self.t_idx), bool) if sel is None else sel
        return Cell(self, o, sel)

    @property
    def levels(self):
        return np.bincount(self.t_lev + 1, minlength=len(LEVELS) + 1).tolist()


def _bincount_sdw(s, d, X, S, nd):
    """Sum rows of X (n x W) into an (S, nd, W) array by stratum s and day d."""
    W = X.shape[1]
    flat = s * nd + d
    out = np.zeros((S * nd, W))
    for w in range(W):
        out[:, w] = np.bincount(flat, weights=X[:, w], minlength=S * nd)
    return out.reshape(S, nd, W)


class Cell:
    """A subset of a family's treated calls vs all controls in their strata (each treated call has total control
    weight 1, spread equally over its stratum). Two-way day-block bootstrap: treated and control rows both carry their
    own day's multiplicity; a stratum with no control in a draw drops its treated rows from that draw."""

    def __init__(self, fam: Family, o: str, sel: np.ndarray):
        P = fam.P
        nd = len(P.days)
        self.nd, self.o = nd, o
        ok = sel & (fam.t_lev >= 0)
        self.n_t = int(ok.sum())
        self.n_unmatched = int((sel & (fam.t_lev < 0)).sum())
        W = WIN[o]
        if self.n_t == 0:
            return
        Et, Rt, dt_ = fam.mats("t", o)
        Ec, Rc, dc = fam.mats("c", o)
        parts_t, parts_c = [], []
        S = 0
        for li in np.unique(fam.t_lev[ok]):
            tsel = np.flatnonzero(ok & (fam.t_lev == li))
            uk, inv = np.unique(fam.t_key[tsel], return_inverse=True)
            kc = fam.ckeys[li]
            pos = np.searchsorted(uk, kc)
            pos_c = np.minimum(pos, len(uk) - 1)
            cm = np.flatnonzero(uk[pos_c] == kc)
            parts_t.append((tsel, S + inv))
            parts_c.append((cm, S + pos_c[cm]))
            S += len(uk)
        self.S = S
        ti = np.concatenate([p[0] for p in parts_t])
        ts = np.concatenate([p[1] for p in parts_t])
        ci = np.concatenate([p[0] for p in parts_c])
        cs = np.concatenate([p[1] for p in parts_c])
        self.ETs = _bincount_sdw(ts, dt_[ti], Et[ti], S, nd)
        self.RTs = _bincount_sdw(ts, dt_[ti], Rt[ti], S, nd)
        self.Tsd = np.bincount(ts * nd + dt_[ti], minlength=S * nd).reshape(S, nd).astype(float)
        self.Esd = _bincount_sdw(cs, dc[ci], Ec[ci], S, nd)
        self.Rsd = _bincount_sdw(cs, dc[ci], Rc[ci], S, nd)
        self.Nsd = np.bincount(cs * nd + dc[ci], minlength=S * nd).reshape(S, nd).astype(float)

    def _arms(self, m: np.ndarray):
        """Arm sums (ET, RT, EC, RC), each (b, W), for day multiplicities m (b, nd)."""
        Tm = m @ self.Tsd.T
        Nm = m @ self.Nsd.T
        valid = (Nm > 0).astype(float)
        wC = np.where(Nm > 0, Tm / np.maximum(Nm, 1e-12), 0.0)
        ET = np.einsum("bs,bsw->bw", valid, np.einsum("bd,sdw->bsw", m, self.ETs))
        RT = np.einsum("bs,bsw->bw", valid, np.einsum("bd,sdw->bsw", m, self.RTs))
        EC = np.einsum("bs,bsw->bw", wC, np.einsum("bd,sdw->bsw", m, self.Esd))
        RC = np.einsum("bs,bsw->bw", wC, np.einsum("bd,sdw->bsw", m, self.Rsd))
        return ET, RT, EC, RC

    def _effect(self, ET, RT, EC, RC):
        if EFFECT == "lnhr":
            return _lnhr(ET, RT, EC, RC)
        return _F(ET, RT) - _F(EC, RC)

    def point(self):
        """(effect on the EFFECT scale, F_kick, F_ctrl)."""
        if self.n_t == 0:
            return np.nan, np.nan, np.nan
        ET, RT, EC, RC = self._arms(np.ones((1, self.nd)))
        return float(self._effect(ET, RT, EC, RC)[0]), float(_F(ET, RT)[0]), float(_F(EC, RC)[0])

    def boot(self, C: np.ndarray, chunk: int = 50):
        """C: (B, nd) day multiplicities. Returns effect draws (B,)."""
        if self.n_t == 0:
            return np.full(C.shape[0], np.nan)
        out = []
        for b0 in range(0, C.shape[0], chunk):
            out.append(self._effect(*self._arms(C[b0:b0 + chunk])))
        return np.concatenate(out)


def day_draws(nd: int, B: int, rng) -> np.ndarray:
    return rng.multinomial(nd, np.full(nd, 1.0 / nd), size=B).astype(float)


def summarize_draws(point, draws):
    d = draws[np.isfinite(draws)]
    if len(d) < 20 or not np.isfinite(point):
        return {"est": point, "lo": np.nan, "hi": np.nan, "se": np.nan}
    return {"est": float(point), "lo": float(np.percentile(d, 2.5)), "hi": float(np.percentile(d, 97.5)),
            "se": float(np.std(d))}


def fit_recovery(dmid: np.ndarray, R: np.ndarray, w: np.ndarray):
    """Weighted LS fit of R(delta) = 1 - a exp(-delta / tau). Returns (a, tau, delta_half)."""
    ok = np.isfinite(R) & np.isfinite(w) & (w > 0) & np.isfinite(dmid)
    if ok.sum() < 2:
        return np.nan, np.nan, np.nan
    A = np.linspace(0, 1, 51)[:, None, None]
    T = np.geomspace(0.5, 480, 64)[None, :, None]
    pred = 1 - A * np.exp(-dmid[ok][None, None, :] / T)
    sse = ((pred - R[ok][None, None, :]) ** 2 * w[ok][None, None, :]).sum(-1)
    ia, it = np.unravel_index(np.argmin(sse), sse.shape)
    a, tau = float(A[ia, 0, 0]), float(T[0, it, 0])
    dh = tau * np.log(2 * a) if a > 0.5 else 0.0
    return a, tau, dh


MIN_E1_STRATUM = 10


def _ref(e1: dict, ages: np.ndarray):
    """E1 reference standardized to the stratum mix (age bin: idle 0-3, active 4-6) of a treated set: (point, draws).

    e1[("age", s)] = (pt, draws, n) per age bin; e1[rs] = pooled by read state (fallback when a bin has < 10 primers)."""
    if len(ages) == 0:
        return np.nan, None
    pt, dr = 0.0, 0.0
    for sbin in np.unique(ages):
        w = float(np.mean(ages == sbin))
        cand = e1.get(("age", int(sbin)))
        if cand is None or cand[2] < MIN_E1_STRATUM or not np.isfinite(cand[0]):
            cand = e1.get(1 if sbin <= 3 else 0)
        if cand is None or not np.isfinite(cand[0]):
            return np.nan, None
        pt = pt + w * cand[0]
        dr = dr + w * cand[1]
    return pt, dr


def _ratio(e2_pt, e2_dr, e1_pt, e1_dr):
    if e1_dr is None or not np.isfinite(e1_pt):
        return {"est": np.nan, "lo": np.nan, "hi": np.nan, "se": np.nan}, None
    Rpt = e2_pt / e1_pt if abs(e1_pt) > 1e-9 else np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        Rd = e2_dr / e1_dr
    return summarize_draws(Rpt, Rd), Rd


def analyze_class(P: Prep, cl: str, rng, B: int = B_BOOT, outcomes=("O1", "O2", "O3"), draws: np.ndarray | None = None,
                  min_bin: int = 10, quiet_s: float = QUIET_S) -> dict:
    """All estimates for one class in one period."""
    D = build_design(P, cl, rng, quiet_s=quiet_s)
    res = {"class": cl, "n_kick_calls": D["n_kick_calls"], "n_primers": D["n_primers"], "primary": PRIMARY[cl],
           "quiet_min": quiet_s / 60}
    if D["n_primers"] == 0:
        return res
    nd = len(P.days)
    C = draws if draws is not None else day_draws(nd, B, rng)
    primer, e1c, fam1 = D["primer"], D["e1c"], D["fam1"]
    ir_p = P.idle_at_read[primer]
    res["match_levels_e1"] = fam1.levels
    res["n_primers_idle"] = int(ir_p.sum())
    res["n_effective"] = int(D["eff"].sum())
    res["frac_effective_idle"] = float(D["eff"].sum() / max(ir_p.sum(), 1))
    Ls = D["L"][np.isfinite(D["L"])]
    res["L_median"] = float(np.median(Ls)) if len(Ls) else np.nan
    res["L_q25_q75"] = np.percentile(Ls, [25, 75]).tolist() if len(Ls) else [np.nan, np.nan]
    res["L_n"] = int(len(Ls))
    ev1 = D["ev1_primer"]
    dead = ev1[ir_p & (ev1 <= WIN["O1"])]
    res["dead_time_median_min"] = float(np.median(dead)) if len(dead) else np.nan
    res["n_second"] = int(len(D.get("sec", [])))
    res["n_batched"] = int(D["batched"].sum())
    if "sec" in D:
        res["second_by_bin"] = dict(zip(DELTA_LABELS, np.bincount(D["bin_t"], minlength=len(DELTA_LABELS)).tolist()))
        res["second_by_status"] = {STATUS_NAMES[v]: int((D["st_t"] == v).sum()) for v in STATUS.values()}
        res["match_levels_e2"] = D["fam2"].levels
        res["delta_median_min"] = float(np.median(D["d_t"]))
        res["n_second_idle"] = int(P.idle_at_read[D["sec"]].sum())
    outs = {}
    for o in outcomes:
        if o == "O3" and P.writes_per_agentday < 1.0:
            outs[o] = {"skipped": f"writes per agent-day {P.writes_per_agentday:.2f} < 1"}
            continue
        idle_o = o in ("O1", "O1a")
        reads = (1,) if idle_o else (0,)        # O1/O1a: idle-at-read rows only; O2/O2c/O3: active-at-read rows only
        rmask_p = ir_p if idle_o else ~ir_p
        if not rmask_p.any():
            outs[o] = {"skipped": "no primers in this read state"}
            continue
        r = {}
        e1 = {}
        ab_p = age_bin(P, primer)
        for sbin in np.unique(ab_p):
            if idle_o != (sbin <= 3):
                continue
            sel = ab_p == sbin
            cell = fam1.cell(o, sel)
            if cell.n_t:
                e1[("age", int(sbin))] = (cell.point()[0], cell.boot(C), cell.n_t)
        for rs in reads:
            sel = ir_p == bool(rs)
            cell = fam1.cell(o, sel)
            pt = cell.point()
            dr = cell.boot(C)
            e1[rs] = (pt[0], dr, cell.n_t)
            r[f"E1_read{rs}"] = {**summarize_draws(pt[0], dr), "F_kick": pt[1], "F_ctrl": pt[2], "n": cell.n_t,
                                 "unmatched": cell.n_unmatched}
        r["E1"] = r[f"E1_read{reads[0]}"]
        e1_ok = bool(r["E1"]["n"] >= 20 and np.isfinite(r["E1"]["lo"]) and r["E1"]["lo"] > 0)
        r["E1_positive"] = e1_ok
        if "sec" in D:
            sec, fam2 = D["sec"], D["fam2"]
            ir_s = P.idle_at_read[sec]
            ab_s = age_bin(P, sec)
            allowed = ir_s if idle_o else ~ir_s
            bins_out, dm, Rb, wts, Rdraws, nb = {}, [], [], [], [], []
            for b, lab in enumerate(DELTA_LABELS):
                sel = allowed & (D["bin_t"] == b)
                n_b = int(sel.sum())
                if n_b == 0:
                    bins_out[lab] = {"n": 0}
                    dm.append(np.nan); Rb.append(np.nan); wts.append(np.nan); nb.append(0)
                    Rdraws.append(np.full(C.shape[0], np.nan))
                    continue
                cell = fam2.cell(o, sel)
                pt = cell.point()
                dr = cell.boot(C)
                e1pt, e1dr = _ref(e1, ab_s[sel])
                Rs, Rd = _ratio(pt[0], dr, e1pt, e1dr)
                d_med = float(np.median(D["d_t"][sel]))
                bins_out[lab] = {"n": cell.n_t, "E2": summarize_draws(pt[0], dr), "F_kick": pt[1], "F_ctrl": pt[2],
                                 "E1_ref": e1pt, "R": Rs, "delta_med": d_med}
                dm.append(d_med); Rb.append(Rs["est"]); nb.append(cell.n_t)
                if Rd is not None:
                    rd = Rd[np.isfinite(Rd)]
                    wts.append(1.0 / max(np.var(np.clip(rd, -3, 4)), 1e-3) if len(rd) > 20 else np.nan)
                    Rdraws.append(Rd)
                else:
                    wts.append(np.nan)
                    Rdraws.append(np.full(C.shape[0], np.nan))
            r["E2_bins"] = bins_out
            # pooled spacing ranges (A4): (0, 15], (15, 60], (60, 240] min
            pool_out = {}
            for lab, lo_, hi_ in (("0-15", 0.0, 15.0), ("15-60", 15.0, 60.0), ("60-240", 60.0, 240.0)):
                sel = allowed & (D["d_t"] > lo_) & (D["d_t"] <= hi_)
                if sel.sum() < 5:
                    continue
                cell = fam2.cell(o, sel)
                pt = cell.point()
                dr = cell.boot(C)
                e1pt, e1dr = _ref(e1, ab_s[sel])
                Rs, _ = _ratio(pt[0], dr, e1pt, e1dr)
                pool_out[lab] = {"n": cell.n_t, "E2": summarize_draws(pt[0], dr), "E1_ref": e1pt, "R": Rs,
                                 "F_kick": pt[1], "F_ctrl": pt[2]}
            r["R_pool"] = pool_out
            powered = np.array(nb) >= min_bin
            dmv, Rv, wv = np.array(dm, float), np.where(powered, np.array(Rb, float), np.nan), np.array(wts, float)
            pb = np.flatnonzero(powered & np.isfinite(Rv))
            if len(pb):
                r["R_short"] = {"bin": DELTA_LABELS[pb[0]], **bins_out[DELTA_LABELS[pb[0]]]["R"]}
                r["R_long"] = {"bin": DELTA_LABELS[pb[-1]], **bins_out[DELTA_LABELS[pb[-1]]]["R"]}
                if len(pb) >= 3:
                    from scipy.stats import spearmanr
                    r["R_trend_spearman"] = float(spearmanr(dmv[pb], Rv[pb]).statistic)
            if e1_ok and len(pb) >= 2:
                a, tau, dh = fit_recovery(dmv, Rv, wv)
                Rdr = np.array(Rdraws)
                fits = np.array([fit_recovery(dmv, np.where(powered, Rdr[:, k], np.nan), wv) for k in range(Rdr.shape[1])])
                dhs = fits[:, 2]
                dhs_f = dhs[np.isfinite(dhs)]
                hb = np.clip(np.digitize(dhs_f, DELTA_EDGES[1:-1], right=True), 0, len(DELTA_LABELS) - 1)
                hb[dhs_f <= 0] = -1
                r["fit"] = {"a": a, "tau": tau, "delta_half": dh,
                            "delta_half_lo": float(np.percentile(dhs_f, 2.5)) if len(dhs_f) else np.nan,
                            "delta_half_hi": float(np.percentile(dhs_f, 97.5)) if len(dhs_f) else np.nan,
                            "delta_half_p80": float(np.percentile(dhs_f, 80)) if len(dhs_f) else np.nan,
                            "a_lo": float(np.nanpercentile(fits[:, 0], 2.5)), "a_hi": float(np.nanpercentile(fits[:, 0], 97.5)),
                            "share_no_window": float(np.mean(dhs_f <= 0)) if len(dhs_f) else np.nan,
                            "draw_bins": {("none" if k < 0 else DELTA_LABELS[k]): int((hb == k).sum()) for k in np.unique(hb)},
                            "shortest_powered_bin": DELTA_LABELS[pb[0]]}
            st = {}
            for sname, sv in STATUS.items():
                sel = allowed & (D["st_t"] == sv)
                if sel.sum() < 5:
                    continue
                cell = fam2.cell(o, sel)
                pt = cell.point()
                dr = cell.boot(C)
                e1pt, e1dr = _ref(e1, ab_s[sel])
                Rs, _ = _ratio(pt[0], dr, e1pt, e1dr)
                st[sname] = {"n": cell.n_t, "E2": summarize_draws(pt[0], dr), "R": Rs,
                             "delta_med": float(np.median(D["d_t"][sel]))}
            r["by_status"] = st
        if "bat_t" in D:
            bt, famb = D["bat_t"], D["famb"]
            sel = P.idle_at_read[bt] if idle_o else ~P.idle_at_read[bt]
            if sel.sum():
                cell = famb.cell(o, sel)
                pt = cell.point()
                dr = cell.boot(C)
                e1pt, e1dr = _ref(e1, age_bin(P, bt[sel]))
                Rs, _ = _ratio(pt[0], dr, e1pt, e1dr)
                r["batched"] = {"n": cell.n_t, "marginal": summarize_draws(pt[0], dr), "R": Rs}
        outs[o] = r
    res["outcomes"] = outs
    return res


PRIMARY = {"N": "O1", "H": "O2", "A": "O2", "D": "O1"}


# =============================================================================== helpers for native tests / confirmation

def e1_table(P: Prep, D: dict, o: str, C: np.ndarray) -> dict:
    """E1 cells by age bin and pooled for the read state of outcome o (same as inside analyze_class)."""
    primer, fam1 = D["primer"], D["fam1"]
    ir = P.idle_at_read[primer]
    ab = age_bin(P, primer)
    e1 = {}
    idle_o = o in ("O1", "O1a")
    for sbin in np.unique(ab):
        if idle_o != (sbin <= 3):
            continue
        cell = fam1.cell(o, ab == sbin)
        if cell.n_t:
            e1[("age", int(sbin))] = (cell.point()[0], cell.boot(C), cell.n_t)
    rs = 1 if idle_o else 0
    cell = fam1.cell(o, ir == bool(rs))
    pt = cell.point()
    dr = cell.boot(C)
    e1[rs] = (pt[0], dr, cell.n_t)
    e1["summary"] = {**summarize_draws(pt[0], dr), "F_kick": pt[1], "F_ctrl": pt[2], "n": cell.n_t}
    return e1


def ratio_for(P: Prep, D: dict, o: str, sel: np.ndarray, e1: dict, C: np.ndarray, fam_key: str = "fam2",
              t_key: str = "sec") -> tuple[dict, np.ndarray | None]:
    """E2 and R for a custom subset `sel` of a family's treated rows (default: second kicks)."""
    fam = D[fam_key]
    rmask = P.idle_at_read[D[t_key]] if o in ("O1", "O1a") else ~P.idle_at_read[D[t_key]]
    sel = sel & rmask
    if sel.sum() == 0:
        return {"n": 0}, None
    cell = fam.cell(o, sel)
    pt = cell.point()
    dr = cell.boot(C)
    e1pt, e1dr = _ref(e1, age_bin(P, D[t_key][sel]))
    Rs, Rd = _ratio(pt[0], dr, e1pt, e1dr)
    return {"n": cell.n_t, "E2": summarize_draws(pt[0], dr), "F_kick": pt[1], "F_ctrl": pt[2], "E1_ref": e1pt,
            "R": Rs}, Rd
