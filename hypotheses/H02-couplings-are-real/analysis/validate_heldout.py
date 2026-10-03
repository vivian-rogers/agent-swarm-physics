"""Synthetic check of the leave-one-day-out comparison (N2) and of the per-coupling test at real-data scale.

N = 15, D = 5 days x 241 bins, regime-III calibration, block drive. Coupling scenarios:
  none      no cross couplings
  weak      density 0.15, |J| ~ U[0.02, 0.08]
  planted   density 0.15, |J| ~ U[0.05, 0.25] (the harness background)
For each: held-out dLL per bin (M3 - M1, M2 - M1) and the fraction of |z| > 1.96 vs N1 (50 surrogates).
Output: data/processed/H02-couplings-are-real/validate_heldout.parquet
"""
from __future__ import annotations

import os
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
from multiprocessing import Pool

import numpy as np
import polars as pl

import h02lib as L
import harness as H
from h02lib import heldout

N, D = 15, 5
SCEN = {"none": None, "weak": (0.02, 0.08), "planted": (0.05, 0.25)}


def job(args):
    scen, rep = args
    rng = np.random.default_rng([4242, list(SCEN).index(scen), rep])
    k = rng.integers(0, len(H.CAL["h0"]), N)
    h0 = np.array(H.CAL["h0"])[k]; Js = np.array(H.CAL["Jself"])[k]
    Jx = np.zeros((N, N))
    if SCEN[scen]:
        m = rng.random((N, N)) < 0.15; np.fill_diagonal(m, False)
        Jx[m] = rng.uniform(*SCEN[scen], m.sum()) * np.where(rng.random(m.sum()) < 0.7, 1, -1)
    bf = rng.normal(0, H.CAL["sigma_common"], (D, 8, 1)) + rng.normal(0, H.CAL["sigma_agent"], (D, 8, N))
    S, day, minute = L.simulate(h0, Js, Jx, D, H.TD, rng, blockfield=bf)
    labs = rng.integers(0, 5, N)
    ho = heldout(S, day, minute, labs)
    T = sum(r["T"] for r in ho)
    J = L.fit_kinetic(S, day, minute, "block", "1")[0]
    segs = L.segments(day, minute, "block")
    nul = np.array([L.fit_kinetic(L.circular_shift(S, segs, rng), day, minute, "block", "1")[0] for _ in range(50)])
    z = (J - nul.mean(0)) / nul.std(0)
    off = ~np.eye(N, dtype=bool)
    return {"scen": scen, "rep": rep, "d31": sum(r["M3"] - r["M1"] for r in ho) / T,
            "d21": sum(r["M2"] - r["M1"] for r in ho) / T, "days_M3_gt_M1": sum(r["M3"] > r["M1"] for r in ho),
            "frac_sig": float((np.abs(z[off]) > 1.96).mean())}


def main():
    jobs = [(s, r) for s in SCEN for r in range(10)]
    with Pool(3) as p:
        res = pl.DataFrame(p.map(job, jobs, chunksize=1))
    res.write_parquet(H.DATA / "validate_heldout.parquet")
    print(res.group_by("scen").agg((pl.col("d31") * 1000).median().round(2).alias("d31_mnats"),
                                   (pl.col("d21") * 1000).median().round(2).alias("d21_mnats"),
                                   pl.col("days_M3_gt_M1").mean(), pl.col("frac_sig").median().round(3)))


if __name__ == "__main__":
    main()
