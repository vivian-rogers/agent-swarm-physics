"""Bin-width robustness (axis F): refit KI-1 block vs N1 on 2-min bins (active if active in either minute)
and compare with the 1-min results in real_couplings.parquet (est = block_N1).
Output: data/processed/H02-couplings-are-real/binwidth.parquet (per chunk agreement stats)
"""
from __future__ import annotations

import os
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl

import h02lib as L
from calibrate import load_chunks

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H02-couplings-are-real"
NSURR = 50


def coarsen(S, day, minute, w=2):
    rows, dd, mm = [], [], []
    for d in np.unique(day):
        idx = np.flatnonzero(day == d)
        n = idx.size // w
        blk = S[idx[:n * w]].reshape(n, w, -1).max(1)  # +1 if any minute active
        rows.append(blk); dd.append(np.full(n, d)); mm.append(np.arange(n))
    return np.vstack(rows), np.concatenate(dd), np.concatenate(mm)


def job(args):
    ch, c = args
    L.BLOCK_MIN, L.MIN_LAST_BLOCK = 15, 5  # 30 min in 2-min bins
    S2, d2, m2 = coarsen(c["S"], c["day"], c["minute"])
    rng = np.random.default_rng([42, int(ch[1:3]), int(ch[-1])])
    J = L.fit_kinetic(S2, d2, m2, "block", "1")[0]
    segs = L.segments(d2, m2, "block")
    nul = np.array([L.fit_kinetic(L.circular_shift(S2, segs, rng), d2, m2, "block", "1")[0] for _ in range(NSURR)])
    z = (J - nul.mean(0)) / nul.std(0)
    a = c["agents"]
    return [{"chunk": ch, "i": a[i], "j": a[j], "J2": float(J[i, j]), "z2": float(z[i, j])}
            for i in range(len(a)) for j in range(len(a)) if i != j]


def main():
    chunks = load_chunks()
    with Pool(3) as pool:
        out = pool.map(job, sorted(chunks.items()), chunksize=1)
    two = pl.DataFrame([r for o in out for r in o])
    one = pl.read_parquet(DATA / "real_couplings.parquet").filter(pl.col("est") == "block_N1").select("chunk", "i", "j", "J", "z")
    m = one.join(two, on=["chunk", "i", "j"])
    summ = (m.group_by("chunk").agg(
        pl.corr("J", "J2").alias("corr_J"),
        ((pl.col("z").abs() > 1.96) & (pl.col("z2").abs() > 1.96)).sum().alias("n_sig_both"),
        (pl.col("z").abs() > 1.96).sum().alias("n_sig_1"), (pl.col("z2").abs() > 1.96).sum().alias("n_sig_2"),
        (((pl.col("z").abs() > 1.96) & (pl.col("z2").abs() > 1.96)) & (pl.col("J").sign() == pl.col("J2").sign())).sum().alias("n_same_sign"),
        ((pl.col("z").abs() > 1.96) & (pl.col("J").sign() == pl.col("J2").sign())).sum().alias("n_sig1_same_sign_any"),
    ).sort("chunk"))
    summ.write_parquet(DATA / "binwidth.parquet")
    with pl.Config(tbl_rows=30):
        print(summ)
    tot = summ.select(pl.col("n_sig_1").sum(), pl.col("n_sig1_same_sign_any").sum(), pl.col("n_sig_both").sum(),
                      pl.col("n_same_sign").sum(), pl.col("corr_J").median())
    print(tot)


if __name__ == "__main__":
    main()
