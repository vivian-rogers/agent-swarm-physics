"""H09 round 1b: per-period estimates into the shared table (write_estimates). Reads r1b JSON outputs only.
Usage: uv run python hypotheses/H09-swarm-thermodynamics/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H09-swarm-thermodynamics/r1b"
ST = "exploratory round 1b (activity_bins_fixed, context ledger)"


def main():
    rows = []
    e1 = json.loads((D / "explore_e1_e5.json").read_text())
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").select("pt_date", "goal_no")
    pdays = pl.DataFrame(e1["E1_per_day"]).join(cal, on="pt_date")
    src = str((D / "explore_e1_e5.json").relative_to(ROOT))
    for (g,), d in pdays.group_by("goal_no"):
        for col, tag in (("VR", ""), ("VR_trim", " [all-present-window trim]")):
            v = d[col].drop_nulls().to_numpy()
            if len(v) < 3:
                continue
            rows.append({"period_unit": E.map_unit(int(g)) or f"G{int(g):02d}", "goal_no": int(g), "statistic": "e1_activity_variance_ratio",
                         "channel": "activity", "estimate": float(np.median(v)), "ci_lo": float(np.percentile(v, 25)), "ci_hi": float(np.percentile(v, 75)),
                         "ci_level": 0.5, "ci_kind": "none", "n": len(v), "n_kind": "days",
                         "method": "median daily Var(K)/independent-agent variance with a 30-min field (IQR as interval)" + tag,
                         "null": "independent agents, 30-min field", "role": "replication", "source": src, "status": ST})
    gt = json.loads((D / "r1b_gate.json").read_text())
    src = str((D / "r1b_gate.json").relative_to(ROOT))
    for g, r in gt["G1_by_goal"].items():
        rows.append({"period_unit": E.map_unit(int(g)) or f"G{int(g):02d}", "goal_no": int(g), "statistic": "gate_mention_odds_ratio",
                     "channel": "ledger @-mention at post-pause call", "estimate": r["ment_or_mh_agent"], "ci_kind": "none", "n": r["n"],
                     "n_kind": "post-pause calls", "method": "MH OR of acting (vs re-pausing) at a timer gate, new @-mention vs not, agent strata",
                     "null": "none", "role": "replication", "source": src, "status": ST})
    n1 = gt["N1_NE43"]
    for step in ("step_a_bookends", "step_b_nudger"):
        q = n1[step]
        rows.append({"period_unit": "local:NE43", "goal_no": 51, "statistic": f"ne43_{step}_log_ratio_p_act_no_new", "channel": "timer gate",
                     "estimate": q["log_ratio_p_act_no_new"], "ci_lo": q["ci95_agent_boot"][0], "ci_hi": q["ci95_agent_boot"][1], "ci_level": 0.95,
                     "ci_kind": "percentile", "n": q["agents_matched"], "n_kind": "agents",
                     "method": "agent-matched log ratio of P(act | no new item) across the step", "null": "agent bootstrap",
                     "role": "native", "source": src, "status": ST})
    mm = json.loads((D / "r1b_memory.json").read_text())
    src = str((D / "r1b_memory.json").relative_to(ROOT))
    for g, r in mm["E8_by_goal"].items():
        rows.append({"period_unit": E.map_unit(int(g)) or f"G{int(g):02d}", "goal_no": int(g), "statistic": "e8_memory_elasticity_on_ledger_reads",
                     "channel": "memory", "estimate": r["E8a_elasticity_lnV_lnPread"], "ci_kind": "none", "n": r["n_snapshots"],
                     "n_kind": "snapshots", "method": "within agent x goal slope of ln V on ln(1 + ledger reads since last snapshot)",
                     "null": "none", "role": "replication", "source": src, "status": ST})
        rows.append({"period_unit": E.map_unit(int(g)) or f"G{int(g):02d}", "goal_no": int(g), "statistic": "e8_memory_relaxation_gamma",
                     "channel": "memory", "estimate": -r["E8c_dV_on_Vprev_minus_gamma"], "ci_kind": "none", "n": r["n_snapshots"],
                     "n_kind": "snapshots", "method": "dV = beta P_read - gamma V_prev, within agent x goal", "null": "none",
                     "role": "replication", "source": src, "status": ST})
    n2 = mm["N2_roster_sweep_51"]
    for k, ci in (("elasticity_V_on_reads_per_call", "ci95"), ("elasticity_V_on_N", "ci95_N")):
        rows.append({"period_unit": "G51", "goal_no": 51, "statistic": f"n2_{k}", "channel": "memory", "estimate": n2[k],
                     "ci_lo": n2[ci][0], "ci_hi": n2[ci][1], "ci_level": 0.95, "ci_kind": "percentile", "n": n2["agent_weeks"],
                     "n_kind": "agent-weeks", "method": "within-agent slope of ln weekly median memory size (#51 roster sweep)",
                     "null": "agent-cluster bootstrap", "role": "native", "source": src, "status": ST})
    E.write_estimates(rows, hypothesis="H09")
    print("wrote", len(rows))


if __name__ == "__main__":
    main()
