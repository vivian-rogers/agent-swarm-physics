"""H07 scheme, step 3: history searches after the split (leakage channel), from raw events.

One streaming pass over events.jsonl.gz; parses only lines containing SEARCH_HISTORY; keeps events with
T0 <= t < 2026-05-01 (no holdout window intersects it). Output `search_history_text.parquet` (a text sidecar):
event_index, t, agent, room, query (<= 300 chars), and flags for whether the query or the answer mention the
other fork (rpg-game-best / rpg-game-rest / #best / #rest / 'best room' / 'rest room').
"""
from __future__ import annotations

import datetime as dt
import gzip
import json
import re
import sys
from pathlib import Path

import orjson
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import RAW, UTC, git_commit, parse_ts  # noqa: E402

OUT = ROOT / "data/processed/H07-rpg-forks"
T0 = dt.datetime(2026, 3, 16, 16, 20, 5, 640000, tzinfo=UTC)
T1 = dt.datetime(2026, 5, 1, tzinfo=UTC)
BEST = re.compile(r"rpg-game-best|#best\b|\bbest room\b|\bbest team\b", re.I)
REST = re.compile(r"rpg-game-rest|#rest\b|\brest room\b|\brest team\b", re.I)
RPG = re.compile(r"\brpg\b|rpg-game", re.I)


def main():
    ro = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    A = dict(zip(ro["agent_id"].to_list(), ro["agent"].to_list()))
    rooms = pl.read_parquet(ROOT / "data/processed/shared/rooms.parquet")
    R = dict(zip(rooms["room_id"].to_list(), rooms["room"].to_list()))
    recs = []
    with gzip.open(RAW / "events.jsonl.gz", "rb") as f:
        for line in f:
            if b"SEARCH_HISTORY" not in line:
                continue
            r = orjson.loads(line)
            d = r["data"]
            if d.get("actionType") != "SEARCH_HISTORY":
                continue
            t = parse_ts(r["created_at"])
            if not (T0 <= t < T1):
                continue
            q = d.get("query") or ""
            ans = d.get("answerToQuery") or ""
            if not isinstance(ans, str):
                ans = json.dumps(ans)
            recs.append((r["event_index"], t, A.get(d.get("agentId")), R.get(d.get("roomId")), q[:300],
                         bool(RPG.search(q)), bool(BEST.search(q)), bool(REST.search(q)),
                         bool(RPG.search(ans)), bool(BEST.search(ans)), bool(REST.search(ans)), len(ans)))
    df = pl.DataFrame(recs, schema=["event_index", "t", "agent", "room", "query", "q_rpg", "q_best", "q_rest",
                                    "a_rpg", "a_best", "a_rest", "answer_len"], orient="row",
                      infer_schema_length=None).sort("t")
    df.write_parquet(OUT / "search_history_text.parquet")
    p = OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov["search_history"] = {"built_by": "hypotheses/H07-rpg-forks/scheme/search_history.py",
                              "git_commit": git_commit(), "inputs": [{"source": "ai-village", "tables": ["events"]}],
                              "params": {"window": [T0.isoformat(), T1.isoformat()]},
                              "built_at": dt.datetime.now(UTC).isoformat()}
    p.write_text(json.dumps(prov, indent=1))
    print(len(df), "searches")


if __name__ == "__main__":
    main()
