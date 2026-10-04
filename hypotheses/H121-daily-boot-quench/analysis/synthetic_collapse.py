"""H121 Amendment A1 calibration (before real data): between-day dispersion of ln tau_d as the collapse statistic.
Worlds F (homogeneous field lifetime 30 calls) and H (log-uniform x1/3..x3 per day) on units 27, 41, 51c.
Statistic: DerSimonian-Laird between-day SD of ln tau_d over resolved days (agent-bootstrap SEs).
Output: data/processed/H121-daily-boot-quench/synthetic/collapse_A1.json
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h121lib as L  # noqa: E402

D = HERE.parents[2] / "data/processed/H121-daily-boot-quench"


def between_sd(days):
    res = [d for d in days if d.get("resolved")]
    if len(res) < 3:
        return np.nan, len(res)
    lt = np.log([d["tau"] for d in res])
    se = np.array([(np.log(d["tau_hi"]) - np.log(d["tau_lo"])) / 3.92 for d in res])
    _, _, t2 = L.re_pool(lt, se)
    return float(np.sqrt(t2)), len(res)


def run(unit, reps=8):
    df = pl.read_parquet(D / "calls" / f"{unit}.parquet").filter(pl.col("k") <= 700)
    K = int(pl.read_parquet(D / "unit_meta.parquet").filter(pl.col("unit_id") == unit)["K_max"][0])
    out = []
    for w in ("F", "H"):
        for r in range(reps):
            rng = np.random.default_rng(1000 + r)
            days = df["day"].unique().to_list()
            ft = {d: float(30 * np.exp(rng.uniform(np.log(1 / 3), np.log(3)))) for d in days} if w == "H" else 30.0
            sim = L.simulate_unit(df, rng, rho=0.5, g=0.13, F_amp=0.25, F_tau=ft)
            fits = [L.day_fit(sim.filter(pl.col("day") == d), K, 30, rng) for d in sorted(days)]
            sd, n = between_sd(fits)
            out.append({"unit": unit, "world": w, "rep": r, "sd_between": sd, "n_resolved": n})
    return out


if __name__ == "__main__":
    rows = []
    with ProcessPoolExecutor(max_workers=2) as ex:
        for o in ex.map(run, ["27", "41", "51c"]):
            rows += o
    df = pl.DataFrame(rows)
    s = df.group_by("world").agg(pl.col("sd_between").median().alias("med"), (pl.col("sd_between") <= np.log(2) / 1.96).mean().alias("holds"),
                                 pl.col("n_resolved").median())
    print(s)
    (D / "synthetic/collapse_A1.json").write_text(json.dumps({"reps": rows, "summary": s.to_dicts()}, indent=1, default=float))
