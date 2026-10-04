"""Dated step-change catalog: CHANGELOG scaffold entries (classified), NE rows, goal kickoffs, roster and room changes.

Moved from H56 (hypotheses/H56-ep-platform-fingerprint/scheme/build.py: build_days, parse_changelog, classify,
build_events; STANDARDS §8, 2026-10-04). Rules and hand exceptions are unchanged; H56's copy stays in place. H74 reads
the catalog as its evaluation set (plus its own undocumented dates, reproduced here by `evaluation_catalog`).

Classes: scaffold_tool, scaffold_family (family_target = the named lab), scaffold_prompt, goal_prompt, operator,
operator_schedule, infra_invisible, excluded (CHANGELOG, H56 card rules and hand lists); goal (kickoff = the goal's first
calendar day); roster (joins / leaves from period_step_changes, Claude Code agent dropped); room (structural room-set
changes); undocumented (NE40, undated). Entries on the same (day0, cls, family_target) are merged (refs kept).
day0 = the first calendar day on or after the entry's date.

Holdout: the catalog is metadata about dates and covers ALL days. `holdout0` flags events whose day0 is held out:
exploratory users filter `~holdout0` (H56's rule); confirm scripts select `holdout0`. No raw-table counts are made.

Outputs (data/processed/shared/, + an `event_catalog` entry in _provenance.json):
  event_catalog.parquet       day0, cls, family_target, refs, date, label (CHANGELOG entry text, <= 70 chars + tags; no
                              agent text), source, n_entries, holdout0, regime0, goal0, weekday0, aidx, nidx, ref, event_id
  event_catalog_days.parquet  every calendar day: pt_date, weekday, goal_no, regime, holdout, window_s, unit_id,
                              aidx (row in this table), nidx (row among non-holdout days; null when held out)
Functions: build_days(), build_events(days), evaluation_catalog(ec) (H74's events.parquet rule), UNDOC.

Usage: uv run python infra/shared/event_catalog.py            (build)
       uv run python infra/shared/event_catalog.py --verify   (compare with H56's event_catalog/days and H74's events)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT as SH, RAW, ROOT, holdout_mask, load_holdout, write_provenance  # noqa: E402

CHANGELOG = RAW / "CHANGELOG.md"
H56 = ROOT / "data/processed/H56-ep-platform-fingerprint"
H74 = ROOT / "data/processed/H74-change-detector"

# ----------------------------------------------------------------------------- changelog classification (H56 card)
# Hand exceptions (fixed before any EP; see the H56 card). Keys: (date, substring of the entry text).
# The 02-10 nudger entry is replaced by NE10 scored at the first observed nudge (H36 Amendment 0c).
DROP = [("2026-02-10", "auto-nudger")]
OPERATOR = [("2026-06-13", "auto-nudger"), ("2026-06-15", "auto-nudger"),
            ("2026-06-07", "whitelisted user"), ("2026-06-13", "Saturday-evening")]
SCHEDULE = [("2025-05-23", "start time"), ("2025-07-18", "start time"), ("2025-08-18", "timing"),
            ("2026-03-09", "daylight"), ("2026-06-07", "hours"), ("2026-06-15", "hours"), ("2026-06-29", "hours")]
INVISIBLE = [("2026-02-18", "PII redaction"), ("2026-05-25", "Tinker"), ("2025-12-02", "text-only"),
             ("2025-07-31", "user-timeout"), ("2025-04-14", "premoderation"), ("2026-03-16", "soft-delete")]
EXCLUDED = [("2026-01-08", "Claude Code")]
# Family-targeted entries (scored on the named lab's agents vs the rest)
FAMILY = [("2025-04-24", "Gemini", "Google"), ("2025-07-10", "Gemini", "Google"), ("2025-08-07", "Gemini", "Google"),
          ("2025-09-30", "Claude", "Anthropic"), ("2025-11-20", "Gemini", "Google"), ("2025-11-25", "Gemini", "Google"),
          ("2026-02-20", "Gemini", "Google"), ("2026-03-10", "GPT-5.4", "OpenAI:GPT-5.4"),
          ("2026-03-16", "GPT-5.4", "OpenAI:GPT-5.4"), ("2026-03-26", "Anthropic", "Anthropic"),
          ("2026-04-24", "DeepSeek", "DeepSeek"), ("2026-05-26", "[Temporary]", "Fine-tuned (Kimi)"),
          ("2026-06-02", "Anthropic", "Anthropic"), ("2026-06-03", "Anthropic", "Anthropic"),
          ("2026-07-02", "Anthropic", "Anthropic")]
OTHER_AS_TOOL = [("2026-06-29", "GitLab"), ("2026-04-14", "ordering")]
CLASS_RANK = {"scaffold_tool": 0, "scaffold_family": 1, "scaffold_prompt": 2, "goal_prompt": 3, "operator": 4,
              "operator_schedule": 5, "infra_invisible": 6, "excluded": 7}
# Undocumented dated changes used by H74 (scored after the blind run); dates from DQ9 and H56.
UNDOC = [("NE39", "2025-07-01", "public chat closed (DQ9)"), ("OUT0331", "2026-03-31", "history search returns near-empty answers (H56)"),
         ("NE40", "2026-04-20", "search oracle swap Gemini 2.5 Pro -> Sonnet 4.6 (H56)"),
         ("NE45", "2026-07-29", "search tool date fields int -> str (H56)"),
         ("NE43a", "2026-08-05", "daily pause/resume bookends stop (first day without)"),
         ("NE43b", "2026-08-21", "nudger off (first day without)")]


def parse_changelog():
    txt = CHANGELOG.read_text().split("## Scaffolding changes", 1)[1]
    cur, out = None, []
    for line in txt.splitlines():
        m = re.match(r"^## (\d{4}-\d{2}-\d{2})(.*)$", line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"^- \*\*\[([^\]]+)\]\*\*\s*(.*)$", line)
        if m and cur:
            out.append({"date": cur, "tags": m.group(1), "text": m.group(2)})
    return out


def classify(e):
    d, t, tags = e["date"], e["text"], e["tags"]
    hit = lambda lst: any(d == dd and s.lower() in t.lower() for dd, s in lst)  # noqa: E731
    if hit(EXCLUDED):
        return "excluded", None
    if hit(DROP):
        return "drop", None
    if hit(OPERATOR):
        return "operator", None
    if hit(SCHEDULE):
        return "operator_schedule", None
    if hit(INVISIBLE):
        return "infra_invisible", None
    for dd, s, fam in FAMILY:
        if d == dd and s.lower() in t.lower():
            return "scaffold_family", fam
    if hit(OTHER_AS_TOOL):
        return "scaffold_tool", None
    tg = set(re.split(r"[/ ]+", tags))
    if tg & {"Tools", "Memory", "Computer-use", "Human-use"}:
        return "scaffold_tool", None
    if "Prompt" in tg:
        return "scaffold_prompt", None
    if tg & {"Chat"}:
        return "scaffold_tool", None
    if tg <= {"Goals"}:
        return "goal_prompt", None
    if "Other" in tg:
        return "scaffold_tool", None
    return "scaffold_prompt", None


def build_days() -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "weekday", "goal_no", "regime", "holdout",
                                                          "window_s").sort("pt_date")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert all(a == b for a, b in zip(hm, cal["holdout"].to_list())), "calendar holdout flag disagrees with holdout_mask"
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "days").explode("days").rename({"days": "pt_date"})
    pu = pu.unique("pt_date", keep="first")
    cal = cal.join(pu, on="pt_date", how="left").with_row_index("aidx").with_columns(pl.col("aidx").cast(pl.Int32))
    nh = cal.filter(~pl.col("holdout")).with_row_index("nidx").select("pt_date", pl.col("nidx").cast(pl.Int32))
    return cal.join(nh, on="pt_date", how="left")


def build_events(days: pl.DataFrame) -> pl.DataFrame:
    dlist = days["pt_date"].to_list()

    def day0(date):
        for x in dlist:
            if x >= date:
                return x
        return None

    rows = []
    for e in parse_changelog():
        cls, fam = classify(e)
        if cls == "drop":
            continue
        ref = "NE14b" if e["date"] == "2026-03-24" else "CL:" + e["date"]
        rows.append({"ref": ref, "cls": cls, "family_target": fam, "date": e["date"], "source": "changelog",
                     "label": f"[{e['tags']}] " + e["text"][:70]})
    kick = pl.read_parquet(SH / "kicks_classified.parquet", columns=["kind", "pt_date"])
    first_nudge = kick.filter(pl.col("kind") == "nudge")["pt_date"].min()
    rows += [
        {"ref": "NE10", "cls": "operator", "family_target": None, "date": first_nudge, "source": "NE",
         "label": "auto-nudger on, scored at first observed nudge"},
        {"ref": "NE43", "cls": "operator", "family_target": None, "date": "2026-08-21", "source": "NE",
         "label": "automated speaker silent (nudger off); undocumented"},
        {"ref": "NE36", "cls": "operator", "family_target": None, "date": "2026-04-02", "source": "NE",
         "label": "operator corrects Year-1 total belief"},
        {"ref": "NE38", "cls": "operator", "family_target": None, "date": "2026-07-29", "source": "NE",
         "label": "human reassigns one agent's role"},
        {"ref": "NE35", "cls": "operator", "family_target": None, "date": "2026-02-25", "source": "NE",
         "label": "operator resets challenge format"},
        {"ref": "NE37", "cls": "operator", "family_target": None, "date": "2026-06-22", "source": "NE",
         "label": "village redirected to one agent"},
    ]
    g0 = days.group_by("goal_no").agg(pl.col("pt_date").min()).sort("goal_no")
    for g, d in g0.iter_rows():
        rows.append({"ref": f"#{g}", "cls": "goal", "family_target": None, "date": d, "source": "calendar",
                     "label": f"goal #{g} kickoff"})
    psc = pl.read_parquet(SH / "period_step_changes.parquet")
    for d, kind, src, what in psc.iter_rows():
        if kind in ("roster_join", "roster_leave"):
            if src == "Opus 4.5 (Claude Code)":
                continue
            rows.append({"ref": f"{kind.split('_')[1]}:{src}", "cls": "roster", "family_target": None,
                         "date": d, "source": "period_step_changes", "label": f"{src} {kind.split('_')[1]}s"})
        elif kind == "rooms":
            rows.append({"ref": f"rooms:{d}", "cls": "room", "family_target": None, "date": d,
                         "source": "period_step_changes", "label": what[:70]})
    rows.append({"ref": "NE40", "cls": "undocumented", "family_target": None, "date": None, "source": "NE",
                 "label": "history-search answerer swapped (undated)"})
    ev = pl.DataFrame(rows, schema={"ref": pl.Utf8, "cls": pl.Utf8, "family_target": pl.Utf8, "date": pl.Utf8,
                                    "source": pl.Utf8, "label": pl.Utf8})
    ev = ev.with_columns(pl.col("date").map_elements(lambda x: day0(x) if x else None, return_dtype=pl.Utf8).alias("day0"))
    ev = (ev.with_columns(pl.col("cls").replace_strict(CLASS_RANK, default=9).alias("rank"))
          .group_by("day0", "cls", "family_target", maintain_order=True)
          .agg(pl.col("ref").unique(maintain_order=True).alias("refs"), pl.col("date").min(),
               pl.col("label").first(), pl.col("source").first(), pl.len().alias("n_entries")))
    ev = ev.join(days.select(pl.col("pt_date").alias("day0"), pl.col("holdout").alias("holdout0"),
                             pl.col("regime").alias("regime0"), pl.col("goal_no").alias("goal0"),
                             pl.col("weekday").alias("weekday0"), "aidx", "nidx"), on="day0", how="left")
    ev = ev.with_columns(pl.col("refs").list.first().alias("ref")).sort("day0", "cls", nulls_last=True)
    return ev.with_row_index("event_id").with_columns(pl.col("event_id").cast(pl.Int32))


def evaluation_catalog(ec: pl.DataFrame) -> pl.DataFrame:
    """H74's events.parquet rule: drop infra_invisible / excluded / undocumented rows, add UNDOC dates; day0 = first
    active day (n_agent_events > 0, incl. held out) on or after the date; held0 = day0 is held out."""
    cal = pl.read_parquet(SH / "calendar.parquet")
    held = set(cal.filter(pl.col("holdout"))["pt_date"].to_list())
    ec = ec.filter(~pl.col("cls").is_in(["infra_invisible", "excluded", "undocumented"])).select(
        pl.col("event_id").cast(pl.String).alias("event"), "date", "cls", "label", "ref", "family_target")
    und = pl.DataFrame([{"event": e, "date": d, "cls": "undocumented", "label": lab, "ref": e, "family_target": None}
                        for e, d, lab in UNDOC], schema=ec.schema)
    ev = pl.concat([ec, und])
    all_days = cal.filter(pl.col("n_agent_events") > 0).sort("pt_date")["pt_date"].to_list()
    day0 = [next((x for x in all_days if x >= d), None) for d in ev["date"].to_list()]
    return ev.with_columns(pl.Series("day0", day0)).with_columns(pl.col("day0").is_in(list(held)).alias("held0"))


def main():
    days = build_days()
    ev = build_events(days)
    days.write_parquet(SH / "event_catalog_days.parquet", compression="zstd")
    ev.write_parquet(SH / "event_catalog.parquet", compression="zstd")
    by_cls = {k: int(v) for k, v in ev.group_by("cls").len().sort("cls").iter_rows()}
    write_provenance("event_catalog", ["raw/CHANGELOG.md", "calendar", "period_units", "period_step_changes",
                                       "kicks_classified (first nudge date)"],
                     {"rules": "H56 card 'Data scheme' (classes, hand lists DROP/OPERATOR/SCHEDULE/INVISIBLE/EXCLUDED/"
                               "FAMILY/OTHER_AS_TOOL); merge on (day0, cls, family_target)",
                      "holdout": "all days; holdout0 flags held-out day0 (filter ~holdout0 when exploring)",
                      "holdout_locked_at": load_holdout()["locked_at"],
                      "source": "hypotheses/H56-ep-platform-fingerprint/scheme/build.py (rules unchanged)",
                      "events_by_class": by_cls, "rows": ev.height})
    print(f"event_catalog.parquet: {ev.height} events; {json.dumps(by_cls)}", flush=True)


def verify() -> dict:
    """Recompute in memory and compare with H56's event_catalog.parquet / days.parquet and H74's events.parquet
    (read-only); also check that the shared files on disk equal the recomputation."""
    days = build_days()
    ev = build_events(days)
    res = {}
    for name, mine, path in (("H56 days", days, H56 / "days.parquet"), ("H56 event_catalog", ev, H56 / "event_catalog.parquet"),
                             ("shared days", days, SH / "event_catalog_days.parquet"),
                             ("shared event_catalog", ev, SH / "event_catalog.parquet")):
        if not path.exists():
            res[name] = "missing"
            continue
        old = pl.read_parquet(path)
        if old.equals(mine):
            res[name] = "identical"
        else:
            r = {"rows": [old.height, mine.height]}
            if old.columns == mine.columns and old.height == mine.height:
                r["columns_differ"] = [c for c in old.columns if not old[c].equals(mine[c])]
            else:
                r["column_sets"] = [old.columns, mine.columns]
            k = ["day0", "cls", "family_target"]
            if all(c in old.columns for c in k):
                j = old.select(k + ["refs"]).join(mine.select(k + ["refs"]), on=k, how="full", nulls_equal=True, suffix="_new")
                r["only_old"] = j.filter(pl.col("refs_new").is_null()).select(k + ["refs"]).to_dicts()[:10]
                r["only_new"] = j.filter(pl.col("refs").is_null()).select([c + "_new" for c in k] + ["refs_new"]).to_dicts()[:10]
            res[name] = r
    if (H74 / "events.parquet").exists():
        old = pl.read_parquet(H74 / "events.parquet")
        new = evaluation_catalog(pl.read_parquet(H56 / "event_catalog.parquet"))
        res["H74 events (from H56 catalog)"] = "identical" if old.equals(new) else {"rows": [old.height, new.height]}
        new2 = evaluation_catalog(ev)
        res["H74 events (from shared catalog)"] = "identical" if old.equals(new2) else {"rows": [old.height, new2.height]}
    res["ok"] = all(v == "identical" for k, v in res.items() if k != "ok")
    print(json.dumps(res, indent=1, default=str), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify()["ok"] else 1)
    main()
