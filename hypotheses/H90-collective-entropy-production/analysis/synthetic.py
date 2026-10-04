"""H90 synthetic validation (axis F): planted directed coupling vs block-flip / block-shift nulls at village counts.

  uv run python hypotheses/H90-collective-entropy-production/analysis/synthetic.py [--quick]

Sizes (from the real trimmed counts, structure only): S40 N 15 x 5 days (40 behavior steps / 200 talk minutes per day),
S38 N 13 x 16 days (44 / 220), S51 N 27 x 33 days (69 / 345).
Scenarios: '0' independent agents; 'F' common drive with agent-specific lags and talk-rate-biased naming (no coupling);
'C0.5', 'C1' gated coupling from each agent's 2-3 namers. Behavior: 4 latent states with a driven cycle
(work -> explore -> coord -> work) and soft labels; talk: binary bursts.
Writes data/processed/H90-collective-entropy-production/synthetic/summary.parquet (+ replicates.parquet).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h90lib as L  # noqa: E402

SIZES = {"S40": (15, 5, 40, 200), "S38": (13, 16, 44, 220), "S51": (27, 33, 69, 345)}
SCEN = {"0": (0.0, 0.0), "F": (0.0, 1.0), "C0.5": (0.5, 0.0), "C1": (1.0, 0.0)}


def naming_graph(N, rng, rates=None):
    """A[j, i] = 1 if j names i (2-3 namers per agent); w = observed message counts (with naming noise)."""
    A = np.zeros((N, N), int)
    for i in range(N):
        k = rng.integers(2, 4)
        p = np.ones(N) if rates is None else rates.copy()
        p[i] = 0
        p = p / p.sum()
        js = rng.choice(N, k, replace=False, p=p)
        A[js, i] = 1
    w = A * rng.poisson(8, (N, N)) + rng.poisson(0.3, (N, N))
    np.fill_diagonal(w, 0)
    return A, w


def ar1(T, tau, sd, rng):
    a = np.exp(-1 / tau)
    x = np.zeros(T)
    e = rng.normal(0, sd * np.sqrt(1 - a * a), T)
    x[0] = rng.normal(0, sd)
    for t in range(1, T):
        x[t] = a * x[t - 1] + e[t]
    return x


# ---------------------------------------------------------------- behavior (5 columns; absent unused in trimmed windows)
P0 = np.array([[0.70, 0.12, 0.06, 0.12],     # work -> work, explore, coord, wait
               [0.06, 0.66, 0.20, 0.08],     # explore
               [0.18, 0.04, 0.66, 0.12],     # coord
               [0.12, 0.08, 0.10, 0.70]])    # wait   (driven cycle work -> explore -> coord -> work)


def sim_behavior(N, D, T, J, field, rng, A):
    days = []
    lag = rng.integers(0, 3, N)
    for _ in range(D):
        f = ar1(T + 3, 6, 1.0, rng) * field
        x = np.zeros((N, T), int)
        x[:, 0] = rng.integers(0, 4, N)
        for t in range(T - 1):
            cnt = (x[:, t] == 2).astype(float) @ A               # namers in coord at t
            logits = np.log(P0[x[:, t]])
            logits[:, 2] += J * cnt + f[t + 3 - lag]
            p = np.exp(logits - logits.max(1, keepdims=True))
            p /= p.sum(1, keepdims=True)
            u = rng.random(N)[:, None]
            x[:, t + 1] = (p.cumsum(1) < u).sum(1)
        # soft labels: confidence c on the true state, the rest spread at random over the other 3 latent states
        c = rng.beta(6, 2, (N, T))
        X = np.zeros((N, T, 5), np.float32)
        rest = rng.dirichlet(np.ones(3), (N, T)) * (1 - c)[..., None]
        for i in range(N):
            for t in range(T):
                k = x[i, t]
                others = [o for o in range(4) if o != k]
                X[i, t, 1 + k] = c[i, t]
                X[i, t, [1 + o for o in others]] = rest[i, t]
        days.append({"agents": np.arange(N), "X": X})
    return days


def sim_talk(N, D, T, J, field, rng, A, b):
    days = []
    lag = rng.integers(0, 3, N)
    for _ in range(D):
        f = ar1(T + 3, 15, 1.0, rng) * field
        s = np.zeros((N, T), np.uint8)
        s[:, 0] = rng.random(N) < 0.08
        for t in range(T - 1):
            drive = b + 2.0 * s[:, t] + J * (s[:, t].astype(float) @ A) + f[t + 3 - lag]
            s[:, t + 1] = rng.random(N) < 1 / (1 + np.exp(-drive))
        days.append({"agents": np.arange(N), "X": s})
    return days


def one(size, scen, channel, rng, R_shift, R_flip):
    N, D, Tb, Tt = SIZES[size]
    J, field = SCEN[scen]
    b = rng.normal(-3.0, 0.5, N)
    rates = 1 / (1 + np.exp(-b))
    A, w = naming_graph(N, rng, rates if scen == "F" else None)
    if channel == "behavior":
        days = sim_behavior(N, D, Tb, J, field, rng, A)
    else:
        days = sim_talk(N, D, Tt, J, field, rng, A, b)
    obs, stats, lay, folds = L.period_estimate(days, channel, N, w, per_agent=True)
    sh = L.null_dist(days, channel, N, w, "shift", R_shift, rng, folds=folds)
    fl = L.null_dist(days, channel, N, w, "flip", R_flip, rng, folds=folds)
    row = {"size": size, "scen": scen, "channel": channel, "N": N, "days": D}
    for k in ("Sigma1", "sum_sigma_i", "Sigma1_all", "coll_all", "coll_named", "coll_unnamed", "addr", "rho_coll"):
        row[k] = obs[k]
    for k in ("coll_all", "coll_named", "addr"):
        v = [x[k] for x in sh]
        row[f"{k}_p_shift"] = L.pval(obs[k], v)
        row[f"{k}_shift_q95"] = float(np.nanpercentile(v, 95))
        row[f"{k}_shift_mean"] = float(np.nanmean(v))
    for k in ("Sigma1", "coll_all"):
        v = [x[k] for x in fl]
        row[f"{k}_flip_mean"] = float(np.nanmean(v))
        row[f"{k}_flip_sd"] = float(np.nanstd(v))
        row[f"{k}_p_flip"] = L.pval(obs[k], v)
    return row


def main(quick=False):
    rng = np.random.default_rng(9090)
    reps = {("S40", "talk"): 25, ("S38", "talk"): 20, ("S51", "talk"): 12,
            ("S40", "behavior"): 25, ("S38", "behavior"): 12, ("S51", "behavior"): 6}
    if quick:
        reps = {k: 2 for k in reps}
    rows = []
    t0 = time.time()
    for size in SIZES:
        for ch in ("talk", "behavior"):
            for scen in SCEN:
                for r in range(reps[(size, ch)]):
                    rs, rf = (30, 10) if ch == "talk" else (20, 5)
                    rows.append(one(size, scen, ch, rng, R_shift=rs, R_flip=rf) | {"rep": r})
                print(size, ch, scen, f"{time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(rows)
    out = L.OUTD / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out / "replicates.parquet")
    summ = df.group_by(["size", "channel", "scen"], maintain_order=True).agg(
        pl.len().alias("reps"),
        (pl.col("coll_all_p_shift") < 0.05).mean().alias("P_coll_shift"),
        (pl.col("addr_p_shift") < 0.05).mean().alias("P_addr_shift"),
        ((pl.col("coll_named_p_shift") < 0.05)).mean().alias("P_named_shift"),
        pl.col("coll_all").mean().alias("coll_all_mean"), pl.col("coll_named").mean().alias("coll_named_mean"),
        pl.col("coll_unnamed").mean().alias("coll_unnamed_mean"), pl.col("Sigma1").mean().alias("Sigma1_mean"),
        pl.col("sum_sigma_i").mean().alias("sum_sigma_i_mean"), pl.col("rho_coll").median().alias("rho_med"),
        pl.col("coll_all_flip_mean").mean().alias("coll_flip_mean"), pl.col("coll_all_flip_sd").mean().alias("coll_flip_sd"),
        pl.col("Sigma1_flip_mean").mean().alias("Sigma1_flip_mean"),
        (pl.col("Sigma1_p_flip") < 0.05).mean().alias("P_single_flip"))
    summ.write_parquet(out / "summary.parquet")
    pl.Config.set_tbl_cols(20)
    pl.Config.set_tbl_width_chars(250)
    print(summ)


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)
