"""H33 shared helpers: paths, thread caps (2), holdout guard, analysis units, provenance.

Imported by scheme/build.py and analysis/*.py. Env vars are set before numpy/polars are imported.
Imports (never modifies) H12 (PR estimators, self-repeat removal) and H15 (write verbs).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import zlib  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
# Round switch (2026-10-04). H33_ROUND=r1 (default) reproduces round 1; H33_ROUND=r1b = improved data: productivity from
# the DQ4 work ledger (agent work commits, distinct files; #30 on), activity_bins_fixed controls, diversity with both
# embedding models (DQ5 white32) and three dedups. Outputs under <OUT_R1>/r1b, figures under figures/r1b.
ROUND = os.environ.get("H33_ROUND", "r1")
assert ROUND in ("r1", "r1b"), ROUND
OUT_R1 = ROOT / "data/processed/H33-diversity-productivity"
OUT = OUT_R1 / "r1b" if ROUND == "r1b" else OUT_R1
FIG = HYP / "figures" / "r1b" if ROUND == "r1b" else HYP / "figures"
SFX = "_r1b" if ROUND == "r1b" else ""
Y_PRIMARY = "commits_w" if ROUND == "r1b" else "writes"          # log(1 + y) is the outcome
Y_ROBUST = (("files_w", "lines_nb", "writes", "commits") if ROUND == "r1b"
            else ("commits", "deploys", "artifacts_adv", "writes_clean"))
X_ROBUST = (("tv10", "pr6", "pr15", "pr10_bge_w", "pr10_gte", "pr10_bge_copies", "pr10_bge_restate", "pr10_gte_copies",
             "pr10_gte_restate") if ROUND == "r1b" else ("tv10", "pr6", "pr15"))
MIN_GOAL = 30 if ROUND == "r1b" else 0       # work ledger dense from #30; earlier zeros are ambiguous
SEED = 20261004
CLAUDE_CODE_AGENT = 19

sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H12-groupthink-dimensional-collapse/analysis"))
sys.path.insert(0, str(ROOT / "hypotheses/H15-semantic-information-scrambles/scheme"))
from common import REVISION, holdout_mask, load_holdout, load_whitener  # noqa: E402,F401

# Pre-registered parameters (card, 2026-10-04)
N_PR = 10          # rarefaction size for the primary agent-day PR
N_PR_ROB = (6, 15)
N_PR_HALF = 6      # half-day PR (reverse-causation test)
DRAWS = 20
D = 32
SWARM_M, SWARM_K, SWARM_DRAWS = 5, 10, 50
NEAR_DUP = 0.95


def unit_expr() -> pl.Expr:
    """Analysis unit = goal period; #36 split at the 2026-03-24 regime boundary (whitener changes)."""
    return (pl.when((pl.col("goal_no") == 36) & (pl.col("pt_date") < "2026-03-24")).then(pl.lit("36a"))
            .when(pl.col("goal_no") == 36).then(pl.lit("36b"))
            .otherwise(pl.col("goal_no").cast(pl.Utf8)))


def pt_date_expr(col: str = "t") -> pl.Expr:
    return pl.col(col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8)


def calendar_nonholdout() -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm))
    cal = cal.filter(~pl.col("holdout") & ~pl.col("hm") & (pl.col("goal_no") > 0) & (pl.col("n_agent_events") > 0))
    return cal.drop("hm").with_columns(unit_expr().alias("unit"), pl.col("regime").cast(pl.Utf8))


def holdout_days() -> set[str]:
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return {d for d, h, f in zip(cal["pt_date"], hm, cal["holdout"]) if h or f}


def refuse_holdout(pt_dates, what: str = "rows"):
    bad = set(pt_dates) & holdout_days()
    if bad:
        raise SystemExit(f"HOLDOUT GUARD: {len(bad)} holdout days in {what} (e.g. {sorted(bad)[:3]})")


def stable_seed(obj) -> int:
    return zlib.crc32(json.dumps(obj, sort_keys=True, default=str).encode()) % 2**31


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(HYP)],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def write_provenance(built_by: str, tables: list[str], params: dict, path: Path | None = None):
    path = path or (OUT / "_provenance.json")
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[built_by] = {"built_by": built_by, "git_commit": git_commit(),
                      "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                      "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(prov, indent=1))


def unit_dir(unit: str, root: Path | None = None) -> Path:
    return (root or OUT) / f"G{int(unit.rstrip('abt')):02d}"


def load_agent_day(root: Path | None = None) -> pl.DataFrame:
    return pl.concat([pl.read_parquet(f) for f in sorted((root or OUT).glob("G*/agent_day.parquet"))], how="diagonal_relaxed")


def load_swarm_day(root: Path | None = None) -> pl.DataFrame:
    return pl.concat([pl.read_parquet(f) for f in sorted((root or OUT).glob("G*/swarm_day.parquet"))], how="diagonal_relaxed")
