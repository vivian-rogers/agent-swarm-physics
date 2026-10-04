"""History-search rows: one row per SEARCH_HISTORY event, numbers and repo ids only (no text stored).

Moved from H84 (`scheme/search_events.py`, also read as data by H87) and H56 (`scheme/build_ne40.py`, NE40 answer
features); round-3 consolidation, STANDARDS §8, 2026-10-04. One streaming pass over raw events.jsonl.gz (substring
prefilter, then actionType check) gives the union of both tables' columns; the rules are unchanged and the hypothesis
copies stay in place. (H74's `search_format` counts in `schema_diff.py` are a third, already shared, search scan.)

Columns:
  t (UTC), pt_date, goal_no (Int8), agent (Int8 roster code), event_index
  query_chars, ans_chars, ans_rids / q_rids (work_repos row ids named in the answer / query: build_artifacts.refs_in_text
    + canon; 'org' names resolved by repo basename, the GitLab switch date breaking basename ties)           [H84]
  schema_date / schema_day (the tool's date field), cost, in_tok, out_tok, ans_lines, ans_md_head, ans_bold,
    ans_bullets, ans_numbered, ans_nonascii, ans_blank_lines, m_star3_bullet, m_dash_bullet, m_emdash, m_based_on,
    m_hash_head                                                                                             [H56 NE40]
  holdout (holdout_mask of (pt_date, goal_no or -1); always False in the default build)
Repo ids are `work_repos` rows sorted by repo name (the ids H70, H84 and H87 use; `repo_index()`).

Holdout. Default: held-out rows (common.holdout_mask, as H84 and H56) are dropped in the scan loop before any field is
parsed. `include_holdout=True` (CLI `--include-holdout`) admits the held-out rows of an explicit date range only, for
frozen confirm scripts behind their own guard (holdout_ledger.check, Vivian's sign-off): the CLI refuses it without
`--i-understand-this-uses-the-locked-holdout`, `--dates START END_EXCL` and an `--out` folder outside
data/processed/shared/. `--only-holdout` keeps only held-out rows in the range (H84 `search_events.py --held` is
`--dates 2025-01-01 2027-01-01 --only-holdout`). This replaces the H84 `--held` file that H84's and H87's confirm.py
expect (`search_events_confirm.parquet`).

Helpers: `h84_view(df)` and `h56_view(df)` give the two source tables exactly; `map_to_calls(se, calls)` is the
search -> ledger call rule of H84 and H87 (latest call of the agent with t_first <= t, kept if t <= t_log + 1 s).

Usage: uv run python infra/shared/search_events.py              (build data/processed/shared/search_events.parquet)
       uv run python infra/shared/search_events.py --verify     (vs H84's and H56's tables; plus the include_holdout
                                                                 path on a non-holdout stand-in range)
       uv run python infra/shared/search_events.py --include-holdout --i-understand-this-uses-the-locked-holdout \
              --dates 2026-06-01 2026-07-07 --out <confirm folder> [--only-holdout]          (confirm scripts only)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

import orjson  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import OUT as SH, PT, REVISION, ROOT, git_commit, holdout_mask, parse_ts  # noqa: E402
from build_artifacts import GITLAB_SWITCH, canon, refs_in_text  # noqa: E402

RAW = ROOT / "data/raw/ai-village/events.jsonl.gz"
OUT = SH / "search_events.parquet"
ACK = "--i-understand-this-uses-the-locked-holdout"
H84_COLS = ["t", "pt_date", "goal_no", "agent", "event_index", "ans_chars", "query_chars", "ans_rids", "q_rids"]
H56_COLS = ["t", "pt_date", "goal_no", "agent", "event_index", "schema_date", "schema_day", "query_chars", "cost",
            "in_tok", "out_tok", "ans_chars", "ans_lines", "ans_md_head", "ans_bold", "ans_bullets", "ans_numbered",
            "ans_nonascii", "ans_blank_lines", "m_star3_bullet", "m_dash_bullet", "m_emdash", "m_based_on",
            "m_hash_head"]


# ---------------------------------------------------------------------------------------------- repo ids (H84)
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


# ---------------------------------------------------------------------------------------------- answer features (H56)
def feats(ans: str) -> dict:
    lines = ans.split("\n")
    return {"ans_lines": len(lines),
            "ans_md_head": sum(1 for x in lines if x.lstrip().startswith("#")),
            "ans_bold": ans.count("**") // 2,
            "ans_bullets": sum(1 for x in lines if re.match(r"^\s*[-*•]\s", x) is not None),
            "ans_numbered": sum(1 for x in lines if re.match(r"^\s*\d+[.)]\s", x) is not None),
            "ans_nonascii": sum(1 for ch in ans if ord(ch) > 127) / max(len(ans), 1),
            "ans_blank_lines": sum(1 for x in lines if not x.strip()),
            "m_star3_bullet": sum(1 for x in lines if x.startswith("*   ") or x.startswith("    *   ")),
            "m_dash_bullet": sum(1 for x in lines if x.lstrip().startswith("- ")),
            "m_emdash": ans.count("—"),
            "m_based_on": int(ans.lstrip().lower().startswith("based on")),
            "m_hash_head": sum(1 for x in lines if x.startswith("## ") or x.startswith("### "))}


# ---------------------------------------------------------------------------------------------- scan
def scan(include_holdout: bool = False, dates: tuple[str, str] | None = None, only_holdout: bool = False,
         raw: Path = RAW) -> pl.DataFrame:
    """One raw pass. Default: non-holdout rows of every day. include_holdout=True needs an explicit [start, end) date
    range and keeps the rows inside it (held-out and not; only the held-out ones with only_holdout=True)."""
    if include_holdout:
        assert dates is not None, "include_holdout needs an explicit date range"
    else:
        assert not only_holdout, "only_holdout needs include_holdout"
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "agent_id"])
    code = dict(zip(ros["agent_id"].to_list(), ros["agent"].to_list()))
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    goal_of = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    rid, by_base = repo_index()
    held_cache: dict = {}

    def held(ptd: str, g) -> bool:
        k = (ptd, g)
        if k not in held_cache:
            held_cache[k] = bool(holdout_mask([ptd], [g if g is not None else -1])[0])
        return held_cache[k]

    rows = []
    with gzip.open(raw, "rb") as f:
        for line in f:
            if b'"SEARCH_HISTORY"' not in line:
                continue
            r = orjson.loads(line)
            d = r.get("data") or {}
            if d.get("actionType") != "SEARCH_HISTORY":
                continue
            t = parse_ts(r["created_at"])
            ptd = t.astimezone(PT).date().isoformat()
            g = goal_of.get(ptd)
            h = held(ptd, g)
            if include_holdout:
                if not (dates[0] <= ptd < dates[1]) or (only_holdout and not h):
                    continue
            elif h:
                continue
            ans = d.get("answerToQuery") or ""
            q = d.get("query") or ""
            rows.append({"t": t, "pt_date": ptd, "goal_no": g, "agent": code.get(d.get("agentId")),
                         "event_index": r["event_index"], "ans_chars": len(ans), "query_chars": len(q),
                         "ans_rids": rids_in(ans, t, rid, by_base), "q_rids": rids_in(q, t, rid, by_base),
                         "schema_date": "startDate" in d, "schema_day": "startDay" in d, "cost": d.get("cost"),
                         "in_tok": d.get("inputTokens"), "out_tok": d.get("outputTokens"), **feats(ans),
                         "holdout": h})
    df = pl.DataFrame(rows, schema_overrides={"ans_rids": pl.List(pl.Int32), "q_rids": pl.List(pl.Int32)},
                      infer_schema_length=None)
    df = df.with_columns(pl.col("agent").cast(pl.Int8), pl.col("goal_no").cast(pl.Int8))
    return df.sort("t")


def h84_view(df: pl.DataFrame) -> pl.DataFrame:
    """H84 search_events.parquet (and search_events_confirm.parquet when df came from an --only-holdout build)."""
    return df.select(H84_COLS)


def h56_view(df: pl.DataFrame) -> pl.DataFrame:
    """H56 ne40_search_features.parquet (goal_no and agent as Int64, as H56 wrote them)."""
    return df.select(H56_COLS).with_columns(pl.col("goal_no").cast(pl.Int64), pl.col("agent").cast(pl.Int64))


def map_to_calls(se: pl.DataFrame, calls: pl.DataFrame) -> pl.DataFrame:
    """H84/H87 rule: each search goes to the agent's latest ledger call with t_first <= t, kept if t <= t_log + 1 s.
    calls needs g, agent, t_first, t_log. Returns the mapped searches (sorted by t) with g, t_first, t_log."""
    keys_first = calls.select("g", "agent", "t_first", "t_log").sort("t_first")
    s = se.sort("t").join_asof(keys_first, left_on="t", right_on="t_first", by="agent", strategy="backward",
                               check_sortedness=False)
    return s.filter(pl.col("g").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1)))


# ---------------------------------------------------------------------------------------------- write / verify
def write(df: pl.DataFrame, path: Path, include_holdout: bool, extra: dict | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path, compression="zstd")
    prov = {"built_by": "infra/shared/search_events.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["raw/events (SEARCH_HISTORY rows)", "shared/work_repos", "shared/roster",
                                   "shared/calendar"]}],
            "params": {"text_stored": False, "rows": df.height,
                       "holdout": ("INCLUDED in the listed range (confirm build)" if include_holdout
                                   else "dropped at scan (holdout_mask)"),
                       "repo_resolution": "build_artifacts.refs_in_text + canon; org names by basename",
                       "source": "H84 scheme/search_events.py + H56 scheme/build_ne40.py (rules unchanged)",
                       **(extra or {})},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pp = path.parent / "_provenance.json"
    old = json.loads(pp.read_text()) if pp.exists() else {}
    old[path.stem] = prov
    pp.write_text(json.dumps(old, indent=1))


def _cmp(a: pl.DataFrame, b: pl.DataFrame) -> str:
    if a.columns != b.columns:
        return f"columns differ: {set(a.columns) ^ set(b.columns)}"
    if a.schema != b.schema:
        return f"dtypes differ: {[(c, a.schema[c], b.schema[c]) for c in a.columns if a.schema[c] != b.schema[c]]}"
    if a.equals(b):
        return "identical"
    if a.height != b.height:
        return f"rows {a.height} vs {b.height}"
    return f"same rows; columns differ: {[c for c in a.columns if not a[c].equals(b[c])]}"


def verify(standin: tuple[str, str] = ("2026-04-02", "2026-05-23")) -> dict:
    """(1) The default scan vs H84's search_events.parquet and H56's ne40_search_features.parquet (read-only).
    (2) The include_holdout path on a stand-in range with no held-out day reproduces the default rows of that range."""
    res, ok = {}, True
    df = scan()
    res["rows"] = df.height
    for name, view, p in (("H84", h84_view, ROOT / "data/processed/H84-search-outage-memory-scramble/search_events.parquet"),
                          ("H56", h56_view, ROOT / "data/processed/H56-ep-platform-fingerprint/ne40_search_features.parquet")):
        if p.exists():
            r = _cmp(pl.read_parquet(p), view(df))
            res[name] = r
            ok &= r == "identical"
        else:
            res[name] = "source table absent"
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    c = cal.filter(pl.col("pt_date").is_between(pl.lit(standin[0]), pl.lit(standin[1]), closed="left"))
    assert not any(holdout_mask(c["pt_date"].to_list(), c["goal_no"].fill_null(-1).to_list())), \
        "stand-in range contains a held-out day"
    alt = scan(include_holdout=True, dates=standin)
    ref = df.filter(pl.col("pt_date").is_between(pl.lit(standin[0]), pl.lit(standin[1]), closed="left"))
    r = _cmp(ref, alt)
    res[f"include_holdout_path_on_{standin[0]}_{standin[1]}"] = f"{r} ({alt.height} rows)"
    ok &= r == "identical"
    res["ok"] = bool(ok)
    print(json.dumps(res, indent=1), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--include-holdout", action="store_true", help="confirm scripts only (see docstring)")
    ap.add_argument(ACK, dest="ack", action="store_true")
    ap.add_argument("--dates", nargs=2, metavar=("START", "END_EXCL"))
    ap.add_argument("--only-holdout", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.verify:
        sys.exit(0 if verify()["ok"] else 1)
    if a.include_holdout:
        if not a.ack or not a.dates or not a.out:
            sys.exit(f"refusing: --include-holdout needs {ACK}, --dates and --out (confirm scripts only)")
        out = Path(a.out).resolve()
        if out == SH.resolve() or SH.resolve() in out.parents:
            sys.exit("refusing: held-out rows may not be written under data/processed/shared/")
        df = scan(include_holdout=True, dates=tuple(a.dates), only_holdout=a.only_holdout)
        write(df, out / "search_events.parquet", True, {"dates": a.dates, "only_holdout": a.only_holdout})
        print(df.height, "search rows ->", out)
        return
    if a.only_holdout or a.dates:
        sys.exit("refusing: --dates / --only-holdout only go with --include-holdout")
    df = scan()
    write(df, OUT, False)
    print(df.height, "non-holdout searches;", df.filter(pl.col("ans_rids").list.len() > 0).height,
          "answers name a work repo")


if __name__ == "__main__":
    main()
