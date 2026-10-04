"""H40 core library: the call-clock hazard model.

For a message m from sender j read out by recipient i at call c1 (context ledger), every later call c_n of i
(n = 1 is the read-out call) is an update attempt; y = 1 at the call that produced i's reply to m (DQ2 parent).

  cloglog h_n = alpha_{i,u} + [n=1](b1 + eta1 log W + ...) + [n>=2](phi log n + psi log a + chi log(1+b) + eta log e)
                + delta log(1+k) + zeta ment + gap / mode / prev-talk / reset terms

Call clock: eta = eta1 = 0. Wall clock: eta = 1 (cloglog makes h = 1 - exp(-lambda e) exact).

Everything here works on numpy arrays indexed by call_windows.turn_id (= row index, sorted by agent then time).
Threads pinned to <= 2 (project rule).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import scipy.sparse as sp  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H40-call-clock-coupling"
OUT = ROOT / "data/processed/H40-call-clock-coupling"
SH = ROOT / "data/processed/shared"
FIG = HYP / "figures"
SEED = 20261004
T0 = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
H_FIT_S = 1800.0          # risk-set horizon for fitting: 30 min of wall age
H_EPS_S = 2100.0          # horizon kept for the cadence-elasticity computation (30 min / 0.86)
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask  # noqa: E402,F401

GAPS = ["busy", "long_prev", "pause", "after_vol", "after_forced", "other"]
GAP_CODE = {g: i for i, g in enumerate(GAPS)}


# ----------------------------------------------------------------------------- calls

@dataclass
class Calls:
    agent: np.ndarray
    day: np.ndarray          # int32 code of pt_date
    goal: np.ndarray
    t: np.ndarray            # float64 seconds since T0 (t_call)
    lo: np.ndarray
    hi: np.ndarray
    t_end: np.ndarray
    summary: np.ndarray      # bool: CONSOLIDATE / session stop (cannot talk, receives nothing)
    talk: np.ndarray
    gap: np.ndarray          # int8 GAPS code
    chat: np.ndarray         # bool: regime-I/II chat-mode call
    k_new: np.ndarray
    reset: np.ndarray        # any context reset since the previous receiving call
    holdout: np.ndarray
    first_of_day: np.ndarray
    conf: np.ndarray         # 0 low 1 medium 2 high
    pause_s: np.ndarray
    day_end: np.ndarray      # last turn_id of the same agent-day block
    key: np.ndarray          # agent * 1e9 + t, monotone in turn_id
    days: list = field(default_factory=list)

    @property
    def n(self):
        return len(self.t)


def _sec(col: pl.Series) -> np.ndarray:
    return ((col.dt.epoch("us") - int(T0.timestamp() * 1e6)) / 1e6).to_numpy().astype(np.float64)


def load_calls() -> Calls:
    cw = pl.read_parquet(SH / "call_windows.parquet", columns=[
        "turn_id", "agent", "pt_date", "goal_no", "holdout", "talk", "ctx_mode", "t_call", "t_call_lo", "t_call_hi",
        "t_end", "gap_kind", "start_conf", "first_of_day", "pause_s"])
    lt = pl.read_parquet(SH / "context_ledger_turns.parquet", columns=[
        "turn_id", "k_new", "reset_consol", "reset_forced", "reset_session"])
    assert cw["turn_id"].is_sorted() and cw["turn_id"][0] == 0 and cw["turn_id"][-1] == cw.height - 1
    cw = cw.join(lt, on="turn_id", how="left").sort("turn_id")
    days = sorted(cw["pt_date"].unique().to_list())
    dpos = {d: i for i, d in enumerate(days)}
    gk = cw["gap_kind"].cast(pl.String).to_numpy()
    forced = cw["reset_forced"].fill_null(False).to_numpy()
    gap = np.full(cw.height, GAP_CODE["other"], dtype=np.int8)
    gap[gk == "busy"] = GAP_CODE["busy"]
    gap[gk == "long_prev"] = GAP_CODE["long_prev"]
    gap[(gk == "pause") | (gk == "pause_early")] = GAP_CODE["pause"]
    gap[(gk == "after_summary") & ~forced] = GAP_CODE["after_vol"]
    gap[(gk == "after_summary") & forced] = GAP_CODE["after_forced"]
    agent = cw["agent"].to_numpy().astype(np.int16)
    day = np.array([dpos[d] for d in cw["pt_date"].to_list()], dtype=np.int32)
    t = _sec(cw["t_call"])
    # last turn id of each agent-day block (blocks are contiguous because turn_id is sorted by agent, then time)
    blk = np.r_[True, (agent[1:] != agent[:-1]) | (day[1:] != day[:-1])]
    starts = np.flatnonzero(blk)
    ends = np.r_[starts[1:] - 1, len(t) - 1]
    day_end = np.repeat(ends, np.diff(np.r_[starts, len(t)])).astype(np.int64)
    conf = cw["start_conf"].cast(pl.String).replace_strict({"low": 0, "medium": 1, "high": 2}, default=0).to_numpy()
    return Calls(
        agent=agent, day=day, goal=cw["goal_no"].to_numpy(), t=t, lo=_sec(cw["t_call_lo"]), hi=_sec(cw["t_call_hi"]),
        t_end=_sec(cw["t_end"]), summary=(cw["ctx_mode"].cast(pl.String) == "summary").to_numpy(),
        talk=cw["talk"].to_numpy(), gap=gap, chat=(cw["ctx_mode"].cast(pl.String) == "chat").to_numpy(),
        k_new=cw["k_new"].fill_null(0).to_numpy().astype(np.int32),
        reset=(cw["reset_consol"].fill_null(False) | cw["reset_forced"].fill_null(False)
               | cw["reset_session"].fill_null(False)).to_numpy(),
        holdout=cw["holdout"].to_numpy(), first_of_day=cw["first_of_day"].to_numpy(), conf=conf.astype(np.int8),
        pause_s=cw["pause_s"].fill_null(0).to_numpy().astype(np.float32), day_end=day_end,
        key=agent.astype(np.float64) * 1e9 + t, days=days)


def call_of(calls: Calls, agent: np.ndarray, t_s: np.ndarray) -> np.ndarray:
    """turn_id of the agent's latest call with t_call <= t (within the agent's block); -1 if none."""
    k = agent.astype(np.float64) * 1e9 + t_s
    i = np.searchsorted(calls.key, k, side="right") - 1
    ok = (i >= 0) & (calls.agent[np.clip(i, 0, None)] == agent)
    return np.where(ok, i, -1)


# ----------------------------------------------------------------------------- units, rosters, cadence

def unit_map() -> pl.DataFrame:
    """period_units exploded to days (holdout units included; callers filter)."""
    pu = pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "goal_no", "days", "holdout"])
    return pu.explode("days").rename({"days": "pt_date"}).select("unit_id", "goal_no", "pt_date", "holdout")


def roster() -> pl.DataFrame:
    return pl.read_parquet(SH / "roster.parquet", columns=["agent", "name", "lab", "model_string", "claude_code"])


def cadence_table(calls: Calls, goal: int, units: pl.DataFrame, allow_holdout: bool = False) -> pl.DataFrame:
    """Per agent x unit: calls, presence hours (first call start to last call end, per day), call rate, talk calls,
    median start-to-start interval, share of presence spent in timer pauses."""
    sel = np.flatnonzero((calls.goal == goal) & (allow_holdout | ~calls.holdout))
    if not len(sel):
        return pl.DataFrame()
    df = pl.DataFrame({"tid": sel, "agent": calls.agent[sel], "day": calls.day[sel], "t": calls.t[sel],
                       "t_end": calls.t_end[sel], "talk": calls.talk[sel], "summary": calls.summary[sel],
                       "gap": calls.gap[sel], "chat": calls.chat[sel]})
    df = df.with_columns(pl.Series("pt_date", [calls.days[d] for d in calls.day[sel]]))
    df = df.join(units.filter(pl.col("goal_no") == goal).select("unit_id", "pt_date"), on="pt_date", how="left")
    df = df.sort("tid").with_columns(pl.col("t").diff().over(["agent", "day"]).alias("dt"))
    d = (df.group_by(["agent", "unit_id", "day"])
         .agg(pl.len().alias("calls"), ((pl.col("t_end").max() - pl.col("t").min()) / 3600).alias("hours"),
              pl.col("talk").sum().alias("talk_calls"), pl.col("chat").sum().alias("chat_calls"),
              pl.col("dt").filter(pl.col("gap") == GAP_CODE["pause"]).sum().alias("pause_s"),
              pl.col("dt").filter(pl.col("gap") == GAP_CODE["busy"]).median().alias("med_busy_dt"),
              pl.col("dt").median().alias("med_dt"), pl.col("dt").mean().alias("mean_dt"),
              (pl.col("dt") ** 2).mean().alias("ms_dt")))
    a = (d.group_by(["agent", "unit_id"])
         .agg(pl.col("calls").sum(), pl.col("hours").sum(), pl.col("talk_calls").sum(), pl.col("chat_calls").sum(),
              pl.col("pause_s").sum(), pl.col("med_busy_dt").median(), pl.col("med_dt").median(),
              (pl.col("ms_dt") * pl.col("calls")).sum().alias("ms_w"), (pl.col("mean_dt") * pl.col("calls")).sum().alias("m_w"),
              pl.len().alias("n_days"))
         .with_columns((pl.col("calls") / pl.col("hours")).alias("rate"),
                       (pl.col("talk_calls") / pl.col("hours")).alias("talk_rate"),
                       (pl.col("pause_s") / 3600 / pl.col("hours")).alias("pause_share"),
                       # renewal mean residual wait E[d^2] / (2 E[d]) (inspection paradox), seconds
                       ((pl.col("ms_w") / pl.col("m_w")) / 2).alias("resid_wait_s"))
         .drop("ms_w", "m_w")
         .with_columns(pl.lit(goal).cast(pl.Int8).alias("goal_no")))
    return a.join(roster(), on="agent", how="left").sort(["unit_id", "agent"])


# ----------------------------------------------------------------------------- items and replies

def _call_tid_of_messages(calls: Calls) -> pl.DataFrame:
    """Every agent chat message B -> the call that produced it (b_meta_ledger t_call, exact; else latest call of the
    author starting before t_B). Columns: message_id, author, b_tid."""
    bm = pl.read_parquet(SH / "reply_threading/b_meta_ledger.parquet", columns=["b", "s_us", "s_fallback"])
    mi = pl.read_parquet(SH / "reply_threading/msg_index.parquet")          # msg (row at DQ2 build) -> message_id
    bm = bm.join(mi, left_on="b", right_on="msg", how="left").filter(~pl.col("s_fallback")).select("message_id", "s_us")
    ch = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "speaker_kind", "agent"])
    ch = ch.filter(pl.col("speaker_kind").cast(pl.String) == "agent")
    df = ch.join(bm, on="message_id", how="left")
    a = df["agent"].to_numpy().astype(np.int16)
    has = ~df["s_us"].is_null().to_numpy()
    s_sec = np.where(has, (df["s_us"].fill_null(0).to_numpy().astype(np.float64) - T0.timestamp() * 1e6) / 1e6, np.nan)
    tid = np.full(len(a), -1, dtype=np.int64)
    # exact: the call of this author whose t_call equals s (tolerance 1 ms)
    cand = call_of(calls, a, np.where(has, s_sec + 1e-3, 0.0))
    okc = has & (cand >= 0)
    exact = np.zeros(len(a), dtype=bool)
    exact[okc] = np.abs(calls.t[cand[okc]] - s_sec[okc]) < 2e-3
    tid[exact] = cand[exact]
    # fallback: the latest call of the author starting before t_B
    tb = _sec(df["t"])
    fb = call_of(calls, a, tb - 1e-3)
    tid[~exact] = fb[~exact]
    return pl.DataFrame({"message_id": df["message_id"], "author": a, "b_tid": tid, "b_exact": exact})


def build_items(calls: Calls, goal: int, units: pl.DataFrame, btid: pl.DataFrame | None = None,
                allow_holdout: bool = False) -> pl.DataFrame:
    """Item rows of one goal period (non-holdout): agent messages read out by agent recipients, with the read-out call,
    timing, batch info and three outcome calls (DQ2 parent, any labelled p_reply >= 0.5, addressing)."""
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind").cast(pl.String) == "agent")
    it = it.select("turn_id", "message_id", "sender", "age_s", "ment", "rank", "uncertain", "omitted").collect()
    tids = it["turn_id"].to_numpy()
    sel = ((calls.goal[tids] == goal) & (allow_holdout | ~calls.holdout[tids]) & ~calls.first_of_day[tids]
           & ~it["omitted"].to_numpy())
    it = it.filter(pl.Series(sel))
    tids = it["turn_id"].to_numpy()
    recv = calls.agent[tids]
    t_m = calls.t[tids] - it["age_s"].to_numpy().astype(np.float64)
    pt = [calls.days[d] for d in calls.day[tids]]
    df = pl.DataFrame({"c1": tids.astype(np.int64), "message_id": it["message_id"], "sender": it["sender"].to_numpy(),
                       "recv": recv, "t_m": t_m, "W": it["age_s"].to_numpy().astype(np.float64),
                       "rank": it["rank"].to_numpy(), "ment": it["ment"].to_numpy(),
                       "uncertain": it["uncertain"].to_numpy(), "k1": calls.k_new[tids], "pt_date": pt,
                       "day": calls.day[tids]})
    df = df.join(units.filter(pl.col("goal_no") == goal).select("unit_id", "pt_date"), on="pt_date", how="left")
    if btid is None:
        btid = _call_tid_of_messages(calls)
    rp = pl.scan_parquet(SH / "reply_pairs.parquet").filter(
        (pl.col("pair_set").cast(pl.String) == "cand") & (pl.col("a_kind") == 0) & (pl.col("goal_no") == goal)
        & (pl.lit(allow_holdout) | ~pl.col("holdout"))).select("A_message_id", "B_message_id", "b_agent", "parent", "labelled", "p_reply").collect()
    rp = rp.join(btid.select(pl.col("message_id").alias("B_message_id"), "b_tid"), on="B_message_id", how="left")
    par = (rp.filter(pl.col("parent")).group_by(["A_message_id", "b_agent"]).agg(pl.col("b_tid").min().alias("r_tid")))
    anyp = (rp.filter(pl.col("labelled") & (pl.col("p_reply") >= 0.5)).group_by(["A_message_id", "b_agent"])
            .agg(pl.col("b_tid").min().alias("any_tid")))
    soft = (rp.filter(pl.col("labelled")).group_by(["A_message_id", "b_agent"])
            .agg(pl.col("p_reply").max().alias("p_max")))
    key = {"message_id": "A_message_id", "recv": "b_agent"}
    df = (df.join(par.rename({v: k for k, v in key.items()}), on=["message_id", "recv"], how="left")
          .join(anyp.rename({v: k for k, v in key.items()}), on=["message_id", "recv"], how="left")
          .join(soft.rename({v: k for k, v in key.items()}), on=["message_id", "recv"], how="left"))
    # addressing: the recipient's first talk call at or after c1 whose message names the sender
    cm = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    ad = (btid.join(cm, on="message_id", how="inner").explode("mentions_roster")
          .filter(pl.col("mentions_roster").is_not_null() & (pl.col("b_tid") >= 0))
          .select(pl.col("author").cast(pl.Int16).alias("recv"), pl.col("mentions_roster").cast(pl.Int16).alias("sender"),
                  pl.col("b_tid").alias("addr_tid"))
          .unique().sort("addr_tid"))
    df = df.with_columns(pl.col("recv").cast(pl.Int16), pl.col("sender").cast(pl.Int16)).sort("c1")
    df = df.join_asof(ad, left_on="c1", right_on="addr_tid", by=["recv", "sender"], strategy="forward")
    for c in ("r_tid", "any_tid", "addr_tid"):
        df = df.with_columns(pl.col(c).fill_null(-1).cast(pl.Int64))
    # a reply mapped before the read-out call cannot be a response under the visibility rule: drop it (rare)
    for c in ("r_tid", "any_tid"):
        df = df.with_columns(pl.when(pl.col(c) < pl.col("c1")).then(-1).otherwise(pl.col(c)).alias(c))
    df = df.with_columns(pl.lit(goal).cast(pl.Int8).alias("goal_no")).with_row_index("item")
    return df


# ----------------------------------------------------------------------------- risk sets

@dataclass
class Rows:
    item: np.ndarray       # index into the item arrays
    tid: np.ndarray        # call turn_id
    n: np.ndarray          # 1 = read-out call
    a: np.ndarray          # wall age of m at the call (s)
    e: np.ndarray          # wall time the call spans (W at n = 1) (s)
    b: np.ndarray          # newer messages since m (burial)
    k: np.ndarray          # new items at the call
    gap: np.ndarray
    chat: np.ndarray
    reset: np.ndarray      # a context reset happened after the read-out call
    prev_talk: np.ndarray


def with_times(calls: Calls, t_new: np.ndarray) -> Calls:
    """Shallow copy with new call times (made monotone within each agent block) and the matching search key."""
    t2 = t_new.copy()
    blk = np.r_[True, calls.agent[1:] != calls.agent[:-1]]
    gid = np.cumsum(blk) - 1
    # enforce t2[c] >= t2[c-1] + 1 ms inside agent blocks
    adj = t2 - np.arange(len(t2)) * 1e-3
    starts = np.flatnonzero(blk)
    for s0, s1 in zip(starts, np.r_[starts[1:], len(t2)]):
        adj[s0:s1] = np.maximum.accumulate(adj[s0:s1])
    t2 = adj + np.arange(len(t2)) * 1e-3
    del gid
    c = Calls(**{f: getattr(calls, f) for f in calls.__dataclass_fields__})
    c.t = t2
    c.key = calls.agent.astype(np.float64) * 1e9 + t2
    return c


def jitter_times(calls: Calls, rng: np.random.Generator) -> np.ndarray:
    """Call starts redrawn uniformly within each call's [t_call_lo, t_call_hi] bounds."""
    lo = np.minimum(calls.lo, calls.t)
    hi = np.maximum(calls.hi, calls.t)
    return lo + (hi - lo) * rng.random(len(lo))


