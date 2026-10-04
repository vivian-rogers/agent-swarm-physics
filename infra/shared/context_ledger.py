"""Turn-level context ledger: for every model call of every agent, what had newly entered its context since its previous
call. Docs (schema, semantics, validation, limits): infra/data-quality/context_ledger.md.

Outputs (data/processed/shared/, zstd parquet, no text, ALL days; `holdout` flags locked-holdout days and exploratory
users must drop them):
  call_windows.parquet          one row per model call (= turn): timing layer. Call start (best estimate, bounds, source,
                                confidence), logged times, end, previous call's end, what sits in between (pause, long
                                previous call, consolidation, session boundary, first call of the day).
  context_ledger_turns.parquet  one row per model call: content layer. Counts of chat items that newly entered the
                                context (by kind), @-mentions of the agent, backlogs, reset flags, unseen-event cap,
                                outage overlap.
  context_ledger_items.parquet  one row per (receiving call, chat message): message id (never text), sender, kind, age
                                at the call start, mention flag, rank, cap/uncertainty flags.
  call_starts_logged.parquet    cache of the raw scan: logged call starts of Gemini-family calls (HTTP `date` header minus
                                the server-timing duration, in `computer_use_turns.agent_messages` / `events.data.output`).

Visibility rule (one sentence): a message is in context for call c iff it was posted in the agent's room (at posting
time) by someone else before c's context assembly t_start(c); it is *new* at c iff it was posted at or after the
previous receiving call's t_start. t_start is (in order of preference) logged (Gemini), the expiry of a timer PAUSE plus
overhead, a nearby scaffold marker (forced mouse_move / restart) plus overhead, the end of the previous call plus the
calibrated scaffold overhead (chained computer-use and summary calls), or the first logged record minus the agent's
calibrated latency (scheduled chat-mode calls, first call of a day, early wakes). A PAUSE, a long tool call or any other
gap is therefore time during which arrivals become visible to the NEXT call, never to the call that is already running.
Calibration and validation numbers: infra/data-quality/context_ledger_validation.json.

Usage (at most 2 threads; leave the machine to the other agents):
  uv run python infra/shared/context_ledger.py                      # = build_all step: scan if no cache, build, validate
  uv run python infra/shared/context_ledger.py scan                 # raw pass for logged starts (cache, ~2-6 min)
  uv run python infra/shared/context_ledger.py build                # all tables
  uv run python infra/shared/context_ledger.py build --dry-run 38   # one goal period: build in memory, print checks,
                                                                    # write nothing (or to --out DIR)
  uv run python infra/shared/context_ledger.py validate             # -> infra/data-quality/context_ledger_validation.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, RAW, ROOT, holdout_mask, write_provenance  # noqa: E402

SH = OUT
DQ = ROOT / "infra/data-quality"
LOGGED = SH / "call_starts_logged.parquet"
OUTAGES_SHARED = SH / "outages.parquet"                                  # shared outages (infra/shared/outages.py)
OUTAGES_H38 = ROOT / "data/processed/H38-platform-stalls/outages.parquet"  # H38's original (fallback)
OUTAGES = OUTAGES_SHARED if OUTAGES_SHARED.exists() else OUTAGES_H38
KICKS = SH / "kicks_classified.parquet"                                   # automated-message kinds (optional)
H08_CC = ROOT / "data/processed/H08-context-is-the-coupling/cc"          # H08's Claude Code fetch tables (validation)
UTC = dt.timezone.utc

# ----------------------------------------------------------------------------- parameters
SAME_CALL_S = 1.0          # records of one agent <= 1 s apart are one model call (parallel tool calls, talk+wait, ...)
MIRROR_S = 2.0             # a computer-use mirror turn and its event within 2 s are one call (H14 rule, nearest join)
TIMER_TOL_S = 30.0         # a wake >= expiry - 30 s ends a PAUSE at its timer (H09); earlier = early wake
LONG_PREV_S = 60.0         # previous call busy (start -> logged end) > 60 s = "long tool call" in between
MARKER_NEAR_S = 600.0      # a scaffold marker anchors a call start only if it is <= 10 min before the call
LOOKBACK_S = 7 * 86400     # items older than 7 days at a call are not listed (agent away; counted in lookback_capped)
CAP_DATE = dt.datetime(2026, 6, 11, tzinfo=UTC)   # scaffold: <= 200 unseen events shown per turn from 2026-06-11
CAP_N = 200
ROOMS_V1 = dt.datetime(2026, 2, 25, tzinfo=UTC)   # before rooms v1 everyone is in #general (room 0)
PERMA = "2026-03-24"       # regime III: permanent computer use
CF_SEG = (41, 42)          # H15: consolidation after a 41-42-record segment = forced (the 41-turn cap)

MIRRORS = {"send_message_back_to_chat": "AGENT_TALK", "pause": "PAUSE", "search_history": "SEARCH_HISTORY",
           "move_to_room": "ENTER_ROOM", "request_Google_sign_in": "REQUEST_GOOGLE_SIGN_IN",
           "request_human_helper": "REQUEST_HUMAN_HELPER",
           "cancel_request_for_human_helper": "CANCEL_REQUEST_FOR_HUMAN_HELPER",
           "request_approval_for_unsolicited_outreach": "OUTREACH_APPROVAL_REQUEST"}
BOUNDARY_EVENTS = ("CONSOLIDATE", "START_USING_COMPUTER")     # the next computer-use turn starts a fresh context
MARKER_EVENTS = ("RESTARTING_AFTER_GOOGLE_SIGN_IN",)          # scaffold restarts: a boundary, not a model call
IGNORED_EVENTS = ("STOP_HUMAN_USE_SESSION", "OUTREACH_APPROVAL_RESPONSE")   # external, attributed to the agent

KINDS = ["cu_action", "talk", "pause", "wait", "consolidate", "session_start", "session_stop", "search", "room_move",
         "request"]
K = {k: i for i, k in enumerate(KINDS)}
EVENT_KIND = {"AGENT_TALK": "talk", "PAUSE": "pause", "WAIT": "wait", "CONSOLIDATE": "consolidate",
              "START_USING_COMPUTER": "session_start", "STOP_USING_COMPUTER": "session_stop",
              "SEARCH_HISTORY": "search", "ENTER_ROOM": "room_move", "REQUEST_GOOGLE_SIGN_IN": "request",
              "REQUEST_HUMAN_HELPER": "request", "CANCEL_REQUEST_FOR_HUMAN_HELPER": "request",
              "OUTREACH_APPROVAL_REQUEST": "request"}
# primary kind of a multi-record call (first match wins)
KIND_PRIORITY = ["consolidate", "session_stop", "session_start", "pause", "wait", "search", "room_move", "request",
                 "talk", "cu_action"]
SRC = ["event", "action", "both"]
MODES = ["chat", "cu", "summary"]          # summary = memory consolidation / session-summary call (receives no items)
START_SRC = ["logged", "prev_end", "pause_expiry", "marker", "latency"]
CONF = ["low", "medium", "high"]
GAP = ["busy", "pause", "pause_early", "after_summary", "marker", "session_start", "long_prev", "first_of_day"]
ITEM_KINDS = ["agent", "human", "nudge", "pause_resume", "automated_other"]
PAUSE_RX = re.compile(r"(?i)paus\w* the village")
RESUME_RX = re.compile(r"(?i)resum\w* the village|resuming for today")
NUDGE_RX = re.compile(r"triggered by:\s*\[")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


def from_us(x) -> pl.Series:
    return pl.Series(np.asarray(x, dtype=np.int64)).cast(pl.Datetime("us")).dt.replace_time_zone("UTC")

# ============================================================================= 1. raw scan: logged call starts

RX_SESSION = re.compile(rb'"session_id":"([0-9a-f-]{36})"')
RX_CREATED = re.compile(rb'"created_at":"(20[0-9]{2}-[0-9]{2}-[0-9]{2} [0-9:.]+)"')
RX_DATE = re.compile(rb'"date":"([A-Z][a-z]{2}, [0-9]{2} [A-Z][a-z]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}) GMT"')
RX_DUR = re.compile(rb'gfet4t7; dur=([0-9]+)')
RX_AGENT = re.compile(rb'"(?:agentId|speakerId)":"([0-9a-f-]{36})"')
RX_TYPE = re.compile(rb'"actionType":"([A-Z_]+)"')


def _ts(b: bytes) -> dt.datetime:
    return dt.datetime.fromisoformat(b.decode()).replace(tzinfo=UTC)


def _hdr(b: bytes) -> dt.datetime:
    return dt.datetime.strptime(b.decode(), "%a, %d %b %Y %H:%M:%S").replace(tzinfo=UTC)


def _scan_file(name: str, kind: str, sess: dict, agents: dict):
    out = []
    with gzip.open(RAW / f"{name}.jsonl.gz", "rb") as f:
        for line in f:
            i = line.find(b"sdkHttpResponse")
            if i < 0:
                continue
            md, mu = RX_DATE.search(line, i), RX_DUR.search(line, i)
            j = line.rfind(b'"created_at":"')
            mc = RX_CREATED.match(line, j) if j >= 0 else None
            if not (md and mu and mc):
                continue
            if kind == "turn":
                ms = RX_SESSION.search(line)
                a = sess.get(ms.group(1).decode()) if ms else None
                typ = None
            else:
                ma, mt = RX_AGENT.search(line), RX_TYPE.search(line)
                a = agents.get(ma.group(1).decode()) if ma else None
                typ = mt.group(1).decode() if mt else None
            out.append((kind, a, _ts(mc.group(1)), _hdr(md.group(1)), int(mu.group(1)), typ))
    return out


def scan_logged():
    """One lean pass over computer_use_turns and events (lines without `sdkHttpResponse` are skipped unparsed)."""
    t0 = time.time()
    ros = pl.read_parquet(SH / "roster.parquet")
    agents = dict(zip(ros["agent_id"].to_list(), ros["agent"].to_list()))
    sess = {}
    rx_id, rx_ag = re.compile(rb'"id":"([0-9a-f-]{36})"'), re.compile(rb'"agent_id":"([0-9a-f-]{36})"')
    with gzip.open(RAW / "computer_use_sessions.jsonl.gz", "rb") as f:
        for line in f:
            mi, ma = rx_id.search(line), rx_ag.search(line)
            if mi and ma:
                sess[mi.group(1).decode()] = agents.get(ma.group(1).decode())
    log(f"sessions {len(sess):,}")
    rows = _scan_file("events", "event", sess, agents)
    log(f"events: {len(rows):,} logged ({time.time()-t0:.0f}s)")
    rows += _scan_file("computer_use_turns", "turn", sess, agents)
    log(f"+turns: {len(rows):,} logged ({time.time()-t0:.0f}s)")
    df = pl.DataFrame(rows, orient="row", schema={"src": pl.Utf8, "agent": pl.Int8, "t_log": pl.Datetime("us", "UTC"),
                                                   "t_resp": pl.Datetime("us", "UTC"), "dur_ms": pl.Int32,
                                                   "action_type": pl.Utf8})
    df = df.with_columns(pl.col("src").cast(pl.Categorical), pl.col("action_type").cast(pl.Categorical)).sort("agent", "t_log")
    df.write_parquet(LOGGED, compression="zstd")
    write_provenance("context_ledger:scan", ["computer_use_turns", "events", "computer_use_sessions", "agents"],
                     {"field": "agent_messages / data.output .sdkHttpResponse.headers: date (1 s resolution) and "
                               "server-timing gfet4t7 dur (ms)", "start_estimate": "date + 0.5 s - dur",
                      "text": "none kept"})
    log(f"wrote {LOGGED.name}: {df.height:,} rows in {time.time()-t0:.0f}s")
    return df

# ============================================================================= 2. inputs


class Inputs:
    """Shared tables restricted to [t0, t1) (None = everything)."""

    def __init__(self, t0=None, t1=None):
        def win(lf, col="t"):
            if t0 is not None:
                lf = lf.filter((pl.col(col) >= t0) & (pl.col(col) < t1))
            return lf
        self.roster = pl.read_parquet(SH / "roster.parquet")
        self.cc = set(self.roster.filter(pl.col("claude_code"))["agent"].to_list())
        self.lab = dict(zip(self.roster["agent"].to_list(), self.roster["lab"].to_list()))
        self.cal = pl.read_parquet(SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.Utf8))
        assert self.cal["holdout"].to_list() == holdout_mask(self.cal["pt_date"].to_list(), self.cal["goal_no"].to_list())
        self.ev_all = win(pl.scan_parquet(SH / "events_core.parquet").select(
            "event_index", "t", "pt_date", "actor_kind", "agent", "action_type", "room", "pause_s", "tokens_in")).collect()
        self.acts = win(pl.scan_parquet(SH / "actions.parquet").select(
            "t", "agent", "action", "tok_in", "tok_cache_read", "tok_cache_write", "tok_out")).collect()
        chat = win(pl.scan_parquet(SH / "chat_core.parquet").select(
            "message_id", "t", "pt_date", "room", "speaker_kind", "agent", "length")).collect()
        men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
        self.chat = chat.join(men, on="message_id", how="left", maintain_order="left")
        self.rooms_tl = pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start")
        self.logged = pl.read_parquet(LOGGED) if LOGGED.exists() else None
        if self.logged is not None and t0 is not None:
            self.logged = self.logged.filter((pl.col("t_log") >= t0) & (pl.col("t_log") < t1))
        self.outages = pl.read_parquet(OUTAGES) if OUTAGES.exists() else None
        self.auto_kind = self._classify_automated()

    def _classify_automated(self) -> dict:
        """message_id -> item kind for automated messages: from the shared kicks_classified table when it exists, else
        (and as a cross-check, `self.auto_kind_text`) from the text read in memory only, never written."""
        ids = self.chat.filter(pl.col("speaker_kind").cast(pl.Utf8) == "automated")["message_id"]
        self.auto_kind_text, self.auto_kind_src = {}, "text"
        if ids.len() == 0:
            return {}
        tx = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).filter(
            pl.col("message_id").is_in(ids.implode()))
        for mid, text in tx.iter_rows():
            text = text or ""
            if NUDGE_RX.search(text) or text.startswith("@"):
                self.auto_kind_text[mid] = ITEM_KINDS.index("nudge")
            elif PAUSE_RX.search(text) or RESUME_RX.search(text):
                self.auto_kind_text[mid] = ITEM_KINDS.index("pause_resume")
            else:
                self.auto_kind_text[mid] = ITEM_KINDS.index("automated_other")
        if KICKS.exists():
            kc = (pl.read_parquet(KICKS, columns=["message_id", "kind"])
                  .filter(pl.col("message_id").is_in(ids.implode())
                          & pl.col("kind").cast(pl.Utf8).is_in(["nudge", "pause_resume", "automated_other"])))
            if kc.height:
                self.auto_kind_src = "kicks_classified"
                out = dict(self.auto_kind_text)   # messages missing from kicks_classified keep the text rule
                out.update({m: ITEM_KINDS.index(k) for m, k in zip(kc["message_id"].to_list(), kc["kind"].cast(pl.Utf8).to_list())})
                return out
        return dict(self.auto_kind_text)


def room_lookup(rooms_tl: pl.DataFrame) -> dict:
    tl = {}
    for (a,), sub in rooms_tl.group_by(["agent"], maintain_order=True):
        tl[int(a)] = (us(sub["t_start"]), sub["room"].to_numpy().astype(np.int16))
    return tl


ROOMS_V1_US = int(ROOMS_V1.timestamp() * 1e6)


def room_at(tl: dict, a: int, t: np.ndarray) -> np.ndarray:
    """Agent a's room at times t (rooms_timeline, as-of backward); #general (0) before rooms v1; -1 unknown."""
    t = np.asarray(t, dtype=np.int64)
    out = np.full(len(t), -1, dtype=np.int16)
    if a in tl:
        ts, rm = tl[a]
        idx = np.searchsorted(ts, t, side="right") - 1
        out = np.where(idx >= 0, rm[np.clip(idx, 0, None)], -1).astype(np.int16)
    return np.where((out < 0) & (t < ROOMS_V1_US), 0, out).astype(np.int16)

