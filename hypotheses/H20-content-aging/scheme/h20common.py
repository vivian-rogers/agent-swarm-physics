"""H20 shared helpers: paths, thread limits, holdout guard, period lists.

Every H20 script imports this first. It caps BLAS threads (the machine is shared; <= 2 workers).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HDIR = ROOT / "hypotheses/H20-content-aging"
SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H20-content-aging"
H01 = ROOT / "data/processed/H01-emergent-superagents-exist"
sys.path.insert(0, str(ROOT / "infra/shared"))
import common  # noqa: E402

CLAUDE_CODE_AGENT = 19
MIN_STMTS = 8          # agent-days with fewer statements are dropped (card O1)
SEED = 20261003

# Periods (card "Candidate goal periods")
LONG = [4, 8, 38, 51]
MEDIUM = [6, 13, 18, 19, 20, 27]
SHORT = [5, 10, 11, 12, 16, 17, 21, 23, 24, 25, 26, 30, 31, 35, 39, 40, 41, 42, 44]
EXCLUDED = {2: "2 days", 3: "3 days", 7: "2 days", 33: "3 days", 37: "3 days",
            36: "crosses the 2026-03-24 regime boundary on its day 2"}
ALL_PERIODS = LONG + MEDIUM + SHORT

# Step changes inside periods (rejuvenation test, card O7; H01 Amendment 2 split dates)
STEPS = {38: ["2026-04-14", "2026-04-20"], 51: ["2026-07-09", "2026-08-05", "2026-08-25", "2026-09-03"]}

# Locked holdout periods relevant to H20 confirmation (never touched in exploration)
CONFIRM_LONG = [1]
CONFIRM_TAIL = 51
CONFIRM_SHORT = [14, 15, 22, 28, 29, 45, 47, 49, 50]


def role(g: int) -> str:
    return "long" if g in LONG else "medium" if g in MEDIUM else "short" if g in SHORT else "other"


def held_out_goals() -> set[int]:
    return set(common.load_holdout()["goal_periods_held_out"])


def assert_not_holdout(goal_nos, pt_dates):
    """Refuse to continue if any row is in the locked holdout (exploration guard)."""
    m = common.holdout_mask(list(pt_dates), list(goal_nos))
    if any(m):
        raise RuntimeError(f"holdout rows present ({sum(m)}); exploration must not touch the locked holdout")


def write_provenance(params: dict, tables: list[str], built_by: str):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[Path(built_by).stem] = {
        "built_by": built_by, "git_commit": common.git_commit(),
        "inputs": [{"source": "ai-village", "revision": common.REVISION, "tables": tables}],
        "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    path.write_text(json.dumps(prov, indent=1))
