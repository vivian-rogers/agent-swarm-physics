"""Synthetic size and power of the Newton-step EP estimators (infra/shared/ep_newton.py), legacy vs corrected.

Worlds (village counts; structure only, no project data):
  potts   N agents, 4 behavior states with a driven single-agent cycle (work -> explore -> coord -> work; H90's P0), on a
          minute grid of D days x L steps. J = 0: independent agents (true sigma_coll = 0). J > 0: planted directed
          coupling, each agent's coord logit gets J x (number of its 2-3 sources in coord at t).
          Observables (H14 O4 layout): single = each agent's antisymmetrized transition indicators (6 per agent);
          pw = s_i^c(t+1) s_j^c(t) - s_i^c(t) s_j^c(t+1) for c in {work, coord} (2 per pair). Nested sets:
          Sigma_1 = Newton(single), Sigma_1+pw = Newton(single u pw), sigma_coll = Sigma_1+pw - Sigma_1.
  ising   N binary spins (H05 X5 layout: all pairwise g_ij, one set). J = 0: independent two-state chains (Sigma = 0).
          J > 0: random asymmetric couplings of scale J/sqrt(N); exact EP = sum_{i<j} (J_ij - J_ji) <g_ij>.
Sizes: S5 = N 15 x 5 days x 230 steps (H14 5-day periods, H05 weekly windows), S16 = N 13 x 16 days (G38),
S24 = N 27 x 24 days (H14's G51 block).
Per replicate: both estimators on the data and on R cross-day surrogates (each agent's days permuted independently,
a derangement; exact null for independent stationary agents); p = (1 + #null >= obs) / (R + 1).
Reference for recovery: the legacy cross-fit on one long simulation (200 days; d/T small, so no divergence) = the
population Gaussian bound 2 mu'K^-1 mu that both estimators target; the corrected estimator's own long-run value is
also reported (it is attenuated by its ridge by design).

  uv run python infra/shared/ep_newton_synthetic.py [--quick]
Writes data/processed/shared/ep_newton_synthetic/{replicates,summary}.parquet and summary.json.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ep_newton as E  # noqa: E402
from common import OUT, write_provenance  # noqa: E402

OUTD = OUT / "ep_newton_synthetic"
SIZES = {"S5": (15, 5, 230), "S16": (13, 16, 230), "S24": (27, 24, 230)}
P0 = np.array([[0.70, 0.12, 0.06, 0.12],
               [0.06, 0.66, 0.20, 0.08],
               [0.18, 0.04, 0.66, 0.12],
               [0.12, 0.08, 0.10, 0.70]])
Q = 4
COORD, WORK = 2, 0


# ============================================================================ worlds
def sources(N, rng):
    A = np.zeros((N, N))
    for i in range(N):
        js = rng.choice([j for j in range(N) if j != i], rng.integers(2, 4), replace=False)
        A[js, i] = 1
    return A


def sim_potts(N, D, L, J, rng, A):
    """(D, L, N) int states."""
    X = np.zeros((D, L, N), np.int8)
    lP = np.log(P0)
    for d in range(D):
        x = rng.integers(0, Q, N)
        for _ in range(20):                       # short burn-in toward the stationary mix
            p = np.exp(lP[x]); p /= p.sum(1, keepdims=True)
            x = (p.cumsum(1) < rng.random(N)[:, None]).sum(1)
        for t in range(L):
            X[d, t] = x
            lg = lP[x].copy()
            lg[:, COORD] += J * ((x == COORD).astype(float) @ A)
            p = np.exp(lg - lg.max(1, keepdims=True)); p /= p.sum(1, keepdims=True)
            x = np.minimum((p.cumsum(1) < rng.random(N)[:, None]).sum(1), Q - 1)
    return X


def potts_G(X):
    """Observables and block ids from (D, L, N). Returns G, day, n_single."""
    D, L, N = X.shape
    Xp = X[:, :-1].reshape(-1, N).astype(np.int64)
    Xn = X[:, 1:].reshape(-1, N).astype(np.int64)
    day = np.repeat(np.arange(D), L - 1)
    iu, ju = np.triu_indices(Q, 1)
    cols = []
    for i in range(N):
        code = Xp[:, i] * Q + Xn[:, i]
        for a, b in zip(iu, ju):
            cols.append((code == a * Q + b).astype(np.float64) - (code == b * Q + a))
    Gs = np.stack(cols, 1)
    Gs = Gs[:, np.any(Gs != 0, 0)]
    pi, pj = np.triu_indices(N, 1)
    pw = []
    for c in (WORK, COORD):
        sp = 2.0 * (Xp == c) - 1
        sn = 2.0 * (Xn == c) - 1
        pw.append(sn[:, pi] * sp[:, pj] - sp[:, pi] * sn[:, pj])
    Gp = np.hstack(pw)
    Gp = Gp[:, np.any(Gp != 0, 0)]
    return np.hstack([Gs, Gp]), day, Gs.shape[1]


def sim_ising(N, D, L, J, rng, Jm=None):
    """(D, L, N) +-1 spins; parallel kinetic Ising with fields h ~ N(-0.3, 0.2) and self-coupling 0.6."""
    h = rng.normal(-0.3, 0.2, N)
    if Jm is None:
        Jm = rng.normal(0, J / np.sqrt(N), (N, N)) if J > 0 else np.zeros((N, N))
        np.fill_diagonal(Jm, 0.6)
    X = np.zeros((D, L, N), np.int8)
    for d in range(D):
        s = np.where(rng.random(N) < 0.5, 1.0, -1.0)
        for _ in range(50):
            s = np.where(rng.random(N) < 1 / (1 + np.exp(-2 * (h + Jm @ s))), 1.0, -1.0)
        for t in range(L):
            X[d, t] = s
            s = np.where(rng.random(N) < 1 / (1 + np.exp(-2 * (h + Jm @ s))), 1.0, -1.0)
    return X, Jm


def ising_G(X):
    D, L, N = X.shape
    Sp = X[:, :-1].reshape(-1, N).astype(np.float64)
    Sn = X[:, 1:].reshape(-1, N).astype(np.float64)
    i, j = np.triu_indices(N, 1)
    return Sn[:, i] * Sp[:, j] - Sp[:, i] * Sn[:, j], np.repeat(np.arange(D), L - 1)


def ising_exact(Jm, X):
    G, _ = ising_G(X)
    i, j = np.triu_indices(Jm.shape[0], 1)
    return float(((Jm[i, j] - Jm[j, i]) * G.mean(0)).sum())


def crossday(X, rng):
    D, _, N = X.shape
    Y = np.empty_like(X)
    for a in range(N):
        for _ in range(100):
            perm = rng.permutation(D)
            if not np.any(perm == np.arange(D)):
                break
        Y[:, :, a] = X[perm, :, a]
    return Y


# ============================================================================ estimators on one data set
def est_potts(X):
    G, day, ns = potts_G(X)
    sub = {"s1": np.arange(ns), "s12": np.arange(G.shape[1])}
    blk = np.r_[np.zeros(ns), np.ones(G.shape[1] - ns)]
    o = E.newton_subsets_xprod(G, day, sub)
    n = E.newton_subsets_heldout(G, day, sub, block=blk)
    return {"old_s1": o["s1"], "old_coll": o["s12"] - o["s1"], "new_s1": n["s1"], "new_coll": n["s12"] - n["s1"],
            "d": G.shape[1], "T": G.shape[0]}


def est_ising(X):
    G, day = ising_G(X)
    return {"old_sig": E.ep_gauss_crossfit(G, day)["sigma"], "new_sig": E.ep_newton_heldout(G, day)["sigma"],
            "d": G.shape[1], "T": G.shape[0]}


def pval(obs, null):
    null = np.asarray(null)
    return float((1 + np.sum(null >= obs)) / (len(null) + 1))


def one(world, size, J, rng, R):
    N, D, L = SIZES[size]
    if world == "potts":
        A = sources(N, rng)
        X = sim_potts(N, D, L, J, rng, A)
        obs = est_potts(X)
        keys = ("old_coll", "new_coll", "old_s1", "new_s1")
        nulls = [est_potts(crossday(X, rng)) for _ in range(R)]
    else:
        X, Jm = sim_ising(N, D, L, J, rng)
        obs = est_ising(X)
        obs["exact"] = ising_exact(Jm, X)
        keys = ("old_sig", "new_sig")
        nulls = [est_ising(crossday(X, rng)) for _ in range(R)]
    row = {"world": world, "size": size, "J": J, **obs}
    for k in keys:
        v = [x[k] for x in nulls]
        row[f"{k}_null_mean"] = float(np.mean(v))
        row[f"{k}_p"] = pval(obs[k], v)
    return row


def reference(world, size, J, rng, days=200):
    """Long-run values: legacy cross-fit (the population Gaussian bound) and the corrected estimator's own limit."""
    N, _, L = SIZES[size]
    if world == "potts":
        X = sim_potts(N, days, L, J, rng, sources(N, rng))
        r = est_potts(X)
        return {"ref_old_coll": r["old_coll"], "ref_new_coll": r["new_coll"], "ref_old_s1": r["old_s1"],
                "ref_new_s1": r["new_s1"]}
    X, Jm = sim_ising(N, days, L, J, rng)
    r = est_ising(X)
    return {"ref_old_sig": r["old_sig"], "ref_new_sig": r["new_sig"], "ref_exact": ising_exact(Jm, X)}


