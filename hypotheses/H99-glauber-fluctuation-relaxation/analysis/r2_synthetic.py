"""H99 round 2 synthetic validation on real call skeletons (before real data).

Worlds (README Round 2, "Nulls and validation"): W0 independent talk at the real calls; W1a/W1b hop-1 read-out coupling
g1 = 0.13 / 0.30; W2 one-call-delayed coupling (hop 2) g = 0.13; W3 slow village-wide drive (OU 5 min); W4 the same
drive per room; W5 fast village field (15 s). Each replicate runs the minute-grid removal stack with the room partition
and the call-clock kernel. Output: data/processed/H99-glauber-fluctuation-relaxation/r2/synthetic/runs.parquet.

Usage: uv run python .../r2_synthetic.py [--units 38a,41,51c,51g] [--reps 6] [--worlds W0,W1a,...] [--calib]
"""
from __future__ import annotations

import argparse
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as R  # noqa: E402
import r2run as RR  # noqa: E402

OUT = RR.R2 / "synthetic"
WORLDS = {
    "W0": {},
    "W1a": {"g1": 0.13},
    "W1b": {"g1": 0.30},
    "W2": {"g1": 0.13, "hop": 2},
    "W3": {"drive_amp": 0.5, "drive_tau": 300.0},
    "W4": {"drive_amp": 0.5, "drive_tau": 300.0, "drive_room": True},
    "W5": {"fast_amp": 0.6, "fast_tau": 15.0},
}


def one(args):
    uid, world, rep, params = args
    meta, calls, msgs, exo, ws = RR.load_unit(uid)
    sk = R.skeleton(calls, msgs)
    rng = np.random.default_rng(zlib.crc32(f"{uid}|{world}|{rep}".encode()))
    Cs, Ms = R.simulate(sk, rng, r_bar=meta["r_bar"], **params)
    row = {"unit": uid, "world": world, "rep": rep, **{f"p_{k}": float(v) for k, v in params.items()}}
    V = RR.call_grid_variants(Cs, exo, ws)
    row.update(RR.minute_stats(V, rng, B=200))
    r1, _ = RR.r1_stats(Cs, Ms, meta, rng, B=200)
    row.update({f"r1_{k}": v for k, v in r1.items()})
    return {k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v) for k, v in row.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="38a,41,51c,51g")
    ap.add_argument("--reps", type=int, default=6)
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--out", default="runs")
    ap.add_argument("--set", default="", help="override params, e.g. drive_amp=1.2")
    a = ap.parse_args()
    over = {}
    for kv in filter(None, a.set.split(",")):
        k, v = kv.split("=")
        over[k] = float(v) if k != "drive_room" else bool(int(v))
    jobs = [(u, w, r, {**WORLDS[w], **over}) for u in a.units.split(",") for w in a.worlds.split(",") for r in range(a.reps)]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(2) as ex:
        for row in ex.map(one, jobs):
            rows.append(row)
            print(row["unit"], row["world"], int(row["rep"]), f"V0 drho1 {row.get('V0_drho1', np.nan):+.3f}",
                  f"V5 {row.get('V5_drho1', np.nan):+.3f}", f"g_chi {row.get('V0_g_chi', np.nan):+.3f}",
                  f"Pi {row.get('V0_pair_r1_same', np.nan):+.3f}/{row.get('V0_pair_r1_cross', np.nan):+.3f}",
                  f"J1 {row.get('r1_J1_inflight', np.nan):+.4f} J2 {row.get('r1_J2_room', np.nan):+.4f}", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    p = OUT / f"{a.out}.parquet"
    if p.exists() and a.out != "runs_calib":
        old = pl.read_parquet(p)
        key = df.select("unit", "world").unique()
        old = old.join(key, on=["unit", "world"], how="anti")
        df = pl.concat([old, df], how="diagonal_relaxed")
    df.write_parquet(p)


if __name__ == "__main__":
    main()
