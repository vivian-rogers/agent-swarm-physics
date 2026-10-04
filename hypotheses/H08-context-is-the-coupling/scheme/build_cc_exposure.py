"""C1 scheme: what the Claude Code agent actually saw (its logged village-API fetches), plus the village events of its
tenure for the room-rule reconstruction.

  uv run python hypotheses/H08-context-is-the-coupling/scheme/build_cc_exposure.py

Two streaming passes over raw tables (no text is written):
1. events.jsonl.gz, rows created 2026-01-20 .. 2026-04-05: id, event_index, created_at, actionType, actor (agent code,
   'human' or 'automated'/'other'), roomId -> room code.
2. claude_code_messages.jsonl.gz: every `mcp__village__get_events` call and its result (event ids, types, creation
   times; agentStatus counters), per-message token usage, compaction boundaries, and every tool call (turn cadence).

Outputs in data/processed/H08-context-is-the-coupling/cc/: cc_village_events, cc_fetches, cc_seen, cc_usage,
cc_compactions, cc_toolcalls (parquet, zstd). Rows on holdout PT dates (held-out goal periods or NE windows) are
dropped before writing; `--allow-holdout` is reserved for the confirmatory script.
"""
from __future__ import annotations

import gzip
import json
import sys
import time
from pathlib import Path

import orjson

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403

RAW = ROOT / "data/raw/ai-village"
from zoneinfo import ZoneInfo  # noqa: E402
PT_ZONE = ZoneInfo("America/Los_Angeles")
CC = OUT / "cc"
T0, T1 = "2026-01-20", "2026-04-05"


def ts(s):
    """ISO timestamps (UTC). Some API results carry locale-formatted strings of unknown zone: returned as None (the
    authoritative event time comes from the events table via the event id)."""
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "").replace("T", " ")[:26]).replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def scan_events(ros_by_id, room_by_id):
    rows = []
    with gzip.open(RAW / "events.jsonl.gz", "rb") as f:
        for line in f:
            # cheap prefilter on the creation date
            i = line.find(b'"created_at"')
            if i >= 0:
                d = line[i + 14:i + 24].decode(errors="ignore")
                if not (T0 <= d < T1):
                    continue
            r = orjson.loads(line)
            ca = r.get("created_at") or ""
            if not (T0 <= ca[:10] < T1):
                continue
            dd = r.get("data") or {}
            at = dd.get("actionType")
            actor = dd.get("speakerId") or dd.get("agentId")
            if actor in ros_by_id:
                ak, ac = "agent", ros_by_id[actor]
            elif at == "USER_TALK":
                ak, ac = "human", -1
            else:
                ak, ac = "other", -1
            rows.append({"event_id": r["id"], "event_index": int(r["event_index"]), "t": ts(ca), "action": at,
                         "actor_kind": ak, "agent": ac, "room": room_by_id.get(dd.get("roomId"), -1),
                         "has_room": dd.get("roomId") is not None, "message_id": dd.get("messageId")})
    return pl.DataFrame(rows, schema={"event_id": pl.Utf8, "event_index": pl.Int64, "t": pl.Datetime("us", "UTC"),
                                      "action": pl.Utf8, "actor_kind": pl.Utf8, "agent": pl.Int16, "room": pl.Int16,
                                      "has_room": pl.Boolean, "message_id": pl.Utf8})


def ts_local(s):
    """Locale-formatted API timestamps ('2/20/2026, 11:05:45 AM' or '4/3/2025, 12:28:52 PM PDT'): Pacific clock time
    (calibrated: matched event ids give UTC - local = 8 h in February), returned in UTC."""
    if not s or "/" not in s:
        return None
    s = s.strip()
    for suf in (" PDT", " PST"):
        if s.endswith(suf):
            s = s[: -len(suf)]
    try:
        loc = dt.datetime.strptime(s, "%m/%d/%Y, %I:%M:%S %p").replace(tzinfo=PT_ZONE)
    except ValueError:
        return None
    return loc.astimezone(dt.timezone.utc).replace(tzinfo=None)


def result_text(b):
    cont = b.get("content")
    if isinstance(cont, list):
        for x in cont:
            if isinstance(x, dict) and x.get("type") == "text":
                return x.get("text")
    elif isinstance(cont, str):
        return cont
    return None


