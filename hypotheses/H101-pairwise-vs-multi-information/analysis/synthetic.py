"""H101 synthetic validation (axis F): is I2/IN, and the field-removed rho_F, identifiable at village counts?

Worlds are generated per unit-day at the real day count, real active-agent count N_d, real item count T_d and real
per-agent use rates (descriptive moments only; no co-usage statistic of the real data enters). Items are drawn by
vectorized Gibbs sampling of
    E(s) = sum_i h_i s_i + phi_m K + sum_{i<j} J_ij s_i s_j + beta * sum_G 1[K_G >= 3]
with a Gaussian latent item field phi_m ~ N(0, sig^2) (a shared popularity field; its marginal is exactly a V(K)
term), then truncated to K >= 1 at the day level (as the real ensemble). Worlds:
  Y1 pairwise : sig = 1, J_ij ~ N(0.3, 0.5^2), beta = 0
  Y2 field    : sig = 1, J = 0, beta = 0
  Y3 group    : as Y1 plus two 4-agent groups with a group term beta (sized so the large-T subset r_HO ~ 0.2)
  Y0 indep    : sig = 0, J = 0, beta = 0
The estimator is the real pipeline (run.py: unit_stats): per day, S random subsets of n = min(6, N_d) agents, the
hierarchy on the K >= 1 support, ratio of sums over days and subsets.

Usage: uv run python hypotheses/H101-pairwise-vs-multi-information/analysis/synthetic.py [--reps 12]
"""
from __future__ import annotations

import argparse
import zlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h101lib as L  # noqa: E402
import run as R  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H101-pairwise-vs-multi-information/synthetic"
UNITS = ["4c", "27", "40", "51g"]


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def gibbs(T, h, J, sig, groups, beta, rng, sweeps=25):
    N = len(h)
    phi = rng.normal(0, sig, T) if sig > 0 else np.zeros(T)
    S = (rng.random((T, N)) < sigmoid(h)[None, :]).astype(np.float64)
    gidx = [[g for g in range(len(groups)) if i in groups[g]] for i in range(N)]
    for _ in range(sweeps):
        for i in range(N):
            f = h[i] + phi + S @ J[:, i]
            for g in gidx[i]:
                others = [j for j in groups[g] if j != i]
                kg = S[:, others].sum(1)
                f = f + beta * ((kg + 1 >= 3).astype(float) - (kg >= 3).astype(float))
            S[:, i] = rng.random(T) < sigmoid(f)
    return S.astype(np.int8)


def world_day(N, T, rates, kind, rng, beta=2.0):
    J = np.zeros((N, N))
    groups, b, sig = [], 0.0, 1.0
    if kind in ("Y1", "Y3"):
        A = rng.normal(0.3, 0.5, (N, N))
        J = np.triu(A, 1)
        J = J + J.T
    if kind == "Y3":
        perm = rng.permutation(N)
        groups = [list(perm[:4])] + ([list(perm[4:8])] if N >= 8 else [])
        b = beta
    if kind == "Y0":
        sig = 0.0
    # match rates after truncation: three fixed-point steps on h
    h = np.log(np.clip(rates, 1e-3, 0.9) / (1 - np.clip(rates, 1e-3, 0.9))) - 0.5
    for _ in range(3):
        S = gibbs(min(3 * T, 6000), h, J, sig, groups, b, rng, sweeps=12)
        S = S[S.sum(1) > 0]
        r = np.clip(S.mean(0), 1e-3, 0.99)
        h = h + (np.log(rates / (1 - rates)) - np.log(r / (1 - r)))
    S = gibbs(int(T * 2.5) + 50, h, J, sig, groups, b, rng)
    S = S[S.sum(1) > 0][:T]
    return S


def real_shape(unit):
    z = np.load(ROOT / f"data/processed/H101-pairwise-vs-multi-information/days/{unit}.npz")
    out = []
    for k in range(len(z["days"])):
        X = z[f"conv_{k}"]
        out.append((X.shape[1], X.shape[0], np.clip(X.mean(0), 0.005, 0.8)))
    return out


def job(args):
    unit, kind, rep, beta = args
    rng = np.random.default_rng(zlib.crc32(f"{unit}|{kind}|{rep}".encode()))
    days = real_shape(unit)
    mats = [world_day(N, T, rates, kind, rng, beta) for (N, T, rates) in days]
    st = R.unit_stats(mats, rng, n_sub=R.N_SUB, S=R.S_SUB)
    st.update({"unit": unit, "world": kind, "rep": rep})
    return st


def large_T_truth(beta, rng, N=10, n=6):
    """Large-T subset r_HO and rho_F in the Y3 world at real-like rates (sizing beta)."""
    rates = np.full(N, 0.15)
    S = world_day(N, 40000, rates, "Y3", rng, beta)
    rows = []
    for s in range(6):
        sub = rng.choice(N, n, replace=False)
        rows.append(L.hierarchy(S[:, sub]))
    return L.agg(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=12)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--beta", type=float, default=None)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    sizing = {}
    if a.beta is None:
        for beta in (1.5, 2.5, 3.5):
            t = large_T_truth(beta, rng)
            sizing[beta] = {k: t[k] for k in ("rho_F", "r_HO", "rho_raw", "phi", "I_N")}
            print("sizing beta", beta, {k: round(v, 3) for k, v in sizing[beta].items()}, flush=True)
        beta = min(sizing, key=lambda b: abs(sizing[b]["r_HO"] - 0.2))
    else:
        beta = a.beta
    jobs = [(u, w, r, beta) for u in UNITS for w in ("Y0", "Y1", "Y2", "Y3") for r in range(a.reps)]
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(job, jobs))
    df = pl.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (list, dict))} for r in res])
    df.write_parquet(OUT / "synthetic.parquet")
    summ = (df.group_by("unit", "world").agg(
        pl.len().alias("reps"), pl.col("rho_F").median().alias("rho_F_med"), pl.col("rho_F").quantile(0.1).alias("rho_F_q10"),
        pl.col("r_HO").median().alias("r_HO_med"), pl.col("rho_raw").median().alias("rho_raw_med"),
        pl.col("phi").median().alias("phi_med"), pl.col("I_N").median().alias("I_N_med"),
        (pl.col("ho_excess_p") < 0.05).mean().alias("ho_detect"), (pl.col("I_N_p") < 0.05).mean().alias("IN_detect"))
        .sort("unit", "world"))
    print(summ)
    (OUT / "synthetic_summary.json").write_text(json.dumps({"beta": beta, "sizing": {str(k): v for k, v in sizing.items()},
                                                            "summary": summ.to_dicts()}, indent=1))


if __name__ == "__main__":
    main()
