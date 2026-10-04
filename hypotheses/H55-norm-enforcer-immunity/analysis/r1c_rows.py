"""H55 round 1c: per-period rows for the shared per_period_estimates table (tag "round 1c, stance v2.1").

  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/r1c_rows.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402
import polars as pl  # noqa: E402

R1C = ROOT / "data/processed/H55-norm-enforcer-immunity/r1c"
TAG = "round 1c, stance v2.1"


def pu_id(goal: int) -> str:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").filter(pl.col("goal_no") == goal)
    return pu["unit_id"][0] if pu.height == 1 else f"G{goal:02d}"


def main():
    rows = []
    src = "data/processed/H55-norm-enforcer-immunity/r1c/real_periods.json"
    for r in json.loads((R1C / "real_periods.json").read_text()):
        g = r["goal_no"]
        base = {"period_unit": pu_id(g), "goal_no": g, "role": "replication", "source": src, "post_hoc": False}
        p1 = r["P1"]
        if p1.get("scorable"):
            rows.append({**base, "statistic": "friction_rho_Cv2_nuD", "channel": "stance_v2", "estimate": p1["rho"],
                         "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": p1["n_agents"], "n_kind": "agents",
                         "method": "H55.r1c Spearman(c_j C_v2 rate, received-D target field)", "null": "agent permutation (5000)",
                         "notes": f"{TAG}; p greater {p1['p_greater']:.3f}, less {p1['p_less']:.3f}; partial {p1['rho_partial']:.3f}"})
        p2 = r["P2"]
        if p2.get("scorable"):
            rows.append({**base, "statistic": "friction_gamma_D_replies_to_Cv2", "channel": "stance_v2", "estimate": p2["gamma"],
                         "ci_lo": p2["lo"], "ci_hi": p2["hi"], "ci_kind": "percentile", "se": p2["se"], "n": p2["n_treated"],
                         "n_kind": "replies to C_v2 messages", "method": "H55.r1c within speaker+target D contrast",
                         "null": "label-noise agent-field NG (R500)",
                         "notes": f"{TAG}; NG p greater {p2.get('p_NG_greater', float('nan')):.3f}; corrected {p2.get('gamma_corrected', float('nan')):.4f}; bootstrap CI descriptive (A1c)"})
    E.write_estimates(rows, hypothesis="H55")
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
