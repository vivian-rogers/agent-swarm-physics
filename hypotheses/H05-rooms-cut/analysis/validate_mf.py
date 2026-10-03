"""H05-MF estimator check on synthetic kinetic Ising data (no project data touched).

Two rooms (4 + 11 agents, the #best/#rest sizes), 5 days x 241 bins, self-coupling 0.7, activity ~0.5.
True couplings J_in ~ N(mu, 0.05) within rooms and J_out = mu (one room) or 0 (cut). The block mean-field
estimator sees only block-averaged equal-time correlations (with a cross-day surrogate subtracted, as on the real
data) and variances. Does it rank J_in > J_out, return J_out ~ 0 after a cut, and how does its scale relate to mu?

Usage: uv run python hypotheses/H05-rooms-cut/analysis/validate_mf.py
Writes data/processed/H05-rooms-cut/validate_mf.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ep import simulate_kinetic_ising
from mf_blocks import block_J

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H05-rooms-cut"


def day_corr(S):
    X = S.astype(float); X -= X.mean(0); s = X.std(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (X.T @ X) / len(X) / np.outer(s, s)


def run(rng, mu, cut, nd=5, L=241, N=15, nrep=20):
    rooms = np.r_[np.zeros(4, int), np.ones(11, int)]
    out = []
    for _ in range(nrep):
        J = rng.normal(mu, 0.05, (N, N))
        if cut:
            J[rooms[:, None] != rooms[None, :]] = 0.0
        np.fill_diagonal(J, 0.7)
        h = rng.normal(0, 0.15, N)
        # a shared daily-schedule field, so the cross-day surrogate has something to remove
        ht = np.zeros(L); ht[:15] = np.linspace(-1.0, 0, 15)
        S, d = simulate_kinetic_ising(J, h, nd, L, rng=rng, h_t=ht)
        days = [S[d == k] for k in range(nd)]
        C = np.nanmean([day_corr(x) for x in days], 0)
        Cs = np.nanmean([day_corr(np.hstack([days[a], days[b]]))[:N, N:] for a in range(nd) for b in range(nd) if a != b], 0)
        Cs = 0.5 * (Cs + Cs.T)
        act = (S > 0).mean(0); v = 4 * act * (1 - act)
        ii, jj = np.triu_indices(N, 1)
        r = (C - Cs)[ii, jj]; sv = np.sqrt(v[ii] * v[jj])
        q = block_J(ii, jj, r, sv, rooms)
        out.append((q["J_in"], q["J_out"]))
    a = np.array(out)
    return {"mu": mu, "cut": cut, "J_in_mean": float(a[:, 0].mean()), "J_out_mean": float(a[:, 1].mean()),
            "J_out_sd": float(a[:, 1].std()), "frac_in_gt_out": float(np.mean(a[:, 0] > a[:, 1]))}


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    res = [run(rng, mu, cut) for mu in (0.01, 0.02, 0.04) for cut in (False, True)]
    for r in res:
        print(r)
    (OUT / "validate_mf.json").write_text(json.dumps(res, indent=1))
