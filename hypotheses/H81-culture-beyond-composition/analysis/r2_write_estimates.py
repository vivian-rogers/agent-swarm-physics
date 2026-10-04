"""H81 round 2: per-regime-span rows in per_period_estimates (non-holdout; role replication). Round-1 rows are left as
they are (analysis/write_estimates.py).
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/r2_write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as Q  # noqa: E402

sys.path.insert(0, str(Q.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "hypotheses/H81-culture-beyond-composition/analysis/r2_run.py"
CH = {"bge_small": "content_bge", "gte_modernbert": "content_gte"}


def fin(x):
    return float(x) if x is not None and np.isfinite(x) else None


def main():
    res = json.loads((Q.R2 / "r2_results.json").read_text())
    rows = []
    base = lambda reg: {"period_unit": f"local:{reg}-span", "goal_no": None, "regime": reg, "holdout": False,  # noqa: E731
                        "role": "replication", "source": SRC}
    for m in Q.MODELS:
        for key, o in res["r1"][m].items():
            reg, plc = key.split("/")
            rows.append({**base(reg), "statistic": f"r2_record_carrier_C_R1_{plc}", "channel": CH[m], "estimate": o["C_R1"],
                         "ci_lo": o.get("C_R1_lo"), "ci_hi": o.get("C_R1_hi"), "ci_level": 0.95, "ci_kind": "percentile",
                         "n": o["n_agent_blocks_both"], "n_kind": "agent-blocks with read and placebo record",
                         "method": f"cos(agent-block culture residual, read-record content) - cos(., {plc} record content); "
                                   "goal-weighted; FE personal vectors (culture_vectors)",
                         "null": f"S_ex (calendar OU drift) q95 {o.get('S_ex_q95_C', float('nan')):.3f}; power at "
                                 f"{o.get('lam_star')} {o.get('power_C_at_lam_star', float('nan')):.2f}",
                         "notes": f"goal-cluster bootstrap CI; M_R {o['M_R']:.2f}, M_U {o['M_U']:.2f}; n goals {o['n_goals']}"})
        for reg, o in res["r2a"][m].items():
            rows.append({**base(reg), "statistic": "r2_slow_mode_D_adjg_operator_removed", "channel": CH[m],
                         "estimate": o["D_adjg_operator_removed"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                         "n": None, "method": "D_adjg after removing top-3 human-message PCs and neighbour-goal human "
                                              "centroids (+-21 d) from each goal's projector",
                         "null": f"S0 q95 {o.get('S0_q95_operator_removed', float('nan')):.3f}; placebo removal mean "
                                 f"{o['D_adjg_placebo_mean']:.3f} (sd {o['D_adjg_placebo_sd']:.3f}, 20 draws)",
                         "notes": f"retention {o['rho_op']:.2f} vs placebo {o['rho_pl']:.2f}"})
        for reg, o in res["r2b"][m].items():
            rows.append({**base(reg), "statistic": "r2_outside_topic_loading_L_out", "channel": CH[m], "estimate": o["L_out"],
                         "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": o["n_blocks"], "n_kind": "blocks",
                         "method": "cos(u_b, outside-topic statement residuals of other goals +-14 d) - cos(u_b, size-matched "
                                   "controls)", "null": f"label permutation within agent-days q95 {o['perm_q95']:.4f}, "
                                                        f"p {o['p_perm']:.3f}", "notes": f"{o['n_agentdays']} agent-days"})
        for reg, o in res["r2c"][m].items():
            for clk in ("calendar", "hours", "goals"):
                f = o[clk]
                se = fin(f.get("tau_se"))
                lo, hi = E.ci_from_se(f["tau"], se) if se else (None, None)
                rows.append({**base(reg), "statistic": f"r2_slow_mode_tau_{clk}", "channel": CH[m], "estimate": fin(f["tau"]),
                             "ci_lo": lo, "ci_hi": hi, "se": se, "ci_level": 0.95, "ci_kind": "se_z" if se else "none",
                             "n": f["n"], "n_kind": "cross-goal block pairs",
                             "method": f"OU profile fit of block culture-residual similarity vs {clk} lag (weighted NLS)",
                             "null": "clock decision needs synthetic accuracy >= 0.7",
                             "notes": f"weighted SSE {f['sse']:.4f}; best clock {o['best']}; units "
                                      f"{ {'calendar': 'days', 'hours': 'documented hours', 'goals': 'goal periods'}[clk] }"})
        for reg, o in res["r4"][m].items():
            for nm, f in (("tau_81_blocks", o["sep81"]), ("tau_82_boundaries", o["sep82"])):
                se = fin(f.get("tau_se"))
                lo, hi = E.ci_from_se(f["tau"], se) if se else (None, None)
                rows.append({**base(reg), "statistic": f"r2_joint_ou_{nm}", "channel": CH[m], "estimate": fin(f["tau"]),
                             "ci_lo": lo, "ci_hi": hi, "se": se, "ci_level": 0.95, "ci_kind": "se_z" if se else "none",
                             "n": f["n"], "n_kind": "pairs" if "81" in nm else "boundary x day x centroid fits",
                             "method": "OU fit A exp(-lag/tau) + c (days)", "null": "one-mode synthetic (S_ex) for dtau",
                             "notes": f"dtau {o['dtau']:.1f} d, jackknife SE {o['dtau_se_jk']:.1f}; joint tau "
                                      f"{o['joint'].get('tau', float('nan')):.1f}, LR {o['joint'].get('LR', float('nan')):.1f}"})
    df = E.write_estimates(rows, hypothesis="H81")
    print("rows written:", df.height)


if __name__ == "__main__":
    main()
