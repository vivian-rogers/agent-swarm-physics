"""Summarize the H43 synthetic validation (synthetic_results.json) into a table (JSON) and a figure.

Metrics per scale x variant x class (primary outcome: N -> O1, A/H -> O2 on busy recipients):
  size      share of null bins (>= 10 second kicks) whose 95% CI for R excludes 1
  recovery  delta_half (fit) vs the planted window; R_pool by spacing range; episode test (in vs act / post)
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/synthetic_summary.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h43lib as L  # noqa: E402

SYN = L.OUT / "synthetic"
TAU = 30.0


def truth_half(r_primer: float = 0.9) -> float:
    """delta at which a same-class habituation clock (tau = 30 min) reaches half the primer's recovery."""
    return TAU * math.log(1 / (1 - 0.5 * r_primer))


def main():
    d = json.loads((SYN / "synthetic_results.json").read_text())
    runs = d["runs"]
    table = {}
    for r in runs:
        for cl, s in r["summary"].items():
            key = f"{r['scale']}|{r['variant']}|{r['n_mode']}|{cl}"
            t = table.setdefault(key, {"n_reps": 0, "E1": [], "E1_pos": [], "bins": {}, "dh": [], "pool": {},
                                       "status": {}, "n_primers": [], "n_second": []})
            t["n_reps"] += 1
            t["E1"].append(s["E1"].get("est"))
            t["E1_pos"].append(bool(s["E1_positive"]))
            t["n_primers"].append(s["n_primers"])
            t["n_second"].append(s["n_second"])
            for b, (est, lo, hi, n) in s["R_bins"].items():
                if n is not None and n >= 10 and est is not None:
                    t["bins"].setdefault(b, []).append((est, lo, hi, n))
            if s.get("fit"):
                t["dh"].append((s["fit"]["delta_half"], s["fit"]["delta_half_lo"], s["fit"]["delta_half_hi"]))
            for b, v in (s.get("R_pool") or {}).items():
                if v[3] >= 10:
                    t["pool"].setdefault(b, []).append(v)
            for b, v in (s.get("by_status") or {}).items():
                if v[3] >= 10:
                    t["status"].setdefault(b, []).append(v)
    out = {}
    th = truth_half()
    for key, t in sorted(table.items()):
        sc, var, mode, cl = key.split("|")
        row = {"n_reps": t["n_reps"], "n_primers_mean": float(np.mean(t["n_primers"])),
               "n_second_mean": float(np.mean([x or 0 for x in t["n_second"]])),
               "E1_mean": float(np.nanmean([x for x in t["E1"] if x is not None])) if any(x is not None for x in t["E1"]) else None,
               "E1_positive_share": float(np.mean(t["E1_pos"]))}
        allb = [x for v in t["bins"].values() for x in v if x[1] is not None and x[2] is not None]
        if allb:
            excl = [not (lo <= 1 <= hi) for _, lo, hi, _ in allb]
            row["bins_ci_excludes_1_share"] = float(np.mean(excl))
            row["n_bin_estimates"] = len(allb)
        row["R_bins_median"] = {b: float(np.median([x[0] for x in v])) for b, v in sorted(t["bins"].items(), key=lambda kv: L.DELTA_LABELS.index(kv[0]))}
        row["R_pool_median"] = {b: float(np.median([x[0] for x in v])) for b, v in t["pool"].items()}
        row["R_pool_ci_excl_1_share"] = {b: float(np.mean([not (x[1] <= 1 <= x[2]) for x in v if x[1] is not None])) for b, v in t["pool"].items()}
        row["status_median"] = {b: float(np.median([x[0] for x in v])) for b, v in t["status"].items()}
        if t["dh"]:
            dh = np.array([x[0] for x in t["dh"]], float)
            row["delta_half_median"] = float(np.median(dh))
            row["delta_half_no_window_share"] = float(np.mean(dh <= 0))
            if var == "time_any":
                cov = [lo <= th <= hi for _, lo, hi in t["dh"] if lo is not None and hi is not None]
                row["delta_half_truth"] = th
                row["delta_half_covers_truth_share"] = float(np.mean(cov)) if cov else None
                row["delta_half_within_1p5_share"] = float(np.mean((dh >= th / 1.5) & (dh <= th * 1.5)))
        out[key] = row
    L.jdump({"truth_delta_half_time_any_min": th, "table": out, "params": d["params"]}, SYN / "synthetic_summary.json")
    for k, v in out.items():
        if "|policy|" not in k and "|replay|" not in k:
            continue
        print(k, {kk: (round(vv, 2) if isinstance(vv, float) else vv) for kk, vv in v.items()
                  if kk in ("n_primers_mean", "n_second_mean", "E1_mean", "E1_positive_share", "bins_ci_excludes_1_share",
                            "delta_half_median", "delta_half_no_window_share", "delta_half_covers_truth_share",
                            "delta_half_within_1p5_share")})
        print("     bins", {b: round(x, 2) for b, x in v["R_bins_median"].items()}, "pool", {b: round(x, 2) for b, x in v["R_pool_median"].items()},
              "status", {b: round(x, 2) for b, x in v["status_median"].items()})


if __name__ == "__main__":
    main()
