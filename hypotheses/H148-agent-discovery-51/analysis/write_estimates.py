"""H148 round 1: per-period estimates (#51 exploration span) into the shared table (infra/shared/estimates.py).

Role `native` (one period; no replication layer in round 1). Synthetic rows are not written.
Usage: uv run python hypotheses/H148-agent-discovery-51/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h148lib as L  # noqa: E402
import estimates as E  # noqa: E402

BASE = dict(period_unit="local:G51-explore", goal_no=51, first_day="2026-07-06", last_day="2026-09-04",
            role="native", source="data/processed/H148-agent-discovery-51/results")


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main():
    rows = []
    for level in ("agents", "elements"):
        f = L.OUT / "results" / f"{level}_w30.json"
        if not f.exists():
            continue
        R = json.loads(f.read_text())
        pr = R["predictions"]
        ch = f"30min {level} atoms"
        if level == "agents":
            for key, post, null in (("P1", False, "within-(day, E) permutation of the agent's source states"),
                                    ("P1_posthoc_crossday", True, "permutation within E cells across the half's days")):
                n = pr[key]["n_agents"]
                k = round(pr[key]["share"] * n)
                lo, hi = wilson(k, n)
                rows.append({**BASE, "statistic": "single_atom_individual_share_agents", "channel": ch,
                             "estimate": k / n, "ci_lo": lo, "ci_hi": hi, "n": n, "n_kind": "agents present >= 10 days",
                             "method": "held-out colonial A vs permutation (Besag-Clifford h 10, <= 300); p <= 0.025 on "
                                       "odd and even days" + (" [post hoc cross-day null]" if post else ""),
                             "null": null, "ci_level": 0.95, "ci_kind": "parametric", "post_hoc": post,
                             "notes": "Wilson interval"})
        n_multi = sum(1 for d in R["discovered"] if len(d["atoms"]) >= 2)
        rows.append({**BASE, "statistic": "n_discovered_multi_atom_individuals", "channel": ch, "estimate": float(n_multi),
                     "ci_lo": None, "ci_hi": None, "n": float(R["n_atoms"]), "n_kind": "atoms searched",
                     "method": "Krakauer boundary search, coupling tau vs day-permutation null, odd/even days, "
                               "both directions (A1, A2)", "null": "day-permutation of the candidate atom",
                     "ci_kind": "none", "post_hoc": False})
        p7 = pr["P7"]
        rows.append({**BASE, "statistic": "rotated_to_real_local_maxima_ratio", "channel": ch,
                     "estimate": float(p7["ratio_local_maxima"]), "ci_lo": None, "ci_hi": None,
                     "n": float(len(R["shuffle"])), "n_kind": "within-day rotations",
                     "method": "multi-atom local maxima of the search on within-day rotated atoms / on real data",
                     "null": "within-day rotation of every atom", "ci_kind": "none", "post_hoc": False})
        if "P5" in pr:
            rows.append({**BASE, "statistic": "n_discovered_field_systems", "channel": ch,
                         "estimate": float(pr["P5"]["n_field_systems"]), "ci_lo": None, "ci_hi": None,
                         "n": float(pr["P5"]["n_element_systems"]), "n_kind": "discovered element systems",
                         "method": "role-text (H145 role patterns) or operator-topic elements >= half of a system",
                         "null": "none (count)", "ci_kind": "none", "post_hoc": False})
    out = E.write_estimates(rows, hypothesis="H148")
    print("wrote", out.height, "rows")


if __name__ == "__main__":
    main()
