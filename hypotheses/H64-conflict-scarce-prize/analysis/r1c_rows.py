"""H64 round 1c: per-period rows for the shared per_period_estimates table (tag "round 1c, stance v2.1").

  uv run python hypotheses/H64-conflict-scarce-prize/analysis/r1c_rows.py
D-scale natives: positive = more validated disagreement (run.py's estimators were fed -D; signs flipped back here).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import estimates as E  # noqa: E402
from estimates_rows import pu_id  # noqa: E402

R1C = ROOT / "data/processed/H64-conflict-scarce-prize/r1c"
TAG = "round 1c, stance v2.1"


def main():
    rows = []
    src = "data/processed/H64-conflict-scarce-prize/r1c/replication_units.json"
    for r in json.loads((R1C / "replication_units.json").read_text()):
        pid = pu_id(r["goal"], r["unit"])
        base = {"period_unit": pid, "goal_no": r["goal"], "role": "replication", "source": src, "post_hoc": False}
        rows.append({**base, "statistic": "disagree_validated_rate", "channel": "stance_v2", "estimate": r["d"][0],
                     "ci_lo": r["d"][1], "ci_hi": r["d"][2], "n": r["n"], "n_kind": "replies", "ci_kind": "percentile",
                     "method": "H64.r1c d_p disagree_validated_agent", "null": "none",
                     "notes": f"{TAG}; prize class {r['prize_class']}; day-cluster bootstrap; expected false-flag rate {r['fbar_p']:.4f}"})
        rows.append({**base, "statistic": "disagree_rate_confusion_corrected", "channel": "stance_v2", "estimate": r["d_corr"],
                     "ci_lo": None, "ci_hi": None, "n": r["n"], "n_kind": "replies", "ci_kind": "none",
                     "method": "H64.r1c d* = (d - fbar_p)/(r - fbar_p), pi 0.64 r 0.61", "null": "none",
                     "notes": f"{TAG}; corners of the precision/recall box {r['d_corr_hiFP']:.4f} / {r['d_corr_loFP']:.4f}"})
        rows.append({**base, "statistic": "disagreeing_pairs_excess", "channel": "stance_v2",
                     "estimate": r["n_neg_robust"] - r["null_mean_robust"], "ci_lo": None, "ci_hi": None,
                     "n": r["n_tested_robust"], "n_kind": "agent pairs tested", "ci_kind": "none",
                     "method": "H64.r1c cluster-robust BH 0.1 pair count, binary D", "null": "label-noise agent-field NG (R200)",
                     "notes": f"{TAG}; observed {r['n_neg_robust']} vs null mean {r['null_mean_robust']:.2f}; p {r['p_ng_robust']:.3f}"})
    nat = json.loads((R1C / "natives.json").read_text())
    for name, goal in (("G12", 12), ("G26", 26), ("G23", 23)):
        res = nat[name]["negD"]
        for k in ("g_open", "g_set", "delta"):
            lo, hi = res["ci"][k]
            rows.append({"period_unit": pu_id(goal, ""), "goal_no": goal, "role": "native",
                         "source": "data/processed/H64-conflict-scarce-prize/r1c/natives.json",
                         "statistic": f"prize_gated_{k}_disagree_v2", "channel": "stance_v2", "estimate": -res["est"][k],
                         "ci_lo": -hi if hi is not None else None, "ci_hi": -lo if lo is not None else None, "n": res["n"],
                         "n_kind": "replies", "method": "H64.r1c did on D (positive = disagreement)",
                         "null": "relation permutation", "ci_kind": "percentile", "post_hoc": False,
                         "notes": f"{TAG}; perm p g_open {res['p_open']:.4f}, delta {res['p_delta']:.4f}; rival open/settled {res['n_rival_open']}/{res['n_rival_set']}"})
    E.write_estimates(rows, hypothesis="H64")
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
