"""H04 response machinery: matched event-triggered Green's functions, linearity tests,
fluctuation-response (FD) ratios and goal-kickoff step responses.

Shared tables only (data/processed/shared/). Every entry point takes an explicit list of
PT dates; callers are responsible for the holdout (see `select_days`).

Conventions (see the card, hypotheses/H04-reversible-forcing/README.md):
- activity n = 1 if activity_bins.state in {3 act, 4 talk}; minute = minutes since the day's window start;
- tau = 0 is the kick minute; responses are summed over tau >= 1;
- matched controls: same regime pool, no message kick reaching the agent in [m-30, m+60];
  strata = agent x state(m-1) x active-count bin x idle-count bin x day-third, coarse fallback without agent.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "3" if _v == "POLARS_MAX_THREADS" else "2")

import datetime as dt
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H04-reversible-forcing"
FIG = ROOT / "hypotheses/H04-reversible-forcing/figures"
HOLDOUT = json.loads((ROOT / "hypotheses/holdout.json").read_text())

PRE, POST = 30, 60
ISO_POST = 60  # isolation / control-eligibility window after the kick; sensitivity runs set 30 (then only A30 is clean)
LAGS = np.arange(-PRE, POST + 1)
L0 = PRE  # column index of tau = 0
HIST = 15  # pre-history window for matching
MIN_CTRL = 20
ACT_BINS = np.array([0, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3])  # 0..15 active minutes -> bin
IDLE_BINS = np.array([0] + [1] * 7 + [2] * 8)  # 0..15 idle minutes -> bin
N_LOCAL = 4 * 4 * 3 * 3  # state(m-1) x act bin x idle bin x day-third
NB_BIN = np.array([0, 1, 1] + [2] * 200)  # bystander exposures in [m-30, m+60]: 0, 1-2, 3+
N_STRATA_LOCAL = N_LOCAL * 3
RNG_SEED = 20261003


# ----------------------------------------------------------------------------- days and holdout

def calendar() -> pl.DataFrame:
    return pl.read_parquet(S / "calendar.parquet")


def is_holdout_date(d: str, goal_no: int | None) -> bool:
    if goal_no is not None and goal_no in set(HOLDOUT["goal_periods_held_out"]):
        return True
    return any(w["start"] <= d < w["end"] for w in HOLDOUT["ne_windows"])


def select_days(cal: pl.DataFrame, *, allow_holdout: bool = False, date_from: str | None = None,
                date_to: str | None = None, regimes=None, hours=None) -> list[str]:
    """PT dates with an active window. date_to is exclusive. Holdout days are dropped unless allow_holdout."""
    c = cal.filter(pl.col("window_s") > 0)
    if not allow_holdout:
        c = c.filter(~pl.col("holdout"))
    if date_from:
        c = c.filter(pl.col("pt_date") >= date_from)
    if date_to:
        c = c.filter(pl.col("pt_date") < date_to)
    if regimes is not None:
        c = c.filter(pl.col("regime").cast(pl.Utf8).is_in(list(regimes)))
    if hours is not None:
        c = c.filter(pl.col("documented_hours").is_in(list(hours)))
    days = sorted(c["pt_date"].to_list())
    if not allow_holdout:
        assert not any(is_holdout_date(d, g) for d, g in c.select("pt_date", "goal_no").iter_rows()), "holdout leak"
    return days


# ----------------------------------------------------------------------------- data structures

@dataclass
class Day:
    pt_date: str
    regime: str
    hours: int | None
    weekday: int
    goal_no: int
    win_start: dt.datetime
    agents: np.ndarray            # agent codes (rows)
    state: np.ndarray             # (n_agents, n_min) int8, 1..4
    hits_any: np.ndarray = None   # message kicks reaching the agent per minute
    hits_h: np.ndarray = None     # human messages (as room recipient)
    hits_n: np.ndarray = None     # nudges as target
    hits_nb: np.ndarray = None    # nudges as bystander
    hits_dir: np.ndarray = None   # direct kicks: nudges to the agent + human messages in its room

    @property
    def n_min(self):
        return self.state.shape[1]

    def row(self, agent: int) -> int:
        w = np.nonzero(self.agents == agent)[0]
        return int(w[0]) if len(w) else -1


def load_days(days: list[str]) -> list[Day]:
    cal = calendar().filter(pl.col("pt_date").is_in(days))
    ab = (pl.scan_parquet(S / "activity_bins.parquet").filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "minute", "agent", "state").collect().sort("pt_date", "agent", "minute"))
    meta = {r["pt_date"]: r for r in cal.iter_rows(named=True)}
    out = []
    for (d,), g in ab.group_by(["pt_date"], maintain_order=True):
        agents = np.unique(g["agent"].to_numpy())
        n_min = int(g["minute"].max()) + 1
        st = np.ones((len(agents), n_min), dtype=np.int8)
        ai = np.searchsorted(agents, g["agent"].to_numpy())
        st[ai, g["minute"].to_numpy()] = g["state"].to_numpy()
        m = meta[d]
        out.append(Day(d, str(m["regime"]), m["documented_hours"], int(m["weekday"]), int(m["goal_no"] or 0),
                       m["win_start"], agents, st))
    return out


def load_messages(days: list[str]) -> pl.DataFrame:
    """Human and nudge messages on `days` with recipients (exposure) and valid targets/mentions.

    Nudge = automated message naming >= 1 agent on that day's roster (the parser's spurious `o1` and the
    daily pause/resume bookends drop out). Returns one row per message.
    """
    chat = pl.read_parquet(S / "chat_core.parquet").with_row_index("msg")
    chat = chat.filter(pl.col("pt_date").is_in(days) & pl.col("speaker_kind").cast(pl.Utf8).is_in(["human", "automated"]))
    ros = pl.read_parquet(S / "roster.parquet").filter(~pl.col("claude_code")).select("agent", "joined", "left")
    men = (chat.select("msg", "pt_date", "mentions").explode("mentions").rename({"mentions": "agent"})
           .drop_nulls("agent").join(ros, on="agent", how="inner")
           .filter((pl.col("pt_date") >= pl.col("joined")) & (pl.col("left").is_null() | (pl.col("pt_date") < pl.col("left"))))
           .group_by("msg").agg(pl.col("agent").unique().alias("valid_mentions")))
    exp = (pl.read_parquet(S / "exposure.parquet").filter(pl.col("msg").is_in(chat["msg"].implode()))
           .group_by("msg").agg(pl.col("agent").alias("recipients")))
    m = chat.join(men, on="msg", how="left").join(exp, on="msg", how="left")
    m = m.with_columns(pl.col("valid_mentions").fill_null(pl.lit([], dtype=pl.List(pl.Int8))),
                       pl.col("recipients").fill_null(pl.lit([], dtype=pl.List(pl.Int8))))
    m = m.with_columns(
        pl.when(pl.col("speaker_kind").cast(pl.Utf8) == "human").then(pl.lit("human"))
        .when(pl.col("valid_mentions").list.len() > 0).then(pl.lit("nudge"))
        .otherwise(pl.lit("bookend")).alias("kind"))
    return m.select("msg", "t", "pt_date", "room", "kind", "valid_mentions", "recipients", "length")


def responder_rows(days: list[Day], msgs: pl.DataFrame) -> pl.DataFrame:
    """One row per (message, responding agent): day index, minute, row, kind, role."""
    dix = {d.pt_date: k for k, d in enumerate(days)}
    rows = []
    for r in msgs.filter(pl.col("kind") != "bookend").iter_rows(named=True):
        k = dix.get(r["pt_date"])
        if k is None:
            continue
        d = days[k]
        minute = int((r["t"] - d.win_start).total_seconds() // 60)
        if minute < 0 or minute >= d.n_min:
            continue
        rec = set(r["recipients"]) | (set(r["valid_mentions"]) if r["kind"] == "nudge" else set())
        men = set(r["valid_mentions"])
        for a in rec:
            i = d.row(a)
            if i < 0:
                continue
            if r["kind"] == "nudge":
                role = "target" if a in men else "bystander"
            else:
                role = "mentioned" if a in men else "unmentioned"
            rows.append((k, minute, i, a, r["kind"], role, r["msg"]))
    return pl.DataFrame(rows, schema=["day", "minute", "row", "agent", "kind", "role", "msg"], orient="row")


def attach_hits(days: list[Day], resp: pl.DataFrame):
    for d in days:
        z = lambda: np.zeros(d.state.shape, dtype=np.int16)
        d.hits_any, d.hits_h, d.hits_n, d.hits_nb, d.hits_dir = z(), z(), z(), z(), z()
    for k, minute, i, kind, role in resp.select("day", "minute", "row", "kind", "role").iter_rows():
        d = days[k]
        d.hits_any[i, minute] += 1
        if kind == "human":
            d.hits_h[i, minute] += 1
            d.hits_dir[i, minute] += 1
        elif role == "target":
            d.hits_n[i, minute] += 1
            d.hits_dir[i, minute] += 1
        else:
            d.hits_nb[i, minute] += 1


def window_sum(x: np.ndarray, lo: int, hi: int) -> np.ndarray:
    """Sum of x[:, m+lo .. m+hi] (inclusive, truncated at edges) for every m."""
    n = x.shape[1]
    cs = np.concatenate([np.zeros((x.shape[0], 1), dtype=np.int64), np.cumsum(x, axis=1, dtype=np.int64)], axis=1)
    m = np.arange(n)
    a = np.clip(m + lo, 0, n)
    b = np.clip(m + hi + 1, 0, n)
    return cs[:, b] - cs[:, a]


# ----------------------------------------------------------------------------- cell table

@dataclass
class Cells:
    """All agent-minutes with a full pre-history (m >= HIST) and tau=+30 inside the day."""
    day: np.ndarray
    row: np.ndarray
    minute: np.ndarray
    agent: np.ndarray
    s_base_full: np.ndarray  # pre-history stratum with agent identity (without the bystander bin)
    s_base_local: np.ndarray # pre-history stratum without agent
    nbw: np.ndarray          # bystander nudge exposures in [m-30, m+60]
    eligible: np.ndarray     # control-eligible: no direct kick in [m-30, m+60]
    traj: np.ndarray         # (n_cells, len(LAGS)) int8, -1 = outside the day
    act_on: np.ndarray       # n(m)=1 and n(m-1)=0 (an activation at m)
    post30: np.ndarray       # sum_{s=1..30} n(m+s)
    act10: np.ndarray = None # an activation (0->1) within tau = 1..10
    index: dict = field(default_factory=dict)  # (day,row,minute) -> cell id

    def strata(self, ids, nb_adjust: int = 0):
        nb = NB_BIN[np.clip(self.nbw[ids] + nb_adjust, 0, len(NB_BIN) - 1)]
        return self.s_base_full[ids] * 3 + nb, self.s_base_local[ids] * 3 + nb

    @property
    def s_full(self):
        return self.strata(slice(None))[0]

    @property
    def s_local(self):
        return self.strata(slice(None))[1]

    def lookup(self, day, row, minute) -> np.ndarray:
        return np.array([self.index.get((int(a), int(b), int(c)), -1) for a, b, c in zip(day, row, minute)], dtype=np.int64)


def build_cells(days: list[Day], agent_codes: np.ndarray, var: str = "active") -> Cells:
    """var = "active" (state 3 or 4) or "talk" (state 4) for the response trajectories; strata always use activity."""
    parts = {k: [] for k in ("day", "row", "minute", "agent", "s_base_full", "s_base_local", "nbw", "eligible", "traj", "act_on", "post30")}
    a_index = {int(a): j for j, a in enumerate(agent_codes)}
    for k, d in enumerate(days):
        st = d.state
        n = (st >= 3).astype(np.int8)
        y = n if var == "active" else (st == 4).astype(np.int8)
        idle = (st == 2).astype(np.int8)
        na, nm = st.shape
        if nm < HIST + 31:
            continue
        m = np.arange(HIST, nm - 30)
        act15 = window_sum(n, -HIST, -1)[:, m]
        idl15 = window_sum(idle, -HIST, -1)[:, m]
        sprev = st[:, m - 1].astype(np.int64) - 1
        tod = (m * 3 // nm)[None, :].repeat(na, 0)
        loc = ((sprev * 4 + ACT_BINS[act15]) * 3 + IDLE_BINS[idl15]) * 3 + tod
        aidx = np.array([a_index[int(a)] for a in d.agents])[:, None].repeat(len(m), 1)
        elig = (window_sum(d.hits_dir, -PRE, ISO_POST)[:, m] == 0)
        nbw = window_sum(d.hits_nb, -PRE, ISO_POST)[:, m]
        pad = np.full((na, PRE + nm + POST), -1, dtype=np.int8)
        pad[:, PRE:PRE + nm] = y
        cols = PRE + m[:, None] + LAGS[None, :]                      # (len(m), n_lags)
        traj = pad[:, cols]                                          # (na, len(m), n_lags)
        act_on = (y[:, m] == 1) & (y[:, m - 1] == 0)
        post30 = window_sum(y, 1, 30)[:, m]
        rows_ = np.arange(na)[:, None].repeat(len(m), 1)
        parts["day"].append(np.full(na * len(m), k, dtype=np.int32))
        parts["row"].append(rows_.ravel().astype(np.int16))
        parts["minute"].append(np.tile(m, na).astype(np.int32))
        parts["agent"].append(np.repeat(d.agents, len(m)).astype(np.int16))
        parts["s_base_full"].append((aidx * N_LOCAL + loc).ravel())
        parts["s_base_local"].append(loc.ravel())
        parts["nbw"].append(nbw.ravel().astype(np.int16))
        parts["eligible"].append(elig.ravel())
        parts["traj"].append(traj.reshape(-1, len(LAGS)))
        parts["act_on"].append(act_on.ravel())
        parts["post30"].append(post30.ravel().astype(np.int16))
    c = Cells(**{k: np.concatenate(v) for k, v in parts.items()})
    t = c.traj[:, L0:L0 + 11]
    c.act10 = ((t[:, 1:] == 1) & (t[:, :-1] == 0)).any(axis=1)
    c.index = {(int(a), int(b), int(m)): j for j, (a, b, m) in enumerate(zip(c.day, c.row, c.minute))}
    return c


@dataclass
class Controls:
    mean_full: np.ndarray
    cnt_full: np.ndarray
    mean_local: np.ndarray
    cnt_local: np.ndarray
    act_full: np.ndarray      # mean post30 of spontaneous activations per full stratum
    act_full_n: np.ndarray
    act_local: np.ndarray
    act_local_n: np.ndarray
    act_traj_full: np.ndarray  # mean trajectory after spontaneous activations (per full stratum)
    act_traj_local: np.ndarray
    non_traj_full: np.ndarray = None   # mean trajectory after a non-activation (n(m)=n(m-1)=0)
    non_traj_local: np.ndarray = None
    non_full_n: np.ndarray = None
    non_local_n: np.ndarray = None
    act10_full: np.ndarray = None      # P(activation within 10 min) among eligible cells
    act10_local: np.ndarray = None


def control_means(c: Cells, n_agents: int) -> Controls:
    nf, nl = n_agents * N_STRATA_LOCAL, N_STRATA_LOCAL
    e = c.eligible
    tr = c.traj[e]
    SF, SL = c.s_full, c.s_local
    sf, sl = SF[e], SL[e]
    mf = np.zeros((nf, len(LAGS))); kf = np.zeros((nf, len(LAGS)))
    ml = np.zeros((nl, len(LAGS))); kl = np.zeros((nl, len(LAGS)))
    for j in range(len(LAGS)):
        v = tr[:, j] >= 0
        x = tr[:, j].astype(np.float64)
        kf[:, j] = np.bincount(sf[v], minlength=nf)
        mf[:, j] = np.bincount(sf[v], weights=x[v], minlength=nf)
        kl[:, j] = np.bincount(sl[v], minlength=nl)
        ml[:, j] = np.bincount(sl[v], weights=x[v], minlength=nl)
    with np.errstate(invalid="ignore", divide="ignore"):
        mf, ml = mf / kf, ml / kl
    # spontaneous activations (eligible, activation at m, post window inside the day)
    a = e & c.act_on & (c.traj[:, L0 + 30] >= 0)
    af_n = np.bincount(SF[a], minlength=nf).astype(float)
    al_n = np.bincount(SL[a], minlength=nl).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        af = np.bincount(SF[a], weights=c.post30[a], minlength=nf) / af_n
        al = np.bincount(SL[a], weights=c.post30[a], minlength=nl) / al_n
        post = c.traj[a][:, L0 + 1:L0 + 31].astype(float)
        atf = np.stack([np.bincount(SF[a], weights=post[:, s], minlength=nf) for s in range(30)], 1) / af_n[:, None]
        atl = np.stack([np.bincount(SL[a], weights=post[:, s], minlength=nl) for s in range(30)], 1) / al_n[:, None]
    z = e & (c.traj[:, L0] == 0) & (c.traj[:, L0 - 1] == 0) & (c.traj[:, L0 + 30] >= 0)
    nf_n = np.bincount(SF[z], minlength=nf).astype(float)
    nl_n = np.bincount(SL[z], minlength=nl).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        post0 = c.traj[z][:, L0 + 1:L0 + 31].astype(float)
        ntf = np.stack([np.bincount(SF[z], weights=post0[:, s_], minlength=nf) for s_ in range(30)], 1) / nf_n[:, None]
        ntl = np.stack([np.bincount(SL[z], weights=post0[:, s_], minlength=nl) for s_ in range(30)], 1) / nl_n[:, None]
        p10f = np.bincount(sf, weights=c.act10[e].astype(float), minlength=nf) / np.bincount(sf, minlength=nf)
        p10l = np.bincount(sl, weights=c.act10[e].astype(float), minlength=nl) / np.bincount(sl, minlength=nl)
    return Controls(mf, kf, ml, kl, af, af_n, al, al_n, atf, atl, ntf, ntl, nf_n, nl_n, p10f, p10l)


# ----------------------------------------------------------------------------- Green's functions

@dataclass
class Resp:
    """Per-day sums of (treated - matched control) trajectories for one treated set."""
    name: str
    n_cells: int
    n_kicks: int
    fallback: float
    day_sum: np.ndarray   # (n_days, n_lags)
    day_cnt: np.ndarray
    day_y1: np.ndarray    # per-day sum of treated n at tau=1
    day_c1: np.ndarray    # per-day sum of control mean at tau=1
    day_n1: np.ndarray


def matched_response(c: Cells, ctl: Controls, cell_ids: np.ndarray, n_days: int, name: str, n_kicks: int | None = None,
                     nb_adjust: int = 0) -> Resp:
    """nb_adjust = -1 for bystander-treated cells (their own exposure is the kick, not the environment)."""
    ids = cell_ids[cell_ids >= 0]
    nl = len(LAGS)
    if len(ids) == 0:
        z = np.zeros((n_days, nl))
        return Resp(name, 0, 0, np.nan, z, z.copy(), np.zeros(n_days), np.zeros(n_days), np.zeros(n_days))
    sf, sl = c.strata(ids, nb_adjust)
    use_full = ctl.cnt_full[sf, L0 + 1] >= MIN_CTRL
    cm = np.where(use_full[:, None], ctl.mean_full[sf], ctl.mean_local[sl])
    tr = c.traj[ids].astype(float)
    valid = (c.traj[ids] >= 0) & np.isfinite(cm)
    res = np.where(valid, tr - np.nan_to_num(cm), 0.0)
    dd = c.day[ids]
    day_sum = np.zeros((n_days, nl)); day_cnt = np.zeros((n_days, nl))
    np.add.at(day_sum, dd, res)
    np.add.at(day_cnt, dd, valid.astype(float))
    v1 = valid[:, L0 + 1]
    y1 = np.bincount(dd[v1], weights=tr[v1, L0 + 1], minlength=n_days)
    c1 = np.bincount(dd[v1], weights=cm[v1, L0 + 1], minlength=n_days)
    n1 = np.bincount(dd[v1], minlength=n_days).astype(float)
    return Resp(name, len(ids), n_kicks if n_kicks is not None else len(ids), float(1 - use_full.mean()),
                day_sum, day_cnt, y1, c1, n1)


def boot_weights(n_days: int, B: int = 1000, seed: int = RNG_SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    w = rng.multinomial(n_days, np.full(n_days, 1 / n_days), size=B).astype(float)
    return np.vstack([np.ones((1, n_days)), w])  # row 0 = the point estimate


def curves(r: Resp, W: np.ndarray) -> np.ndarray:
    """G(tau) for each bootstrap row of W: (B+1, n_lags)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        return (W @ r.day_sum) / (W @ r.day_cnt)


