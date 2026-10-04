"""H124 synthetic validation (axis F), before any real-data error is computed.

S4: N = 4 asynchronous kinetic Ising on the real per-call schedules of 4c and 6b (order only), J_ii in {0.5, 1.5},
    off-diagonal N(0, s^2) asymmetric with s in {0.1, 0.3, 0.6}; 20 worlds per cell.
S21: N = 21 on the first 10 non-holdout #51 days (order only, 21 most frequent callers), sparse directed J
    (3 partners per agent, |J| = s x U(0.5, 1.5), random sign), s in {0.15, 0.5}, J_ii in {0.5, 1.5}; 10 worlds per cell.
Errors of ML, nMF, TAP, MS against the true J, and of the approximations against ML.

Output: data/processed/H124-small-n-meanfield-benchmark/synthetic/{s4,s21}.parquet
Usage: uv run python hypotheses/H124-small-n-meanfield-benchmark/analysis/synthetic.py [--only s4|s21]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h124lib as L  # noqa: E402


def world_J(N, s, jii, rng, sparse=None):
    if sparse is None:
        J = rng.normal(0, s, (N, N))
    else:
        J = np.zeros((N, N))
        for i in range(N):
            part = rng.choice([j for j in range(N) if j != i], sparse, replace=False)
            J[i, part] = s * rng.uniform(0.5, 1.5, sparse) * rng.choice([-1, 1], sparse)
    np.fill_diagonal(J, jii)
    h = np.full(N, np.arctanh(-0.5) + 0.5 * jii)
    return h, J


def evaluate(rows, N, J_true):
    res = L.fit_all(rows, N)
    et = L.errors(res, J_true=J_true)
    em = L.errors(res)
    out = {}
    for k in ("ML",) + L.METHODS:
        out[f"{k}_epsJ_true"] = et[k]["epsJ"]
        out[f"{k}_epsS_true"] = et[k]["eps_sigma"]
        out[f"{k}_shrink_true"] = et[k].get("shrink", np.nan)
    for k in L.METHODS:
        out[f"{k}_epsJ_ml"] = em[k]["epsJ"]
        out[f"{k}_epsS_ml"] = em[k]["eps_sigma"]
        out[f"{k}_ok"] = em[k]["ok_rows"]
        out[f"{k}_cover"] = em[k]["cover"]
    return out


def run_s4(rng):
    rows = []
    t0 = time.time()
    for unit in ("4c", "6b"):
        sched = L.actor_days_from_percall(unit)
        for jii in (0.5, 1.5):
            for s in (0.1, 0.3, 0.6):
                for w in range(20):
                    h, J = world_J(4, s, jii, rng)
                    sim = L.simulate_percall(sched, h, J, rng, R=1)[0]
                    rows.append({"schedule": unit, "Jii": jii, "s": s, "world": w, **evaluate(sim, 4, J)})
                df = pl.DataFrame(rows).filter((pl.col("schedule") == unit) & (pl.col("Jii") == jii) & (pl.col("s") == s))
                print(unit, jii, s, {c: round(df[c].median(), 3) for c in df.columns if c.endswith(("_true", "_ml"))
                                     and "epsJ" in c}, f"{time.time() - t0:.0f}s", flush=True)
    return pl.DataFrame(rows)


def run_s21(rng):
    z = np.load(L.OUT / "schedule_51head.npz")
    sched = [(k, z[k]) for k in sorted(z.files)]
    N = 21
    rows = []
    t0 = time.time()
    for jii in (0.5, 1.5):
        for s in (0.15, 0.5):
            worlds = [world_J(N, s, jii, rng, sparse=3) for _ in range(10)]
            # different J per world: simulate one at a time in a batch of 1 (R=1) to keep J per world
            for w, (h, J) in enumerate(worlds):
                sim = L.simulate_percall(sched, h, J, rng, R=1)[0]
                rows.append({"Jii": jii, "s": s, "world": w, **evaluate(sim, N, J)})
            df = pl.DataFrame(rows).filter((pl.col("Jii") == jii) & (pl.col("s") == s))
            print("S21", jii, s, {c: round(df[c].median(), 3) for c in df.columns if "epsJ" in c},
                  f"{time.time() - t0:.0f}s", flush=True)
    return pl.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    (L.OUT / "synthetic").mkdir(exist_ok=True)
    rng = np.random.default_rng(20261004)
    if a.only in ("", "s4"):
        run_s4(rng).write_parquet(L.OUT / "synthetic/s4.parquet")
    if a.only in ("", "s21"):
        run_s21(rng).write_parquet(L.OUT / "synthetic/s21.parquet")


if __name__ == "__main__":
    main()
