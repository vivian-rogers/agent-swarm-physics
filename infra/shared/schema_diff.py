"""Schema-diff platform monitor: record signatures (field names + JSON value types) per day from the raw logs, and the
daily count of new and retired signatures. The cheapest precise platform-change detector found so far (H74 channel S).

Moved from H74 (hypotheses/H74-change-detector/scheme/scan_signatures.py for the scan; analysis/h74lib.py: score_S for
the diff; STANDARDS §8, 2026-10-04). Rules unchanged; H74's copies stay in place.

Scan (one pass over raw `events` and `computer_use_turns`, 2 processes). NUMBERS AND FIELD NAMES ONLY: no message text,
no tool output and no answer text is stored. Signature record types:
  ev:<actionType>  keys:types of events.data (excluding the provider-shaped `output`; nested dicts typed as 'dict')
  turn_action      keys:types of computer_use_turns.agent_action (null -> 'none')
  turn_env         null / non-null status of output, error, system, has_redaction_been_overruled
  turn_api         provider response shape: dict -> sorted top keys (+ usage / usageMetadata subkeys);
                   list -> sorted set of item (type, sorted keys)
Search-answer format counts (one row per SEARCH_HISTORY event; counts and category codes only).

Diff (per active day, against the days before it; H74 card rule, B = 10):
  new      a signature first seen today (not day 1), with >= 5 records and either no agent or >= 2 agents of which
           >= 2 are not newcomers (an agent's first 3 active days);
  retired  a signature absent today that held >= 2% of its family's records and had >= 2 agents (or none) over the
           previous B days, with >= 10 records expected today and >= 2 of its baseline agents active today; only the
           first day of a retirement counts.
  z_S = 4 (n_new + n_gone) (H74's channel score; alarm at 4).

Holdout: held-out days are dropped before writing (asserted), as H74. `--include-holdout` (confirm scripts only) needs
`--i-understand-this-uses-the-locked-holdout` and an `--out` folder outside data/processed/shared/.

Outputs (data/processed/shared/schema_diff/, + _provenance.json):
  signatures_daily.parquet  pt_date, rtype, sig (12-hex hash), n, n_agents, agents (agent codes)
  signature_dict.parquet    sig -> rtype, fields (the field:type string)
  search_format.parquet     pt_date, t, agent, f_* format counts
  schema_diff_daily.parquet pt_date, n_new, n_gone, z_S, detail ("new:<fields>;gone:<fields>", field names only)

Usage: uv run python infra/shared/schema_diff.py               scan (~raw pass) + diff
       uv run python infra/shared/schema_diff.py --diff-only   recompute the diff from the stored scan
       uv run python infra/shared/schema_diff.py --verify      compare with H74's scan outputs and channel-S scores
Functions: scan(include_holdout), diff_daily(sigs, days, newcomer), newcomers(days), active_days().
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from collections import defaultdict  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import orjson  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT as SH, PT, RAW, REVISION, ROOT, UTC, git_commit, holdout_mask  # noqa: E402

OUT = SH / "schema_diff"
H74 = ROOT / "data/processed/H74-change-detector"
B = 10                 # baseline days for retirements (H74 card)
CLAUDE_CODE = 19
ACK = "--i-understand-this-uses-the-locked-holdout"


# ----------------------------------------------------------------------------- scan (H74 scan_signatures.py)
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


def scan(include_holdout: bool = False, out: Path | None = None) -> dict:
    """H74 scan_signatures.main. Writes signatures_daily, signature_dict and search_format to `out` (default OUT)."""
    out = out or OUT
    out.mkdir(parents=True, exist_ok=True)
    roster = pl.read_parquet(SH / "roster.parquet")
    code = dict(zip(roster["agent_id"].to_list(), roster["agent"].to_list()))
    cal = pl.read_parquet(SH / "calendar.parquet")
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
    df.sort("pt_date", "rtype", "sig").write_parquet(out / "signatures_daily.parquet", compression="zstd")
    sig_all = {**se, **st}
    used = set(df["sig"].unique().to_list())
    pl.DataFrame([{"sig": k, "rtype": v[0], "fields": v[1]} for k, v in sig_all.items() if k in used]).write_parquet(
        out / "signature_dict.parquet", compression="zstd")
    sf = pl.DataFrame(search, infer_schema_length=None)
    hm = holdout_mask(sf["pt_date"].to_list(), [goal_of.get(d, -1) if goal_of.get(d) is not None else -1 for d in sf["pt_date"].to_list()])
    if not include_holdout:
        sf = sf.filter(~pl.Series(hm))
        assert not set(sf["pt_date"].unique().to_list()) & held
    sf.write_parquet(out / "search_format.parquet", compression="zstd")
    return {"signature_day_rows": df.height, "signatures": len(used), "searches": sf.height}


# ----------------------------------------------------------------------------- diff (H74 h74lib.score_S)
def active_days(include_holdout: bool = False) -> list[str]:
    """H74's day set: calendar days with agent events (non-holdout unless include_holdout), in time order."""
    cal = pl.read_parquet(SH / "calendar.parquet")
    c = cal.filter((pl.lit(include_holdout) | ~pl.col("holdout")) & (pl.col("n_agent_events") > 0)).sort("pt_date")
    return c["pt_date"].to_list()


