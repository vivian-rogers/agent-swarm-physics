"""H41 core: period skeletons from the DQ1 context ledger, the logged light cone, static hops, hazards.

Used by scheme/build.py (real data) and analysis/synthetic.py (planted truths on real skeletons).
No text is read here. Times are float seconds since the Unix epoch (UTC).

Definitions: see ../README.md, "Operational definitions" (written 2026-10-04 before any real-data run).
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H41-readout-light-cone"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

INF = np.inf
AUTOMATED_NODE = 99
HUMAN_BASE = 100
ROOMS_START = 1772006400.0  # 2026-02-25 08:00 UTC: before this everyone sits in #general (room 0)
# Room index: "fixed" (round 1b, default) keeps open rooms_timeline segments; "old" reproduces round 1 (open segments
# dropped). Set with the environment variable H41_ROOMS=old.
ROOMS_MODE = os.environ.get("H41_ROOMS", "fixed")
if ROOMS_MODE not in ("fixed", "old"):
    raise ValueError(f"H41_ROOMS must be 'fixed' or 'old', got {ROOMS_MODE!r}")


def ts(col: str) -> pl.Expr:
    """Datetime column -> float epoch seconds."""
    return pl.col(col).dt.epoch("us").cast(pl.Float64) / 1e6


def cc_agents() -> list[int]:
    ros = pl.read_parquet(SH / "roster.parquet")
    return ros.filter(pl.col("claude_code"))["agent"].to_list()


def calendar() -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet").sort("pt_date")
    hm = np.array(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    return cal.with_columns(pl.Series("hold", hm | cal["holdout"].fill_null(False).to_numpy()),
                            ts("win_start").alias("ws"), ts("win_end").alias("we"))


def active_time(t: np.ndarray, days: np.ndarray, cal: pl.DataFrame) -> np.ndarray:
    """Active-time coordinate (s): cumulative calendar windows, clipped inside each day's window."""
    d = dict(zip(cal["pt_date"].to_list(), range(cal.height)))
    off = cal["active_offset_s"].to_numpy().astype(float)
    ws = cal["ws"].to_numpy()
    wl = cal["window_s"].to_numpy().astype(float)
    ix = np.array([d.get(x, -1) for x in days], dtype=np.int64)
    ok = ix >= 0
    out = np.full(len(t), np.nan)
    out[ok] = off[ix[ok]] + np.clip(t[ok] - ws[ix[ok]], 0, wl[ix[ok]])
    return out


@dataclass
class Skeleton:
    goal: int
    days: list
    agents: np.ndarray                 # roster agent codes with receiving calls (Claude Code excluded)
    # calls (receiving; ctx_mode != summary), sorted by agent then t_call
    c_agent: np.ndarray
    c_ci: np.ndarray                   # per-agent call index
    c_t: np.ndarray
    c_lo: np.ndarray
    c_hi: np.ndarray
    c_first: np.ndarray
    c_talk: np.ndarray
    c_kind: np.ndarray
    c_day: np.ndarray
    c_turn: np.ndarray
    agent_calls: dict = field(default_factory=dict)   # agent -> slice into call arrays
    # read events (ledger items), sorted by reader call time
    e_reader: np.ndarray = None
    e_ci: np.ndarray = None
    e_t: np.ndarray = None             # reader call t_call
    e_sender: np.ndarray = None        # node id
    e_tm: np.ndarray = None            # message time
    e_msg: np.ndarray = None           # row in msgs
    e_unc: np.ndarray = None
    e_ci_len: np.ndarray = None        # lenient reading call index
    e_t_len: np.ndarray = None         # lenient entry time (t_call_lo of the lenient call)
    e_at: np.ndarray = None            # active time of the reading call
    len_order: np.ndarray = None       # argsort of e_t_len
    # messages of the period (non-holdout days)
    msgs: pl.DataFrame = None          # message_id, t, room, kind, agent, node, mrow, ci_talk (producing call), day
    readers_of: dict = field(default_factory=dict)  # mrow -> (reader array, ci array)
    rooms: pl.DataFrame = None         # rooms_timeline rows overlapping the period
    cal: pl.DataFrame = None
    t_min: float = 0.0
    t_max: float = 0.0


