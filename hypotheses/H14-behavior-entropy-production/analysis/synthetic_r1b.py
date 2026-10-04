"""H14 round 1b synthetic check (axis F), run before any real-data round-1b statistic.

1. The fast count-based DB null reproduces H14's size (reversible chains, cold daily starts) and power.
2. The block-flip null (blocks of 12 steps) has size <= 0.07 on reversible chains with cold daily starts, for hard
   states and for Jev-like soft vectors (argmax accuracy ~0.6), at v3-like sampling (q = 8, 5 days x 48 windows and
   20 days x 96 windows), and power against an irreversible chain.
3. Soft-observable Newton is a lower bound: compare with the hidden chain's exact EP.
Writes data/processed/H14-behavior-entropy-production/r1b/synthetic_r1b.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1b_lib as B  # noqa: E402
import numpy as np  # noqa: E402

OUT = B.ROOT / "data/processed/H14-behavior-entropy-production/r1b"


def chain(q, rng, irr=0.0):
    """Random reversible chain (symmetric weights / pi) plus an optional cyclic drive of strength irr."""
    W = rng.gamma(0.6, 1.0, (q, q))
    W = (W + W.T) / 2
    np.fill_diagonal(W, W.sum(1) * 1.5)
    P = W / W.sum(1, keepdims=True)
    if irr > 0:
        for i in range(q):
            j = (i + 1) % q
            d = irr * min(P[i, j], P[j, i] if True else 0)
            P[i, j] += d
            P[j, i] = max(P[j, i] - d, 1e-6)
        P = P / P.sum(1, keepdims=True)
    return P


def exact_ep(P):
    w, v = np.linalg.eig(P.T)
    pi = np.real(v[:, np.argmin(np.abs(w - 1))])
    pi = np.abs(pi) / np.abs(pi).sum()
    F = pi[:, None] * P
    m = (F > 0) & (F.T > 0)
    return float(0.5 * np.sum((F - F.T)[m] * np.log(F[m] / F.T[m])))


def simulate(P, n_days, L, rng, cold=0):
    q = len(P)
    cP = np.cumsum(P, 1)
    xs, ds = [], []
    for d in range(n_days):
        x = np.empty(L, np.int64)
        x[0] = cold
        u = rng.random(L)
        for t in range(1, L):
            x[t] = min(int(np.searchsorted(cP[x[t - 1]], u[t])), q - 1)
        xs.append(x); ds.append(np.full(L, d))
    return np.concatenate(xs), np.concatenate(ds)


def soften(x, q, rng, acc=0.6, conc=2.0):
    lab = np.where(rng.random(len(x)) < acc, x, rng.integers(0, q, len(x)))
    alpha = np.full((len(x), q), 0.3)
    alpha[np.arange(len(x)), lab] += conc
    g = rng.gamma(alpha)
    return g / g.sum(1, keepdims=True)


def one(P, n_days, L, rng, R=100):
    q = len(P)
    x, d = simulate(P, n_days, L, rng)
    ok = d[1:] == d[:-1]
    a, b, dd = x[:-1][ok], x[1:][ok], d[1:][ok]
    C = B.day_counts(a, b, dd, q, n_days)
    obs = B.newton_counts(C)
    # DB null
    s0 = np.array([x[d == k][0] for k in range(n_days)])
    Ls = np.full(n_days, L - 1)
    Cn = B.db_null_counts(a, b, dd, s0, Ls, np.arange(n_days), q, n_days, R, rng)
    dbn = np.array([B.newton_counts(c) for c in Cn])
    # flip null (hard)
    seg = dd
    blk = B.blocks_of(seg, 12)
    Cb, bd = B.block_counts(a, b, dd, blk, q)
    fl = B.flip_null_counts(Cb, bd, n_days, R, rng)
    # soft
    Pm = soften(x, q, rng)
    G = B.soft_G(Pm[:-1][ok], Pm[1:][ok])
    sobs = B.newton_G(G, dd)
    sfl = B.flip_null_G(G, dd, blk, R, rng)
    return {"obs": obs, "p_db": B.pval(dbn, obs), "p_flip": B.pval(fl, obs), "soft": sobs, "p_soft_flip": B.pval(sfl, sobs)}


def main():
    rng = np.random.default_rng(20261004)
    res = {}
    q = 8
    for samp, (nd, L, reps) in {"4h_5x48": (5, 48, 60), "8h_20x96": (20, 96, 40), "turns_10x300": (10, 300, 40)}.items():
        for irr in (0.0, 0.5):
            rows = []
            for _ in range(reps):
                P = chain(q, rng, irr)
                r = one(P, nd, L, rng)
                r["true"] = exact_ep(P)
                rows.append(r)
            out = {"reps": reps, "true_median": float(np.median([r["true"] for r in rows])),
                   "newton_median": float(np.nanmedian([r["obs"] for r in rows])),
                   "soft_newton_median": float(np.nanmedian([r["soft"] for r in rows])),
                   "rej_db": float(np.mean([r["p_db"] < 0.05 for r in rows])),
                   "rej_flip": float(np.mean([r["p_flip"] < 0.05 for r in rows])),
                   "rej_soft_flip": float(np.mean([r["p_soft_flip"] < 0.05 for r in rows]))}
            res[f"{samp}/irr{irr}"] = out
            print(samp, irr, json.dumps(out), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "synthetic_r1b.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
