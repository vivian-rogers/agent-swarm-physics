"""H23 scheme step 1: pull the #44 computer-use turns of the #best agents and the temporary leader from raw.

One streaming pass over data/raw/ai-village/computer_use_turns.jsonl.gz (gzip -dc | python: 2 processes).
Keeps turns created in [2026-05-26 17:00, 2026-05-30 00:00) UTC and inside goal period #44 (no holdout rows) by
agents 24-29 (#best: Opus 4.7, Kimi K2.6, GPT-5.5, Gemini 3.5 Flash, temporary leader, Opus 4.8).

Output (gitignored, text sidecar; never commit its contents):
    data/processed/H23-leader-distillation-copy/G44/turns_text.parquet
        turn_id, session_id, agent, t, kind (bash / tool / talk), tool, command, output, error, assistant_text
The holdout is re-checked with infra/shared/common.holdout_mask before writing.
"""
from __future__ import annotations

import datetime as dt
import gzip
import subprocess
import sys
from pathlib import Path

import orjson
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import RAW, holdout_mask, pt_date, GoalLookup, parse_ts  # noqa: E402

OUT = ROOT / "data/processed/H23-leader-distillation-copy/G44"
T_LO, T_HI = "2026-05-26 17:00:00", "2026-05-30 00:00:00"
AGENTS = {24, 25, 26, 27, 28, 29}
CAP_OUT, CAP_TXT = 40_000, 40_000


def assistant_text(msgs) -> str:
    """Concatenate visible text and thinking from a provider-shaped response (Anthropic / OpenAI / others)."""
    parts: list[str] = []

    def walk(o):
        if isinstance(o, dict):
            for k in ("text", "thinking", "reasoning_content", "summary_text"):
                v = o.get(k)
                if isinstance(v, str) and v.strip():
                    parts.append(v)
            for k in ("content", "summary", "parts"):
                if k in o:
                    walk(o[k])
            if o.get("type") in ("function_call", "tool_use") or "arguments" in o or "input" in o:
                a = o.get("arguments", o.get("input"))
                if isinstance(a, (dict, list)):
                    a = orjson.dumps(a).decode()
                if isinstance(a, str):
                    parts.append(f"[{o.get('name', 'tool')}] {a}")
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(msgs)
    return "\n".join(parts)


def main():
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    id2code = {r["agent_id"]: r["agent"] for r in roster.iter_rows(named=True) if r["agent"] in AGENTS}
    sess2agent: dict[str, int] = {}
    with gzip.open(RAW / "computer_use_sessions.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            if r["agent_id"] in id2code:
                sess2agent[r["id"]] = id2code[r["agent_id"]]
    rows = []
    p = subprocess.Popen(["gzip", "-dc", str(RAW / "computer_use_turns.jsonl.gz")], stdout=subprocess.PIPE,
                         bufsize=1 << 24)
    n = 0
    for line in p.stdout:
        n += 1
        if b'"created_at":"2026-05-2' not in line:
            continue
        r = orjson.loads(line)
        ca = r.get("created_at") or ""
        if not (T_LO <= ca < T_HI):
            continue
        a = sess2agent.get(r["session_id"])
        if a is None:
            continue
        act = r.get("agent_action") or {}
        cmd = act.get("command") if isinstance(act, dict) else None
        tool = None
        if isinstance(act, dict):
            tool = "bash" if cmd is not None else act.get("action") or act.get("name")
        kind = "bash" if cmd is not None else ("tool" if act else "talk")
        rows.append({"turn_id": r["id"], "session_id": r["session_id"], "agent": a, "t": parse_ts(ca),
                     "kind": kind, "tool": tool,
                     "command": cmd if cmd is None else cmd[:CAP_OUT],
                     "output": (r.get("output") or "")[:CAP_OUT] or None,
                     "error": (r.get("error") or "")[:4000] or None,
                     "assistant_text": assistant_text(r.get("agent_messages"))[:CAP_TXT] or None})
    p.wait()
    df = pl.DataFrame(rows).sort("t")
    gl = GoalLookup()
    df = df.with_columns(pl.Series("goal_no", [gl(t) for t in df["t"]], dtype=pl.Int8),
                         pl.col("agent").cast(pl.Int8)).filter(pl.col("goal_no") == 44)
    held = holdout_mask([pt_date(t) for t in df["t"]], df["goal_no"].to_list())
    assert not any(held), "holdout rows in the #44 window"
    OUT.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT / "turns_text.parquet", compression="zstd", compression_level=9)
    print(f"scanned {n} lines; kept {df.height} turns", df.group_by("agent", "kind").len().sort("agent"))


if __name__ == "__main__":
    main()