def load_skeleton(goal: int, cal: pl.DataFrame | None = None, days_filter=None, include_holdout: bool = False) -> Skeleton:
    """Receiving calls, read events and messages of one goal period, holdout days removed.

    include_holdout=True is used only by analysis/confirm.py behind its guard flags.
    """
    cal = calendar() if cal is None else cal
    if include_holdout:
        days = cal.filter(pl.col("goal_no") == goal)["pt_date"].to_list()
    else:
        days = cal.filter((pl.col("goal_no") == goal) & ~pl.col("hold"))["pt_date"].to_list()
    if days_filter is not None:
        days = [d for d in days if days_filter(d)]
    cc = cc_agents()
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & (pl.lit(include_holdout) | ~pl.col("holdout"))
                  & (pl.col("ctx_mode") != "summary") & ~pl.col("agent").is_in(cc))
          .select("turn_id", "agent", "pt_date", "kind", "talk", ts("t_call").alias("t"), ts("t_call_lo").alias("lo"),
                  ts("t_call_hi").alias("hi"), ts("t_first").alias("tf"))
          .collect().sort("agent", "t", "turn_id"))
    cw = cw.with_columns(pl.int_range(pl.len()).over("agent").alias("ci"))
    sk = Skeleton(goal=goal, days=days, agents=np.unique(cw["agent"].to_numpy()),
                  c_agent=cw["agent"].to_numpy().astype(np.int32), c_ci=cw["ci"].to_numpy().astype(np.int64),
                  c_t=cw["t"].to_numpy(), c_lo=cw["lo"].to_numpy(), c_hi=cw["hi"].to_numpy(),
                  c_first=cw["tf"].to_numpy(), c_talk=cw["talk"].to_numpy(), c_kind=cw["kind"].cast(pl.Utf8).to_numpy(),
                  c_day=cw["pt_date"].to_numpy(), c_turn=cw["turn_id"].to_numpy())
    sk.cal = cal
    a = sk.c_agent
    bounds = np.flatnonzero(np.diff(a)) + 1
    starts = np.r_[0, bounds]
    ends = np.r_[bounds, len(a)]
    sk.agent_calls = {int(a[s]): slice(int(s), int(e)) for s, e in zip(starts, ends)}

    chat = (pl.scan_parquet(SH / "chat_core.parquet")
            .filter(pl.col("pt_date").is_in(days))
            .select("message_id", ts("t").alias("t"), "pt_date", "room", pl.col("speaker_kind").cast(pl.Utf8).alias("kind"),
                    "agent", "human").collect().sort("t", "message_id"))
    hum = chat.filter(pl.col("kind") == "human")["human"].unique().sort().to_list()
    hmap = {h: HUMAN_BASE + i for i, h in enumerate(hum)}
    node = np.where(chat["kind"].to_numpy() == "agent", chat["agent"].fill_null(-1).to_numpy().astype(np.int64),
                    np.where(chat["kind"].to_numpy() == "automated", AUTOMATED_NODE, -1))
    hv = chat["human"].to_list()
    for i, k in enumerate(chat["kind"].to_list()):
        if k == "human":
            node[i] = hmap[hv[i]]
    chat = chat.with_columns(pl.Series("node", node), pl.int_range(pl.len()).alias("mrow"))
    # producing talk call of each agent message: nearest talk call t_first within 2 s (same agent)
    talk = cw.filter(pl.col("talk")).select("agent", "tf", "ci").sort("agent", "tf")
    am = chat.filter(pl.col("kind") == "agent").select("mrow", "agent", "t").sort("agent", "t")
    j = am.join_asof(talk.with_columns(pl.col("tf").alias("tf_key")), left_on="t", right_on="tf_key", by="agent",
                     strategy="nearest", check_sortedness=False)
    j = j.with_columns(pl.when((pl.col("t") - pl.col("tf")).abs() <= 2.0).then(pl.col("ci")).otherwise(None).alias("ci_talk"))
    chat = chat.join(j.select("mrow", "ci_talk"), on="mrow", how="left").sort("mrow")
    sk.msgs = chat
    sk.t_min = float(cw["t"].min()) if cw.height else 0.0
    sk.t_max = float(cw["t"].max()) if cw.height else 0.0

    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .join(cw.lazy().select("turn_id", "agent", "ci", "t", "lo", "hi"), on="turn_id", how="inner")
          .filter(~pl.col("omitted"))  # beyond the 200-event cap: never shown to the agent (only #51 in non-holdout data)
          .select("turn_id", "message_id", "agent", "ci", "t", "uncertain")
          .collect())
    it = it.join(chat.select("message_id", "mrow", pl.col("t").alias("tm"), "node"), on="message_id", how="inner")
    # lenient call: previous receiving call if uncertain and t_m < t_call_hi(previous)
    calls = cw.select("agent", "ci", "lo", "hi")
    prev = calls.with_columns((pl.col("ci") + 1).alias("ci_next")).select("agent", pl.col("ci_next").alias("ci"),
                                                                          pl.col("hi").alias("hi_prev"),
                                                                          pl.col("lo").alias("lo_prev"))
    it = it.join(prev, on=["agent", "ci"], how="left").join(calls.select("agent", "ci", pl.col("lo").alias("lo_this")),
                                                             on=["agent", "ci"], how="left")
    usep = pl.col("uncertain") & pl.col("hi_prev").is_not_null() & (pl.col("tm") < pl.col("hi_prev"))
    it = it.with_columns(pl.when(usep).then(pl.col("ci") - 1).otherwise(pl.col("ci")).alias("ci_len"),
                         pl.when(usep).then(pl.col("lo_prev")).otherwise(pl.col("lo_this")).alias("t_len"))
    it = it.sort("t", "agent", "tm")
    sk.e_reader = it["agent"].to_numpy().astype(np.int64)
    sk.e_ci = it["ci"].to_numpy().astype(np.int64)
    sk.e_t = it["t"].to_numpy()
    sk.e_sender = it["node"].to_numpy().astype(np.int64)
    sk.e_tm = it["tm"].to_numpy()
    sk.e_msg = it["mrow"].to_numpy().astype(np.int64)
    sk.e_unc = it["uncertain"].to_numpy()
    sk.e_ci_len = it["ci_len"].to_numpy().astype(np.int64)
    sk.e_t_len = it["t_len"].to_numpy()
    sk.len_order = np.argsort(sk.e_t_len, kind="stable")
    eday = it.join(cw.select("turn_id", "pt_date"), on="turn_id", how="left")["pt_date"].to_numpy()
    sk.e_at = active_time(sk.e_t, eday, cal)
    # readers of each message
    o = np.argsort(sk.e_msg, kind="stable")
    m_sorted = sk.e_msg[o]
    b = np.flatnonzero(np.diff(m_sorted)) + 1
    st, en = np.r_[0, b], np.r_[b, len(m_sorted)]
    sk.readers_of = {int(m_sorted[s]): o[s:e] for s, e in zip(st, en)} if len(m_sorted) else {}
    sk.rooms = rooms_table(sk.t_min, sk.t_max)
    return sk


