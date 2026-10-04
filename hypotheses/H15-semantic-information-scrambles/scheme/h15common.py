"""H15 shared helpers: paths, thread caps, holdout guard, analysis units, viability candidates.

Imported by scheme/build.py and analysis/*.py. Thread use is capped at 2 (other agents share the machine):
the env vars are set before numpy/polars are imported.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402,F401

SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
OUT = ROOT / "data/processed/H15-semantic-information-scrambles"
FIG = HYP / "figures"
SEED = 20261003
UTC = dt.timezone.utc

CLAUDE_CODE_AGENT = 19
# Write verbs = functional output (D2.3.a).
WRITE_VERBS = ["git push", "git commit", "deploy", "gh pr create", "gh pr merge", "gh repo create",
               "glab mr create", "glab mr merge", "glab repo create", "glab project create"]
V_CANDIDATES = ["V_out", "V_eng", "V_rel", "V_ord", "V_coh"]
V_LABEL = {"V_out": "write turns / h (functional)", "V_eng": "engaged-minute fraction (structural)",
           "V_rel": "1 - error fraction (reliability)", "V_ord": "-H(action mix) (order, KW -S)",
           "V_coh": "plan coherence (order)"}

# Analysis units: goal periods; #36 is split at the 2026-03-24 regime boundary (NE14 F).
UNIT_SPLITS = {36: ["2026-03-24"]}


def unit_of(goal_no: int, pt_date: str) -> str:
    cuts = UNIT_SPLITS.get(int(goal_no))
    if not cuts:
        return str(int(goal_no))
    k = sum(pt_date >= c for c in cuts)
    return f"{int(goal_no)}{'ab'[k]}"


def unit_expr() -> pl.Expr:
    """Polars expression for unit_of over columns goal_no, pt_date."""
    return (pl.when((pl.col("goal_no") == 36) & (pl.col("pt_date") < "2026-03-24")).then(pl.lit("36a"))
            .when((pl.col("goal_no") == 36)).then(pl.lit("36b"))
            .otherwise(pl.col("goal_no").cast(pl.Utf8)))


def calendar_nonholdout() -> pl.DataFrame:
    """Active PT days not in the locked holdout (calendar flag AND holdout_mask, belt and braces)."""
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm))
    cal = cal.filter(~pl.col("holdout") & ~pl.col("hm") & (pl.col("goal_no") > 0) & (pl.col("n_agent_events") > 0))
    return cal.drop("hm").with_columns(unit_expr().alias("unit"),
                                       ((pl.col("win_end") - pl.col("win_start")).dt.total_seconds() / 3600)
                                       .alias("win_h"))


def holdout_days() -> set[str]:
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return {d for d, h, f in zip(cal["pt_date"], hm, cal["holdout"]) if h or f}


def refuse_holdout(pt_dates, what: str = "rows"):
    """Assert no holdout day slipped into an exploratory table."""
    bad = set(pt_dates) & holdout_days()
    if bad:
        raise SystemExit(f"HOLDOUT GUARD: {len(bad)} holdout days in {what} (e.g. {sorted(bad)[:3]})")


def pt_date_expr(col: str = "t") -> pl.Expr:
    return pl.col(col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8)


def write_provenance(name: str, tables: list[str], params: dict | None = None, built_by: str | None = None):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[name] = {"built_by": built_by or f"hypotheses/H15-semantic-information-scrambles/scheme/{name}.py",
                  "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                  "params": params or {}, "built_at": dt.datetime.now(UTC).isoformat()}
    path.write_text(json.dumps(prov, indent=1))
