"""Village-skeleton simulator (DQ8): synthetic swarms on a real period unit's skeleton, written in the shared tables'
schemas, so any hypothesis pipeline can run unchanged on synthetic input with a known (planted) truth.

Why: almost every hypothesis built its own "synthetic world on real schedules" for axis-F validation (H12, H25, H26,
H29, H31, H34, H36, H38, H39, ...), inconsistently, and several hit the same traps independently (shared fields that
look like coupling or branching, day edges and stalls that fake co-activation, lull filters that bias variance
ratios, controls that condition on the future). One tested simulator makes every validation comparable.

1. Skeleton (structure, not outcomes)
   extract_skeleton(unit_id)   one `period_units` unit from the shared tables:
       roster and presence (agents on the roster each day, each agent's first..last record span),
       real minute states (only to derive rate profiles: activity, P(talk | active), messages per minute),
       rooms over time (rooms_timeline), kick times / kinds / targets (kicks_classified), the operator schedule
       (stall_minutes.scheduled), real stalls (stall_minutes.explained) and silence reasons, statement counts per
       agent x 30-min window (embeddings/statements, chat), project-label coverage (project_states, W = 30),
       call windows (call_windows: each turn's call start / end, used for the read-out delay).
       Held-out units raise HoldoutError unless allow_holdout=True (confirmatory designs only). No text is read.
   toy_skeleton(...)           the same structure without any data (tests, calibration, long weekday timelines).

2. Dynamics (pluggable, one model per channel; all optional)
   ActivityModel   1-min kinetic Ising (parallel Glauber) on +-1 activity spins. With J = 0 and no fields it is the
                   independent rate-matched baseline: each agent is a two-state Markov chain whose occupancy follows
                   its own real (smoothed) activity profile and whose switching rate matches its real one, exactly:
                   P(+|+) = 1 - c/(2p), P(+|-) = c/(2(1-p))  ->  h = (logit a + logit b)/4, K = (logit a - logit b)/4.
                   Options: coupling J to the others' deviations from their expected spin (mean field, village or
                   room scope), delay = none | lag (L_i minutes) | readout (the others as they were at the agent's
                   last call start: H08's read-out rule), shared fields (global OU, room OU, time-of-day, day,
                   weekday, agent-day), kick responses (field or catalytic, from skeleton kicks or a synthetic
                   nudger that targets agents idle >= 10 min, as the real nudger does).
   EdgeDrive       day-edge drive: every agent starts within `jitter` min of the operator's resume and stops
                   within `jitter` of the pause (H38's regime-III scaffold co-activation), plus an optional burst.
   StallModel      planted platform stalls (everyone silent but maybe one agent; marked with infra reasons with
                   probability r), or source="real" to replay the unit's real stalls and scheduled-off minutes.
   TalkModel       "bernoulli": talk = active & Bernoulli(real P(talk | active) profile), rate-matched messages;
                   "hawkes": multivariate Hawkes (exponential kernel, self n_s, cross n_x shared over the scope's
                   other agents), simulated exactly by the cluster (branching) construction, baseline solved so the
                   stationary rate matches each agent's real message rate (mu = (I - A) r). Parents are recorded.
   ContentModel    "ou": vector-spin (O(n)) kinetics per 30-min window in d = 32 with anisotropic noise
                   (participation ratio ~8), room or village mean-field coupling J, drives (global day, room day,
                   kickoff relaxation, time of day); "degroot": read-out DeGroot averaging toward the previous
                   window's room statements with weight alpha. Statements = unit(static + latent + noise), emitted
                   with the real statement counts per agent-window, float16 unit vectors like the shared white32.
   ProjectModel    kinetic Potts herding over q projects per 30-min window (choice prob ~ exp(h_a + J frac_a)),
                   with herding "waves" (a random project recruits each agent with prob wave_p), observed only where
                   the real project labels exist (label coverage).
   KickModel       field / catalytic responses to kicks (see ActivityModel).

3. Outputs: Sim.tables() -> dict of polars frames in the shared schemas: activity_bins, chat_core,
   chat_mentions_clean, statements (+ Sim.statement_vectors, n x 32 float16), agent_win30 (+ vectors), project_states,
   kicks_classified, stall_minutes (subset of columns), reasons, call_windows (lite: the skeleton's turns), plus
   truth frames (kick_truth, msg_truth). Sim.spins(channel) gives per-day (T x N) +-1 arrays and minute indices.
   Sim.truth holds the planted parameters (J, n_x, n_s, alpha, ...) and realized quantities (g_true, branching).

Presets: DYNAMICS (names in the DQ8 brief) and preset(name, **overrides) -> dict of models; simulate(sk, seed, **models).

Usage
    import simulate as SIM
    sk = SIM.extract_skeleton("41")                          # or SIM.toy_skeleton(N=10, n_days=5)
    sim = SIM.simulate(sk, seed=1, **SIM.preset("ising_readout", J=0.6))
    tabs = sim.tables()                                      # activity_bins, chat_core, statements, ...
    days = sim.spins("activity")                             # [(S (T x N, +-1), minute), ...]
    print(sim.truth["activity"])                             # planted J, realized g_true

Docs: infra/data-quality/simulator_and_nulls.md. Tests: infra/shared/tests/test_simulate.py. Null library: nulls.py.
Thread use: BLAS / polars capped at 2 threads (set before numpy / polars are imported).
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import datetime as dt  # noqa: E402
import math  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SH = ROOT / "data/processed/shared"
UTC = dt.timezone.utc

# reason codes (outages.py / H38) and activity_bins state codes (build_derived.py)
R_NONE, R_PRE, R_POST, R_INFRA, R_CONSOL, R_PAUSE = 0, 1, 2, 3, 4, 5
S_SILENT, S_IDLE, S_ACT, S_TALK = 1, 2, 3, 4
D_CONTENT = 32
WIN_MIN = 30


class HoldoutError(RuntimeError):
    """Raised when a skeleton is requested for a held-out unit without allow_holdout=True."""


# ============================================================================================ small helpers
def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def _logit(p):
    return np.log(p) - np.log1p(-p)


def _moving_avg(X: np.ndarray, mask: np.ndarray, L: int) -> np.ndarray:
    """Centered moving average of X (T x N) over the masked minutes inside a +-L//2 window (per column)."""
    T = X.shape[0]
    h = L // 2
    Xm = np.where(mask, X, 0.0).astype(np.float64)
    cs = np.vstack([np.zeros((1, X.shape[1])), np.cumsum(Xm, 0)])
    cm = np.vstack([np.zeros((1, X.shape[1])), np.cumsum(mask.astype(np.float64), 0)])
    lo = np.clip(np.arange(T) - h, 0, T)
    hi = np.clip(np.arange(T) + h + 1, 0, T)
    s = cs[hi] - cs[lo]
    c = cm[hi] - cm[lo]
    return np.where(c > 0, s / np.maximum(c, 1), 0.0)


def _ou(n: int, sd: float, tau: float, rng, size=None) -> np.ndarray:
    """Stationary AR(1) series (length n, optional extra dims) with marginal sd and correlation time tau (steps)."""
    shape = (n,) if size is None else (n,) + tuple(np.atleast_1d(size))
    if sd <= 0 or n == 0:
        return np.zeros(shape)
    a = math.exp(-1.0 / max(tau, 1e-6))
    e = rng.standard_normal(shape) * sd * math.sqrt(1 - a * a)
    x = np.empty(shape)
    x[0] = rng.standard_normal(shape[1:]) * sd
    for t in range(1, n):
        x[t] = a * x[t - 1] + e[t]
    return x


def _runs(x: np.ndarray):
    x = np.asarray(x, bool)
    if not x.any():
        return np.zeros(0, int), np.zeros(0, int)
    d = np.diff(np.r_[0, x.astype(np.int8), 0])
    st, en = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    return st, en - st


def aniso_shape(rng, d: int = D_CONTENT, k0: float = 4.0) -> np.ndarray:
    """d x d matrix L with L L^T = Q diag(lam) Q^T, lam ~ exp(-k/k0) normalized to trace 1 (PR ~ 2 k0)."""
    lam = np.exp(-np.arange(d) / k0)
    lam /= lam.sum()
    Q, _ = np.linalg.qr(rng.standard_normal((d, d)))
    return Q * np.sqrt(lam)


# ============================================================================================ skeleton
@dataclass
class DaySkel:
    pt_date: str
    weekday: int                 # 0 = Monday
    win_start: dt.datetime       # calendar window start (UTC); minute m = win_start + m min
    minute0: int                 # first minute of the unit on this day (window minute index)
    T: int                       # minutes of the unit on this day
    active_offset_min: int       # activity_bins.active_min = active_offset_min + minute
    period_day: int              # 0-based day index within the goal period (project_states.day)
    on_roster: np.ndarray        # (N,) bool
    span: np.ndarray             # (T, N) bool: between the agent's first and last record of the day
    state: np.ndarray            # (T, N) int8 real activity_bins state (0 = not on roster); profiles only
    room: np.ndarray             # (T, N) int8
    sched_off: np.ndarray        # (T,) bool operator-paused minutes
    stall: np.ndarray            # (T,) bool real explained joint silences (H38 stall)
    reasons: np.ndarray          # (T, N) int8 real silence reasons
    msg_count: np.ndarray        # (T, N) int16 real agent chat messages per minute
    stmt_count: np.ndarray       # (W, N) int16 real chat statements per 30-min window (win30 = win0 + w)
    win0: int
    label_mask: np.ndarray       # (W, N) bool real project label present (W = 30, sources all)
    calls: dict                  # agent idx -> (t_call_s, t_end_s, talk) arrays, seconds since win_start
    kicks: list                  # dicts: minute (window index), t_s, kind, subkind, targets (idx array), room

    @property
    def minutes(self) -> np.ndarray:
        return np.arange(self.minute0, self.minute0 + self.T)

    @property
    def W(self) -> int:
        return self.stmt_count.shape[0]


