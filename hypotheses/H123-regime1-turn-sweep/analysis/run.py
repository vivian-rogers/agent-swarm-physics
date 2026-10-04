"""H123 O3/O4: cross-agent EP at lags 1, 2, 4 on event-time spins, the floor (block flips), and the sweep predictions
(symmetric fitted J on the real order vs on a random order; fitted J on the real order). Runs after audit.py and
synthetic.py. Units with >= 2 days (day folds). Channels: talk (primary), mode (cu vs chat).

Output: data/processed/H123-regime1-turn-sweep/results/ep.parquet (+ ep.json), sens_G27.json
Usage: uv run python hypotheses/H123-regime1-turn-sweep/analysis/run.py [--units 27,23] [--floor 30] [--reps 20]
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


def hours_and_n(S: pl.DataFrame):
    g = S.group_by("day").agg((pl.col("t_call").max() - pl.col("t_call").min()).dt.total_seconds().alias("s"),
                              pl.col("agent").n_unique().alias("n"))
    return float(g["s"].sum() / 3600), float(g["n"].mean())


def jboot(dd, N, rng, B=50):
    vals = []
    for _ in range(B):
        pick = rng.integers(0, len(dd), len(dd))
        h, J = L.fit_heatbath([dd[i] for i in pick], N)
        Js = (J + J.T) / 2
        vals.append(float(np.sqrt(np.mean(Js[~np.eye(N, dtype=bool)] ** 2))))
    return [float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))]


def unit_channel(S, ch, n_floor, reps, rng, edge=L.EDGE, drop_first=False):
    if drop_first:
        S = S.filter(pl.col("day") != S["day"].min())
    dd, codes = L.spins(S, ch, edge=edge)
    N = len(codes)
    if len(dd) < 2:
        return None
    real = L.ep_cross(dd, N)
    fl = [L.ep_cross(L.block_flip(dd, rng), N) for _ in range(n_floor)]
    sw = L.sweep_predictions(dd, N, R=reps, seed=int(rng.integers(1 << 30)))
    hrs, nbar = hours_and_n(S)
    steps_per_hour = real["T"] / max(hrs * (1 - 2 * edge), 1e-9)
    row = {"channel": ch, "N": N, "T": real["T"], "n_days": real["n_days"], "single": real["single"],
           "steps_per_hour": steps_per_hour, "nbar": nbar, "rms_Js": sw["rms_Js"], "rms_Ja": sw["rms_Ja"],
           "rms_Js_ci": jboot(dd, N, rng)}
    for lag in L.LAGS:
        f = np.array([x[f"x{lag}"] for x in fl])
        x = real[f"x{lag}"]
        row.update({f"x{lag}": x, f"x{lag}_se": real[f"x{lag}_se"], f"floor{lag}_q95": float(np.quantile(f, 0.95)),
                    f"floor{lag}_mean": float(f.mean()),
                    **{f"{nm}_x{lag}": sw[f"{nm}_x{lag}"] for nm in ("sweep", "rand", "full")},
                    **{f"{nm}_x{lag}_sd": sw[f"{nm}_x{lag}_sd"] for nm in ("sweep", "rand", "full")},
                    **{f"{nm}_x{lag}_q95": sw[f"{nm}_x{lag}_q95"] for nm in ("sweep", "rand", "full")}})
        above = (x > row[f"floor{lag}_q95"]) and (x > row[f"rand_x{lag}_q95"])
        row[f"above{lag}"] = bool(above)
        row[f"phi{lag}"] = float((row[f"sweep_x{lag}"] - row[f"rand_x{lag}"]) / x) if above else None
        row[f"x{lag}_per_agent_hour"] = x * steps_per_hour / nbar
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    ap.add_argument("--floor", type=int, default=30)
    ap.add_argument("--reps", type=int, default=20)
    args = ap.parse_args()
    U = pl.read_parquet(L.OUT / "units.parquet").filter(pl.col("n_days") >= 2)
    if args.units:
        U = U.filter(pl.col("unit").is_in(args.units.split(",")))
    rows = []
    t0 = time.time()
    for u in U.iter_rows(named=True):
        S = L.load_steps(u["unit"])
        rng = np.random.default_rng(abs(hash(u["unit"])) % (1 << 30))
        for ch in ("talk", "mode"):
            r = unit_channel(S, ch, args.floor, args.reps, rng)
            if r is None:
                continue
            r.update({"unit": u["unit"], "goal_no": u["goal_no"], "regime": u["regime"]})
            rows.append(r)
            print(u["unit"], ch, {k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()
                                  if k in ("N", "T", "x1", "x2", "x4", "floor2_q95", "sweep_x2", "rand_x2",
                                           "sweep_x4", "rand_x4", "full_x2", "above1", "above2", "above4", "rms_Js")},
                  f"{time.time() - t0:.0f}s", flush=True)
    out = L.OUT / "results"
    tag = "_" + args.units.replace(",", "_") if args.units else ""
    pl.DataFrame([{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()} for r in rows]) \
        .write_parquet(out / f"ep{tag}.parquet")
    (out / f"ep{tag}.json").write_text(json.dumps(rows, indent=1, default=float))
    if not args.units or "27" in args.units.split(","):
        S = L.load_steps("27")
        rng = np.random.default_rng(7)
        sens = {"no_edge_cut": unit_channel(S, "talk", 20, 12, rng, edge=0.0),
                "drop_first_day": unit_channel(S, "talk", 20, 12, rng, drop_first=True)}
        (out / "sens_G27.json").write_text(json.dumps(sens, indent=1, default=float))
        print("sens", {k: {kk: v[kk] for kk in ("x1", "x2", "x4", "above1", "above2", "above4")} for k, v in sens.items()})


if __name__ == "__main__":
    main()