def amp(G: np.ndarray, lo: int, hi: int) -> np.ndarray:
    return np.nansum(G[..., L0 + lo:L0 + hi + 1], axis=-1)


def ci(x: np.ndarray, q=(2.5, 97.5)):
    x = np.asarray(x, float)
    b = x[1:][np.isfinite(x[1:])]
    lo, hi = (np.percentile(b, q) if len(b) > 10 else (np.nan, np.nan))
    return float(x[0]), float(lo), float(hi)


def shape_stats(g: np.ndarray) -> dict:
    """Peak lag and 1/e relaxation time of a point-estimate curve (tau >= 1)."""
    post = g[L0 + 1:]
    if not np.isfinite(post).any():
        return {"peak_lag": None, "peak": None, "relax_1e": None}
    sm = np.convolve(np.nan_to_num(post), np.ones(3) / 3, mode="same")
    p = int(np.argmax(sm))
    pk = sm[p]
    if pk <= 0:
        return {"peak_lag": None, "peak": float(pk), "relax_1e": None}
    after = np.nonzero(sm[p:] < pk / np.e)[0]
    return {"peak_lag": p + 1, "peak": float(pk), "relax_1e": (int(after[0]) if len(after) else None)}


def summarize(r: Resp, W: np.ndarray) -> dict:
    G = curves(r, W)
    out = {"name": r.name, "n_cells": r.n_cells, "n_kicks": r.n_kicks, "n_days": int((r.day_cnt[:, L0 + 1] > 0).sum()),
           "fallback_share": r.fallback}
    if r.n_cells == 0:
        return out
    for lab, (lo, hi) in {"A30": (1, 30), "A60": (1, 60), "placebo_m30_m16": (-30, -16), "pre_m15_m1": (-15, -1)}.items():
        out[lab] = ci(amp(G, lo, hi))
    out.update(shape_stats(G[0]))
    out["G"] = G[0].tolist()
    lo, hi = np.nanpercentile(G[1:], [2.5, 97.5], axis=0)
    out["G_lo"], out["G_hi"] = lo.tolist(), hi.tolist()
    return out


