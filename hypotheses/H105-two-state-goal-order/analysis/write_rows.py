"""Write H105 per-period rows to the shared per_period_estimates table (write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h105lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402


def main():
    des = pl.read_parquet(L.DATA / "designs.parquet")
    unit = dict(zip(des["design"].to_list(), des["A_unit"].to_list()))
    agoal = dict(zip(des["design"].to_list(), des["A_goal"].to_list()))
    pairs = pl.read_parquet(L.DATA / "NE34/pairs_all_configs.parquet").filter(pl.col("cfg").is_in(["primary", "gte"]) & pl.col("testable"))
    kick = pl.read_parquet(L.DATA / "NE34/kickoffs.parquet").filter(pl.col("testable"))
    rows = []
    src_p = "data/processed/H105-two-state-goal-order/NE34/pairs_all_configs.parquet"
    src_k = "data/processed/H105-two-state-goal-order/NE34/kickoffs.parquet"

    def add(design, stat, est, lo, hi, n, method, null, ch, src, kind="percentile", notes=None):
        if est is None or est != est:
            return
        rows.append(dict(period_unit=unit[design], goal_no=agoal[design], statistic=stat, channel=ch, estimate=est,
                         ci_lo=lo, ci_hi=hi, ci_kind=kind if lo is not None else "none", ci_level=0.90 if lo is not None else None,
                         n=n, n_kind="agents", method=method, null=null, role="replication", source=src, notes=notes))
    for r in pairs.iter_rows(named=True):
        ch = "content_bge_small" if r["cfg"] == "primary" else "content_gte_modernbert"
        add(r["design"], "goal_occupancy_assigned", r["pA"], r["pA_lo"], r["pA_hi"], r["n_agents"], "agent-window goal spin (95% decoy threshold, majority), assigned-week days 2+", "decoy rate 0.05", ch, src_p)
        add(r["design"], "two_state_loop_gain_assigned", r["gA"], None, None, r["n_agents"], "g2 = 1 - V_ind/V (composition-adjusted occupancy)", "independent agents g2=0", ch, src_p)
        add(r["design"], "tilt_variance_log_ratio", r["rho"], r["rho_lo"], r["rho_hi"], r["n_agents"], "ln(V_A obs / V_A tilt-predicted from the free week, RPA)", "0 (tilt); not identifiable (Amendment 1)", ch, src_p)
        add(r["design"], "logit_shift_slope", r["s"], r["s_lo"], r["s_hi"], r["n_agents"], "IV slope of logit f_i^A on logit f_i^F (statement-level)", "1 (tilt), 0 (common target)", ch, src_p)
    for r in kick.iter_rows(named=True):
        if r["design"] in ("K04", "K06", "K12", "K17", "K38"):
            continue  # identical to the pairs
        add(r["design"], "goal_occupancy_assigned", r["pA"], r["pA_lo"], r["pA_hi"], r["n_agents"], "as pairs; F = last <=5 days of the previous period", "decoy rate 0.05", "content_bge_small", src_k)
        add(r["design"], "tilt_variance_log_ratio", r["rho"], r["rho_lo"], r["rho_hi"], r["n_agents"], "as pairs; F = previous period tail", "0 (tilt); not identifiable", "content_bge_small", src_k)
    g51 = json.loads((L.DATA / "natives/G51.json").read_text())
    for m, v in g51.items():
        for u in v["units"]:
            rows.append(dict(period_unit=u["unit"], goal_no=51, statistic="two_state_loop_gain_own_goal", channel=f"content_{m}",
                             estimate=u["g_own"], ci_lo=None, ci_hi=None, ci_kind="none", n=u["N"], n_kind="agents",
                             method="g2 of each agent's spin along its own agent_goal (own decoy threshold)",
                             null=f"R_own 90% CI [{u['R_own_lo']:.2f},{u['R_own_hi']:.2f}] vs 1", role="native",
                             source="data/processed/H105-two-state-goal-order/natives/G51.json"))
    ne = json.loads((L.DATA / "natives/NE38.json").read_text())
    for m, v in ne.items():
        rows.append(dict(period_unit="51f", goal_no=51, statistic="ne38_others_occupancy_did", channel=f"content_{m}", estimate=v["did"],
                         ci_lo=v["did_lo"], ci_hi=v["did_hi"], ci_kind="percentile", ci_level=0.90, n=None, n_kind="agents",
                         method="others' occupancy change along Opus 5's new goal minus mean change along other agents' goals",
                         null="0 (no coupling transfer)", role="native", source="data/processed/H105-two-state-goal-order/natives/NE38.json",
                         notes="spans units 51e/51f (07-24..08-04)"))
    out = E.write_estimates(rows, hypothesis="H105")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
