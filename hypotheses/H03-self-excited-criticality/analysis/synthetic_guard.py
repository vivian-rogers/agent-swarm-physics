"""Synthetic guard (axis F): does the pipeline return n ~ 0 on non-self-exciting data with village sampling,
and recover a known n? Each scenario reuses a period's real day windows, exogenous message times and the fitted
M1_B2 baseline.

Scenarios (R replicates per goal x set):
  n0        inhomogeneous Poisson from the fitted B2 baseline + kick + exo response; fit M1_B2, M1_B0, M1_B3, M2_grid
  n0_fine   inhomogeneous Poisson whose rate is the REAL per-day 10-min count / 600 s (finer than B2 can represent;
            it also imprints real clustering at >= 10 min); fit M1_B2, M1_B3
  n06       Hawkes n = 0.6, beta = fitted beta (clipped to [1/1000, 1/5]), baseline and exo scaled by 0.4; fit M1_B2
  n09       Hawkes n = 0.9, baseline and exo scaled by 0.1; fit M1_B2

Output: data/processed/H03-self-excited-criticality/synthetic_guard.parquet
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/synthetic_guard.py [R]
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool

import numpy as np
import polars as pl

from common import BETA_STARTS, DATA, FITS, N_WORKERS, fit_model, hc, load, specs, write_provenance

G = {}


def _init():
    days, ev, exo = load()
    G["days"] = days
    G["dm"] = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}


def fine_rates(ds, width=600.0):
    K = int(np.ceil(ds.T.max() / width))
    cnt = np.zeros((ds.D, K))
    np.add.at(cnt, (ds.day, np.minimum((ds.t // width).astype(int), K - 1)), 1)
    lens = np.clip(ds.T[:, None] - width * np.arange(K)[None, :], 0, width)
    return np.where(lens > 0, cnt / np.maximum(lens, 1e-9), 0.0)


def run_task(task):
    goal, eset, R = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
    sp = specs()
    ds = hc.Dataset(dm, keys, sp["M1_B2"])
    p = np.load(FITS / f"{goal}_{eset}_M1_B2.npy")
    src = hc.FitResult(ds, p, np.nan, None)
    beta_hat = float(np.exp(p[ds.layout()[0]["ab"]][1]))
    beta_sim = float(np.clip(beta_hat, 1 / 1000, 1 / 5))
    mu_fine = fine_rates(ds)
    rng = np.random.default_rng(7 * goal + (eset == "ALL"))
    rows = []
    scen = {
        "n0": (dict(n_override=0.0), ["M1_B2", "M1_B0", "M1_B3", "M2_grid"], 0.0),
        "n0_fine": (dict(n_override=0.0, mu_db_override=mu_fine, bin_override=600.0, kick_scale=0.0, exo_scale=0.0),
                    ["M1_B2", "M1_B3"], 0.0),
        "n06": (dict(n_override=0.6, beta_override=beta_sim, base_scale=0.4, exo_scale=0.4), ["M1_B2"], 0.6),
        "n09": (dict(n_override=0.9, beta_override=beta_sim, base_scale=0.1, exo_scale=0.1), ["M1_B2"], 0.9),
    }
    for r in range(R):
        for sname, (kw, models, n_true) in scen.items():
            sim = hc.simulate_univariate(src, rng, **kw)
            dms = hc.daymap_from_sim(src, sim, dm)
            for m in models:
                dss = hc.Dataset(dms, list(range(ds.D)), sp[m])
                if dss.n < 20:
                    continue
                f = fit_model(m, dss, beta_starts=BETA_STARTS)
                s = f.summary()
                rows.append({"goal_no": goal, "set": eset, "scenario": sname, "rep": r, "model": m,
                             "n_true": n_true, "beta_true": beta_sim if n_true > 0 else np.nan,
                             "n_hat": s["n"], "tau_hat": s.get("tau_s", s.get("tau_mean_s", np.nan)),
                             "n_events": dss.n, "n_events_real": ds.n})
    print(f"guard goal {goal} {eset}: {len(rows)} fits, {time.time() - t0:.0f}s", flush=True)
    return rows


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    days, _, _ = load()
    size = days.group_by("goal_no").agg(pl.col("n_all").sum()).sort("n_all", descending=True)["goal_no"].to_list()
    tasks = [(g, s, R) for g in size for s in ("ALL", "TALK")]
    with Pool(N_WORKERS, initializer=_init) as pool:
        out = pool.map(run_task, tasks, chunksize=1)
    pl.DataFrame([r for o in out for r in o]).write_parquet(DATA / "synthetic_guard.parquet", compression="zstd")
    write_provenance({"synthetic_guard.parquet": {"built_by": "analysis/synthetic_guard.py", "R": R}})


if __name__ == "__main__":
    main()
