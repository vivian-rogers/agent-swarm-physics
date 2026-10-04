"""H56 scheme: build data/processed/H56-ep-platform-fingerprint/ from shared tables (non-holdout rows only).

Outputs (no text):
  days.parquet           every calendar (active) day: index, weekday, regime, goal, unit, holdout
  event_catalog.parquet  dated step changes with class (rules in the card, "Data scheme"); all days, holdout flagged
  counts.parquet         transition counts per agent x non-holdout day x within-day quarter x variant x (a, b)
  agent_days.parquet     per agent x day x variant: records, transitions, span hours
  _provenance.json

Variants (card): 0 act_all, 1 act_agent, 2 coarse_all, 3 coarse_agent.
Run: OMP_NUM_THREADS=2 POLARS_MAX_THREADS=2 uv run python hypotheses/H56-ep-platform-fingerprint/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H56-ep-platform-fingerprint"
CHANGELOG = ROOT / "data/raw/ai-village/CHANGELOG.md"

VARIANTS = ["act_all", "act_agent", "coarse_all", "coarse_agent", "act_agent_b3", "coarse_agent_b3"]
Q = {"act_all": 11, "act_agent": 11, "coarse_all": 6, "coarse_agent": 6, "act_agent_b3": 11, "coarse_agent_b3": 6}
BURN = 3   # Amendment 1 (synthetic-only basis): drop the first 3 transitions of every agent-only segment
AGENT_ACTS = [0, 1, 2, 3, 4, 5, 6]          # shell click scroll look type chat idle
AGENT_COARSE = [0, 1, 2, 3, 4]              # browse type shell chat idle
INFRA_ERR = ["timeout", "vm", "resource", "network"]
SCAFFOLD_GAPS = ["after_summary", "marker", "session_start", "first_of_day"]
CLAUDE_CODE_AGENT = 19

# ----------------------------------------------------------------------------- changelog classification
# Hand exceptions (fixed before any EP; see card). Keys: (date, substring of the entry text).
# The 02-10 nudger entry is replaced by NE10 scored at the first observed nudge (H36 Amendment 0c).
DROP = [("2026-02-10", "auto-nudger")]
OPERATOR = [ ("2026-06-13", "auto-nudger"), ("2026-06-15", "auto-nudger"),
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


# ----------------------------------------------------------------------------- days
def build_days():
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "weekday", "goal_no", "regime", "holdout",
                                                          "window_s").sort("pt_date")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert all(a == b for a, b in zip(hm, cal["holdout"].to_list())), "calendar holdout flag disagrees with holdout_mask"
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "days").explode("days").rename({"days": "pt_date"})
    pu = pu.unique("pt_date", keep="first")
    cal = cal.join(pu, on="pt_date", how="left").with_row_index("aidx").with_columns(pl.col("aidx").cast(pl.Int32))
    nh = cal.filter(~pl.col("holdout")).with_row_index("nidx").select("pt_date", pl.col("nidx").cast(pl.Int32))
    return cal.join(nh, on="pt_date", how="left")


# ----------------------------------------------------------------------------- events
def build_events(days):
    roster = pl.read_parquet(SH / "roster.parquet")
    lab_of = dict(zip(roster["name"], roster["lab"]))
    dlist = days["pt_date"].to_list()

    def day0(date):
        for x in dlist:
            if x >= date:
                return x
        return None

    rows = []
    # changelog
    for e in parse_changelog():
        cls, fam = classify(e)
        if cls == "drop":
            continue
        if e["date"] == "2026-03-24":
            ref = "NE14b"
        else:
            ref = "CL:" + e["date"]
        rows.append({"ref": ref, "cls": cls, "family_target": fam, "date": e["date"], "source": "changelog",
                     "label": f"[{e['tags']}] " + e["text"][:70]})
    # NE catalog rows not in the changelog (or re-scored)
    kick = pl.read_parquet(SH / "kicks_classified.parquet")
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
    # goal kickoffs
    g0 = days.group_by("goal_no").agg(pl.col("pt_date").min()).sort("goal_no")
    for g, d in g0.iter_rows():
        rows.append({"ref": f"#{g}", "cls": "goal", "family_target": None, "date": d, "source": "calendar",
                     "label": f"goal #{g} kickoff"})
    # roster and rooms from period_step_changes
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
    # merge same (day0, cls, family_target): keep refs and labels
    ev = (ev.with_columns(pl.col("cls").replace_strict(CLASS_RANK, default=9).alias("rank"))
          .group_by("day0", "cls", "family_target", maintain_order=True)
          .agg(pl.col("ref").unique(maintain_order=True).alias("refs"), pl.col("date").min(),
               pl.col("label").first(), pl.col("source").first(), pl.len().alias("n_entries")))
    ev = ev.join(days.select(pl.col("pt_date").alias("day0"), pl.col("holdout").alias("holdout0"),
                             pl.col("regime").alias("regime0"), pl.col("goal_no").alias("goal0"),
                             pl.col("weekday").alias("weekday0"), "aidx", "nidx"), on="day0", how="left")
    ev = ev.with_columns(pl.col("refs").list.first().alias("ref")).sort("day0", "cls", nulls_last=True)
    return ev.with_row_index("event_id").with_columns(pl.col("event_id").cast(pl.Int32))


# ----------------------------------------------------------------------------- transition counts
def build_counts(days, include_holdout=False, only_dates=None):
    """include_holdout=True is used ONLY in memory by analysis/confirm.py (guarded); main() never sets it."""
    st = pl.read_parquet(SH / "states_turn.parquet")
    if not include_holdout:
        st = st.filter(~pl.col("holdout"))
        hm = holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())
        assert not any(hm), "holdout rows leaked into the H56 scheme"
    if only_dates is not None:
        st = st.filter(pl.col("pt_date").is_in(list(only_dates)))
    st = st.filter(pl.col("agent") != CLAUDE_CODE_AGENT)
    a = pl.read_parquet(SH / "actions.parquet", columns=["t", "agent"]).with_row_index("row")
    b = pl.read_parquet(SH / "actions_bash_head_fixed.parquet", columns=["row", "t", "error_class"])
    a = a.join(b.rename({"t": "t_b"}), on="row", how="left")
    assert (a["t"] == a["t_b"]).all()
    err = a.unique(["agent", "t"], keep="first").select("agent", "t", pl.col("error_class").cast(pl.Utf8))
    cw = (pl.read_parquet(SH / "call_windows.parquet", columns=["agent", "t_first", "gap_kind", "holdout"])
          .filter(pl.lit(include_holdout) | ~pl.col("holdout")).select("agent", pl.col("t_first").alias("t"), pl.col("gap_kind").cast(pl.Utf8))
          .unique(["agent", "t"], keep="first"))
    st = (st.join(err, on=["agent", "t"], how="left").join(cw, on=["agent", "t"], how="left")
          .with_row_index("ord").sort("agent", "t", "ord"))
    audit = {"records": st.height,
             "infra_error_records": int(st["error_class"].is_in(INFRA_ERR).sum()),
             "scaffold_gap_starts": int(st["gap_kind"].is_in(SCAFFOLD_GAPS).sum()),
             "matched_call_start_share": float(st["gap_kind"].is_not_null().mean())}
    infra = st["error_class"].is_in(INFRA_ERR).fill_null(False).to_numpy()
    sgap = st["gap_kind"].is_in(SCAFFOLD_GAPS).fill_null(False).to_numpy()
    agent = st["agent"].to_numpy()
    dayc = st["pt_date"].cast(pl.Categorical).to_physical().to_numpy()
    act = st["act"].to_numpy()
    coarse = st["coarse"].to_numpy()
    tt = st["t"].dt.epoch("s").to_numpy()
    pt = st["pt_date"].to_numpy()

    out, ad = [], []
    for vi, v in enumerate(VARIANTS):
        if v == "act_all":
            keep = np.ones(len(act), bool)
            x = act
        elif v == "coarse_all":
            keep = coarse >= 0
            x = coarse
        elif v in ("act_agent", "act_agent_b3"):
            keep = np.isin(act, AGENT_ACTS) & ~infra
            x = act
        else:
            keep = np.isin(coarse, AGENT_COARSE) & ~infra
            x = coarse
        if v.endswith("_all"):
            # decimate (H14): drop removed records, then consecutive kept records form transitions
            idx = np.flatnonzero(keep)
            i0, i1 = idx[:-1], idx[1:]
            ok = (agent[i0] == agent[i1]) & (dayc[i0] == dayc[i1])
        else:
            # cut: consecutive records in the full sequence, both kept, next not a scaffold-set call start
            i0 = np.arange(len(act) - 1)
            i1 = i0 + 1
            ok = keep[i0] & keep[i1] & (agent[i0] == agent[i1]) & (dayc[i0] == dayc[i1]) & ~sgap[i1]
            if v.endswith("_b3"):
                # position of each transition within its run of consecutive valid transitions (a run starts
                # after any cut, i.e. after every scaffold record, scaffold-set call start or day start)
                ix = np.arange(len(ok))
                last_break = np.maximum.accumulate(np.where(~ok, ix, -1))
                ok = ok & ((ix - last_break - 1) >= BURN)
        i0, i1 = i0[ok], i1[ok]
        df = pl.DataFrame({"agent": agent[i1].astype(np.int8), "pt_date": pt[i1], "a": x[i0].astype(np.int8),
                           "b": x[i1].astype(np.int8)})
        df = df.with_columns(pl.int_range(pl.len()).over(["agent", "pt_date"]).alias("r"),
                             pl.len().over(["agent", "pt_date"]).alias("nt"))
        df = df.with_columns(((pl.col("r") * 4) // pl.col("nt")).cast(pl.Int8).alias("block"))
        c = (df.group_by("agent", "pt_date", "block", "a", "b").len("n")
             .with_columns(pl.lit(vi, pl.Int8).alias("variant"), pl.col("n").cast(pl.Int32)))
        out.append(c)
        # agent-day summary for this variant
        kr = pl.DataFrame({"agent": agent[keep].astype(np.int8), "pt_date": pt[keep], "t": tt[keep]})
        s = kr.group_by("agent", "pt_date").agg(pl.len().alias("n_rec"), ((pl.col("t").max() - pl.col("t").min()) / 3600.0).alias("span_h"))
        s = s.join(df.group_by("agent", "pt_date").agg(pl.len().alias("n_trans")), on=["agent", "pt_date"], how="left")
        ad.append(s.with_columns(pl.lit(vi, pl.Int8).alias("variant"), pl.col("n_trans").fill_null(0)))
        audit[f"transitions_{v}"] = int(len(i0))
    counts = pl.concat(out).sort("variant", "agent", "pt_date", "block", "a", "b")
    agent_days = pl.concat(ad).sort("variant", "agent", "pt_date")
    return counts, agent_days, audit


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    days = build_days()
    days.write_parquet(OUT / "days.parquet", compression="zstd")
    ev = build_events(days)
    ev.write_parquet(OUT / "event_catalog.parquet", compression="zstd")
    counts, agent_days, audit = build_counts(days)
    counts.write_parquet(OUT / "counts.parquet", compression="zstd")
    agent_days.write_parquet(OUT / "agent_days.parquet", compression="zstd")
    audit["events_by_class"] = {k: int(v) for k, v in ev.group_by("cls").len().iter_rows()}
    (OUT / "scheme_audit.json").write_text(json.dumps(audit, indent=1))
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["scheme"] = {
        "built_by": "hypotheses/H56-ep-platform-fingerprint/scheme/build.py",
        "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["shared/states_turn", "shared/actions", "shared/actions_bash_head_fixed",
                               "shared/call_windows", "shared/calendar", "shared/period_units",
                               "shared/period_step_changes", "shared/roster", "shared/kicks_classified",
                               "raw/CHANGELOG.md"]}],
        "params": {"variants": VARIANTS, "agent_acts": AGENT_ACTS, "agent_coarse": AGENT_COARSE, "burn_in": BURN,
                   "infra_error_classes": INFRA_ERR, "scaffold_gap_kinds": SCAFFOLD_GAPS, "blocks_per_day": 4,
                   "holdout_locked_at": load_holdout()["locked_at"], "non_holdout_only": True},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    prov_path.write_text(json.dumps(prov, indent=1))
    print(json.dumps(audit, indent=1))


if __name__ == "__main__":
    main()