def rooms_table(t_min: float, t_max: float, mode: str | None = None) -> pl.DataFrame:
    """rooms_timeline rows overlapping [t_min - 1 day, t_max + 1 day].

    Bug fix (coordinator, 2026-10-04, found by re-freeze batch B; round 1b): rooms still open have no end time; the
    round-1 filter (te >= t_min - 1 day) dropped them, so RoomIndex.at returned the agent's previous room (61-70% of
    #51 lookups). Open rooms are now kept with te = +inf. H41_ROOMS=old reproduces round 1 exactly.
    """
    mode = mode or ROOMS_MODE
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").with_columns(ts("t_start").alias("ts"), ts("t_end").alias("te"))
    if mode != "old":
        rt = rt.with_columns(pl.col("te").fill_null(float("inf")))
    return rt.filter((pl.col("te") >= t_min - 86400) & (pl.col("ts") <= t_max + 86400))


# ----------------------------------------------------------------------------------------------- rooms
def room_at(sk: Skeleton, agent: int, t: float) -> int:
    """Room of an agent at time t (as-of rooms_timeline); #general before rooms existed."""
    if t < ROOMS_START:
        return 0
    r = sk.rooms.filter((pl.col("agent") == agent) & (pl.col("ts") <= t))
    if r.height == 0:
        return -1
    r = r.sort("ts")
    return int(r["room"][-1])