def readout_call(calls: Calls, recv: np.ndarray, t_m: np.ndarray) -> np.ndarray:
    """First call of the recipient assembled after t_m (the ledger rule): turn_id, or -1 if none that day."""
    i = np.searchsorted(calls.key, recv.astype(np.float64) * 1e9 + t_m, side="right")
    i = np.clip(i, 0, calls.n - 1)
    ok = (calls.agent[i] == recv) & (calls.t[i] > t_m)
    # skip summary calls (they receive nothing): move to the next non-summary call of the same block
    for _ in range(4):
        s = ok & calls.summary[i] & (i + 1 < calls.n)
        i = np.where(s, i + 1, i)
        ok = ok & (calls.agent[i] == recv)
    return np.where(ok & ~calls.summary[i], i, -1)


def expand(calls: Calls, c1: np.ndarray, t_m: np.ndarray, rank: np.ndarray, horizon: float = H_FIT_S) -> Rows:
    """Risk-set rows (untruncated by any outcome): for each item, the recipient's non-summary calls from c1 while the
    wall age is <= horizon, on the same PT day."""
    tt = calls.t
    c1 = np.asarray(c1, dtype=np.int64)
    agent = calls.agent[c1]
    end = np.searchsorted(calls.key, agent.astype(np.float64) * 1e9 + t_m + horizon, side="right") - 1
    end = np.minimum(end, calls.day_end[c1])
    end = np.maximum(end, c1)
    L = end - c1 + 1
    off = np.repeat(np.cumsum(L) - L, L)
    idx = np.repeat(c1, L) + (np.arange(L.sum()) - off)
    item = np.repeat(np.arange(len(c1)), L)
    keep = ~calls.summary[idx]
    keep[np.r_[0, np.cumsum(L)[:-1]]] = True          # the read-out call is never a summary call
    idx, item = idx[keep], item[keep]
    first = np.r_[True, item[1:] != item[:-1]]
    grp_start = np.maximum.accumulate(np.where(first, np.arange(len(item)), 0))
    n = (np.arange(len(item)) - grp_start + 1).astype(np.int32)
    a = tt[idx] - t_m[item]
    prev_t = np.r_[0.0, tt[idx][:-1]]
    e = np.where(first, a, tt[idx] - prev_t)
    kk = calls.k_new[idx]
    knew_after = np.where(first, 0, kk).astype(np.int64)
    csum = np.cumsum(knew_after)
    base = csum[grp_start] - knew_after[grp_start]
    b = (rank[item].astype(np.int64) - 1) + (csum - base)
    rs = np.where(first, 0, calls.reset[idx]).astype(np.int64)
    rcs = np.cumsum(rs)
    reset = (rcs - (rcs[grp_start] - rs[grp_start])) > 0
    pt = np.where(idx > 0, calls.talk[np.maximum(idx - 1, 0)], False) & ~calls.summary[np.maximum(idx - 1, 0)]
    return Rows(item=item.astype(np.int64), tid=idx.astype(np.int64), n=n, a=a.astype(np.float64),
                e=np.maximum(e, 0.05).astype(np.float64), b=b.astype(np.int64), k=kk.astype(np.int32),
                gap=calls.gap[idx], chat=calls.chat[idx], reset=reset, prev_talk=pt)


