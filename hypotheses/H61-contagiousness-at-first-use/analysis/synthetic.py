"""H61 synthetic validation (axis F), run before any real-data outcome is modelled.

Real feature matrices (no outcomes) of six periods; outcomes simulated from a fitness model with known parameters.
  S1 size:  logit P(Y) = a0 + class + poster + day drift (kickoff bump + downward trend + random walk), theta = 0
  S2 power: S1 + theta on focus (-0.3 / SD), receptive (+0.3 / SD), specificity (-0.2 / SD)
  S3 convergence: read-5 and unread-5 indicators from the same latent fitness (no transmission difference)
  uv run python hypotheses/H61-contagiousness-at-first-use/analysis/synthetic.py
Output: data/processed/H61-contagiousness-at-first-use/synthetic/{s1s2.parquet,s3.parquet,summary.json}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ["_v"] = "1"
    os.environ[_v] = "1"

import json  # noqa: E402
import sys  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h61lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H61-contagiousness-at-first-use"
PERIODS = [13, 20, 27, 38, 41, 51]
CLS_EFF = {0: 0.6, 1: 0.4, 2: -0.3, 3: 0.2}
THETA = {"lg_novel": -0.3, "f_rec": 0.3, "spec": -0.2}
BASE = 0.18


def features(g: int) -> pl.DataFrame:
    df = pl.read_parquet(OUT / f"G{g:02d}/ideas.parquet")
    if g == 51:
        df = df.filter(pl.col("day") < 10)
    # drop every outcome column so nothing real can leak into the synthetic runs
    df = df.drop("reach24", "n_exposed", "n_unexposed", "n_read5", "n_unread5", "n_read_old")
    return L.prep(df.with_columns(pl.lit(1).alias("reach24"), pl.lit(0).alias("n_read5"), pl.lit(0).alias("n_unread5")))


def simulate(df: pl.DataFrame, rng, theta: dict | None, drift: bool = True) -> np.ndarray:
    n = df.height
    z = np.array([CLS_EFF[int(c)] for c in df["cls"].to_numpy()])
    post = df["poster"].to_numpy()
    pe = {a: rng.normal(0, 0.4) for a in np.unique(post)}
    z += np.array([pe[a] for a in post])
    if drift:
        day = df["day"].to_numpy()
        nd = int(day.max()) + 1
        rw = np.cumsum(rng.normal(0, 0.15, nd)) - 0.08 * np.arange(nd)
        rw[0] += 0.4
        z += rw[day]
    if theta:
        for f, b in theta.items():
            x = df[f].to_numpy().astype(float)
            z += b * (x - x.mean()) / (x.std() or 1)
    lo, hi = -10.0, 5.0
    for _ in range(50):                    # base rate matched to BASE
        mid = (lo + hi) / 2
        if (1 / (1 + np.exp(-(mid + z)))).mean() > BASE:
            hi = mid
        else:
            lo = mid
    return z + mid


def run_s12(args):
    g, rep, kind = args
    df = features(g)
    rng = np.random.default_rng(1000 * g + rep + (0 if kind == "null" else 500000))
    z = simulate(df, rng, THETA if kind == "power" else None)
    y = (rng.random(df.height) < 1 / (1 + np.exp(-z))).astype(np.int8)
    df = df.with_columns(pl.Series("y", y), pl.Series("reach24", 1 + y))
    pred = L.forward_chain(df, "y", models=("B0", "B1", "B2", "B3", "B4", "F", "Fm"))
    s = L.score_period(pred, "y", B=300, seed=rep)
    return dict(goal=g, rep=rep, kind=kind, n_test=s["n_test"], n_pos=s["n_pos"],
                dll_F_B3=s["dll_F_B3"], lo_B3=s["dll_F_B3_lo"], dll_F_B4=s["dll_F_B4"], lo_B4=s["dll_F_B4_lo"],
                dll_F_B1=s["dll_F_B1"], lo_B1=s["dll_F_B1_lo"], auc_F=s["auc_F"], auc_B1=s["auc_B1"],
                auc_B3=s["auc_B3"], lift_y=s["lift_y"])


def run_s3(args):
    g, rep = args
    df = features(g)
    rng = np.random.default_rng(77 * g + rep)
    zf = simulate(df, rng, THETA)            # a real fitness signal, shared by both outcomes
    zr = zf + np.log(0.12 / BASE)
    zu = zf + np.log(0.03 / BASE)
    yr = (rng.random(df.height) < 1 / (1 + np.exp(-zr))).astype(np.int8)
    yu = (rng.random(df.height) < 1 / (1 + np.exp(-zu))).astype(np.int8)
    df = df.with_columns(pl.Series("y_read5", yr), pl.Series("y_unread5", yu))
    r = L.gains_conv(df, B=100, seed=rep)
    return dict(goal=g, rep=rep, **{k: v for k, v in r.items()})


def main():
    (OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    jobs = [(g, r, k) for g in PERIODS for k, nrep in (("null", 30), ("power", 15)) for r in range(nrep)]
    with Pool(4) as pool:
        res = pool.map(run_s12, jobs, chunksize=1)
    s12 = pl.DataFrame(res)
    s12.write_parquet(OUT / "synthetic/s1s2.parquet")
    jobs3 = [(g, r) for g in (20, 38, 51) for r in range(12)]
    with Pool(4) as pool:
        res3 = pool.map(run_s3, jobs3, chunksize=1)
    s3 = pl.DataFrame(res3)
    s3.write_parquet(OUT / "synthetic/s3.parquet")
    summ = {}
    for k in ("null", "power"):
        d = s12.filter(pl.col("kind") == k)
        summ[k] = {f"G{g:02d}": dict(
            rej_F_B3=float((d.filter(pl.col("goal") == g)["lo_B3"] > 0).mean()),
            rej_F_B4=float((d.filter(pl.col("goal") == g)["lo_B4"] > 0).mean()),
            rej_F_B1=float((d.filter(pl.col("goal") == g)["lo_B1"] > 0).mean()),
            med_dll_F_B3=float(d.filter(pl.col("goal") == g)["dll_F_B3"].median()),
            med_dll_F_B4=float(d.filter(pl.col("goal") == g)["dll_F_B4"].median()),
            med_auc_gain=float((d.filter(pl.col("goal") == g)["auc_F"] - d.filter(pl.col("goal") == g)["auc_B1"]).median()),
            med_lift=float(d.filter(pl.col("goal") == g)["lift_y"].median()))
            for g in PERIODS}
        summ[k]["all"] = dict(rej_F_B3=float((d["lo_B3"] > 0).mean()), rej_F_B4=float((d["lo_B4"] > 0).mean()))
    e = s3.filter(pl.col("eligible"))
    summ["s3"] = dict(n=e.height, mean_diff=float(e["diff"].mean()), sd_diff=float(e["diff"].std()),
                      frac_ci_pos=float((e["diff_lo"] > 0).mean()), frac_ci_neg=float((e["diff_hi"] < 0).mean()),
                      frac_pos=float((e["diff"] > 0).mean()))
    (OUT / "synthetic/summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
