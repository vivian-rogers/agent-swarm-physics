"""H02-MF: mean-field forward models (card, "Sub-hypothesis H02-MF").

MF-a  Curie-Weiss inversion (HH80): within (day, 30-min block), VR = sum_b n_b Var_b(M) / sum_b n_b sum_i Var_b(s_i);
      q = mean within-block single-spin variance; beta*J0 = (1 - 1/VR) / q. Null: N1 block-shift surrogates.
      Forward test: pooled P(K) vs per-block Poisson-binomial (independent) and its CW tilt exp(bJ0 M^2/2N + delta M),
      delta matching each block's mean K. Unfitted: tail masses and kurtosis.
MF-b  Leader-follower mean field (HH83): for each candidate leader k, followers' logit = eta_f (own M1 predictor:
      block fields + self) + 2 J_ff m_{F\\f}(t) + 2 J_lf s_k(t); reverse J_fl from s_k(t+1) on m_F(t).
      z vs N1 surrogates.
Outputs: data/processed/H02-couplings-are-real/mf_cw.parquet, mf_pk.parquet, mf_lf.parquet
Usage: uv run python mf.py [n_surr_cw] [n_surr_lf]     |     uv run python mf.py nolull   (lull-excluded CW check)
"""
from __future__ import annotations

import os
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import brentq

import h02lib as L
from calibrate import load_chunks

ROOT = Path(__file__).resolve().parents[3]
DATA = __import__("r1b_common").data_dir()   # round 1 or round 1b (+ mask): analysis/r1b_common.py


# ------------------------------------------------------------------ MF-a Curie-Weiss
def cw_stats(S, day, minute):
    bid = L.block_ids(day, minute)
    obs = exp_ = qs = n_tot = 0.0
    for b in np.unique(bid):
        X = S[bid == b].astype(float)
        n = X.shape[0]
        if n < 5:
            continue
        v = X.var(0)
        obs += X.sum(1).var() * n; exp_ += v.sum() * n; qs += v.mean() * n; n_tot += n
    VR = obs / exp_
    q = qs / n_tot
    return {"VR": VR, "q": q, "bJ0": (1 - 1 / VR) / q}


def poisson_binomial(p):
    P = np.array([1.0])
    for pi in p:
        P = np.convolve(P, [1 - pi, pi])
    return P


def cw_forward(S, day, minute, bJ0):
    """Pooled predicted P(K) (independent, CW) and observed, over bins."""
    N = S.shape[1]
    Kgrid = np.arange(N + 1); Mgrid = 2 * Kgrid - N
    bid = L.block_ids(day, minute)
    obs = np.zeros(N + 1); ind = np.zeros(N + 1); cw = np.zeros(N + 1)
    for b in np.unique(bid):
        X = S[bid == b]
        n = X.shape[0]
        K = (X > 0).sum(1)
        obs += np.bincount(K, minlength=N + 1)
        p = np.clip((X > 0).mean(0), 1e-6, 1 - 1e-6)
        P0 = poisson_binomial(p)
        ind += n * P0
        target = K.mean()
        base = np.log(P0 + 1e-300) + bJ0 * Mgrid ** 2 / (2 * N)

        def tilt(d):
            w = base + d * Mgrid; w = np.exp(w - w.max()); return w / w.sum()
        try:
            d = brentq(lambda d: tilt(d) @ Kgrid - target, -20, 20)
        except ValueError:
            d = 0.0
        cw += n * tilt(d)
    tot = obs.sum()
    return obs / tot, ind / tot, cw / tot


def dist_stats(P, N):
    K = np.arange(N + 1)
    mu = P @ K; var = P @ (K - mu) ** 2
    kurt = (P @ (K - mu) ** 4) / var ** 2 if var > 0 else np.nan
    return {"var": float(var), "kurt": float(kurt), "lo": float(P[:2].sum()), "hi": float(P[-2:].sum())}


# ------------------------------------------------------------------ MF-b leader-follower
def m1_parts(S, day, minute):
    X, Y, pen, info = L.kinetic_design(S, day, minute, "block", "1")
    N = info["N"]
    cp = np.full((N, N), L.BIG); np.fill_diagonal(cp, L.LAM_J); pen[:, 1:1 + N] = cp
    B = L.fit_logistic(X, Y, pen)
    return X @ B.T, Y, X[:, 1:1 + N]


def lf_all(S, day, minute):
    """Per candidate leader k: J_ff, J_lf, J_fl (Ising units)."""
    eta, Y, Sc = m1_parts(S, day, minute)
    T, N = Y.shape
    out = np.zeros((N, 3))
    tot = Sc.sum(1)
    for k in range(N):
        F = [j for j in range(N) if j != k]
        sumF = tot - Sc[:, k]
        mFf = (sumF[:, None] - Sc[:, F]) / max(len(F) - 1, 1)  # (T, |F|) mean of the other followers
        Xs = np.column_stack([mFf.T.ravel(), np.tile(Sc[:, k], len(F))])
        Ys = Y[:, F].T.ravel()[:, None]
        off = eta[:, F].T.ravel()[:, None]
        B = L.fit_logistic(Xs, Ys, np.array([L.LAM_J, L.LAM_J]), offset=off)
        Br = L.fit_logistic((sumF / len(F))[:, None], Y[:, [k]], np.array([L.LAM_J]), offset=eta[:, [k]])
        out[k] = [B[0, 0] / 2, B[0, 1] / 2, Br[0, 0] / 2]
    return out