def ratio_test(num: np.ndarray, den: np.ndarray) -> dict:
    """Linearity verdict on a bootstrap ratio (row 0 = point). Rule fixed on the card."""
    with np.errstate(invalid="ignore", divide="ignore"):
        r = num / den
    p, lo, hi = ci(r)
    den_p, den_lo, den_hi = ci(den)
    if not (np.isfinite(den_lo) and (den_lo > 0 or den_hi < 0)):
        verdict = "inconclusive (reference response not significant)"
    elif not np.isfinite(lo):
        verdict = "inconclusive (too few)"
    elif 0.67 <= p <= 1.5 and lo <= 1 <= hi:
        verdict = "pass"
    elif hi < 0.67 or lo > 1.5:
        verdict = "fail"
    else:
        verdict = "inconclusive"
    return {"ratio": p, "lo": lo, "hi": hi, "verdict": verdict}


# ----------------------------------------------------------------------------- FD: autocorrelation, CKP and Onsager

def autocorr(days: list[Day], agents_w: dict[int, float], max_lag: int = POST) -> np.ndarray:
    """Connected autocorrelation C(tau) of n on kick-free minutes (no message kick in [m-30, m+60]),
    centered per agent-day, pooled per agent, then weighted across agents by agents_w."""
    num = {a: np.zeros(max_lag + 1) for a in agents_w}
    den = {a: np.zeros(max_lag + 1) for a in agents_w}
    for d in days:
        free = window_sum(d.hits_dir, -PRE, ISO_POST) == 0
        n = (d.state >= 3).astype(float)
        for i, a in enumerate(d.agents):
            a = int(a)
            if a not in agents_w:
                continue
            f = free[i]
            if f.sum() < max_lag + 10:
                continue
            x = n[i] - n[i][f].mean()
            for t in range(max_lag + 1):
                ok = f[:len(f) - t] & f[t:]
                num[a][t] += (x[:len(x) - t] * x[t:])[ok].sum()
                den[a][t] += ok.sum()
    C = np.zeros(max_lag + 1); wsum = 0.0
    for a, w in agents_w.items():
        if den[a][max_lag] > 0:
            C += w * num[a] / den[a]; wsum += w
    return C / wsum if wsum else C * np.nan


