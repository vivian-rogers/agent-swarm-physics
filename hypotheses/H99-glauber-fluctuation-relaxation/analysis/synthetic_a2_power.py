"""H99 A2 power check (post hoc, 2026-10-04): the fast-field and slow-field worlds of synthetic_a2.py at field sizes
that give g_chi ~ 0.1-0.3 (the real talk range), tau0 = 0.25 min, units 27 and 51g, 8 replicates.
Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/synthetic_a2_power.py
"""
from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h99lib as L  # noqa: E402
import synthetic as SY  # noqa: E402

rows = []
for world, amp in (("fast", 0.4), ("fast", 0.6), ("slow", 0.25), ("slow", 0.35)):
    SY.A_FIELD[world] = amp
    for unit in ("27", "51g"):
        keeps, rates = SY.load_masks(unit)
        for rep in range(8):
            rng = np.random.default_rng(zlib.crc32(f"pw|{world}|{amp}|{unit}|{rep}".encode()))
            days = [SY.sim_day(k, r, world, 0.25, rng, 0.0, "or") for k, r in zip(keeps, rates)]
            b = L.boot(L.binary_sums(days, keeps), B=200, rng=rng)
            rows.append({"world": world, "amp": amp, "unit": unit, "rep": rep, **{k: b.get(k) for k in
                         ("g_chi", "g_chi_lo", "drho1", "drho1_lo", "drho1_hi", "drho2", "drho2_lo")}})
df = pl.DataFrame(rows)
df.write_parquet(SY.OUT / "synthetic_a2_power.parquet")
s = df.group_by("world", "amp").agg(pl.col("g_chi").median().round(3), (pl.col("g_chi_lo") > 0).mean().alias("g_res"),
                                    pl.col("drho1").median().round(3),
                                    ((pl.col("drho1") <= -0.03) & (pl.col("drho1_hi") < 0)).mean().alias("fast_call"),
                                    (((pl.col("drho1") >= 0.03) & (pl.col("drho1_lo") > 0)) | ((pl.col("drho2") >= 0.03) & (pl.col("drho2_lo") > 0))).mean().alias("slow_call")).sort("world", "amp")
print(s.write_csv())
(SY.OUT / "synthetic_a2_power.json").write_text(json.dumps(s.to_dicts(), indent=1))
