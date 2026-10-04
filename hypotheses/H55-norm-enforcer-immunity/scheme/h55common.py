"""H55 shared paths and helpers (thread caps set before numpy/polars import)."""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import common as C  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H55-norm-enforcer-immunity"
OUT.mkdir(parents=True, exist_ok=True)
HDIR = ROOT / "hypotheses/H55-norm-enforcer-immunity"
SCRATCH = Path("/private/tmp/claude-501/-Users-wrogers-Documents-school-fun-agenttesting/"
               "015f2aa2-05c1-4a7e-ba6c-25bf6c9d1344/scratchpad")
SEED = 20261004
ENFORCER_ROLES = ("psychologist", "ethicist", "diplomat")                       # primary (HH162 / H37)
ENFORCER_ROLES_EXT = ENFORCER_ROLES + ("performance coach", "village helper")    # H37's post hoc grouping


def write_prov(name: str, built_by: str, tables: list[str], params: dict | None = None, extra: dict | None = None):
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[name] = {"built_by": built_by, "git_commit": C.git_commit(),
                  "inputs": [{"source": "ai-village", "revision": C.REVISION, "tables": tables}],
                  "params": params or {}, "built_at": dt.datetime.now(dt.timezone.utc).isoformat(), **(extra or {})}
    path.write_text(json.dumps(prov, indent=1))


def holdout_flags(pt_dates, goal_nos):
    return C.holdout_mask(list(pt_dates), list(goal_nos))