def ckp(r: Resp, W: np.ndarray, C: np.ndarray) -> dict:
    """CKP fluctuation-dissipation ratio with log-odds field calibration (convention on the card)."""
    G = curves(r, W)
    with np.errstate(invalid="ignore", divide="ignore"):
        pk = (W @ r.day_y1) / (W @ r.day_n1)
        pc = (W @ r.day_c1) / (W @ r.day_n1)
        lg = lambda p: np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
        h = lg(pk) - lg(pc)
        chi = np.cumsum(G[:, L0 + 1:L0 + 31], axis=1) / h[:, None]            # tau = 1..30
    lam = C[1] / C[0]
    ref = (1 + lam) * (C[0] - C[1:31])                                          # tau = 1..30
    X = chi / ref[None, :]
    sl = slice(4, 30)  # tau = 5..30
    xs = ref[sl]
    slope = np.array([np.polyfit(xs, chi[b, sl], 1)[0] if np.all(np.isfinite(chi[b, sl])) else np.nan for b in range(len(W))])
    out = {"h_logodds": ci(h), "p_kick_tau1": ci(pk), "p_ctrl_tau1": ci(pc), "lambda": float(lam),
           "C0": float(C[0]), "X_fast": ci(X[:, 0]), "X_tau10": ci(X[:, 9]), "X_tau30": ci(X[:, 29]),
           "X_slow": ci(slope)}
    with np.errstate(divide="ignore", invalid="ignore"):
        out["Teff_slow"] = ci(1 / slope)
        out["Teff_fast"] = ci(1 / X[:, 0])
    out["chi"] = chi[0].tolist(); out["ref"] = ref.tolist(); out["C"] = C.tolist()
    h_p, h_lo, h_hi = out["h_logodds"]
    out["h_significant"] = bool(np.isfinite(h_lo) and (h_lo > 0 or h_hi < 0))
    return out