# ============================================================================= 3. calls (turns) and their windows


def records(inp: Inputs) -> pl.DataFrame:
    """All agent records (computer-use action rows + agent events), CC agent excluded, with marker flags."""
    ev = (inp.ev_all.filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()
                            & ~pl.col("agent").is_in(list(inp.cc)))
          .select("t", "agent", pl.col("action_type").cast(pl.Utf8).alias("k"), pl.lit(0, pl.Int8).alias("src"),
                  "pause_s", pl.col("room").alias("ev_room"), pl.col("tokens_in").alias("tok")))
    # total prompt tokens: Anthropic reports uncached input + cache reads + cache writes separately; OpenAI and Gemini
    # input counts already include the cached part
    anth = [a for a, l in inp.lab.items() if l == "Anthropic"]
    ac = (inp.acts.filter(pl.col("agent").is_not_null() & ~pl.col("agent").is_in(list(inp.cc)))
          .with_columns(pl.when(pl.col("agent").is_in(anth))
                        .then(pl.col("tok_in").fill_null(0) + pl.col("tok_cache_read").fill_null(0)
                              + pl.col("tok_cache_write").fill_null(0))
                        .otherwise(pl.col("tok_in")).alias("tot"))
          .select("t", "agent", pl.col("action").cast(pl.Utf8).alias("k"), pl.lit(1, pl.Int8).alias("src"),
                  pl.lit(None, pl.Float32).alias("pause_s"), pl.lit(None, pl.Int8).alias("ev_room"),
                  pl.when(pl.col("tok_in").is_null()).then(None).otherwise(pl.col("tot")).cast(pl.Int32).alias("tok")))
    rec = (pl.concat([ev, ac], how="vertical_relaxed").filter(~pl.col("k").is_in(list(IGNORED_EVENTS)))
           .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
           .sort("agent", "t", "src"))
    # forced mouse_move (H14 rule; 99.99% have zero input tokens where usage is logged): the first computer-use row
    # after a CONSOLIDATE / START_USING_COMPUTER event or of the agent's day, if it is a mouse_move
    newday = pl.col("pt_date") != pl.col("pt_date").shift(1).over("agent")
    rec = rec.with_columns((pl.col("k").is_in(list(BOUNDARY_EVENTS)) | newday.fill_null(True)).cast(pl.Int32)
                           .cum_sum().over("agent").alias("bseg"))
    rec = rec.with_columns(pl.when(pl.col("src") == 1).then(pl.col("src").cum_count().over("agent", "bseg", "src"))
                           .alias("apos"))
    rec = rec.with_columns((((pl.col("src") == 1) & (pl.col("apos") == 1) & (pl.col("k") == "mouse_move"))
                            | pl.col("k").is_in(list(MARKER_EVENTS))).alias("marker"))
    return rec


