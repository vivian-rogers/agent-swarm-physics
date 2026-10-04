"""H84 scheme (shared with H87): one row per history search, numbers and repo ids only (no text stored).

One streaming pass over raw events.jsonl.gz, keeping SEARCH_HISTORY rows (substring prefilter, then actionType check).
Per search: t (UTC), pt_date, goal_no, agent (int8 code), event_index, ans_chars, query_chars, and the work_repos ids
named in the answer (ans_rids) and in the query (q_rids). Repo references are found with the shared artifact
canonicalizer (infra/shared/build_artifacts: refs_in_text + canon; 'org' names resolved by repo basename as there).
Held-out days are dropped at scan time (holdout_mask); `--held` (confirm.py only) keeps only held-out days.

Usage: uv run python hypotheses/H84-search-outage-memory-scramble/scheme/search_events.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

import orjson  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import PT, REVISION, git_commit, holdout_mask, parse_ts  # noqa: E402
from build_artifacts import GITLAB_SWITCH, canon, refs_in_text  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H84-search-outage-memory-scramble"
RAW = ROOT / "data/raw/ai-village/events.jsonl.gz"


def repo_index():
    wr = pl.read_parquet(SH / "work_repos.parquet", columns=["repo"]).sort("repo").with_row_index("rid")
    rid = dict(zip(wr["repo"].to_list(), wr["rid"].to_list()))
    by_base = defaultdict(list)
    for name in rid:
        by_base[name.split("/")[-1]].append(name)
    return rid, by_base


def rids_in(text: str, t: dt.datetime, rid: dict, by_base: dict) -> list[int]:
    out = set()
    if not text:
        return []
    for how, ref in refs_in_text(text):
        if how == "org":
            cands = by_base.get(ref.lower(), [])
            if len(cands) > 1:
                want = "gitlab.com" if t.astimezone(PT).date().isoformat() >= GITLAB_SWITCH else "github.com"
                cands = [c for c in cands if c.startswith(want)]
            if len(cands) == 1:
                out.add(rid[cands[0]])
            continue
        c = canon(ref)
        if c is None:
            continue
        kind, name, _host, parent = c
        repo = name if kind == "repo" else parent
        if repo is not None and repo in rid:
            out.add(rid[repo])
    return sorted(out)


def scan(held: bool = False) -> pl.DataFrame:
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "agent_id"])
    code = dict(zip(ros["agent_id"].to_list(), ros["agent"].to_list()))
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    goal_of = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    rid, by_base = repo_index()
    rows = []
    with gzip.open(RAW, "rb") as f:
        for line in f:
            if b'"SEARCH_HISTORY"' not in line:
                continue
            r = orjson.loads(line)
            d = r.get("data") or {}
            if d.get("actionType") != "SEARCH_HISTORY":
                continue
            t = parse_ts(r["created_at"])
            ptd = t.astimezone(PT).date().isoformat()
            ans = d.get("answerToQuery") or ""
            q = d.get("query") or ""
            rows.append({"t": t, "pt_date": ptd, "goal_no": goal_of.get(ptd), "agent": code.get(d.get("agentId")),
                         "event_index": r["event_index"], "ans_chars": len(ans), "query_chars": len(q),
                         "ans_rids": rids_in(ans, t, rid, by_base), "q_rids": rids_in(q, t, rid, by_base)})
    df = pl.DataFrame(rows, schema_overrides={"ans_rids": pl.List(pl.Int32), "q_rids": pl.List(pl.Int32)},
                      infer_schema_length=None)
    hm = pl.Series(holdout_mask(df["pt_date"].to_list(), [g if g is not None else -1 for g in df["goal_no"].to_list()]))
    df = df.filter(hm if held else ~hm).with_columns(pl.col("agent").cast(pl.Int8), pl.col("goal_no").cast(pl.Int8))
    return df.sort("t")


def main():
    held = "--held" in sys.argv
    df = scan(held)
    OUT.mkdir(parents=True, exist_ok=True)
    name = "search_events_confirm.parquet" if held else "search_events.parquet"
    df.write_parquet(OUT / name, compression="zstd")
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov[name] = {"built_by": "hypotheses/H84-search-outage-memory-scramble/scheme/search_events.py",
                  "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": REVISION,
                              "tables": ["raw/events (SEARCH_HISTORY rows)", "shared/work_repos", "shared/roster",
                                         "shared/calendar"]}],
                  "params": {"text_stored": False, "holdout": "kept only" if held else "dropped at scan",
                             "repo_resolution": "build_artifacts.refs_in_text + canon; org names by basename"},
                  "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    if not held:
        print(df.height, "non-holdout searches;", df.filter(pl.col("ans_rids").list.len() > 0).height,
              "answers name a work repo")


if __name__ == "__main__":
    main()