def newcomers(days: list[str], include_holdout: bool = False) -> dict[tuple[int, str], bool]:
    """(agent, pt_date) -> True on an agent's first 3 days with ledger calls among `days` (Claude Code agent excluded);
    H74's rule (agent_day_features rows)."""
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.lit(include_holdout) | ~pl.col("holdout")) & (pl.col("agent") != CLAUDE_CODE))
          .select("agent", "pt_date").unique().collect().filter(pl.col("pt_date").is_in(days)))
    first = cw.group_by("agent").agg(pl.col("pt_date").sort().head(3).alias("f3"))
    return {(a, d): True for a, f3 in first.iter_rows() for d in f3}


def diff_daily(sigs: pl.DataFrame, days: list[str], newcomer: dict[tuple[int, str], bool] | None = None):
    """Platform-wide signature changes per day: new (never seen on an earlier day; >= 5 records; >= 2 agents not all
    newcomers, or agentless) and retired (>= 2% of its family and >= 2 agents in the previous B days, expected >= 10
    today, zero today, at least 2 of its baseline agents active today). Returns (z_S, {new, gone, detail})."""
    T = len(days)
    pos = {d: i for i, d in enumerate(days)}
    s = sigs.filter(pl.col("pt_date").is_in(days)).with_columns(
        pl.col("rtype").str.split(":").list.first().alias("fam"),
        pl.col("pt_date").replace_strict(pos, return_dtype=pl.Int32).alias("t"))
    fam_tot = s.group_by("t", "fam").agg(pl.col("n").sum().alias("tot"))
    tot = {(t, f): n for t, f, n in fam_tot.iter_rows()}
    by_sig = {}
    for (sig,), g in s.group_by("sig"):
        by_sig[sig] = {t: (n, ag, fam) for t, n, ag, fam in zip(g["t"].to_list(), g["n"].to_list(), g["agents"].to_list(),
                                                                g["fam"].to_list())}
    active = {}
    for (t, ag) in s.select("t", "agents").explode("agents").drop_nulls().unique().iter_rows():
        active.setdefault(t, set()).add(ag)
    new = np.zeros(T, int)
    gone = np.zeros(T, int)
    detail = [[] for _ in range(T)]
    for sig, rec in by_sig.items():
        ts = sorted(rec)
        first = ts[0]
        n0, ag0, fam = rec[first]
        agents = [a for a in ag0 if a >= 0]
        nonnew = [a for a in agents if not (newcomer or {}).get((a, days[first]), False)]
        if first > 0 and n0 >= 5 and (len(agents) == 0 or (len(agents) >= 2 and len(nonnew) >= 2)):
            new[first] += 1
            detail[first].append(("new", sig))
        for t in range(1, T):
            if t in rec:
                continue
            base = [u for u in range(max(0, t - B), t)]
            nb = sum(rec[u][0] for u in base if u in rec)
            if nb == 0:
                continue
            ftot = sum(tot.get((u, fam), 0) for u in base)
            share = nb / max(ftot, 1)
            bag = set(a for u in base if u in rec for a in rec[u][1] if a >= 0)
            exp_today = share * tot.get((t, fam), 0)
            if share >= 0.02 and (len(bag) >= 2 or not bag) and exp_today >= 10 and \
                    (not bag or len(bag & active.get(t, set())) >= 2):
                if (t - 1) in rec:   # only the first day of a retirement counts
                    gone[t] += 1
                    detail[t].append(("gone", sig))
    return 4.0 * (new + gone), {"new": new, "gone": gone, "detail": detail}