class RoomIndex:
    """Fast as-of room lookup per agent."""

    def __init__(self, sk: Skeleton):
        self.by = {}
        for a in sk.rooms["agent"].unique().to_list():
            r = sk.rooms.filter(pl.col("agent") == a).sort("ts")
            self.by[int(a)] = (r["ts"].to_numpy(), r["te"].to_numpy(), r["room"].to_numpy().astype(int))

    def at(self, agent: int, t: float) -> int:
        if t < ROOMS_START:
            return 0
        v = self.by.get(int(agent))
        if v is None:
            return -1
        i = np.searchsorted(v[0], t, side="right") - 1
        return int(v[2][i]) if i >= 0 else -1

    def rooms_in(self, agent: int, t0: float, t1: float) -> set:
        """Rooms the agent occupied at some time in [t0, t1]."""
        if t1 < ROOMS_START:
            return {0}
        v = self.by.get(int(agent))
        if v is None:
            return set()
        out = set()
        i0 = max(np.searchsorted(v[0], t0, side="right") - 1, 0)
        i1 = np.searchsorted(v[0], t1, side="right")
        for i in range(i0, i1):
            out.add(int(v[2][i]))
        if t0 < ROOMS_START:
            out.add(0)
        return out

    def moves(self, agent: int, t0: float, t1: float) -> list:
        """(time, from_room, to_room) moves of an agent in (t0, t1]."""
        v = self.by.get(int(agent))
        if v is None or t1 < ROOMS_START:
            return []
        out = []
        for i in range(1, len(v[0])):
            if t0 < v[0][i] <= t1 and v[2][i] != v[2][i - 1]:
                out.append((float(v[0][i]), int(v[2][i - 1]), int(v[2][i])))
        return out


# ----------------------------------------------------------------------------------------------- cone
def cone(sk: Skeleton, src: int, t0: float, t_end: float, lenient: bool = False, n_nodes: int | None = None,
         max_iter: int = 50):
    """Logged light cone from node `src` posting at t0 (time-respecting read-out paths up to t_end).

    Returns (T, K, H): entry time, entry call index (per-agent ci), hop count per node; inf / -1 outside.
    Best estimate: reader enters at the ledger's reading call. Lenient: an uncertain pair may be read one call earlier.
    """
    n_nodes = n_nodes or (HUMAN_BASE + 2000)
    T = np.full(n_nodes, INF)
    K = np.full(n_nodes, -1, np.int64)
    H = np.full(n_nodes, -1, np.int64)
    T[src] = t0
    H[src] = 0
    if lenient:
        tt = sk.e_t_len[sk.len_order]
        lo, hi = np.searchsorted(tt, t0 - 900.0, side="left"), np.searchsorted(tt, t_end, side="right")
        idx = sk.len_order[lo:hi]
        et, eci = sk.e_t_len[idx], sk.e_ci_len[idx]
    else:
        lo, hi = np.searchsorted(sk.e_t, t0, side="right"), np.searchsorted(sk.e_t, t_end, side="right")
        idx = np.arange(lo, hi)
        et, eci = sk.e_t[idx], sk.e_ci[idx]
    if len(idx) == 0:
        return T, K, H
    er, es, etm = sk.e_reader[idx], sk.e_sender[idx], sk.e_tm[idx]
    for _ in range(max_iter):
        elig = T[es] <= etm
        if not elig.any():
            break
        ii = np.flatnonzero(elig)
        rr = er[ii]
        u, first = np.unique(rr, return_index=True)
        cand_t = et[ii[first]]
        better = cand_t < T[u]
        if not better.any():
            break
        uu = u[better]
        T[uu] = cand_t[better]
        K[uu] = eci[ii[first[better]]]
        H[uu] = H[es[ii[first[better]]]] + 1
    # hop counts may be stale for nodes whose parent improved later: recompute from each node's entry event only
    # (the source keeps H = 0; fixed 2026-10-04 after round 1: the first version also overwrote the source's H)
    for _ in range(max_iter):
        elig = T[es] <= etm
        ii = np.flatnonzero(elig)
        if len(ii) == 0:
            break
        rr = er[ii]
        u, first = np.unique(rr, return_index=True)
        ent = (et[ii[first]] == T[u]) & (u != src)
        u, ev = u[ent], ii[first[ent]]
        newH = H[es[ev]] + 1
        if np.array_equal(H[u], newH):
            break
        H[u] = newH
    return T, K, H


