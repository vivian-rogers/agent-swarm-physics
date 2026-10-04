"""H42 native tests G51, NE14 and G19 from the unit table (NE41 has its own script, native_ne41.py).

Writes data/processed/H42-readout-hawkes-kernel/native_summary.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

import h42lib as L  # noqa: E402

FLOOR = 1e-3


def lg(x):
    return np.log(np.maximum(np.asarray(x, float), FLOOR))


def slope(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3:
        return np.nan
    return float(np.polyfit(x, y, 1)[0])


def main():
    df = pl.read_parquet(L.DATA / "units.parquet")
    out = {}
    # ---- G51
    g = df.filter(pl.col("goal_no") == 51).sort("unit_id")
    rows = g.select("unit_id", "n_days", "n_agents", "n_talk", "rec_per_msg", "B:B:nx", "A:A:nx", "pr:B:nx", "B:A_g:nx",
                    "B:B:shift_q95", "B:B:dayblock_max", "A:A:shift_q95",
                    (pl.col("B:B:cv") - pl.col("B:S0:cv")).alias("gainB"),
                    (pl.col("A:A:cv") - pl.col("A:S0:cv")).alias("gainA"),
                    (pl.col("B:B:cv") - pl.col("B:A_g:cv")).alias("dBAg"), "cv")
    xB, xA = lg(g["B:B:nx"]), lg(g["A:A:nx"])
    N = np.log(g["n_agents"].to_numpy().astype(float))
    pp = lg(g["B:B:nx"]) - np.log(np.maximum(g["rec_per_msg"].to_numpy(), 1))
    cvu = rows.filter(pl.col("cv") == True)  # noqa: E712
    out["G51"] = {"units": rows.to_dicts(),
                  "sd_log_B": float(np.std(xB)), "sd_log_A": float(np.std(xA)),
                  "cv_log_B": float(np.std(xB) / abs(np.mean(xB))), "cv_log_A": float(np.std(xA) / abs(np.mean(xA))),
                  "frac_floor_B": float(np.mean(g["B:B:nx"].to_numpy() <= FLOOR)),
                  "frac_floor_A": float(np.mean(g["A:A:nx"].to_numpy() <= FLOOR)),
                  "slope_perpair_B_vs_logN_nonzero": slope(N[g["B:B:nx"].to_numpy() > FLOOR], pp[g["B:B:nx"].to_numpy() > FLOOR]),
                  "slope_logn_B_vs_logN_nonzero": slope(N[g["B:B:nx"].to_numpy() > FLOOR], xB[g["B:B:nx"].to_numpy() > FLOOR]),
                  "spearman_nxB_N": float(spearmanr(g["n_agents"], g["B:B:nx"])[0]),
                  "spearman_nxA_N": float(spearmanr(g["n_agents"], g["A:A:nx"])[0]),
                  "spearman_perpairB_N": float(spearmanr(g["n_agents"], g["B:B:nx"].to_numpy() / g["rec_per_msg"].to_numpy())[0]),
                  "spearman_nxB_order": float(spearmanr(np.arange(len(g)), g["B:B:nx"])[0]),
                  "n_cv": len(cvu), "gainB_pos": int((cvu["gainB"].to_numpy() > 0).sum()),
                  "B_gt_both_nulls": int(((g["B:B:nx"] > g["B:B:shift_q95"]) &
                                          (g["B:B:nx"] > g["B:B:dayblock_max"].fill_null(np.inf))).sum())}
    # ---- NE14
    e = df.filter(pl.col("unit_id").is_in(["35", "36a", "36b", "36c", "37"])).sort("unit_id")
    side = np.where(np.isin(e["unit_id"].to_numpy(), ["35", "36a"]), "II", "III")
    e = e.with_columns(pl.Series("side", side))
    res = {}
    for c in ("B:B:nx", "A:A:nx", "pr:B:nx", "A:A_H03:nx", "B:A_g:nx"):
        m2 = float(np.median(e.filter(pl.col("side") == "II")[c].to_numpy()))
        m3 = float(np.median(e.filter(pl.col("side") == "III")[c].to_numpy()))
        res[c] = {"II": m2, "III": m3, "abs_dlog": float(abs(np.log(max(m3, FLOOR)) - np.log(max(m2, FLOOR))))}
    tau2 = np.nanmedian(e.filter(pl.col("side") == "II")["A:A:tau_A"].to_numpy()) if "A:A:tau_A" in e.columns else np.nan
    tau3 = np.nanmedian(e.filter(pl.col("side") == "III")["A:A:tau_A"].to_numpy()) if "A:A:tau_A" in e.columns else np.nan
    lag2 = float(np.median(e.filter(pl.col("side") == "II")["lag_mean"].to_numpy()))
    lag3 = float(np.median(e.filter(pl.col("side") == "III")["lag_mean"].to_numpy()))
    ecv = e.filter(pl.col("cv") == True)  # noqa: E712
    out["NE14"] = {"units": e.select("unit_id", "side", "n_days", "n_agents", "n_talk", "lag_med", "lag_mean", "B:B:nx",
                                     "A:A:nx", "pr:B:nx", "B:A_g:nx",
                                     *(["A:A:tau_A"] if "A:A:tau_A" in e.columns else []),
                                     (pl.col("B:B:cv") - pl.col("B:A_g:cv")).alias("dBAg"),
                                     (pl.col("B:B:cv") - pl.col("B:S0:cv")).alias("gainB")).to_dicts(),
                   "medians": res, "tauA_II": float(tau2) if tau2 == tau2 else None,
                   "tauA_III": float(tau3) if tau3 == tau3 else None, "lag_mean_II": lag2, "lag_mean_III": lag3,
                   "B_ge_Ag_cv": {r["unit_id"]: bool(r["B:B:cv"] >= r["B:A_g:cv"]) for r in ecv.iter_rows(named=True)}}
    # ---- G19
    h = df.filter(pl.col("goal_no") == 19).sort("unit_id")
    out["G19"] = {"units": h.select("unit_id", "n_days", "n_agents", "n_talk", "pr:B:nx", "pr:B:shift_q95",
                                    "pr:B:dayblock_max", "B:B:nx", "B:B:shift_q95", "B:B:dayblock_max", "B:A_g:nx",
                                    "A:A:nx", (pl.col("B:B:cv") - pl.col("B:S0:cv")).alias("gainB"),
                                    (pl.col("pr:B:cv") - pl.col("pr:A:cv")).alias("pr_dBA"), "cv").to_dicts()}
    (L.DATA / "native_summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "units"} for k, v in out.items()}, indent=1, default=float))
    for k in out:
        print(k)
        for r in out[k]["units"]:
            print("  ", {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in r.items()})


if __name__ == "__main__":
    main()
