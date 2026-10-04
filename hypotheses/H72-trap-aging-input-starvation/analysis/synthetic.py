"""H72 synthetic validation (axis F): parametric bootstrap on the real gate design.

Real gate rows of G51, G38 and G18 keep their covariates (clocks, current reads, nuisance, agents, days). Outcomes are
drawn from planted worlds and the H72 estimator is run unchanged:
  aging      beta_a -0.5, beta_s 0
  starve     beta_a 0,    beta_s -0.5
  both       beta_a -0.3, beta_s -0.3
  null       beta_a 0,    beta_s 0
All worlds: agent effects N(0, 0.5), day effects N(0, 0.3), a directed-read kick +0.7, base set to a 30% escape rate.
Wald CIs (agent-FE information) are used for the many replicates; a day-block bootstrap coverage check runs on a few
G51 replicates. Planted outcomes only: no real outcome is read here.
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/analysis/synthetic.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h72lib as L  # noqa: E402

WORLDS = {"aging": (-0.5, 0.0), "starve": (0.0, -0.5), "both": (-0.3, -0.3), "null": (0.0, 0.0)}
PERIODS = {51: 20, 38: 40, 18: 40}
KICK = 0.7


def plant(P, ba, bs, rng):
    n_ag = P["agent"].max() + 1
    alpha = rng.normal(0, 0.5, n_ag)[P["agent"]]
    dd = rng.normal(0, 0.3, P["day"].max() + 1)[P["day"]]
    lin = alpha + dd + ba * P["la"] + bs * P["ls"] + KICK * P["nuis"].get("cur_dir", 0.0)
    # base: 30% mean escape
    lo, hi = -10.0, 10.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if np.mean(1 / (1 + np.exp(-(mid + lin)))) > 0.3:
            hi = mid
        else:
            lo = mid
    p = 1 / (1 + np.exp(-(mid + lin)))
    return (rng.random(len(p)) < p).astype(float)


def wald_ci(b, se):
    return [b - 1.96 * se, b + 1.96 * se]


def run():
    g = pl.read_parquet(L.OUT / "gates.parquet")
    res = {}
    t0 = time.time()
    for per, reps in PERIODS.items():
        P0 = L.prep(g.filter(pl.col("goal_no") == per), "sus", "novel")
        res[per] = {"n": P0["n"], "corr_la_ls": float(np.corrcoef(P0["la"], P0["ls"])[0, 1])}
        for w, (ba, bs) in WORLDS.items():
            rng = np.random.default_rng(hash((per, w)) % 2**32)
            rows = []
            for r in range(reps):
                P = dict(P0)
                P["y"] = plant(P0, ba, bs, rng)
                pt = L.point(P)
                rr = {"beta_a0": pt["beta_a0"], "beta_a": pt["beta_a"], "beta_s": pt["beta_s"], "rho": pt["rho"],
                      "ci_a0": wald_ci(pt["beta_a0"], pt["se_a0"]), "ci_a": wald_ci(pt["beta_a"], pt["se_a"]),
                      "ci_s": wald_ci(pt["beta_s"], pt["se_s"])}
                n_esc = int(P["y"].sum())
                rr["verdict"] = L.verdict(rr, n_esc, P["n"] - n_esc)
                rr["cover_a"] = rr["ci_a"][0] <= ba <= rr["ci_a"][1]
                rr["cover_s"] = rr["ci_s"][0] <= bs <= rr["ci_s"][1]
                rows.append(rr)
            A = np.array([[x["beta_a"], x["beta_s"], x["beta_a0"]] for x in rows])
            verd = {}
            for x in rows:
                verd[x["verdict"]] = verd.get(x["verdict"], 0) + 1
            res[per][w] = {"truth": [ba, bs], "mean_beta_a": float(A[:, 0].mean()), "sd_beta_a": float(A[:, 0].std()),
                           "mean_beta_s": float(A[:, 1].mean()), "sd_beta_s": float(A[:, 1].std()),
                           "mean_beta_a0": float(A[:, 2].mean()),
                           "cover_a": float(np.mean([x["cover_a"] for x in rows])),
                           "cover_s": float(np.mean([x["cover_s"] for x in rows])),
                           "verdicts": {k: v / reps for k, v in verd.items()}, "reps": reps}
            print(per, w, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[per][w].items()}),
                  f"{time.time() - t0:.0f}s", flush=True)
    # bootstrap coverage on G51 (few replicates)
    P0 = L.prep(g.filter(pl.col("goal_no") == 51), "sus", "novel")
    boot = {}
    for w in ("starve", "aging"):
        ba, bs = WORLDS[w]
        rng = np.random.default_rng(7 if w == "starve" else 8)
        cov_a, cov_s, verd = [], [], []
        for r in range(4):
            P = dict(P0)
            P["y"] = plant(P0, ba, bs, rng)
            pt = L.point(P)
            bt = L.bootstrap(P, 100, seed=r)
            cov_a.append(bt["ci_a"][0] <= ba <= bt["ci_a"][1])
            cov_s.append(bt["ci_s"][0] <= bs <= bt["ci_s"][1])
            rr = dict(pt, **{k: bt[k] for k in ("ci_a0", "ci_a", "ci_s")})
            n_esc = int(P["y"].sum())
            verd.append(L.verdict(rr, n_esc, P["n"] - n_esc))
        boot[w] = {"cover_a": float(np.mean(cov_a)), "cover_s": float(np.mean(cov_s)), "verdicts": verd}
        print("boot", w, boot[w], flush=True)
    res["boot_G51"] = boot
    (L.OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    (L.OUT / "synthetic/synthetic_results.json").write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    run()