def group_calls(rec: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Group non-marker records into model calls. Returns (calls, markers)."""
    mk = rec.filter(pl.col("marker")).select("agent", "t", "k")
    r = rec.filter(~pl.col("marker")).sort("agent", "t", "src")
    gap = (pl.col("t") - pl.col("t").shift(1).over("agent")).dt.total_microseconds() / 1e6
    kp, sp = pl.col("k").shift(1).over("agent"), pl.col("src").shift(1).over("agent")
    mir = pl.lit(False)
    for a_k, e_k in MIRRORS.items():
        mir = mir | ((kp == a_k) & (pl.col("k") == e_k)) | ((kp == e_k) & (pl.col("k") == a_k))
    link = ((gap <= SAME_CALL_S) | ((gap <= MIRROR_S) & mir & (sp != pl.col("src")))).fill_null(False)
    r = r.with_columns((~link).cast(pl.Int32).cum_sum().over("agent").alias("cid"))
    kind_rank = {k: i for i, k in enumerate(KIND_PRIORITY)}
    r = r.with_columns(pl.col("k").replace_strict({**{a: EVENT_KIND[e] for a, e in MIRRORS.items()}, **EVENT_KIND},
                                                  default="cu_action").alias("kk"))
    r = r.with_columns(pl.col("kk").replace_strict(kind_rank, return_dtype=pl.Int8).alias("kr"))
    # H15 segment length at a CONSOLIDATE: computer-use rows (incl. mirrors and markers) in the segment it closes,
    # i.e. since the previous boundary (CONSOLIDATE / START_USING_COMPUTER / new day). The CONSOLIDATE row opens the
    # next segment (bseg increments on it), so the closed segment is bseg - 1.
    segrows = (rec.group_by("agent", "bseg").agg((pl.col("src") == 1).sum().cast(pl.Int32).alias("seg_len"))
               .with_columns((pl.col("bseg") + 1).alias("bseg")))
    seg = (rec.filter(pl.col("k") == "CONSOLIDATE").select("agent", "t", "bseg")
           .join(segrows, on=["agent", "bseg"], how="left").select("agent", "t", "seg_len"))
    r = r.join(seg, on=["agent", "t"], how="left", maintain_order="left")
    calls = (r.group_by("agent", "cid", maintain_order=True)
             .agg(pl.col("t").min().alias("t_first"), pl.col("t").max().alias("t_log"),
                  pl.col("kr").min().alias("kr"), (pl.col("kk") == "talk").any().alias("talk"),
                  pl.col("src").min().alias("smin"), pl.col("src").max().alias("smax"),
                  pl.col("pause_s").max().alias("pause_s"),
                  pl.col("t").filter(pl.col("k") == "PAUSE").min().alias("t_pause"),
                  pl.col("ev_room").drop_nulls().last().alias("ev_room"),
                  pl.col("tok").filter(pl.col("src") == 1).max().alias("tok_act"),
                  pl.col("tok").filter(pl.col("src") == 0).max().alias("tok_ev"),
                  pl.col("seg_len").max().alias("seg_len"),
                  pl.len().alias("n_rec"), pl.col("pt_date").first().alias("pt_date"))
             .with_columns(pl.col("kr").replace_strict({i: K[k] for i, k in enumerate(KIND_PRIORITY)},
                                                       return_dtype=pl.Int8).alias("kind"),
                           pl.when(pl.col("smin") == pl.col("smax")).then(pl.col("smin")).otherwise(2)
                           .cast(pl.Int8).alias("src"))
             .drop("kr", "smin", "smax", "cid").sort("agent", "t_first"))
    return calls, mk


def calibrate(cw: pl.DataFrame) -> dict:
    """Scaffold overhead = logged start - base, by gap class, from calls with a logged (Gemini) start on non-holdout
    days. Base = the latest scaffold marker if one sits between the calls, else the previous call's end (for a call
    after a timer PAUSE: the expiry)."""
    g = cw.filter(pl.col("logged_start").is_not_null() & ~pl.col("holdout") & ~pl.col("first_of_day")
                  & pl.col("t_prev_end").is_not_null())
    base = pl.when(pl.col("_marker_near") >= 0).then(pl.col("_marker_near")).otherwise(pl.col("t_prev_end").dt.epoch("us"))
    g = g.with_columns(((pl.col("logged_start").dt.epoch("us") - base) / 1e6).alias("ov"))
    out = {"overhead": {}, "n_logged": int(g.height)}
    nomk = pl.col("_marker_near") < 0
    for name, f in {"busy_cu": (pl.col("gap_kind") == GAP.index("busy")) & nomk & (pl.col("ctx_mode") == 1),
                    "busy_chat": (pl.col("gap_kind") == GAP.index("busy")) & nomk & (pl.col("ctx_mode") == 0),
                    "session_start": (pl.col("gap_kind") == GAP.index("session_start")) & nomk,
                    "summary": pl.col("gap_kind").is_in([GAP.index("busy"), GAP.index("long_prev")]) & nomk
                    & (pl.col("ctx_mode") == 2),
                    "long_prev": (pl.col("gap_kind") == GAP.index("long_prev")) & nomk,
                    "pause": pl.col("gap_kind") == GAP.index("pause"),
                    "marker": (pl.col("_marker_near") >= 0) & ~pl.col("gap_kind").is_in([GAP.index("pause"), GAP.index("pause_early")]),
                    "after_summary": (pl.col("gap_kind") == GAP.index("after_summary")) & nomk}.items():
        x = g.filter(f)["ov"].to_numpy()
        x = x[np.isfinite(x)]
        if len(x) >= 50:
            out["overhead"][name] = {"n": int(len(x)), "q05": float(np.percentile(x, 5)), "q25": float(np.percentile(x, 25)),
                                     "median": float(np.median(x)), "q75": float(np.percentile(x, 75)),
                                     "q95": float(np.percentile(x, 95)), "share_lt_-2s": float(np.mean(x < -2))}
    # call latency (first logged record - logged start) on chained computer-use calls vs scheduled chat-mode calls
    g = g.with_columns(((pl.col("t_first") - pl.col("logged_start")).dt.total_microseconds() / 1e6).alias("lat"))
    out["latency"] = {}
    for name, f in {"cu_busy": (pl.col("ctx_mode") == 1) & (pl.col("gap_kind") == GAP.index("busy")),
                    "chat_scheduled": (pl.col("ctx_mode") == 0) & pl.col("gap_kind").is_in([GAP.index("busy"),
                                                                                            GAP.index("long_prev")])}.items():
        x = g.filter(f)["lat"].to_numpy()
        if len(x) >= 50:
            out["latency"][name] = {"n": int(len(x)), **{f"q{p:02d}": float(np.percentile(x, p)) for p in (10, 50, 90)}}
    # latency relative to the agent's median chained-call latency (rho): places calls whose start is not chained
    # (scheduled chat-mode calls, first call of a day, early wakes) at t_first - m_agent * rho
    cu = g.filter((pl.col("ctx_mode") == 1) & (pl.col("gap_kind") == GAP.index("busy")) & (pl.col("lat") > 0))
    med = cu.group_by("agent").agg(pl.col("lat").median().alias("m"), pl.len().alias("n")).filter(pl.col("n") >= 20)
    gg = g.join(med.select("agent", "m"), on="agent", how="inner").with_columns((pl.col("lat") / pl.col("m")).alias("rho"))
    out["rho"] = {}
    for name, f in {"cu": (pl.col("ctx_mode") == 1) & (pl.col("gap_kind") == GAP.index("busy")),
                    "chat": (pl.col("ctx_mode") == 0) & pl.col("gap_kind").is_in([GAP.index("busy"), GAP.index("long_prev")]),
                    "first_of_day": pl.col("first_of_day")}.items():
        x = gg.filter(f)["rho"].to_numpy()
        x = x[np.isfinite(x) & (x > 0)]
        if len(x) >= 50:
            out["rho"][name] = {"n": int(len(x)), **{f"q{p:02d}": float(np.percentile(x, p)) for p in (5, 50, 95)}}
    return out


def overhead_for(cal: dict, name: str, q: str) -> float:
    o = cal["overhead"].get(name) or cal["overhead"].get("busy_cu")
    return max(0.0, o[q]) if o else 0.0


def build_windows(inp: Inputs, cal_override: dict | None = None) -> tuple[pl.DataFrame, dict]:
    rec = records(inp)
    calls, mk = group_calls(rec)
    log(f"records {rec.height:,} -> calls {calls.height:,}, markers {mk.height:,}")
    # day attributes
    cal = inp.cal.select("pt_date", "goal_no", "regime", "holdout")
    calls = calls.join(cal, on="pt_date", how="left", maintain_order="left").with_columns(
        pl.col("regime").fill_null(pl.when(pl.col("pt_date") < "2026-02-25").then(pl.lit("I"))
                                   .when(pl.col("pt_date") < PERMA).then(pl.lit("II")).otherwise(pl.lit("III"))),
        pl.col("holdout").fill_null(pl.Series(holdout_mask(calls["pt_date"].to_list(), [0] * calls.height))))
    # context mode: chat (event-only call outside a computer-use session, before perma), cu, summary
    # in a computer-use session iff the latest session_start/stop call before this one is a start
    calls = calls.with_columns(pl.when(pl.col("kind").is_in([K["session_start"], K["session_stop"]]))
                               .then(pl.col("kind")).otherwise(None).alias("_ss"))
    calls = calls.with_columns(pl.col("_ss").shift(1).over("agent").forward_fill().over("agent").alias("_ssprev"))
    insess = (pl.col("_ssprev") == K["session_start"]).fill_null(False)
    calls = calls.with_columns(
        pl.when(pl.col("kind").is_in([K["consolidate"], K["session_stop"]])).then(2)
        .when((pl.col("pt_date") >= PERMA) | (pl.col("src") >= 1) | insess).then(1)
        .otherwise(0).cast(pl.Int8).alias("ctx_mode")).drop("_ss", "_ssprev")
    # ---- vectorized pass: end of each call, previous end, markers in between, gap kind
    calls = calls.with_row_index("turn_id").with_columns(pl.col("turn_id").cast(pl.Int32))
    A = calls["agent"].to_numpy().astype(np.int64)
    TF, TL = us(calls["t_first"]), us(calls["t_log"])
    TP = calls["t_pause"].dt.epoch("us").fill_null(-1).to_numpy()
    PS = calls["pause_s"].fill_null(np.nan).to_numpy().astype(float)
    KD = calls["kind"].to_numpy()
    DAY = calls["pt_date"].to_numpy()
    same_prev = np.r_[False, A[1:] == A[:-1]]          # previous row is the same agent's previous call
    same_next = np.r_[A[:-1] == A[1:], False]
    mk = mk.sort("agent", "t")
    mkey = (mk["agent"].to_numpy().astype(np.int64) << 51) | us(mk["t"])
    key = lambda a, t: (a << 51) | t  # noqa: E731
    # pause calls end at their timer expiry, or earlier at the next record / marker (early wake)
    is_p = (KD == K["pause"]) & (TP > 0) & np.isfinite(PS)
    nxt = np.where(same_next, np.r_[TF[1:], 0], np.iinfo(np.int64).max)
    j = np.searchsorted(mkey, key(A, TL), "right")
    mnext = np.where(j < len(mkey), mkey[np.clip(j, 0, len(mkey) - 1)], np.iinfo(np.int64).max)
    mnext = np.where((mnext >> 51) == A, mnext & ((1 << 51) - 1), np.iinfo(np.int64).max)
    expiry = TP + np.where(is_p, np.nan_to_num(PS) * 1e6, 0).astype(np.int64)
    t_end = np.where(is_p, np.maximum(TL, np.minimum(expiry, np.minimum(nxt, mnext))), TL)
    prev_end = np.where(same_prev, np.r_[0, t_end[:-1]], -1)
    first_day = ~same_prev | np.r_[True, DAY[1:] != DAY[:-1]]
    # latest scaffold marker strictly between the previous call's logged end and this call's first record
    TLp = np.r_[0, TL[:-1]]
    j0 = np.searchsorted(mkey, key(A, TLp), "right")
    j1 = np.searchsorted(mkey, key(A, TF), "left")
    has_mk = same_prev & (j1 > j0)
    marker_t = np.where(has_mk, mkey[np.clip(j1 - 1, 0, max(0, len(mkey) - 1))] & ((1 << 51) - 1) if len(mkey) else -1, -1)
    after_pause = same_prev & np.r_[False, is_p[:-1]]
    exp_prev = np.r_[0, TP[:-1]] + (np.r_[0.0, np.nan_to_num(PS[:-1])] - TIMER_TOL_S).clip(0) * 1e6
    wake_early = after_pause & (prev_end < exp_prev.astype(np.int64))
    # a marker anchors the next call's start only when it is near it (a forced mouse_move from the previous evening
    # must not place a morning call); for resets every marker counts
    marker_near = np.where((marker_t >= 0) & (TF - marker_t <= MARKER_NEAR_S * 1_000_000), marker_t, -1)
    calls = calls.with_columns(pl.Series("_pe", prev_end), from_us(t_end).alias("t_end"),
                               pl.Series("_marker_near", marker_near.astype(np.int64)),
                               pl.Series("after_pause", after_pause), pl.Series("wake_early", wake_early),
                               pl.Series("first_of_day", first_day), pl.Series("_marker", marker_t.astype(np.int64)))
    calls = calls.with_columns(pl.when(pl.col("_pe") >= 0).then(from_us(np.where(prev_end >= 0, prev_end, 0)))
                               .otherwise(None).alias("t_prev_end")).drop("_pe")
    prevk = pl.col("kind").shift(1).over("agent")
    calls = calls.with_columns(
        pl.when(pl.col("first_of_day")).then(GAP.index("first_of_day"))
        .when(pl.col("after_pause") & pl.col("wake_early")).then(GAP.index("pause_early"))
        .when(pl.col("after_pause")).then(GAP.index("pause"))
        .when(prevk.is_in([K["consolidate"], K["session_stop"]])).then(GAP.index("after_summary"))
        .when(pl.col("_marker") >= 0).then(GAP.index("marker"))
        .when(prevk == K["session_start"]).then(GAP.index("session_start"))
        .otherwise(GAP.index("busy")).cast(pl.Int8).alias("gap_kind"))
    # logged starts (Gemini): the call's records matched exactly on (agent, logged time)
    if inp.logged is not None and inp.logged.height:
        lg = inp.logged.select("agent", "t_log", ((pl.col("t_resp").dt.epoch("us") + 500_000
                                                    - pl.col("dur_ms").cast(pl.Int64) * 1000)).alias("ls"),
                               (pl.col("dur_ms") / 1000).cast(pl.Float32).alias("dur_api_s"),
                               pl.col("t_resp"))
        recs = rec.filter(~pl.col("marker")).select("agent", "t")
        # map each record time to its call via an as-of join on t_first
        rc = recs.sort("t").join_asof(calls.select("agent", "turn_id", pl.col("t_first")).sort("t_first"),
                                      left_on="t", right_on="t_first", by="agent", strategy="backward")
        rc = rc.join(lg, left_on=["agent", "t"], right_on=["agent", "t_log"], how="inner")
        per = rc.group_by("turn_id").agg(pl.col("ls").min(), pl.col("dur_api_s").first(), pl.col("t_resp").min())
        calls = calls.join(per, on="turn_id", how="left", maintain_order="left")
        calls = calls.with_columns(pl.when(pl.col("ls").is_not_null()).then(from_us(calls["ls"].fill_null(0)))
                                   .otherwise(None).alias("logged_start")).drop("ls")
    else:
        calls = calls.with_columns(pl.lit(None, pl.Datetime("us", "UTC")).alias("logged_start"),
                                   pl.lit(None, pl.Float32).alias("dur_api_s"),
                                   pl.lit(None, pl.Datetime("us", "UTC")).alias("t_resp"))
    # long previous call: previous call busy (its start -> its logged end) > LONG_PREV_S; first pass uses prev_end as
    # the previous start; applied as a gap kind only where nothing more specific applies
    pbusy = ((pl.col("t_log") - pl.col("t_prev_end")).dt.total_microseconds() / 1e6).shift(1).over("agent")
    calls = calls.with_columns(pbusy.alias("prev_busy_s"))
    calls = calls.with_columns(
        pl.when((pl.col("gap_kind") == GAP.index("busy")) & (pl.col("prev_busy_s") > LONG_PREV_S)
                & prevk.is_in([K["cu_action"], K["search"], K["talk"]]))
        .then(GAP.index("long_prev")).otherwise(pl.col("gap_kind")).cast(pl.Int8).alias("gap_kind"))
    calls = calls.sort("agent", "t_first")
    assert calls["turn_id"].is_sorted(), "calls must stay in (agent, t_first) order"
    cal = cal_override or calibrate(calls)
    calls = estimate_starts(calls, cal)
    return calls, cal


def estimate_starts(calls: pl.DataFrame, cal: dict, use_logged: bool = True) -> pl.DataFrame:
    """Best estimate of each call's context-assembly time t_start, with bounds [t_start_lo, t_start_hi], source and
    confidence. Preference: logged (Gemini) > pause expiry > scaffold marker > previous end + calibrated overhead >
    first record - the agent's median latency (first call of a day, early wake: the idle before the call is unknown)."""
    TF = us(calls["t_first"])
    PE = calls["t_prev_end"].dt.epoch("us").fill_null(-1).to_numpy()
    LS = calls["logged_start"].dt.epoch("us").fill_null(-1).to_numpy() if use_logged else np.full(calls.height, -1)
    MK = calls["_marker_near"].to_numpy()
    GK = calls["gap_kind"].to_numpy()
    MODE = calls["ctx_mode"].to_numpy()
    A = calls["agent"].to_numpy()
    n = calls.height
    G = {g: GK == GAP.index(g) for g in GAP}
    q = lambda name: [int(overhead_for(cal, name, x) * 1e6) for x in ("q05", "median", "q95")]  # noqa: E731
    est, lo, hi = np.full(n, -1, np.int64), np.full(n, -1, np.int64), np.full(n, -1, np.int64)
    src, conf = np.full(n, START_SRC.index("prev_end"), np.int8), np.where(MODE == 1, 1, 0).astype(np.int8)
    has_pe = PE >= 0

    def put(mask, base, name, s, c=None):
        o05, omed, o95 = q(name)
        est[mask], lo[mask], hi[mask] = base[mask] + omed, base[mask] + o05, base[mask] + o95
        src[mask] = s
        if c is not None:
            conf[mask] = c
    busy = has_pe & (G["busy"] | G["marker"]) & (MK < 0)
    put(busy & (MODE == 1), PE, "busy_cu", START_SRC.index("prev_end"))
    put(has_pe & G["session_start"] & (MK < 0), PE, "session_start", START_SRC.index("prev_end"))
    # chat-mode calls (regimes I/II outside computer use) are scheduled, not chained: logged Gemini starts sit a
    # median ~50 s after the previous end (wide), while first record - start is tight (~10 s). They are placed by
    # latency below (busy_chat overhead kept only as calibration output).
    put(has_pe & G["long_prev"] & (MODE == 1), PE, "long_prev", START_SRC.index("prev_end"))
    # memory-consolidation / session-summary calls are chained to the call that triggered them
    put(has_pe & (G["busy"] | G["long_prev"]) & (MODE == 2) & (MK < 0), PE, "summary", START_SRC.index("prev_end"), 1)
    put(has_pe & G["after_summary"] & (MK < 0), PE, "after_summary", START_SRC.index("prev_end"))
    put(has_pe & G["pause"], PE, "pause", START_SRC.index("pause_expiry"))
    put((MK >= 0) & ~G["pause"] & ~G["pause_early"], MK, "marker", START_SRC.index("marker"), 1)
    # latency-placed: chat-mode calls, first call of a day without a marker, early wakes, no previous call
    lat_mask = est < 0
    src[lat_mask], conf[lat_mask] = START_SRC.index("latency"), 0
    ok = (src == START_SRC.index("prev_end")) & (MODE == 1) & G["busy"] & (est > 0)
    lat = (TF - est) / 1e6
    ok &= lat > 0
    gm = float(np.median(lat[ok])) if ok.any() else 10.0
    g10, g90 = (float(np.percentile(lat[ok], 10)), float(np.percentile(lat[ok], 90))) if ok.any() else (2.0, 30.0)
    df = pl.DataFrame({"a": A[ok], "l": lat[ok]}).group_by("a").agg(pl.col("l").median().alias("m"),
                                                                       pl.col("l").quantile(0.1).alias("q10"),
                                                                       pl.col("l").quantile(0.9).alias("q90"),
                                                                       pl.len().alias("n")).filter(pl.col("n") >= 20)
    mm = dict(zip(df["a"].to_list(), df["m"].to_list()))
    m = np.array([mm.get(a, gm) for a in A]) if lat_mask.any() else np.zeros(n)
    rho = cal.get("rho", {})
    dflt = {"q05": 0.5, "q50": 1.0, "q95": 2.5}
    r_cu, r_chat = rho.get("cu", dflt), rho.get("chat", rho.get("cu", dflt))
    r50 = np.where(MODE == 0, r_chat["q50"], r_cu["q50"])
    r05 = np.where(MODE == 0, r_chat["q05"], r_cu["q05"])
    r95 = np.where(MODE == 0, r_chat["q95"], r_cu["q95"])
    est[lat_mask] = TF[lat_mask] - (m * r50 * 1e6)[lat_mask].astype(np.int64)
    lo[lat_mask] = TF[lat_mask] - (m * r95 * 1e6)[lat_mask].astype(np.int64)
    hi[lat_mask] = TF[lat_mask] - (m * r05 * 1e6)[lat_mask].astype(np.int64)
    floor = np.where(has_pe, PE, np.iinfo(np.int64).min)
    for x in (est, lo, hi):
        x[lat_mask] = np.maximum(x[lat_mask], floor[lat_mask])
    # logged starts override (+-0.5 s: the date header has 1 s resolution)
    lg = LS > 0
    est[lg], lo[lg], hi[lg] = LS[lg], LS[lg] - 500_000, LS[lg] + 500_000
    src[lg], conf[lg] = START_SRC.index("logged"), 2
    # never after the call's first logged record; monotone per agent
    est, lo, hi = np.minimum(est, TF), np.minimum(lo, TF), np.minimum(hi, TF)
    calls = calls.with_columns(pl.Series("_e", est), pl.Series("_lo", lo), pl.Series("_hi", hi))
    calls = calls.with_columns(pl.col("_e").cum_max().over("agent").alias("_e"))
    calls = calls.with_columns(pl.min_horizontal("_lo", "_e").alias("_lo"), pl.max_horizontal("_hi", "_e").alias("_hi"))
    calls = calls.with_columns(from_us(calls["_e"]).alias("t_start"), from_us(calls["_lo"]).alias("t_start_lo"),
                               from_us(calls["_hi"]).alias("t_start_hi"), pl.Series("start_src", src, pl.Int8),
                               pl.Series("start_conf", conf, pl.Int8)).drop("_e", "_lo", "_hi")
    calls = calls.with_columns(((pl.col("t_first") - pl.col("t_start")).dt.total_microseconds() / 1e6)
                               .cast(pl.Float32).alias("latency_s"),
                               ((pl.col("t_log") - pl.col("t_resp")).dt.total_microseconds() / 1e6 - 0.5)
                               .cast(pl.Float32).alias("exec_s"))
    calls = calls.with_columns(((pl.col("t_log") - pl.col("t_start")).dt.total_microseconds() / 1e6)
                               .shift(1).over("agent").cast(pl.Float32).alias("prev_busy_s"))
    calls = calls.with_columns((pl.col("prev_busy_s") > LONG_PREV_S).fill_null(False).alias("long_prev"))
    return calls


