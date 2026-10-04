"""H123 synthetic validation (axis F), run after the audit and before any real-data EP number.

Symmetric-J heat-bath kinetic Ising (N = 10, talk-like rate 30%) on three update orders at G27's real step counts and
day folds: exact round robin, rate-matched random sequential (the real sequence shuffled within day), and the real
G27 actor sequence (order only; no real states). Plus an asymmetric world on a random order. Same estimator as the
real data (held-out Newton, sigma_x(L) = Sigma(single u cross_L) - Sigma(single)).

Output: data/processed/H123-regime1-turn-sweep/synthetic/summary.parquet, pipeline.json
Usage: uv run python hypotheses/H123-regime1-turn-sweep/analysis/synthetic.py [--reps 12]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h123lib as L  # noqa: E402

J0S = (0.0, 0.5, 1.0, 2.0)
RATE = 0.30


def orders(days_data, N, rng):
    real = [(d, a) for d, a, _ in days_data]
    rr = [(d, np.arange(len(a)) % N) for d, a in real]
    rnd = [(d, rng.permutation(a)) for d, a in real]
    return {"round_robin": rr, "random": rnd, "real_G27": real}


def couplings(N, J0, rng, asym=False):
    A = rng.normal(0, J0 / np.sqrt(N), (N, N))
    Js = np.triu(A, 1)
    Js = Js + Js.T
    if not asym:
        return Js
    B = rng.normal(0, J0 / np.sqrt(N), (N, N))
    Ja = np.triu(B, 1)
    Ja = Ja - Ja.T
    return Js + Ja


def run_cell(order, N, J0, reps, rng, asym=False, n_floor=15):
    h = np.full(N, np.arctanh(2 * RATE - 1))
    vals, floors = [], []
    for r in range(reps):
        J = couplings(N, J0, rng, asym)
        sim = L.simulate(order, h, J, 1, rng)[0]
        vals.append(L.ep_cross(sim, N))
        if r < 3:
            for _ in range(n_floor // 3):
                floors.append(L.ep_cross(L.block_flip(sim, rng), N))
    out = {}
    for lag in L.LAGS:
        v = np.array([x[f"x{lag}"] for x in vals])
        f = np.array([x[f"x{lag}"] for x in floors])
        q95 = float(np.quantile(f, 0.95))
        out.update({f"x{lag}_mean": float(v.mean()), f"x{lag}_sd": float(v.std(ddof=1)),
                    f"floor{lag}_q95": q95, f"pass{lag}": float(np.mean(v > q95))})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=12)
    args = ap.parse_args()
    out_dir = L.OUT / "synthetic"
    out_dir.mkdir(exist_ok=True)
    S = L.load_steps("27")
    dd, codes = L.spins(S, "talk")
    N = len(codes)
    rng = np.random.default_rng(20261004)
    ords = orders(dd, N, rng)
    rows = []
    t0 = time.time()
    for name, order in ords.items():
        for J0 in J0S:
            res = run_cell(order, N, J0, args.reps, rng)
            rows.append({"order": name, "J0": J0, "asym": False, **res})
            print(name, J0, {k: round(v, 5) for k, v in res.items()}, f"{time.time() - t0:.0f}s", flush=True)
    for J0 in J0S[1:]:
        res = run_cell(ords["random"], N, J0, args.reps, rng, asym=True)
        rows.append({"order": "random", "J0": J0, "asym": True, **res})
        print("asym random", J0, {k: round(v, 5) for k, v in res.items()}, f"{time.time() - t0:.0f}s", flush=True)
    pl.DataFrame(rows).write_parquet(out_dir / "summary.parquet")
    # (d) pipeline check: true symmetric J at J0 = 1 on round robin and real order; fit J from one replicate, then
    # sweep_predictions vs the true-J sigma.
    h = np.full(N, np.arctanh(2 * RATE - 1))
    pipe = {}
    for name in ("round_robin", "real_G27"):
        J = couplings(N, 1.0, rng)
        sim = L.simulate(ords[name], h, J, 1, rng)[0]
        hf, Jf = L.fit_heatbath(sim, N)
        true = L.sweep_predictions(sim, N, R=8, seed=1, J_override=J, h_override=h)
        fit = L.sweep_predictions(sim, N, R=8, seed=2, J_override=Jf, h_override=hf)
        pipe[name] = {"J_err": float(np.linalg.norm(Jf - J) / np.linalg.norm(J)),
                      **{f"true_sweep_x{lag}": true[f"sweep_x{lag}"] for lag in L.LAGS},
                      **{f"fit_sweep_x{lag}": fit[f"sweep_x{lag}"] for lag in L.LAGS},
                      **{f"true_rand_x{lag}": true[f"rand_x{lag}"] for lag in L.LAGS}}
        print("pipeline", name, {k: round(v, 5) for k, v in pipe[name].items()}, flush=True)
    (out_dir / "pipeline.json").write_text(json.dumps(pipe, indent=1))


if __name__ == "__main__":
    main()
