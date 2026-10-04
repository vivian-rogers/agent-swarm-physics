"""H126: per-unit rows into the shared per_period_estimates table (replication units; natives N12, N51).
Kickoff designs and NE38 are transitions and are not written (estimates_schema.md, "one model per period").
Usage: uv run python hypotheses/H126-telegraph-goal-occupancy/analysis/write_rows.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H126-telegraph-goal-occupancy"
RES = D / "results"
SRC = "data/processed/H126-telegraph-goal-occupancy/results"


def main():
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet")
    pinfo = {r["unit_id"]: r for r in pu.iter_rows(named=True)}
    rows = []

    def base(uid, role, n, nk="agents"):
        r = pinfo[uid]
        return dict(hypothesis="H126", period_unit=uid, goal_no=int(r["goal_no"]), role=role, n=float(n), n_kind=nk,
                    first_day=r["first_day"], last_day=r["last_day"], unit_local=uid, status="ok")
    units = json.loads((RES / "units.json").read_text())
    for u in units:
        if not u.get("eligible"):
            continue
        uid = u["design"][1:]
        b = base(uid, "replication", u["n_agents"])
        rows += [
            dict(**b, statistic="telegraph_dll_held_m4_minus_m2", channel="content_goal", estimate=u["dll4_held"],
                 ci_lo=None, ci_hi=None, ci_kind="none",
                 method="held-out-day (2-fold) log-lik per statement, profile 4-state hyperexponential minus per-agent 2-state HMM, call clock",
                 null=f"parametric bootstrap under the fitted telegraph (N0); q95 {u['null_q95']:.4f}", source=f"{SRC}/units.json"),
            dict(**b, statistic="telegraph_dwell_cv_max", channel="content_goal", estimate=max(u["cv_on"], u["cv_off"]),
                 ci_lo=None, ci_hi=None, ci_kind="none", method="max dwell CV (on, off) of the fitted profile 4-state model",
                 null="exponential dwell CV = 1", source=f"{SRC}/units.json"),
            dict(**b, statistic="telegraph_occupancy_log_ratio_heldout", channel="content_goal", estimate=u["rho_p"],
                 ci_lo=None, ci_hi=None, ci_kind="none",
                 method="ln(observed / M2a-predicted agent-window occupancy) on held-out days, mean of 2 folds",
                 null="0 (telegraph with stationary rates)", source=f"{SRC}/units.json"),
            dict(**b, statistic="telegraph_tau_on_calls_median", channel="content_goal", estimate=u["tau_on_med"],
                 ci_lo=None, ci_hi=None, ci_kind="none", method="median over agents of 1/k_off (calls), two-stage HMM",
                 null=None, source=f"{SRC}/units.json"),
            dict(**b, statistic="telegraph_tau_off_calls_median", channel="content_goal", estimate=u["tau_off_med"],
                 ci_lo=None, ci_hi=None, ci_kind="none", method="median over agents of 1/k_on (calls), two-stage HMM",
                 null=None, source=f"{SRC}/units.json"),
            dict(**b, statistic="telegraph_p_dwell", channel="content_goal", estimate=u["p_dw"], ci_lo=None, ci_hi=None,
                 ci_kind="none", method="statement-weighted mean k_on/(k_on+k_off), two-stage HMM", null=None,
                 source=f"{SRC}/units.json"),
            dict(**b, statistic="telegraph_dll_call_minus_wall", channel="content_goal", estimate=u["dllw_held"],
                 ci_lo=None, ci_hi=None, ci_kind="none", method="held-out-day log-lik per statement, call-clock minus wall-clock M2a",
                 null="0", source=f"{SRC}/units.json"),
        ]
    nat = json.loads((RES / "natives.json").read_text())
    for r in [x for x in nat["N12"] if x.get("eligible")]:
        uid = r["design"].split("_")[1]
        b = base(uid, "native", r["n_agents"])
        for st, est, lo, hi in (("telegraph_dln_kon_debate", r["dln_a"], r["a_lo"], r["a_hi"]),
                                ("telegraph_dln_koff_debate", r["dln_b"], r["b_lo"], r["b_hi"])):
            rows.append(dict(**b, statistic=st, channel="content_goal", estimate=est, ci_lo=lo, ci_hi=hi, ci_level=0.90,
                             ci_kind="percentile", method="shared-rate HMM, rates split by DQ6 debate windows; agent-cluster bootstrap",
                             null="0", source=f"{SRC}/natives.json"))
    for r in nat["N51"]:
        if not r.get("eligible"):
            continue
        b = base(r["unit"], "native", r["n_agents"])
        rows += [dict(**b, statistic="telegraph_own_goal_dll_held_m4_minus_m2", channel="content_own_goal",
                      estimate=r["dll4_held"], ci_lo=None, ci_hi=None, ci_kind="none",
                      method="as the replication statistic, own agent_goal directions", null=f"N0 q95 {r['null_q95']:.4f}",
                      source=f"{SRC}/natives.json"),
                 dict(**b, statistic="telegraph_own_goal_occupancy_log_ratio_heldout", channel="content_own_goal",
                      estimate=r["rho_p"], ci_lo=None, ci_hi=None, ci_kind="none",
                      method="as the replication statistic, own agent_goal directions", null="0",
                      source=f"{SRC}/natives.json")]
    rows = [r for r in rows if r["estimate"] is not None and math.isfinite(r["estimate"])]
    E.write_estimates(rows, hypothesis="H126")
    print("wrote", len(rows))


if __name__ == "__main__":
    main()