# ============================================================================= 4. items and turn aggregates


def build_items(inp: Inputs, calls: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """(items, per-turn aggregates). Items: chat messages that newly entered each receiving call's context."""
    tl = room_lookup(inp.rooms_tl)
    recv = calls.filter(pl.col("ctx_mode") != 2).select("turn_id", "agent", "t_start", "t_start_lo", "t_start_hi",
                                                          "t_first", "pt_date").sort("agent", "t_start")
    # an agent's first receiving call has no previous one: its window opens at that day's calendar window start
    # (a new agent has no unseen-event high-water mark; we do not credit it with earlier days' messages)
    day0 = inp.cal.select("pt_date", pl.col("win_start").alias("_w0"))
    recv = recv.join(day0, on="pt_date", how="left").sort("agent", "t_start")
    recv = recv.with_columns(pl.col("t_start").shift(1).over("agent")
                             .fill_null(pl.min_horizontal(pl.col("_w0").fill_null(pl.col("t_start")), pl.col("t_start")))
                             .alias("t_win0"),
                             pl.col("turn_id").shift(1).over("agent").alias("prev_turn"),
                             pl.col("t_first").shift(1).over("agent").alias("t_first_prev"),
                             pl.col("t_start_hi").shift(1).over("agent").alias("t_hi_prev"))
    chat = inp.chat.with_columns(
        pl.when(pl.col("speaker_kind").cast(pl.Utf8) == "agent").then(0)
        .when(pl.col("speaker_kind").cast(pl.Utf8) == "human").then(1)
        .otherwise(pl.col("message_id").replace_strict(inp.auto_kind, default=ITEM_KINDS.index("automated_other")))
        .cast(pl.Int8).alias("ikind")).sort("t")
    m_t = us(chat["t"])
    m_room = chat["room"].fill_null(-1).to_numpy().astype(np.int16)
    m_spk = chat["agent"].fill_null(-1).to_numpy().astype(np.int16)
    pieces = []
    for (a,), rv in recv.group_by(["agent"], maintain_order=True):
        a = int(a)
        ts = us(rv["t_start"])
        lo_t, hi_t = int(us(rv["t_win0"][:1])[0]), ts[-1]
        i0, i1 = np.searchsorted(m_t, lo_t, "left"), np.searchsorted(m_t, hi_t, "left")
        idx = np.arange(i0, i1)
        if len(idx) == 0:
            continue
        ra = room_at(tl, a, m_t[idx])
        keep = (ra == m_room[idx]) & (ra >= 0) & (m_spk[idx] != a)
        idx = idx[keep]
        if len(idx) == 0:
            continue
        # receiving call: first receiving call with t_start > t_m (windows [t_start(prev), t_start) tile time)
        j = np.searchsorted(ts, m_t[idx], "right")
        ok = j < len(ts)
        idx, j = idx[ok], j[ok]
        pieces.append(pl.DataFrame({"row": idx.astype(np.int64), "turn_id": rv["turn_id"].to_numpy()[j],
                                    "agent": np.full(len(idx), a, np.int8)}))
    pairs = pl.concat(pieces) if pieces else pl.DataFrame(schema={"row": pl.Int64, "turn_id": pl.Int32, "agent": pl.Int8})
    ch = chat.with_row_index("row").with_columns(pl.col("row").cast(pl.Int64))
    it = (pairs.join(ch.select("row", "message_id", pl.col("t").alias("t_msg"), pl.col("agent").alias("sender"), "ikind",
                               "mentions_roster", "room", "length"), on="row", how="left")
          .join(recv.select("turn_id", "t_start", "t_start_lo", "t_win0", "t_first_prev", "t_hi_prev", "prev_turn"),
                on="turn_id", how="left"))
    it = it.with_columns(((pl.col("t_start") - pl.col("t_msg")).dt.total_microseconds() / 1e6).cast(pl.Float32).alias("age_s"),
                         pl.col("mentions_roster").list.contains(pl.col("agent")).fill_null(False).alias("ment"))
    n0 = it.height
    it = it.filter(pl.col("age_s") <= LOOKBACK_S)
    capped = n0 - it.height
    it = it.with_columns(
        (pl.col("t_msg") < pl.col("t_first_prev")).fill_null(False).alias("during_prev"),
        ((pl.col("t_msg") >= pl.col("t_start_lo")) | (pl.col("t_msg") < pl.col("t_hi_prev")).fill_null(False))
        .alias("uncertain"),
        pl.col("t_msg").rank("ordinal", descending=True).over("turn_id").cast(pl.Int16).alias("rank"))
    # unseen-event cap (from 2026-06-11): events by others in the message's room in [t_msg, t_start)
    it = add_cap(inp, it, tl)
    log(f"items {it.height:,} (dropped {capped:,} older than the lookback)")
    agg = (it.group_by("turn_id").agg(
        *[(pl.col("ikind") == i).sum().cast(pl.Int16).alias(f"n_{k}") for i, k in enumerate(ITEM_KINDS)],
        pl.len().cast(pl.Int32).alias("k_new"), pl.col("ment").sum().cast(pl.Int16).alias("n_ment"),
        ((pl.col("ikind") == ITEM_KINDS.index("nudge")) & pl.col("ment")).sum().cast(pl.Int16).alias("n_nudge_me"),
        pl.col("omitted").sum().cast(pl.Int16).alias("n_omitted"), pl.col("uncertain").sum().cast(pl.Int16).alias("n_uncertain"),
        pl.col("length").sum().cast(pl.Int32).alias("chars_new")))
    infl = (it.filter(pl.col("during_prev")).group_by("prev_turn").agg(pl.len().cast(pl.Int16).alias("n_inflight"))
            .rename({"prev_turn": "turn_id"}))
    agg = agg.join(infl, on="turn_id", how="full", coalesce=True)
    items = it.select("turn_id", "message_id", pl.col("sender").cast(pl.Int8),
                      pl.col("ikind").alias("kind"), "age_s", "ment", "rank", "during_prev", "uncertain", "omitted")
    return items.sort("turn_id", "rank", descending=[False, True]), agg, capped


def add_cap(inp: Inputs, it: pl.DataFrame, tl: dict) -> pl.DataFrame:
    """omitted = the message is older than the 200 newest unseen events at its call (scaffold cap from 2026-06-11)."""
    ev = inp.ev_all.filter(pl.col("actor_kind").cast(pl.Utf8).is_in(["agent", "human", "automated"])
                           & (pl.col("t") >= CAP_DATE - dt.timedelta(days=LOOKBACK_S // 86400)))
    if ev.height == 0 or it.filter(pl.col("t_start") >= CAP_DATE).height == 0:
        return it.with_columns(pl.lit(False).alias("omitted"), pl.lit(None, pl.Int32).alias("ev_rank"))
    ev = fill_event_rooms(ev, tl)
    t_ev, r_ev = us(ev["t"]), ev["eroom"].to_numpy()
    a_ev = ev["agent"].fill_null(-1).to_numpy()
    sub = it.with_row_index("_i").filter(pl.col("t_start") >= CAP_DATE)
    rank = np.zeros(sub.height, np.int64)
    tm, tsrt = us(sub["t_msg"]), us(sub["t_start"])
    rr, aa = sub["room"].fill_null(-1).to_numpy(), sub["agent"].to_numpy()
    for r in np.unique(rr):
        er = np.sort(t_ev[r_ev == r])
        sel = rr == r
        rank[sel] = np.searchsorted(er, tsrt[sel], "left") - np.searchsorted(er, tm[sel], "left")
        for a in np.unique(aa[sel]):
            own = np.sort(t_ev[(r_ev == r) & (a_ev == a)])
            s2 = sel & (aa == a)
            rank[s2] -= np.searchsorted(own, tsrt[s2], "left") - np.searchsorted(own, tm[s2], "left")
    full = np.full(it.height, -1, np.int64)
    full[sub["_i"].to_numpy()] = rank
    return it.with_columns(pl.Series("ev_rank", full).cast(pl.Int32)).with_columns(
        (pl.col("ev_rank") > CAP_N).alias("omitted"))


def fill_event_rooms(ev: pl.DataFrame, tl: dict) -> pl.DataFrame:
    room = ev["room"].fill_null(-1).to_numpy().astype(np.int16)
    a = ev["agent"].fill_null(-1).to_numpy()
    t = us(ev["t"])
    for x in np.unique(a[(room < 0) & (a >= 0)]):
        sel = (room < 0) & (a == x)
        room[sel] = room_at(tl, int(x), t[sel])
    room = np.where((room < 0) & (t < ROOMS_V1_US), 0, room)
    return ev.with_columns(pl.Series("eroom", room))


def turn_table(inp: Inputs, calls: pl.DataFrame, agg: pl.DataFrame) -> pl.DataFrame:
    tl = room_lookup(inp.rooms_tl)
    t = calls.join(agg, on="turn_id", how="left", maintain_order="left").sort("agent", "t_first")
    cnt = [f"n_{k}" for k in ITEM_KINDS] + ["k_new", "n_ment", "n_nudge_me", "n_omitted", "n_uncertain", "n_inflight",
                                            "chars_new"]
    t = t.with_columns(*[pl.col(c).fill_null(0) for c in cnt])
    recv = pl.col("ctx_mode") != 2
    # room at the call start and at the window start
    room = np.full(t.height, -1, np.int16)
    room0 = np.full(t.height, -1, np.int16)
    A = t["agent"].to_numpy()
    ts = us(t["t_start"])
    tw = t["t_prev_call"].dt.epoch("us").fill_null(-1).to_numpy() if "t_prev_call" in t.columns else None
    for a in np.unique(A):
        sel = A == a
        room[sel] = room_at(tl, int(a), ts[sel])
    t = t.with_columns(pl.Series("room", room).cast(pl.Int8))
    # previous receiving call's start (= window start)
    t = t.with_columns(pl.when(recv).then(pl.col("t_start")).otherwise(None).shift(1).over("agent")
                       .forward_fill().over("agent").alias("t_prev_call"))
    day0 = inp.cal.select("pt_date", pl.col("win_start").alias("_w0"))
    t = t.join(day0, on="pt_date", how="left", maintain_order="left").with_columns(
        pl.col("t_prev_call").fill_null(pl.min_horizontal(pl.col("_w0").fill_null(pl.col("t_start")), pl.col("t_start"))))
    tw = t["t_prev_call"].dt.epoch("us").fill_null(-1).to_numpy()
    for a in np.unique(A):
        sel = (A == a) & (tw >= 0)
        room0[sel] = room_at(tl, int(a), tw[sel])
    t = t.with_columns(((pl.Series(room0) >= 0) & (pl.Series(room0) != pl.Series(room))).alias("room_changed"))
    # resets between the previous receiving call and this one
    kd = pl.col("kind")
    t = t.with_columns(
        (kd == K["consolidate"]).alias("_c"), ((kd == K["consolidate"]) & pl.col("seg_len").is_between(*CF_SEG)).alias("_cf"),
        ((kd == K["session_stop"]) | (kd == K["session_start"]) | (pl.col("_marker") >= 0)).alias("_s"),
        pl.when(kd == K["consolidate"]).then(pl.col("seg_len")).otherwise(None).alias("_sl"))
    # run id: a receiving call closes its run; non-receiving calls in between belong to the next receiving call's run
    t = t.with_columns(recv.cast(pl.Int32).cum_sum().over("agent").alias("_r"))
    t = t.with_columns(pl.when(recv).then(pl.col("_r") - 1).otherwise(pl.col("_r")).alias("_run"))
    runs = t.group_by("agent", "_run").agg(pl.col("_c").any().alias("reset_consol"), pl.col("_cf").any().alias("reset_forced"),
                                           pl.col("_s").any().alias("_sess"), pl.col("_sl").max().alias("prev_seg_len"))
    t = t.join(runs, on=["agent", "_run"], how="left", maintain_order="left")
    # a session_start call itself is chat-mode: the reset applies to the call after it (marker / session_start gap)
    t = t.with_columns(
        (pl.col("_sess") & (kd != K["session_start"]) | (pl.col("_marker") >= 0)
         | (pl.col("kind").shift(1).over("agent") == K["session_start"])).fill_null(False).alias("reset_session"))
    t = t.with_columns(pl.when(recv).then(pl.col("reset_consol")).otherwise(False).alias("reset_consol"),
                       pl.when(recv).then(pl.col("reset_forced")).otherwise(False).alias("reset_forced"),
                       pl.when(recv).then(pl.col("reset_session")).otherwise(False).alias("reset_session"))
    reset_any = pl.col("reset_consol") | pl.col("reset_session")
    # backlogs over receiving calls
    rt = t.filter(recv).select("turn_id", "agent", "talk", "k_new", "ctx_mode", "reset_consol", "reset_session")
    rt = rt.with_columns(pl.col("talk").cast(pl.Int32).cum_sum().shift(1, fill_value=0).over("agent").alias("_tg"),
                         (pl.col("reset_consol") | pl.col("reset_session")).cast(pl.Int32).cum_sum().over("agent").alias("_rg"))
    rt = rt.with_columns(pl.col("k_new").cum_sum().over("agent", "_tg").cast(pl.Int32).alias("k_since_talk"),
                         pl.col("k_new").cum_sum().over("agent", "_rg").cast(pl.Int32).alias("_kctx"),
                         pl.int_range(1, pl.len() + 1).over("agent", "_rg").cast(pl.Int16).alias("_pos"))
    rt = rt.with_columns(pl.when(pl.col("ctx_mode") == 1).then(pl.col("_kctx")).otherwise(None).alias("k_ctx"),
                         pl.when(pl.col("ctx_mode") == 1).then(pl.col("_pos")).otherwise(None).alias("ctx_pos"))
    t = t.join(rt.select("turn_id", "k_since_talk", "k_ctx", "ctx_pos"), on="turn_id", how="left", maintain_order="left")
    _ = reset_any
    # unseen events by others in the agent's room in the window (cap check from 2026-06-11)
    t = add_event_counts(inp, t, tl)
    # outages (H38) overlapping the window
    t = add_outages(inp, t)
    t = t.with_columns(((pl.col("t_start") - pl.col("t_prev_call")).dt.total_seconds() > LOOKBACK_S)
                       .fill_null(False).alias("lookback_capped"))
    return t


def add_event_counts(inp: Inputs, t: pl.DataFrame, tl: dict) -> pl.DataFrame:
    ev = inp.ev_all.filter(pl.col("actor_kind").cast(pl.Utf8).is_in(["agent", "human", "automated"]))
    ev = fill_event_rooms(ev, tl)
    t_ev, r_ev = us(ev["t"]), ev["eroom"].to_numpy()
    a_ev = ev["agent"].fill_null(-1).to_numpy()
    n_ev = np.zeros(t.height, np.int64)
    ts = us(t["t_start"])
    tw = t["t_prev_call"].dt.epoch("us").fill_null(-1).to_numpy()
    tw = np.where(tw < 0, ts, np.maximum(tw, ts - LOOKBACK_S * 1_000_000))
    room, A = t["room"].to_numpy(), t["agent"].to_numpy()
    for r in np.unique(room):
        if r < 0:
            continue
        er = np.sort(t_ev[r_ev == r])
        sel = room == r
        n_ev[sel] = np.searchsorted(er, ts[sel], "left") - np.searchsorted(er, tw[sel], "left")
        for a in np.unique(A[sel]):
            own = np.sort(t_ev[(r_ev == r) & (a_ev == a)])
            s2 = sel & (A == a)
            n_ev[s2] -= np.searchsorted(own, ts[s2], "left") - np.searchsorted(own, tw[s2], "left")
    t = t.with_columns(pl.Series("n_ev", n_ev).cast(pl.Int32))
    return t.with_columns(((pl.col("t_start") >= CAP_DATE) & (pl.col("n_ev") > CAP_N) & (pl.col("ctx_mode") != 2))
                          .alias("cap_hit"))


def add_outages(inp: Inputs, t: pl.DataFrame) -> pl.DataFrame:
    if inp.outages is None or inp.outages.height == 0:
        return t.with_columns(pl.lit(None, pl.Float32).alias("outage_s"), pl.lit(None, pl.Boolean).alias("outage_off"))
    ts = us(t["t_start"])
    tw = t["t_prev_call"].dt.epoch("us").fill_null(-1).to_numpy()
    tw = np.where(tw < 0, ts, tw)

    def overlap(o: pl.DataFrame) -> np.ndarray:
        o = o.sort("t_start")
        s, e = us(o["t_start"]), us(o["t_end"])
        d = (e - s).astype(np.float64)
        cum = np.r_[0.0, np.cumsum(d)]

        def C(x):
            i = np.searchsorted(s, x, "right") - 1
            base = np.where(i >= 0, cum[np.clip(i, 0, None)], 0.0)
            part = np.where(i >= 0, np.clip(x - s[np.clip(i, 0, None)], 0, d[np.clip(i, 0, None)]), 0.0)
            return base + part
        return (C(ts) - C(tw)) / 1e6
    o = inp.outages
    return t.with_columns(pl.Series("outage_s", overlap(o)).cast(pl.Float32),
                          pl.Series("outage_off", overlap(o.filter(pl.col("village_off"))) > 0))

# ============================================================================= 5. assemble and write


CW_COLS = ["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "kind", "talk", "src", "ctx_mode", "n_rec",
           "t_start", "t_start_lo", "t_start_hi", "start_src", "start_conf", "t_first", "t_log", "t_end", "t_prev_end",
           "t_marker", "gap_kind", "after_pause", "wake_early", "long_prev", "prev_busy_s", "first_of_day", "logged_start",
           "dur_api_s", "exec_s", "latency_s", "pause_s"]
TURN_COLS = ["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_start", "t_prev_call", "t_first", "t_log",
             "src", "kind", "talk", "ctx_mode", "room", "room_changed",
             "n_agent", "n_human", "n_nudge", "n_pause_resume", "n_automated_other", "n_ment", "n_nudge_me",
             "k_new", "k_since_talk", "k_ctx", "chars_new", "n_inflight", "n_uncertain", "n_ev", "cap_hit", "n_omitted",
             "reset_consol", "reset_forced", "reset_session", "first_of_day", "ctx_pos", "prev_seg_len",
             "outage_s", "outage_off", "lookback_capped"]


def build(t0=None, t1=None, cal_override=None):
    tt = time.time()
    inp = Inputs(t0, t1)
    log(f"inputs loaded ({time.time()-tt:.0f}s); logged starts: {0 if inp.logged is None else inp.logged.height:,}; "
        f"outages table: {'yes' if inp.outages is not None else 'no'}")
    calls, cal = build_windows(inp, cal_override)
    log(f"windows done ({time.time()-tt:.0f}s); calibration n_logged={cal['n_logged']:,}")
    items, agg, capped = build_items(inp, calls)
    turns = turn_table(inp, calls, agg)
    log(f"turns done ({time.time()-tt:.0f}s)")
    calls = calls.with_columns(pl.when(pl.col("_marker") >= 0).then(pl.col("_marker")).otherwise(None)
                               .cast(pl.Datetime("us")).dt.replace_time_zone("UTC").alias("t_marker"))
    cw = calls.select(CW_COLS).with_columns(pl.col("regime").cast(pl.Categorical), pl.col("prev_busy_s").cast(pl.Float32),
                                            pl.col("n_rec").cast(pl.Int16), pl.col("pause_s").cast(pl.Float32))
    turns = turns.select(TURN_COLS).with_columns(
        pl.col("regime").cast(pl.Categorical), pl.col("k_new").cast(pl.Int16),
        *[pl.col(c).cast(pl.Int16) for c in ("n_agent", "n_human", "n_nudge", "n_pause_resume", "n_automated_other",
                                             "n_ment", "n_nudge_me", "n_omitted", "n_uncertain", "n_inflight")],
        pl.col("prev_seg_len").cast(pl.Int16))
    return {"call_windows": cw, "turns": turns, "items": items, "calibration": cal, "lookback_dropped": capped,
            "inputs": inp, "calls": calls}


def export(res: dict) -> dict:
    """Output form: t_start -> t_call, small codes as readable enums (dictionary-encoded in parquet)."""
    enum = lambda col, names: pl.col(col).replace_strict(dict(enumerate(names)), return_dtype=pl.Enum(names))  # noqa: E731
    common_ = [enum("kind", KINDS), enum("src", SRC), enum("ctx_mode", MODES)]
    cw = res["call_windows"].rename({"t_start": "t_call", "t_start_lo": "t_call_lo", "t_start_hi": "t_call_hi"}).with_columns(
        *common_, enum("start_src", START_SRC), enum("start_conf", CONF), enum("gap_kind", GAP))
    tu = res["turns"].rename({"t_start": "t_call"}).with_columns(*common_)
    it = res["items"].with_columns(enum("kind", ITEM_KINDS))
    return {"call_windows": cw, "turns": tu, "items": it}


def write(res: dict, out: Path = SH):
    out.mkdir(parents=True, exist_ok=True)
    ex = export(res)
    ex["call_windows"].write_parquet(out / "call_windows.parquet", compression="zstd", compression_level=9)
    ex["turns"].write_parquet(out / "context_ledger_turns.parquet", compression="zstd", compression_level=9)
    ex["items"].write_parquet(out / "context_ledger_items.parquet", compression="zstd", compression_level=9)
    ((DQ if out == SH else out) / "context_ledger_calibration.json").write_text(json.dumps(res["calibration"], indent=1))
    if out == SH:
        params = {"same_call_s": SAME_CALL_S, "mirror_s": MIRROR_S, "mirrors": MIRRORS, "timer_tol_s": TIMER_TOL_S,
                  "long_prev_s": LONG_PREV_S, "lookback_s": LOOKBACK_S, "cap": [str(CAP_DATE.date()), CAP_N],
                  "forced_consolidation_segment": CF_SEG, "calibration": res["calibration"],
                  "outages": str(OUTAGES.relative_to(ROOT)) if OUTAGES.exists() else None,
                  "rule": "item new at receiving call c iff t_start(prev receiving call) <= t_msg < t_start(c), in the "
                          "agent's room at t_msg, sender != agent; consolidation / session-stop calls receive no items",
                  "holdout": "all days, flagged"}
        write_provenance("context_ledger", ["events_core", "actions", "chat_core", "chat_mentions_clean", "chat_text "
                                            "(automated rows, in memory)", "rooms_timeline", "roster", "calendar",
                                            "call_starts_logged", "outages", "kicks_classified"], params)
    for f in ("call_windows", "context_ledger_turns", "context_ledger_items"):
        p = out / f"{f}.parquet"
        log(f"{p.name}: {p.stat().st_size/1e6:.1f} MB")


def goal_bounds(g: int):
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == g)
    return cal["win_start"].min() - dt.timedelta(hours=12), cal["win_end"].max() + dt.timedelta(hours=1)


def summarize(res: dict) -> dict:
    t, it, cw = res["turns"], res["items"], res["call_windows"]
    s = {"turns": t.height, "items": it.height, "receiving": int((t["ctx_mode"] != 2).sum()),
         "by_regime": {}, "start_src": dict(zip(*[x.to_list() for x in cw.group_by("start_src").len().sort("start_src")])),
         "gap_kind": {GAP[k]: v for k, v in cw.group_by("gap_kind").len().sort("gap_kind").iter_rows()}}
    for (r,), sub in t.group_by(["regime"]):
        s["by_regime"][str(r)] = {"turns": sub.height, "k_new_mean": float(sub["k_new"].mean()),
                                  "talk_share": float(sub["talk"].mean()), "reset_consol": int(sub["reset_consol"].sum()),
                                  "reset_forced": int(sub["reset_forced"].sum()), "cap_hit": int(sub["cap_hit"].sum())}
    return s

# ============================================================================= 6. validation


def _q(x, ps=(5, 25, 50, 75, 95)):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return {str(p): round(float(np.percentile(x, p)), 3) for p in ps} if len(x) else None


def item_frame(res: dict) -> pl.DataFrame:
    """Items with agent, exact message time, room, length and the receiving call's timing."""
    it, t = res["items"], res["turns"]
    ch = res["inputs"].chat.select("message_id", pl.col("t").alias("t_msg"), pl.col("room").alias("m_room"), "length")
    return (it.join(t.select("turn_id", "agent", "regime", "holdout", "t_start", "t_prev_call", "t_first", "ctx_mode",
                             "talk"), on="turn_id", how="left")
            .join(ch, on="message_id", how="left"))


def consistency(res: dict) -> dict:
    cw, t, it = res["call_windows"], res["turns"], res["items"]
    out = {"rows": {"call_windows": cw.height, "turns": t.height, "items": it.height,
                    "receiving_turns": int((t["ctx_mode"] != 2).sum())}}
    s = cw.sort("agent", "t_first")
    v = {}
    v["t_start_after_t_first"] = int((s["t_start"] > s["t_first"]).sum())
    v["t_first_after_t_log"] = int((s["t_first"] > s["t_log"]).sum())
    v["start_outside_bounds"] = int(((s["t_start_lo"] > s["t_start"]) | (s["t_start"] > s["t_start_hi"])).sum())
    v["t_start_not_monotone"] = int(s.select((pl.col("t_start") < pl.col("t_start").shift(1).over("agent")).sum()).item())
    v["t_end_before_t_log"] = int((s["t_end"] < s["t_log"]).sum())
    rt = t.filter(pl.col("ctx_mode") != 2)
    v["window_start_not_before_call"] = int((rt["t_prev_call"] > rt["t_start"]).sum())
    v["k_new_sum_minus_items"] = int(t["k_new"].cast(pl.Int64).sum()) - it.height
    j = item_frame(res)
    v["items_after_call_start"] = int((j["t_msg"] >= j["t_start"]).sum())
    v["items_before_window"] = int((j["t_msg"] < j["t_prev_call"]).sum())
    v["items_on_summary_calls"] = int((j["ctx_mode"] == 2).sum())
    v["duplicate_agent_message"] = int(j.select(pl.struct("agent", "message_id").is_duplicated().sum()).item())
    v["sender_is_recipient"] = int((j["sender"].cast(pl.Int16) == j["agent"].cast(pl.Int16)).sum())
    v["age_negative"] = int((it["age_s"] < 0).sum())
    # room respected: recompute the recipient's room at the message time
    tl = room_lookup(res["inputs"].rooms_tl)
    bad = 0
    for (a,), sub in j.group_by(["agent"]):
        bad += int((room_at(tl, int(a), us(sub["t_msg"])) != sub["m_room"].to_numpy()).sum())
    v["room_mismatch"] = bad
    out["violations"] = v
    out["shares"] = {
        "src": {SRC[k]: round(c / cw.height, 4) for k, c in cw.group_by("src").len().sort("src").iter_rows()},
        "kind": {KINDS[k]: round(c / cw.height, 4) for k, c in cw.group_by("kind").len().sort("kind").iter_rows()},
        "start_src": {START_SRC[k]: round(c / cw.height, 4) for k, c in cw.group_by("start_src").len().sort("start_src").iter_rows()},
        "start_conf": {CONF[k]: round(c / cw.height, 4) for k, c in cw.group_by("start_conf").len().sort("start_conf").iter_rows()},
        "gap_kind": {GAP[k]: round(c / cw.height, 4) for k, c in cw.group_by("gap_kind").len().sort("gap_kind").iter_rows()},
        "automated_kind_source": res["inputs"].auto_kind_src,
        "automated_kind_text_rule_disagreements": int(sum(1 for m, k in res["inputs"].auto_kind.items()
                                                          if res["inputs"].auto_kind_text.get(m, k) != k)),
        "items_uncertain": round(float(it["uncertain"].mean()), 4) if it.height else None,
        "items_omitted_cap": int(it["omitted"].sum()),
        "turns_cap_hit": int(t["cap_hit"].sum())}
    return out


def naive_vs_ledger(res: dict) -> dict:
    """Status changes between the naive rule (H18: a call starts at the agent's previous logged record; every call
    receives) and the ledger's per-call t_start. Per regime: share of (message, recipient) pairs whose first receiving
    call changes, and H29's statistic: of the messages the naive rule calls 'invisible' to a talk call (posted after its
    naive start, before its first record), the share that the ledger counts as visible."""
    c = res["calls"].sort("agent", "t_first")
    c = c.with_columns(pl.col("t_log").shift(1).over("agent").alias("_tlp"))
    c = c.with_columns(pl.when(pl.col("_marker") >= 0).then(from_us(c["_marker"].clip(0, None)))
                       .otherwise(pl.col("_tlp")).alias("s_naive"))
    j = item_frame(res)
    out = {}
    for (r,), sub in j.filter(~pl.col("holdout")).group_by(["regime"]):
        changed, n, flip_vis, inv_naive, reasons = 0, 0, 0, 0, {}
        for (a,), sa in sub.group_by(["agent"]):
            ca = c.filter(pl.col("agent") == a)
            sn = ca["s_naive"].dt.epoch("us").fill_null(-1).to_numpy()
            ids, tf, gk = ca["turn_id"].to_numpy(), us(ca["t_first"]), ca["gap_kind"].to_numpy()
            tm = us(sa["t_msg"])
            k = np.searchsorted(sn, tm, "right")          # first call whose naive start is after the message
            ok = k < len(sn)
            naive_id = np.where(ok, ids[np.clip(k, 0, len(ids) - 1)], -1)
            led = sa["turn_id"].to_numpy()
            ch = ok & (naive_id != led)
            n += int(ok.sum())
            changed += int(ch.sum())
            # reason = gap kind of the ledger's receiving call (or summary roll-over)
            led_pos = np.searchsorted(ids, led)
            for g in np.unique(gk[led_pos[ch]]):
                reasons[GAP[g]] = reasons.get(GAP[g], 0) + int((gk[led_pos[ch]] == g).sum())
        # H29 statistic on talk calls: for each talk call, messages in [s_naive, t_first)
        tc = c.filter((pl.col("regime") == r) & pl.col("talk") & ~pl.col("holdout") & pl.col("s_naive").is_not_null())
        jt = j.filter(pl.col("regime") == r)
        by_reason = {}
        for (a,), ta in tc.group_by(["agent"]):
            ja = jt.filter(pl.col("agent") == a)
            if ja.height == 0:
                continue
            tm = np.sort(us(ja["t_msg"]))
            sn, tf, ts = us(ta["s_naive"]), us(ta["t_first"]), us(ta["t_start"])
            inv = np.searchsorted(tm, tf, "left") - np.searchsorted(tm, sn, "left")
            vis = np.clip(np.searchsorted(tm, ts, "left") - np.searchsorted(tm, sn, "left"), 0, None)
            inv_naive += int(inv.sum())
            flip_vis += int(np.minimum(vis, inv).sum())
            for g in np.unique(ta["gap_kind"].to_numpy()):
                m = ta["gap_kind"].to_numpy() == g
                d = by_reason.setdefault(GAP[g], [0, 0])
                d[0] += int(inv[m].sum())
                d[1] += int(np.minimum(vis, inv)[m].sum())
        out[str(r)] = {"pairs": n, "changed_receiving_call": changed, "changed_share": round(changed / max(1, n), 4),
                       "changed_by_gap_kind": reasons,
                       "talk_invisible_naive": inv_naive, "talk_invisible_naive_now_visible": flip_vis,
                       "talk_flip_share": round(flip_vis / max(1, inv_naive), 4),
                       "talk_flip_by_gap_kind": {k: {"naive_invisible": a_, "now_visible": b_,
                                                     "share": round(b_ / max(1, a_), 3)} for k, (a_, b_) in by_reason.items()}}
    return out


def logged_validation(res: dict) -> dict:
    """Gemini calls: the start estimator without the logged time vs the logged start (leave-logged-out). Error of
    t_start, and agreement of the receiving call for the agents' items."""
    c = res["calls"]
    alt = estimate_starts(c.drop("t_start", "t_start_lo", "t_start_hi", "start_src", "start_conf", "latency_s",
                                 "exec_s", "prev_busy_s", "long_prev"), res["calibration"], use_logged=False)
    c = c.with_columns(alt["t_start"].alias("t_alt"), alt["start_src"].alias("src_alt"),
                       alt["t_start_lo"].alias("lo_alt"), alt["t_start_hi"].alias("hi_alt"))
    g = c.filter(pl.col("logged_start").is_not_null() & ~pl.col("holdout"))
    out = {"calls_with_logged_start": int(c["logged_start"].is_not_null().sum()),
           "agents": sorted(set(c.filter(pl.col("logged_start").is_not_null())["agent"].to_list())), "error_s": {}}
    err = ((g["t_alt"] - g["logged_start"]).dt.total_microseconds() / 1e6).to_numpy()
    inb = ((g["logged_start"] >= g["lo_alt"]) & (g["logged_start"] <= g["hi_alt"])).to_numpy()
    for s_ in np.unique(g["src_alt"].to_numpy()):
        for gkk in np.unique(g["gap_kind"].to_numpy()):
            m = (g["src_alt"].to_numpy() == s_) & (g["gap_kind"].to_numpy() == gkk)
            if m.sum() >= 30:
                out["error_s"][f"{START_SRC[s_]}|{GAP[gkk]}"] = {"n": int(m.sum()), "err": _q(err[m]),
                                                                 "abs_le_2s": round(float(np.mean(np.abs(err[m]) <= 2)), 3),
                                                                 "logged_within_bounds": round(float(inb[m].mean()), 3)}
    # receiving-call agreement for items of agents with logged calls (non-holdout receiving calls)
    j = item_frame(res).filter(~pl.col("holdout") & pl.col("agent").is_in(out["agents"]))
    rc = c.filter(pl.col("ctx_mode") != 2).sort("agent", "t_first")
    agree = n = 0
    agree_by = {}
    for (a,), sa in j.group_by(["agent"]):
        ca = rc.filter(pl.col("agent") == a)
        ids = ca["turn_id"].to_numpy()
        ta = np.maximum.accumulate(us(ca["t_alt"]))
        k = np.searchsorted(ta, us(sa["t_msg"]), "right")
        ok = k < len(ids)
        alt_id = np.where(ok, ids[np.clip(k, 0, len(ids) - 1)], -1)
        led = sa["turn_id"].to_numpy()
        has_log = ca["logged_start"].is_not_null().to_numpy()[np.searchsorted(ids, led)]
        m = ok & has_log
        n += int(m.sum())
        agree += int((alt_id[m] == led[m]).sum())
        gk = ca["gap_kind"].to_numpy()[np.searchsorted(ids, led)]
        for gg in np.unique(gk[m]):
            mm = m & (gk == gg)
            d = agree_by.setdefault(GAP[gg], [0, 0])
            d[0] += int(mm.sum())
            d[1] += int((alt_id[mm] == led[mm]).sum())
    out["item_assignment_agreement"] = {"items": n, "same_call": round(agree / max(1, n), 4),
                                        "by_gap_kind": {k: round(b / max(1, a_), 4) for k, (a_, b) in agree_by.items()}}
    return out


def token_validation(res: dict) -> dict:
    """Within a computer-use context segment, the growth of a call's input tokens over the previous call should carry
    the characters of the chat items that newly entered it. Compare the ledger's assignment with the naive rule and
    with the ledger shifted one call later / earlier: correlation of delta-tokens with new-item characters."""
    c = res["calls"].sort("agent", "t_first")
    t = res["turns"].select("turn_id", "chars_new", "k_new", "reset_consol", "reset_session", "first_of_day")
    c = c.join(t, on="turn_id", how="left", maintain_order="left").filter(pl.col("ctx_mode") == 1)
    lab = res["inputs"].lab
    c = c.with_columns(pl.col("agent").replace_strict(lab, default="Other").alias("lab"))
    # naive chars per call
    cn = res["calls"].sort("agent", "t_first").with_columns(pl.col("t_log").shift(1).over("agent").alias("_tlp"))
    cn = cn.with_columns(pl.when(pl.col("_marker") >= 0).then(from_us(cn["_marker"].clip(0, None)))
                         .otherwise(pl.col("_tlp")).alias("s_naive"))
    j = item_frame(res)
    naive_chars = {}
    for (a,), sa in j.group_by(["agent"]):
        ca = cn.filter(pl.col("agent") == a)
        sn = ca["s_naive"].dt.epoch("us").fill_null(-1).to_numpy()
        ids = ca["turn_id"].to_numpy()
        k = np.searchsorted(sn, us(sa["t_msg"]), "right")
        ok = k < len(ids)
        df = pl.DataFrame({"turn_id": ids[k[ok]], "len": sa["length"].to_numpy()[ok]}).group_by("turn_id").agg(pl.col("len").sum())
        naive_chars.update(dict(zip(df["turn_id"].to_list(), df["len"].to_list())))
    c = c.with_columns(pl.col("turn_id").replace_strict(naive_chars, default=0).alias("chars_naive"))
    c = c.with_columns(
        (pl.col("tok_act") - pl.col("tok_act").shift(1).over("agent")).alias("dtok"),
        pl.col("chars_new").shift(-1).over("agent").alias("chars_next"),
        pl.col("chars_new").shift(1).over("agent").alias("chars_prev"))
    ok = (pl.col("dtok").is_not_null() & ~pl.col("reset_consol") & ~pl.col("reset_session") & ~pl.col("first_of_day")
          & pl.col("tok_act").shift(1).over("agent").is_not_null() & ~pl.col("holdout")
          & (pl.col("dtok").abs() < 50_000))
    d = c.filter(ok)
    out = {}
    for lab_, sub in [("all", d)] + [(str(k), s) for (k,), s in d.group_by(["lab"])]:
        if sub.height < 500:
            continue
        y = sub["dtok"].to_numpy().astype(float)
        r = {}
        for col in ("chars_new", "chars_naive", "chars_next", "chars_prev"):
            x = sub[col].fill_null(0).to_numpy().astype(float)
            if x.std() == 0:
                continue
            r[col] = {"corr": round(float(np.corrcoef(x, y)[0, 1]), 4),
                      "slope_tok_per_char": round(float(np.polyfit(x, y, 1)[0]), 4)}
        # calls where the ledger and the naive rule disagree: which assignment explains the tokens?
        dis = sub.filter(pl.col("chars_new") != pl.col("chars_naive"))
        if dis.height >= 200:
            yy = dis["dtok"].to_numpy().astype(float)
            r["disagreeing_calls"] = {"n": dis.height, **{col: round(float(np.corrcoef(dis[col].to_numpy().astype(float), yy)[0, 1]), 4)
                                                          for col in ("chars_new", "chars_naive")}}
        out[lab_] = {"n": sub.height, **r}
    return out


def exposure_comparison(res: dict) -> dict:
    """Pairs and lags vs the shared `exposure` table (msg = row index of chat_core; recipient; lag to next event)."""
    ex = pl.read_parquet(SH / "exposure.parquet")
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "regime"]).with_row_index("msg")
    ex = ex.join(cc, on="msg", how="left")
    j = item_frame(res).select("message_id", "agent", "age_s", "regime", "holdout", "t_msg", "t_start")
    t0, t1 = j["t_msg"].min(), j["t_msg"].max()
    ex = ex.filter((pl.col("t") >= t0) & (pl.col("t") <= t1))
    m = ex.join(j, on=["message_id", "agent"], how="full", coalesce=True)
    out = {"exposure_pairs": ex.height, "ledger_pairs": j.height,
           "both": int((m["lag_s"].is_not_null() & m["age_s"].is_not_null()).sum()),
           "exposure_only": int((m["lag_s"].is_not_null() & m["age_s"].is_null()).sum()),
           "ledger_only": int((m["lag_s"].is_null() & m["age_s"].is_not_null()).sum()), "lag_by_regime": {}}
    b = m.filter(pl.col("lag_s").is_not_null() & pl.col("age_s").is_not_null() & ~pl.col("holdout").fill_null(True))
    for (r,), sub in b.group_by(["regime"]):
        el, ll = sub["lag_s"].to_numpy(), sub["age_s"].to_numpy()
        out["lag_by_regime"][str(r)] = {"n": sub.height, "exposure_lag_s": _q(el), "ledger_visible_lag_s": _q(ll),
                                        "exposure_minus_ledger_s": _q(el - ll),
                                        "share_exposure_over_by_60s": round(float(np.mean(el - ll > 60)), 4)}
    return out


def cc_validation(res: dict) -> dict:
    """The Claude Code agent's logged get_events fetches (H08's C1 tables) as ground truth for the ledger's rule:
    windows between consecutive context assemblies, room at posting time, everything unseen enters at the next
    assembly. Fetch = assembly (t_call of the get_events tool call). Current-feed days only (< 2026-03-17)."""
    if not (H08_CC / "cc_fetches.parquet").exists():
        return {"available": False}
    fe = pl.read_parquet(H08_CC / "cc_fetches.parquet").filter(pl.col("t_call") < dt.datetime(2026, 3, 17, tzinfo=UTC))
    se = pl.read_parquet(H08_CC / "cc_seen.parquet")
    ve = pl.read_parquet(H08_CC / "cc_village_events.parquet").select("event_id", "message_id")
    inp = res["inputs"]
    cc_agent = int(next(iter(inp.cc)))
    seen = (se.join(fe.select("fetch_id", "t_call", "t_result"), on="fetch_id", how="inner").join(ve, on="event_id", how="inner")
            .filter(pl.col("message_id").is_not_null()))
    first = seen.sort("t_call").group_by("message_id").agg(pl.col("t_call").first().alias("t_seen_call"),
                                                            pl.col("fetch_id").first().alias("fid_seen"))
    ch = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "agent", "speaker_kind"])
    tl = room_lookup(inp.rooms_tl)
    days = sorted(fe.with_columns(pl.col("t_call").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8)
                                  .alias("d"))["d"].unique().to_list())
    ch = ch.filter(pl.col("pt_date").is_in(days) & (pl.col("agent").fill_null(-1) != cc_agent))
    ch = ch.with_columns(pl.Series("cc_room", room_at(tl, cc_agent, us(ch["t"]))))
    ft = np.sort(us(fe["t_call"]))
    fid = fe.sort("t_call")["fetch_id"].to_numpy()
    # last fetch of each day bounds the prediction (messages after it are never fetched that day)
    fd = fe.with_columns(pl.col("t_call").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("d"))
    lastf = dict(fd.group_by("d").agg(pl.col("t_call").max()).iter_rows())
    ch = ch.with_columns(pl.col("pt_date").replace_strict({k: v for k, v in lastf.items()}, default=None,
                                                          return_dtype=pl.Datetime("us", "UTC")).alias("t_lastf"))
    ch = ch.filter(pl.col("t") < pl.col("t_lastf"))
    k = np.searchsorted(ft, us(ch["t"]), "right")
    ch = ch.with_columns(pl.Series("fid_pred", fid[np.clip(k, 0, len(fid) - 1)]))
    m = ch.join(first, on="message_id", how="left")
    own = m.filter(pl.col("room") == pl.col("cc_room"))
    other = m.filter(pl.col("room") != pl.col("cc_room"))
    seen_own = own.filter(pl.col("fid_seen").is_not_null())
    # position of the actual first-seen fetch relative to the predicted one
    pos = {int(f): i for i, f in enumerate(fid)}
    dpos = np.array([pos.get(int(s), -10**6) - pos.get(int(p), 0)
                     for s, p in zip(seen_own["fid_seen"].to_list(), seen_own["fid_pred"].to_list())])
    sk = seen_own["speaker_kind"].cast(pl.Utf8).to_numpy()
    out = {"available": True, "days": days, "fetches": fe.height, "chat_pred_own_room": own.height,
           "chat_seen_own_room": seen_own.height, "chat_seen_other_room": int(other["fid_seen"].is_not_null().sum()),
           "chat_other_room_posted": other.height,
           "membership_recall": round(seen_own.height / max(1, seen_own.height + int(other["fid_seen"].is_not_null().sum())), 4),
           "membership_precision": round(seen_own.height / max(1, own.height), 4),
           "timing_exact_call": round(float(np.mean(dpos == 0)), 4),
           "timing_within_1_call": round(float(np.mean(np.abs(dpos) <= 1)), 4),
           "timing_later_than_predicted": round(float(np.mean(dpos > 0)), 4),
           "timing_earlier_than_predicted": round(float(np.mean(dpos < 0)), 4),
           "delay_first_seen_s": _q(((seen_own["t_seen_call"] - seen_own["t"]).dt.total_microseconds() / 1e6).to_numpy()),
           "precision_by_kind": {}, "timing_exact_by_kind": {}}
    for kd in ("agent", "human", "automated"):
        o = own.filter(pl.col("speaker_kind").cast(pl.Utf8) == kd)
        if o.height:
            out["precision_by_kind"][kd] = round(float(o["fid_seen"].is_not_null().mean()), 4)
        mk_ = sk == kd
        if mk_.any():
            out["timing_exact_by_kind"][kd] = round(float(np.mean(dpos[mk_] == 0)), 4)
    # per goal period (H08's C1 periods)
    gmap = dict(zip(inp.cal["pt_date"].to_list(), inp.cal["goal_no"].to_list()))
    gs = np.array([gmap.get(d, 0) for d in seen_own["pt_date"].to_list()])
    go = np.array([gmap.get(d, 0) for d in own["pt_date"].to_list()])
    seen_flag = own["fid_seen"].is_not_null().to_numpy()
    out["by_goal"] = {f"G{g}": {"pred_own": int((go == g).sum()), "seen_own": int((gs == g).sum()),
                                "precision": round(float(seen_flag[go == g].mean()), 4),
                                "timing_exact_call": round(float(np.mean(dpos[gs == g] == 0)), 4) if (gs == g).any() else None,
                                "timing_within_1": round(float(np.mean(np.abs(dpos[gs == g]) <= 1)), 4) if (gs == g).any() else None}
                      for g in sorted(set(go.tolist()))}
    # restricted to fetches that mark events seen (the 'unseen events' semantics of the standard scaffold)
    ms = fe.filter(pl.col("mark_seen")).sort("t_call")
    out["mark_seen_fetch_share"] = round(ms.height / max(1, fe.height), 4)
    out["note"] = ("CC pulls events itself (get_events with limit and optional markAsSeen); the standard scaffold "
                   "pushes all unseen events at every call. Precision < 1 reflects the pull loop (limits, re-reads), "
                   "not the room rule; timing tests the window tiling on the messages it did see.")
    return out


