"""H81: write per-period rows to the shared per_period_estimates table (non-holdout only).
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "hypotheses/H81-culture-beyond-composition"
CH = {"bge_small": "content_bge", "gte_modernbert": "content_gte"}


def main():
    rows = []
    kap = pl.read_parquet(L.OUT / "replication/kappa.parquet")
    for r in kap.iter_rows(named=True):
        se = r["kappa_se"] if r["kappa_se"] == r["kappa_se"] else None
        rows.append({"period_unit": f"G{r['goal_no']:02d}", "goal_no": r["goal_no"], "statistic": "kappa_equal_time",
                     "channel": CH[r["model"]], "estimate": r["kappa"],
                     "ci_lo": r["kappa"] - 1.96 * se if se else None, "ci_hi": r["kappa"] + 1.96 * se if se else None,
                     "se": se, "ci_level": 0.95, "ci_kind": "jackknife_z" if se else "none", "n": r["n_agents_goal"],
                     "n_kind": "agents", "method": "mean pairwise alignment of agent residuals (DQ5 style_resid; FE "
                     "leave-goal-out personal vectors; exogenous directions projected)",
                     "null": f"sign-flip band [{r['null_lo']:.3f}, {r['null_hi']:.3f}]", "role": "replication",
                     "first_day": r["first_day"], "last_day": r["last_day"], "source": f"{SRC}/analysis/replication.py",
                     "notes": f"excess variance ratio {r['excess_ratio']:.2f}; equal-time, includes field leakage and convergence"})
    rep = json.loads((L.OUT / "replication/replication.json").read_text())
    for m in ("bge_small", "gte_modernbert"):
        syn = pl.read_parquet(L.OUT / f"synthetic/replicates_{m}.parquet")
        for reg in ("I", "III"):
            p = rep["primary"][f"{m}/{reg}"]
            s0 = syn.filter((pl.col("regime") == reg) & (pl.col("scenario") == "S0"))
            for stat, key, pre in (("slow_mode_D_adjg", "D_adjg", "P2"), ("slow_mode_D_adj_overlap", "D_adj", "P3"),
                                   ("slow_mode_D_near_disjoint", "D_near_perp", "P3 (descriptive)")):
                sd = float(np.nanstd(s0[key].to_numpy()))
                rows.append({"period_unit": f"local:{reg}-span", "goal_no": None, "regime": reg, "holdout": False,
                             "statistic": stat, "channel": CH[m], "estimate": p[key],
                             "ci_lo": p[key] - 1.96 * sd, "ci_hi": p[key] + 1.96 * sd, "se": sd, "ci_level": 0.95,
                             "ci_kind": "parametric", "n": p["n_pairs"], "n_kind": "cross-goal block pairs",
                             "method": f"{pre}: near (<=14 d) minus far (>=42 d) culture-residual similarity, WLS, goal-pair weights",
                             "null": f"synthetic S0 q95 {p['S0_q95'][key]:.3f} (SE from S0 sd)", "role": "replication",
                             "source": f"{SRC}/analysis/replication.py", "notes": f"{p['n_goals']} goals; exception (c)"})
    nat = json.loads((L.OUT / "natives/natives.json").read_text())
    for m in ("bge_small", "gte_modernbert"):
        g = nat["G51"][m]
        rows.append({"period_unit": "G51", "goal_no": 51, "statistic": "G51_cross_agent_lag_alignment_5_15d",
                     "channel": CH[m], "estimate": g["L_slow"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                     "n": g["n_agents"], "n_kind": "agents", "method": "cross-agent lagged residual alignment, k = 5-15 active days",
                     "null": f"circular-shift band [{g['null_q05']:.4f}, {g['null_q95']:.4f}], p_upper {g['p_upper']:.3f}",
                     "role": "native", "first_day": "2026-07-06", "last_day": "2026-09-04",
                     "source": f"{SRC}/analysis/natives.py", "notes": f"L(1) {g['L1']:.3f}; T {g['T_days']} days"})
        for day, v in nat["NE33"][m].items():
            if not isinstance(v, dict):
                continue
            rows.append({"period_unit": f"local:NE33-NE32_{day}", "goal_no": 51, "statistic": "stayer_jump_percentile",
                         "channel": CH[m], "estimate": v["percentile"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                         "n": v["n"], "n_kind": "agents", "method": "stayers' coherent jump at a batch-join boundary",
                         "null": f"{nat['NE33'][m]['n_placebo']} other #51 day boundaries", "role": "native",
                         "first_day": day, "last_day": day, "source": f"{SRC}/analysis/natives.py",
                         "notes": f"J_s {v['J_stayers']:.2f}"})
    df = E.write_estimates(rows, hypothesis="H81")
    print("rows written:", df.height)


if __name__ == "__main__":
    main()