def truncate(rows: Rows, reply_tid: np.ndarray) -> tuple[Rows, np.ndarray]:
    """Drop rows after each item's reply call; return (rows, y)."""
    r = reply_tid[rows.item]
    keep = (r < 0) | (rows.tid <= r)
    y = (rows.tid == r) & (r >= 0)
    sub = Rows(**{f: getattr(rows, f)[keep] for f in rows.__dataclass_fields__})
    return sub, y[keep]


# ----------------------------------------------------------------------------- cells

N_EDGES = np.array([1.5, 2.5, 4.5, 8.5, 16.5, 32.5])
A_EDGES = np.array([8, 16, 32, 64, 128, 256, 512, 1024], dtype=float)
E_EDGES = np.array([2, 4, 8, 16, 32, 64, 128, 256, 512], dtype=float)
K_EDGES = np.array([0.5, 1.5, 3.5, 7.5, 15.5])
B_EDGES = np.array([0.5, 1.5, 3.5, 7.5, 15.5, 31.5])
R_EDGES = np.array([1.5, 2.5, 4.5, 8.5])
SUM_COLS = ["N", "y", "s_logn", "s_loga", "s_loge", "s_logk", "s_logb", "s_logr"]
KEY_COLS = ["day", "au", "nb", "ab", "eb", "kb", "bb", "rb", "gap", "chat", "ment", "reset", "pt"]