def onsager(c: Cells, ctl: Controls, cell_ids: np.ndarray, n_days: int, W: np.ndarray, max_wait: int = 10,
            nb_adjust: int = 0) -> dict:
    """Onsager-regression FD ratio, aligned on the responder's first activation within max_wait min after a kick.

    For each kicked activation at minute a (stratum s at a): E_kick(u) = n(a+u), u = 1..30; E1(u) = mean after
    spontaneous activations in s; E0(u) = mean after non-activations in s (same pre-history). Then
    X(tau) = sum_{u<=tau} (E_kick - E0) / sum_{u<=tau} (E1 - E0); X = 1 if the kick acts only as a one-step field
    on the activation (the reading turn); T_eff = 1/X. Also reports the kick's shift in P(activation within 10 min).
    """
    ids = cell_ids[cell_ids >= 0]
    sf, sl = c.strata(ids, nb_adjust)
    use_f = np.isfinite(ctl.act10_full[sf]) & (ctl.cnt_full[sf, L0 + 1] >= MIN_CTRL)
    p10c = np.where(use_f, ctl.act10_full[sf], ctl.act10_local[sl])
    dd0 = c.day[ids]
    with np.errstate(invalid="ignore", divide="ignore"):
        k10 = np.bincount(dd0, weights=c.act10[ids].astype(float), minlength=n_days)
        c10 = np.bincount(dd0, weights=np.nan_to_num(p10c), minlength=n_days)
        n10 = np.bincount(dd0, minlength=n_days).astype(float)
        p_k, p_c = (W @ k10) / (W @ n10), (W @ c10) / (W @ n10)
    out = {"p_act10_kick": ci(p_k), "p_act10_ctrl": ci(p_c), "p_act10_diff": ci(p_k - p_c)}
    rows = []
    for j in ids:
        tr = c.traj[j]
        for w in range(1, max_wait + 1):
            if tr[L0 + w] < 0:
                break
            if tr[L0 + w] == 1 and tr[L0 + w - 1] == 0:
                a = c.index.get((int(c.day[j]), int(c.row[j]), int(c.minute[j]) + w), -1)
                if a < 0 or c.traj[a, L0 + 30] < 0:
                    break
                sfa, sla = (int(x[0]) for x in c.strata(np.array([a]), nb_adjust))
                if ctl.act_full_n[sfa] >= MIN_CTRL and ctl.non_full_n[sfa] >= MIN_CTRL:
                    e1, e0 = ctl.act_traj_full[sfa], ctl.non_traj_full[sfa]
                elif ctl.act_local_n[sla] >= MIN_CTRL and ctl.non_local_n[sla] >= MIN_CTRL:
                    e1, e0 = ctl.act_traj_local[sla], ctl.non_traj_local[sla]
                else:
                    break
                rows.append((c.day[a], c.traj[a, L0 + 1:L0 + 31].astype(float), e1, e0))
                break
    out["n_activations"] = len(rows)
    out["share_of_kicks_activated"] = len(rows) / max(1, len(ids))
    if len(rows) < 10:
        out["X"] = None
        return out
    dd = np.array([r[0] for r in rows])
    ek = np.array([r[1] for r in rows]); e1 = np.array([r[2] for r in rows]); e0 = np.array([r[3] for r in rows])
    num = np.zeros((n_days, 30)); den = np.zeros((n_days, 30)); raw_k = np.zeros(n_days); raw_1 = np.zeros(n_days)
    np.add.at(num, dd, np.cumsum(ek - e0, 1)); np.add.at(den, dd, np.cumsum(e1 - e0, 1))
    np.add.at(raw_k, dd, ek.sum(1)); np.add.at(raw_1, dd, e1.sum(1))
    with np.errstate(invalid="ignore", divide="ignore"):
        X = (W @ num) / (W @ den)
        out["X"] = {f"tau{t}": ci(X[:, t - 1]) for t in (1, 5, 10, 20, 30)}
        out["Teff_tau30"] = ci(1 / X[:, 29])
        out["_X30_rows"] = X[:, 29]
        out["raw_ratio_post30"] = ci((W @ raw_k) / (W @ raw_1))
    out["kicked_traj"] = ek.mean(0).tolist(); out["spont_traj"] = e1.mean(0).tolist(); out["non_traj"] = e0.mean(0).tolist()
    return out