# ----------------------------------------------------------------------------------------------- static graph
class StaticGraph:
    """Pre-item read-out graph over a sliding active-time window (counts of reads j -> i)."""

    def __init__(self, sk: Skeleton, W: float):
        self.sk, self.W = sk, W
        ok = np.isfinite(sk.e_at) & (sk.e_sender < HUMAN_BASE) & (sk.e_sender != AUTOMATED_NODE) & (sk.e_sender >= 0)
        o = np.argsort(sk.e_at[ok], kind="stable")
        self.at = sk.e_at[ok][o]
        self.j = sk.e_sender[ok][o]
        self.i = sk.e_reader[ok][o]
        self.n = 64
        self.C = np.zeros((self.n, self.n), np.int64)
        self.lo = 0
        self.hi = 0
        self.cur = -INF

    def at_time(self, at0: float) -> np.ndarray:
        """Adjacency (bool, j -> i) from reads with active time in [at0 - W, at0). Calls must come in time order."""
        if at0 < self.cur:  # restart (out of order)
            self.C[:] = 0
            self.lo = self.hi = 0
        self.cur = at0
        hi = np.searchsorted(self.at, at0, side="left")
        if hi > self.hi:
            np.add.at(self.C, (self.j[self.hi:hi], self.i[self.hi:hi]), 1)
            self.hi = hi
        lo = np.searchsorted(self.at, at0 - self.W, side="left")
        if lo > self.lo:
            lo = min(lo, self.hi)
            np.add.at(self.C, (self.j[self.lo:lo], self.i[self.lo:lo]), -1)
            self.lo = lo
        return self.C > 0


def bfs_hops(A: np.ndarray, seeds: np.ndarray) -> np.ndarray:
    """Hop distance (1 = seed) on adjacency A (j -> i); inf if unreachable."""
    n = A.shape[0]
    d = np.full(n, INF)
    if len(seeds) == 0:
        return d
    front = np.zeros(n, bool)
    front[seeds] = True
    d[front] = 1
    k = 1
    seen = front.copy()
    while front.any():
        nxt = A[front].any(axis=0) & ~seen
        if not nxt.any():
            break
        k += 1
        d[nxt] = k
        seen |= nxt
        front = nxt
    return d


# ----------------------------------------------------------------------------------------------- agent call helpers
def calls_of(sk: Skeleton, agent: int):
    s = sk.agent_calls.get(int(agent))
    if s is None:
        return None
    return s


def n_cycles(sk: Skeleton, agent: int, t0: float, ci_use: int, which: str = "t") -> int:
    """Receiving calls of `agent` with t0 < t_call (or bound) and index <= ci_use."""
    s = sk.agent_calls[int(agent)]
    arr = {"t": sk.c_t, "lo": sk.c_lo, "hi": sk.c_hi}[which][s]
    # number of calls with index <= ci_use and time > t0
    k = np.searchsorted(arr[: ci_use + 1], t0, side="right") if which == "t" else int(np.sum(arr[: ci_use + 1] <= t0))
    return int(ci_use + 1 - k)
