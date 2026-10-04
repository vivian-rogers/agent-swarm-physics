"""H116 data scheme: per-call talk spins with read-gated and in-flight inputs for the event and placebo periods.

  uv run python hypotheses/H116-election-coupling-step/scheme/build.py --period G26   (also G24, G25, G27, G12, G35)

Writes data/processed/H116-election-coupling-step/G<NN>/: calls.parquet, xr.npy, xp.npy, agents.json,
validation.json, _provenance.json. Codes only, no text; held-out rows refused (callspins guard).
G24, G25 and G27 are the regime-I placebo weeks around #26 (same roster era); G12 and G35 are replication periods.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import callspins as CS  # noqa: E402

ROOT = CS.ROOT
OUTROOT = ROOT / "data/processed/H116-election-coupling-step"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit  # noqa: E402

UTC = dt.timezone.utc
GOAL = {"G24": 24, "G25": 25, "G26": 26, "G27": 27, "G12": 12, "G35": 35}


def build(period: str) -> dict:
    g = GOAL[period]
    out = OUTROOT / period
    out.mkdir(parents=True, exist_ok=True)
    calls = CS.load_calls([g])
    msgs = CS.load_messages([g])
    agents = sorted(int(a) for a in calls["agent"].unique().to_list())
    calls, XR, XP = CS.build_inputs(calls, msgs, agents)
    calls = calls.with_columns(pl.Series("trim", CS.all_present_trim(calls)))
    val = CS.validate_against_ledger(calls, XR, agents)
    calls.write_parquet(out / "calls.parquet", compression="zstd")
    np.save(out / "xr.npy", XR)
    np.save(out / "xp.npy", XP)
    (out / "agents.json").write_text(json.dumps(agents))
    (out / "validation.json").write_text(json.dumps(val, indent=1))
    prov = {"built_by": "hypotheses/H116-election-coupling-step/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["call_windows", "context_ledger_turns", "context_ledger_items", "chat_core"]}],
            "params": {"period": period, "goal": g, "trim_min_calls": 20, "summary_calls": "dropped",
                       "exclude_recipients": [19]},
            "built_at": dt.datetime.now(UTC).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))
    return {"period": period, "n_calls": calls.height, "agents": agents, "validation": val}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", required=True, choices=sorted(GOAL))
    a = ap.parse_args()
    print(json.dumps(build(a.period), default=str))