def diff_table(src: Path | None = None, include_holdout: bool = False) -> pl.DataFrame:
    src = src or OUT
    sigs = pl.read_parquet(src / "signatures_daily.parquet")
    days = active_days(include_holdout)
    z, info = diff_daily(sigs, days, newcomers(days, include_holdout))
    sdict = dict(pl.read_parquet(src / "signature_dict.parquet").select("sig", "fields").iter_rows())
    return pl.DataFrame({"pt_date": days, "n_new": info["new"].astype(np.int32), "n_gone": info["gone"].astype(np.int32),
                         "z_S": z.astype(float),
                         # sorted: diff_daily visits signatures in group_by order, which is not deterministic
                         "detail": [";".join(sorted(f"{k}:{sdict.get(s, s)[:90]}" for k, s in d)) for d in info["detail"]]})


def write_prov(out: Path, include_holdout: bool, summary: dict):
    prov = {"built_by": "infra/shared/schema_diff.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["raw/events", "raw/computer_use_turns", "raw/computer_use_sessions",
                                   "shared/roster", "shared/calendar", "shared/call_windows (newcomer days)"]}],
            "params": {"text_stored": False, "non_holdout_only": not include_holdout, "baseline_days": B,
                       "signature": "field names + JSON type names; provider response shape",
                       "source": "hypotheses/H74-change-detector/scheme/scan_signatures.py + analysis/h74lib.py:score_S "
                                 "(rules unchanged)", "summary": summary},
            "built_at": dt.datetime.now(UTC).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))


def verify() -> dict:
    res = {}
    for f in ("signatures_daily", "signature_dict", "search_format"):
        a, b = H74 / f"{f}.parquet", OUT / f"{f}.parquet"
        if not (a.exists() and b.exists()):
            res[f] = "missing"
            continue
        x, y = pl.read_parquet(a), pl.read_parquet(b)
        if f == "signature_dict":   # row order follows dict insertion; compare as sets
            x, y = x.sort("sig"), y.sort("sig")
        res[f] = "identical" if x.equals(y) else {"rows": [x.height, y.height]}
    sc = pl.read_parquet(H74 / "scores.parquet").select("pt_date", "s_new", "s_gone", "z_S")
    for name, src in (("diff vs H74 scores (H74 scan)", H74), ("diff vs H74 scores (shared scan)", OUT)):
        if not (src / "signatures_daily.parquet").exists():
            res[name] = "missing"
            continue
        d = diff_table(src).select("pt_date", pl.col("n_new").cast(pl.Int64).alias("s_new2"),
                                   pl.col("n_gone").cast(pl.Int64).alias("s_gone2"), pl.col("z_S").alias("z_S2"))
        j = sc.join(d, on="pt_date", how="full", coalesce=True)
        bad = j.filter((pl.col("s_new") != pl.col("s_new2")) | (pl.col("s_gone") != pl.col("s_gone2"))
                       | (pl.col("z_S") != pl.col("z_S2")) | pl.col("s_new").is_null() | pl.col("s_new2").is_null())
        res[name] = "identical" if bad.height == 0 else {"days_differ": bad.height, "head": bad.head(5).to_dicts()}
    if (OUT / "schema_diff_daily.parquet").exists():
        on_disk = pl.read_parquet(OUT / "schema_diff_daily.parquet")
        res["schema_diff_daily on disk vs recompute"] = "identical" if on_disk.equals(diff_table(OUT)) else "differ"
    res["ok"] = all(v == "identical" for k, v in res.items())
    print(json.dumps(res, indent=1, default=str), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--diff-only", action="store_true")
    ap.add_argument("--include-holdout", action="store_true")
    ap.add_argument(ACK, dest="ack", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.verify:
        sys.exit(0 if verify()["ok"] else 1)
    out = OUT
    if a.include_holdout:
        if not a.ack or not a.out:
            sys.exit(f"refusing: --include-holdout needs {ACK} and --out (confirm scripts only)")
        out = Path(a.out).resolve()
        if out == SH.resolve() or SH.resolve() in out.parents:
            sys.exit("refusing: held-out rows may not be written under data/processed/shared/")
    out.mkdir(parents=True, exist_ok=True)
    if a.diff_only:   # keep the scan summary of the stored scan
        pp = out / "_provenance.json"
        summary = json.loads(pp.read_text())["params"].get("summary", {}) if pp.exists() else {}
    else:
        summary = scan(a.include_holdout, out)
    d = diff_table(out, a.include_holdout)
    d.write_parquet(out / "schema_diff_daily.parquet", compression="zstd")
    summary.update({"days": d.height, "days_new": int((d["n_new"] > 0).sum()), "days_gone": int((d["n_gone"] > 0).sum())})
    write_prov(out, a.include_holdout, summary)
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