def fdt_shape(r: Resp, W: np.ndarray, C: np.ndarray, split: int = 5, horizon: int = 30) -> dict:
    """Field-units-free FDT shape test. Under FDT the impulse response is proportional to -dC/dtau, so the share of
    the integrated response over tau = 1..horizon that falls after tau = split must equal the share of the
    correlation drop C(0) - C(horizon) that occurs after tau = split."""
    G = curves(r, W)
    with np.errstate(invalid="ignore", divide="ignore"):
        fR = np.nansum(G[:, L0 + split + 1:L0 + horizon + 1], 1) / np.nansum(G[:, L0 + 1:L0 + horizon + 1], 1)
    fC = (C[split] - C[horizon]) / (C[0] - C[horizon])
    return {"share_resp_after": ci(fR), "share_corr_drop_after": float(fC), "split": split, "horizon": horizon,
            "C_over_C0": (np.asarray(C) / C[0]).round(4).tolist()}


# ----------------------------------------------------------------------------- H04-MF: mean-field forward check (HH81)

MF_MA = 61     # centered moving-average window (min) for detrending the field
MF_LAGS = 31


def _ma(x: np.ndarray, w: int) -> np.ndarray:
    h = w // 2
    n = x.shape[1]
    cs = np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(x, 1)], 1)
    a = np.clip(np.arange(n) - h, 0, n); b = np.clip(np.arange(n) + h + 1, 0, n)
    return (cs[:, b] - cs[:, a]) / (b - a)


