"""Calibrated held-out test (N2): leave-one-day-out dLL (M3 - M1, M2 - M1) of the real chunk vs the same
statistic on K N1 (block-shift) surrogates of that chunk. z > 0 means couplings transfer across days better
than chance; the raw dLL is negative under the null because unneeded couplings overfit.
Usage: uv run python heldout_null.py [K] [spin]
Output: data/processed/H02-couplings-are-real/heldout_null[_talk].parquet
"""
from __future__ import annotations

import os
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl

import h02lib as L
from calibrate import load_chunks
from h02lib import heldout

ROOT = Path(__file__).resolve().parents[3]
DATA = __import__("r1b_common").data_dir()   # round 1 or round 1b (+ mask): analysis/r1b_common.py
K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
SPIN = sys.argv[2] if len(sys.argv) > 2 else "active"
BLOCK = int(sys.argv[3]) if len(sys.argv) > 3 else 30   # block length (min) for fields and the N1 null
REGIME = sys.argv[4] if len(sys.argv) > 4 else None     # restrict to one regime


def stat(S, day, minute, labs):
    ho = heldout(S, day, minute, labs)
    T = sum(r["T"] for r in ho)
    return sum(r["M3"] - r["M1"] for r in ho) / T, sum(r["M2"] - r["M1"] for r in ho) / T


def job(args):
    ch, c, labs, seed = args
    L.BLOCK_MIN, L.MIN_LAST_BLOCK = BLOCK, max(BLOCK // 3, 3)
    rng = np.random.default_rng([31337, seed])
    lab_arr = np.array([labs[a] for a in c["agents"]])
    r31, r21 = stat(c["S"], c["day"], c["minute"], lab_arr)
    segs = L.segments(c["day"], c["minute"], "block")
    nul = np.array([stat(L.circular_shift(c["S"], segs, rng), c["day"], c["minute"], lab_arr) for _ in range(K)])
    return {"chunk": ch, "mode": c["mode"], "regime": c["regime"], "N": len(c["agents"]),
            "d31": r31, "d31_null_mean": float(nul[:, 0].mean()), "d31_null_sd": float(nul[:, 0].std()),
            "z31": float((r31 - nul[:, 0].mean()) / nul[:, 0].std()),
            "p31": float((1 + (nul[:, 0] >= r31).sum()) / (K + 1)),
            "d21": r21, "z21": float((r21 - nul[:, 1].mean()) / nul[:, 1].std()),
            "p21": float((1 + (nul[:, 1] >= r21).sum()) / (K + 1))}


def main():
    chunks = load_chunks(SPIN)
    if REGIME:
        chunks = {k: v for k, v in chunks.items() if v["regime"] == REGIME}
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    labs = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    jobs = [(ch, c, labs, k) for k, (ch, c) in enumerate(sorted(chunks.items()))]
    with Pool(int(os.environ.get("H02_WORKERS", 3))) as p:  # round 1b runs with 2
        res = pl.DataFrame(p.map(job, jobs, chunksize=1))
    suf = ("" if SPIN == "active" else f"_{SPIN}") + ("" if BLOCK == 30 else f"_b{BLOCK}") + (f"_r{REGIME}" if REGIME else "")
    res.write_parquet(DATA / f"heldout_null{suf}.parquet")
    with pl.Config(tbl_rows=30, tbl_cols=20, tbl_width_chars=200):
        print(res.sort("regime", "mode", "chunk").with_columns(pl.col(pl.Float64).round(3)))
        print(res.group_by("regime", "mode").agg(pl.len(), pl.col("z31").median().round(2), (pl.col("p31") < 0.05).sum().alias("n_p31<.05"),
                                                pl.col("z21").median().round(2), (pl.col("p21") < 0.05).sum().alias("n_p21<.05")).sort("regime", "mode"))


if __name__ == "__main__":
    main()
