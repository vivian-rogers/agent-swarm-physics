"""H19 shared helpers: paths, holdout-safe calendar, goal-period metadata, provenance.

Reads other hypotheses' outputs (never writes there) and the shared tables in data/processed/shared/.
Everything H19 writes goes to data/processed/H19-loop-gain-collapse/ (and the H19 card folder).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H19-loop-gain-collapse"
OUT = ROOT / "data/processed/H19-loop-gain-collapse"
SHARED = ROOT / "data/processed/shared"
PROC = ROOT / "data/processed"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask, load_holdout  # noqa: E402

DAY0 = dt.date(2025, 4, 2)


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H19-loop-gain-collapse"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted-H19" if dirty.strip() else "")


def write_provenance(entry: str, built_by: str, inputs: list[dict], params: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov[entry] = {"built_by": built_by, "git_commit": git_commit(), "inputs": inputs, "params": params,
                   "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1))


def calendar_nonholdout() -> pl.DataFrame:
    """Village days with activity that are NOT in the locked holdout (calendar flag AND infra mask agree)."""
    cal = pl.read_parquet(SHARED / "calendar.parquet")
    cal = cal.filter((pl.col("window_s") > 0) & pl.col("goal_no").is_not_null() & (pl.col("goal_no") > 0))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm))
    cal = cal.filter(~pl.col("holdout") & ~pl.col("hm")).drop("hm")
    return cal.sort("pt_date")


def assert_no_holdout(pt_dates, goal_nos):
    hm = holdout_mask(list(pt_dates), list(goal_nos))
    assert not any(hm), "holdout day leaked into an H19 exploratory selection"


def heldout_goals() -> set[int]:
    return set(load_holdout()["goal_periods_held_out"])


def goal_period_meta() -> pl.DataFrame:
    """Parse the 'At a glance' table of hypotheses/hypohypotheses/goal-periods.md (mode, by, regime, N at start)."""
    txt = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    rows = []
    for line in txt.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(\S+) → (\S+)\s*\|\s*([^|]*)\|\s*(\d+)\s*\|\s*([^|]*)\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|", line)
        if m:
            rows.append({"goal_no": int(m.group(1)), "start": m.group(2), "end": m.group(3),
                         "N_start": int(m.group(5)), "reg_doc": m.group(7), "by": m.group(8), "mode": m.group(9)})
    df = pl.DataFrame(rows).unique("goal_no").sort("goal_no")
    assert df.height == 51, f"expected 51 goal periods, parsed {df.height}"
    return df


def pname(g: int) -> str:
    return f"G{int(g):02d}"
