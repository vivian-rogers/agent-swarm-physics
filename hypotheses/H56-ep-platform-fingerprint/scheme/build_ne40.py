"""H56 NE40 scheme: numeric features of history-search answers (the oracle's output), non-holdout days only.

The history-search answerer was swapped (Gemini 2.5 Pro -> Sonnet 4.6) on an undocumented date (NE40). This scan
reads raw `events` SEARCH_HISTORY rows and keeps NUMBERS ONLY (no text is stored): answer length, line count,
markdown structure counts, non-ASCII share, the tool's date-field schema (startDay vs startDate), query length,
and the event's token counts. Output: data/processed/H56-ep-platform-fingerprint/ne40_search_features.parquet
Run: OMP_NUM_THREADS=2 uv run python hypotheses/H56-ep-platform-fingerprint/scheme/build_ne40.py
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
from common import PT, REVISION, git_commit, holdout_mask, parse_ts  # noqa: E402

OUT = ROOT / "data/processed/H56-ep-platform-fingerprint"
RAW = ROOT / "data/raw/ai-village/events.jsonl.gz"


def feats(ans: str) -> dict:
    lines = ans.split("\n")
    return {"ans_chars": len(ans), "ans_lines": len(lines),
            "ans_md_head": sum(1 for x in lines if x.lstrip().startswith("#")),
            "ans_bold": ans.count("**") // 2,
            "ans_bullets": sum(1 for x in lines if re.match(r"^\s*[-*•]\s", x) is not None),
            "ans_numbered": sum(1 for x in lines if re.match(r"^\s*\d+[.)]\s", x) is not None),
            "ans_nonascii": sum(1 for ch in ans if ord(ch) > 127) / max(len(ans), 1),
            "ans_blank_lines": sum(1 for x in lines if not x.strip()),
            # stylometric markers (counts only): Gemini-style "*   " bullets vs "- " bullets, em dashes,
            # "Based on" openings, ##/### headers
            "m_star3_bullet": sum(1 for x in lines if x.startswith("*   ") or x.startswith("    *   ")),
            "m_dash_bullet": sum(1 for x in lines if x.lstrip().startswith("- ")),
            "m_emdash": ans.count("\u2014"),
            "m_based_on": int(ans.lstrip().lower().startswith("based on")),
            "m_hash_head": sum(1 for x in lines if x.startswith("## ") or x.startswith("### "))}


def main():
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    code = dict(zip(roster["agent_id"], roster["agent"]))
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet")
    goal_of = dict(zip(cal["pt_date"], cal["goal_no"]))
    rows = []
    with gzip.open(RAW, "rb") as f:
        for line in f:
            if b'"SEARCH_HISTORY"' not in line:
                continue
            r = orjson.loads(line)
            d = r["data"]
            if d.get("actionType") != "SEARCH_HISTORY":
                continue
            t = parse_ts(r["created_at"])
            ptd = t.astimezone(PT).date().isoformat()
            ans = d.get("answerToQuery") or ""
            rows.append({"t": t, "pt_date": ptd, "goal_no": goal_of.get(ptd), "agent": code.get(d.get("agentId")),
                         "event_index": r["event_index"], "schema_date": "startDate" in d, "schema_day": "startDay" in d,
                         "query_chars": len(d.get("query") or ""), "cost": d.get("cost"),
                         "in_tok": d.get("inputTokens"), "out_tok": d.get("outputTokens"), **feats(ans)})
    df = pl.DataFrame(rows, infer_schema_length=None)
    hm = holdout_mask(df["pt_date"].to_list(), [g if g is not None else -1 for g in df["goal_no"].to_list()])
    df = df.with_columns(pl.Series("holdout", hm)).filter(~pl.col("holdout")).drop("holdout").sort("t")
    df.write_parquet(OUT / "ne40_search_features.parquet", compression="zstd")
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["ne40_search_features"] = {
        "built_by": "hypotheses/H56-ep-platform-fingerprint/scheme/build_ne40.py", "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION, "tables": ["raw/events (SEARCH_HISTORY rows)",
                                                                              "shared/roster", "shared/calendar"]}],
        "params": {"text_stored": False, "non_holdout_only": True},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print(df.height, "non-holdout search events")


if __name__ == "__main__":
    main()
