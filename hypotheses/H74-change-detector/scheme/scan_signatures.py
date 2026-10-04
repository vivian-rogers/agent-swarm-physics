"""H74 scan: record signatures (field names + JSON value types) per day, and numeric search-answer format counts.

One pass over raw `events` and `computer_use_turns` (two processes). NUMBERS AND FIELD NAMES ONLY: no message text,
no tool output, no answer text is stored. Held-out days are dropped before writing (asserted).
Signature record types:
  ev:<actionType>  keys:types of events.data (excluding the provider-shaped `output`; nested dicts typed as 'dict')
  turn_action      keys:types of computer_use_turns.agent_action (null -> 'none')
  turn_env         null / non-null status of output, error, system, has_redaction_been_overruled
  turn_api         provider response shape: dict -> sorted top keys (+ usage / usageMetadata subkeys);
                   list -> sorted set of item (type, sorted keys)
Outputs (data/processed/H74-change-detector/): signatures_daily.parquet (pt_date, rtype, sig, n, n_agents, agents),
  signature_dict.parquet (sig -> rtype, field/type string), search_format.parquet (one row per search, numbers only).
Run: uv run python hypotheses/H74-change-detector/scheme/scan_signatures.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

import orjson  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

RAW = ROOT / "data/raw/ai-village"
OUT = ROOT / "data/processed/H74-change-detector"
PT = ZoneInfo("America/Los_Angeles")
UTC = dt.timezone.utc


def ptdate(s: str) -> str:
    return dt.datetime.fromisoformat(s).replace(tzinfo=UTC).astimezone(PT).date().isoformat()


def tname(v) -> str:
    if v is None:
        return "none"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "list"
    return "dict"


def keysig(d: dict, skip=()) -> str:
    return ",".join(f"{k}:{tname(v)}" for k, v in sorted(d.items()) if k not in skip)


def api_sig(am) -> str:
    if isinstance(am, dict):
        s = "dict[" + ",".join(sorted(am.keys())) + "]"
        for u in ("usage", "usageMetadata"):
            if isinstance(am.get(u), dict):
                s += f"|{u}[" + ",".join(sorted(am[u].keys())) + "]"
        return s
    if isinstance(am, list):
        items = sorted({(str(x.get("type")), ",".join(sorted(x.keys()))) if isinstance(x, dict) else (tname(x), "")
                        for x in am})
        return "list[" + ";".join(f"{a}({b})" for a, b in items) + "]"
    return tname(am)


def h(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:12]


LINE_BULLET = {"star3": re.compile(r"^\s*\*   "), "star": re.compile(r"^\s*\* "), "dash": re.compile(r"^\s*- "),
               "dot": re.compile(r"^\s*•"), "num": re.compile(r"^\s*\d+[.)]\s")}


def fmt(ans: str) -> dict:
    lines = ans.split("\n")
    head = ans.lstrip()[:40].lower()
    return {"f_chars": len(ans), "f_lines": len(lines), "f_blank": sum(1 for x in lines if not x.strip()),
            "f_h1": sum(1 for x in lines if x.startswith("# ")), "f_h2": sum(1 for x in lines if x.startswith("## ")),
            "f_h3": sum(1 for x in lines if x.startswith("### ")), "f_bold": ans.count("**") // 2,
            **{f"f_b_{k}": sum(1 for x in lines if r.match(x)) for k, r in LINE_BULLET.items()},
            "f_emdash": ans.count("—"), "f_endash": ans.count("–"),
            "f_nonascii": sum(1 for ch in ans if ord(ch) > 127) / max(len(ans), 1),
            "f_mean_line": len(ans) / max(len(lines), 1),
            # opening class: markdown header / bullet / "based on" / other (a category code, not text)
            "f_open": 1 if head.startswith("#") else 2 if head[:1] in "*-•" else 3 if head.startswith("based on") else 0}


def scan_events(agent_code):
    counts = defaultdict(lambda: defaultdict(int))
    sigs = {}
    search = []
    with gzip.open(RAW / "events.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            d = r.get("data") or {}
            at = d.get("actionType", "none")
            s = f"ev:{at}|" + keysig(d, skip=("output",))
            k = h(s)
            sigs[k] = ("ev:" + at, s)
            day = ptdate(r["created_at"])
            ag = agent_code.get(d.get("agentId") or d.get("speakerId"), -1)
            counts[(day, "ev:" + at, k)][ag] += 1
            if at == "SEARCH_HISTORY":
                search.append({"pt_date": day, "t": r["created_at"], "agent": ag, **fmt(d.get("answerToQuery") or "")})
    return dict((k, dict(v)) for k, v in counts.items()), sigs, search


def scan_turns(agent_code):
    sess = {}
    with gzip.open(RAW / "computer_use_sessions.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            sess[r["id"]] = agent_code.get(r.get("agent_id"), -1)
    counts = defaultdict(lambda: defaultdict(int))
    sigs = {}
    with gzip.open(RAW / "computer_use_turns.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            day = ptdate(r["created_at"])
            ag = sess.get(r.get("session_id"), -1)
            act = r.get("agent_action")
            parts = [("turn_action", "turn_action|" + (keysig(act) if isinstance(act, dict) else tname(act))),
                     ("turn_env", "turn_env|" + ",".join(f"{k}:{'null' if r.get(k) is None else tname(r.get(k))}"
                                                        for k in ("output", "error", "system", "has_redaction_been_overruled"))),
                     ("turn_api", "turn_api|" + api_sig(r.get("agent_messages")))]
            for rt, s in parts:
                k = h(s)
                sigs[k] = (rt, s)
                counts[(day, rt, k)][ag] += 1
    return dict((k, dict(v)) for k, v in counts.items()), sigs, []


def main(include_holdout: bool = False, out: Path | None = None):
    """include_holdout=True is for analysis/confirm.py only (guarded there); the default reproduces round 1."""
    OUT = out or globals()["OUT"]
    OUT.mkdir(parents=True, exist_ok=True)
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    code = dict(zip(roster["agent_id"].to_list(), roster["agent"].to_list()))
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet")
    goal_of = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    with ProcessPoolExecutor(2) as ex:
        fe, ft = ex.submit(scan_events, code), ex.submit(scan_turns, code)
        (ce, se, search), (ct, st, _) = fe.result(), ft.result()
    rows = []
    for counts in (ce, ct):
        for (day, rt, k), ags in counts.items():
            rows.append({"pt_date": day, "rtype": rt, "sig": k, "n": sum(ags.values()),
                         "n_agents": len([a for a in ags if a >= 0]), "agents": sorted(a for a in ags if a >= 0)})
    df = pl.DataFrame(rows, schema={"pt_date": pl.String, "rtype": pl.String, "sig": pl.String, "n": pl.Int64,
                                    "n_agents": pl.Int32, "agents": pl.List(pl.Int16)})
    hm = holdout_mask(df["pt_date"].to_list(), [goal_of.get(d, -1) if goal_of.get(d) is not None else -1 for d in df["pt_date"].to_list()])
    held = set(cal.filter(pl.col("holdout"))["pt_date"].to_list())
    if not include_holdout:
        df = df.filter(~pl.Series(hm))
        assert not set(df["pt_date"].unique().to_list()) & held
    df.sort("pt_date", "rtype", "sig").write_parquet(OUT / "signatures_daily.parquet", compression="zstd")
    sig_all = {**se, **st}
    used = set(df["sig"].unique().to_list())
    pl.DataFrame([{"sig": k, "rtype": v[0], "fields": v[1]} for k, v in sig_all.items() if k in used]).write_parquet(
        OUT / "signature_dict.parquet", compression="zstd")
    sf = pl.DataFrame(search, infer_schema_length=None)
    hm = holdout_mask(sf["pt_date"].to_list(), [goal_of.get(d, -1) if goal_of.get(d) is not None else -1 for d in sf["pt_date"].to_list()])
    if not include_holdout:
        sf = sf.filter(~pl.Series(hm))
        assert not set(sf["pt_date"].unique().to_list()) & held
    sf.write_parquet(OUT / "search_format.parquet", compression="zstd")
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["scan_signatures"] = {"built_by": "hypotheses/H74-change-detector/scheme/scan_signatures.py", "git_commit": git_commit(),
                               "inputs": [{"source": "ai-village", "revision": REVISION,
                                           "tables": ["raw/events", "raw/computer_use_turns", "raw/computer_use_sessions",
                                                      "shared/roster", "shared/calendar"]}],
                               "params": {"text_stored": False, "non_holdout_only": not include_holdout,
                                          "signature": "field names + JSON type names; provider response shape"},
                               "built_at": dt.datetime.now(UTC).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print(df.height, "signature-day rows;", len(used), "signatures;", sf.height, "searches")


if __name__ == "__main__":
    main()
