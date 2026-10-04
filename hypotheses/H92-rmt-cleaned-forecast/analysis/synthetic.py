"""H92 synthetic validation (axis F) at village counts, before any real-data forecast.

Units of 5 days, expanding training window, forecast of day t+1's realized matrix (and, for content, of the true
population matrix). Content: N in {4, 8, 16, 32}, W in {4, 8, 16}, fill 0.75, rho_w 0.3. Talk: L in {120, 240, 480}
kept minutes, rate 0.1, minute persistence 0.7. Structures:
  a  one uniform mode (market 0.4)
  b  uniform + two-room mode (0.4 / 0.4)
  c  many weak modes (market 0.2 + 6 random factors, loadings N(0, 0.15^2))
  d  structure b with drift: one random agent changes room every day
  s0 pure noise (edge size: share of fits where the calibrated edge keeps a spurious mode)
Output: data/processed/H92-rmt-cleaned-forecast/synthetic/{forecasts.parquet, summary.parquet}
Usage: uv run python hypotheses/H92-rmt-cleaned-forecast/analysis/synthetic.py [--units 16]
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import polars as pl

import h92lib as L

DM = L.DM
RHO_W, RHO_T, FILL = 0.3, 0.7, 0.75


def loads_for(struct, N, rng, day=0, rooms=None):
    if struct == "s0":
        return np.zeros((N, 0)), rooms
    if struct == "a":
        return np.full((N, 1), 0.4), rooms
    if struct in ("b", "d"):
        if rooms is None:
            rooms = np.arange(N) % 2
        if struct == "d" and day > 0:
            rooms = rooms.copy(); i = rng.integers(N); rooms[i] = 1 - rooms[i]
        return DM.room_loads(N, 0.4, 0.4, rooms), rooms
    if struct == "c":
        return np.hstack([np.full((N, 1), 0.2), rng.normal(0, 0.15, (N, 6))]), rooms
    raise ValueError(struct)


def run_unit(rng, channel, struct, N, size, n_days=5):
    rooms = None
    Lc = None
    days, mins, truths = [], [], []
    for t in range(n_days):
        if struct == "c":
            Lc = Lc if Lc is not None else loads_for("c", N, rng)[0]
            ld = Lc
        else:
            ld, rooms = loads_for(struct, N, rng, t, rooms)
        if channel == "content":
            Z = DM.synth_content_day(rng, N, size, ld, RHO_W, FILL)
            days.append(Z)
        else:
            S = DM.synth_spin_day(rng, N, size, ld if ld.shape[1] else np.zeros((N, 1)), rate=0.1, rho_t=RHO_T)
            days.append(DM.standardize(S)); mins.append(np.arange(size))
        truths.append(L.unitdiag(ld @ ld.T + np.eye(N)))
    out = []
    for j in range(1, n_days):
        tr = days[:j]
        if channel == "content":
            X = L.content_X(tr, None); edge = L.edge_content(tr, rng)
            Q = DM.overlap(days[j])
        else:
            X = L.spins_X(tr); edge = L.edge_spins(tr, mins[:j], rng)
            Q = DM.corr(days[j])
        est = L.all_estimates(X, edge)
        rec = {"channel": channel, "struct": struct, "N": N, "size": size, "n_train": j, **est["_meta"]}
        for k in L.EST:
            rec[f"mse_{k}"] = L.mse_off(est[k], Q)
            if channel == "content":
                rec[f"true_{k}"] = L.mse_off(est[k], truths[j])
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=int, default=16)
    a = ap.parse_args()
    rng = np.random.default_rng(L.SEED)
    out = L.OUT / "synthetic"; out.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for N in (4, 8, 16, 32):
        for W in (4, 8, 16):
            for st in ("s0", "a", "b", "c", "d"):
                for _ in range(a.units):
                    rows += run_unit(rng, "content", st, N, W)
        for Lm in (120, 240, 480):
            for st in ("s0", "a", "b"):
                for _ in range(a.units):
                    rows += run_unit(rng, "talk", st, N, Lm)
        print(f"N={N} done ({time.time() - t0:.0f}s)", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(out / "forecasts.parquet", compression="zstd")
    agg = [pl.len().alias("n"), (pl.col("k_cal") > 0).mean().alias("frac_kcal_pos"), pl.col("k_cal").mean().alias("k_cal"),
           pl.col("k_mp").mean().alias("k_mp")]
    for k in L.EST:
        agg.append((1 - pl.col("mse_E5_clip") / pl.col(f"mse_{k}")).mean().alias(f"r_{k}"))
        agg.append((pl.col(f"mse_{k}")).mean().alias(f"mse_{k}"))
    best = df.with_columns(pl.concat_list([pl.col(f"mse_{k}") for k in L.EST[1:]]).list.arg_min().alias("best_i"))
    best = best.with_columns(pl.col("best_i").replace_strict(dict(enumerate(L.EST[1:]))).alias("best"))
    sm = (best.group_by("channel", "struct", "N", "size").agg(*agg, pl.col("best").mode().first().alias("best_mode"),
                                                             (pl.col("best") == "E5_clip").mean().alias("frac_E5_best"))
          .sort("channel", "struct", "N", "size"))
    sm.write_parquet(out / "summary.parquet", compression="zstd")
    tr = (df.filter(pl.col("channel") == "content").group_by("struct", "N", "size")
          .agg(*[(1 - pl.col("true_E5_clip") / pl.col(f"true_{k}")).mean().alias(f"rt_{k}") for k in ("E2_raw", "E3_lwi", "E4_lwcc", "E1_mean")])
          .sort("struct", "N", "size"))
    tr.write_parquet(out / "summary_truth.parquet", compression="zstd")
    pl.Config.set_tbl_rows(200); pl.Config.set_tbl_cols(30); pl.Config.set_tbl_width_chars(250)
    print(sm.select("channel", "struct", "N", "size", "n", "frac_kcal_pos", "k_cal", "k_mp", "r_E2_raw", "r_E3_lwi", "r_E4_lwcc",
                    "r_E1_mean", "r_E6_clip_mp", "best_mode", "frac_E5_best"))
    print(tr)
    (out / "summary.json").write_text(json.dumps({"units_per_cell": a.units, "rho_w": RHO_W, "rho_t": RHO_T, "fill": FILL},
                                                 indent=1))
    print(f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