def spot_checks(res: dict, n_per_regime: int = 300, seed: int = 7) -> dict:
    """Brute-force recount of new chat items for random receiving calls (independent of the vectorized join), and
    raw-file check of message time and room for the sampled items."""
    rng = np.random.default_rng(seed)
    t = res["turns"].filter((pl.col("ctx_mode") != 2) & ~pl.col("holdout") & pl.col("t_prev_call").is_not_null()
                            & ~pl.col("lookback_capped"))
    chat = res["inputs"].chat.sort("t")
    tl = room_lookup(res["inputs"].rooms_tl)
    ct, cr, ca = us(chat["t"]), chat["room"].fill_null(-1).to_numpy(), chat["agent"].fill_null(-1).to_numpy()
    out, sample_ids = {}, []
    for (r,), sub in t.group_by(["regime"]):
        idx = rng.choice(sub.height, size=min(n_per_regime, sub.height), replace=False)
        s = sub[idx]
        bad = 0
        for row in s.iter_rows(named=True):
            a, w0, w1 = row["agent"], int(row["t_prev_call"].timestamp() * 1e6), int(row["t_start"].timestamp() * 1e6)
            i0, i1 = np.searchsorted(ct, w0, "left"), np.searchsorted(ct, w1, "left")
            sel = np.arange(i0, i1)
            ra = room_at(tl, a, ct[sel])
            cnt = int(((ra == cr[sel]) & (ra >= 0) & (ca[sel] != a)).sum())
            bad += cnt != row["k_new"]
        out[str(r)] = {"sampled_calls": s.height, "count_mismatches": bad}
        sample_ids += s.filter(pl.col("k_new") > 0)["turn_id"].to_list()[:40]
    # raw check: chat_messages.jsonl.gz created_at / room_id for items of the sampled calls
    it = res["items"].filter(pl.col("turn_id").is_in(sample_ids))
    want = set(it["message_id"].to_list())
    rooms = pl.read_parquet(SH / "rooms.parquet")
    rmap = dict(zip(rooms["room_id"].to_list(), rooms["room"].to_list()))
    raw = {}
    rx = re.compile(rb'"id":"([0-9a-f-]{36})"')
    with gzip.open(RAW / "chat_messages.jsonl.gz", "rb") as f:
        for line in f:
            mi = rx.search(line)
            if mi and mi.group(1).decode() in want:
                rr = json.loads(line)
                raw[rr["id"]] = (dt.datetime.fromisoformat(rr["created_at"]).replace(tzinfo=UTC), rmap.get(rr["room_id"]))
    j = item_frame(res).filter(pl.col("turn_id").is_in(sample_ids))
    mism_t = sum(1 for mid, tm in zip(j["message_id"].to_list(), j["t_msg"].to_list())
                 if mid in raw and raw[mid][0] != tm)
    mism_r = sum(1 for mid, rm in zip(j["message_id"].to_list(), j["m_room"].to_list()) if mid in raw and raw[mid][1] != rm)
    later = sum(1 for mid, ts in zip(j["message_id"].to_list(), j["t_start"].to_list()) if mid in raw and raw[mid][0] >= ts)
    out["raw_chat_check"] = {"items": j.height, "found_in_raw": len(raw), "time_mismatch": mism_t,
                             "room_mismatch": mism_r, "raw_time_not_before_call_start": later}
    return out


