"""H22 round 1c: per-unit rows for the shared per_period_estimates table (tag "round 1c, stance v2.1").

  uv run python hypotheses/H22-private-goals-spin-glass/analysis/r1c_rows.py
Reads data/processed/H22-private-goals-spin-glass/r1c/{stance,readflight_bge_small}.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

R1C = ROOT / "data/processed/H22-private-goals-spin-glass/r1c"
TAG = "round 1c, stance v2.1"
COUNTED = {"51b", "51c", "51d"}


def main():
    rows = []
    st = json.loads((R1C / "stance.json").read_text())
    src = "data/processed/H22-private-goals-spin-glass/r1c/stance.json"
    for u, r in st["units"].items():
        if not r.get("scorable"):
            continue
        base = {"period_unit": f"local:{u}", "unit_local": u, "goal_no": 51, "role": "replication", "source": src,
                "post_hoc": False, "n_kind": "replies", "null": "label-noise agent-field NG (R2000, pi/r drawn, differential FP)"}
        for k in ("SR", "OP", "K"):
            t, sd = r["T_D"].get(k), r["null_sd"].get(k)
            if t is None or sd is None:
                continue
            n = r["n_by_class"]["SR"] if k == "SR" else r["n_by_class"]["OP"] if k == "OP" else r["n_by_class"]["SR"] + r["n_by_class"]["OP"]
            rows.append({**base, "statistic": f"stance_v2_disagree_contrast_T_{k}", "channel": "stance_v2", "estimate": t,
                         "se": sd, "ci_lo": t - 1.96 * sd, "ci_hi": t + 1.96 * sd, "ci_kind": "se_z", "n": n,
                         "method": "H22.r1c two-way residual D contrast vs U",
                         "status": "descriptive" if (u not in COUNTED or (u == "51d" and k in ("SR", "K"))) else None,
                         "notes": f"{TAG}; NG p {r['p_NG'][k]:.3f}; corrected T* {r['T_corrected'][k]:.4f}; flags {r['flags_by_class']}"})
        b = r.get("balance_s2") or {}
        if b.get("tau3_dc") is not None:
            ci = b.get("tau3_dc_ci90") or [None, None]
            rows.append({**base, "statistic": "stance_v2_balance_tau3_dc", "channel": "stance_v2_soft", "estimate": b["tau3_dc"],
                         "ci_lo": ci[0], "ci_hi": ci[1], "ci_level": 0.90, "ci_kind": "percentile", "n": r["n_replies"],
                         "method": "H22.r1c tau3(dc) of J^s from s2_soft, three day folds", "null": "none",
                         "notes": f"{TAG}; round-1b DQ2 soft value in 1b rows"})
    g = st["G23v2"]
    rows.append({"period_unit": "G23", "goal_no": 23, "role": "native", "source": src, "post_hoc": False,
                 "statistic": "stance_v2_disagree_contrast_opponents", "channel": "stance_v2", "estimate": g["T_D"],
                 "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": g["n_opp_replies"], "n_kind": "opponent replies",
                 "method": "H22.r1c two-way residual D, chess opponents vs other pairs", "null": "node permutation + NG",
                 "notes": f"{TAG}; perm p {g['p_perm_greater']:.3f}; NG p {g['p_NG_greater']:.3f}"})
    for model in ("bge_small", "gte_modernbert"):
        rf_path = R1C / f"readflight_{model}.json"
        if not rf_path.exists():
            continue
        rf = json.loads(rf_path.read_text())
        for u, r in rf["units"].items():
            rows.append({"period_unit": f"local:{u}", "unit_local": u, "goal_no": 51, "role": "replication",
                         "source": f"data/processed/H22-private-goals-spin-glass/r1c/readflight_{model}.json", "post_hoc": False,
                         "statistic": "read_vs_inflight_Gamma_conflict_minus_other", "channel": f"content:{model}",
                         "estimate": r["Gamma"], "ci_lo": r["Gamma_ci"][0], "ci_hi": r["Gamma_ci"][1], "se": r["Gamma_se"],
                         "ci_kind": "percentile", "n": r["n_targets"], "n_kind": "target statements",
                         "method": "H22.r1c read-gated linear response by pair class (read_response nuisance)",
                         "null": "room x 1-h block bootstrap; placebo pair sets",
                         "notes": f"{TAG} (content arm); placebo pct {r['placebo_pct']:.3f}; read-minus-inflight conflict {r['read_minus_inflight_conf']:.4f}, other {r['read_minus_inflight_oth']:.4f}"})
    w = E.write_estimates(rows, hypothesis="H22")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
