"""H99 synthetic check for the content channel (axis F), on the real agent-window masks of two units.

Latent 32-d agent states evolve per 30-min window in mean-field modal coordinates (exact discretization of a linear
Glauber/OU network): the collective mode M (per dimension) is AR(1) with coefficient a^(1-g) and stationary variance
1/(1-g); transverse modes are AR(1) with coefficient a and variance 1. Observed vectors = latent + white measurement
noise (variance s2 x signal) where the real mask has a row. Worlds: ind (g = 0), glauber (g = 0.2, 0.4), slow (a shared
OU field per dimension with coefficient 0.8 per window, sized to g_chi ~ 0.2, g = 0), fast (shared white field per
window, g = 0). The real estimator (agent and day centring, content_sums, boot) is applied.
Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/synthetic_content.py
"""
from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h99lib as L  # noqa: E402

ROOT = HERE.parents[2]
BASE = ROOT / "data/processed/H99-glauber-fluctuation-relaxation"
D = 32


def simulate(agent, day, win, world, g, a, s2, rng):
    ags = np.unique(agent)
    N = len(ags)
    apos = {x: i for i, x in enumerate(ags)}
    out = np.zeros((len(agent), D))
    u = np.ones(N) / np.sqrt(N)
    P = np.eye(N) - np.outer(u, u)
    for d in np.unique(day):
        sd = np.flatnonzero(day == d)
        W = int(win[sd].max()) + 1
        lam = a ** (1 - g)
        Z = np.zeros((W, N, D))
        m = rng.normal(0, np.sqrt(1 / (1 - g)), D)
        t = P @ rng.normal(0, 1, (N, D))
        f = rng.normal(0, 1, D)
        for w in range(W):
            m = lam * m + np.sqrt((1 - lam ** 2) / (1 - g)) * rng.normal(0, 1, D)
            t = a * t + np.sqrt(1 - a ** 2) * (P @ rng.normal(0, 1, (N, D)))
            Z[w] = np.outer(u, m) + t
            if world == "slow":
                f = 0.8 * f + np.sqrt(1 - 0.64) * rng.normal(0, 1, D)
                Z[w] += 0.5 * f[None, :]
            if world == "fast":
                Z[w] += 0.5 * rng.normal(0, 1, D)[None, :]
        for r in sd:
            out[r] = Z[win[r], apos[agent[r]]] + np.sqrt(s2) * rng.normal(0, 1, D)
    return out


def estimate(agent, day, win, V, rng):
    V = V.copy()
    for ag in np.unique(agent):
        V[agent == ag] -= V[agent == ag].mean(0)
    # Amendment A1: no day-mean centring (a leave-in day mean fakes anti-correlation: g_chi -0.21 at independence)
    rows = L.content_sums(agent, day, win, V)
    return L.boot(rows, B=200, rng=rng)


def main():
    res = []
    for unit in ("40", "51g"):
        z = np.load(BASE / "content" / f"{unit}.npz")
        agent, day, win = z["agent"], z["day"], z["win"]
        for world, g in (("ind", 0.0), ("glauber", 0.2), ("glauber", 0.4), ("slow", 0.0), ("fast", 0.0)):
            for s2 in (0.0, 1.0):
                for rep in range(6):
                    rng = np.random.default_rng(zlib.crc32(f"{unit}|{world}|{g}|{s2}|{rep}".encode()))
                    V = simulate(agent, day, win, world, g, 0.5, s2, rng)
                    b = estimate(agent, day, win, V, rng)
                    res.append({"unit": unit, "world": world, "g": g, "s2": s2, "rep": rep,
                                **{k: b.get(k) for k in ("g_chi", "g_chi_lo", "g_chi_hi", "dg", "dg_lo", "dg_hi", "dg2",
                                                         "dg2_lo", "dg2_hi", "dg_nr", "dg_nr_lo", "dg_nr_hi", "g_chi_nr")}})
    df = pl.DataFrame(res, infer_schema_length=None)
    (BASE / "synthetic").mkdir(parents=True, exist_ok=True)
    df.write_parquet(BASE / "synthetic" / "synthetic_content.parquet")
    s = (df.group_by("world", "g", "s2").agg(
        pl.col("g_chi").median().round(3), pl.col("dg").median().round(3).alias("dg1"),
        ((pl.col("dg_lo") <= 0) & (pl.col("dg_hi") >= 0)).mean().round(2).alias("cov1"),
        pl.col("dg_nr").median().round(3).alias("dg_nr"),
        ((pl.col("dg_nr_lo") <= 0) & (pl.col("dg_nr_hi") >= 0)).mean().round(2).alias("cov_nr"),
        ((pl.col("dg_hi") - pl.col("dg_lo")) / 2).median().round(3).alias("hw1"),
        ((pl.col("dg_nr_hi") - pl.col("dg_nr_lo")) / 2).median().round(3).alias("hw_nr"),
        pl.col("g_chi_nr").median().round(3)).sort("world", "g", "s2"))
    print(s.write_csv())
    (BASE / "synthetic" / "synthetic_content_summary.json").write_text(json.dumps(s.to_dicts(), indent=1))


if __name__ == "__main__":
    main()
