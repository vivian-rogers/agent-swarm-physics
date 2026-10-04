"""H90 synthetic size check (A2): Delta_addr false-positive rate under the lagged field and independence, S51 and S38
talk, 40 replicates each (the main synthetic had 12-20).
  uv run python hypotheses/H90-collective-entropy-production/analysis/synthetic_size.py
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h90lib as L  # noqa: E402
import synthetic as S  # noqa: E402

rng = np.random.default_rng(90901)
rows = []
for size in ("S51", "S38"):
    for scen in ("F", "0"):
        for r in range(40):
            rows.append(S.one(size, scen, "talk", rng, R_shift=30, R_flip=2) | {"rep": r})
df = pl.DataFrame(rows)
df.write_parquet(L.OUTD / "synthetic" / "size_check.parquet")
print(df.group_by(["size", "scen"], maintain_order=True).agg(
    pl.len(), (pl.col("addr_p_shift") < 0.05).mean().alias("P_addr"), (pl.col("coll_all_p_shift") < 0.05).mean().alias("P_coll"),
    (pl.col("coll_named_p_shift") < 0.05).mean().alias("P_named")).write_csv(float_precision=3))