def e_time(c: np.ndarray) -> float:
    """1/e crossing of a normalized correlation (or response) curve indexed by lag 0, 1, 2, ... (linear interpolation)."""
    below = np.nonzero(c < 1 / np.e)[0]
    if not len(below) or below[0] == 0:
        return np.nan
    t = below[0]
    return float(t - 1 + (c[t - 1] - 1 / np.e) / (c[t - 1] - c[t]))


def mf_day_stats(days: list[Day]) -> dict:
    """Per-day sums for the Curie-Weiss inversion and autocorrelations (detrended and day-centered variants)."""
    nd = len(days)
    out = {k: np.zeros(nd) for k in ("v_tot", "v_ind", "v_tot_c", "v_ind_c", "hom_num", "hom_den")}
    out["a1"] = np.zeros((nd, MF_LAGS)); out["am"] = np.zeros((nd, MF_LAGS))
    for k, d in enumerate(days):
        sp = 2.0 * (d.state >= 3) - 1.0
        if sp.shape[1] < MF_MA:
            continue
        x = sp - _ma(sp, MF_MA)
        X = x.sum(0)
        out["v_tot"][k] = (X ** 2).sum(); out["v_ind"][k] = (x ** 2).sum()
        xc = sp - sp.mean(1, keepdims=True)
        out["v_tot_c"][k] = (xc.sum(0) ** 2).sum(); out["v_ind_c"][k] = (xc ** 2).sum()
        m = sp.mean(0); N, T = sp.shape
        out["hom_num"][k] = N * ((m - m.mean()) ** 2).sum(); out["hom_den"][k] = T * (1 - m.mean() ** 2)
        for t in range(MF_LAGS):
            out["a1"][k, t] = (x[:, :T - t] * x[:, t:]).sum()
            out["am"][k, t] = (X[:T - t] * X[t:]).sum()
    return out


def mean_field(days: list[Day], W: np.ndarray) -> dict:
    st = mf_day_stats(days)
    with np.errstate(invalid="ignore", divide="ignore"):
        VR = (W @ st["v_tot"]) / (W @ st["v_ind"])
        VRc = (W @ st["v_tot_c"]) / (W @ st["v_ind_c"])
        VRh = (W @ st["hom_num"]) / (W @ st["hom_den"])
        c1 = (W @ st["a1"]); c1 = c1 / c1[:, :1]
        cm = (W @ st["am"]); cm = cm / cm[:, :1]
    K = 1 - 1 / VR
    tau0 = np.array([e_time(r) for r in c1]); taum = np.array([e_time(r) for r in cm])
    tau0_int = c1[:, :31].sum(1) - 0.5
    tau_pred = tau0 / (1 - K)
    return {"VR": ci(VR), "K": ci(K), "K_daycentered": ci(1 - 1 / VRc), "K_homogeneous": ci(1 - 1 / VRh),
            "tau0": ci(tau0), "tau0_integrated": ci(tau0_int), "tau_m": ci(taum), "tau_pred": ci(tau_pred),
            "taum_over_tau0": ci(taum / tau0), "inv_1mK": ci(1 / (1 - K)),
            "mf_p3_ratio": ci((taum / tau0) * (1 - K)),
            "c1": c1[0].round(4).tolist(), "cm": cm[0].round(4).tolist(), "_tau_pred_rows": tau_pred, "_K_rows": K}