def aggregate(rows: Rows, y: np.ndarray, item_day: np.ndarray, item_au: np.ndarray, item_ment: np.ndarray,
              item_rank: np.ndarray, w: np.ndarray | None = None) -> pl.DataFrame:
    """Cells keyed by day x agent-unit x covariate bins, with sums of each log covariate."""
    it = rows.item
    nb = np.searchsorted(N_EDGES, rows.n)
    ab = np.searchsorted(A_EDGES, rows.a)
    eb = np.searchsorted(E_EDGES, rows.e)
    kb = np.searchsorted(K_EDGES, rows.k)
    bb = np.searchsorted(B_EDGES, rows.b)
    first = rows.n == 1
    rk = item_rank[it]
    rb = np.where(first, np.searchsorted(R_EDGES, rk), 0)
    key = (item_day[it].astype(np.int64))
    for v, width in ((item_au[it], 10), (nb, 3), (ab, 4), (eb, 4), (kb, 3), (bb, 3), (rb, 3), (rows.gap, 5),
                     (rows.chat, 1), (item_ment[it], 1), (rows.reset, 1), (rows.prev_talk, 1)):
        key = (key << width) | np.asarray(v, dtype=np.int64)
    uk, inv = np.unique(key, return_inverse=True)
    ww = np.ones(len(inv)) if w is None else w
    sums = {
        "N": np.bincount(inv, weights=ww),
        "y": np.bincount(inv, weights=ww * y),
        "s_logn": np.bincount(inv, weights=ww * np.log(rows.n)),
        "s_loga": np.bincount(inv, weights=ww * np.log(np.maximum(rows.a, 1.0) / 60.0)),
        "s_loge": np.bincount(inv, weights=ww * np.log(rows.e / 10.0)),
        "s_logk": np.bincount(inv, weights=ww * np.log1p(rows.k)),
        "s_logb": np.bincount(inv, weights=ww * np.log1p(rows.b)),
        "s_logr": np.bincount(inv, weights=ww * np.where(first, np.log(rk), 0.0)),
    }
    # decode keys
    dec = {}
    k = uk.copy()
    for name, width in (("pt", 1), ("reset", 1), ("ment", 1), ("chat", 1), ("gap", 5), ("rb", 3), ("bb", 3),
                        ("kb", 3), ("eb", 4), ("ab", 4), ("nb", 3), ("au", 10)):
        dec[name] = (k & ((1 << width) - 1)).astype(np.int16)
        k = k >> width
    dec["day"] = k.astype(np.int32)
    out = {c: dec[c] for c in KEY_COLS}
    out.update(sums)
    return pl.DataFrame(out)


