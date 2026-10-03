"""Cascade-size distributions (axis D, signature s^-3/2).

1. Reconstructed cascades: sample the branching structure of the fitted M1_B2 model (each event's parent drawn from
   its posterior: immigrant vs. triggered; triggered parent ∝ kernel weight). Model-conditioned, so agreement with
   Borel(n) is partly by construction; the tail shape still depends on the data's clustering.
2. Model-free bursts: runs of pooled events separated by gaps <= g (g = 60 s, 300 s). Compared between the real data,
   simulations of the fitted Hawkes model, and simulations of the inhomogeneous-Poisson null (P_B2). This statistic
   is not fitted, so it is an unfitted-prediction test.

Output: data/processed/H03-self-excited-criticality/cascades.parquet (goal, set, source, gap, size, count)
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/cascades.py
"""
from __future__ import annotations

import time
from multiprocessing import Pool

import numpy as np
import polars as pl

from common import DATA, FITS, N_WORKERS, fit_path, hc, load, select_goals, specs, write_output, write_provenance

GAPS = [60.0, 300.0]
R_SIM = 5
G = {}


def _init():
    days, ev, exo = load()
    G["days"] = days
    G["dm"] = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}


def hist_rows(goal, eset, source, gap, sizes):
    v, c = np.unique(sizes, return_counts=True)
    return [{"goal_no": goal, "set": eset, "source": source, "gap": gap, "size": int(a), "count": int(b)}
            for a, b in zip(v, c)]


def run_task(task):
    goal, eset = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
    sp = specs()
    rng = np.random.default_rng(31 * goal + (eset == "ALL"))
    rows = []
    fits = {}
    for m in ("M1_B2", "P_B2"):
        ds = hc.Dataset(dm, keys, sp[m])
        p = np.load(fit_path(goal, eset, m))
        fits[m] = hc.FitResult(ds, p, np.nan, None)
    f = fits["M1_B2"]
    rows += hist_rows(goal, eset, "reconstructed", 0.0, hc.reconstruct_cascades(f, rng, n_samples=5))
    ds = f.ds
    for gap in GAPS:
        rows += hist_rows(goal, eset, "data", gap, hc.burst_sizes(ds.t, ds.day, gap))
    for src_name, m in (("sim_hawkes", "M1_B2"), ("sim_poisson", "P_B2")):
        acc = {g: [] for g in GAPS}
        for _ in range(R_SIM):
            sim = hc.simulate_univariate(fits[m], rng)
            t = np.concatenate([sim[d] for d in range(ds.D)])
            day = np.repeat(np.arange(ds.D), [len(sim[d]) for d in range(ds.D)])
            for gap in GAPS:
                acc[gap].append(hc.burst_sizes(t, day, gap))
        for gap in GAPS:
            rows += hist_rows(goal, eset, src_name, gap, np.concatenate(acc[gap]))
    print(f"cascades goal {goal} {eset}: {time.time() - t0:.0f}s", flush=True)
    return rows


def main():
    days, _, _ = load()
    goals = sorted(days["goal_no"].unique().to_list(), reverse=True)
    tasks = [(g, s) for g in select_goals(goals) for s in ("ALL", "TALK")]
    with Pool(N_WORKERS, initializer=_init) as pool:
        out = pool.map(run_task, tasks, chunksize=1)
    write_output(pl.DataFrame([r for o in out for r in o]), "cascades.parquet")
    write_provenance({"cascades.parquet": {"built_by": "analysis/cascades.py", "gaps_s": GAPS, "R_sim": R_SIM,
                                           "reconstruction_samples": 5}})


if __name__ == "__main__":
    main()
