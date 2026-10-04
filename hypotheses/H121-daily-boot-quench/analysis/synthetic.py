"""H121 synthetic validation (axis F) on real call grids, before any real-data statistic.

Worlds (linear per-call update, h121lib.simulate_unit; every agent starts in the talking state):
  G0, G15, G30, G45: rho = 0.5, g = 0, 0.15, 0.30, 0.45 (Glauber / AR worlds; g = 0.6 dropped, see Amendment A1)
  F: rho = 0.5, g = 0.13, slow boot field F = 0.25 exp(-k/30)
  H: as F, but the field lifetime varies by day (log-uniform over x1/3 .. x3 around 30 calls)
Units: 27 (regime I), 41 and 51c (regime III). Output: data/processed/H121-daily-boot-quench/synthetic/.

    uv run python hypotheses/H121-daily-boot-quench/analysis/synthetic.py [--reps 12] [--boot 60]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h121lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H121-daily-boot-quench"
OUTD = D / "synthetic"
UNITS = ["27", "41", "51c"]
WORLDS = {"G0": dict(rho=0.5, g=0.0), "G15": dict(rho=0.5, g=0.15), "G30": dict(rho=0.5, g=0.30),
          "G45": dict(rho=0.5, g=0.45), "F": dict(rho=0.5, g=0.13, F_amp=0.25, F_tau=30.0),
          "H": dict(rho=0.5, g=0.13, F_amp=0.25, F_tau="het")}
KCAP = 700


def run_unit(args):
    unit, reps, B = args
    df = pl.read_parquet(D / "calls" / f"{unit}.parquet").filter(pl.col("k") <= KCAP)
    meta = pl.read_parquet(D / "unit_meta.parquet").filter(pl.col("unit_id") == unit).to_dicts()[0]
    K = int(meta["K_max"])
    rows, curves = [], {}
    for w, par in WORLDS.items():
        par = dict(par)
        acc = None
        for r in range(reps):
            rng = np.random.default_rng(hash((unit, w, r)) % (2 ** 32))
            if par.get("F_tau") == "het":
                days = df["day"].unique().to_list()
                ft = {d: float(30.0 * np.exp(rng.uniform(np.log(1 / 3), np.log(3)))) for d in days}
                p2 = {**par, "F_tau": ft}
            else:
                p2 = par
            sim = L.simulate_unit(df, rng, **p2)
            k, s, n = L.curve_arrays(sim, K)
            acc = (s, n) if acc is None else (acc[0] + s, acc[1] + n)
            est = L.unit_estimate(sim, K, g=par["g"], g_se=0.0, B=B, seed=r)
            cv = L.one_exp_cv(sim, K)
            # per-day collapse (F and H worlds only)
            share = np.nan
            if w in ("F", "H"):
                drng = np.random.default_rng(r)
                fits = [L.day_fit(sim.filter(pl.col("day") == d), K, 30, drng) for d in sorted(sim["day"].unique())]
                res = [f for f in fits if f.get("resolved")]
                if res and est.get("ok"):
                    share = float(np.mean([abs(np.log(f["tau"] / est["tau"])) <= np.log(2) for f in res]))
                n_res = len(res)
            else:
                n_res = 0
            rows.append({"unit": unit, "world": w, "rep": r, **{k2: v for k2, v in est.items() if not isinstance(v, (list, dict))},
                         "cv_gain": cv.get("cv_gain"), "collapse_share": share, "n_resolved_days": n_res,
                         "rho_true": par["rho"], "g_true": par["g"]})
        s, n = acc
        m = s / np.maximum(n, 1)
        ft = L.fit_exp1(np.arange(K + 1), m, n, K)
        curves[w] = {"tau_true_mc": ft["tau"] if ft else None, "m": m.tolist()}
        print(unit, w, "tau_mc", None if ft is None else round(ft["tau"], 2), flush=True)
    return rows, {unit: {w: c["tau_true_mc"] for w, c in curves.items()}}, {unit: {w: c["m"] for w, c in curves.items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=12)
    ap.add_argument("--boot", type=int, default=60)
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    rows, truth, curves = [], {}, {}
    with ProcessPoolExecutor(max_workers=2) as ex:
        for r, t, c in ex.map(run_unit, [(u, a.reps, a.boot) for u in UNITS]):
            rows += r
            truth.update(t)
            curves.update(c)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df = df.with_columns(pl.struct("unit", "world").map_elements(lambda s: truth[s["unit"]][s["world"]],
                                                                  return_dtype=pl.Float64).alias("tau_true"))
    df = df.with_columns((pl.col("tau") / pl.col("tau_true") - 1).alias("rel_err"),
                         ((pl.col("tau_lo") <= pl.col("tau_true")) & (pl.col("tau_hi") >= pl.col("tau_true"))).alias("cover"),
                         (pl.col("tau") / pl.col("tau_true")).alias("K_true"))
    df.write_parquet(OUTD / "reps.parquet")
    (OUTD / "curves.json").write_text(json.dumps(curves))
    summ = (df.group_by("unit", "world").agg(
        pl.col("tau_true").first(), pl.col("tau").median().alias("tau_med"), pl.col("rel_err").median().alias("rel_err_med"),
        pl.col("cover").mean().alias("coverage"), (pl.col("rho") - pl.col("rho_true")).median().alias("rho_bias"),
        (pl.col("rho") - pl.col("rho_true")).abs().max().alias("rho_maxabs"),
        pl.col("K_ar").median().alias("K_ar_med"), pl.col("K").median().alias("K_hh_med"),
        pl.col("K_ar").is_between(0.5, 2).mean().alias("K_ar_in_band"), pl.col("K").is_between(0.5, 2).mean().alias("K_hh_in_band"),
        (pl.col("K") > 2).mean().alias("K_hh_gt2"), (pl.col("K_ar") > 2).mean().alias("K_ar_gt2"),
        pl.col("K_true").is_between(0.5, 2).mean().alias("Ktrue_in_band"),
        pl.col("cv_gain").median().alias("cv_gain_med"), (pl.col("cv_gain") < 0.10).mean().alias("one_exp_pass"),
        (pl.col("collapse_share") >= 0.5).mean().alias("collapse_holds"), pl.col("n_resolved_days").median().alias("n_res_days"),
    ).sort("unit", "world"))
    summ.write_parquet(OUTD / "summary.parquet")
    pl.Config.set_tbl_rows(40); pl.Config.set_tbl_cols(30); pl.Config.set_tbl_width_chars(300)
    print(summ)
    (OUTD / "summary.json").write_text(json.dumps(summ.to_dicts(), indent=1, default=float))


if __name__ == "__main__":
    main()
