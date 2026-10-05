"""Pair-level read-out jumps (for H67's gain reconciliation on identical pairs; written under H50's data folder).
Per non-reserved period unit and directed agent pair (sender -> recipient) with >= 300 ledger reads: the round-1
hop-1 talk jump J1 (h50lib.gate_kernel, K = 1, W = 1.5 x median call interval, shifted-time placebo, block bootstrap),
plus counts. Writes r2/pair_J1.parquet (agent ids are roster codes).

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/r2_pairs.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h50lib as L  # noqa: E402
import r2_relay as RR  # noqa: E402

OUT = RR.OUT
MIN_READS = 300


def main():
    units = pl.read_parquet(OUT / "units.parquet").filter(pl.col("eligible") & (pl.col("kind") == "period_unit"))
    rows = []
    for u, reg, g in zip(units["unit"], units["regime"], units["goal_no"]):
        U, R = RR.load(u)
        c = U["calls"]
        keys = L.call_keys(U)
        W = 1.5 * L.median_call_interval(U)
        y = c["talk"].astype(float)
        snd = R["m_sender"][R["p_msg"]]
        rec = R["p_rec"]
        te, de = R["m_t"][R["p_msg"]], R["m_day"][R["p_msg"]]
        codes = U["agent_codes"]
        ok = snd >= 0
        pk = np.where(ok, snd * 64 + rec, -1)
        uk, cnt = np.unique(pk[ok], return_counts=True)
        for k, n in zip(uk, cnt):
            if n < MIN_READS:
                continue
            s = pk == k
            gk = L.gate_kernel(U, keys, te[s], de[s], rec[s], y, K=1, W=W, nboot=200)
            a, b = int(k // 64), int(k % 64)
            rows.append(dict(unit=u, regime=reg, goal_no=int(g), sender=int(codes[a]), recipient=int(codes[b]),
                             n_reads=int(n), n_named=int(R["p_ment"][s].sum()), J1=float(gk["jumps"][0]),
                             J1_lo=float(gk["j_lo"][0]), J1_hi=float(gk["j_hi"][0]), J1_se=float(gk["k_se"][0]),
                             recipient_talk_rate=float(y[c["agent"] == b].mean())))
        print(u, len([r for r in rows if r["unit"] == u]), "pairs", flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "r2/pair_J1.parquet")
    print(df.height, "rows;", df.group_by("regime").agg(pl.len(), pl.col("J1").median()))


if __name__ == "__main__":
    main()
