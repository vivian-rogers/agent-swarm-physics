"""H93 distance to the multiplicity boundary: for each period and channel, the smallest coupling gamma_c at which the
fitted Brock-Durlauf fields (M4: named, habit, log cumulative size, NEW) support >= 2 stable fixed points, scanned on a
grid with all other fitted parameters held fixed. Ratio r = betaJ-hat / gamma_c < 1 means a unique equilibrium.
Fit scope: the unit with the most choice events (fields are unit-specific). Writes results/phase.json.

  uv run python hypotheses/H93-brock-durlauf-project-choice/analysis/phase.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import h93lib as L  # noqa: E402
import run as RUN  # noqa: E402

DATA = ROOT / "data/processed/H93-brock-durlauf-project-choice"
PERIODS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
GRID = np.r_[np.arange(0, 10, 0.5), np.arange(10, 41, 2.0)]


def gamma_c(H, an, rng):
    for g in GRID:
        if g <= 0:
            continue
        if len(L.bd_fixed_points(H, an, g, n_random=4, corners=8, rng=rng, max_iter=4000)) >= 2:
            return float(g)
    return None


def main():
    out = {}
    rng = np.random.default_rng(93)
    for g in PERIODS:
        for ch in ("work", "attention"):
            lt, ev, occ = RUN.load(g, ch)
            if lt is None:
                continue
            cnt = lt.group_by("unit").agg(pl.col("eid").n_unique().alias("k")).sort("k", descending=True)
            u = cnt["unit"][0]
            sub = lt.filter(pl.col("unit") == u)
            f = L.fit(sub, "M4")
            if not f["ok"] or (f.get("gamma_se") or 99) > 20:
                out[f"G{g}_{ch}"] = {"unit": u, "identified": False}
                continue
            H, an, opts, agents = L.bd_fields(sub, f, u)
            gc = gamma_c(H, an, rng)
            out[f"G{g}_{ch}"] = {"unit": u, "identified": True, "gamma": f["gamma"], "gamma_lo": f["gamma_lo"],
                                 "gamma_hi": f["gamma_hi"], "gamma_c": gc, "K": len(opts), "N": len(agents),
                                 "ratio": (f["gamma"] / gc) if gc else None,
                                 "ratio_hi": (f["gamma_hi"] / gc) if gc else None,
                                 "b_own": L.coef(f, "prev")[0], "b_named": L.coef(f, "named")[0], "b_cum": L.coef(f, "logcum")[0]}
            print(g, ch, u, out[f"G{g}_{ch}"].get("gamma"), gc, flush=True)
    (DATA / "results" / "phase.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
