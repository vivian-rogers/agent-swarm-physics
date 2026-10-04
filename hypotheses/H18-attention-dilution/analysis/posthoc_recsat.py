"""Post-hoc (2026-10-03, after round-1 results; NOT pre-registered): does k matter at fixed recency rank?

M_recsat: h = rho^(rank-1) * (1 + k0)/(k0 + k), rho and k0 free. Nested: k0 -> inf gives M_rec (rank only),
rho -> 1 gives M_sat (k only). Within-day-block CV of rec, sat, recsat per period, with day-bootstrap differences.
  uv run python hypotheses/H18-attention-dilution/analysis/posthoc_recsat.py
Writes data/processed/H18-attention-dilution/posthoc_recsat.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from h18lib import Units, cv, fit, paired_day_boot  # noqa: E402
from periods import PERIODS, gname  # noqa: E402

DATA = HERE.parents[2] / "data/processed/H18-attention-dilution"


def main():
    out = {}
    for g in PERIODS:
        gp = gname(g)
        d = DATA / gp
        U = Units(pl.read_parquet(d / "talks.parquet"), pl.read_parquet(d / "pending.parquet"), "talk_id")
        f = fit("recsat", U)
        rho = 1 / (1 + math.exp(-f["params"]["lrho"]))
        k0 = math.exp(f["params"]["logk0"])
        ll = cv(["rec", "sat", "recsat"], U, "block")
        r = dict(rho=rho, k0=k0, aic={m: fit(m, U)["aic"] for m in ("rec", "sat")} | {"recsat": f["aic"]},
                 cv={m: float(np.nanmean(v)) for m, v in ll.items()},
                 recsat_vs_rec=paired_day_boot(ll["recsat"], ll["rec"], U.day),
                 recsat_vs_sat=paired_day_boot(ll["recsat"], ll["sat"], U.day))
        out[gp] = r
        print(gp, f"rho {rho:.2f} k0 {k0:.2f} | recsat-rec x1e3 {1e3 * r['recsat_vs_rec'][0]:.2f} "
                  f"[{1e3 * r['recsat_vs_rec'][1]:.2f}, {1e3 * r['recsat_vs_rec'][2]:.2f}] | recsat-sat x1e3 "
                  f"{1e3 * r['recsat_vs_sat'][0]:.2f} [{1e3 * r['recsat_vs_sat'][1]:.2f}, {1e3 * r['recsat_vs_sat'][2]:.2f}]",
              flush=True)
        (DATA / "posthoc_recsat.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
