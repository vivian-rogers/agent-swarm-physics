"""Null-hierarchy fits on non-holdout chunks: mode I vs mode C (card, Observables 2-4).

Per chunk:
  - KI-1 naive vs N0 (day shift) and vs N1 (block shift); KI-1 block vs N1 (primary); KI-5 block vs N1;
    EQ-PL block vs N1. Per-coupling z = (J - mean_null) / sd_null over B surrogates.
  - net outgoing influence I_k and its z vs the N1 surrogate distribution (KI-1 block and KI-5 block).
  - leave-one-day-out: couplings from training days, fields refit on the held-out day; M1 / M2 / M3 log-lik.
Outputs (data/processed/H02-couplings-are-real/): real_chunks.parquet, real_couplings.parquet, real_influence.parquet
Usage: uv run python nulls_real.py [B]
"""
from __future__ import annotations

import os
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import norm

import h02lib as L
from calibrate import load_chunks

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H02-couplings-are-real"
SHARED = ROOT / "data/processed/shared"
NSURR = int(sys.argv[1]) if len(sys.argv) > 1 else 100
WORKERS = 3


# ----------------------------------------------------------------- held-out comparison (N2)
def mean_field_covs(S, labs):
    """Per agent: mean spin of same-lab others (0 if none) and of other-lab agents. Returns (T, N, 2)."""
    T, N = S.shape
    out = np.zeros((T, N, 2))
    labs = np.asarray(labs)
    for i in range(N):
        same = (labs == labs[i]) & (np.arange(N) != i)
        other = labs != labs[i]
        if same.any():
            out[:, i, 0] = S[:, same].mean(1)
        if other.any():
            out[:, i, 1] = S[:, other].mean(1)
    return out


def loglik(eta, y):
    return (y * eta - np.logaddexp(0, eta))


def heldout(S, day, minute, labs):
    """Leave-one-day-out log-lik per transition (nats, summed over agents) for M1, M2, M3."""
    N = S.shape[1]
    X, Y, pen, info = L.kinetic_design(S, day, minute, "block", "1")
    dst = info["dst"]; dday = day[dst]
    nb_cols = X.shape[1] - (1 + N)
    blkcols = X[:, 1 + N:]
    mf = mean_field_covs(S.astype(float), labs)[info["src"]]  # (T', N, 2)
    rows = []
    for d in np.unique(day):
        tr, te = dday != d, dday == d
        keep_tr = blkcols[tr].sum(0) > 0; keep_te = blkcols[te].sum(0) > 0
        Xtr = np.hstack([X[tr][:, :1 + N], blkcols[tr][:, keep_tr]])
        ptr = np.zeros((N, Xtr.shape[1])); ptr[:, 1:1 + N] = L.LAM_J; ptr[:, 1 + N:] = L.LAM_D; ptr[:, 0] = 1e-8
        # M3: full couplings
        B3 = L.fit_logistic(Xtr, Y[tr], ptr)
        # M1: self only
        p1 = ptr.copy(); cp = np.full((N, N), L.BIG); np.fill_diagonal(cp, L.LAM_J); p1[:, 1:1 + N] = cp
        B1 = L.fit_logistic(Xtr, Y[tr], p1)
        # M2: self + same-lab mean + other-lab mean (per-agent designs)
        B2 = []
        for i in range(N):
            Xi = np.hstack([Xtr[:, :1], Xtr[:, 1 + i:2 + i], mf[tr, i, :], Xtr[:, 1 + N:]])
            pi = np.zeros(Xi.shape[1]); pi[1:4] = L.LAM_J; pi[4:] = L.LAM_D; pi[0] = 1e-8
            B2.append(L.fit_logistic(Xi, Y[tr][:, i:i + 1], pi)[0])
        # test day: refit intercept + block fields with coupling part frozen as offset
        Xte_f = np.hstack([np.ones((te.sum(), 1)), blkcols[te][:, keep_te]])
        pf = np.zeros(Xte_f.shape[1]); pf[1:] = L.LAM_D; pf[0] = 1e-8
        Ste = X[te][:, 1:1 + N]
        off3 = Ste @ B3[:, 1:1 + N].T
        off1 = Ste * np.diag(B1[:, 1:1 + N])[None, :]
        off2 = np.stack([B2[i][1] * Ste[:, i] + mf[te, i, :] @ B2[i][2:4] for i in range(N)], 1)
        res = {"day": int(d), "T": int(te.sum())}
        for name, off in [("M1", off1), ("M2", off2), ("M3", off3)]:
            Bf = L.fit_logistic(Xte_f, Y[te], pf, offset=off)
            eta = Xte_f @ Bf.T + off
            res[name] = float(loglik(eta, Y[te]).sum())
        rows.append(res)
    return rows


