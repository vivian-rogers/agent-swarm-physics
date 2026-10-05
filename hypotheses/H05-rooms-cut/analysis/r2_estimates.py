"""H05 round 2: rows for the shared per_period_estimates table (infra/shared/estimates.py: write_estimates).
Reads data/processed/H05-rooms-cut/r2/r2_results.json. Non-reserved data only.
Usage: uv run python hypotheses/H05-rooms-cut/analysis/r2_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H05-rooms-cut/r2"
SRC = str((D / "r2_results.json").relative_to(ROOT))
STATUS = "exploratory round 2 (2026-10-05)"


def main():
    r = json.loads((D / "r2_results.json").read_text())
    rows = []
    R1, R2, R3 = r["R1"], r["R2"], r["R3"]
    for g, v in R1["P1_windows"].items():
        if v["ratio_cross_within"] is None:
            continue
        rows.append({"period_unit": E.map_unit(int(g)) or f"G{int(g):02d}", "goal_no": int(g),
                     "statistic": "coedit_share_cross_over_within", "channel": "work commits", "estimate": v["ratio_cross_within"],
                     "ci_kind": "none", "n": v["n_within"] + v["n_cross"], "n_kind": "pair-days",
                     "method": "share of pair-days with a same-day co-edited repository (DQ4 agent work), cross-room / within-room (R2 R1-P1)",
                     "null": "none", "role": "replication", "source": SRC, "status": STATUS,
                     "notes": f"within {v['within_share']:.3f} cross {v['cross_share']:.3f}"})
    for side in ("cross", "within"):
        c = R1[f"P2_{side}"]
        rows.append({"period_unit": "local:multi-room-pooled", "goal_no": None, "statistic": f"commit_response_coedit_contrast_{side}",
                     "channel": "work commits", "estimate": c["diff"], "se": c["null_sd"], "ci_kind": "none", "n": c["n"],
                     "n_kind": "pair-days", "method": "stratified diff of E_x (30-min commit response minus cross-day surrogate), co-edit vs not, strata goal x activity tertile (R2 R1-P2; exception d)",
                     "null": f"co-edit label permutation within strata, one-sided p={c['p_perm_one_sided']:.3g}", "role": "native",
                     "source": SRC, "status": STATUS, "notes": f"{c['n_flag']} co-edit pair-days"})
    p3 = R1["P3_focus"]
    rows.append({"period_unit": "local:51g-focus", "goal_no": 51, "statistic": "focus_cut_arm_commit_coupling_did", "channel": "work commits",
                 "estimate": p3["E_x_DiD"], "ci_lo": p3["E_x_DiD_ci95"][0], "ci_hi": p3["E_x_DiD_ci95"][1], "ci_level": 0.95,
                 "ci_kind": "percentile", "n": p3["n_pairs"]["cut_pre"] + p3["n_pairs"]["cut_during"], "n_kind": "cut-arm pair-windows",
                 "method": "E_x DiD (during - pre #focus) cut arm vs stay pairs (R2 R1-P3)", "null": "pair bootstrap", "role": "native",
                 "source": SRC, "status": STATUS, "first_day": "2026-07-27", "last_day": "2026-08-21"})
    for mask in ("none", "trim"):
        k = R2[f"P1_kappa_{mask}"]
        rows.append({"period_unit": "local:III-pooled", "goal_no": None, "statistic": "room_size_dilution_beta_kappa", "channel": "talk",
                     "estimate": k["beta_hat"], "ci_lo": k["beta_ci95"][0], "ci_hi": k["beta_ci95"][1], "ci_level": 0.95, "ci_kind": "se_z",
                     "n": k["n"], "n_kind": "co-located pair-days",
                     "method": "beta = -b/kappa_bar, TWFE kappa_x on log(N_room-1), pair+day FE (R2 R2-P1; biased, see synthetic bands)"
                               + ("" if mask == "none" else " [trim]"),
                     "null": "synthetic bands beta0 [-0.43,0.24], beta0.45 [0.13,0.71]", "role": "native", "source": SRC, "status": STATUS})
    for key, lab, ph in (("P2_uptake_mention", "mention, pre-registered pooled", False), ("P2_uptake_reply", "reply parent, pooled", False),
                         ("P2_uptake_mention_two_room_era", "mention, two-room era #37-#44", True)):
        u = R2[key]
        rows.append({"period_unit": "local:III-pooled" if "era" not in key else "local:two-room-era", "goal_no": None,
                     "statistic": "room_size_dilution_beta_uptake", "channel": "talk (ledger pending sets)", "estimate": u["beta_u"],
                     "se": u["se"], "ci_lo": u["beta_ci95"][0], "ci_hi": u["beta_ci95"][1], "ci_level": 0.95, "ci_kind": "se_z",
                     "n": u["n"], "n_kind": "directed pair-days", "method": f"Poisson pair+day FE, per-sender uptake on log(N_room-1) ({lab}) (R2 R2-P2)",
                     "null": "z test", "role": "native", "source": SRC, "status": STATUS, "post_hoc": ph})
    n42 = R2["P3_NE42"]
    rows.append({"period_unit": "local:NE42", "goal_no": 40, "statistic": "ne42_merge_drop_beyond_dilution", "channel": "talk",
                 "estimate": n42["excess_merge_drop"], "se": n42["excess_merge_drop_se"], "ci_lo": n42["excess_merge_drop_ci95"][0],
                 "ci_hi": n42["excess_merge_drop_ci95"][1], "ci_level": 0.95, "ci_kind": "percentile", "n": n42["n_stay_pairs"],
                 "n_kind": "stay pairs", "method": "f_merge*kappa_x(#39) - kappa_x(#40), f from N_room^-0.45 (R2 R2-P3; not blind)",
                 "null": "pair bootstrap", "role": "native", "source": SRC, "status": STATUS, "first_day": "2026-05-04"})
    for ch in ("output", "search"):
        c = R3[f"P1_{ch}_cross"]
        if not c.get("n_exposures"):
            continue
        rows.append({"period_unit": "local:multi-room-pooled", "goal_no": None, "statistic": "leak_conductance_per_exposure",
                     "channel": f"cross-room {ch}", "estimate": c["excess"], "ci_lo": c["excess_ci95"][0], "ci_hi": c["excess_ci95"][1],
                     "ci_level": 0.95, "ci_kind": "percentile", "n": c["n_exposures"], "n_kind": "exposures",
                     "method": "P(adopt novel repo within 2 h of first exposure) - matched placebo-item rate, same agent and time (R2 R3-P1; exception d)",
                     "null": f"matched placebo items; lift {c['lift']}", "role": "native", "source": SRC, "status": STATUS})
    c = R3["chat_within"]
    rows.append({"period_unit": "local:multi-room-pooled", "goal_no": None, "statistic": "leak_conductance_per_exposure",
                 "channel": "within-room chat read (reference)", "estimate": c["excess"], "ci_lo": c["excess_ci95"][0], "ci_hi": c["excess_ci95"][1],
                 "ci_level": 0.95, "ci_kind": "percentile", "n": c["n_exposures"], "n_kind": "exposures",
                 "method": "same estimator, readers in the home room (R2 R3-P2 reference)", "null": "matched placebo items",
                 "role": "native", "source": SRC, "status": STATUS})
    E.write_estimates(rows, hypothesis="H05")
    print("wrote", len(rows), "rows")


if __name__ == "__main__":
    main()
