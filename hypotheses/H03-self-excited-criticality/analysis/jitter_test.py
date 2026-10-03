"""Surrogate tests for the fine timing (added 2026-10-03 after the synthetic guard showed that B2 is fooled by
>= 10-min rate modulation; see card Notes).

  jit600 / jit120  pooled events re-placed uniformly within their 10-min / 2-min cell of the day (counts per cell
                   kept exactly; agent labels kept). Destroys excitation faster than the cell, keeps slower modulation.
                   Fit: M1_B2_t5 (exp kernel, tau <= 5 min) and M2_grid (n_fast300 = weight on tau <= 300 s).
  shift            each agent's events circularly shifted within the day by +-U(300, 1800) s, independently per agent
                   (keeps each agent's own autocorrelation, breaks cross-agent timing). Fit: M3_sc.

Output: data/processed/H03-self-excited-criticality/jitter_test.parquet
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/jitter_test.py [R]
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool

import numpy as np
import polars as pl

from common import DATA, N_WORKERS, fit_model, hc, load, select_goals, specs, write_output, write_provenance

G = {}


def _init():
    days, ev, exo = load()
    G["days"] = days
    G["dm"] = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}


def jitter_day(d: hc.Day, width, rng):
    cell = np.floor(d.t / width)
    lo = cell * width
    hi = np.minimum(lo + width, d.T)
    t = lo + rng.random(len(d.t)) * (hi - lo)
    o = np.argsort(t, kind="stable")
    return hc.Day(t=t[o], agent=d.agent[o], T=d.T, first=d.first, x=d.x, active=d.active)


def shift_day(d: hc.Day, rng):
    t = d.t.copy()
    for a in np.unique(d.agent):
        m = d.agent == a
        sh = rng.uniform(300, 1800) * rng.choice([-1, 1])
        t[m] = np.mod(t[m] + sh, d.T)
    o = np.argsort(t, kind="stable")
    return hc.Day(t=t[o], agent=d.agent[o], T=d.T, first=d.first, x=d.x, active=d.active)


def summ(f, kind, rep, model, goal, eset):
    s = f.summary()
    return {"goal_no": goal, "set": eset, "kind": kind, "rep": rep, "model": model, "n": s["n"],
            "tau_s": s.get("tau_s", s.get("tau_mean_s", np.nan)), "n_fast300": s.get("n_fast300", np.nan),
            "n_self": s.get("n_self", np.nan), "n_cross": s.get("n_cross", np.nan), "ll": s["ll"],
            "n_self_fast300": s.get("n_self_fast300", np.nan), "n_cross_fast300": s.get("n_cross_fast300", np.nan)}


def run_task(task):
    goal, eset, R = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
    sp = specs()
    rng = np.random.default_rng(97 * goal + (eset == "ALL"))
    rows = []
    for m in ("M1_B2_t5", "M2_grid", "M3_sc"):
        rows.append(summ(fit_model(m, hc.Dataset(dm, keys, sp[m])), "real", 0, m, goal, eset))
    for r in range(R):
        for kind, width in (("jit600", 600.0), ("jit120", 120.0)):
            dmj = {k: jitter_day(dm[k], width, rng) for k in keys}
            for m in ("M1_B2_t5", "M2_grid"):
                rows.append(summ(fit_model(m, hc.Dataset(dmj, keys, sp[m])), kind, r, m, goal, eset))
        dms = {k: shift_day(dm[k], rng) for k in keys}
        rows.append(summ(fit_model("M3_sc", hc.Dataset(dms, keys, sp["M3_sc"])), "shift", r, "M3_sc", goal, eset))
    print(f"jitter goal {goal} {eset}: {time.time() - t0:.0f}s", flush=True)
    return rows


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    days, _, _ = load()
    size = days.group_by("goal_no").agg(pl.col("n_all").sum()).sort("n_all", descending=True)["goal_no"].to_list()
    tasks = [(g, s, R) for g in select_goals(size) for s in ("ALL", "TALK")]
    with Pool(N_WORKERS, initializer=_init) as pool:
        out = pool.map(run_task, tasks, chunksize=1)
    write_output(pl.DataFrame([r for o in out for r in o]), "jitter_test.parquet")
    write_provenance({"jitter_test.parquet": {"built_by": "analysis/jitter_test.py", "R": R,
                                              "surrogates": "jit600, jit120 (pooled within-cell), shift (per-agent "
                                                            "circular +-U(300,1800) s)"}})


if __name__ == "__main__":
    main()
