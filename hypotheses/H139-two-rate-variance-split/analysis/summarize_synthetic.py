"""Summarize the H139 synthetic runs: size, power, bias, A_min per unit, and the decision rules (i)-(iv).

    uv run python hypotheses/H139-two-rate-variance-split/analysis/summarize_synthetic.py
Output: data/processed/H139-two-rate-variance-split/synthetic/summary.json (+ printed tables)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import glob  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h139lib as L  # noqa: E402
from synthetic import GK0, J0, LADDER, OUT  # noqa: E402


def lo(col, k=0):
    return np.array([json.loads(x)[k] if x is not None else np.nan for x in col])


def amin(rates: dict[float, float], thr=0.8):
    """Smallest A with detection >= thr, log-interpolated between ladder rungs (nan if never reached)."""
    xs = sorted(rates)
    prev = None
    for a in xs:
        if rates[a] >= thr:
            if prev is None:
                return a
            a0, r0 = prev
            f = (thr - r0) / (rates[a] - r0) if rates[a] > r0 else 1.0
            return float(np.exp(np.log(a0) + f * (np.log(a) - np.log(a0))))
        prev = (a, rates[a])
    return np.nan


def main():
    df = pl.concat([pl.read_parquet(f) for f in sorted(glob.glob(str(OUT / "runs_*.parquet")))], how="diagonal_relaxed")
    out = {"units": {}, "params": {"J": J0, "g_k": GK0, "ladder": LADDER}}
    for unit in df["unit"].unique(maintain_order=True).to_list():
        d = df.filter(pl.col("unit") == unit)
        U = {"rbar": float(d["rbar"][0]), "A_pred": float(d.filter(pl.col("world") == "W1")["A_pred"][0]),
             "worlds": {}}
        for w in d["world"].unique(maintain_order=True).to_list():
            x = d.filter(pl.col("world") == w)
            ak = x["A_k"].to_numpy()
            c95lo, c95hi = lo(x["ci_A_k"], 0), lo(x["ci_A_k"], 1)
            c90lo = lo(x["ci90_A_k"], 0)
            A_true = float(x["A_true"][0])
            rf = x["R_fast"].to_numpy()
            r = {"n": x.height, "A_true": A_true, "A_emp_med": float(x["A_emp"].median()),
                 "A_k_med": float(np.nanmedian(ak)), "A_k_mean": float(np.nanmean(ak)),
                 "A_k_mc_se": float(np.nanstd(ak) / np.sqrt(np.isfinite(ak).sum())),
                 "se_A_k_med": float(x["se_A_k"].median()),
                 "det95": float(np.mean(c95lo > 0)), "det90": float(np.mean(c90lo > 0)),
                 "cover95": float(np.mean((c95lo <= A_true) & (A_true <= c95hi))),
                 "raw_A_k_med": float(np.nanmedian(x["raw_A_k"].to_numpy())),
                 "f_s_med": float(np.nanmedian(x["f_s"].to_numpy())),
                 "P3_pass_frac": float(np.mean(x["f_s"].to_numpy() >= 0.8)),
                 "two_beats_one": float(np.mean(x["two_beats_one"].fill_null(False).to_numpy())),
                 "R_fast_med": float(np.nanmedian(rf)), "R_fast_lt03": float(np.mean(rf < 0.3)),
                 "R_fast_gt07": float(np.mean(rf > 0.7)), "R_slow_med": float(np.nanmedian(x["R_slow"].to_numpy())),
                 "R_fast_n_med": float(x["R_fast_n"].median()),
                 "free_g_k_med": float(np.nanmedian(x["free_g_k"].to_numpy())) if "free_g_k" in x.columns else np.nan,
                 "g_s_med": float(np.nanmedian(x["g_s"].to_numpy()))}
            if A_true > 0:
                r["bias_ratio_med"] = float(np.nanmedian(ak) / A_true)
                r["bias_ratio_mean"] = float(np.nanmean(ak) / A_true)
                r["bias_ratio_mean_ci"] = [float((np.nanmean(ak) - 1.96 * r["A_k_mc_se"]) / A_true),
                                           float((np.nanmean(ak) + 1.96 * r["A_k_mc_se"]) / A_true)]
            U["worlds"][w] = r
        W = U["worlds"]
        lad95 = {a: W[f"L{a:g}"]["det95"] for a in LADDER if f"L{a:g}" in W}
        lad90 = {a: W[f"L{a:g}"]["det90"] for a in LADDER if f"L{a:g}" in W}
        U["A_min95"] = amin(lad95)
        U["A_min90"] = amin(lad90)
        U["A_min_over_Apred"] = U["A_min95"] / U["A_pred"]
        U["S1_fires"] = bool(U["A_min95"] > 2 * U["A_pred"]) if np.isfinite(U["A_min95"]) else True
        U["S1_fires_90"] = bool(U["A_min90"] > 2 * U["A_pred"]) if np.isfinite(U["A_min90"]) else True
        # J needed for A_pred = A_min / 2 at the unit's read rate and g_k 0.15
        U["J_star"] = float(np.sqrt(U["A_min95"] / (2 * U["rbar"] * L.kick_memory(GK0))))
        U["rule_iii_W0_false_pos"] = W["W0"]["det95"] if "W0" in W else np.nan
        if "W1x5" in W:
            U["S2_bias_x5"] = W["W1x5"]["bias_ratio_mean"] - 1
            U["S2_bias_x20"] = W["W1x20"]["bias_ratio_mean"] - 1
            U["S2_bias_x20_ci"] = [v - 1 for v in W["W1x20"]["bias_ratio_mean_ci"]]
        if "Wctx" in W:
            U["S3_sep"] = bool(W["Wctx"]["R_fast_lt03"] >= 0.8 and W["W1"]["R_fast_gt07"] >= 0.8)
            U["S3_ctx_lt03"], U["S3_W1_gt07"] = W["Wctx"]["R_fast_lt03"], W["W1"]["R_fast_gt07"]
        if "Lctx3" in W:
            U["S3big_ctx_lt03"], U["S3big_L3_gt07"] = W["Lctx3"]["R_fast_lt03"], W["L3"]["R_fast_gt07"]
        out["units"][unit] = U
        print(f"\n== {unit}: r_bar {U['rbar']:.3f} A_pred {U['A_pred']:.5f} A_min95 {U['A_min95']:.3f} "
              f"A_min90 {U['A_min90']:.3f} ratio {U['A_min_over_Apred']:.0f} S1 {U['S1_fires']} J* {U['J_star']:.3f}")
        for w, r in W.items():
            print(f"  {w:7s} n {r['n']:3d} A_true {r['A_true']:.4f} A_k med {r['A_k_med']:+.4f} (se {r['se_A_k_med']:.3f}) "
                  f"det95 {r['det95']:.2f} cov {r['cover95']:.2f} raw {r['raw_A_k_med']:+.3f} f_s {r['f_s_med']:.3f} "
                  f"2>1 {r['two_beats_one']:.2f} Rf {r['R_fast_med']:+.2f} (<.3 {r['R_fast_lt03']:.2f}, >.7 "
                  f"{r['R_fast_gt07']:.2f}) Rs {r['R_slow_med']:.2f} gkfree {r['free_g_k_med']:.3f}")
    us = out["units"]
    out["overall"] = {
        "S1_fires_units": [u for u in us if us[u]["S1_fires"]],
        "S1_fires_90_units": [u for u in us if us[u]["S1_fires_90"]],
        "A_min_over_Apred_range": [float(min(us[u]["A_min_over_Apred"] for u in us)),
                                   float(max(us[u]["A_min_over_Apred"] for u in us))],
        "W0_false_pos_max": float(max(us[u]["rule_iii_W0_false_pos"] for u in us)),
    }
    (OUT / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["overall"], indent=1))


if __name__ == "__main__":
    main()