@dataclass
class Skeleton:
    unit_id: str
    goal_no: int
    regime: str
    holdout: bool
    agents: np.ndarray           # (N,) int8 roster codes
    days: list
    source: str = "real"
    smooth_min: int = 121
    _prof: dict = field(default_factory=dict, repr=False)

    @property
    def N(self) -> int:
        return len(self.agents)

    def profiles(self) -> dict:
        """Rate profiles from the real states (cached): p_act, q_talk (P(talk | active)), r_msg (messages/min) per day,
        and per-agent switching rate `switch` and messages per talk minute `mpt`."""
        if self._prof:
            return self._prof
        p_act, q_talk, r_msg = [], [], []
        n_sw = np.zeros(self.N)
        n_pair = np.zeros(self.N)
        n_msg = np.zeros(self.N)
        n_tm = np.zeros(self.N)
        for d in self.days:
            act = d.state >= S_ACT
            talk = d.state == S_TALK
            sp = d.span
            pa = _moving_avg(act.astype(float), sp, self.smooth_min)
            p_act.append(np.where(sp, np.clip(pa, 0.01, 0.98), 0.0))
            num = _moving_avg(talk.astype(float), sp, self.smooth_min)
            q = np.where(pa > 0, num / np.maximum(pa, 1e-9), 0.0)
            q_talk.append(np.where(sp, np.clip(q, 0.0, 0.95), 0.0))
            r_msg.append(np.where(sp, _moving_avg(d.msg_count.astype(float), sp, self.smooth_min), 0.0))
            both = sp[1:] & sp[:-1]
            n_sw += ((act[1:] != act[:-1]) & both).sum(0)
            n_pair += both.sum(0)
            n_msg += np.where(talk, d.msg_count, 0).sum(0)
            n_tm += talk.sum(0)
        sw = np.where(n_pair > 0, n_sw / np.maximum(n_pair, 1), 0.2)
        self._prof = {"p_act": p_act, "q_talk": q_talk, "r_msg": r_msg, "switch": np.clip(sw, 0.01, 0.9),
                      "mpt": np.where(n_tm > 0, n_msg / np.maximum(n_tm, 1), 1.0)}
        return self._prof

    def summary(self) -> dict:
        return {"unit_id": self.unit_id, "goal_no": self.goal_no, "regime": self.regime, "holdout": self.holdout,
                "N": self.N, "n_days": len(self.days), "minutes": int(sum(d.T for d in self.days)),
                "n_kicks": int(sum(len(d.kicks) for d in self.days)),
                "n_stmts": int(sum(int(d.stmt_count.sum()) for d in self.days)),
                "n_calls": int(sum(sum(len(v[0]) for v in d.calls.values()) for d in self.days)),
                "rooms": sorted({int(x) for d in self.days for x in np.unique(d.room)}), "source": self.source}


def activity_bins_table() -> str:
    """The corrected sidecar when present (activity_bins.parquet drops a day-specific share of events: see
    activity_bins_fixed.py), else the original with a warning."""
    if (SH / "activity_bins_fixed.parquet").exists():
        return "activity_bins_fixed"
    import warnings
    warnings.warn("activity_bins_fixed.parquet missing: using activity_bins.parquet, which drops events "
                  "(run infra/shared/activity_bins_fixed.py)")
    return "activity_bins"


def _scan(name: str):
    import polars as pl
    return pl.scan_parquet(SH / f"{name}.parquet")