def merge_cells(parts: list[pl.DataFrame]) -> pl.DataFrame:
    df = pl.concat(parts)
    return df.group_by(KEY_COLS).agg([pl.col(c).sum() for c in SUM_COLS]).sort(KEY_COLS)


# ----------------------------------------------------------------------------- design and fit

SPEC_FULL = "full"        # eta, eta1, phi, psi, chi free (gap, mode main effects)
SPEC_GAP = "gap"          # + log e x gap and x chat interactions (gap-specific eta)
SPEC_CALL = "call"        # call clock: no wall-time terms (eta = eta1 = psi = 0)
SPEC_WALL = "wall"        # wall clock: log e offset (eta = eta1 = 1), psi decay, no phi


def design(cells: pl.DataFrame, spec: str = SPEC_FULL, n_au: int | None = None):
    """Sparse design [agent-unit FE | mechanism columns], offset, names. Mechanism covariates are cell means."""
    N = cells["N"].to_numpy()
    m = {c: cells[c].to_numpy() / np.maximum(N, 1e-12) for c in SUM_COLS[2:]}
    nb = cells["nb"].to_numpy()
    first = (nb == 0).astype(float)
    later = 1.0 - first
    gap = cells["gap"].to_numpy()
    chat = cells["chat"].to_numpy().astype(float)
    ment = cells["ment"].to_numpy().astype(float)
    cols, names = [], []

    def add(v, nm):
        cols.append(np.asarray(v, dtype=float))
        names.append(nm)

    add(first, "n1")
    add(first * m["s_logr"], "n1_logrank")
    add(first * ment, "n1_ment")
    add(later * ment, "ment")
    add(m["s_logk"], "logk")
    add(cells["pt"].to_numpy().astype(float), "prev_talk")
    add(later * cells["reset"].to_numpy(), "reset_since")
    if chat.any():
        add(chat, "chat")
    for g in range(1, len(GAPS)):
        if (gap == g).any():
            add(later * (gap == g), f"gap_{GAPS[g]}")
            if (first * (gap == g)).sum() > 0:
                add(first * (gap == g), f"n1_gap_{GAPS[g]}")
    offset = np.zeros(len(N))
    if spec in (SPEC_FULL, SPEC_GAP):
        add(first * m["s_loga"], "eta1")          # log(W/60) at the read-out call
        add(later * m["s_logn"], "phi")
        add(later * m["s_loga"], "psi")
        add(later * m["s_logb"], "chi")
        add(later * m["s_loge"], "eta")
        if spec == SPEC_GAP:
            for g in range(1, len(GAPS)):
                if (later * (gap == g)).sum() > 0:
                    add(later * (gap == g) * m["s_loge"], f"eta_x_{GAPS[g]}")
                if (first * (gap == g)).sum() > 0:
                    add(first * (gap == g) * m["s_loga"], f"eta1_x_{GAPS[g]}")
            if chat.any():
                add(later * chat * m["s_loge"], "eta_x_chat")
                add(first * chat * m["s_loga"], "eta1_x_chat")
    elif spec == SPEC_CALL:
        add(later * m["s_logn"], "phi")
        add(later * m["s_logb"], "chi")
    elif spec == SPEC_WALL:
        add(later * m["s_loga"], "psi")
        add(later * m["s_logb"], "chi")
        offset = later * m["s_loge"] + first * m["s_loga"]
    else:
        raise ValueError(spec)
    au = cells["au"].to_numpy().astype(np.int64)
    G = int(au.max()) + 1 if n_au is None else n_au
    FE = sp.csr_matrix((np.ones(len(au)), (np.arange(len(au)), au)), shape=(len(au), G))
    Xm = np.column_stack(cols) if cols else np.zeros((len(N), 0))
    return FE, Xm, offset, names