def job(args):
    ch, c, seed, n_cw, n_lf = args
    rng = np.random.default_rng([777001, seed])
    S, day, minute, agents = c["S"], c["day"], c["minute"], c["agents"]
    N = S.shape[1]
    segs = L.segments(day, minute, "block")
    cw = cw_stats(S, day, minute)
    nul = np.array([cw_stats(L.circular_shift(S, segs, rng), day, minute)["bJ0"] for _ in range(n_cw)])
    obs, ind, cwp = cw_forward(S, day, minute, cw["bJ0"])
    tvd = lambda a, b: 0.5 * np.abs(a - b).sum()
    so, si, sc = dist_stats(obs, N), dist_stats(ind, N), dist_stats(cwp, N)
    cwrow = {"chunk": ch, "mode": c["mode"], "regime": c["regime"], "N": N, **cw,
             "bJ0_null_mean": float(nul.mean()), "bJ0_null_sd": float(nul.std()),
             "z": float((cw["bJ0"] - nul.mean()) / nul.std()), "p": float((1 + (nul >= cw["bJ0"]).sum()) / (n_cw + 1)),
             "tvd_ind": tvd(obs, ind), "tvd_cw": tvd(obs, cwp),
             **{f"obs_{k}": v for k, v in so.items()}, **{f"ind_{k}": v for k, v in si.items()},
             **{f"cw_{k}": v for k, v in sc.items()}}
    pk = [{"chunk": ch, "K": int(k), "obs": float(obs[k]), "ind": float(ind[k]), "cw": float(cwp[k])} for k in range(N + 1)]
    lf = lf_all(S, day, minute)
    nl = np.array([lf_all(L.circular_shift(S, segs, rng), day, minute) for _ in range(n_lf)])
    A, An = lf[:, 1] - lf[:, 2], nl[:, :, 1] - nl[:, :, 2]
    zlf = (lf[:, 1] - nl[:, :, 1].mean(0)) / nl[:, :, 1].std(0)
    zA = (A - An.mean(0)) / An.std(0)
    zff = (lf[:, 0] - nl[:, :, 0].mean(0)) / nl[:, :, 0].std(0)
    lfrows = [{"chunk": ch, "mode": c["mode"], "regime": c["regime"], "agent": a, "J_ff": float(lf[i, 0]),
               "J_lf": float(lf[i, 1]), "J_fl": float(lf[i, 2]), "A": float(A[i]), "z_lf": float(zlf[i]),
               "z_A": float(zA[i]), "z_ff": float(zff[i]), "rank_lf": L.rank_of(lf[:, 1], i), "rank_A": L.rank_of(A, i)}
              for i, a in enumerate(agents)]
    return cwrow, pk, lfrows


def nolull(n_surr=50):
    """Robustness: CW beta*J0 on bins with K > 1 (no global lulls); each surrogate filtered the same way after shifting."""
    rng = np.random.default_rng(5)

    def stat(S, day, minute):
        keep = (S > 0).sum(1) > 1
        return cw_stats(S[keep], day[keep], minute[keep])["bJ0"], 1 - keep.mean()
    rows = []
    for k, c in sorted(load_chunks().items()):
        S, day, minute = c["S"], c["day"], c["minute"]
        segs = L.segments(day, minute, "block")
        b, drop = stat(S, day, minute)
        nul = np.array([stat(L.circular_shift(S, segs, rng), day, minute) for _ in range(n_surr)])
        rows.append({"chunk": k, "mode": c["mode"], "regime": c["regime"], "drop_frac": drop,
                     "drop_frac_null": float(nul[:, 1].mean()), "bJ0_nolull": b, "null_mean": float(nul[:, 0].mean()),
                     "z_nolull": float((b - nul[:, 0].mean()) / nul[:, 0].std())})
    d = pl.DataFrame(rows).join(pl.read_parquet(DATA / "mf_cw.parquet").select("chunk", "bJ0", "z"), on="chunk")
    d.write_parquet(DATA / "mf_cw_nolull.parquet")
    print(d.sort("regime", "mode", "chunk").with_columns(pl.col(pl.Float64).round(3)))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "nolull":
        return nolull()
    n_cw = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    n_lf = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    chunks = load_chunks()
    jobs = [(ch, c, k, n_cw, n_lf) for k, (ch, c) in enumerate(sorted(chunks.items()))]
    with Pool(int(os.environ.get("H02_WORKERS", 3))) as p:  # round 1b runs with 2
        res = p.map(job, jobs, chunksize=1)
    cw = pl.DataFrame([r[0] for r in res]); cw.write_parquet(DATA / "mf_cw.parquet")
    pl.DataFrame([x for r in res for x in r[1]]).write_parquet(DATA / "mf_pk.parquet")
    lf = pl.DataFrame([x for r in res for x in r[2]]); lf.write_parquet(DATA / "mf_lf.parquet")
    with pl.Config(tbl_rows=30, tbl_cols=30, tbl_width_chars=250):
        print(cw.sort("regime", "mode", "chunk").select("chunk", "mode", "regime", "N", "VR", "q", "bJ0", "z", "p", "tvd_ind", "tvd_cw",
              "obs_lo", "ind_lo", "cw_lo", "obs_hi", "ind_hi", "cw_hi", "obs_kurt", "ind_kurt", "cw_kurt").with_columns(pl.col(pl.Float64).round(3)))
        print(lf.group_by("regime", "mode").agg(pl.len(), (pl.col("z_lf") > 2).mean().round(3).alias("frac_zlf>2"),
              (pl.col("z_A") > 2).mean().round(3).alias("frac_zA>2"), pl.col("J_ff").median().round(3),
              pl.col("z_ff").median().round(2)).sort("regime", "mode"))


if __name__ == "__main__":
    main()
