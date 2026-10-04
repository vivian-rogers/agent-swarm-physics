"""H97 calibration for the synthetic (no kickoff direction used): per regime, from ordinary placebo day boundaries of the
eligible transitions: within-agent-day resultant |mean z|, between-agent signal spread, full-space placebo memory beta0.
Writes data/processed/H97-quench-restoring-force/synthetic/calibration.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h97lib as L  # noqa: E402


def placebo_boundaries(stmt: pl.DataFrame, tr: dict):
    """Consecutive active days inside one unit of p-1 or p, not touching p's day 1."""
    out = []
    days = (stmt.filter(pl.col("unit_id") != "?").select("goal_no", "pt_date", "day_idx", "unit_id").unique()
            .sort("goal_no", "day_idx"))
    for (g,), dd in days.group_by(["goal_no"]):
        rows = dd.sort("day_idx").to_dicts()
        for a, b in zip(rows[:-1], rows[1:]):
            if a["unit_id"] != b["unit_id"] or b["day_idx"] != a["day_idx"] + 1:
                continue
            if g == tr["p"] and a["day_idx"] == 1:
                continue
            out.append((g, a["pt_date"], b["pt_date"]))
    return out


def main():
    tr_all = pl.read_parquet(L.DATA / "transitions.parquet").filter(pl.col("kind") == "kickoff")
    res = {}
    for reg in ("I", "II", "III"):
        resultants, spreads, betas = [], [], []
        for tr in tr_all.filter(pl.col("regime") == reg).iter_rows(named=True):
            stmt, _ = L.load_design(tr["design"])
            for g, d0, d1 in placebo_boundaries(stmt, tr):
                prev = L.seg_vectors(stmt, (pl.col("goal_no") == g) & (pl.col("pt_date") == d0))
                post = L.seg_vectors(stmt, (pl.col("goal_no") == g) & (pl.col("pt_date") == d1))
                bd = L.boundary(prev, post)
                if len(bd) < L.MIN_N_TRANSITION:
                    continue
                for a, (X, Y) in bd.items():
                    resultants.append(np.linalg.norm(X.mean(0)))
                XA, XB, Y, ag = L.split_arrays(bd, n_splits=10)
                k = np.zeros(32); k[0] = 1
                betas.append(L.memory_beta(XA, XB, Y, k, "full"))
                # between-agent signal spread: E|x_i - x_bar|^2 from split halves (noise-free)
                cA = XA - XA.mean(1, keepdims=True); cB = XB - XB.mean(1, keepdims=True)
                spreads.append(float((cA * cB).sum(-1).mean()))
        res[reg] = dict(n_boundaries=len(betas), resultant_median=float(np.median(resultants)),
                        spread_median=float(np.median(spreads)), beta0_full_median=float(np.nanmedian(betas)),
                        beta0_full_iqr=[float(np.nanpercentile(betas, 25)), float(np.nanpercentile(betas, 75))])
    out = L.DATA / "synthetic"
    out.mkdir(exist_ok=True)
    (out / "calibration.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
