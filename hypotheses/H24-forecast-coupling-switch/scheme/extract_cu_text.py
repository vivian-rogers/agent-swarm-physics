"""H24 scheme step 1: pull the #21 computer-use turns (typed text, bash commands, the model's own
reasoning text) out of raw computer_use_turns, for the switch-on audit and numeric-forecast extraction.

One sequential pass over the 2.5 GB raw table (gzip -dc in a subprocess + one Python process = 2
processes). Lines are filtered on the created_at substring before parsing, so only #21 lines are parsed.

Output (gitignored, under data/ only; contains agent text, never copy it into committed files):
  data/processed/H24-forecast-coupling-switch/G21/cu_turns_text.parquet
    t (UTC), session_id, agent (int8 roster code), action, typed (agent_action.text, typed text),
    command (bash command), reasoning (assistant text + thinking, truncated), output_head (tool output, truncated)

Usage: uv run python hypotheses/H24-forecast-coupling-switch/scheme/extract_cu_text.py
"""
from __future__ import annotations

import datetime as dt
import gzip
import subprocess
import sys
import time
from pathlib import Path

import orjson
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import RAW, OUT, parse_ts  # noqa: E402

DEST = ROOT / "data/processed/H24-forecast-coupling-switch/G21"
LO, HI = dt.datetime(2025, 12, 1, 14, tzinfo=dt.timezone.utc), dt.datetime(2025, 12, 6, tzinfo=dt.timezone.utc)
SKIP_KEYS = {"signature", "thoughtSignature", "encrypted_content", "data", "image", "source", "arguments", "id",
             "call_id", "type", "role", "status", "phase", "name", "media_type"}
MAX_REASON, MAX_OUT = 6000, 1500


def collect_text(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in SKIP_KEYS:
                continue
            if isinstance(v, str):
                if k in ("text", "thinking", "reasoning", "reasoning_content", "content", "summary") and v.strip():
                    acc.append(v)
            else:
                collect_text(v, acc)
    elif isinstance(o, list):
        for v in o:
            collect_text(v, acc)


def main(lo=LO, hi=HI, dest=DEST):
    """Keep turns with lo <= created_at < hi (UTC) and write dest/cu_turns_text.parquet."""
    t0 = time.time()
    days, d = [], lo.date()
    while d <= hi.date():
        days.append(b'"created_at":"' + d.isoformat().encode())
        d += dt.timedelta(days=1)
    roster = pl.read_parquet(OUT / "roster.parquet", columns=["agent", "agent_id"])
    a_code = dict(zip(roster["agent_id"].to_list(), roster["agent"].to_list()))
    sess = {}
    with gzip.open(RAW / "computer_use_sessions.jsonl.gz", "rb") as f:
        for line in f:
            s = orjson.loads(line)
            sess[s["id"]] = a_code.get(s["agent_id"])
    print(f"sessions: {len(sess)} ({time.time() - t0:.0f}s)", flush=True)

    p = subprocess.Popen(["gzip", "-dc", str(RAW / "computer_use_turns.jsonl.gz")], stdout=subprocess.PIPE, bufsize=1 << 22)
    recs, n = [], 0
    for line in p.stdout:
        n += 1
        tail = line[-200:]
        if not any(x in tail for x in days):
            continue
        r = orjson.loads(line)
        t = parse_ts(r["created_at"])
        if not (lo <= t < hi):
            continue
        aa = r.get("agent_action") or {}
        acc = []
        collect_text(r.get("agent_messages"), acc)
        reasoning = "\n".join(acc)[:MAX_REASON]
        out = r.get("output") or ""
        recs.append({"t": t, "session_id": r["session_id"], "agent": sess.get(r["session_id"]),
                     "action": aa.get("action") or ("bash" if "command" in aa else None),
                     "typed": aa.get("text") if isinstance(aa.get("text"), str) else None,
                     "command": aa.get("command") if isinstance(aa.get("command"), str) else None,
                     "reasoning": reasoning or None, "output_head": out[:MAX_OUT] or None})
        if n % 200000 == 0:
            print(f"  {n} lines, {len(recs)} kept ({time.time() - t0:.0f}s)", flush=True)
    p.wait()
    df = pl.DataFrame(recs, schema_overrides={"agent": pl.Int8}).sort("t")
    dest.mkdir(parents=True, exist_ok=True)
    df.write_parquet(dest / "cu_turns_text.parquet", compression="zstd")
    print(f"done: {n} lines scanned, {df.height} #21 turns kept, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
