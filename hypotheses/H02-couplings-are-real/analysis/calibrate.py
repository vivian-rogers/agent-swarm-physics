"""Calibrate the synthetic harness from non-holdout data: fit M1 (block fields + self-coupling, no cross couplings).

Writes data/processed/H02-couplings-are-real/calibration.json with per-agent (h0, Jself, active_frac) for each regime,
and the variance decomposition of block fields into a common (per day-block) part and an agent-specific part.
"""
from __future__ import annotations

import os
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "2"); os.environ.setdefault("OMP_NUM_THREADS", "2")
import json
from pathlib import Path

import numpy as np
import polars as pl

import h02lib as L

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H02-couplings-are-real"


def load_chunks():
    sp = pl.read_parquet(DATA / "spins.parquet")
    out = {}
    for ch in sp["chunk"].unique().sort().to_list():
        d = sp.filter(pl.col("chunk") == ch)
        agents = sorted(d["agent"].unique().to_list())
        piv = (d.with_columns(pl.when(pl.col("state") >= 3).then(1).otherwise(-1).cast(pl.Int8).alias("s"))
               .pivot(on="agent", index=["day", "minute"], values="s").sort("day", "minute"))
        S = piv.select([str(a) for a in agents]).to_numpy()
        meta = d.select("goal_no", "mode", "regime").row(0)
        out[ch] = {"S": S.astype(np.int8), "day": piv["day"].to_numpy(), "minute": piv["minute"].to_numpy(),
                   "agents": agents, "goal_no": meta[0], "mode": meta[1], "regime": meta[2]}
    return out


def fit_m1(S, day, minute):
    X, Y, pen, info = L.kinetic_design(S, day, minute, "block", "1")
    N = info["N"]
    cp = np.full((N, N), L.BIG); np.fill_diagonal(cp, L.LAM_J)
    pen[:, 1:1 + N] = cp
    B = L.fit_logistic(X, Y, pen)
    h0 = B[:, 0] / 2; Js = np.diag(B[:, 1:1 + N]) / 2; dlt = B[:, 1 + N:] / 2  # (N, nblocks)
    return h0, Js, dlt


def main():
    chunks = load_chunks()
    cal = {}
    for reg in ["I", "III"]:
        h0s, Jss, afs, sc2, se2 = [], [], [], [], []
        for ch, c in chunks.items():
            if c["regime"] != reg:
                continue
            S = c["S"].astype(np.int8)
            if S.ndim != 2 or np.isnan(S.astype(float)).any():
                continue
            h0, Js, dlt = fit_m1(S, c["day"], c["minute"])
            h0s += list(h0); Jss += list(Js); afs += list((S > 0).mean(0))
            com = dlt.mean(0)  # common part per block
            res = dlt - com[None, :]
            se2.append(res.var()); sc2.append(max(com.var() - res.var() / dlt.shape[0], 0.0))
        cal[reg] = {"h0": h0s, "Jself": Jss, "active_frac": afs,
                    "sigma_common": float(np.sqrt(np.mean(sc2))), "sigma_agent": float(np.sqrt(np.mean(se2)))}
        print(reg, "agents", len(h0s), "h0 med %.2f" % np.median(h0s), "Jself med %.2f [%.2f, %.2f]" % (
            np.median(Jss), np.percentile(Jss, 10), np.percentile(Jss, 90)), "active med %.2f" % np.median(afs),
            "sigma_common %.3f sigma_agent %.3f" % (cal[reg]["sigma_common"], cal[reg]["sigma_agent"]))
    (DATA / "calibration.json").write_text(json.dumps(cal))


if __name__ == "__main__":
    main()
