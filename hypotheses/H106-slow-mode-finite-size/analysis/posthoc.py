"""H106 POST HOC (written 2026-10-04 after the real replication result): the per-period near-lag similarity rho_G
falls in the N >= 8 era of regime I. Calibrate the era contrast
    d_rho = mean rho_G (periods with N_G >= 8) - mean rho_G (N_G < 8)
against the drift (D, alpha 0) and magnet (M, alpha -1) worlds and an 'era-collapse' world E (slow mode present only
before 2025-11-17, i.e. absent once N >= 8), on the real regime-I panel, both models.
Output: data/processed/H106-slow-mode-finite-size/posthoc/posthoc.json
Usage: uv run python hypotheses/H106-slow-mode-finite-size/analysis/posthoc.py [--reps 150]
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h106lib as L  # noqa: E402
from replication import periods_table  # noqa: E402

MODELS = ["bge_small", "gte_modernbert"]


def d_rho(rows):
    p = pl.DataFrame(rows).drop_nans("rho")
    return float(p.filter(pl.col("N_G") >= 8)["rho"].mean() - p.filter(pl.col("N_G") < 8)["rho"].mean())


def one(pan, X, rng, grid):
    A, B, R, Rh = L.residuals(pan, X)
    sel = L.draw_subsets(A, B, pan.nb, rng, 50)
    U, Uh, ok = L.culture_vectors(R, Rh, sel, pan.block_goal)
    S = L.pair_similarity(U, ok)
    _, Rsb = L.split_half(Uh, ok)
    Rhat, _ = L.smooth_reliability(Rsb, pan.block_N, pan.block_ndays, ok)
    T = L.pairs(pan, S, ok, Rhat)
    return d_rho(periods_table(pan, T, 0.4, "x", "I"))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=150)
    a = ap.parse_args()
    out = L.OUT / "posthoc"; out.mkdir(parents=True, exist_ok=True)
    per = pl.read_parquet(L.OUT / "replication/periods.parquet").filter(pl.col("regime") == "I")
    res = {}
    for model in MODELS:
        real = d_rho(per.filter(pl.col("model") == model).to_dicts())
        ad, X, blocks = L.load(model, "style_resid", "I")
        P = L.projectors(model, "I", ad)
        pan = L.Panel(ad, blocks, P)
        sc = L.variance_scales(pan, X)
        grid = L.RateGrid(pan.block_a, pan.block_N)
        rng = np.random.default_rng(zlib.crc32(f"H106|posthoc|{model}".encode()))
        dist = {}
        for w, kw in (("D", dict(share=0.5, alpha=0.0)), ("M", dict(share=0.5, alpha=-1.0))):
            dist[w] = [one(pan, L.simulate(pan, sc, rng, grid, **kw), rng, grid) for _ in range(a.reps)]
        # era collapse: slow mode only on blocks with N < 8 (planted D world, mode zeroed where N >= 8)
        ev = []
        for _ in range(a.reps):
            Xd = L.simulate(pan, sc, rng, grid, share=0.5, alpha=0.0)
            X0 = L.simulate(pan, sc, rng, grid, share=0.0)
            late = pan.block_N[pan.block] >= 8
            Xe = Xd.copy(); Xe[late] = X0[late]
            ev.append(one(pan, Xe, rng, grid))
        dist["E"] = ev
        res[model] = {"real": real, **{w: {"median": float(np.median(v)), "q05": float(np.quantile(v, 0.05)),
                                           "q95": float(np.quantile(v, 0.95)),
                                           "pct_real": float(np.mean(np.array(v) < real))} for w, v in dist.items()}}
        print(model, json.dumps(res[model]), flush=True)
    (out / "posthoc.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
