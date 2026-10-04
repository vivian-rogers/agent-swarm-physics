"""H96 rows for the shared per-period estimates table (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H96-goal-switch-hysteresis"
SRC = "data/processed/H96-goal-switch-hysteresis/"


def v(x):
    return None if (x is None or not np.isfinite(x)) else float(x)


def rows() -> list[dict]:
    out = []
    for model in ("bge_small", "gte_modernbert"):
        tr = json.loads((DATA / f"results/transitions_{model}_style_resid32.json").read_text())
        for o in tr:
            P = o["P"]; s = o["state"]
            base = {"period_unit": E.map_unit(P), "goal_no": P, "unit_local": f"G{P:02d}", "role": "replication",
                    "channel": "content", "ci_level": 0.95, "ci_kind": "percentile", "n": s["n_agents"],
                    "n_kind": "agents (post-switch)", "source": SRC + f"results/transitions_{model}_style_resid32.json",
                    "first_day": None}
            m = f"{model} style_resid32; leave-agent-out old state, new field projected out, minus median placebo old state; agent bootstrap"
            for stat, key, null in (("old_state_remanence_pre", "M_pre", "0 (median placebo old state)"),
                                    ("old_state_remanence_day1", "M_1", "0 (median placebo old state)"),
                                    ("old_state_persistence_R1", "R1", f"pseudo-switch median {o['R1_pseudo_median']:.2f}"),
                                    ("old_state_inertia_tau_active_h", "tau", "quench (< 0.5 h)"),
                                    ("switch_time_tau_sw_active_h", "tau_sw", "none (A1 estimator)")):
                d = s[key]
                out.append({**base, "statistic": stat, "estimate": v(d["est"]), "ci_lo": v(d["lo"]), "ci_hi": v(d["hi"]),
                            "method": m + f" [{model}]", "null": null, "post_hoc": key == "tau_sw",
                            "notes": f"transition #{o['Pm1']}->#{P}; q={s['q']:.3f}; verdict {o['verdict']}"})
            out.append({**base, "statistic": "old_state_order_q", "estimate": v(s["q"]), "ci_lo": None, "ci_hi": None,
                        "ci_kind": "none", "method": f"mean cross-agent cosine of agent-day vectors on the old-state days [{model}]",
                        "null": "none", "notes": f"transition #{o['Pm1']}->#{P}"})
        nat = json.loads((DATA / f"natives/natives_{model}.json").read_text())
        g = nat["G39"]["groups"]["all"]
        out.append({"period_unit": E.map_unit(39), "goal_no": 39, "unit_local": "G39", "role": "native",
                    "channel": "content", "statistic": "room_domain_memory_day1", "estimate": v(g["Delta_1"]),
                    "ci_lo": v(g["lo"][1]), "ci_hi": v(g["hi"][1]), "ci_level": 0.95, "ci_kind": "percentile",
                    "n": g["n"], "n_kind": "veteran agents", "method": f"own-room minus other-room #38 old state, #39 field projected out [{model}]",
                    "null": "0", "source": SRC + f"natives/natives_{model}.json",
                    "notes": f"pre {g['Delta_pre']}; verdict {nat['G39']['verdict']}"})
        a = nat["NE38"]["agent40"]
        out.append({"period_unit": "local:NE38", "goal_no": 51, "unit_local": "NE38", "role": "native",
                    "channel": "content", "statistic": "single_agent_switch_R1", "estimate": v(a["R1"]),
                    "ci_lo": v(a["R1_ci"][0]), "ci_hi": v(a["R1_ci"][1]), "ci_level": 0.95, "ci_kind": "percentile",
                    "n": 1, "n_kind": "agent (statement bootstrap)",
                    "method": f"own old role state persistence after reassignment vs placebo agents [{model}]",
                    "null": f"placebo agents median {nat['NE38']['placebo_R1']['median'] if nat['NE38']['placebo_R1'] else None}",
                    "source": SRC + f"natives/natives_{model}.json",
                    "notes": f"percentile {nat['NE38']['agent40_percentile']}; verdict {nat['NE38']['verdict']}"})
    for r in out:
        r.pop("first_day", None)
    return out


if __name__ == "__main__":
    r = rows()
    E.write_estimates(r, hypothesis="H96")
    print(len(r), "rows written")
