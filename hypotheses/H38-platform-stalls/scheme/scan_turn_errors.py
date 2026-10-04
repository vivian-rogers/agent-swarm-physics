"""H38 scheme, step 1: categorize computer-use turn errors (one pass over raw computer_use_turns).

`actions.error` (shared) is a boolean "stderr was non-empty", which is dominated by benign stderr (git push/fetch
progress, curl progress meters). For stall attribution we need the *infrastructure* failures: bash timeouts, VM /
display failures, resource exhaustion, network failures. This scan reads only the `error` and `system` strings,
maps each to a category code with fixed regexes, and keeps no text.

Outputs (data/processed/H38-platform-stalls/):
  turn_errors.parquet   t (UTC), agent (int8), session (int32 code), err_cat, sys_cat   (rows with error or system only)
  sessions.parquet      session (int32), agent, created (UTC), first_t, last_t, n_turns, asked_to_stop

Categories (first matching rule, applied to the first 400 characters):
  timeout     bash/tool did not return ("timed out")
  vm          VM / display / session plumbing: coordinates unavailable, xdotool/DISPLAY failures, "Session has not
              started", screenshot failures, X server
  resource    too many open files, no space left, cannot allocate memory, killed (OOM)
  network     DNS / connection refused / reset / unreachable, TLS failures, HTTP 429 / 5xx gateway text
  git_info    benign git stderr ("From https://…", "To https://…", "Switched to branch", "Already on")
  progress    curl/wget progress meters
  tool_use    the agent misused a tool's arguments ("text is required for key", "is not accepted for")
  other       anything else (tracebacks, shell syntax errors, command not found, non-zero exit codes)
Infrastructure categories: timeout, vm, resource, network.

Usage: uv run python hypotheses/H38-platform-stalls/scheme/scan_turn_errors.py
"""
from __future__ import annotations

import datetime as dt
import gzip
import json
import re
import sys
import time
from pathlib import Path

import orjson
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, parse_ts  # noqa: E402

RAW = ROOT / "data/raw/ai-village"
OUT = ROOT / "data/processed/H38-platform-stalls"

RULES = [
    ("timeout", re.compile(r"timed out|has not returned|Timeout(Error)?\b", re.I)),
    ("vm", re.compile(r"Unable to get coordinates|xdotool|DISPLAY=|cannot open display|Session has not started|"
                      r"screenshot|X server|Xlib|no display", re.I)),
    ("resource", re.compile(r"Too many open files|No space left|Cannot allocate memory|MemoryError|out of memory|"
                            r"\bKilled\b", re.I)),
    ("network", re.compile(r"Could not resolve host|Temporary failure in name resolution|Name or service not known|"
                           r"Connection (refused|reset|timed out|aborted)|Network is unreachable|SSL|TLS|"
                           r"\b(429|502|503|504)\b|Bad Gateway|Service Unavailable|Too Many Requests|rate.?limit", re.I)),
    ("git_info", re.compile(r"^(From|To) (https?://|git@)|^Switched to (a new )?branch|^Already on|^remote:|"
                            r"^Everything up-to-date|^branch '", re.I)),
    ("progress", re.compile(r"% Total\s+% Received|^\s*\d+\s+\d+[kKmM]?\s+\d+\s", re.I)),
    ("tool_use", re.compile(r"is required for|is not accepted for|not a valid|Invalid (action|key|coordinate)", re.I)),
]
CATS = ["none", "timeout", "vm", "resource", "network", "git_info", "progress", "tool_use", "other"]
SID = re.compile(rb'"session_id":"([0-9a-f\-]{36})"')
CAT_RE = re.compile(rb'"created_at":"([^"]+)"')


def cat_of(s: str | None) -> str:
    if not s:
        return "none"
    head = s[:400]
    for name, rx in RULES:
        if rx.search(head):
            return name
    return "other"


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    agents = {}
    with gzip.open(RAW / "agents.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            agents[r["id"]] = r
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet").select("agent", "agent_id")
    acode = dict(zip(roster["agent_id"].to_list(), roster["agent"].to_list()))
    sess = {}
    with gzip.open(RAW / "computer_use_sessions.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            sess[r["id"]] = [len(sess), acode.get(r["agent_id"]), r["created_at"], bool(r.get("has_been_asked_to_stop")),
                             None, None, 0]
    errs = []
    n = 0
    with gzip.open(RAW / "computer_use_turns.jsonl.gz", "rb") as f:
        for line in f:
            n += 1
            m = SID.search(line)
            sid = m.group(1).decode() if m else None
            ts = CAT_RE.findall(line)
            t = ts[-1].decode() if ts else None  # the record's own created_at is the last one on the line
            s = sess.get(sid)
            if s is not None and t is not None:
                if s[4] is None or t < s[4]:
                    s[4] = t
                if s[5] is None or t > s[5]:
                    s[5] = t
                s[6] += 1
            if b'"error":null' in line and b'"system":null' in line:
                continue
            r = orjson.loads(line)
            ec, sc = cat_of(r.get("error")), cat_of(r.get("system"))
            if ec == "none" and sc == "none":
                continue
            errs.append((r["created_at"], s[1] if s else None, s[0] if s else None, ec, sc))
            if n % 500000 == 0:
                print(f"{n:,} lines {time.time() - t0:.0f}s", flush=True)
    E = (pl.DataFrame(errs, schema=["t", "agent", "session", "err_cat", "sys_cat"], orient="row")
         .with_columns(pl.col("t").str.to_datetime("%Y-%m-%d %H:%M:%S%.f", time_zone="UTC").dt.cast_time_unit("us"),
                       pl.col("agent").cast(pl.Int8), pl.col("session").cast(pl.Int32),
                       pl.col("err_cat").cast(pl.Enum(CATS)), pl.col("sys_cat").cast(pl.Enum(CATS)))
         .sort("t"))
    E.write_parquet(OUT / "turn_errors.parquet", compression="zstd")
    S = (pl.DataFrame([(v[0], v[1], v[2], v[4], v[5], v[6], v[3]) for v in sess.values()],
                      schema=["session", "agent", "created", "first_t", "last_t", "n_turns", "asked_to_stop"], orient="row")
         .with_columns(*[pl.col(c).str.to_datetime("%Y-%m-%d %H:%M:%S%.f", time_zone="UTC", strict=False).dt.cast_time_unit("us")
                         for c in ("created", "first_t", "last_t")],
                       pl.col("session").cast(pl.Int32), pl.col("agent").cast(pl.Int8), pl.col("n_turns").cast(pl.Int32))
         .sort("created"))
    S.write_parquet(OUT / "sessions.parquet", compression="zstd")
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["scan_turn_errors"] = {
        "built_by": "hypotheses/H38-platform-stalls/scheme/scan_turn_errors.py", "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["computer_use_turns", "computer_use_sessions", "agents"]}],
        "params": {"categories": CATS, "infra_categories": ["timeout", "vm", "resource", "network"],
                   "rules": {k: v.pattern for k, v in RULES}, "text": "none kept"},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print(E.group_by("err_cat").len().sort("len", descending=True))
    print(E.group_by("sys_cat").len().sort("len", descending=True))
    print(f"{n:,} turns, {E.height:,} error/system rows, {S.height:,} sessions; {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
