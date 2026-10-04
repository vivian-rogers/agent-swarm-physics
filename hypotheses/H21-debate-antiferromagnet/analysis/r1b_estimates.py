"""H21 round 1b: write per-period estimates (infra/shared/estimates.py) from r1b/r1b.json.

Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

R1B = ROOT / "data/processed/H21-debate-antiferromagnet/r1b"
SRC = "data/processed/H21-debate-antiferromagnet/r1b/r1b.json"


def main():
    r = json.loads((R1B / "r1b.json").read_text())
    rows = []
    base12 = {"period_unit": "12a", "goal_no": 12, "unit_local": "G12 debates", "first_day": "2025-09-01", "last_day": "2025-09-04",
              "source": SRC, "status": "round 1b"}
    for name, c in r.get("content", {}).items():
        lo, hi = (c.get("delta_ci") or [None, None])[:2]
        rows.append({**base12, "role": "replication", "statistic": "staggered_order_delta", "channel": f"content:{name}",
                     "estimate": c["delta"], "ci_lo": lo, "ci_hi": hi, "ci_kind": "percentile", "n": 10, "n_kind": "debates",
                     "method": "within- minus cross-team cosine of agent- and debate-centred spins, equal weight per debate",
                     "null": "team re-partition within debate", "notes": f"p={c['p_delta']}; recovered={c['recovered']}/10"})
        if c.get("text_axis_sigma") is not None:
            rows.append({**base12, "role": "replication", "statistic": "text_axis_staggered_moment", "channel": f"content:{name}",
                         "estimate": c["text_axis_sigma"], "ci_kind": "none", "n": 10, "n_kind": "debates",
                         "method": "LOAO-free staggered projection on the motion's pro-minus-con template axis",
                         "null": "team re-partition", "notes": f"p={c['text_axis_p']}"})
    s = r["stance"]
    rows.append({**base12, "role": "replication", "statistic": "staggered_order_delta", "channel": "stance:dq2",
                 "estimate": s["S1_delta_soft"]["delta"], "ci_kind": "none", "n": s["S1_delta_soft"]["n_debates"], "n_kind": "debates",
                 "method": "mean soft stance teammates minus opponents (DQ2 replies in debate phases), equal weight per debate",
                 "null": "team re-partition; calibrated agent-field ordered logit (hard labels)",
                 "notes": f"p_team={s['S1_delta_soft']['p_team_perm']}; hard p_agent_field={s['S1_delta_hard']['p_agent_field']}"})
    rows.append({**base12, "role": "replication", "statistic": "teams_recovered", "channel": "stance:dq2",
                 "estimate": float(s["S2_recovery"]["recovered"]), "ci_kind": "none", "n": s["S2_recovery"]["n_debates"], "n_kind": "debates",
                 "method": "ground-state two-block split of each debate's stance graph equals the drafted teams",
                 "null": "Poisson-binomial chance", "notes": f"expected={s['S2_recovery']['expected']:.2f}; p={s['S2_recovery']['p']}"})
    if s["S3_post"].get("delta_post") is not None:
        rows.append({**base12, "role": "replication", "statistic": "staggered_order_delta_post_verdict", "channel": "stance:dq2",
                     "estimate": s["S3_post"]["delta_post"], "ci_kind": "none", "n": s["S3_post"]["n_debates"], "n_kind": "debates",
                     "method": "soft-stance teammates minus opponents in the 10 min after the verdict", "null": "none (descriptive)"})
    n = r["native_G12"]
    rows.append({**base12, "role": "native", "statistic": "within_pair_contrast", "channel": "stance:dq2",
                 "estimate": n["stance_soft"]["mean_c"], "ci_kind": "none", "n": n["stance_soft"]["n_pairs"], "n_kind": "pairs",
                 "method": "same agent pair: mean soft stance as opponents minus as teammates (re-drafting)",
                 "null": "sign flip over pairs; calibrated agent-field null (hard labels)",
                 "notes": f"p_signflip={n['stance_soft']['p_signflip_lower']}; hard p_agent_field={n['stance_hard']['p_agent_field_lower']}"})
    for m in ("bge_small", "gte_modernbert"):
        c = n[f"content_{m}"]
        rows.append({**base12, "role": "native", "statistic": "within_pair_contrast", "channel": f"content:{m}",
                     "estimate": c["mean_c"], "ci_kind": "none", "n": c["n_pairs"], "n_kind": "pairs",
                     "method": "same agent pair: mean spin cosine as opponents minus as teammates", "null": "sign flip over pairs",
                     "notes": f"p_two_sided={c['p_signflip_two_sided']}"})
    g26 = r["native_G26"]["contest"]
    b26 = {"period_unit": "26", "goal_no": 26, "unit_local": "26 contest (01-05 to result)", "source": SRC, "status": "round 1b", "role": "native"}
    if g26["stance_mantel"].get("r") is not None:
        rows.append({**b26, "statistic": "ballot_camp_mantel_r", "channel": "stance:dq2", "estimate": g26["stance_mantel"]["r"],
                     "ci_kind": "none", "n": g26["stance_mantel"]["n_pairs"], "n_kind": "pairs",
                     "method": "corr(residual pair stance, -ballot dissimilarity)", "null": "voter-label permutation",
                     "notes": f"p_greater={g26['stance_mantel'].get('p_greater')}"})
    for m in ("bge_small", "gte_modernbert"):
        c = g26[f"content_mantel_{m}"]
        if c.get("r") is not None:
            rows.append({**b26, "statistic": "ballot_camp_mantel_r", "channel": f"content:{m}", "estimate": c["r"], "ci_kind": "none",
                         "n": c["n_pairs"], "n_kind": "pairs", "method": "corr(pair content cosine, -ballot dissimilarity)",
                         "null": "voter-label permutation", "notes": f"p_greater={c.get('p_greater')}"})
    g33 = r["native_G33"]
    rows.append({"period_unit": "33", "goal_no": 33, "unit_local": "33", "source": SRC, "status": "round 1b", "role": "native",
                 "statistic": "camp_score", "channel": "stance:dq2", "estimate": g33["camp_score_hard"], "ci_kind": "none",
                 "n": g33["n_pairs_J"], "n_kind": "pairs", "method": "satisfied |J| weight of the best two-camp split (double-centred)",
                 "null": "calibrated agent-field ordered logit", "notes": f"null mean={g33['camp_null_mean']:.3f}; p={g33['p_camp_agent_field']}"})
    w = E.write_estimates(rows, hypothesis="H21")
    print("estimates written:", w.height)


if __name__ == "__main__":
    main()
