"""H51 synthetic validation (axis F), run before any real axis-observable statistic.

Observables are simulated at the REAL periods' axis values (common sample) with the REAL missingness pattern of each
observable; nothing from the real observables enters. Worlds:
  W0       regime offsets only (null for the dial)
  W1_rho   regime offsets + b * K_true; within-regime partial R^2 of K_true = rho2 in {0.15, 0.3, 0.5}; the analysis
           sees K_obs = K_true + N(0, g_lag_se) (H67 period SE)
  W2       regime offsets + c * logN, within-regime partial R^2 0.3 (N-only world; size of the dial rule against N)
  W3       single index: Y_j = b_j * (Z w_true) + noise, R^2 0.4, one w_true shared by all observables
Metrics: per-observable collapse-rule firing (D1 = K, D2 = index); within-regime permutation rejection (p < 0.05);
hypothesis-level "D1 collapses >= 3/4 and p < 0.05"; |cos(w_hat, w_true)| in W3.
Usage: uv run python hypotheses/H51-one-dial-collapse/analysis/synthetic.py [--reps 60]
"""
from __future__ import annotations

import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h51lib as L  # noqa: E402


def base_frame():
    d = L.common_sample(L.load())
    return d


def simulate(d: pl.DataFrame, world: str, rng: np.random.Generator) -> tuple[pl.DataFrame, np.ndarray | None]:
    reg = d["regime"].to_numpy()
    K = d["K"].to_numpy().astype(float)
    se = d["g_lag_se"].to_numpy().astype(float)
    logN = d["logN"].to_numpy().astype(float)
    Z = np.column_stack([L.zs(d[a].to_numpy()) for a in L.AXES])
    w_true = None
    if world == "W3":
        w_true = rng.normal(size=4)
        w_true /= np.linalg.norm(w_true)
    cols = {}
    for j in L.OBS:
        mask = d[j].is_not_null().to_numpy()  # real missingness pattern only
        off = {r: rng.normal(0, 0.8) for r in np.unique(reg)}
        a = np.array([off[r] for r in reg])
        e = rng.normal(size=len(reg))
        if world == "W0":
            y = a + e
        elif world.startswith("W1"):
            rho2 = float(world.split("_")[1])
            xw = K - np.array([K[reg == r].mean() for r in reg])
            b = np.sqrt(rho2 / (1 - rho2) / xw.var())
            y = a + b * K + e
        elif world == "W2":
            xw = logN - np.array([logN[reg == r].mean() for r in reg])
            c = np.sqrt(0.3 / 0.7 / xw.var())
            y = a + c * logN + e
        elif world == "W3":
            u = Z @ w_true
            b = np.sqrt(0.4 / 0.6 / u.var())
            y = b * u + e
        y = np.where(mask, y, np.nan)
        cols[j] = pl.Series(j, y).fill_nan(None)
    s = d.with_columns(**cols)
    s = s.with_columns(K=pl.Series(K + rng.normal(size=len(K)) * np.nan_to_num(se, nan=np.nanmedian(se))))
    return s, w_true


def one(args):
    world, rep, n_perm = args
    rng = np.random.default_rng(1000 * ["W0", "W1_0.15", "W1_0.3", "W1_0.5", "W2", "W3"].index(world) + rep)
    d = base_frame()
    s, w_true = simulate(d, world, rng)
    cs = L.collapse_scores(s, seed=rep)
    ps = L.perm_stat(s, "K", n_perm=n_perm, seed=rep)
    out = {"world": world, "rep": rep, "p_perm": ps["p"],
           "n_collapse_K": sum(cs[j]["collapse_K"] for j in L.OBS),
           "n_collapse_index": sum(cs[j]["collapse_index"] for j in L.OBS)}
    for j in L.OBS:
        out[f"cvK_{j}"] = cs[j]["cv_r2"]["K"]
        out[f"cvreg_{j}"] = cs[j]["cv_r2"]["regime"]
        out[f"cvidx_{j}"] = cs[j]["cv_r2"]["index"]
        if w_true is not None:
            w = np.array([cs[j]["w"][a] for a in L.AXES])
            out[f"cos_{j}"] = float(abs(w @ w_true))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=60)
    ap.add_argument("--perm", type=int, default=199)
    a = ap.parse_args()
    worlds = ["W0", "W1_0.15", "W1_0.3", "W1_0.5", "W2", "W3"]
    jobs = [(w, r, a.perm) for w in worlds for r in range(a.reps)]
    t0 = time.time()
    with Pool(2) as pool:
        res = pool.map(one, jobs, chunksize=4)
    df = pl.DataFrame(res, infer_schema_length=None)
    out = L.DATA / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out / "runs.parquet")
    summ = {}
    for w in worlds:
        x = df.filter(pl.col("world") == w)
        s = {"reps": x.height,
             "perm_reject_0.05": float((x["p_perm"] < 0.05).mean()),
             "collapse_K_rate_per_obs": float(x["n_collapse_K"].mean() / 4),
             "collapse_index_rate_per_obs": float(x["n_collapse_index"].mean() / 4),
             "hyp_K_3of4_and_p": float(((x["n_collapse_K"] >= 3) & (x["p_perm"] < 0.05)).mean()),
             "hyp_index_3of4": float((x["n_collapse_index"] >= 3).mean()),
             "median_cvK": {j: float(x[f"cvK_{j}"].median()) for j in L.OBS},
             "median_cvreg": {j: float(x[f"cvreg_{j}"].median()) for j in L.OBS}}
        if w == "W3":
            cos = np.concatenate([x[f"cos_{j}"].to_numpy() for j in L.OBS])
            s["cos_ge_0.8"] = float((cos >= 0.8).mean())
            s["cos_median"] = float(np.median(cos))
        summ[w] = s
    summ["_meta"] = {"n_periods_common": int(L.common_sample(L.load()).height), "perm": a.perm, "secs": time.time() - t0,
                     "n_per_obs": {j: int(L.common_sample(L.load())[j].is_not_null().sum()) for j in L.OBS}}
    L.jdump(summ, out / "summary.json")
    for w, s in summ.items():
        print(w, s)


if __name__ == "__main__":
    main()