def decay_rows(Gb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per bootstrap row: 1/e relaxation time after the smoothed peak, and effective width A60/peak (minutes)."""
    rel, wid = [], []
    for g in Gb:
        post = np.nan_to_num(g[L0 + 1:])
        sm = np.convolve(post, np.ones(3) / 3, mode="same")
        p = int(np.argmax(sm)); pk = sm[p]
        if pk <= 0:
            rel.append(np.nan); wid.append(np.nan); continue
        tail = sm[p:] / pk
        rel.append(e_time(tail)); wid.append(post.sum() / pk)
    return np.array(rel), np.array(wid)


# ----------------------------------------------------------------------------- provenance

def git_commit() -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        return r.stdout.strip() or "none (not a git repository)"
    except Exception:
        return "none"


def write_provenance(entry: str, built_by: str, tables: list[str], params: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov[entry] = {"built_by": built_by, "git_commit": git_commit(),
                   "inputs": [{"source": "data/processed/shared (ai-village rev 838b4150303ca8228e8edb432d8b8ccae353d258)",
                               "tables": tables}],
                   "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1))


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, float) and not np.isfinite(o):
            return None
        return str(o)
    txt = json.dumps(obj, default=conv, indent=1, allow_nan=True)
    txt = txt.replace("NaN", "null").replace("-Infinity", "null").replace("Infinity", "null")
    path.write_text(txt)


# ----------------------------------------------------------------------------- treated sets

def build_sets(days: list[Day], resp: pl.DataFrame, c: Cells) -> dict:
    """Treated cell sets for G, dose, superposition and time translation.

    Isolation is on *direct* kicks (nudges to the agent, human messages in its room) in [m-30, m+60];
    bystander exposures are allowed and handled by the bystander-count stratum. "strict" variants also
    exclude every bystander exposure. Returns {name: {"ids", "n_kicks", "nb_adjust", ...extra}}.
    """
    W = {}
    for k, d in enumerate(days):
        W[k] = {
            "dir": window_sum(d.hits_dir, -PRE, ISO_POST),
            "any": window_sum(d.hits_any, -PRE, ISO_POST),
            "pre": window_sum(d.hits_dir, -PRE, -1),
            "now2": window_sum(d.hits_dir, 0, 1),
            "now2_h": window_sum(d.hits_h, 0, 1),
            "now2_n": window_sum(d.hits_n, 0, 1),
            "after2": window_sum(d.hits_dir, 2, ISO_POST),
            "after1": window_sum(d.hits_dir, 1, ISO_POST),
        }
    r = resp.with_columns(pl.col("day").cast(pl.Int64))
    sets = {}

    def add(name, rows, nb_adjust=0, **extra):
        rows = rows.unique(["day", "row", "minute"], maintain_order=True)
        ids = c.lookup(rows["day"].to_numpy(), rows["row"].to_numpy(), rows["minute"].to_numpy())
        keep = ids >= 0
        ent = {"ids": ids[keep], "nb_adjust": nb_adjust,
               "n_kicks": int(rows.filter(pl.Series(keep))["msg"].n_unique()) if len(rows) else 0}
        for k_, v in extra.items():
            ent[k_] = np.asarray(v)[keep]
        sets[name] = ent

    def wstat(rows, key):
        return np.array([W[k][key][i, m] for k, i, m in rows.select("day", "row", "minute").iter_rows()], dtype=np.int64)

    groups = {
        "nudge_target": (r.filter((pl.col("kind") == "nudge") & (pl.col("role") == "target")), 1, 0),
        "nudge_bystander": (r.filter((pl.col("kind") == "nudge") & (pl.col("role") == "bystander")), 0, -1),
        "human_all": (r.filter(pl.col("kind") == "human"), 1, 0),
        "human_mentioned": (r.filter((pl.col("kind") == "human") & (pl.col("role") == "mentioned")), 1, 0),
        "human_unmentioned": (r.filter((pl.col("kind") == "human") & (pl.col("role") == "unmentioned")), 1, 0),
    }
    for g, (rows, own_direct, nba) in groups.items():
        rows = rows.unique(["day", "row", "minute"], maintain_order=True)
        add(g + "_all", rows, nba)
        if not len(rows):
            continue
        dirw, anyw = wstat(rows, "dir"), wstat(rows, "any")
        iso = rows.filter(pl.Series(dirw == own_direct))
        add(g + "_iso", iso, nba)
        add(g + "_strict", rows.filter(pl.Series((dirw == own_direct) & (anyw == 1))), nba)
        if len(iso):
            nm = np.array([days[k].n_min for k in iso["day"].to_list()])
            third = iso["minute"].to_numpy() * 3 // nm
            wd = np.array([days[k].weekday for k in iso["day"].to_list()])
            add(g + "_iso_early", iso.filter(pl.Series(third == 0)), nba)
            add(g + "_iso_mid", iso.filter(pl.Series(third == 1)), nba)
            add(g + "_iso_late", iso.filter(pl.Series(third == 2)), nba)
            add(g + "_iso_mon", iso.filter(pl.Series(wd == 1)), nba)
            add(g + "_iso_midweek", iso.filter(pl.Series((wd >= 2) & (wd <= 4))), nba)
            add(g + "_iso_fri", iso.filter(pl.Series(wd == 5)), nba)

    # dose: n direct kicks of one type within [m, m+1], no other direct kick in [m-30, m+60]
    for kind, key, role in (("human", "now2_h", None), ("nudge", "now2_n", "target")):
        rows = r.filter(pl.col("kind") == kind)
        if role:
            rows = rows.filter(pl.col("role") == role)
        rows = rows.unique(["day", "row", "minute"], maintain_order=True)
        if not len(rows):
            continue
        pre, now2, nowk, after2 = (wstat(rows, x) for x in ("pre", "now2", key, "after2"))
        clean = (pre == 0) & (after2 == 0) & (now2 == nowk)
        for lab, lo, hi in (("1", 1, 1), ("2", 2, 2), ("3to4", 3, 4), ("5plus", 5, 999)):
            sel = clean & (nowk >= lo) & (nowk <= hi)
            add(f"dose_{kind}_{lab}", rows.filter(pl.Series(sel)), 0, dose=nowk[sel])

    # superposition: exactly two direct kicks of one type in [m-30, m+60], the second 3..20 min after the first
    for kind, hk, role in (("human", "hits_h", None), ("nudge", "hits_n", "target")):
        rows = r.filter(pl.col("kind") == kind)
        if role:
            rows = rows.filter(pl.col("role") == role)
        rows = rows.unique(["day", "row", "minute"], maintain_order=True)
        sel, delta = [], []
        for k, i, m in rows.select("day", "row", "minute").iter_rows():
            d = days[k]
            H, A = getattr(d, hk), d.hits_dir
            ok = (W[k]["pre"][i, m] == 0 and A[i, m] == 1 and H[i, m] == 1 and W[k]["after1"][i, m] == 1)
            dlt = -1
            if ok:
                nxt = np.nonzero(A[i, m + 1:m + ISO_POST + 1])[0]
                dlt = int(nxt[0]) + 1 if len(nxt) else -1
                ok = 3 <= dlt <= 20 and H[i, m + dlt] == 1
            sel.append(ok); delta.append(dlt if ok else -1)
        sel = np.array(sel, bool)
        add(f"pair_{kind}", rows.filter(pl.Series(sel)) if len(rows) else rows, 0, delta=np.array(delta)[sel] if len(rows) else [])
    return sets
