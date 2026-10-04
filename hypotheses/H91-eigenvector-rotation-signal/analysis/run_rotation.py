"""H91: eigenvector rotation between consecutive non-holdout active days, every channel and variant.

For each non-holdout active day b with a previous calendar active day a that is also non-holdout (as H36's R1),
restrict both day matrices to the agents eligible on both (|A| >= 4) and compute delta_k (k = 1, 2, 3), the same-day
block-bootstrap null (primary, Amendment 1) and the re-centered pooled-split null (secondary), R = 199.
Channels: content_{bge,gte} (primary), content_*_style_resid_period, content_*_restate (variants), talk (all-present
window, talk-eligible agents on both days).
Output: data/processed/H91-eigenvector-rotation-signal/rotation.parquet
Usage: uv run python hypotheses/H91-eigenvector-rotation-signal/analysis/run_rotation.py [--R 199]
"""
from __future__ import annotations

import argparse
import time
import zlib

import numpy as np
import polars as pl

import h91lib as L

DM = L.DM
CHANNELS = ["content_bge", "content_gte", "content_bge_style_resid_period", "content_gte_style_resid_period",
            "content_bge_restate", "content_gte_restate", "talk"]


def day_pairs() -> list[tuple[str, str]]:
    """(a, b) = (previous calendar active day, day) with both non-holdout. Held-out days are read only as dates
    (calendar.holdout) to break the chain; nothing else about them is touched."""
    cal = pl.read_parquet(DM.SH / "calendar.parquet").filter(pl.col("goal_no").is_not_null()).sort("pt_date")
    d, h = cal["pt_date"].to_list(), cal["holdout"].to_list()
    return [(d[i - 1], d[i]) for i in range(1, len(d)) if not h[i] and not h[i - 1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--R", type=int, default=L.R_NULL)
    a = ap.parse_args()
    t0 = time.time()
    pairs = day_pairs()
    rows = []
    for ch in CHANNELS:
        days = DM.load_days(L.OUT / ("spins.npz" if ch == "talk" else f"{ch}.npz"))
        for da, db in pairs:
            if da not in days or db not in days:
                continue
            A, B = days[da], days[db]
            if ch == "talk":
                aa, ab_ = A["agents"][A["talk_ok"]], B["agents"][B["talk_ok"]]
            else:
                aa, ab_ = A["agents"], B["agents"]
            common = np.intersect1d(aa, ab_)
            if len(common) < DM.MIN_AGENTS:
                continue
            ia, ib = np.searchsorted(A["agents"], common), np.searchsorted(B["agents"], common)
            rng = np.random.default_rng(zlib.crc32(f"{ch}|{db}".encode()) + L.SEED)
            if ch == "talk":
                r = L.rot_spins(A["talk"][ia], A["minutes"], B["talk"][ib], B["minutes"], rng, R=a.R)
                size = {"La": int(A["talk"].shape[1]), "Lb": int(B["talk"].shape[1])}
            else:
                r = L.rot_content(A["Z"][ia], B["Z"][ib], rng, R=a.R)
                size = {"La": int(A["Z"].shape[1]), "Lb": int(B["Z"].shape[1])}
            rows.append({"channel": ch, "day_a": da, "pt_date": db, "n_a": int(len(A["agents"])), "n_b": int(len(B["agents"])),
                         **size, **r})
        print(f"{ch}: {sum(1 for x in rows if x['channel'] == ch)} pairs ({time.time() - t0:.0f}s)", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    cal = DM.calendar().select("pt_date", "goal_no", "regime", "unit_id")
    df = df.join(cal, on="pt_date", how="left").join(
        cal.select(pl.col("pt_date").alias("day_a"), pl.col("goal_no").alias("goal_a")), on="day_a", how="left")
    df.write_parquet(L.OUT / "rotation.parquet", compression="zstd")
    print(f"done: {df.height} rows in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
