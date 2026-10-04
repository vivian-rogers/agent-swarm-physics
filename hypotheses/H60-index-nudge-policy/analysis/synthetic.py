"""H60 synthetic validation (axis F) on the real G51 gate design (nudger-on days; real states and nudge assignment).

Planted outcome: active calls in 30 min, Poisson with mean mu0(x) + M * g(x), where
  mu0 = 8 * exp(agent N(0, 0.4) + day N(0, 0.2) - 0.15 (ln a - c_a) + 0.1 cur_other)
  S1 heterogeneous: g = max(0, 2 - 1.5 (ln k - c_k) + 0.8 (ln r - c_r))
  S2 flat (R0):     g = 2
  S3 selection:     g = 2, but mu0 is lowered at nudged gates by 1.5 (ln k - c_k) (the nudger picks agents whose
                    unobserved stuckness grows with k): a spurious nudge x ln k slope.
The H60 estimator (cross-fitted direct method, day-block bootstrap) runs unchanged. True policy values use the
planted g on the gates each policy selects. Planted outcomes only: no real outcome is read.
Usage: uv run python hypotheses/H60-index-nudge-policy/analysis/synthetic.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h60lib as L  # noqa: E402

REPS = {"S1": 10, "S2": 16, "S3": 10}
BOOT = 60


def planted(P, scen, rng):
    c_a, c_k, c_r = L.centers_of(P, np.arange(P["n"]))
    alpha = rng.normal(0, 0.4, P["agent"].max() + 1)[P["agent"]]
    dd = rng.normal(0, 0.2, P["day"].max() + 1)[P["day"]]
    mu0 = 8 * np.exp(alpha + dd - 0.15 * (P["la"] - c_a) + 0.1 * P["nuis"].get("cur_other", 0))
    if scen == "S1":
        g = np.maximum(0, 2 - 1.5 * (P["lk"] - c_k) + 0.8 * (P["lr"] - c_r))
    else:
        g = np.full(P["n"], 2.0)
    if scen == "S3":
        mu0 = np.maximum(mu0 - P["M"] * 1.5 * (P["lk"] - c_k), 0.2)
    y = rng.poisson(np.maximum(mu0 + P["M"] * g, 0.05)).astype(float)
    return y, g


def true_values(P, g, cf):
    r1, r2 = cf["_r"]
    sel_idx = np.concatenate([r1.get("sel_index_rows", []), r2.get("sel_index_rows", [])]).astype(int)
    sel_once = np.concatenate([r1.get("sel_once_rows", []), r2.get("sel_once_rows", [])]).astype(int)
    M = P["M"] > 0
    return {"logged": float(g[M].mean()), "random": float(g.mean()), "once_early": float(g[P["k"] == 2].mean()),
            "index": float(g[sel_idx].mean()), "index_once": float(g[sel_once].mean()) if len(sel_once) else np.nan}


def run():
    gt = pl.read_parquet(L.OUT / "gates.parquet").filter((pl.col("goal_no") == 51) & pl.col("nudger_on"))
    P0 = L.prep(gt, "calls30")
    out = {"n_gates": P0["n"], "n_nudged": int(P0["M"].sum())}
    t0 = time.time()
    for scen, reps in REPS.items():
        rng = np.random.default_rng({"S1": 1, "S2": 2, "S3": 3}[scen])
        rows = []
        for r in range(reps):
            P = dict(P0)
            P["y"], g = planted(P0, scen, rng)
            cf = L.crossfit(P)
            tv = true_values(P, g, cf)
            D = L.boot_crossfit(P, BOOT, seed=r)
            ci = L.ratio_ci(D, "index", "logged")
            rows.append({"est": {p: cf[p] for p in L.POL}, "true": tv,
                         "est_ratio": cf["index"] / cf["logged"], "true_ratio": tv["index"] / tv["logged"],
                         "est_once_ratio": cf["once_early"] / cf["logged"],
                         "true_once_ratio": tv["once_early"] / tv["logged"],
                         "ci_index_logged": ci, "reject_1": bool(ci[0] > 1)})
            print(scen, r, round(rows[-1]["est_ratio"], 2), round(rows[-1]["true_ratio"], 2), [round(x, 2) for x in ci],
                  f"{time.time() - t0:.0f}s", flush=True)
        er = np.array([x["est_ratio"] for x in rows]); tr = np.array([x["true_ratio"] for x in rows])
        out[scen] = {"reps": reps, "est_ratio_mean": float(er.mean()), "est_ratio_sd": float(er.std()),
                     "true_ratio_mean": float(tr.mean()),
                     "est_once_ratio_mean": float(np.mean([x["est_once_ratio"] for x in rows])),
                     "true_once_ratio_mean": float(np.mean([x["true_once_ratio"] for x in rows])),
                     "rate_ci_above_1": float(np.mean([x["reject_1"] for x in rows])),
                     "cover_true_ratio": float(np.mean([x["ci_index_logged"][0] <= x["true_ratio"] <= x["ci_index_logged"][1]
                                                        for x in rows])),
                     "rows": rows}
        print(scen, {k: v for k, v in out[scen].items() if k != "rows"}, flush=True)
    (L.OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    (L.OUT / "synthetic/synthetic_results.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    run()
