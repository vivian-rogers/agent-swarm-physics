"""Write H79 round-1 per-period rows to the shared estimates table. Non-holdout only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H79-artifact-autocatalytic-set/results"
SRC = "data/processed/H79-artifact-autocatalytic-set/results/{}.json"


def main():
    rows = []
    for p, role in (("G51", "replication"), ("G31", "replication"), ("G38", "replication"), ("G41", "replication"),
                    ("G40", "native")):
        r = json.loads((D / f"{p}.json").read_text())
        g = int(p[1:])
        b = {"period_unit": p, "goal_no": g, "role": role, "post_hoc": False, "source": SRC.format(p),
             "channel": "artifact catalysis (executed repo -> write)"}
        W = float(r["real"]["work_commits"])
        rows += [
            {**b, "statistic": "raf_coverage_work_commits", "estimate": r["real"]["coverage"],
             "ci_lo": r["coverage_ci"][0], "ci_hi": r["coverage_ci"][1], "ci_kind": "percentile", "ci_level": 0.95,
             "n": W, "n_kind": "agent work commits", "method": "maxRAF (Hordijk-Steel, background reactants, A1); day bootstrap",
             "null": f"rewired cross-catalysis mean {r['null']['coverage_mean']:.3f}"},
            {**b, "statistic": "raf_self_share_all_identity", "estimate": r["real"]["self_share_of_raf_commits_all"],
             "ci_kind": "none", "n": W + r["real"]["auto_commits"], "n_kind": "agent-identity commits",
             "method": "share of maxRAF commits in self-catalysed reactions", "null": "none"},
            {**b, "statistic": "inperiod_tool_share_work", "estimate": r["real"]["inperiod_tool_share_work"],
             "ci_kind": "none", "n": W, "n_kind": "agent work commits",
             "method": "maxRAF events catalysed by a repo made in the period, other than the product",
             "null": f"rewired mean {r['null']['inperiod_mean']:.3f} (p {r['null']['p_inperiod']:.2f})"},
            {**b, "statistic": "support3_cycles_len_ge3", "estimate": float(r["n3_support3"]), "ci_kind": "none",
             "n": float(r["real"]["n_raf_reactions"]), "n_kind": "maxRAF reactions",
             "method": "simple catalytic cycles >= 3 among reactions with >= 3 events (A2)",
             "null": f"rewired mean {r['null']['n3_support3_mean']:.1f}; p_high {r['null']['p_n3_support3']:.2f}; "
                     f"p_low {r['null']['p_low_n3_support3']:.2f}"},
            {**b, "statistic": "time_arrow_exec_before_over_after", "estimate": r["time_arrow"]["ratio"],
             "ci_lo": r["time_arrow"]["ratio_ci"][0], "ci_hi": r["time_arrow"]["ratio_ci"][1], "ci_kind": "percentile",
             "ci_level": 0.95, "n": float(r["n_days"]), "n_kind": "days",
             "method": "catalysed commit share, executions before vs after the write", "null": "ratio 1"},
            {**b, "statistic": "caf_over_raf_commits", "estimate": r["real"]["caf_over_raf_commits"], "ci_kind": "none",
             "n": W + r["real"]["auto_commits"], "n_kind": "agent-identity commits",
             "method": "temporal maxCAF / maxRAF in commits", "null": "none"},
        ]
    nat = json.loads((D / "natives.json").read_text())["NE29"]
    for f in nat["followup"]:
        rows.append({"period_unit": f"G{f['goal_no']:02d}", "goal_no": f["goal_no"], "role": "native",
                     "unit_local": "NE29 follow-up", "statistic": "ne29_retiree_catalysed_share",
                     "channel": "artifact catalysis by a departed agent's repos", "estimate": f["share"], "ci_kind": "none",
                     "n": float(f["work_commits"]), "n_kind": "other agents' work commits after 2026-02-19",
                     "method": "events catalysed by repos first touched by Claude 3.7 Sonnet",
                     "null": "egregore-positive threshold 0.05", "post_hoc": False, "source": SRC.format("natives")})
    out = E.write_estimates(rows, hypothesis="H79")
    print(out.height, "rows")


if __name__ == "__main__":
    main()
