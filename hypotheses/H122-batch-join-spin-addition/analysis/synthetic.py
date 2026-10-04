"""H122 synthetic validation (axis F) on real event skeletons (NE32, NE27): real incumbents' calls and read /
placebo / exogenous counts; outcomes simulated from M0 fitted on the real PRE window plus planted post-join terms.

Worlds: null; J_N = 0.1, 0.3 (logit per newcomer read, P12 and F37); delta = 0.2, 0.4 (constant shift, P12 and F37).
Output: data/processed/H122-batch-join-spin-addition/synthetic/{reps,summary}.parquet

    uv run python hypotheses/H122-batch-join-spin-addition/analysis/synthetic.py [--reps 50]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h122lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H122-batch-join-spin-addition"
WORLDS = {"null": (0.0, 0.0), "J0.1": (0.1, 0.0), "J0.3": (0.3, 0.0), "d0.2": (0.0, 0.2), "d0.4": (0.0, 0.4)}


def run(args):
    ev, reps = args
    e = pl.read_parquet(D / "events.parquet").filter(pl.col("event") == ev).to_dicts()[0]
    N = {0: e["N_pre"], 1: e["N_p12"], 2: e["N_f37"]}
    df = L.prep(pl.read_parquet(D / "calls" / f"{ev}.parquet"))
    m0_true = L.M0(df.filter(pl.col("win") == 0))
    rows = []
    for w, (J, dl) in WORLDS.items():
        for r in range(reps):
            rng = np.random.default_rng(hash((ev, w, r)) % (2 ** 32))
            sim = L.simulate(df, N, m0_true, rng, J=J, delta=dl)
            fit = L.fit_models(sim, N)
            sc = L.scores(fit, B=500, seed=r)
            rows.append({"event": ev, "world": w, "rep": r, "J_true": J, "delta_true": dl, **fit["par"]["pre"],
                         "J_N": fit["par"]["J_N"], "delta": fit["par"]["delta"], **sc})
        print(ev, w, flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=50)
    a = ap.parse_args()
    out = D / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=2) as ex:
        for r in ex.map(run, [("NE32", a.reps), ("NE27", a.reps)]):
            rows += r
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(out / "reps.parquet")
    s = (df.group_by("event", "world").agg(
        pl.len().alias("reps"),
        (pl.col("d_C_J_lo") > 0).mean().alias("MJ_wins"), (pl.col("d_C_J_hi") < 0).mean().alias("MC_wins"),
        pl.col("d_C_J").median().alias("dLL_med"), pl.col("J_N").median().alias("J_N_med"),
        pl.col("delta").median().alias("delta_med"), (pl.col("d_PL_J_lo") > 0).mean().alias("MJ_beats_pl"),
    ).sort("event", "world"))
    s.write_parquet(out / "summary.parquet")
    (out / "summary.json").write_text(json.dumps(s.to_dicts(), indent=1, default=float))
    pl.Config.set_tbl_width_chars(250)
    print(s)


if __name__ == "__main__":
    main()
