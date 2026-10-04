"""H90 synthetic power at the effect size G51 shows (amendment A3, post hoc; labelled): talk coupling J in {0.25, 0.35}
at the three village sizes, 20 replicates each, Delta_addr and sigma_nam against 30 block shifts.
  uv run python hypotheses/H90-collective-entropy-production/analysis/synthetic_effect.py
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h90lib as L  # noqa: E402
import synthetic as S  # noqa: E402

rng = np.random.default_rng(90902)
rows = []
for J in (0.25, 0.35):
    S.SCEN[f"C{J}"] = (J, 0.0)
    for size in ("S40", "S38", "S51"):
        for r in range(20):
            rows.append(S.one(size, f"C{J}", "talk", rng, R_shift=30, R_flip=2) | {"rep": r, "J": J})
        print(J, size, flush=True)
df = pl.DataFrame(rows)
df.write_parquet(L.OUTD / "synthetic" / "effect_power.parquet")
print(df.group_by(["J", "size"], maintain_order=True).agg(
    pl.len(), (pl.col("addr_p_shift") < 0.05).mean().alias("P_addr"), (pl.col("coll_named_p_shift") < 0.05).mean().alias("P_named"),
    pl.col("coll_named").mean().alias("named_mean"), pl.col("addr").mean().alias("addr_mean")).write_csv(float_precision=4))
