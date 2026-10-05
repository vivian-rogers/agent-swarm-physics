"""H08 round 2, R5 scheme: the status block of every village-tool result the Claude Code agent received.

  uv run python hypotheses/H08-context-is-the-coupling/scheme/build_cc_status.py

One pass over claude_code_messages.jsonl.gz. Rows whose PT date is reserved (held-out goal periods or NE windows; the
calendar's goal number is used for the goal check) are skipped from the raw `created_at` field before the row is parsed.
For each tool result that carries `agentStatus`: time, session, tool name, whether it is a get_events result, number of
events, `unseenEventsCount`, the index of the village goal whose text equals `currentVillageGoal` (whitespace
normalized; -1 = no match) and the index of the goal active at that time (village_goals start/end), `villageDayNumber`
and the result's `day` field when present, the age of `lastMemoryCreatedAt`, and the number of `villageAgents`.
No text is written. Output: data/processed/H08-context-is-the-coupling/r2/cc_status.parquet.
"""
from __future__ import annotations

import gzip
import json
import re
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import orjson

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403

RAW = ROOT / "data/raw/ai-village"
OUT2 = OUT / "r2"
PT = ZoneInfo("America/Los_Angeles")


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def ts(s):
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "").replace("T", " ")[:26]).replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def main():
    t0 = time.time()
    goals = [orjson.loads(l) for l in gzip.open(RAW / "village_goals.jsonl.gz")]
    goals.sort(key=lambda g: g["start_time"] or "")
    gtext = {norm(g["goal"]): i for i, g in enumerate(goals)}
    gst = [ts(g["start_time"]) for g in goals]
    gen = [ts(g["end_time"]) if g["end_time"] else None for g in goals]

    def active(t):
        idx = [i for i in range(len(goals)) if gst[i] and gst[i] <= t and (gen[i] is None or t < gen[i])]
        return idx[-1] if idx else -1

    cal = calendar()
    goal_of = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    hold_of = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    tool_of = {}
    recs = []
    n_skip = 0
    with gzip.open(RAW / "claude_code_messages.jsonl.gz", "rb") as f:
        for line in f:
            i = line.rfind(b'"created_at":"')
            if i < 0:
                continue
            ca = line[i + 14:line.find(b'"', i + 14)].decode(errors="ignore")
            t = ts(ca)
            d = t.astimezone(PT).date().isoformat()
            g = goal_of.get(d)
            if hold_of.get(d, False) or is_holdout(d, g) or g is None:
                n_skip += 1
                continue
            if b"agentStatus" not in line and b'"tool_use"' not in line:
                continue
            r = orjson.loads(line)
            m = (r.get("content") or {}).get("message") if isinstance(r.get("content"), dict) else None
            if not isinstance(m, dict):
                continue
            for b in m.get("content") or []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    tool_of[b.get("id")] = b.get("name") or ""
                elif b.get("type") == "tool_result":
                    c = b.get("content")
                    txt = c if isinstance(c, str) else (c[0].get("text") if isinstance(c, list) and c and isinstance(c[0], dict) else None)
                    if not txt or txt[:1] != "{" or "agentStatus" not in txt:
                        continue
                    try:
                        j = json.loads(txt)
                    except Exception:
                        continue
                    st = j.get("agentStatus") or {}
                    lm = ts(st.get("lastMemoryCreatedAt"))
                    tool = tool_of.get(b.get("tool_use_id"), "")
                    day = j.get("day")
                    recs.append({"t": t, "pt_date": d, "goal_no": g, "session": r.get("sdk_session_id"), "tool": tool,
                                 "get_events": tool == "mcp__village__get_events",
                                 "n_events": len(j.get("events") or []) if isinstance(j.get("events"), list) else None,
                                 "unseen": st.get("unseenEventsCount"),
                                 "goal_shown": gtext.get(norm(st.get("currentVillageGoal")), -1)
                                 if st.get("currentVillageGoal") is not None else None,
                                 "goal_active": active(t),
                                 "day_number": st.get("villageDayNumber") if isinstance(st.get("villageDayNumber"), int) else None,
                                 "day_field": day if isinstance(day, int) else None,
                                 "memory_age_s": (t - lm).total_seconds() if lm else None,
                                 "n_village_agents": len(st.get("villageAgents") or []) if isinstance(st.get("villageAgents"), list) else None})
    df = pl.DataFrame(recs, infer_schema_length=None).sort("t")
    OUT2.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT2 / "cc_status.parquet", compression="zstd")
    print(f"{df.height} status blocks; {n_skip} raw rows on reserved or non-calendar days skipped unparsed; {time.time() - t0:.0f}s")
    write_provenance("r2/cc_status.parquet", "hypotheses/H08-context-is-the-coupling/scheme/build_cc_status.py",
                     ["claude_code_messages (raw)", "village_goals", "calendar"],
                     {"reserved_days": "skipped before parsing", "goal_match": "whitespace-normalized exact text"}, folder=OUT2)


if __name__ == "__main__":
    main()
