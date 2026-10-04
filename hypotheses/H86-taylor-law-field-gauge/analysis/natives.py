"""H86 natives on daily statistics (replication/daily.parquet, activity channel):
  N1 NE14  regime II (35, 36a) -> III (36b, 36c, 37): change in daily c_x raw and trimmed; placebos 35 -> 36a, 36b/c -> 37
  N2 NE43  #51: 51f (before 08-05) vs 51g (08-05 .. 08-21) vs 51h + 51i (after 08-21): c_x raw at the bookend stop;
           c_x trim and c_T trim at the nudge stop
Day bootstrap of side means (days resampled within side). Writes natives/natives.json.
Usage: uv run python hypotheses/H86-taylor-law-field-gauge/analysis/natives.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h86lib as L  # noqa: E402

B = 4000
RNG = np.random.default_rng(20261007)


def side(d, units, grid, stat):
    return d.filter(pl.col("unit_id").is_in(units) & (pl.col("grid") == grid))[stat].drop_nans().drop_nulls().to_numpy()


def contrast(d, a, b, grid, stat):
    x, y = side(d, a, grid, stat), side(d, b, grid, stat)
    if len(x) < 1 or len(y) < 1:
        return None
    est = y.mean() - x.mean()
    bs = np.array([RNG.choice(y, len(y)).mean() - RNG.choice(x, len(x)).mean() for _ in range(B)])
    return {"before": float(x.mean()), "after": float(y.mean()), "diff": float(est),
            "ci": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))], "n_days": [len(x), len(y)]}


def main():
    d = pl.read_parquet(L.DATA / "replication/daily.parquet").filter(pl.col("channel") == "activity")
    res = {"NE14": {}, "NE43": {}}
    for grid in ("raw", "trim"):
        for stat in ("c_x", "c_T", "phi"):
            res["NE14"][f"{stat}_{grid}"] = contrast(d, ["35", "36a"], ["36b", "36c", "37"], grid, stat)
            res["NE14"][f"{stat}_{grid}_placebo_II"] = contrast(d, ["35"], ["36a"], grid, stat)
            res["NE14"][f"{stat}_{grid}_placebo_III"] = contrast(d, ["36b", "36c"], ["37"], grid, stat)
            res["NE43"][f"{stat}_{grid}_bookends"] = contrast(d, ["51f"], ["51g"], grid, stat)
            res["NE43"][f"{stat}_{grid}_nudges"] = contrast(d, ["51g"], ["51h", "51i"], grid, stat)
    out = L.DATA / "natives"
    out.mkdir(parents=True, exist_ok=True)
    (out / "natives.json").write_text(json.dumps(res, indent=1, default=float))
    for k, v in res.items():
        for s, r in v.items():
            if r:
                print(k, s, round(r["before"], 4), round(r["after"], 4), round(r["diff"], 4), [round(c, 4) for c in r["ci"]], r["n_days"])


if __name__ == "__main__":
    main()