# ----------------------------------------------------------------- per chunk
def analyse(args):
    ch, c, labs, seed = args
    rng = np.random.default_rng([20261003, seed])
    S, day, minute, agents = c["S"], c["day"], c["minute"], c["agents"]
    N = S.shape[1]
    off = ~np.eye(N, dtype=bool)
    fits = {
        "naive": lambda X: L.fit_kinetic(X, day, minute, "none", "1")[0],
        "block": lambda X: L.fit_kinetic(X, day, minute, "block", "1")[0],
        "box5": lambda X: L.fit_kinetic(X, day, minute, "block", "box", 5)[0],
        "eq": lambda X: L.fit_equal(X, day, minute, "block")[1],
    }
    real = {k: f(S) for k, f in fits.items()}
    segN1, segN0 = L.segments(day, minute, "block"), L.segments(day, minute, "day")
    nullN1 = {k: np.empty((NSURR, N, N)) for k in fits}
    nullN0 = np.empty((NSURR, N, N))
    for b in range(NSURR):
        S1 = L.circular_shift(S, segN1, rng)
        for k, f in fits.items():
            nullN1[k][b] = f(S1)
        nullN0[b] = fits["naive"](L.circular_shift(S, segN0, rng))
    combos = {"naive_N0": (real["naive"], nullN0), "naive_N1": (real["naive"], nullN1["naive"]),
              "block_N1": (real["block"], nullN1["block"]), "box5_N1": (real["box5"], nullN1["box5"]),
              "eq_N1": (real["eq"], nullN1["eq"])}
    lab_arr = np.array([labs[a] for a in agents])
    same = (lab_arr[:, None] == lab_arr[None, :]) & off
    summ = {"chunk": ch, "goal_no": c["goal_no"], "mode": c["mode"], "regime": c["regime"], "N": N,
            "T": int(S.shape[0]), "act": float((S > 0).mean()), "n_days": int(np.unique(day).size),
            "same_lab_share": float(same[off].mean())}
    coup_rows = []
    for name, (J, nul) in combos.items():
        mu, sd = nul.mean(0), nul.std(0)
        z = (J - mu) / sd
        mask = np.triu(off) if name == "eq_N1" else off
        zz = z[mask]
        sig = np.abs(zz) > 1.96
        p = 2 * norm.sf(np.abs(zz))
        summ |= {f"{name}_frac_sig": float(sig.mean()), f"{name}_bh": L.bh_count(p, 0.1),
                 f"{name}_npairs": int(mask.sum()),
                 f"{name}_frac_pos_sig": float((zz[sig] > 0).mean()) if sig.any() else np.nan,
                 f"{name}_absJ": float(np.abs(J[mask]).mean()), f"{name}_absJ_null": float(np.abs(nul[:, mask]).mean()),
                 f"{name}_meanJ": float(J[mask].mean()), f"{name}_meanJ_null": float(nul[:, mask].mean()),
                 f"{name}_mean_z2": float((zz ** 2).mean())}
        if name in ("block_N1", "box5_N1"):
            sm = same[mask]
            summ |= {f"{name}_sig_same_share": float(sm[sig].mean()) if sig.any() else np.nan,
                     f"{name}_z_same": float(zz[sm].mean()) if sm.any() else np.nan,
                     f"{name}_z_cross": float(zz[~sm].mean())}
        ii, jj = np.nonzero(mask)
        for a, b_, Jv, zv, mv, sv in zip(ii, jj, J[mask], zz, mu[mask], sd[mask]):
            coup_rows.append({"chunk": ch, "est": name, "i": agents[a], "j": agents[b_], "J": float(Jv),
                              "z": float(zv), "null_mean": float(mv), "null_sd": float(sv),
                              "same_lab": bool(same[a, b_])})
    infl_rows = []
    for name in ("block", "box5", "naive"):
        I = L.net_influence(real[name])
        In = np.array([L.net_influence(x) for x in nullN1[name]])
        zI = (I - In.mean(0)) / In.std(0)
        for k, a in enumerate(agents):
            infl_rows.append({"chunk": ch, "est": name, "agent": a, "I": float(I[k]), "zI": float(zI[k]),
                              "rank": L.rank_of(I, k), "act": float((S[:, k] > 0).mean())})
    # held-out (N2)
    ho = heldout(S, day, minute, lab_arr)
    T_ho = sum(r["T"] for r in ho)
    for m in ("M1", "M2", "M3"):
        summ[f"ho_{m}"] = sum(r[m] for r in ho)
    summ["ho_T"] = T_ho
    summ["ho_d31_per_bin"] = (summ["ho_M3"] - summ["ho_M1"]) / T_ho
    summ["ho_d21_per_bin"] = (summ["ho_M2"] - summ["ho_M1"]) / T_ho
    summ["ho_days_M3_gt_M1"] = int(sum(r["M3"] > r["M1"] for r in ho))
    summ["ho_days_M3_gt_M2"] = int(sum(r["M3"] > r["M2"] for r in ho))
    summ["ho_days_M2_gt_M1"] = int(sum(r["M2"] > r["M1"] for r in ho))
    return summ, coup_rows, infl_rows


def main():
    chunks = load_chunks()
    roster = pl.read_parquet(SHARED / "roster.parquet")
    labs = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    jobs = [(ch, c, labs, k) for k, (ch, c) in enumerate(sorted(chunks.items()))]
    with Pool(WORKERS) as pool:
        out = pool.map(analyse, jobs, chunksize=1)
    pl.DataFrame([o[0] for o in out]).write_parquet(DATA / "real_chunks.parquet")
    pl.DataFrame([r for o in out for r in o[1]]).write_parquet(DATA / "real_couplings.parquet", compression="zstd")
    pl.DataFrame([r for o in out for r in o[2]]).write_parquet(DATA / "real_influence.parquet")
    print("done", len(out))


if __name__ == "__main__":
    main()
