"""H99 synthetic validation (axis F) on real trimmed masks.

Binary spins are simulated at 10-s substeps on the real kept-minute masks and per-day agent counts of four units and
observed per minute ('or': talk at any substep of the minute, as a talk minute; 'point': state at the minute's end).
Each agent holds a state sigma_i in {0, 1}; at every substep it updates with probability 1/(6 tau0) by heat bath:
    P(sigma_i = 1) = sigmoid(h_i + Kc * sum_{j != i} (sigma_j(t - delay) - pi_j) + a * f(t))
Worlds: ind (Kc = 0, a = 0); glauber g in {0.1, 0.2, 0.4} (Kc = g / ((N - 1) <pi(1 - pi)>), no delay);
fast (OU field f with lifetime 1 min, a sized to g_chi ~ 0.15, Kc = 0); slow (lifetime 10 min); delay (g = 0.15,
delay 2 min). tau0 in {1, 3} min. Per-agent pi from the unit's real talk rates (descriptive).
The estimator is the real one (h99lib.binary_sums + boot, B = 200).

Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/synthetic.py [--reps 8]
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h99lib as L  # noqa: E402

ROOT = HERE.parents[2]
BASE = ROOT / "data/processed/H99-glauber-fluctuation-relaxation"
OUT = BASE / "synthetic"
UNITS = ["8", "27", "38a", "51g"]
SUB = 6
A_FIELD = {"fast": 1.0, "slow": 0.6}


def load_masks(unit):
    z = np.load(BASE / "grids" / f"{unit}.npz")
    nd = len(z["days"])
    keeps = [z[f"keep_{k}"] for k in range(nd)]
    rates = [np.clip(z[f"talk_{k}"][:, z[f"keep_{k}"]].mean(1), 0.01, 0.6) for k in range(nd)]
    return keeps, rates


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sim_day(keep, rate, world, tau0, rng, g=0.0, obs="or"):
    L_ = len(keep)
    N = len(rate)
    pi = np.clip(rate * 0.6, 0.005, 0.5)
    h = np.log(pi / (1 - pi))
    u = 1.0 / (SUB * tau0)
    Kc = 0.0
    delay = 0
    a = 0.0
    tau_f = None
    if world.startswith("glauber") or world == "delay":
        Kc = g / ((N - 1) * np.mean(pi * (1 - pi)))
        if world == "delay":
            delay = 2 * SUB
    if world in ("fast", "slow"):
        a = A_FIELD[world]
        tau_f = 0.25 if world == "fast" else 10.0
    nsteps = L_ * SUB
    sig = (rng.random(N) < pi).astype(float)
    hist = np.zeros((max(delay, 1) + 1, N))
    hist[:] = sig
    f = 0.0
    phi = np.exp(-1.0 / (SUB * tau_f)) if tau_f else 0.0
    obs_or = np.zeros((N, L_), np.int8)
    obs_pt = np.zeros((N, L_), np.int8)
    for s in range(nsteps):
        if tau_f:
            f = phi * f + np.sqrt(1 - phi ** 2) * rng.standard_normal()
        src = hist[(s - delay) % len(hist)] if delay else sig
        tot = src.sum()
        field = h + a * f
        if Kc:
            field = field + Kc * ((tot - src) - (pi.sum() - pi))
        upd = rng.random(N) < u
        if upd.any():
            new = (rng.random(N) < sigmoid(field)).astype(float)
            sig = np.where(upd, new, sig)
        if delay:
            hist[s % len(hist)] = sig
        m = s // SUB
        obs_or[:, m] |= sig.astype(np.int8)
        if s % SUB == SUB - 1:
            obs_pt[:, m] = sig.astype(np.int8)
    return obs_or if obs == "or" else obs_pt


def job(args):
    unit, world, g, tau0, rep, obs = args
    rng = np.random.default_rng(zlib.crc32(f"{unit}|{world}|{g}|{tau0}|{rep}|{obs}".encode()))
    keeps, rates = load_masks(unit)
    days = [sim_day(k, r, world, tau0, rng, g, obs) for k, r in zip(keeps, rates)]
    rows = L.binary_sums(days, keeps)
    b = L.boot(rows, B=200, rng=rng)
    out = {"unit": unit, "world": world, "g_true": g, "tau0": tau0, "rep": rep, "obs": obs}
    out.update({k: b.get(k) for k in ("g_chi", "g_chi_lo", "g_chi_hi", "g_tau", "g_tau_lo", "g_tau_hi", "dg", "dg_lo",
                                      "dg_hi", "dg_se", "dg_ml", "dg_ml_lo", "dg_ml_hi", "rho_c1", "rho_p1", "K",
                                      "dg_nr", "dg_nr_lo", "dg_nr_hi", "dg2", "dg2_lo", "dg2_hi", "dg3",
                                      "dg3_lo", "dg3_hi", "dg5", "dg5_lo", "dg5_hi", "g_tau3")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    worlds = [("ind", 0.0), ("glauber", 0.1), ("glauber", 0.2), ("glauber", 0.4), ("fast", 0.0), ("slow", 0.0),
              ("delay", 0.15)]
    units = UNITS[:2] if a.quick else UNITS
    jobs = [(u, w, g, t, r, "or") for u in units for (w, g) in worlds for t in (1.0, 3.0) for r in range(a.reps)]
    jobs += [(u, w, g, 1.0, r, "point") for u in units for (w, g) in worlds if w in ("glauber",) for r in range(a.reps)]
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(job, jobs))
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(OUT / "synthetic.parquet")
    s = (df.with_columns(cov0=(pl.col("dg_lo") <= 0) & (pl.col("dg_hi") >= 0),
                         neg=(pl.col("dg_hi") < 0), pos=(pl.col("dg_lo") > 0),
                         gsig=(pl.col("g_chi_lo") > 0))
         .group_by("world", "g_true", "tau0", "obs").agg(
             pl.len().alias("n"), pl.col("g_chi").median().alias("g_chi"), pl.col("g_tau").median().alias("g_tau"),
             pl.col("dg").median().alias("dg_med"), pl.col("dg").abs().median().alias("absdg_med"),
             pl.col("cov0").mean().alias("ci_covers0"), pl.col("neg").mean().alias("dg_neg"),
             pl.col("pos").mean().alias("dg_pos"), pl.col("gsig").mean().alias("g_chi_sig"),
             ((pl.col("dg_hi") - pl.col("dg_lo")) / 2).median().alias("dg_halfwidth"),
             pl.col("dg_ml").median().alias("dg_ml_med"), pl.col("dg2").median().alias("dg2_med"),
             pl.col("dg3").median().alias("dg3_med"), ((pl.col("dg3_lo") <= 0) & (pl.col("dg3_hi") >= 0)).mean().alias("ci3_covers0"),
             (pl.col("dg3_lo") > 0).mean().alias("dg3_pos"), (pl.col("dg3_hi") < 0).mean().alias("dg3_neg"),
             ((pl.col("dg3_hi") - pl.col("dg3_lo")) / 2).median().alias("dg3_hw"))
         .sort("world", "g_true", "tau0", "obs"))
    pl.Config.set_tbl_rows(100)
    pl.Config.set_tbl_width_chars(220)
    print(s)
    by_unit = (df.filter(pl.col("obs") == "or").group_by("unit", "world", "g_true").agg(
        pl.col("dg").median().alias("dg_med"), ((pl.col("dg_hi") - pl.col("dg_lo")) / 2).median().alias("hw"))
        .sort("unit", "world", "g_true"))
    print(by_unit)
    (OUT / "synthetic_summary.json").write_text(json.dumps({"summary": s.to_dicts(), "by_unit": by_unit.to_dicts(),
                                                            "A_FIELD": A_FIELD}, indent=1, default=float))


if __name__ == "__main__":
    main()
