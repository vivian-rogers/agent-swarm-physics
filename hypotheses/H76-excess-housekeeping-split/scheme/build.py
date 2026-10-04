"""H76 scheme: Jev v3 behavior windows -> per-block ensemble fluxes and their excess / housekeeping split.

  uv run python hypotheses/H76-excess-housekeeping-split/scheme/build.py
Writes data/processed/H76-excess-housekeeping-split/G<NN>/blocks_<space>.parquet: one row per block (day, grid
untrimmed|trimmed|kick2h|decay1h, kind, steps, agents, raw sigma / sigma_ex / sigma_hk, block-flip surrogate mean and
95th percentile). Codes and numbers only; no text.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import h76lib as L  # noqa: E402
import h76run as RN  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import REVISION, git_commit  # noqa: E402

PERIODS = {51: "2026-07-06", 38: "2026-04-02", 40: "2026-05-04"}


def blocks_table(blocks: dict, days: dict) -> pl.DataFrame:
    rows = []

    def add(day, grid, kind, idx, b):
        rows.append(dict(day=day, grid=grid, kind=kind, idx=idx, steps=b.M, agents=b.Jper.shape[0],
                         sigma_raw=b.raw[0], ex_raw=b.raw[1], hk_raw=b.raw[2], sigma_floor=b.floor[0], ex_floor=b.floor[1],
                         hk_floor=b.floor[2], sigma_p95=b.p95[0], ex_p95=b.p95[1], hk_p95=b.p95[2]))
    if blocks["kick"] is not None:
        add("kickoff", "kick2h", "kick", 0, blocks["kick"])
    for k, b in blocks["dstart"].items():
        add(k, "kick2h", "daystart", 0, b)
    for k, lst in blocks["untrim"].items():
        for i, (kind, b) in enumerate(lst):
            add(k, "untrimmed", kind, i, b)
    for k, lst in blocks["trim"].items():
        for i, (kind, b) in enumerate(lst):
            add(k, "trimmed", kind, i, b)
    for i, (k, b) in enumerate(blocks["decay"]):
        add(k, "decay1h", "decay", i, b)
    return pl.DataFrame(rows)


def provenance(params: dict):
    L.OUTD.mkdir(parents=True, exist_ok=True)
    (L.OUTD / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H76-excess-housekeeping-split/scheme/build.py (+ analysis/run.py, analysis/synthetic.py)",
        "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["behavior_states_v3 (DQ3)", "calendar", "goals.parquet", "context_ledger_turns (DQ1)"]}],
        "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))


def main():
    rng = np.random.default_rng(76)
    for g, kd in PERIODS.items():
        for space in ("coarse", "fine"):
            days = L.load_v3(g, space)
            bl = RN.build_blocks(days, kd, rng, R=20)
            t = blocks_table(bl, days)
            d = L.OUTD / f"G{g:02d}"
            d.mkdir(parents=True, exist_ok=True)
            t.write_parquet(d / f"blocks_{space}.parquet", compression="zstd")
            print(g, space, len(days), t.height, flush=True)
    provenance({"step_min": 5, "block_steps": 6, "kick_steps": RN.KICK_STEPS, "decay_block": RN.DECAY_BLOCK,
                "alpha": L.ALPHA, "surrogate": "per-agent block flip, R=20", "coarse_groups": L.COARSE_GROUPS})


if __name__ == "__main__":
    main()