def scan_cc():
    calls = {}           # tool_use id -> (t_call, input flags)
    fetches, seen, usage, comp, tools = [], [], [], [], []
    seen_msg_ids = set()
    with gzip.open(RAW / "claude_code_messages.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            t = ts(r["created_at"])
            c = r.get("content") or {}
            mt, sub = r.get("message_type"), r.get("message_subtype")
            if mt == "system" and sub == "compact_boundary":
                cm = c.get("compact_metadata") or {}
                comp.append({"t": t, "pre_tokens": cm.get("pre_tokens"), "trigger": cm.get("trigger"),
                             "session": r.get("sdk_session_id")})
                continue
            m = c.get("message") if isinstance(c, dict) else None
            if not isinstance(m, dict):
                continue
            if mt == "assistant":
                u = m.get("usage") or {}
                mid = m.get("id")
                if u and mid not in seen_msg_ids:
                    seen_msg_ids.add(mid)
                    usage.append({"t": t, "input": u.get("input_tokens"), "cache_read": u.get("cache_read_input_tokens"),
                                  "cache_write": u.get("cache_creation_input_tokens"), "output": u.get("output_tokens"),
                                  "session": r.get("sdk_session_id")})
            for b in m.get("content") or []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    name = b.get("name") or ""
                    tools.append({"t": t, "tool": name, "session": r.get("sdk_session_id")})
                    if name == "mcp__village__get_events":
                        inp = b.get("input") or {}
                        calls[b.get("id")] = (t, inp.get("limit"), bool(inp.get("markAsSeen")), "startAfter" in inp,
                                              "endBefore" in inp)
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in calls:
                    tc, lim, mark, sa, eb = calls[b.get("tool_use_id")]
                    txt = result_text(b)
                    j = None
                    if txt and txt[:1] == "{":
                        try:
                            j = json.loads(txt)
                        except Exception:
                            j = None
                    fid = len(fetches)
                    st = (j or {}).get("agentStatus") or {}
                    evs = (j or {}).get("events") or []
                    fetches.append({"fetch_id": fid, "t_call": tc, "t_result": t, "limit": lim, "mark_seen": mark,
                                    "start_after": sa, "end_before": eb, "parsed": j is not None,
                                    "n_events": len(evs), "unseen": st.get("unseenEventsCount"),
                                    "has_more": (j or {}).get("hasMore"), "current_room": st.get("currentRoom"),
                                    "in_cu_session": st.get("isInComputerUseSession"),
                                    "memory_update_needed": st.get("memoryUpdateNeeded"),
                                    "session": r.get("sdk_session_id")})
                    for e in evs:
                        if isinstance(e, dict) and e.get("id"):
                            seen.append({"fetch_id": fid, "event_id": e["id"], "action": e.get("actionType"),
                                         "t_event": ts(e.get("createdAt")), "t_event_local": ts_local(e.get("createdAt"))})
    seen_df = pl.DataFrame(seen, schema={"fetch_id": pl.Int64, "event_id": pl.Utf8, "action": pl.Utf8,
                                         "t_event": pl.Datetime("us", "UTC"), "t_event_local": pl.Datetime("us")})
    seen_df = seen_df.with_columns(pl.col("t_event_local").dt.replace_time_zone("UTC").alias("t_event_api"))
    return (pl.DataFrame(fetches), seen_df, pl.DataFrame(usage), pl.DataFrame(comp), pl.DataFrame(tools))


def holdout_dates_mask(t: pl.Series) -> np.ndarray:
    """True where the PT date of t is in the locked holdout (goal period or NE window)."""
    sys.path.insert(0, str(ROOT / "infra/shared"))
    from common import GoalLookup
    gl = GoalLookup()
    d = t.dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).to_list()
    g = [gl(x) if x is not None else 0 for x in t.to_list()]
    return np.array([is_holdout(dd, gg) if dd is not None else False for dd, gg in zip(d, g)])


def main(allow: bool | None = None, out_dir: Path | None = None):
    allow = ("--allow-holdout" in sys.argv) if allow is None else allow
    CC = out_dir or (OUT / "confirm/cc" if allow else OUT / "cc")
    t0 = time.time()
    CC.mkdir(parents=True, exist_ok=True)
    ros = pl.read_parquet(SH / "roster.parquet")
    ros_by_id = dict(zip(ros["agent_id"].to_list(), ros["agent"].to_list()))
    rooms = pl.read_parquet(SH / "rooms.parquet")
    room_by_id = dict(zip(rooms["room_id"].to_list(), rooms["room"].to_list()))
    fe, se, us_, co, to = scan_cc()
    print(f"cc stream: {fe.height} fetches, {se.height} seen rows, {us_.height} usage, {co.height} compactions, "
          f"{to.height} tool calls ({time.time() - t0:.0f}s)", flush=True)
    if not allow:
        fe = fe.filter(~pl.Series(holdout_dates_mask(fe["t_result"])))
        se = se.filter(pl.col("fetch_id").is_in(fe["fetch_id"].implode()))
        us_ = us_.filter(~pl.Series(holdout_dates_mask(us_["t"])))
        co = co.filter(~pl.Series(holdout_dates_mask(co["t"]))) if co.height else co
        to = to.filter(~pl.Series(holdout_dates_mask(to["t"])))
    for name, df in (("cc_fetches", fe), ("cc_seen", se), ("cc_usage", us_), ("cc_compactions", co), ("cc_toolcalls", to)):
        df.write_parquet(CC / f"{name}.parquet", compression="zstd")
    ev = scan_events(ros_by_id, room_by_id)
    if not allow:
        ev = ev.filter(~pl.Series(holdout_dates_mask(ev["t"])))
    ev.write_parquet(CC / "cc_village_events.parquet", compression="zstd")
    print(f"village events {ev.height} ({time.time() - t0:.0f}s)", flush=True)
    write_provenance(f"{CC.relative_to(OUT)}/*", "hypotheses/H08-context-is-the-coupling/scheme/build_cc_exposure.py",
                     ["claude_code_messages", "events", "roster (shared)", "rooms (shared)"],
                     {"events_window": [T0, T1], "text": "none written", "holdout": "holdout PT dates dropped before writing"})


if __name__ == "__main__":
    main()
