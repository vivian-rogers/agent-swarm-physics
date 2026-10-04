"""H66 replication layer: the common estimator (h66lib.analyze_grid) on every eligible non-holdout unit of
regimes II-III. Writes data/processed/H66-platform-latency-field/replication/<unit>.json and summary.parquet.
Run: uv run python hypotheses/H66-platform-latency-field/analysis/replication.py [--workers 2] [--only 44b,51c]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h66lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H66-platform-latency-field"


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    return o


def job(unit):
    t = time.time()
    g = pl.read_parquet(OUT / "grid" / f"{unit}.parquet")
    r = L.analyze_grid(g, seed=hash(unit) % (2**31), R=99, K=20, B=200, full=True)
    if r is None:
        return unit, None
    r["unit"] = unit
    r["seconds"] = time.time() - t
    (OUT / "replication" / f"{unit}.json").write_text(json.dumps(_clean(r), indent=1))
    return unit, r["seconds"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    (OUT / "replication").mkdir(exist_ok=True)
    units = pl.read_parquet(OUT / "units.parquet")
    us = units["unit_id"].to_list() if not a.only else a.only.split(",")
    # biggest first so the pool stays busy
    size = dict(zip(units["unit_id"], units["rows"]))
    us = sorted(us, key=lambda u: -size.get(u, 0))
    with ProcessPoolExecutor(a.workers) as ex:
        for u, s in ex.map(job, us):
            print(u, s, flush=True)


if __name__ == "__main__":
    main()
