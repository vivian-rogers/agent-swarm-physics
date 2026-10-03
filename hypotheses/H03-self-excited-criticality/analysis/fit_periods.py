"""Per-goal-period Hawkes fits (non-holdout only): baseline ladder, kernels, self/cross, KS, day-blocked CV.

Output: data/processed/H03-self-excited-criticality/period_fits.parquet (one row per goal x event set x model)
        data/processed/H03-self-excited-criticality/period_cv.parquet
        data/processed/H03-self-excited-criticality/fits/<goal>_<set>_<model>.npy  (parameter vectors)
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/fit_periods.py
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool

import numpy as np
import polars as pl

from common import (DATA, FITS, fit_path, select_goals, write_output, N_WORKERS, fit_model, hc, load, period_meta, specs, write_provenance)

KS_MODELS = ["M1_B2", "P_B2", "M1_B0", "P_B0", "M1_B3", "P_B3", "M2_grid", "M1_B2_t30"]
CV_MODELS = ["M1_B2", "M1_B2_t30", "P_B2", "M2_grid", "M1_B1", "P_B1", "M1_B3", "P_B3", "M1_B3_2h", "P_B3_2h",
             "M3_sc", "M3_self", "P_B2a"]
G = {}


def _init():
    days, ev, exo = load()
    G["days"] = days
    G["dm"] = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}


def cv_period(dm, keys, goal, eset, seed=0, k=5):
    rng = np.random.default_rng(seed + goal)
    pool = [kk for kk in keys if not dm[kk].first]
    if len(pool) < 2 or len(keys) < 3:
        return []
    folds = np.array_split(rng.permutation(pool), min(k, len(pool)))
    sp = specs()
    rows = []
    for fi, fold in enumerate(folds):
        fold = list(fold)
        train = [kk for kk in keys if kk not in fold]
        for name in CV_MODELS:
            ds = hc.Dataset(dm, train, sp[name])
            if ds.n == 0:
                continue
            f = fit_model(name, ds)
            # (M3_self: transfer copies the pinned cross weights ~e^-30, so held-out eval stays self-only)
            ll, n = hc.eval_heldout(f, dm, fold)
            rows.append({"goal_no": goal, "set": eset, "fold": fi, "model": name, "ll_test": ll, "n_test": n})
    return rows


def run_task(task):
    goal, eset = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
    meta = period_meta(days, keys)
    rows = []
    for name, spec in specs().items():
        ds = hc.Dataset(dm, keys, spec)
        if ds.n < 20:
            continue
        f = fit_model(name, ds)
        fit_path(goal, eset, name).parent.mkdir(parents=True, exist_ok=True)
        np.save(fit_path(goal, eset, name), f.p)
        s = f.summary()
        s.update({"goal_no": goal, "set": eset, "model": name, **meta})
        if name in ("M1_B2", "M1_B2_t30"):
            s["n_prof_lo"], s["n_prof_hi"] = hc.profile_ci_n(f)
        if name in KS_MODELS:
            z = f.rescaled_intervals()
            s["ks_D"], s["ks_p"] = hc.ks_exp1(z)
            s["ks_D_late"], _ = hc.ks_exp1(z[z.size // 2:]) if z.size > 40 else (np.nan, np.nan)
        rows.append(s)
    cv = cv_period(dm, keys, goal, eset)
    print(f"goal {goal} {eset}: {len(rows)} fits, {len(cv)} cv rows, {time.time() - t0:.0f}s", flush=True)
    return rows, cv


def run_cv_only(task):
    goal, eset = task
    days, dm = G["days"], G["dm"][eset]
    keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
    return cv_period(dm, keys, goal, eset)


def main_cv_only():
    days, _, _ = load()
    size = days.group_by("goal_no").agg(pl.col("n_all").sum()).sort("n_all", descending=True)["goal_no"].to_list()
    tasks = [(g, s) for g in select_goals(size) for s in ("ALL", "TALK")]
    with Pool(N_WORKERS, initializer=_init) as pool:
        out = pool.map(run_cv_only, tasks, chunksize=1)
    write_output(pl.DataFrame([r for o in out for r in o]), "period_cv.parquet")
    write_provenance({"period_cv.parquet": {"built_by": "analysis/fit_periods.py --cv-only",
                                            "scheme": "5-fold day-blocked; goal's first day always in train; "
                                                      "test-day unit levels refit, all else fixed; transferred "
                                                      "within-day shape floored at median/20"}})


def main():
    if "--cv-only" in sys.argv:
        return main_cv_only()
    FITS.mkdir(parents=True, exist_ok=True)
    days, _, _ = load()
    goals = sorted(days["goal_no"].unique().to_list())
    # biggest first for load balance
    size = days.group_by("goal_no").agg(pl.col("n_all").sum()).sort("n_all", descending=True)["goal_no"].to_list()
    size = select_goals(size)
    tasks = [(g, s) for g in size for s in ("ALL", "TALK")]
    with Pool(N_WORKERS, initializer=_init) as pool:
        out = pool.map(run_task, tasks, chunksize=1)
    rows = [r for o in out for r in o[0]]
    cvs = [r for o in out for r in o[1]]
    write_output(pl.DataFrame(rows, infer_schema_length=None), "period_fits.parquet")
    write_output(pl.DataFrame(cvs), "period_cv.parquet")
    write_provenance({"period_fits.parquet": {"built_by": "analysis/fit_periods.py", "goals": goals,
                                              "models": list(specs())},
                      "period_cv.parquet": {"built_by": "analysis/fit_periods.py",
                                            "scheme": "5-fold day-blocked; goal's first day always in train; "
                                                      "test-day unit levels refit, all else fixed"}})


if __name__ == "__main__":
    main()
