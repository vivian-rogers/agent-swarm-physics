"""Synthetic recovery harness (faithfulness axis F) with village sampling.

Parts (card, Observables 1):
  A  recovery vs days D, leader strength J_L and leader activity: KI-1 (block), KI-1-naive, EQ-PL (block)
  B  delayed influence (5-min boxcar) fitted with KI-1 vs KI-5
  C  null calibration and power of the surrogate tests at D = 5: per-coupling z vs N1 (and naive vs N0),
     and the confirmatory leader statistic (rank 1 by I_k and z(I_k) >= 2 vs N1)
Outputs: data/processed/H02-couplings-are-real/harness_{A,B,C}.parquet
Usage: uv run python harness.py [A|B|C ...]
"""
from __future__ import annotations

import os
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"; os.environ["OMP_NUM_THREADS"] = "1"
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl

import h02lib as L

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H02-couplings-are-real"
CAL = json.loads((DATA / "calibration.json").read_text())["III"]
N, TD, KL, RHO = 18, 241, 5, 0.15
NBLK = 8
WORKERS = 3


def leader_h_for_rate(Jself, target=0.10):
    """Field giving a two-state Markov chain stationary active fraction `target` (other inputs ignored)."""
    from scipy.optimize import brentq
    sig = lambda x: 1 / (1 + np.exp(-x))
    def f(h):
        a, b = sig(2 * (h + Jself)), sig(2 * (h - Jself))
        return b / (1 - a + b) - target
    return brentq(f, -6, 6)


def draw_system(rng, JL, low_leader, with_leader=True, background=True):
    k = rng.integers(0, len(CAL["h0"]), N)
    h0 = np.array(CAL["h0"])[k]; Js = np.array(CAL["Jself"])[k]
    Jx = np.zeros((N, N))
    if background:
        m = rng.random((N, N)) < RHO; np.fill_diagonal(m, False)
        Jx[m] = rng.uniform(0.05, 0.25, m.sum()) * np.where(rng.random(m.sum()) < 0.7, 1, -1)
    if with_leader and JL > 0:
        fol = rng.choice(np.arange(1, N), KL, replace=False)
        Jx[fol, 0] = JL
    if low_leader:
        h0[0] = leader_h_for_rate(Js[0], 0.10)
    return h0, Js, Jx


def draw_field(rng, D):
    return rng.normal(0, CAL["sigma_common"], (D, NBLK, 1)) + rng.normal(0, CAL["sigma_agent"], (D, NBLK, N))


def metrics(Jhat, Jx, prefix):
    off = ~np.eye(N, dtype=bool)
    I = L.net_influence(Jhat)
    oth = np.delete(I, 0)
    return {f"{prefix}_auc": L.auc(np.abs(Jhat[off]), Jx[off] != 0),
            f"{prefix}_corr": float(np.corrcoef(Jhat[off], Jx[off])[0, 1]) if Jx[off].std() > 0 else np.nan,
            f"{prefix}_rank": L.rank_of(I, 0), f"{prefix}_lz": float((I[0] - oth.mean()) / oth.std()),
            f"{prefix}_meanoff": float(Jhat[off].mean())}


def run_A(args):
    D, JL, low, rep = args
    rng = np.random.default_rng([20261003, D, int(JL * 100), int(low), rep])
    h0, Js, Jx = draw_system(rng, JL, low)
    S, day, minute = L.simulate(h0, Js, Jx, D, TD, rng, blockfield=draw_field(rng, D))
    out = {"D": D, "JL": JL, "low_leader": low, "rep": rep, "leader_act": float((S[:, 0] > 0).mean()),
           "act": float((S > 0).mean())}
    Jb, _, _ = L.fit_kinetic(S, day, minute, "block", "1"); out |= metrics(Jb, Jx, "ki")
    Jn, _, _ = L.fit_kinetic(S, day, minute, "none", "1"); out |= metrics(Jn, Jx, "naive")
    _, Jsym, _ = L.fit_equal(S, day, minute, "block")
    off = ~np.eye(N, dtype=bool)
    und = (Jx != 0) | (Jx.T != 0)
    hs = L.hub_strength(Jsym)
    out |= {"eq_auc": L.auc(np.abs(Jsym[np.triu(off)]), und[np.triu(off)]), "eq_rank": L.rank_of(hs, 0)}
    # spurious follower-follower couplings in the equilibrium fit (pairs with no true edge)
    fol = np.flatnonzero(Jx[:, 0] == JL) if JL > 0 else np.array([], int)
    ff = np.zeros((N, N), bool)
    if fol.size > 1:
        ff[np.ix_(fol, fol)] = True
    ff &= ~und & off
    noedge = ~und & off & ~ff
    out["eq_ff_minus_none"] = float(Jsym[ff].mean() - Jsym[noedge].mean()) if ff.any() else np.nan
    return out


def run_B(args):
    D, JL, rep = args
    rng = np.random.default_rng([777, D, int(JL * 100), rep])
    h0, Js, Jx = draw_system(rng, JL, False)
    S, day, minute = L.simulate(h0, Js, Jx, D, TD, rng, blockfield=draw_field(rng, D), delay="box", K=5)
    out = {"D": D, "JL": JL, "rep": rep}
    J1, _, _ = L.fit_kinetic(S, day, minute, "block", "1"); out |= metrics(J1, Jx, "ki1")
    J5, _, _ = L.fit_kinetic(S, day, minute, "block", "box", 5); out |= metrics(J5, Jx, "ki5")
    return out