@dataclass
class Fit:
    beta: np.ndarray          # mechanism coefficients
    fe: np.ndarray            # agent-unit intercepts
    names: list
    cov: np.ndarray           # model-based covariance of the mechanism coefficients
    fe_se: np.ndarray
    ll: float
    converged: bool
    n_iter: int

    def get(self, nm, default=np.nan):
        return float(self.beta[self.names.index(nm)]) if nm in self.names else default

    def se(self, nm):
        return float(np.sqrt(self.cov[self.names.index(nm), self.names.index(nm)])) if nm in self.names else np.nan


def _cloglog_mu(eta):
    eta = np.clip(eta, -30, 5)
    ee = np.exp(eta)
    mu = -np.expm1(-ee)
    dmu = ee * np.exp(-ee)
    return np.clip(mu, 1e-12, 1 - 1e-12), np.maximum(dmu, 1e-300)


def fit(FE, Xm, offset, y, N, w=None, start=None, ridge_fe=1e-3, maxit=60, tol=1e-7) -> Fit:
    """Binomial cloglog IRLS (Fisher scoring) on cells with agent-unit FE. Proportions y/N, prior weights N*w."""
    yy = y if w is None else y * w
    NN = N if w is None else N * w
    pos = NN > 0
    G, P = FE.shape[1], Xm.shape[1]
    FEc = FE.tocsr()
    assert np.all(np.diff(FEc.indptr) == 1), "FE must be one-hot (one group per row)"
    g_idx = FEc.indices.astype(np.int64)
    Xm = np.ascontiguousarray(Xm, dtype=np.float64)

    class _X:   # blockwise [one-hot FE | dense Xm] operator
        def __matmul__(self, b):
            return b[:G][g_idx] + Xm @ b[G:]
    X = _X()

    def normal_eq(W, z):
        A = np.zeros((G + P, G + P))
        A[np.arange(G), np.arange(G)] = np.bincount(g_idx, weights=W, minlength=G)
        WX = Xm * W[:, None]
        for j in range(P):
            A[:G, G + j] = np.bincount(g_idx, weights=WX[:, j], minlength=G)
        A[G:, :G] = A[:G, G:].T
        A[G:, G:] = Xm.T @ WX
        bv = np.concatenate([np.bincount(g_idx, weights=W * z, minlength=G), WX.T @ z])
        return A, bv
    if start is None:
        p0 = max(yy.sum() / max(NN.sum(), 1e-12), 1e-6)
        beta = np.zeros(G + P)
        beta[:G] = np.log(-np.log1p(-p0))
    else:
        beta = start.copy()
    # groups with no successes are separated: the ridge keeps their FE finite (and far negative)
    R = np.full(G + P, 1e-6)
    R[:G] = ridge_fe
    p = np.where(pos, yy / np.where(pos, NN, 1), 0)

    def pen_ll(b):
        mu_c, _ = _cloglog_mu(X @ b + offset)
        return float(np.sum(yy * np.log(mu_c) + (NN - yy) * np.log1p(-mu_c)) - 0.5 * np.sum(R * b ** 2))

    conv = False
    ll_old = pen_ll(beta)
    for it in range(maxit):
        eta = X @ beta + offset
        mu, dmu = _cloglog_mu(eta)
        W = NN * dmu ** 2 / (mu * (1 - mu))
        z = (eta - offset) + (p - mu) / dmu
        A, bvec = normal_eq(W, z)
        A += np.diag(R)
        try:
            new = np.linalg.solve(A, bvec)
        except np.linalg.LinAlgError:
            new = np.linalg.lstsq(A, bvec, rcond=None)[0]
        step = new - beta
        # cap absurd steps, then halve until the penalized log-likelihood does not decrease
        mx = np.max(np.abs(step))
        if mx > 5:
            step *= 5 / mx
        improved = False
        for _ in range(30):
            cand = beta + step
            ll = pen_ll(cand)
            if np.isfinite(ll) and ll >= ll_old - 1e-10 * (1 + abs(ll_old)):
                improved = True
                break
            step *= 0.5
        if not improved:
            conv = True
            break
        beta = cand
        if abs(ll - ll_old) < tol * (1 + abs(ll)) and np.max(np.abs(step)) < 1e-4:
            conv = True
            ll_old = ll
            break
        ll_old = ll
    eta = X @ beta + offset
    mu, dmu = _cloglog_mu(eta)
    W = NN * dmu ** 2 / (mu * (1 - mu))
    A, _ = normal_eq(W, np.zeros(len(W)))
    A += np.diag(R)
    try:
        cov_full = np.linalg.inv(A)
    except np.linalg.LinAlgError:
        cov_full = np.linalg.pinv(A)
    return Fit(beta=beta[G:], fe=beta[:G], names=[], cov=cov_full[G:, G:], fe_se=np.sqrt(np.clip(np.diag(cov_full)[:G], 0, None)),
               ll=ll_old, converged=conv, n_iter=it + 1), beta


