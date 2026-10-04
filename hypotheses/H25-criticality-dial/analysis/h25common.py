"""H25 shared helpers: paths, holdout-safe calendar, period metadata, provenance.

Reads shared tables and other hypotheses' outputs (never writes there). Everything H25 writes goes to
data/processed/H25-criticality-dial/ and the H25 card folder.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
sys.dont_write_bytecode = True

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H25-criticality-dial"
OUT = ROOT / "data/processed/H25-criticality-dial"
SHARED = ROOT / "data/processed/shared"
PROC = ROOT / "data/processed"
FIG = HYP / "figures"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask, load_holdout, load_whitener  # noqa: E402,F401

SEED = 20261004


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H25-criticality-dial"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted-H25" if dirty.strip() else "")


def write_provenance(entry: str, built_by: str, tables: list[str], params: dict, extra_inputs: list[dict] | None = None,
                     out: Path | None = None):
    out = out or OUT
    out.mkdir(parents=True, exist_ok=True)
    p = out / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    inputs = [{"source": "ai-village", "revision": REVISION, "tables": tables, "via": "data/processed/shared"}]
    prov[entry] = {"built_by": built_by, "git_commit": git_commit(), "inputs": inputs + (extra_inputs or []),
                   "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1, default=str))


def calendar_all() -> pl.DataFrame:
    cal = pl.read_parquet(SHARED / "calendar.parquet")
    cal = cal.filter((pl.col("window_s") > 0) & pl.col("goal_no").is_not_null() & (pl.col("goal_no") > 0))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return cal.with_columns(pl.Series("hm", hm), pl.col("regime").cast(pl.String)).sort("pt_date")


def calendar_nonholdout() -> pl.DataFrame:
    """Village days with activity that are NOT in the locked holdout (calendar flag AND infra mask agree)."""
    cal = calendar_all()
    return cal.filter(~pl.col("holdout") & ~pl.col("hm")).drop("hm")


def assert_no_holdout(pt_dates, goal_nos):
    hm = holdout_mask(list(pt_dates), list(goal_nos))
    assert not any(hm), "holdout day leaked into an H25 exploratory selection"


def pname(g: int) -> str:
    return f"G{int(g):02d}"


def goal_period_meta() -> pl.DataFrame:
    """Mode / regime / N at start from the 'At a glance' table of goal-periods.md (same parser as H19)."""
    import re
    txt = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    rows = []
    for line in txt.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(\S+) → (\S+)\s*\|\s*([^|]*)\|\s*(\d+)\s*\|\s*([^|]*)\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|", line)
        if m:
            rows.append({"goal_no": int(m.group(1)), "d_doc": m.group(4).strip(), "N_start": int(m.group(5)),
                         "AH": m.group(6).strip(), "reg_doc": m.group(7), "by": m.group(8), "mode": m.group(9)})
    return pl.DataFrame(rows).unique("goal_no").sort("goal_no")
