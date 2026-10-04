"""Write H64 per-period rows to the shared per_period_estimates table (write_estimates).

    uv run python hypotheses/H64-conflict-scarce-prize/analysis/estimates_rows.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H64-conflict-scarce-prize"


def pu_id(goal: int, unit: str) -> str:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").filter(pl.col("goal_no") == goal)
    if unit and not unit.isdigit():
        return unit
    return str(goal) if pu.height == 1 else f"G{goal:02d}"


def main():
    rows = []
    src = "data/processed/H64-conflict-scarce-prize/replication/units.json"
    for r in json.loads((DATA / "replication/units.json").read_text()):
        pid = pu_id(r["goal"], r["unit"])
        base = {"period_unit": pid, "goal_no": r["goal"], "role": "replication", "source": src, "post_hoc": False}
        rows.append({**base, "statistic": "position_opposition_rate", "channel": "stance", "estimate": r["r_pos"][0],
                     "ci_lo": r["r_pos"][1], "ci_hi": r["r_pos"][2], "n": r["n"], "n_kind": "replies",
                     "method": "H64.r_p_dq2_conf08_position", "null": "none", "ci_kind": "percentile",
                     "notes": f"prize class {r['prize_class']}; day-cluster bootstrap"})
        rows.append({**base, "statistic": "confident_opposes_rate", "channel": "stance", "estimate": r["r_opp"][0],
                     "ci_lo": r["r_opp"][1], "ci_hi": r["r_opp"][2], "n": r["n"], "n_kind": "replies",
                     "method": "H64.r_opp_dq2_conf08", "null": "none", "ci_kind": "percentile"})
        rows.append({**base, "statistic": "antagonism_excess_pairs", "channel": "stance", "estimate": r["E_robust"],
                     "ci_lo": None, "ci_hi": None, "n": r["n_tested_robust"], "n_kind": "agent pairs tested",
                     "method": "H64.E_cluster_robust_bh01", "null": "agent_field_ordered_logit_R200",
                     "ci_kind": "none", "notes": f"observed {r['n_neg_robust']} vs null mean {r['null_mean_robust']:.2f}; p_AF {r['p_af_robust']:.3f}"})
        rows.append({**base, "statistic": "mean_soft_stance", "channel": "stance", "estimate": r["sbar"][0],
                     "ci_lo": r["sbar"][1], "ci_hi": r["sbar"][2], "n": r["n"], "n_kind": "replies",
                     "method": "H64.sbar", "null": "none", "ci_kind": "percentile"})
    for name, goal in (("G12", 12), ("G26", 26), ("G23", 23)):
        nat = json.loads((DATA / f"natives/{name}.json").read_text())
        for oc, res in (("soft", nat["soft"]), ("hard", nat["hard"])):
            for k in ("g_open", "g_set", "delta"):
                rows.append({"period_unit": pu_id(goal, ""), "goal_no": goal, "role": "native",
                             "source": f"data/processed/H64-conflict-scarce-prize/natives/{name}.json",
                             "statistic": f"prize_gated_{k}", "channel": "stance", "estimate": res["est"][k],
                             "ci_lo": res["ci"][k][0], "ci_hi": res["ci"][k][1], "n": res["n"], "n_kind": "replies",
                             "method": f"H64.did_{oc}", "null": "relation_permutation", "ci_kind": "percentile",
                             "post_hoc": False,
                             "notes": f"perm p g_open {res['p_open']:.4f}, delta {res['p_delta']:.4f}; rival open/settled {res['n_rival_open']}/{res['n_rival_set']}"})
    E.write_estimates(rows, hypothesis="H64")
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