def fit_cells(cells: pl.DataFrame, spec: str = SPEC_FULL, w: np.ndarray | None = None, start=None, n_au=None):
    FE, Xm, off, names = design(cells, spec, n_au=n_au)
    f, full = fit(FE, Xm, off, cells["y"].to_numpy(), cells["N"].to_numpy(), w=w, start=start)
    f.names = names
    return f, full


def loglik(cells: pl.DataFrame, spec: str, f: Fit, n_au: int) -> float:
    FE, Xm, off, names = design(cells, spec, n_au=n_au)
    b = np.zeros(len(names))
    for i, nm in enumerate(names):
        if nm in f.names:
            b[i] = f.beta[f.names.index(nm)]
    fe = np.zeros(n_au)
    fe[:len(f.fe)] = f.fe
    eta = FE @ fe + Xm @ b + off
    mu, _ = _cloglog_mu(eta)
    y, N = cells["y"].to_numpy(), cells["N"].to_numpy()
    return float(np.sum(y * np.log(mu) + (N - y) * np.log1p(-mu)))


def day_bootstrap(cells: pl.DataFrame, spec: str, B: int, seed: int, start=None, n_au=None, names_keep=None):
    """Refit on day-reweighted cells (multinomial weights over days). Returns (coef draws [B x P], fe draws, names)."""
    FE, Xm, off, names = design(cells, spec, n_au=n_au)
    y, N = cells["y"].to_numpy(), cells["N"].to_numpy()
    days = cells["day"].to_numpy()
    ud, dinv = np.unique(days, return_inverse=True)
    rng = np.random.default_rng(seed)
    draws, fes = [], []
    for _ in range(B):
        wd = rng.multinomial(len(ud), np.ones(len(ud)) / len(ud)).astype(float)
        f, full = fit(FE, Xm, off, y, N, w=wd[dinv], start=start, maxit=30)
        draws.append(f.beta)
        fes.append(np.where(np.bincount(cells["au"].to_numpy(), weights=wd[dinv] * N, minlength=FE.shape[1]) > 0,
                            f.fe, np.nan))
    return np.array(draws), np.array(fes), names


# ----------------------------------------------------------------------------- row-level linear predictor

