"""Run every H39 point-lever period (2 worker processes, 1 BLAS thread each), largest first.

Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/run_all.py [--quick] [--only G51,G38]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from write_period_folders import POINT_PERIODS  # noqa: E402


def job(args):
    p, quick = args
    import run_period
    t0 = time.time()
    try:
        run_period.run(p, quick)
        return p, "ok", time.time() - t0
    except Exception:
        return p, traceback.format_exc(), time.time() - t0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    periods = [f"G{g:02d}" for g in POINT_PERIODS]
    if a.only:
        periods = [p for p in periods if p in a.only.split(",")]
    order = ["G51", "G38", "G04"] + [p for p in periods if p not in ("G51", "G38", "G04")]
    order = [p for p in order if p in periods]
    with ProcessPoolExecutor(2) as ex:
        futs = [ex.submit(job, (p, a.quick)) for p in order]
        for f in as_completed(futs):
            p, st, dt = f.result()
            print(f"== {p}: {st if st == 'ok' else 'FAILED'} ({dt:.0f}s)", flush=True)
            if st != "ok":
                print(st, flush=True)
