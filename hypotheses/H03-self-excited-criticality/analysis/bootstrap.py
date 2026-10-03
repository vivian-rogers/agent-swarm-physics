"""Day-level bootstrap for the per-period fits (resample a period's village days with replacement; each copy is a
separate realization with its own day-level baseline). Warm-started from the point estimate.

Output: data/processed/H03-self-excited-criticality/period_boot.parquet (one row per goal x set x model x replicate)
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/bootstrap.py [B_M1] [B_other]
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool

import numpy as np
import polars as pl

from common import DATA, FITS, N_WORKERS, fit_model, fit_path, hc, load, select_goals, specs, write_output, write_provenance

MODELS = {"M1_B2": None, "M1_B2_t30": None, "M2_grid": None, "M3_sc": None}
G = {}


def _init():
    days, ev, exo = load()
    G["days"] = days
    G["dm"] = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}


def point_fit(dm, keys, goal, eset, name):
    spec = specs()[name]
    ds = hc.Dataset(dm, keys, spec)
    p = np.load(fit_path(goal, eset, name))
    return hc.FitResult(ds, p, ds.loglik(p, grad=False), None)


def run_task(task):
    goal, eset, B = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
    rng = np.random.default_rng(1000 * goal + (eset == "ALL"))
    rows = []
    if len(keys) < 3:
        return rows
    for name in MODELS:
        if not (fit_path(goal, eset, name)).exists():
            continue
        src = point_fit(dm, keys, goal, eset, name)
        nb = B[0] if name.startswith("M1") else B[1]
        if days.filter(pl.col("goal_no") == goal)["n_all"].sum() > 30000:   # #51 whole period: cap (its drift
            nb = max(nb // 3, 10)                                           # test uses the block bootstrap)
        for b in range(nb):
            bk = list(rng.choice(keys, len(keys), replace=True))
            ds = hc.Dataset(dm, bk, specs()[name])
            if ds.n < 20:
                continue
            p0, _ = hc.transfer_params(src, ds)
            f = fit_model(name, ds, p0=p0, beta_starts=[1 / 10, 1 / 1000] if ds.free_beta else None)
            s = f.summary()
            rows.append({"goal_no": goal, "set": eset, "model": name, "rep": b, "n": s["n"],
                         "tau_s": s.get("tau_s", s.get("tau_mean_s", np.nan)),
                         "n_self": s.get("n_self", np.nan), "n_cross": s.get("n_cross", np.nan),
                         "n_fast300": s.get("n_fast300", np.nan),
                         "n_cross_fast300": s.get("n_cross_fast300", np.nan),
                         "n_self_fast300": s.get("n_self_fast300", np.nan)})
    print(f"boot goal {goal} {eset}: {len(rows)} reps, {time.time() - t0:.0f}s", flush=True)
    return rows


def main():
    B1 = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    B2 = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    days, _, _ = load()
    size = days.group_by("goal_no").agg(pl.col("n_all").sum()).sort("n_all", descending=True)["goal_no"].to_list()
    tasks = [(g, s, (B1, B2)) for g in select_goals(size) for s in ("ALL", "TALK")]
    with Pool(N_WORKERS, initializer=_init) as pool:
        out = pool.map(run_task, tasks, chunksize=1)
    rows = [r for o in out for r in o]
    write_output(pl.DataFrame(rows), "period_boot.parquet")
    write_provenance({"period_boot.parquet": {"built_by": "analysis/bootstrap.py", "B_M1": B1, "B_other": B2,
                                              "scheme": "resample village days with replacement within period; "
                                                        "periods with < 3 days skipped"}})


if __name__ == "__main__":
    main()