def rows_linpred(rows: Rows, item_ment: np.ndarray, item_rank: np.ndarray, coef: dict, fe: np.ndarray,
                 item_au: np.ndarray, scale: float = 1.0) -> np.ndarray:
    """Linear predictor at the row level for a coefficient dict (names as in design()). `scale` compresses every
    call interval by that factor (cadence counterfactual): ages, spans, batches and burial counts scale with it."""
    first = rows.n == 1
    later = ~first
    it = rows.item
    c = lambda nm: coef.get(nm, 0.0)  # noqa: E731
    a = np.maximum(rows.a * scale, 1.0)
    e = np.maximum(rows.e * scale, 0.05)
    k = rows.k * scale
    b = rows.b * scale
    rk = 1 + (item_rank[it] - 1) * scale
    ment = item_ment[it].astype(float)
    eta = fe[item_au[it]].copy()
    eta += first * (c("n1") + c("n1_logrank") * np.log(rk) + c("n1_ment") * ment + c("eta1") * np.log(a / 60))
    eta += later * (c("ment") * ment + c("phi") * np.log(rows.n) + c("psi") * np.log(a / 60)
                    + c("chi") * np.log1p(b) + c("eta") * np.log(e / 10) + c("reset_since") * rows.reset)
    eta += c("logk") * np.log1p(k) + c("prev_talk") * rows.prev_talk
    if "chat" in coef:
        eta += c("chat") * rows.chat
    for g in range(1, len(GAPS)):
        gm = rows.gap == g
        eta += later * gm * (c(f"gap_{GAPS[g]}") + c(f"eta_x_{GAPS[g]}") * np.log(e / 10))
        eta += first * gm * (c(f"n1_gap_{GAPS[g]}") + c(f"eta1_x_{GAPS[g]}") * np.log(a / 60))
    if "eta_x_chat" in coef:
        eta += later * rows.chat * c("eta_x_chat") * np.log(e / 10) + first * rows.chat * c("eta1_x_chat") * np.log(a / 60)
    return eta


def p_reply_within(rows: Rows, eta_rows: np.ndarray, T: float, n_items: int, scale: float = 1.0) -> np.ndarray:
    """Per item P(reply within wall age T) = 1 - prod over calls with scaled age <= T of (1 - h)."""
    h, _ = _cloglog_mu(eta_rows)
    inside = rows.a * scale <= T
    lg = np.where(inside, np.log1p(-h), 0.0)
    return 1 - np.exp(np.bincount(rows.item, weights=lg, minlength=n_items))


def cadence_elasticity_multi(rows: Rows, item_ment, item_rank, item_au, coef: dict, fe: np.ndarray, Ts,
                             n_items: int, d: float = 0.1) -> dict:
    """eps(T) for several horizons from one pair of linear predictors (faster than calling cadence_elasticity)."""
    s_fast, s_slow = 1 / (1 + d), 1 / (1 - d)
    ef = rows_linpred(rows, item_ment, item_rank, coef, fe, item_au, s_fast)
    es = rows_linpred(rows, item_ment, item_rank, coef, fe, item_au, s_slow)
    out = {}
    for T in Ts:
        pf = p_reply_within(rows, ef, T, n_items, s_fast)
        ps = p_reply_within(rows, es, T, n_items, s_slow)
        out[T] = float((np.log(pf.mean()) - np.log(ps.mean())) / (np.log(1 + d) - np.log(1 - d)))
    return out


def cadence_elasticity(rows: Rows, item_ment, item_rank, item_au, coef: dict, fe: np.ndarray, T: float,
                       n_items: int, d: float = 0.1) -> float:
    """eps(T) = d log P(reply within T) / d log(speed-up), averaged over items (ratio of means).
    Speed-up c means intervals multiplied by 1/c; difference at c = 1 +- d."""
    s_fast, s_slow = 1 / (1 + d), 1 / (1 - d)
    pf = p_reply_within(rows, rows_linpred(rows, item_ment, item_rank, coef, fe, item_au, s_fast), T, n_items, s_fast)
    ps = p_reply_within(rows, rows_linpred(rows, item_ment, item_rank, coef, fe, item_au, s_slow), T, n_items, s_slow)
    return float((np.log(pf.mean()) - np.log(ps.mean())) / (np.log(1 + d) - np.log(1 - d)))


# ----------------------------------------------------------------------------- misc

def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "hypotheses/H40-call-clock-coupling"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def write_provenance(entry: str, built_by: str, tables: list[str], params: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov[entry] = {"built_by": built_by, "git_commit": git_commit(),
                   "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                   "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1))


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        raise TypeError(type(o))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=conv))


def re_mean(est: np.ndarray, se: np.ndarray) -> dict:
    """DerSimonian-Laird random-effects mean."""
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return dict(mean=np.nan, lo=np.nan, hi=np.nan, tau=np.nan, k=0)
    w = 1 / se ** 2
    m_fe = (w * est).sum() / w.sum()
    Q = (w * (est - m_fe) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    m = (ws * est).sum() / ws.sum()
    s = np.sqrt(1 / ws.sum())
    return dict(mean=float(m), lo=float(m - 1.96 * s), hi=float(m + 1.96 * s), tau=float(np.sqrt(tau2)), k=int(len(est)),
                Q=float(Q))
