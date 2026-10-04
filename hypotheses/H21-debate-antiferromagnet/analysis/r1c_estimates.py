"""H21 round 1c: write per-period estimates (infra/shared/estimates.py) from r1c/r1c.json, tagged "round 1c, stance v2.1".

Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/r1c_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

R1C = ROOT / "data/processed/H21-debate-antiferromagnet/r1c"
SRC = "data/processed/H21-debate-antiferromagnet/r1c/r1c.json"
TAG = "round 1c, stance v2.1"
CH = "stance:v2.1 disagree_validated_agent"


def main():
    r = json.loads((R1C / "r1c.json").read_text())
    s = r["S1c"]
    base = {"period_unit": "12a", "goal_no": 12, "unit_local": "G12 debates", "first_day": "2025-09-01", "last_day": "2025-09-04",
            "source": SRC, "status": TAG}
    rows = [
        {**base, "role": "replication", "statistic": "flag_rate_opp_minus_same", "channel": CH, "estimate": s["delta_f"], "ci_kind": "none",
         "n": s["n_debates"], "n_kind": "debates",
         "method": "validated-disagreement flag rate, opposite minus same team, debate phase, equal weight per debate (v2 pairs, p_reply>=0.5)",
         "null": "label-confusion stress null (noise-aware agent-field logistic, FP rate scaled by correct+inform share); team re-partition",
         "notes": f"{TAG}; flags opp {s['flags_opp']}/{s['n_opp']}, same {s['flags_same']}/{s['n_same']}; p_stress={s['p_stress']}; p_team={s['p_team_perm']}; p_af={s['p_af']}"},
        {**base, "role": "replication", "statistic": "true_disagreement_rate_opposite_team", "channel": CH, "estimate": s["dhat_pop"]["true_rate_opp"],
         "ci_lo": s["dhat_pop"]["true_rate_opp_ci95"][0], "ci_hi": s["dhat_pop"]["true_rate_opp_ci95"][1], "ci_level": 0.95, "ci_kind": "percentile",
         "n": s["n_opp"], "n_kind": "replies",
         "method": "Rogan-Gladen corrected rate with validated precision ~0.64 and recall ~0.60 (noise draws x debate bootstrap)",
         "null": "none (estimate)", "notes": f"{TAG}; #12-specific noise gives {s['dhat_g12']['true_rate_opp']:.2f} {s['dhat_g12']['true_rate_opp_ci95']}"},
        {**base, "role": "replication", "statistic": "teams_recovered", "channel": CH, "estimate": float(r["S2c_flag"]["recovered"]), "ci_kind": "none",
         "n": r["S2c_flag"]["n_debates"], "n_kind": "debates", "method": "best two-block split of each debate's flag graph equals the drafted teams (ties share credit)",
         "null": "random split per debate (Monte Carlo)", "notes": f"{TAG}; expected {r['S2c_flag']['expected']:.2f}; p={r['S2c_flag']['p']}"},
        {**base, "role": "replication", "statistic": "flag_rate_opp_minus_same_post_verdict", "channel": CH, "estimate": r["S3c"]["delta_f_post"],
         "ci_kind": "none", "n": r["S3c"]["n"], "n_kind": "replies", "method": "flag contrast in the 10 min after the verdict",
         "null": "team re-partition; power if the debate-phase contrast persisted",
         "notes": f"{TAG}; 0 flags in {r['S3c']['n']} replies; power {r['S3c']['power_if_persisting']['power_model']:.2f}; P(0 flags | rates persist)={r['S3c']['power_if_persisting']['p_zero_flags_if_rates_persist']:.1e}"},
        {**base, "role": "native", "statistic": "within_pair_contrast", "channel": CH, "estimate": r["native_within_pair"]["mean_c"], "ci_kind": "none",
         "n": r["native_within_pair"]["n_pairs"], "n_kind": "pairs", "method": "same agent pair: flag rate as opponents minus as teammates (re-drafting)",
         "null": "sign flip over pairs; noise-aware agent-field null",
         "notes": f"{TAG}; positive {r['native_within_pair']['positive']}, negative {r['native_within_pair']['negative']}; p_signflip={r['native_within_pair']['p_signflip_upper']}"},
    ]
    c = r["controls"]
    for g, unit, first, last in ((33, "33", None, None), (26, "26", None, None)):
        x = c[f"g{g}"]
        rows.append({"period_unit": unit, "goal_no": g, "unit_local": unit, "source": SRC, "status": TAG, "role": "native",
                     "statistic": "true_disagreement_rate_agent_pairs", "channel": CH, "estimate": x["corrected"], "ci_lo": x["ci95"][0],
                     "ci_hi": x["ci95"][1], "ci_level": 0.95, "ci_kind": "percentile", "n": x["n"], "n_kind": "replies",
                     "method": "Rogan-Gladen corrected validated-disagreement rate over all agent-to-agent v2 replies (noise draws x day bootstrap)",
                     "null": "#12 opposite-team rate (difference interval)",
                     "notes": f"{TAG}; flags {x['n_flags']}; #12 opp minus this {x['diff_vs_g12_opp_ci95']}"})
    g = c["g33_camps"]
    rows.append({"period_unit": "33", "goal_no": 33, "unit_local": "33", "source": SRC, "status": TAG, "role": "native", "statistic": "camp_score",
                 "channel": CH, "estimate": g["camp_score"], "ci_kind": "none", "n": g["n_agents"], "n_kind": "agents",
                 "method": "satisfied weight of the best two-camp split of the double-centred flag graph (pairs >= 3 replies)",
                 "null": "noise-aware agent-field logistic", "notes": f"{TAG}; null q95 {g['null_q95']:.3f}; p={g['p']}"})
    w = E.write_estimates(rows, hypothesis="H21")
    print("estimates written:", w.height)


if __name__ == "__main__":
    main()
