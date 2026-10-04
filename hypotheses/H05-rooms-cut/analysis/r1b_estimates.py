"""H05 round 1b: per-period estimates into the shared table (infra/shared/estimates.py: write_estimates).
Reads the r1b JSON outputs (explore_bin1, mf_blocks, r1b_reads; untrimmed and trimmed). Non-holdout only.
Usage: uv run python hypotheses/H05-rooms-cut/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H05-rooms-cut/r1b"
STATUS = "exploratory round 1b (activity_bins_fixed, ledger reads)"


def main():
    rows = []
    for mask, sub in (("none", D), ("trim", D / "trim")):
        ex = json.loads((sub / "explore_bin1.json").read_text())
        mf = json.loads((sub / "mf_blocks.json").read_text())
        tag = "" if mask == "none" else " [all-present-window trim before surrogates]"
        src_x, src_m = str((sub / "explore_bin1.json").relative_to(ROOT)), str((sub / "mf_blocks.json").relative_to(ROOT))
        for g, r in ex["X2"]["talk"].items():
            k = r["kappa_x"]
            rows.append({"period_unit": E.map_unit(int(g)) or f"G{int(g):02d}", "goal_no": int(g),
                         "statistic": "within_minus_cross_kappa_x", "channel": "talk", "estimate": k["diff"],
                         "ci_kind": "none", "n": r["n_within"] + r["n_cross"], "n_kind": "pairs",
                         "method": "pair-window excess lagged corr over cross-day surrogate, within - cross room" + tag,
                         "null": f"room-label permutation p={k['p_perm']:.3g}", "role": "replication", "source": src_x,
                         "status": STATUS, "notes": f"within {k['within']:.4f} cross {k['cross']:.4f}"})
        for spin in ("talk", "active"):
            for g, r in mf["MF1"][spin].items():
                lo, hi = r["loop_gain_ci95"]
                rows.append({"period_unit": E.map_unit(int(g)) or f"G{int(g):02d}", "goal_no": int(g),
                             "statistic": "mf_two_block_loop_gain", "channel": spin, "estimate": r["loop_gain"],
                             "ci_lo": lo, "ci_hi": hi, "ci_level": 0.95, "ci_kind": "percentile", "se": r["loop_gain_se_dayboot"],
                             "n": r["days"], "n_kind": "days", "method": "two-block naive mean field v*sum_j J_ij (H19 E4/E5)" + tag,
                             "null": "none", "role": "replication", "source": src_m, "status": STATUS})
                lo, hi = r["J_in_minus_out_ci95"]
                rows.append({"period_unit": E.map_unit(int(g)) or f"G{int(g):02d}", "goal_no": int(g),
                             "statistic": "mf_block_J_in_minus_out", "channel": spin, "estimate": r["J_in_minus_out"],
                             "ci_lo": lo, "ci_hi": hi, "ci_level": 0.95, "ci_kind": "percentile", "n": r["days"], "n_kind": "days",
                             "method": "two-block naive mean-field inversion of excess c0" + tag,
                             "null": f"room-label permutation p={r.get('p_perm_in_gt_out', float('nan')):.3g}",
                             "role": "replication", "source": src_m, "status": STATUS})
    rd = json.loads((D / "r1b_reads.json").read_text())
    src = str((D / "r1b_reads.json").relative_to(ROOT))
    for mask in ("none", "trim"):
        tag = "" if mask == "none" else " [trim]"
        n42 = rd[f"NE42_{mask}"]["talk"]
        for y in ("kappa_x", "reads"):
            q = n42[y]
            rows.append({"period_unit": "local:NE42", "goal_no": 41, "statistic": f"ne42_split_change_{y}", "channel": "talk",
                         "estimate": q["d_split_mean"], "ci_lo": q["d_split_ci95_pairboot"][0], "ci_hi": q["d_split_ci95_pairboot"][1],
                         "ci_level": 0.95, "ci_kind": "percentile", "n": n42["n_stay_pairs"], "n_kind": "stay pairs",
                         "method": "within-pair change #40 -> #41 for pairs together throughout (R1b-N3)" + tag, "null": "pair bootstrap",
                         "role": "native", "source": src, "status": STATUS, "first_day": "2026-05-11"})
        f = rd[f"focus_{mask}"]
        rows.append({"period_unit": "local:51g-focus", "goal_no": 51, "statistic": "focus_cut_arm_read_drop", "channel": "ledger reads",
                     "estimate": f["cut_arm_read_drop_frac"], "ci_kind": "none", "n": f["during"]["days"], "n_kind": "days",
                     "method": "share of pair-day reads lost by #focus x #general pairs (R1b-N2)" + tag, "null": "none",
                     "role": "native", "source": src, "status": STATUS})
        t = rd[f"HH248_{mask}"]["talk"]["all_III"]["kappa_x"]
        for mdl, key in (("M0_coloc", "coloc"), ("M1_coloc_plus_lreads", "coloc"), ("M1_coloc_plus_lreads", "lreads")):
            b = t[mdl][key]
            lo, hi = E.ci_from_se(b["beta"], b["se"])
            rows.append({"period_unit": "local:III-pooled", "goal_no": None, "statistic": f"hh248_{mdl}_{key}", "channel": "talk",
                         "estimate": b["beta"], "se": b["se"], "ci_lo": lo, "ci_hi": hi, "ci_level": 0.95, "ci_kind": "se_z",
                         "n": t["n"], "n_kind": "pair-days", "method": "TWFE pair + day FE, two-way clustered; kappa_x on co-location (+ log(1+ledger reads))" + tag,
                         "null": "z test", "role": "native", "source": src, "status": STATUS, "post_hoc": False})
    E.write_estimates(rows, hypothesis="H05")
    print("wrote", len(rows), "rows")


if __name__ == "__main__":
    main()
