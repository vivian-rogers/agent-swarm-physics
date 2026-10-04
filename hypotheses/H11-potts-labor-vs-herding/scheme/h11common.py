"""H11 shared helpers: paths, period lists, holdout guard, provenance.

Categorical states per agent per window (see the card, "Data scheme"):
  * project (artifact variant): the project an agent touches most in the window, from the
    H07 artifacts tables, strict mentions only (how in {url, output, bare});
  * action class: the agent's modal action class in the window.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from infra.shared import common as C  # noqa: E402

HYP = ROOT / "hypotheses/H11-potts-labor-vs-herding"
SHARED = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H11-potts-labor-vs-herding"
FIG = HYP / "figures"

WINDOWS_MIN = (15, 30, 60)       # window lengths built; 30 is primary
W_PRIMARY = 30
Q_MAX = 8                        # real project states kept per period (rest -> "other", state 0, no coupling)
MIN_SHARE = 0.02                 # a project must hold >= 2% of labeled agent-windows to get its own state
STRICT_HOW = ("url", "output", "bare")

# Candidate periods named in the card, and their a-priori coupling-mode class (from
# hypotheses/hypohypotheses/goal-periods.md descriptions only; written before any real-data run).
CANDIDATES = {13: "AF", 18: "AF", 19: "FM-consensus", 26: "FM-consensus", 31: "FM-free", 40: "FM-consensus",
              41: "FM-convergence"}
# Transfer periods (same rule, predictions by mode; see card P-transfer).
TRANSFER = {11: "FM-free", 16: "FM-free", 37: "FM-free", 24: "AF", 25: "AF", 30: "AF", 38: "AF",
            20: "none-I", 39: "none-I", 42: "none-I"}


def holdout() -> dict:
    return C.load_holdout()


def held_goals() -> set[int]:
    return set(holdout()["goal_periods_held_out"])


def assert_not_holdout(goals, allow_holdout: bool = False):
    bad = sorted(set(goals) & held_goals())
    if bad and not allow_holdout:
        raise SystemExit(f"refusing: goal periods {bad} are in the locked holdout (hypotheses/holdout.json)")


def nonholdout_goals() -> list[int]:
    h = held_goals()
    return [g for g in range(2, 45) if g not in h]


def write_provenance(folder: Path, built_by: str, tables: list[str], params: dict):
    folder.mkdir(parents=True, exist_ok=True)
    prov = {"built_by": built_by, "git_commit": C.git_commit(),
            "inputs": [{"source": "ai-village", "revision": C.REVISION, "tables": tables,
                        "via": "data/processed/shared (infra/shared/scan_tables.py, build_derived.py, build_artifacts.py)"}],
            "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (folder / "_provenance.json").write_text(json.dumps(prov, indent=1))