def main(quick=False):
    rng = np.random.default_rng(20261004)
    plan = [("potts", "S5", 0.0, 100), ("potts", "S16", 0.0, 40), ("potts", "S24", 0.0, 30)]
    plan += [("potts", sz, J, n) for sz, n in (("S5", 40), ("S16", 20), ("S24", 15)) for J in (0.25, 0.5, 1.0)]
    plan += [("ising", "S5", 0.0, 60), ("ising", "S5", 0.5, 30), ("ising", "S5", 1.0, 30), ("ising", "S24", 0.0, 20)]
    R = 39
    if quick:
        plan = [(w, s, j, 2) for w, s, j, _ in plan if s == "S5"]
        R = 5
    rows, refs = [], []
    t0 = time.time()
    OUTD.mkdir(parents=True, exist_ok=True)
    for world, size, J, reps in plan:
        for r in range(reps):
            rows.append(one(world, size, J, rng, R) | {"rep": r})
        if True:  # reference for every cell (J = 0 shows the population sigma_coll of independent agents)
            refs.append({"world": world, "size": size, "J": J, **reference(world, size, J, rng, days=60 if quick else 200)})
        print(world, size, J, f"{time.time() - t0:.0f}s", flush=True)
        pl.DataFrame(rows, infer_schema_length=None).write_parquet(OUTD / "replicates.parquet")
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(OUTD / "replicates.parquet")
    summ = []
    for (world, size, J), g in df.group_by(["world", "size", "J"], maintain_order=True):
        s = {"world": world, "size": size, "J": J, "reps": g.height, "d": int(g["d"][0]), "T": int(g["T"][0])}
        ks = ("old_coll", "new_coll", "old_s1", "new_s1") if world == "potts" else ("old_sig", "new_sig", "exact")
        for k in ks:
            v = g[k].to_numpy()
            s[f"{k}_mean"] = float(v.mean())
            s[f"{k}_se"] = float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else None
            s[f"{k}_sd"] = float(v.std(ddof=1)) if len(v) > 1 else None
            if f"{k}_p" in g.columns:
                s[f"{k}_reject05"] = float((g[f"{k}_p"].to_numpy() <= 0.05).mean())
                s[f"{k}_null_mean"] = float(g[f"{k}_null_mean"].mean())
        ref = [x for x in refs if x["world"] == world and x["size"] == size and x["J"] == J]
        if ref:
            s.update({k: v for k, v in ref[0].items() if k.startswith("ref_")})
        summ.append(s)
    pl.DataFrame(summ).write_parquet(OUTD / "summary.parquet")
    (OUTD / "summary.json").write_text(json.dumps({"R_crossday": R, "rows": summ, "runtime_s": time.time() - t0},
                                                  indent=1, default=float))
    if not quick:
        write_provenance("ep_newton_synthetic", tables=[], params={"seed": 20261004, "R": R, "plan": plan, "quick": quick})
    for s in summ:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()})


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)
