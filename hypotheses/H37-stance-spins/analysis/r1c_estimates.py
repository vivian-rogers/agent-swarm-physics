"""H37 round 1c: write per-period estimates (infra/shared/estimates.py) from r1c/r1c.json, tagged "round 1c, stance v2.1".

Usage: uv run python hypotheses/H37-stance-spins/analysis/r1c_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "data/processed/H37-stance-spins/r1c/r1c.json"
TAG = "round 1c, stance v2.1"
CH = "stance:v2.1 disagree_validated_agent"


def main():
    r = json.loads((ROOT / SRC).read_text())
    rows = []
    g = r["G12"]
    b12 = {"period_unit": "12a", "goal_no": 12, "unit_local": "G12 debates", "first_day": "2025-09-01", "last_day": "2025-09-04",
           "source": SRC, "status": TAG, "role": "replication"}
    p1 = g["P1c"]
    rows.append({**b12, "statistic": "gamma_flag_opposite_minus_same", "channel": CH, "estimate": p1["gamma_f"], "ci_kind": "none",
                 "n": p1["n"], "n_kind": "replies",
                 "method": "two-way FE (speaker, target) linear probability of the validated-disagreement flag, opposite minus same team, debate phase",
                 "null": "label-confusion stress null (noise-aware agent-field logistic); team re-draw within debate",
                 "notes": f"{TAG}; flags opp {p1['by_rel']['opposite']['flags']}/{p1['by_rel']['opposite']['n']}, same {p1['by_rel']['same']['flags']}/{p1['by_rel']['same']['n']}; "
                          f"p_stress={p1['p_stress']}; p_team={p1['p_team_perm']}"})
    rows.append({**b12, "statistic": "auc_topic_same_vs_opposite", "channel": "topic:reply_pairs.cos (bge-small)", "estimate": g["P2c"]["auc_topic_adj_same_vs_opp"],
                 "ci_kind": "none", "n": p1["n"], "n_kind": "replies", "method": "AUC of agent-adjusted topic cosine for same vs opposite team, debate phase",
                 "null": "0.5", "notes": f"{TAG}; flag gamma with topic covariate {g['P2c']['gamma_f_topic_cov']:.3f}, stress p={g['P2c']['p_topic_cov_stress']}"})
    rows.append({**b12, "statistic": "camp_recovery_accuracy", "channel": CH, "estimate": g["P3c_flag"]["acc"], "ci_kind": "none", "n": 10, "n_kind": "debates",
                 "method": "ground state (true sizes) of each debate's agent-adjusted flag graph vs drafted teams, mean accuracy",
                 "null": "random balanced partitions", "notes": f"{TAG}; chance {g['P3c_flag']['chance']:.3f}; p={g['P3c_flag']['p']}; exact {g['P3c_flag']['exact']}/10"})
    if "P5c" in g:
        rows.append({**b12, "statistic": "gamma_flag_post_verdict", "channel": CH, "estimate": g["P5c"]["gamma_post"], "ci_kind": "none", "n": g["P5c"]["n"],
                     "n_kind": "replies", "method": "FE linear-probability flag contrast in the 10 min after the verdict", "null": "team re-draw",
                     "notes": f"{TAG}; flags {g['P5c']['flags']}"})
    if "G51" in r:
        x = r["G51"]
        b51 = {"period_unit": "51", "goal_no": 51, "unit_local": "51 non-holdout (07-06 to 09-04)", "first_day": "2026-07-06", "last_day": "2026-09-04",
               "source": SRC, "status": TAG, "role": "replication"}
        for c in ("SR", "OP", "SY", "NC"):
            lo, hi = x["beta_true_ci95"][c]
            rows.append({**b51, "statistic": f"role_class_disagreement_logodds_{c}", "channel": CH, "estimate": x["beta_true"][c], "ci_lo": lo, "ci_hi": hi,
                         "ci_level": 0.95, "ci_kind": "percentile", "n": x["n_unordered_pairs_by_class"][c], "n_kind": "pairs",
                         "method": "noise-aware agent-field logistic (precision ~0.64, recall ~0.60), class vs unrelated, same-lab covariate; day bootstrap x noise draws",
                         "null": "role permutation among role holders (FE linear probability)",
                         "notes": f"{TAG}; LP beta {x['beta_lp'][c]:.4f}; p_upper={x['p_upper_role_perm'][c]}; flags {x['class_flags'][c]}/{x['class_counts'][c]}"})
        rows.append({**b51, "statistic": "excess_disagreement_pairs", "channel": CH, "estimate": float(x["P9c"]["n_excess"]), "ci_kind": "none",
                     "n": x["P9c"]["n_tested_pairs"], "n_kind": "pairs", "method": ">=2 flags on >=2 days, Poisson p<0.01 under the noise-aware agent-field model",
                     "null": "noise-aware agent-field simulations", "notes": f"{TAG}; null mean {x['P9c']['n_excess_null_mean']:.2f}; conflict-class {x['P9c']['n_excess_conflict']}"})
    if "G26" in r and r["G26"].get("mantel_r") is not None:
        x = r["G26"]
        rows.append({"period_unit": "26", "goal_no": 26, "unit_local": "26", "source": SRC, "status": TAG, "role": "replication",
                     "statistic": "ballot_disagreement_mantel_r", "channel": CH, "estimate": x["mantel_r"], "ci_kind": "none", "n": x["n_pairs_ge2"], "n_kind": "pairs",
                     "method": "corr(pair flag rate, approval-ballot dissimilarity), pairs with >= 2 replies", "null": "voter permutation",
                     "notes": f"{TAG}; flags {x['n_flags']}; p_greater={x['p_greater']}"})
    if "G40" in r:
        x = r["G40"]
        rows.append({"period_unit": "40", "goal_no": 40, "unit_local": "40", "source": SRC, "status": TAG, "role": "replication",
                     "statistic": "true_disagreement_rate_agent_pairs", "channel": CH, "estimate": x["corrected"], "ci_lo": x["ci95"][0], "ci_hi": x["ci95"][1],
                     "ci_level": 0.95, "ci_kind": "percentile", "n": x["n"], "n_kind": "replies",
                     "method": "Rogan-Gladen corrected validated-disagreement rate (noise draws x day bootstrap)", "null": "half the #12 opposite-team rate",
                     "notes": f"{TAG}; flags {x['n_flags']}; ratio to #12 opp {x['ratio_to_g12_opp']:.3f} {x['ratio_ci95']}; excess pairs {x['n_excess_pairs']}"})
    w = E.write_estimates(rows, hypothesis="H37")
    print("estimates written:", w.height)


if __name__ == "__main__":
    main()
