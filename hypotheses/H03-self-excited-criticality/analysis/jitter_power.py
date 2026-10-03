"""Power calibration of the 10-min jitter test (added 2026-10-03): simulate Hawkes data with known n (0.6 and 0)
from a period's fitted B2 baseline and real windows, jitter within 10-min cells, refit M1_B2_t5. If the test has
power, jittering a true n = 0.6 process should remove most of n_hat.
Output: data/processed/H03-self-excited-criticality/jitter_power.parquet
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/jitter_power.py
"""
from __future__ import annotations

import numpy as np
import polars as pl

from common import DATA, fit_model, fit_path, hc, load, select_goals, specs, write_provenance
from jitter_test import jitter_day

GOALS = [4, 8, 13, 18, 19, 27, 38, 41, 11, 16, 30, 51]


def main():
    days, ev, exo = load()
    dm = hc.make_days(ev, exo, days, "TALK")
    rows = []
    rng = np.random.default_rng(424242)
    for goal in select_goals(GOALS):
        keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
        ds = hc.Dataset(dm, keys, specs()["M1_B2"])
        p = np.load(fit_path(goal, "TALK", "M1_B2"))
        src = hc.FitResult(ds, p, np.nan, None)
        beta = float(np.clip(np.exp(p[ds.layout()[0]["ab"]][1]), 1 / 300, 1 / 10))
        for n_true, scale in ((0.6, 0.4), (0.0, 1.0)):
            for rep in range(2):
                sim = hc.simulate_univariate(src, rng, n_override=n_true, beta_override=beta, base_scale=scale, exo_scale=scale)
                dms = hc.daymap_from_sim(src, sim, dm)
                for kind in ("raw", "jit600"):
                    d2 = dms if kind == "raw" else {k: jitter_day(v, 600.0, rng) for k, v in dms.items()}
                    f = fit_model("M1_B2_t5", hc.Dataset(d2, list(d2), specs()["M1_B2_t5"]))
                    rows.append({"goal_no": goal, "n_true": n_true, "tau_true": 1 / beta, "rep": rep, "kind": kind,
                                 "n_hat": f.summary()["n"]})
        print(goal, flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(DATA / "jitter_power.parquet")
    write_provenance({"jitter_power.parquet": {"built_by": "analysis/jitter_power.py", "goals": GOALS}})
    print(df.group_by("n_true", "kind").agg(pl.col("n_hat").median(), pl.col("n_hat").quantile(0.1).alias("q10"),
                                            pl.col("n_hat").quantile(0.9).alias("q90")).sort("n_true", "kind"))
    w = df.pivot(on="kind", index=["goal_no", "n_true", "rep"], values="n_hat")
    print(w.group_by("n_true").agg((pl.col("raw") - pl.col("jit600")).median().alias("median_drop")))


if __name__ == "__main__":
    main()