def true_A(args):
    """True net-influence rank of the leader for the part-A system (same seed path as run_A)."""
    D, JL, low, rep = args
    rng = np.random.default_rng([20261003, D, int(JL * 100), int(low), rep])
    h0, Js, Jx = draw_system(rng, JL, low)
    I = L.net_influence(Jx)
    return {"D": D, "JL": JL, "low_leader": low, "rep": rep, "true_rank": L.rank_of(I, 0),
            "true_I_leader": float(I[0]), "true_I_next": float(np.sort(np.delete(I, 0))[-1])}


def run_B2(args):
    """Lag-1 truth (no delay) fitted with KI-5: the cost of choosing the delayed estimator when it is wrong."""
    D, JL, rep = args
    rng = np.random.default_rng([888, D, int(JL * 100), rep])
    h0, Js, Jx = draw_system(rng, JL, False)
    S, day, minute = L.simulate(h0, Js, Jx, D, TD, rng, blockfield=draw_field(rng, D))
    out = {"D": D, "JL": JL, "rep": rep}
    J1, _, _ = L.fit_kinetic(S, day, minute, "block", "1"); out |= metrics(J1, Jx, "ki1")
    J5, _, _ = L.fit_kinetic(S, day, minute, "block", "box", 5); out |= metrics(J5, Jx, "ki5")
    return out


def surrogate_z(S, day, minute, fields, kind, B, rng, lag="1"):
    J, _, _ = L.fit_kinetic(S, day, minute, fields, lag)
    segs = L.segments(day, minute, kind)
    nulls = np.empty((B, *J.shape))
    for b in range(B):
        nulls[b] = L.fit_kinetic(L.circular_shift(S, segs, rng), day, minute, fields, lag)[0]
    z = (J - nulls.mean(0)) / nulls.std(0)
    Inull = np.array([L.net_influence(x) for x in nulls])
    I = L.net_influence(J)
    zI = (I - Inull.mean(0)) / Inull.std(0)
    return J, z, I, zI


def run_C(args):
    JL, background, rep = args
    rng = np.random.default_rng([555, int(JL * 100), int(background), rep])
    D = 5
    h0, Js, Jx = draw_system(rng, JL, False, with_leader=JL > 0, background=background)
    S, day, minute = L.simulate(h0, Js, Jx, D, TD, rng, blockfield=draw_field(rng, D))
    off = ~np.eye(N, dtype=bool)
    out = {"JL": JL, "background": background, "rep": rep}
    for name, fields, kind in [("blockN1", "block", "block"), ("naiveN0", "none", "day"), ("blockN0", "block", "day")]:
        J, z, I, zI = surrogate_z(S, day, minute, fields, kind, 100, rng)
        sig = np.abs(z[off]) > 1.96
        true = Jx[off] != 0
        out |= {f"{name}_frac_sig": float(sig.mean()),
                f"{name}_fpr": float(sig[~true].mean()),
                f"{name}_power": float(sig[true].mean()) if true.any() else np.nan,
                f"{name}_rank": L.rank_of(I, 0), f"{name}_zI": float(zI[0]),
                f"{name}_rankz": L.rank_of(zI, 0),
                f"{name}_pass": bool(L.rank_of(I, 0) == 1 and zI[0] >= 2)}
    return out


def main(parts):
    DATA.mkdir(parents=True, exist_ok=True)
    with Pool(WORKERS) as pool:
        if "A" in parts:
            jobs = [(D, JL, low, r) for D in [1, 2, 3, 5, 10, 20] for JL in [0.1, 0.2, 0.3, 0.5]
                    for low in [False, True] for r in range(40)]
            res = pool.map(run_A, jobs, chunksize=4)
            pl.DataFrame(res).write_parquet(DATA / "harness_A.parquet")
            print("A done", len(res), flush=True)
        if "B" in parts:
            jobs = [(D, JL, r) for D in [5, 20] for JL in [0.3, 0.5] for r in range(40)]
            res = pool.map(run_B, jobs, chunksize=4)
            pl.DataFrame(res).write_parquet(DATA / "harness_B.parquet")
            print("B done", len(res), flush=True)
        if "Atrue" in parts:
            jobs = [(D, JL, low, r) for D in [1, 2, 3, 5, 10, 20] for JL in [0.1, 0.2, 0.3, 0.5]
                    for low in [False, True] for r in range(40)]
            pl.DataFrame(pool.map(true_A, jobs, chunksize=16)).write_parquet(DATA / "harness_A_true.parquet")
            print("Atrue done", flush=True)
        if "B2" in parts:
            jobs = [(D, JL, r) for D in [5, 20] for JL in [0.2, 0.3, 0.5] for r in range(40)]
            pl.DataFrame(pool.map(run_B2, jobs, chunksize=4)).write_parquet(DATA / "harness_B2.parquet")
            print("B2 done", flush=True)
        if "C" in parts:
            jobs = [(JL, bg, r) for JL, bg in [(0.0, False), (0.0, True), (0.2, True), (0.3, True), (0.5, True)]
                    for r in range(30)]
            res = pool.map(run_C, jobs, chunksize=2)
            pl.DataFrame(res).write_parquet(DATA / "harness_C.parquet")
            print("C done", len(res), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or ["A", "B", "C"])