def startup_checks(res: dict) -> dict:
    """Facts the rule relies on, re-measured: timer wakes, forced markers, logged-start overheads."""
    cw = res["call_windows"].filter(~pl.col("holdout"))
    out = {}
    for (r,), sub in cw.filter(pl.col("after_pause")).group_by(["regime"]):
        out[f"after_pause_{r}"] = {"n": sub.height, "early_wake_share": round(float(sub["wake_early"].mean()), 4),
                                   "latency_s": _q(sub["latency_s"].to_numpy())}
    out["first_of_day_with_marker_share"] = round(float(
        cw.filter(pl.col("first_of_day"))["start_src"].eq(START_SRC.index("marker")).mean()), 4)
    return out


def validate(res: dict) -> dict:
    v = {"built_at": dt.datetime.now(UTC).isoformat(), "calibration": res["calibration"],
         "lookback_dropped_pairs": res["lookback_dropped"]}
    for name, fn in [("consistency", consistency), ("startup_checks", startup_checks), ("spot_checks", spot_checks),
                     ("naive_vs_ledger", naive_vs_ledger), ("logged_leave_out", logged_validation),
                     ("tokens", token_validation), ("exposure", exposure_comparison), ("claude_code", cc_validation)]:
        t0 = time.time()
        try:
            v[name] = fn(res)
        except Exception as e:  # keep the other checks
            v[name] = {"error": repr(e)}
        log(f"validation {name} ({time.time()-t0:.0f}s)")
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="all", choices=["all", "scan", "build", "validate"],
                    help="all (default, used by build_all.py): scan if the cache is missing, then build --validate")
    ap.add_argument("--dry-run", type=int, default=None, help="goal period number: build it in memory only")
    ap.add_argument("--out", default=None)
    ap.add_argument("--validate", action="store_true", help="run the validation suite after building")
    a = ap.parse_args()
    if a.cmd == "all":
        if not LOGGED.exists():
            scan_logged()
        a.cmd, a.validate = "build", True
    if a.cmd == "scan":
        scan_logged()
    elif a.cmd == "build":
        if a.dry_run is not None:
            t0, t1 = goal_bounds(a.dry_run)
            res = build(t0, t1)
            print(json.dumps(summarize(res), indent=1, default=str))
            print(json.dumps(res["calibration"], indent=1))
            v = validate(res) if a.validate else {"consistency": consistency(res)}
            print(json.dumps(v, indent=1, default=str))
            if a.out:
                write(res, Path(a.out))
                (Path(a.out) / "validation.json").write_text(json.dumps(v, indent=1, default=str))
        else:
            res = build()
            write(res)
            print(json.dumps(summarize(res), indent=1, default=str))
            if a.validate:
                v = validate(res)
                (DQ / "context_ledger_validation.json").write_text(json.dumps(v, indent=1, default=str))
                log("wrote infra/data-quality/context_ledger_validation.json")
    else:
        res = build()
        v = validate(res)
        (DQ / "context_ledger_validation.json").write_text(json.dumps(v, indent=1, default=str))
        log("wrote infra/data-quality/context_ledger_validation.json")


if __name__ == "__main__":
    main()
