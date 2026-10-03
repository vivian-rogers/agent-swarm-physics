"""Event attribution from the fitted M1_B2 model: expected share of events that are baseline (schedule), kickoff,
exogenous (human / nudger messages) or triggered by earlier agent events (sum of posterior responsibilities).
Single process, light.

Output: data/processed/H03-self-excited-criticality/attribution.parquet
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/attribution.py
"""
from __future__ import annotations

import numpy as np
import polars as pl

from common import DATA, fit_path, hc, load, specs, write_provenance


def main():
    days, ev, exo = load()
    rows = []
    for eset in ("TALK", "ALL"):
        dm = hc.make_days(ev, exo, days, eset)
        for goal in sorted(days["goal_no"].unique().to_list()):
            keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
            ds = hc.Dataset(dm, keys, specs()["M1_B2"])
            p = np.load(fit_path(goal, eset, "M1_B2"))
            f = hc.FitResult(ds, p, np.nan, None)
            mu, fixed, ker, _ = f.intensity_parts()
            lam = mu + fixed + ker
            c, s, w = ds.components(p)
            kick = sum(w[k] * ds.F[:, k] for k, nm in enumerate(ds.names) if nm.startswith("kick"))
            exo_ = sum(w[k] * ds.F[:, k] for k, nm in enumerate(ds.names) if nm.startswith("exo"))
            kick = kick if np.ndim(kick) else np.zeros(ds.n)
            exo_ = exo_ if np.ndim(exo_) else np.zeros(ds.n)
            rows.append({"goal_no": goal, "set": eset, "n_events": ds.n, "n_exo_msgs": ds.n_exo_in,
                         "frac_baseline": float((mu / lam).mean()), "frac_kick": float((kick / lam).mean()),
                         "frac_exo": float((exo_ / lam).mean()), "frac_triggered": float((ker / lam).mean())})
    pl.DataFrame(rows).write_parquet(DATA / "attribution.parquet", compression="zstd")
    write_provenance({"attribution.parquet": {"built_by": "analysis/attribution.py", "model": "M1_B2"}})
    t = pl.DataFrame(rows)
    print(t.group_by("set").agg(pl.col("frac_baseline", "frac_kick", "frac_exo", "frac_triggered").median()))


if __name__ == "__main__":
    main()
