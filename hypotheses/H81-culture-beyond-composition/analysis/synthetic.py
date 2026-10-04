"""H81 synthetic validation on the real panels (regime I and III): null size and calibration (S0), power (S1 slow mode),
behavior under individual drift (S2). Runs the full pipeline (projection, leave-goal-out personal vectors, residuals,
pair statistics) on planted data. Scales (agent, goal, block covariances; agent-day noise) are taken from the real
projected vectors as sampling facts; no test statistic is computed on real data here.

Output: data/processed/H81-culture-beyond-composition/synthetic/synthetic.json (+ replicate table parquet)
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/synthetic.py [--reps 200]
"""
from __future__ import annotations

import argparse
import json
import zlib
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402


def one(pan, sc, kick, rng, **kw):
    X = L.simulate(pan, sc, rng, **kw)
    A, B, R = L.agent_block_residuals(pan, X)
    T = L.pair_table(pan, A, B, R, kick)
    return L.slow_stats(T)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=200); ap.add_argument("--model", default="bge_small")
    a = ap.parse_args()
    out = L.OUT / "synthetic"; out.mkdir(parents=True, exist_ok=True)
    rows = []; summ = {}
    for regime in ("I", "III"):
        summ[regime] = {}
        ad, X, blocks = L.load(a.model, "style_resid", regime)
        P = L.projectors(a.model, regime, ad)
        pan = L.Panel(ad, blocks, P)
        sc = L.variance_scales(pan, X)
        kick = L.goal_kickoff(a.model, regime, np.unique(pan.goal))
        summ[regime] = {"trace_Sa": float(np.trace(sc["Sa"])), "trace_Sg": float(np.trace(sc["Sg"])),
                        "trace_Sb": float(np.trace(sc["Sb"])), "trace_E": float((sc["E"] ** 2).sum(1).mean())}
        scen = [("S0", dict(), a.reps)] + [(f"S1_{s}", dict(share=s), a.reps // 2) for s in (0.1, 0.25, 0.5)] + \
               [("S2_0.25", dict(drift=0.25), a.reps // 2), ("S2_0.5", dict(drift=0.5), a.reps // 2)]
        for name, kw, n in scen:
            t0 = time.time()
            rng = np.random.default_rng(zlib.crc32(f"{a.model}|{regime}|{name}".encode()))
            for r in range(n):
                st = one(pan, sc, kick, rng, **kw)
                rows.append({"regime": regime, "scenario": name, "rep": r, **st})
            print(regime, name, n, f"{time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(out / f"replicates_{a.model}.parquet")
    res = {"model": a.model, "scales": summ, "scenarios": {}}
    for regime in ("I", "III"):
        s0 = df.filter((pl.col("regime") == regime) & (pl.col("scenario") == "S0"))
        thr = {k: float(np.nanquantile(s0[k].to_numpy(), 0.95)) for k in ("D_adjg", "D_adjg_perp", "D_adj", "D_adj_perp", "D_near", "D_near_perp")}
        res["scenarios"][regime] = {"S0_q95": thr,
                                    "S0_mean": {k: float(np.nanmean(s0[k].to_numpy())) for k in thr},
                                    "S0_far90_mean": float(np.nanmean(s0["far90"].to_numpy())),
                                    "S0_far90_perp_mean": float(np.nanmean(s0["far90_perp"].to_numpy())),
                                    "S0_far90_q95": float(np.nanquantile(s0["far90"].to_numpy(), 0.95))}
        for sc_name in df["scenario"].unique().to_list():
            d = df.filter((pl.col("regime") == regime) & (pl.col("scenario") == sc_name))
            res["scenarios"][regime][sc_name] = {
                "n": d.height,
                **{f"mean_{k}": float(np.nanmean(d[k].to_numpy())) for k in thr},
                **{f"pass_{k}": float(np.nanmean(d[k].to_numpy() > thr[k])) for k in thr}}
    (out / f"synthetic_{a.model}.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res["scenarios"], indent=1))


if __name__ == "__main__":
    main()