def extract_skeleton(unit_id: str, allow_holdout: bool = False, smooth_min: int = 121) -> Skeleton:
    """Skeleton of one `period_units` unit from the shared tables (no text). See the module docstring."""
    import polars as pl
    sys_path_common()
    from common import holdout_mask

    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("unit_id") == unit_id)
    if pu.height != 1:
        raise KeyError(f"unknown unit {unit_id!r}")
    u = pu.row(0, named=True)
    days = sorted(u["days"])
    if (u["holdout"] or any(holdout_mask(days, [u["goal_no"]] * len(days)))) and not allow_holdout:
        raise HoldoutError(f"unit {unit_id} is (partly) held out; pass allow_holdout=True for a confirmatory design")
    cal_all = pl.read_parquet(SH / "calendar.parquet").sort("pt_date")
    gdays = cal_all.filter(pl.col("goal_no") == u["goal_no"])["pt_date"].to_list()
    pday = {d: i for i, d in enumerate(gdays)}
    cal = cal_all.filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
    ab = (_scan(activity_bins_table()).filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "minute", "agent", "state").collect())
    ab = ab.filter(pl.col("agent").is_in(ros["agent"].implode()))
    # unit minute ranges per day
    rng_day = {}
    for r in cal.iter_rows(named=True):
        ws = r["win_start"]
        Tfull = int(r["window_s"] // 60 + 1)
        lo = max(0, int((u["start"] - ws).total_seconds() // 60)) if u["start"] > ws else 0
        hi = min(Tfull - 1, int((u["end"] - ws).total_seconds() // 60))
        rng_day[r["pt_date"]] = (lo, hi, Tfull, ws, int(r["active_offset_s"] // 60), int(r["weekday"]))
    inr = pl.concat([ab.filter((pl.col("pt_date") == d) & pl.col("minute").is_between(v[0], v[1]))
                     for d, v in rng_day.items()])
    agents = np.array(sorted(inr.filter(pl.col("state") >= S_ACT)["agent"].unique().to_list()), dtype=np.int8)
    if len(agents) == 0:
        raise ValueError(f"unit {unit_id}: no active agents")
    aix = {int(a): i for i, a in enumerate(agents)}
    N = len(agents)
    ag_list = [int(a) for a in agents]

    smin = (_scan("states_min").filter(pl.col("pt_date").is_in(days) & pl.col("agent").is_in(ag_list))
            .select("pt_date", "minute", "agent", "in_span").collect())
    stm = (_scan("stall_minutes").filter(pl.col("pt_date").is_in(days))
           .select("pt_date", "minute", "scheduled", "explained").collect())
    rea = (_scan("reasons").filter(pl.col("pt_date").is_in(days) & pl.col("agent").is_in(ag_list)).collect())
    chat = (_scan("chat_core").filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind") == "agent")
                                      & pl.col("agent").is_in(ag_list)).select("t", "pt_date", "agent").collect())
    st = (_scan("embeddings/statements").filter(pl.col("pt_date").is_in(days) & (pl.col("kind") == "chat")
                                                & pl.col("agent").is_in(ag_list) & pl.col("win30").is_not_null())
          .group_by("pt_date", "win30", "agent").len().collect())
    ps = (_scan("project_states").filter(pl.col("pt_date").is_in(days) & (pl.col("w_min") == 30)
                                         & (pl.col("sources") == "all") & pl.col("agent").is_in(ag_list))
          .select("pt_date", "win", "agent").collect())
    cw = (_scan("call_windows").filter(pl.col("pt_date").is_in(days) & pl.col("agent").is_in(ag_list))
          .select("pt_date", "agent", "t_call", "t_end", "talk").collect())
    kc = (_scan("kicks_classified").filter(pl.col("pt_date").is_in(days))
          .select("t", "pt_date", "kind", "subkind", "targets", "room").collect())
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").filter(pl.col("agent").is_in(ag_list))

    out_days = []
    for d in days:
        lo, hi, Tfull, ws, aoff, wd = rng_day[d]
        T = hi - lo + 1
        mins = np.arange(lo, hi + 1)

        def grid(df, col, dtype, fill):
            A = np.full((T, N), fill, dtype=dtype)
            x = df.filter((pl.col("pt_date") == d) & pl.col("minute").is_between(lo, hi))
            if x.height:
                ii = x["minute"].to_numpy() - lo
                jj = np.array([aix[int(a)] for a in x["agent"].to_list()])
                A[ii, jj] = x[col].to_numpy().astype(dtype)
            return A

        state = grid(ab.filter(pl.col("agent").is_in(ag_list)), "state", np.int8, 0)
        on_roster = (state > 0).any(0)
        span = grid(smin, "in_span", bool, False) & (state > 0)
        reasons = grid(rea, "reason", np.int8, 0)
        s1 = stm.filter((pl.col("pt_date") == d) & pl.col("minute").is_between(lo, hi))
        sched = np.zeros(T, bool)
        stall = np.zeros(T, bool)
        if s1.height:
            sched[s1["minute"].to_numpy() - lo] = s1["scheduled"].to_numpy()
            stall[s1["minute"].to_numpy() - lo] = s1["explained"].to_numpy()
        # messages per minute
        c1 = chat.filter(pl.col("pt_date") == d).with_columns(
            ((pl.col("t") - ws).dt.total_seconds() // 60).cast(pl.Int64).alias("minute"))
        c1 = c1.filter(pl.col("minute").is_between(lo, hi)).group_by("minute", "agent").len()
        msg = np.zeros((T, N), np.int16)
        if c1.height:
            msg[c1["minute"].to_numpy() - lo, [aix[int(a)] for a in c1["agent"].to_list()]] = c1["len"].to_numpy()
        # statements and labels per 30-min window
        w_lo, w_hi = lo // WIN_MIN, hi // WIN_MIN
        W = w_hi - w_lo + 1
        sc = np.zeros((W, N), np.int16)
        s2 = st.filter((pl.col("pt_date") == d) & pl.col("win30").is_between(w_lo, w_hi))
        if s2.height:
            sc[s2["win30"].to_numpy() - w_lo, [aix[int(a)] for a in s2["agent"].to_list()]] = s2["len"].to_numpy()
        lm = np.zeros((W, N), bool)
        p2 = ps.filter((pl.col("pt_date") == d) & pl.col("win").is_between(w_lo, w_hi))
        if p2.height:
            lm[p2["win"].to_numpy() - w_lo, [aix[int(a)] for a in p2["agent"].to_list()]] = True
        # rooms at minute midpoints
        room = np.zeros((T, N), np.int8)
        tmid = [ws + dt.timedelta(minutes=int(m) + 0.5) for m in mins]
        for a, i in aix.items():
            iv = rt.filter(pl.col("agent") == a).sort("t_start")
            if iv.height == 0:
                continue
            ts = iv["t_start"].to_list()
            te = iv["t_end"].to_list()
            rr = iv["room"].to_numpy()
            k = 0
            cur = int(rr[0])
            for t_i, tm in enumerate(tmid):
                while k + 1 < len(ts) and ts[k + 1] <= tm:
                    k += 1
                if ts[k] <= tm and (te[k] is None or tm < te[k]):
                    cur = int(rr[k])
                room[t_i, i] = cur
        # call windows
        calls = {}
        c3 = cw.filter(pl.col("pt_date") == d)
        for a, i in aix.items():
            x = c3.filter(pl.col("agent") == a).sort("t_call")
            if x.height:
                t0 = (x["t_call"] - ws).dt.total_seconds().to_numpy().astype(np.float64)
                t1 = (x["t_end"] - ws).dt.total_seconds().to_numpy().astype(np.float64)
                keep = (t0 >= lo * 60 - 600) & (t0 < (hi + 1) * 60)
                calls[i] = (t0[keep], t1[keep], x["talk"].to_numpy()[keep])
        # kicks
        kicks = []
        k1 = kc.filter(pl.col("pt_date") == d)
        for r in k1.iter_rows(named=True):
            ts_ = (r["t"] - ws).total_seconds()
            m = int(ts_ // 60)
            if m < lo or m > hi:
                continue
            tg = np.array([aix[int(a)] for a in (r["targets"] or []) if int(a) in aix], dtype=np.int64)
            kicks.append({"minute": m, "t_s": float(ts_), "kind": str(r["kind"]),
                          "subkind": None if r["subkind"] is None else str(r["subkind"]), "targets": tg,
                          "room": None if r["room"] is None else int(r["room"])})
        out_days.append(DaySkel(pt_date=d, weekday=wd, win_start=ws, minute0=lo, T=T, active_offset_min=aoff,
                                period_day=pday.get(d, 0), on_roster=on_roster, span=span, state=state, room=room,
                                sched_off=sched, stall=stall, reasons=reasons, msg_count=msg, stmt_count=sc,
                                win0=w_lo, label_mask=lm, calls=calls, kicks=kicks))
    return Skeleton(unit_id=unit_id, goal_no=int(u["goal_no"]), regime=str(u["regime"]), holdout=bool(u["holdout"]),
                    agents=agents, days=out_days, source="real", smooth_min=smooth_min)


def sys_path_common():
    import sys
    p = str(Path(__file__).resolve().parent)
    if p not in sys.path:
        sys.path.insert(0, p)


def eligible_units(min_agents: int = 4, min_days: int = 2, regime: str | None = None) -> list[str]:
    """Non-holdout period units with enough agents and days (for calibration designs)."""
    import polars as pl
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout") & (pl.col("n_agents") >= min_agents)
                                                            & (pl.col("n_days") >= min_days))
    if regime:
        pu = pu.filter(pl.col("regime") == regime)
    return pu["unit_id"].to_list()


def toy_skeleton(N: int = 10, n_days: int = 5, T: int = 240, n_rooms: int = 1, p_act: float = 0.45,
                 switch: float = 0.15, talk_frac: float = 0.15, msgs_per_talk: float = 1.2, stmt_rate: float = 1.5,
                 call_gap_min: float = 3.0, nudge_rate: float = 0.0015, mention_rate: float = 0.003,
                 edge_jitter: int = 15, label_cover: float = 0.7, start_date: str = "2030-01-07", seed: int = 0,
                 goal_no: int = 0, regime: str = "toy") -> Skeleton:
    """A data-free skeleton with village-like structure: heterogeneous agents (activity ~ Beta around p_act), a
    shared hump-shaped daily profile, staggered day edges (U{0..edge_jitter} min), fixed rooms, Poisson calls,
    nudges and mentions as kicks, Poisson statements, partial label coverage. Days are consecutive weekdays from
    start_date (2030-01-07 is a Monday), so weekday structure is available for placebo-date designs."""
    rng = np.random.default_rng(seed)
    agents = np.arange(N, dtype=np.int8)
    base = np.clip(rng.beta(4 * p_act / (1 - p_act + 1e-9), 4, N) if p_act < 1 else np.full(N, 0.9), 0.05, 0.95)
    rooms_of = (np.arange(N) * n_rooms // N).astype(np.int8)
    d0 = dt.date.fromisoformat(start_date)
    days, date = [], d0
    shape = 0.75 + 0.5 * np.sin(np.pi * (np.arange(T) + 0.5) / T)  # hump across the day
    W = int(math.ceil(T / WIN_MIN))
    for k in range(n_days):
        while date.weekday() >= 5:
            date += dt.timedelta(days=1)
        ws = dt.datetime(date.year, date.month, date.day, 17, 0, tzinfo=UTC)
        st_ = rng.integers(0, edge_jitter + 1, N)
        en_ = rng.integers(0, edge_jitter + 1, N)
        span = np.zeros((T, N), bool)
        for i in range(N):
            span[st_[i]:T - en_[i], i] = True
        pa = np.clip(base[None, :] * shape[:, None], 0.02, 0.97)
        # draw "real" states from the independent two-state chain (rate-matched) so profiles are consistent
        a = np.clip(1 - switch / (2 * pa), 0.002, 0.998)
        b = np.clip(switch / (2 * (1 - pa)), 0.002, 0.998)
        act = np.zeros((T, N), bool)
        s = rng.random(N) < pa[0]
        for t in range(T):
            if t:
                pr = np.where(s, a[t], b[t])
                s = rng.random(N) < pr
            act[t] = s & span[t]
        talk = act & (rng.random((T, N)) < talk_frac)
        state = np.where(talk, S_TALK, np.where(act, S_ACT, np.where(span & (rng.random((T, N)) < 0.3), S_IDLE,
                                                                       S_SILENT))).astype(np.int8)
        msg = np.where(talk, 1 + rng.poisson(max(msgs_per_talk - 1, 0), (T, N)), 0).astype(np.int16)
        win_on = np.stack([span[w * WIN_MIN:(w + 1) * WIN_MIN].any(0) for w in range(W)])
        sc = np.where(win_on, rng.poisson(stmt_rate, (W, N)), 0).astype(np.int16)
        calls = {}
        for i in range(N):
            n = rng.poisson(T / call_gap_min)
            t0 = np.sort(rng.uniform(st_[i] * 60, (T - en_[i]) * 60, n))
            calls[i] = (t0, t0 + rng.exponential(20.0, n), rng.random(n) < talk_frac)
        kicks = []
        for kind, rate in (("nudge", nudge_rate), ("mention", mention_rate)):
            nk = rng.poisson(rate * N * T)
            for m in np.sort(rng.integers(0, T, nk)):
                tg = np.array([rng.integers(N)], dtype=np.int64)
                kicks.append({"minute": int(m), "t_s": float(m * 60 + rng.uniform(0, 60)), "kind": kind,
                              "subkind": None, "targets": tg, "room": int(rooms_of[tg[0]])})
        days.append(DaySkel(pt_date=date.isoformat(), weekday=date.weekday(), win_start=ws, minute0=0, T=T,
                            active_offset_min=k * T, period_day=k, on_roster=np.ones(N, bool), span=span, state=state,
                            room=np.repeat(rooms_of[None, :], T, 0), sched_off=np.zeros(T, bool),
                            stall=np.zeros(T, bool), reasons=np.zeros((T, N), np.int8), msg_count=msg,
                            stmt_count=sc, win0=0, label_mask=rng.random((W, N)) < label_cover, calls=calls,
                            kicks=kicks))
        date += dt.timedelta(days=1)
    return Skeleton(unit_id=f"toy{seed}", goal_no=goal_no, regime=regime, holdout=False, agents=agents, days=days,
                    source="toy", smooth_min=121)


# ============================================================================================ models
@dataclass
class Fields:
    """Shared (non-coupling) fields added to the activity logit. sd in logit units; tau in minutes."""
    global_sd: float = 0.0
    global_tau: float = 30.0
    room_sd: float = 0.0
    room_tau: float = 30.0
    tod_amp: float = 0.0          # amp * cos(2 pi (m - phase) / T_day)
    tod_phase: float = 0.0
    day_sd: float = 0.0           # one value per day, shared by all agents
    agent_day_sd: float = 0.0     # independent per agent-day (heterogeneity, not a shared field)
    weekday: dict | None = None   # {weekday: h} e.g. {0: 0.3} = Monday effect


@dataclass
class EdgeDrive:
    """Synchronized day edges: spans start within `jitter` minutes of the first operator-on minute and end within
    `jitter` of the last; optional start-up burst (field burst_h for burst_min minutes after each start)."""
    jitter: int = 2
    burst_min: int = 0
    burst_h: float = 0.0


@dataclass
class KickModel:
    """Responses to kicks. effects: kind -> (h, delay_min, dur_min). mode 'field' adds h to the logit of the targeted
    agent; 'catalyst' multiplies its switching rate by exp(h) at fixed occupancy. source 'skeleton' uses the real
    kicks; 'idle' generates nudges at rate `rate` per minute for agents idle >= idle_min (the real nudger's rule)."""
    effects: dict = field(default_factory=lambda: {"nudge": (0.0, 2, 20)})
    mode: str = "field"
    source: str = "skeleton"
    rate: float = 0.03
    idle_min: int = 10
    kind: str = "nudge"


@dataclass
class ActivityModel:
    J: float = 0.0                # mean-field coupling to the others' spin deviations (logit units, J/N per agent)
    scope: str = "village"        # village | room
    delay: str = "none"           # none | lag | readout
    lag: tuple = (2, 8)           # per-agent lag range (minutes) for delay="lag"
    persistence: str = "matched"  # matched (real switch rate) | value: float switch rate for every agent
    profile: str = "real"         # real (smoothed own activity: carries the real shared schedule) | flat (agent-day mean)
    fields: Fields = field(default_factory=Fields)
    p_idle: float = 0.3           # inactive in-span minutes that carry an idle/pause event


@dataclass
class StallModel:
    pi: float = 0.05              # planted stall fraction of in-session minutes
    mean_len: float = 8.0
    min_len: int = 2
    free_prob: float = 0.3        # one random agent stays free in a stall
    marked_prob: float = 1.0      # a stall leaves infra-error reasons ...
    reason_prob: float = 0.9      # ... on this share of the forced-silent agent-minutes
    partial: float = 1.0          # share of agents hit
    source: str = "planted"       # planted | real (replay the unit's real stalls and scheduled-off minutes)


@dataclass
class TalkModel:
    kind: str = "bernoulli"       # bernoulli | hawkes
    n_x: float = 0.0              # hawkes: cross branching (offspring per event, shared over the scope's others)
    n_s: float = 0.0              # hawkes: self branching
    tau_s: float = 120.0          # hawkes: kernel mean (seconds)
    scope: str = "village"        # village | room
    p_mention_parent: float = 0.5  # hawkes child mentions its parent's author
    p_mention_recent: float = 0.2  # bernoulli: mention the latest other speaker in the room (<= 10 min)
    p_mention_random: float = 0.03


@dataclass
class ContentModel:
    kind: str = "ou"              # ou | degroot
    J: float = 0.0                # ou: mean-field coupling (per window), g_true = J (n-1)/n
    alpha: float = 0.0            # degroot: weight toward the previous window's room statements
    scope: str = "room"
    phi: float = 0.85             # ou persistence per window
    k0: float = 4.0               # anisotropy (PR ~ 8 of 32)
    vz: float = 0.4               # latent variance (trace)
    s_eps2: float = 2.4 / 32      # statement noise per dim
    a_static: float = 1.0         # static agent field + goal weight
    sigma_G: float = 0.0          # global day drive
    sigma_R: float = 0.0          # room-day drive
    A_k: float = 0.0              # kickoff relaxation amplitude
    tau_k: float = 2.0            # kickoff relaxation time (days)
    A_tod: float = 0.0            # time-of-day drive
    innov: float = 0.15           # degroot innovation sd (per dim, before shape)
    counts: str = "real"          # real | poisson


@dataclass
class ProjectModel:
    q: int = 4
    J: float = 0.0                # herding coupling on the share of others holding a project
    h: tuple | None = None        # fields per label 0..q (0 = "other")
    p_reconsider: float = 0.2     # per window
    waves_per_day: float = 0.0
    wave_p: float = 0.6
    scope: str = "village"


# ============================================================================================ simulation result
@dataclass
class DaySim:
    act: np.ndarray
    talk: np.ndarray
    idle: np.ndarray
    span: np.ndarray
    stall: np.ndarray
    reasons: np.ndarray
    msgs: dict
    stmts: dict
    labels: np.ndarray
    kicks: list
    z: np.ndarray | None = None


class Sim:
    def __init__(self, sk: Skeleton, days: list, truth: dict, spec: dict):
        self.sk, self.days, self.truth, self.spec = sk, days, truth, spec
        self.statement_vectors = None
        self.agent_win30_vectors = None

    def spins(self, channel: str = "activity", valid: str = "none") -> list:
        """Per-day (S, minute): S (T x N) +-1 spins of `channel` (activity | talk); minute = window indices.
        valid="stall" drops planted stall minutes (oracle mask)."""
        out = []
        for d, ds in zip(self.sk.days, self.days):
            X = ds.act if channel == "activity" else ds.talk
            S = np.where(X, 1.0, -1.0)
            m = d.minutes
            if valid == "stall":
                S, m = S[~ds.stall], m[~ds.stall]
            out.append((S, m))
        return out

    def content_panel(self, use_latent: bool = False):
        """(N x W_total x d) agent-window mean statement vectors (NaN where none), window day index, rooms (W x N)."""
        Ws = [d.W for d in self.sk.days]
        Wt = int(sum(Ws))
        X = np.full((self.sk.N, Wt, D_CONTENT), np.nan)
        dayix = np.repeat(np.arange(len(Ws)), Ws)
        rooms = np.zeros((Wt, self.sk.N), np.int8)
        o = 0
        for d, ds in zip(self.sk.days, self.days):
            if use_latent and ds.z is not None:
                X[:, o:o + d.W] = np.transpose(ds.z, (1, 0, 2))
            else:
                s = ds.stmts
                if len(s["agent"]):
                    S = np.zeros((self.sk.N, d.W, D_CONTENT))
                    C = np.zeros((self.sk.N, d.W))
                    np.add.at(S, (s["agent"], s["win"]), s["vec"])
                    np.add.at(C, (s["agent"], s["win"]), 1)
                    X[:, o:o + d.W] = np.where(C[..., None] > 0, S / np.maximum(C, 1)[..., None], np.nan)
            mid = np.minimum(np.arange(d.W) * WIN_MIN + WIN_MIN // 2, d.T - 1)
            rooms[o:o + d.W] = d.room[mid]
            o += d.W
        return X, dayix, rooms

    # -------------------------------------------------------------------------------- tables (shared schemas)
    def tables(self) -> dict:
        return to_tables(self)


# ============================================================================================ engines
def _spans(sk: Skeleton, d: DaySkel, edge: EdgeDrive | None, rng) -> np.ndarray:
    if edge is None:
        return d.span.copy()
    on = np.flatnonzero(~d.sched_off)
    lo, hi = (int(on[0]), int(on[-1])) if len(on) else (0, d.T - 1)
    span = np.zeros((d.T, sk.N), bool)
    for i in np.flatnonzero(d.on_roster):
        a = lo + int(rng.integers(0, edge.jitter + 1))
        b = hi - int(rng.integers(0, edge.jitter + 1))
        span[a:b + 1, i] = True
    return span


def _plant_stalls(d: DaySkel, span: np.ndarray, sm: StallModel | None, rng):
    """Returns stall (T,) bool, forced (T, N) bool, infra-reason (T, N) bool."""
    T, N = span.shape
    stall = np.zeros(T, bool)
    forced = np.zeros((T, N), bool)
    infra = np.zeros((T, N), bool)
    if sm is None:
        return stall, forced, infra
    if sm.source == "real":
        stall = d.stall | d.sched_off
        forced[stall] = True
        infra = (d.reasons == R_INFRA) & forced
        return stall, forced, infra
    sess = np.flatnonzero(span.any(1))
    if len(sess) == 0 or sm.pi <= 0:
        return stall, forced, infra
    lo, hi = sess[0], sess[-1] + 1
    rate = sm.pi / sm.mean_len / max(1e-9, 1 - sm.pi)
    t = lo
    while t < hi:
        if rng.random() < rate:
            dur = max(sm.min_len, int(rng.geometric(1 / sm.mean_len)))
            e = min(hi, t + dur)
            stall[t:e] = True
            hit = rng.random(N) < sm.partial if sm.partial < 1 else np.ones(N, bool)
            if rng.random() < sm.free_prob:
                hit[rng.integers(N)] = False
            forced[t:e] |= hit[None, :]
            if rng.random() < sm.marked_prob:
                infra[t:e] |= hit[None, :] & (rng.random((e - t, N)) < sm.reason_prob)
            t = e
        else:
            t += 1
    return stall, forced, infra


def _fields_matrix(sk: Skeleton, d: DaySkel, k: int, f: Fields, rng, room: np.ndarray) -> np.ndarray:
    T, N = d.T, sk.N
    H = np.zeros((T, N))
    if f.global_sd > 0:
        H += _ou(T, f.global_sd, f.global_tau, rng)[:, None]
    if f.room_sd > 0:
        rooms = np.unique(room)
        R = {int(r): _ou(T, f.room_sd, f.room_tau, rng) for r in rooms}
        for r, x in R.items():
            H += np.where(room == r, x[:, None], 0.0)
    if f.tod_amp:
        m = d.minutes
        Td = max(m[-1] + 1, 2)
        H += f.tod_amp * np.cos(2 * np.pi * (m - f.tod_phase) / Td)[:, None]
    if f.day_sd > 0:
        H += rng.normal(0, f.day_sd)
    if f.agent_day_sd > 0:
        H += rng.normal(0, f.agent_day_sd, N)[None, :]
    if f.weekday:
        H += float(f.weekday.get(d.weekday, 0.0))
    return H


def _readout_index(sk: Skeleton, d: DaySkel) -> np.ndarray:
    """(T, N): minute (row index) of the agent's most recent call start <= t - 1 (else t - 1)."""
    T, N = d.T, sk.N
    base = np.maximum(np.arange(T) - 1, 0)
    R = np.repeat(base[:, None], N, 1)
    for i, (t0, _, _) in d.calls.items():
        cm = np.unique(np.floor(t0 / 60).astype(np.int64) - d.minute0)
        cm = cm[(cm >= 0) & (cm < T)]
        if len(cm) == 0:
            continue
        k = np.searchsorted(cm, base, side="right") - 1
        R[:, i] = np.where(k >= 0, cm[np.maximum(k, 0)], base)
    return R


def rate_matched_hK(p: np.ndarray, c) -> tuple:
    """Field h and persistence K of a +-1 Glauber spin with stationary P(+) = p and switching rate c:
    P(+|+) = a = 1 - c/(2p), P(+|-) = b = c/(2(1-p)), sigmoid(2(h + K s)) -> h = (logit a + logit b)/4,
    K = (logit a - logit b)/4 (a, b clipped to [0.002, 0.998])."""
    a = np.clip(1 - c / (2 * p), 0.002, 0.998)
    b = np.clip(c / (2 * (1 - p)), 0.002, 0.998)
    la, lb = _logit(a), _logit(b)
    return (la + lb) / 4, (la - lb) / 4


def engine_inputs(sk: Skeleton, k: int, am: ActivityModel | None = None, span: np.ndarray | None = None):
    """The activity engine's per-minute p (clipped), switching rates c, h0, K and expected spins for day k
    (for estimators that need the exact offsets, e.g. pseudo-likelihood recovery of J in tests)."""
    am = am or ActivityModel()
    d = sk.days[k]
    prof = sk.profiles()
    span = d.span if span is None else span
    N = sk.N
    p = np.clip(np.where(span, prof["p_act"][k], 0.0), 1e-3, 1 - 1e-3)
    c = np.broadcast_to(prof["switch"] if am.persistence == "matched" else float(am.persistence), (N,))
    c = np.minimum(c[None, :], 2 * np.minimum(p, 1 - p) * 0.999)
    h0, K = rate_matched_hK(p, c)
    return {"p": p, "c": c, "h0": h0, "K": K, "m_exp": np.where(span, 2 * p - 1, -1.0)}


def _activity_day(sk, d, prof_p, switch, span, am: ActivityModel, edge, kicks: KickModel | None,
                  stall, forced, rng):
    """Parallel Glauber dynamics for one day. Returns act (T, N) bool, kick truth rows, readout lags."""
    T, N = d.T, sk.N
    p = np.clip(np.where(span, prof_p, 0.0), 1e-3, 1 - 1e-3)
    c = np.broadcast_to(switch if am.persistence == "matched" else float(am.persistence), (N,))
    c = np.minimum(c[None, :], 2 * np.minimum(p, 1 - p) * 0.999)

    def hk(cc):
        return rate_matched_hK(p, cc)

    h0, K = hk(c)
    m_exp = np.where(span, 2 * p - 1, -1.0)
    room = d.room
    H = _fields_matrix(sk, d, 0, am.fields, rng, room)
    if edge is not None and edge.burst_min > 0 and edge.burst_h:
        first = np.where(span.any(0), span.argmax(0), T)
        for i in range(N):
            H[first[i]:first[i] + edge.burst_min, i] += edge.burst_h
    # kicks: field pulses and catalytic windows
    kick_rows = []
    Hk = np.zeros((T, N))
    cat = np.zeros((T, N))
    if kicks is not None and kicks.source == "skeleton":
        for kk in d.kicks:
            if kk["kind"] not in kicks.effects:
                continue
            hval, dl, du = kicks.effects[kk["kind"]]
            m = kk["minute"] - d.minute0
            for i in kk["targets"]:
                a0, a1 = m + 1 + dl, min(T, m + 1 + dl + du)
                if a0 < T:
                    (Hk if kicks.mode == "field" else cat)[a0:a1, i] += hval
                kick_rows.append((m, int(i), kk["kind"], hval, dl, du))
    if kicks is not None and kicks.mode == "catalyst" and np.any(cat):
        h0c, Kc = hk(np.minimum(c * np.exp(cat), 2 * np.minimum(p, 1 - p) * 0.999))
        h0 = np.where(cat != 0, h0c, h0)
        K = np.where(cat != 0, Kc, K)
    gen_kicks = kicks is not None and kicks.source == "idle"
    eff = kicks.effects.get(kicks.kind, (0.0, 2, 20)) if gen_kicks else None
    if am.delay == "readout":
        RO = _readout_index(sk, d)
    elif am.delay == "lag":
        L = rng.integers(am.lag[0], am.lag[1] + 1, N)
    S = np.empty((T, N))
    s = np.where(rng.random(N) < p[0], 1.0, -1.0)
    s[~span[0]] = -1.0
    age = np.zeros(N)
    eff_until = np.full(N, -1)
    Hdyn = np.zeros((T + 64, N))
    ar = np.arange(N)
    for t in range(T):
        if t > 0:
            loc = h0[t] + K[t] * s + H[t] + Hk[t] + Hdyn[t]
            if am.J:
                if am.delay == "none":
                    G = np.broadcast_to(S[t - 1] - m_exp[t - 1], (N, N))
                elif am.delay == "lag":
                    ix = np.maximum(t - 1 - L, 0)
                    G = S[ix] - m_exp[ix]
                else:
                    ix = RO[t]
                    G = S[ix] - m_exp[ix]
                M = span[t][None, :].copy() & np.ones((N, N), bool)
                M[ar, ar] = False
                if am.scope == "room":
                    M &= room[t][:, None] == room[t][None, :]
                n_sc = M.sum(1) + 1
                loc = loc + am.J * (G * M).sum(1) / np.maximum(n_sc, 2)
            s = np.where(rng.random(N) < _sigmoid(2 * loc), 1.0, -1.0)
        s[~span[t]] = -1.0
        if stall[t]:
            s[forced[t]] = -1.0
        S[t] = s
        if gen_kicks:
            age = np.where(s < 0, age + 1, 0)
            kk = (age >= kicks.idle_min) & span[t] & (t > eff_until) & (rng.random(N) < kicks.rate)
            for i in np.flatnonzero(kk):
                hval, dl, du = eff
                a0, a1 = t + 1 + dl, min(T, t + 1 + dl + du)
                Hdyn[a0:a1, i] += hval if kicks.mode == "field" else 0.0
                eff_until[i] = a1
                kick_rows.append((t, int(i), kicks.kind, hval, dl, du))
    lags = None
    if am.delay == "readout":
        lags = (np.arange(T)[:, None] - RO).astype(np.int32)
    return S > 0, kick_rows, lags


def _hawkes_day(sk, d, r_min, span, stall, forced, tm: TalkModel, rng):
    """Exact cluster simulation of a multivariate Hawkes process on one day (times in seconds since win_start)."""
    T, N = d.T, sk.N
    t_lo = d.minute0 * 60.0
    # Cross offspring: each event has Poisson(n_x) children with other agents, each recipient drawn in proportion
    # to its own target rate (busy agents respond more), within the scope (village or the parent's room).
    # Stationary rate matching: A_ij = n_x r_i / sum_{k != j} r_k, so (A r)_i = n_x r_i (S - w_i), w_j =
    # r_j / (tot - r_j), S = sum_j w_j; the baseline mu = r - n_s r - A r stays positive (= (1 - n_s - n_x) r when
    # rates are equal). Room scope uses the same baseline (approximate matching).
    on = d.on_roster
    r = np.where(span & ~forced, r_min, 0.0)  # events / minute
    tot = r.sum(1, keepdims=True)
    w = np.where(tot - r > 0, r / np.maximum(tot - r, 1e-12), 0.0)
    Sw = w.sum(1, keepdims=True)
    mu = r * (1 - tm.n_s - tm.n_x * (Sw - w))
    mu = np.clip(mu, 0.05 * r, None)
    cnt = rng.poisson(mu)
    ti, ai = np.nonzero(cnt)
    times, agents, parents, gen = [], [], [], []
    for t_, a_, c_ in zip(ti, ai, cnt[ti, ai]):
        for _ in range(int(c_)):
            times.append(t_lo + (t_ + rng.random()) * 60.0)
            agents.append(int(a_))
            parents.append(-1)
            gen.append(0)
    times, agents, parents = list(times), list(agents), list(parents)
    frontier = list(range(len(times)))
    t_end = t_lo + T * 60.0
    while frontier:
        new = []
        for e in frontier:
            t0, j = times[e], agents[e]
            m0 = int((t0 - t_lo) // 60)
            if tm.n_s > 0:
                for _ in range(rng.poisson(tm.n_s)):
                    new.append((t0 + rng.exponential(tm.tau_s), j, e))
            if tm.n_x > 0:
                mm = min(max(m0, 0), T - 1)
                el = on & (r[mm] > 0)
                if tm.scope == "room":
                    el &= d.room[mm] == d.room[mm, j]
                el[j] = False
                elig = np.flatnonzero(el)
                if len(elig):
                    k = rng.poisson(tm.n_x)
                    if k:
                        pr = r[mm, elig] / r[mm, elig].sum()
                        for i in rng.choice(elig, k, replace=True, p=pr):
                            new.append((t0 + rng.exponential(tm.tau_s), int(i), e))
        frontier = []
        for (tc, i, par) in new:
            if tc >= t_end:
                continue
            m = int((tc - t_lo) // 60)
            if not span[m, i] or (stall[m] and forced[m, i]):
                continue
            times.append(tc)
            agents.append(i)
            parents.append(par)
            frontier.append(len(times) - 1)
    o = np.argsort(times, kind="stable")
    inv = np.empty_like(o)
    inv[o] = np.arange(len(o))
    t_arr = np.asarray(times)[o]
    a_arr = np.asarray(agents, dtype=np.int64)[o]
    p_raw = np.asarray(parents, dtype=np.int64)[o]
    par = np.where(p_raw >= 0, inv[np.maximum(p_raw, 0)], -1)
    ment = np.full(len(o), -1, np.int64)
    child = par >= 0
    pick = child & (rng.random(len(o)) < tm.p_mention_parent)
    ment[pick] = a_arr[par[pick]]
    ment[ment == a_arr] = -1
    return t_arr, a_arr, par, ment


def _talk_bernoulli(sk, d, act, q, mpt, tm: TalkModel, rng):
    T, N = act.shape
    talk = act & (rng.random((T, N)) < q)
    tt, aa = np.nonzero(talk)
    extra = rng.poisson(np.maximum(mpt[aa] - 1, 0))
    times, agents = [], []
    for t_, a_, x_ in zip(tt, aa, extra):
        for _ in range(1 + int(x_)):
            times.append((d.minute0 + t_ + rng.random()) * 60.0)
            agents.append(int(a_))
    o = np.argsort(times, kind="stable")
    t_arr = np.asarray(times)[o] if times else np.zeros(0)
    a_arr = np.asarray(agents, dtype=np.int64)[o] if agents else np.zeros(0, np.int64)
    ment = np.full(len(t_arr), -1, np.int64)
    last = {}
    for k in range(len(t_arr)):
        m = min(int(t_arr[k] // 60) - d.minute0, T - 1)
        rm = int(d.room[m, a_arr[k]])
        u = rng.random()
        if u < tm.p_mention_recent:
            cand = [(tl, a) for a, (tl, r_) in last.items() if r_ == rm and a != a_arr[k] and t_arr[k] - tl <= 600]
            if cand:
                ment[k] = max(cand)[1]
        elif u < tm.p_mention_recent + tm.p_mention_random:
            oth = np.flatnonzero(d.on_roster)
            oth = oth[oth != a_arr[k]]
            if len(oth):
                ment[k] = int(rng.choice(oth))
        last[int(a_arr[k])] = (t_arr[k], rm)
    return talk, t_arr, a_arr, np.full(len(t_arr), -1, np.int64), ment


def _content(sk: Skeleton, sims: list, cm: ContentModel, rng):
    """Latent content per window and statements for every day (in place on sims). Returns truth dict."""
    d_ = D_CONTENT
    N = sk.N
    L = aniso_shape(rng, d_, cm.k0) * math.sqrt(cm.vz)
    goal = rng.standard_normal(d_)
    goal /= np.linalg.norm(goal)
    static = rng.standard_normal((N, d_))
    static = static / np.linalg.norm(static, axis=1, keepdims=True) * 0.8
    kdir = np.linalg.qr(rng.standard_normal((d_, 3)))[0].T.sum(0) / math.sqrt(3)
    tdir = np.linalg.qr(rng.standard_normal((d_, 2)))[0].T
    z = (rng.standard_normal((N, d_)) @ L.T)
    w_global = 0
    n_scope_all = []
    for k, (d, ds) in enumerate(zip(sk.days, sims)):
        W = d.W
        G = (L @ rng.standard_normal(d_)) * cm.sigma_G
        rooms_d = np.unique(d.room)
        Hr = {int(r): (L @ rng.standard_normal(d_)) * cm.sigma_R for r in rooms_d}
        Z = np.zeros((W, N, d_))
        prev_stmts = None
        for w in range(W):
            mid = min(w * WIN_MIN + WIN_MIN // 2, d.T - 1)
            rm = d.room[mid]
            pres = ds.span[w * WIN_MIN:(w + 1) * WIN_MIN].any(0) & d.on_roster
            F = np.zeros((N, d_)) + G
            for r, v in Hr.items():
                F[rm == r] += v
            F += cm.A_k * math.exp(-(w_global / max(W, 1)) / max(cm.tau_k, 1e-6)) * kdir
            ph = 2 * np.pi * (w + d.win0) / max(W + d.win0, 1)
            F += cm.A_tod * (np.array([math.cos(ph), math.sin(ph)]) @ tdir)
            if cm.kind == "ou":
                if cm.scope == "room":
                    same = (rm[:, None] == rm[None, :]) & pres[None, :]
                else:
                    same = np.repeat(pres[None, :], N, 0)
                np.fill_diagonal(same, False)
                ns = same.sum(1)
                n_scope_all.append(ns[pres] + 1)
                m_oth = (same.astype(float) @ z) / np.maximum(ns, 1)[:, None]
                z = cm.phi * z + (1 - cm.phi) * (cm.J * m_oth + F) + math.sqrt(1 - cm.phi ** 2) * (
                    rng.standard_normal((N, d_)) @ L.T)
            else:  # degroot read-out: move toward the previous window's statements by others in the room
                act_w = ds.act[w * WIN_MIN:(w + 1) * WIN_MIN].any(0)
                if prev_stmts is not None and cm.alpha > 0:
                    pa, pv, pr = prev_stmts
                    for i in np.flatnonzero(act_w):
                        sel = (pa != i) & ((pr == rm[i]) if cm.scope == "room" else True)
                        if np.any(sel):
                            target = pv[sel].mean(0) - cm.a_static * (static[i] + 0.6 * goal)
                            z[i] = (1 - cm.alpha) * z[i] + cm.alpha * target
                z = z + cm.innov * (rng.standard_normal((N, d_)) @ L.T) + 0.05 * F
            Z[w] = z
            # statements of this window
            cnt = d.stmt_count[w] if cm.counts == "real" else rng.poisson(np.maximum(d.stmt_count[w], 0.0))
            cnt = np.where(d.on_roster, cnt, 0)
            ags, vecs, ts, rs_ = [], [], [], []
            for i in np.flatnonzero(cnt):
                lo_m, hi_m = w * WIN_MIN, min((w + 1) * WIN_MIN, d.T)
                if lo_m >= d.T:
                    continue
                am = np.flatnonzero(ds.act[lo_m:hi_m, i]) + lo_m
                for _ in range(int(cnt[i])):
                    m = int(rng.choice(am)) if len(am) else int(rng.integers(lo_m, hi_m))
                    u = cm.a_static * (static[i] + 0.6 * goal) + z[i] + rng.standard_normal(d_) * math.sqrt(cm.s_eps2)
                    vecs.append(u / np.linalg.norm(u))
                    ags.append(int(i))
                    ts.append((d.minute0 + m + rng.random()) * 60.0)
                    rs_.append(int(d.room[m, i]))
            if ags:
                ds.stmts["agent"].extend(ags)
                ds.stmts["vec"].extend(vecs)
                ds.stmts["t_s"].extend(ts)
                ds.stmts["win"].extend([w] * len(ags))
                ds.stmts["room"].extend(rs_)
                prev_stmts = (np.array(ags), np.array(vecs), np.array(rs_))
            else:
                prev_stmts = None
            w_global += 1
        ds.z = Z
        for key in ("agent", "win", "room"):
            ds.stmts[key] = np.asarray(ds.stmts[key], dtype=np.int64)
        ds.stmts["t_s"] = np.asarray(ds.stmts["t_s"], dtype=np.float64)
        ds.stmts["vec"] = np.asarray(ds.stmts["vec"], dtype=np.float64).reshape(-1, d_)
        o = np.argsort(ds.stmts["t_s"], kind="stable")
        for key in ds.stmts:
            ds.stmts[key] = ds.stmts[key][o]
    n_bar = float(np.mean(np.concatenate(n_scope_all))) if n_scope_all else float("nan")
    return {"kind": cm.kind, "J": cm.J, "alpha": cm.alpha, "scope": cm.scope, "phi": cm.phi,
            "g_true": cm.J * (n_bar - 1) / n_bar if cm.kind == "ou" and np.isfinite(n_bar) else None,
            "n_scope_mean": n_bar, "goal_dir": goal, "static": static}


def _projects(sk: Skeleton, sims: list, pm: ProjectModel, rng):
    q, N = pm.q, sk.N
    h = np.zeros(q + 1) if pm.h is None else np.asarray(pm.h, float)
    sig = rng.integers(1, q + 1, N)
    waves = []
    for k, (d, ds) in enumerate(zip(sk.days, sims)):
        W = d.W
        lab = np.full((W, N), -1, np.int8)
        nw = rng.poisson(pm.waves_per_day)
        wave_w = set(rng.integers(0, W, nw).tolist()) if nw else set()
        for w in range(W):
            mid = min(w * WIN_MIN + WIN_MIN // 2, d.T - 1)
            rm = d.room[mid]
            on = d.on_roster
            if w in wave_w:
                a_w = int(rng.integers(1, q + 1))
                take = on & (rng.random(N) < pm.wave_p)
                sig = np.where(take, a_w, sig)
                waves.append((k, w, a_w, int(take.sum())))
            else:
                rec = on & (rng.random(N) < pm.p_reconsider)
                new = sig.copy()
                for i in np.flatnonzero(rec):
                    sc = on.copy()
                    if pm.scope == "room":
                        sc &= rm == rm[i]
                    sc[i] = False
                    n = max(int(sc.sum()), 1)
                    frac = np.bincount(sig[sc], minlength=q + 1)[: q + 1] / n
                    lg = h + pm.J * frac
                    lg[0] = -np.inf if pm.h is None else lg[0]
                    pr = np.exp(lg - lg[np.isfinite(lg)].max())
                    pr[~np.isfinite(pr)] = 0
                    new[i] = int(rng.choice(q + 1, p=pr / pr.sum()))
                sig = new
            lab[w] = np.where(on, sig, -1)
        ds.labels = lab
    return {"q": q, "J": pm.J, "p_reconsider": pm.p_reconsider, "waves": waves, "scope": pm.scope}


# ============================================================================================ simulate
def simulate(sk: Skeleton, seed: int = 0, activity: ActivityModel | None = None, edge: EdgeDrive | None = None,
             stalls: StallModel | None = None, talk: TalkModel | None = None, content: ContentModel | None = None,
             projects: ProjectModel | None = None, kicks: KickModel | None = None) -> Sim:
    """Simulate a swarm on skeleton `sk`. Every model is optional; defaults: independent rate-matched activity,
    bernoulli talk, no content / projects / stalls / kicks / edges."""
    rng = np.random.default_rng(seed)
    am = activity or ActivityModel()
    tm = talk or TalkModel()
    prof = sk.profiles()
    days, kick_truth, lag_all = [], [], []
    msg_truth = []
    for k, d in enumerate(sk.days):
        span = _spans(sk, d, edge, rng)
        stall, forced, infra = _plant_stalls(d, span, stalls, rng)
        p = prof["p_act"][k]
        if am.profile == "flat":
            pm0 = (p * d.span).sum(0) / np.maximum(d.span.sum(0), 1)
            p = np.where(d.span, pm0[None, :], 0.0)
        if edge is not None:  # profiles outside the real span: use the agent's day mean
            pm_ = np.where(d.span.any(0), (p * d.span).sum(0) / np.maximum(d.span.sum(0), 1), 0.3)
            p = np.where(d.span, p, pm_[None, :])
        act, krows, lags = _activity_day(sk, d, p, prof["switch"], span, am, edge, kicks, stall, forced, rng)
        kick_truth += [(d.pt_date,) + r for r in krows]
        if lags is not None:
            lag_all.append(lags[span])
        if tm.kind == "hawkes":
            r = prof["r_msg"][k]
            if edge is not None:
                rm_ = np.where(d.span.any(0), (r * d.span).sum(0) / np.maximum(d.span.sum(0), 1), 0.0)
                r = np.where(d.span, r, rm_[None, :])
            t_arr, a_arr, par, ment = _hawkes_day(sk, d, r, span, stall, forced, tm, rng)
            talk_m = np.zeros_like(act)
            if len(t_arr):
                talk_m[np.minimum((t_arr // 60).astype(int) - d.minute0, d.T - 1), a_arr] = True
            act = act | talk_m
            talk_b = talk_m
        else:
            talk_b, t_arr, a_arr, par, ment = _talk_bernoulli(sk, d, act, prof["q_talk"][k], prof["mpt"], tm, rng)
        idle = (~act) & span & ~(stall[:, None] & forced) & (rng.random(act.shape) < am.p_idle)
        reasons = np.zeros(act.shape, np.int8)
        on = d.on_roster[None, :]
        before = np.cumsum(span, 0) == 0
        after = np.cumsum(span[::-1], 0)[::-1] == 0
        reasons[on & before & ~span] = R_PRE
        reasons[on & after & ~span & ~before] = R_POST
        reasons[idle] = R_PAUSE
        reasons[infra & ~act] = R_INFRA
        reasons[act] = R_NONE
        msgs = {"t_s": t_arr, "agent": a_arr, "parent": par, "mention": ment,
                "room": np.array([int(d.room[min(int(t // 60) - d.minute0, d.T - 1), a]) for t, a in zip(t_arr, a_arr)],
                                 dtype=np.int64)}
        msg_truth.append((d.pt_date, len(t_arr), int((par >= 0).sum())))
        stm = {"agent": [], "vec": [], "t_s": [], "win": [], "room": []}
        days.append(DaySim(act=act, talk=talk_b, idle=idle, span=span, stall=stall, reasons=reasons, msgs=msgs,
                           stmts=stm, labels=np.full((d.W, sk.N), -1, np.int8), kicks=krows))
    truth = {"activity": {"J": am.J, "scope": am.scope, "delay": am.delay,
                          "fields": am.fields.__dict__.copy(), "edge": None if edge is None else edge.__dict__.copy()},
             "talk": {"kind": tm.kind, "n_x": tm.n_x, "n_s": tm.n_s, "tau_s": tm.tau_s, "scope": tm.scope},
             "stalls": None if stalls is None else stalls.__dict__.copy(),
             "kicks": None if kicks is None else {"effects": kicks.effects, "mode": kicks.mode, "source": kicks.source}}
    if lag_all:
        la = np.concatenate(lag_all)
        truth["activity"]["readout_lag_median_min"] = float(np.median(la))
    sim = Sim(sk, days, truth, {"seed": seed})
    truth["activity"]["g_true"] = g_true_cw(sim, am.J)
    tot = sum(x[1] for x in msg_truth)
    truth["talk"]["n_events"] = tot
    truth["talk"]["branching_realized"] = (sum(x[2] for x in msg_truth) / tot) if tot else float("nan")
    if content is not None:
        for ds in days:
            ds.stmts = {"agent": [], "vec": [], "t_s": [], "win": [], "room": []}
        truth["content"] = _content(sk, days, content, rng)
    else:
        for ds in days:
            ds.stmts = {"agent": np.zeros(0, np.int64), "vec": np.zeros((0, D_CONTENT)), "t_s": np.zeros(0),
                        "win": np.zeros(0, np.int64), "room": np.zeros(0, np.int64)}
    if projects is not None:
        truth["projects"] = _projects(sk, days, projects, rng)
    sim.kick_truth = kick_truth
    return sim


def g_true_cw(sim: Sim, J: float, block_min: int = 30) -> float:
    """H25's truth for mean-field coupling on the clean spins: g = J q_bar (N-1)/N (q_bar = within-block single-spin
    variance over present agents, N = mean number of present agents)."""
    if not J:
        return 0.0
    num = den = 0.0
    npres = []
    for d, ds in zip(sim.sk.days, sim.days):
        S = np.where(ds.act, 1.0, -1.0)
        blk = d.minutes // block_min
        for b in np.unique(blk):
            X = S[blk == b]
            sp = ds.span[blk == b].all(0)
            if len(X) >= 5 and sp.sum() >= 2:
                num += (X[:, sp].var(0) * len(X)).sum()
                den += len(X) * sp.sum()
                npres.append(sp.sum())
    if den == 0:
        return float("nan")
    q = num / den
    N = float(np.mean(npres))
    return float(J * q * (N - 1) / N)


# ============================================================================================ presets
DYNAMICS = {
    "independent": "rate-matched independent agents (real activity profiles and switch rates; bernoulli talk)",
    "global_field": "independent agents + a shared OU field (sd 0.5, tau 30 min) and a time-of-day field",
    "room_field": "independent agents + per-room OU fields (sd 0.5, tau 30 min)",
    "tod_field": "independent agents + a time-of-day field (amp 0.5)",
    "day_edge": "synchronized day edges (jitter 2 min) + start-up burst",
    "ising": "kinetic Ising (parallel Glauber), mean-field J, no delay",
    "ising_readout": "kinetic Ising with the read-out delay (others as seen at the agent's last call start)",
    "hawkes": "multivariate Hawkes talk (n_x 0.3, n_s 0.2, tau 120 s), activity independent",
    "vector_spin": "O(32) vector-spin content kinetics with room mean-field coupling J (OU)",
    "degroot": "read-out DeGroot content averaging (alpha 0.3)",
    "potts_waves": "kinetic Potts project herding (J 2) with waves (1 per day)",
    "stalls": "independent agents + planted platform stalls (pi 0.05, marked)",
    "kick_field": "independent agents + field responses to skeleton nudges (h 1.0, delay 2, 20 min)",
}


def preset(name: str, **over) -> dict:
    """Keyword arguments for simulate() for a named dynamics; `over` sets model parameters by name
    (e.g. J=0.6 goes to the model that owns J for that preset)."""
    m: dict = {"activity": ActivityModel()}
    if name == "independent":
        pass
    elif name == "global_field":
        m["activity"] = ActivityModel(fields=Fields(global_sd=0.5, global_tau=30, tod_amp=0.3))
    elif name == "room_field":
        m["activity"] = ActivityModel(fields=Fields(room_sd=0.5, room_tau=30))
    elif name == "tod_field":
        m["activity"] = ActivityModel(fields=Fields(tod_amp=0.5))
    elif name == "day_edge":
        m["edge"] = EdgeDrive(jitter=2, burst_min=10, burst_h=1.0)
    elif name == "ising":
        m["activity"] = ActivityModel(J=0.5)
    elif name == "ising_readout":
        m["activity"] = ActivityModel(J=0.5, delay="readout")
    elif name == "hawkes":
        m["talk"] = TalkModel(kind="hawkes", n_x=0.3, n_s=0.2, tau_s=120.0)
    elif name == "vector_spin":
        m["content"] = ContentModel(kind="ou", J=0.4)
    elif name == "degroot":
        m["content"] = ContentModel(kind="degroot", alpha=0.3)
    elif name == "potts_waves":
        m["projects"] = ProjectModel(J=2.0, waves_per_day=1.0)
    elif name == "stalls":
        m["stalls"] = StallModel(pi=0.05)
    elif name == "kick_field":
        m["kicks"] = KickModel(effects={"nudge": (1.0, 2, 20)})
    else:
        raise KeyError(f"unknown dynamics {name!r}; known: {sorted(DYNAMICS)}")
    for k, v in over.items():
        placed = False
        for obj in m.values():
            if hasattr(obj, k):
                setattr(obj, k, v)
                placed = True
                break
            if hasattr(obj, "fields") and hasattr(obj.fields, k):
                setattr(obj.fields, k, v)
                placed = True
                break
        if not placed:
            raise KeyError(f"parameter {k!r} not found in preset {name!r}")
    return m


# ============================================================================================ tables
def to_tables(sim: Sim) -> dict:
    """Render a Sim into the shared tables' schemas (see module docstring). No text anywhere."""
    import polars as pl
    sk = sim.sk
    ho = bool(sk.holdout)
    reg = sk.regime
    ab_rows, chat_rows, st_rows, ps_rows, sm_rows, rs_rows, cw_rows, kc_rows = [], [], [], [], [], [], [], []
    vecs = []
    msg_k = 0
    st_k = 0
    turn_k = 0
    for k, (d, ds) in enumerate(zip(sk.days, sim.days)):
        T, N = ds.act.shape
        mins = d.minutes
        on = np.flatnonzero(d.on_roster)
        state = np.where(ds.talk, S_TALK, np.where(ds.act, S_ACT, np.where(ds.idle, S_IDLE, S_SILENT)))
        tt, ii = np.meshgrid(np.arange(T), on, indexing="ij")
        tt, ii = tt.ravel(), ii.ravel()
        msgc = np.zeros((T, N), np.int16)
        if len(ds.msgs["t_s"]):
            mm = np.minimum((ds.msgs["t_s"] // 60).astype(int) - d.minute0, T - 1)
            np.add.at(msgc, (mm, ds.msgs["agent"]), 1)
        ab_rows.append(pl.DataFrame({
            "pt_date": [d.pt_date] * len(tt), "minute": mins[tt].astype(np.int64),
            "active_min": (d.active_offset_min + mins[tt]).astype(np.int32), "agent": sk.agents[ii],
            "talk": msgc[tt, ii].astype(np.int16), "idle": ds.idle[tt, ii].astype(np.int16),
            "consolidate": np.zeros(len(tt), np.int16), "other_event": np.zeros(len(tt), np.int16),
            "turns": (ds.act[tt, ii] & ~ds.talk[tt, ii]).astype(np.int16), "paused": ds.idle[tt, ii].astype(np.int16),
            "state": state[tt, ii].astype(np.int8)}))
        # chat
        n = len(ds.msgs["t_s"])
        if n:
            ids = [f"syn-{sk.unit_id}-{msg_k + j}" for j in range(n)]
            ment = [[int(sk.agents[x])] if x >= 0 else [] for x in ds.msgs["mention"]]
            chat_rows.append(pl.DataFrame({
                "message_id": ids, "t": [d.win_start + dt.timedelta(seconds=float(x)) for x in ds.msgs["t_s"]],
                "pt_date": [d.pt_date] * n, "goal_no": np.full(n, sk.goal_no, np.int8), "regime": [reg] * n,
                "room": ds.msgs["room"].astype(np.int8), "speaker_kind": ["agent"] * n,
                "agent": sk.agents[ds.msgs["agent"]], "human": [None] * n,
                "length": np.random.default_rng(msg_k).integers(40, 800, n).astype(np.int32), "mentions": ment,
                "n_urls": np.zeros(n, np.int16), "parent_msg": np.where(ds.msgs["parent"] >= 0,
                                                                          ds.msgs["parent"] + msg_k, -1)},
                schema_overrides={"human": pl.String, "mentions": pl.List(pl.Int8)}))
            msg_k += n
        # statements
        s = ds.stmts
        ns_ = len(s["agent"])
        if ns_:
            st_rows.append(pl.DataFrame({
                "kind": ["chat"] * ns_, "src_row": np.arange(st_k, st_k + ns_, dtype=np.uint32),
                "agent": sk.agents[s["agent"]], "t": [d.win_start + dt.timedelta(seconds=float(x)) for x in s["t_s"]],
                "pt_date": [d.pt_date] * ns_, "room": s["room"].astype(np.int8),
                "goal_no": np.full(ns_, sk.goal_no, np.int8), "regime": [reg] * ns_, "holdout": [ho] * ns_,
                "win30": (s["win"] + d.win0).astype(np.int16)}))
            vecs.append(s["vec"])
            st_k += ns_
        # projects (observed where the real labels exist)
        if (ds.labels >= 0).any():
            obs = (ds.labels >= 0) & d.label_mask
            ww, aa = np.nonzero(obs)
            if len(ww):
                mid = np.minimum(ww * WIN_MIN + WIN_MIN // 2, T - 1)
                lab = ds.labels[ww, aa]
                ps_rows.append(pl.DataFrame({
                    "w_min": np.full(len(ww), 30, np.int16), "sources": ["all"] * len(ww),
                    "goal_no": np.full(len(ww), sk.goal_no, np.int8), "pt_date": [d.pt_date] * len(ww),
                    "day": np.full(len(ww), d.period_day, np.int16), "win": (ww + d.win0).astype(np.int16),
                    "agent": sk.agents[aa], "room": d.room[mid, aa].astype(np.int8),
                    "project": [f"syn:project_{int(x)}" if x > 0 else "syn:other" for x in lab],
                    "n": np.ones(len(ww), np.int32), "n_all": np.ones(len(ww), np.int32),
                    "n_tied": np.ones(len(ww), np.int8), "label": lab.astype(np.int8), "holdout": [ho] * len(ww)}))
        # stall minutes + reasons
        pres = ds.span
        K = (ds.act & pres).sum(1)
        n_present = int(d.on_roster.sum())
        sil = pres & ~ds.act
        cnt = {c: ((ds.reasons == code) & ~ds.act & d.on_roster[None, :]).sum(1) for c, code in
               (("n_pre", R_PRE), ("n_post", R_POST), ("n_infra_err", R_INFRA), ("n_consol", R_CONSOL),
                ("n_pause", R_PAUSE))}
        nrec = sum(cnt.values())
        n_sil = n_present - K
        js = (K <= 1) & (n_present >= 3)
        sched = d.sched_off if (sim.truth.get("stalls") or {}).get("source") == "real" else np.zeros(T, bool)
        sm_rows.append(pl.DataFrame({
            "pt_date": [d.pt_date] * T, "goal_no": np.full(T, sk.goal_no, np.int8), "regime": [reg] * T,
            "holdout": [ho] * T, "minute": mins.astype(np.int32),
            "t": [d.win_start + dt.timedelta(minutes=int(m)) for m in mins], "n_present": np.full(T, n_present, np.int8),
            "K": K.astype(np.int8), "js": js, "scheduled": sched, "msg_sched": sched,
            **{c: v.astype(np.int8) for c, v in cnt.items()},
            "n_none": np.maximum(n_sil - nrec, 0).astype(np.int8),
            "explained": js & (sched | (2 * nrec >= n_sil)), "explained_strict": js & (sched | (nrec >= n_sil - 1)),
            "planted_stall": ds.stall}))
        rt, ra = np.nonzero((ds.reasons > 0) & ~ds.act & d.on_roster[None, :])
        if len(rt):
            rs_rows.append(pl.DataFrame({"pt_date": [d.pt_date] * len(rt), "minute": mins[rt].astype(np.int32),
                                         "agent": sk.agents[ra], "reason": ds.reasons[rt, ra].astype(np.int8)}))
        del sil
        # call windows (the skeleton's turns; structure only)
        for i, (t0, t1, tk) in d.calls.items():
            m = len(t0)
            if m == 0:
                continue
            cw_rows.append(pl.DataFrame({
                "turn_id": np.arange(turn_k, turn_k + m, dtype=np.int32), "agent": np.full(m, sk.agents[i], np.int8),
                "pt_date": [d.pt_date] * m, "goal_no": np.full(m, sk.goal_no, np.int8), "holdout": [ho] * m,
                "t_call": [d.win_start + dt.timedelta(seconds=float(x)) for x in t0],
                "t_end": [d.win_start + dt.timedelta(seconds=float(x)) for x in t1], "talk": np.asarray(tk, bool)}))
            turn_k += m
        for kk in d.kicks:
            tg = [int(sk.agents[x]) for x in kk["targets"]]
            kc_rows.append({"t": d.win_start + dt.timedelta(seconds=kk["t_s"]), "kind": kk["kind"],
                            "subkind": kk["subkind"], "targeted": len(tg) > 0, "room": kk["room"], "speaker": None,
                            "targets": tg, "n_targets": len(tg), "recipients": [], "msg": None, "message_id": None,
                            "goal_no": sk.goal_no, "pt_date": d.pt_date, "ref": None, "holdout": ho})
    out = {}
    ab = pl.concat(ab_rows) if ab_rows else pl.DataFrame()
    out["activity_bins"] = ab.sort("active_min", "agent") if ab.height else ab
    if chat_rows:
        ch = pl.concat(chat_rows).with_columns(pl.col("regime").cast(pl.Categorical),
                                                pl.col("speaker_kind").cast(pl.Categorical))
        out["msg_truth"] = ch.select("message_id", "parent_msg")
        ch = ch.drop("parent_msg").sort("t")
        out["chat_core"] = ch
        out["chat_mentions_clean"] = ch.select("message_id", pl.col("mentions").alias("mentions_clean"),
                                               pl.col("mentions").alias("mentions_roster"))
    if st_rows:
        out["statements"] = pl.concat(st_rows)
        V = np.vstack(vecs)
        sim.statement_vectors = V.astype(np.float16)
        st = out["statements"].with_row_index("_r")
        g = st.group_by("agent", "pt_date", "win30", maintain_order=True).agg(pl.col("_r"))
        M = np.stack([V[np.asarray(r)].mean(0) for r in g["_r"].to_list()])
        out["agent_win30"] = g.drop("_r").with_row_index("gid").with_columns(
            pl.col("gid").cast(pl.UInt32), pl.lit(sk.goal_no, pl.Int8).alias("goal_no"), pl.lit(reg).alias("regime"),
            pl.lit(ho).alias("holdout"), pl.Series("n_chat", [len(r) for r in g["_r"].to_list()], pl.UInt32),
            pl.lit(0, pl.UInt32).alias("n_intent"))
        sim.agent_win30_vectors = M.astype(np.float32)
    if ps_rows:
        out["project_states"] = pl.concat(ps_rows).with_columns(pl.col("sources").cast(pl.Categorical),
                                                                pl.col("project").cast(pl.Categorical))
    out["stall_minutes"] = pl.concat(sm_rows).with_columns(pl.lit(None, pl.String).alias("cause"),
                                                            pl.lit(None, pl.Int32).alias("outage_id"))
    if rs_rows:
        out["reasons"] = pl.concat(rs_rows)
    if cw_rows:
        out["call_windows"] = pl.concat(cw_rows)
    if kc_rows:
        out["kicks_classified"] = pl.DataFrame(kc_rows, schema={
            "t": pl.Datetime("us", "UTC"), "kind": pl.String, "subkind": pl.String, "targeted": pl.Boolean,
            "room": pl.Int8, "speaker": pl.Int8, "targets": pl.List(pl.Int8), "n_targets": pl.Int8,
            "recipients": pl.List(pl.Int8), "msg": pl.UInt32, "message_id": pl.String, "goal_no": pl.Int8,
            "pt_date": pl.String, "ref": pl.Int8, "holdout": pl.Boolean}).with_columns(
            pl.col("kind").cast(pl.Categorical), pl.col("subkind").cast(pl.Categorical))
    if getattr(sim, "kick_truth", None):
        out["kick_truth"] = pl.DataFrame(sim.kick_truth, schema=["pt_date", "minute_idx", "agent_idx", "kind", "h",
                                                                 "delay", "dur"], orient="row")
    return out


if __name__ == "__main__":
    import json
    import sys
    sk = toy_skeleton(N=8, n_days=3) if len(sys.argv) < 2 else extract_skeleton(sys.argv[1])
    print(json.dumps(sk.summary(), indent=1))
    for name in DYNAMICS:
        sim = simulate(sk, seed=1, **preset(name))
        tabs = sim.tables()
        print(name, {k: v.height for k, v in tabs.items()},
              {k: v for k, v in sim.truth["activity"].items() if k in ("J", "g_true")})
