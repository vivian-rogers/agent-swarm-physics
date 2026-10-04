"""H99 Amendment A2 synthetic (post hoc, 2026-10-04): the real talk channel has rho_perp(1) ~ 0 (agent memory below
one minute), outside the A1 synthetic. Same simulator as synthetic.py at tau0 = 0.25 min (and 1 min for reference);
statistic drho_k = rho_c(k) - rho_perp(k)^(1 - g_chi) (collective memory beyond the Glauber prediction).
Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/synthetic_a2.py
"""
from __future__ import annotations

import json
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h99lib as L  # noqa: E402
import synthetic as SY  # noqa: E402


def job(args):
    unit, world, g, tau0, rep = args
    rng = np.random.default_rng(zlib.crc32(f"a2|{unit}|{world}|{g}|{tau0}|{rep}".encode()))
    keeps, rates = SY.load_masks(unit)
    days = [SY.sim_day(k, r, world, tau0, rng, g, "or") for k, r in zip(keeps, rates)]
    b = L.boot(L.binary_sums(days, keeps), B=200, rng=rng)
    return {"unit": unit, "world": world, "g_true": g, "tau0": tau0, "rep": rep,
            **{k: b.get(k) for k in ("g_chi", "g_chi_lo", "rho_c1", "rho_p1", "drho1", "drho1_lo", "drho1_hi", "drho2",
                                     "drho2_lo", "drho2_hi", "dg", "dg2")}}


def main():
    worlds = [("ind", 0.0), ("glauber", 0.2), ("glauber", 0.4), ("fast", 0.0), ("slow", 0.0), ("delay", 0.15)]
    jobs = [(u, w, g, t, r) for u in ("27", "51g") for (w, g) in worlds for t in (0.25, 1.0) for r in range(8)]
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(job, jobs))
    df = pl.DataFrame(res, infer_schema_length=None).with_columns(pl.col("g_true").cast(pl.Float64))
    out = SY.OUT
    df.write_parquet(out / "synthetic_a2.parquet")
    s = (df.group_by("world", "g_true", "tau0").agg(
        pl.col("g_chi").median().round(3), pl.col("rho_p1").median().round(3), pl.col("rho_c1").median().round(3),
        pl.col("drho1").median().round(3), (pl.col("drho1_lo") > 0).mean().round(2).alias("pos1"),
        (pl.col("drho1_hi") < 0).mean().round(2).alias("neg1"), pl.col("drho2").median().round(3),
        (pl.col("drho2_lo") > 0).mean().round(2).alias("pos2"),
        ((pl.col("drho1_hi") - pl.col("drho1_lo")) / 2).median().round(3).alias("hw1")).sort("world", "g_true", "tau0"))
    print(s.write_csv())
    (out / "synthetic_a2_summary.json").write_text(json.dumps(s.to_dicts(), indent=1))


if __name__ == "__main__":
    main()
