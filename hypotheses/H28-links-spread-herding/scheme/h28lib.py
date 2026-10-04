"""H28 shared helpers: paths, period lists, holdout guard, provenance, imports of H11/H18 code.

H11's project map and H18's turn-time rule are imported (never modified):
  * H11  hypotheses/H11-potts-labor-vs-herding/scheme/build.py: project_map()
  * H18  hypotheses/H18-attention-dilution/scheme/build.py: turn_times(sh, t0, t1)
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from infra.shared import common as C  # noqa: E402

HYP = ROOT / "hypotheses/H28-links-spread-herding"
SHARED = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H28-links-spread-herding"
FIG = HYP / "figures"
PERIOD_DIR = HYP / "goalperiod-subhypotheses"

BIN_S = 300                 # 5-min bins
ON_GAP_S = 3600             # on X while touched within the last 60 min
K_MAX = 30                  # universe size cap
STRICT_TOUCH = ("url", "output", "bare")
STRICT_LINK = ("url", "bare")
NE09 = "2025-12-20"         # chat interleaved into computer-use context

# Periods (card, "Candidate goal periods"); roles fixed before the real-data run.
CANDIDATES = [31, 18, 37, 41, 38, 51]
HERDING = [19, 24, 25, 26, 30]
CONTRAST = [39, 40, 42]
ALL_PERIODS = sorted(CANDIDATES + HERDING + CONTRAST)
ROLE = {**{g: "candidate" for g in CANDIDATES}, **{g: "herding" for g in HERDING}, **{g: "contrast" for g in CONTRAST}}
MULTIROOM = [37, 38, 39, 41, 42, 51]      # periods with >1 room in use (51: #focus from 2026-08-05)
PRE_NE09 = [18, 19, 20]
POST_NE09 = [24, 25, 26, 30, 31]


def gname(g: int) -> str:
    return f"G{g:02d}"


def held_goals() -> set[int]:
    return set(C.load_holdout()["goal_periods_held_out"])


def assert_not_holdout(goals, allow_holdout: bool = False):
    bad = sorted(set(goals) & held_goals())
    if bad and not allow_holdout:
        raise SystemExit(f"refusing: goal periods {bad} are in the locked holdout (hypotheses/holdout.json)")


def _load(name: str, path: Path, extra_path: Path | None = None):
    if extra_path is not None and str(extra_path) not in sys.path:
        sys.path.insert(0, str(extra_path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def h11_build():
    d = ROOT / "hypotheses/H11-potts-labor-vs-herding/scheme"
    return _load("h11_build", d / "build.py", d)


def h18_build():
    d = ROOT / "hypotheses/H18-attention-dilution/scheme"
    return _load("h18_build", d / "build.py", ROOT / "hypotheses/H18-attention-dilution/analysis")


def write_provenance(folder: Path, built_by: str, tables: list[str], params: dict, key: str | None = None):
    folder.mkdir(parents=True, exist_ok=True)
    prov = {"built_by": built_by, "git_commit": C.git_commit(),
            "inputs": [{"source": "ai-village", "revision": C.REVISION, "tables": tables,
                        "via": "data/processed/shared (infra/shared/scan_tables.py, build_derived.py, build_artifacts.py, "
                               "build_mentions_clean.py)"}],
            "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p = folder / "_provenance.json"
    if key is None:
        p.write_text(json.dumps(prov, indent=1))
    else:
        old = json.loads(p.read_text()) if p.exists() else {}
        old[key] = prov
        p.write_text(json.dumps(old, indent=1))
