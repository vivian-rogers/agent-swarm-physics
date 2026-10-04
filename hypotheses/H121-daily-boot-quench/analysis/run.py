"""H121 replication run on every eligible non-holdout unit (layer 1), plus per-day fits for the collapse test.

    uv run python hypotheses/H121-daily-boot-quench/analysis/run.py [--units 41,51c] [--boot 200]

Output: data/processed/H121-daily-boot-quench/results/units.parquet, days.parquet.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
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
RES = D / "results"
MIN_AGENTDAYS = 8
WALL_CAP_MIN = 240


def run_unit(args):
    u, B, data_dir = args
    df = pl.read_parquet(Path(data_dir) / "calls" / f"{u['unit_id']}.parquet")
    K = int(u["K_max"])
    g = float(u["g_lag"]) if u["g_lag"] is not None else 0.0
    gse = (float(u["g_lag_hi"]) - float(u["g_lag_lo"])) / 3.92 if u["g_lag_hi"] is not None else 0.0
    est = L.unit_estimate(df, K, g, gse, B=B, seed=1)
    row = {"unit_id": u["unit_id"], "goal_no": u["goal_no"], "regime": u["regime"], "K_max": K, "g_lag": g,
           "g_lag_se": gse, "g_src": u["g_src"], "N_mean": u["N_mean"], "n_agentdays": u["n_agentdays"],
           "n_days": u["n_days_elig"], "med_interval_s": u["med_interval_ss_s"],
           **{k: v for k, v in est.items() if not isinstance(v, (list, dict))}}
    if not est.get("ok"):
        return row, []
    row.update(L.one_exp_cv(df, K))
    row["m0_obs"] = float(df.filter(pl.col("k") == 0)["Y"].mean())
    row["m_ss_obs"] = float(df.filter(pl.col("ss"))["Y"].mean()) if df.filter(pl.col("ss")).height else np.nan
    # variants
    nk = df.filter(~pl.col("kickoff_day"))
    if nk["day"].n_unique() >= 1 and nk.select(pl.struct("agent", "day").n_unique()).item() >= MIN_AGENTDAYS:
        f = L.curve_fit_df(nk, K)
        row["tau_nokick"] = f["tau"] if f else np.nan
    row["K_unfloored"] = est["tau"] / (est["tau0_unfloored"] / (1 - min(max(g, -0.5), 0.99))) \
        if np.isfinite(est.get("tau0_unfloored", np.nan)) else np.nan
    mi = u["med_interval_ss_s"] or np.nan
    if np.isfinite(mi):
        wmax = float(min(WALL_CAP_MIN, K * mi / 60))
        fw = L.wall_fit(df, max(wmax, 20))
        row["tau_wall_min"] = fw["tau"] if fw else np.nan
        row["tau_pred_wall_min"] = est["tau_pred"] * mi / 60
        row["K_wall"] = row["tau_wall_min"] / row["tau_pred_wall_min"] if fw else np.nan
    # per-day fits (collapse)
    rng = np.random.default_rng(7)
    days = []
    for d in sorted(df["day"].unique().to_list()):
        dd = df.filter(pl.col("day") == d)
        if dd["agent"].n_unique() < 3:
            continue
        f = L.day_fit(dd, K, 100, rng)
        days.append({"unit_id": u["unit_id"], "goal_no": u["goal_no"], "regime": u["regime"], "day": d,
                     "pt_date": dd["pt_date"][0], "kickoff_day": bool(dd["kickoff_day"][0]), **f})
    lt = np.array([np.log(x["tau"]) if x.get("tau", 0) and x["tau"] > 0 else np.nan for x in days])
    se = np.array([(np.log(x["tau_hi"]) - np.log(x["tau_lo"])) / 3.92 if x.get("tau_lo", 0) and x["tau_lo"] > 0 else np.nan
                   for x in days])
    row["I2_days"] = L.i_squared(lt, se)
    res = np.array([bool(x.get("resolved")) for x in days], bool)
    if res.sum() >= 3:   # Amendment A1: DerSimonian-Laird between-day SD of ln tau_d over resolved days
        _, _, t2 = L.re_pool(lt[res], se[res])
        row["sd_between_days"] = float(np.sqrt(t2))
    else:
        row["sd_between_days"] = np.nan
    row["n_days_resolved"] = int(sum(1 for x in days if x.get("resolved")))
    return row, days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    ap.add_argument("--boot", type=int, default=200)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    meta = pl.read_parquet(D / "unit_meta.parquet").filter(pl.col("n_agentdays") >= MIN_AGENTDAYS)
    if a.units:
        meta = meta.filter(pl.col("unit_id").is_in(a.units.split(",")))
    rows, days = [], []
    with ProcessPoolExecutor(max_workers=2) as ex:
        for r, d in ex.map(run_unit, [(u, a.boot, str(D)) for u in meta.to_dicts()]):
            rows.append(r)
            days += d
            print(r["unit_id"], round(r.get("tau", float("nan")), 2), round(r.get("K", float("nan")), 2), flush=True)
    U = pl.DataFrame(rows, infer_schema_length=None)
    Dd = pl.DataFrame(days, infer_schema_length=None)
    if a.units and (RES / "units.parquet").exists():
        U = pl.concat([pl.read_parquet(RES / "units.parquet").filter(~pl.col("unit_id").is_in(U["unit_id"])), U],
                      how="diagonal_relaxed")
        Dd = pl.concat([pl.read_parquet(RES / "days.parquet").filter(~pl.col("unit_id").is_in(Dd["unit_id"])), Dd],
                       how="diagonal_relaxed")
    U.sort("goal_no", "unit_id").write_parquet(RES / "units.parquet")
    Dd.write_parquet(RES / "days.parquet")


if __name__ == "__main__":
    main()
