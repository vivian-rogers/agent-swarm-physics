"""Summarise the H57 synthetic validation (axis F) and derive the per-period p-value calibration.

  uv run python hypotheses/H57-copy-under-backlog/analysis/synth_summary.py

Reads data/processed/H57-copy-under-backlog/synthetic/synth_*.parquet; writes synthetic/summary.json (mean slope,
rejection rate at 0.05 per skeleton x scenario x outcome) and synthetic/calibration.json (kappa = SD of the null z
over all constant-world seeds and skeletons, per outcome; per-period p-values use z / kappa).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
SY = ROOT / "data/processed/H57-copy-under-backlog/synthetic"
OUTCOMES = ["e_bge|agent", "e_gte|agent", "e_both|agent", "es_bge|agent", "er_bge|agent", "mkn_all|agent",
            "mkn_rare|agent", "mkr_all|agent", "near_bge_addr|agent", "near_gte_addr|agent", "near_bge_par|agent",
            "em_bge|agent", "mks_all|agent", "e_bge|day", "e_gte|day", "mkn_all|day", "e_bge|filt", "e_gte|filt",
            "er_bge|filt", "mkn_rare|filt", "pc_bge", "pt_bge", "pc_gte", "pt_gte",
            "el_bge|agent", "el_gte|agent", "elc_bge|agent", "elc_gte|agent", "elc_both|agent", "mkl_all|agent",
            "mklc_all|agent", "mklc_rare|agent", "elc_bge|filt", "elc_gte|filt", "mklc_rare|filt",
            "els_bge|agent", "els_gte|agent", "els_both|agent", "mkls_all|agent", "mkls_rare|agent"]


def main():
    d = pl.concat([pl.read_parquet(f) for f in sorted(SY.glob("synth_*.parquet"))], how="diagonal_relaxed")
    summ, calib = {}, {}
    for (sk, sc), g in d.group_by(["skeleton", "scenario"]):
        key = f"{sk}|{sc}"
        summ[key] = {"n_seeds": g.height, "true_copy_slope": float(g["true_copy|agent|b"].mean()),
                     "copy_rate": float(g["copy_rate"].mean())}
        for o in OUTCOMES:
            if f"{o}|b" not in g.columns:
                continue
            b, p = g[f"{o}|b"].to_numpy(), g[f"{o}|p"].to_numpy()
            summ[key][o] = {"mean_b": float(np.nanmean(b)), "sd_b": float(np.nanstd(b)),
                            "rej05": float(np.nanmean(p < 0.05))}
        for m in ("bge", "gte"):
            for K in (16, 32):
                T, Tp = g[f"T_{m}_K{K}"].to_numpy(), g[f"Tp_{m}_K{K}"].to_numpy()
                summ[key][f"T_{m}_K{K}"] = {"mean_T": float(np.nanmean(T)), "rej05": float(np.nanmean(Tp < 0.05))}
            if f"Tpar_{m}_K32" in g.columns:
                summ[key][f"Tpar_{m}_K32"] = {"mean_T": float(np.nanmean(g[f"Tpar_{m}_K32"].to_numpy())),
                                              "rej05": float(np.nanmean(g[f"Tparp_{m}_K32"].to_numpy() < 0.05))}
    null = d.filter((pl.col("scenario") == "const") & ~pl.col("skeleton").str.contains("conv"))
    nullc = d.filter((pl.col("scenario") == "const") & pl.col("skeleton").str.contains("conv"))
    for o in OUTCOMES:
        if f"{o}|b" not in null.columns:
            continue
        b, p = null[f"{o}|b"].to_numpy(), null[f"{o}|p"].to_numpy()
        ok = np.isfinite(b) & np.isfinite(p)
        z = np.sign(b[ok]) * stats.norm.isf(np.clip(p[ok], 1e-12, 1) / 2)
        calib[o] = {"kappa": float(max(1.0, np.sqrt(np.mean(z ** 2)))) if ok.sum() else 1.0, "n": int(ok.sum()),
                    "rej05_raw": float(np.mean(p[ok] < 0.05)) if ok.sum() else None,
                    "mean_z": float(z.mean()) if ok.sum() else None}
        if f"{o}|b" in nullc.columns and nullc.height:
            b2, p2 = nullc[f"{o}|b"].to_numpy(), nullc[f"{o}|p"].to_numpy()
            ok2 = np.isfinite(b2) & np.isfinite(p2)
            if ok2.sum():
                z2 = np.sign(b2[ok2]) * stats.norm.isf(np.clip(p2[ok2], 1e-12, 1) / 2)
                calib[o]["kappa_conv"] = float(max(1.0, np.sqrt(np.mean(z2 ** 2))))
                if not ok.sum():
                    calib[o]["kappa"] = calib[o]["kappa_conv"]
    (SY / "summary.json").write_text(json.dumps(summ, indent=1, sort_keys=True))
    (SY / "calibration.json").write_text(json.dumps(calib, indent=1, sort_keys=True))
    for o in ("e_bge|agent", "e_gte|agent", "e_both|agent", "mkn_all|agent", "near_bge_addr|agent", "er_bge|agent",
              "es_bge|agent", "em_bge|agent", "pc_bge", "pt_bge", "el_bge|agent", "elc_bge|agent", "elc_gte|agent",
              "elc_both|agent", "mklc_all|agent", "mklc_rare|agent", "els_bge|agent", "els_gte|agent",
              "mkls_all|agent"):
        line = [f"{o:22s} kappa {calib.get(o, {}).get('kappa', float('nan')):.2f}"]
        for sk in sorted({k.split('|')[0] for k in summ}):
            for sc in ("const", "load", "phase"):
                v = summ.get(f"{sk}|{sc}", {}).get(o)
                if v:
                    line.append(f"{sk}/{sc[:2]} {v['mean_b']:+.4f}({v['rej05']:.2f})")
        print("  ".join(line))
    for sk in sorted({k.split('|')[0] for k in summ}):
        for sc in ("const", "load", "phase"):
            v = summ.get(f"{sk}|{sc}")
            if v:
                print(sk, sc, "true", round(v["true_copy_slope"], 4), "T_bge_K32", v["T_bge_K32"], "T_gte_K32",
                      v["T_gte_K32"], "Tpar", v.get("Tpar_bge_K32"))


if __name__ == "__main__":
    main()
