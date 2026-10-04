"""H17 round 1b per-period estimates -> shared per_period_estimates (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H17-behavior-metastable-sets/r1b"
SRC = "data/processed/H17-behavior-metastable-sets/r1b"
NOTE = "round 1b (2026-10-04): Jev v3.1 states, 6 macro states (wait = monitor_wait + idle + absent); descriptive (soft P3b/CK not identifiable)"


def unit(goal, days):
    u = E.map_unit(goal, days[0], days[-1])
    return u or f"G{goal:02d}"


def fin(x):
    return x if (x is not None and x < 1e5) else None


def main():
    rows = []
    for f in sorted(D.glob("G*.json")):
        r = json.loads(f.read_text())
        g, q = r["goal"], r["v3_q6"]
        pu = unit(g, r["days"])
        base = dict(period_unit=pu, goal_no=g, channel="behavior (Jev v3)", role="replication", first_day=r["days"][0],
                    last_day=r["days"][-1], source=f"{SRC}/{f.name}", post_hoc=False, n_kind="in-span 5-min windows",
                    n=q["n_windows"])
        lo, hi = q["t2_ci_raw"]
        rows.append(base | dict(statistic="msm_t2_star_v3", estimate=fin(q["t2"]), ci_lo=fin(lo), ci_hi=fin(hi), ci_level=0.95,
                                ci_kind="percentile", method="shifted estimator eig C(1)^-1 C(2), tau 5 min, agent-day bootstrap",
                                null="none", unit_local="min", status=None if fin(q["t2"]) else "unidentified (lambda2 ~ 1)",
                                notes=NOTE))
        rows.append(base | dict(statistic="msm_t2_star_v3_equal_n", estimate=fin(q["t2_eq"]), method="median t2 over 50 agent-day sets of ~3000 windows",
                                null="none", unit_local="min", ci_kind="none", notes=NOTE))
        rows.append(base | dict(statistic="p_blocked_mean", estimate=r["cov"]["p_blocked"], method="mean Jev p_blocked over labelled windows",
                                null="none", ci_kind="none", notes="round 1b stuckness covariate"))
        rows.append(base | dict(statistic="real_failure_share", estimate=r["cov"]["fail_share"], method="sum n_errors / sum n_actions (labelled windows)",
                                null="none", ci_kind="none", notes="round 1b; replaces actions.error (stderr)"))
    n = json.loads((D / "native_r1b.json").read_text())
    for key, g, pu, d0, d1 in (("N1_G51", 51, "G51", "2026-07-06", "2026-09-04"), ("N1_G38", 38, "38", "2026-04-02", "2026-04-24")):
        x = n[key]
        rows.append(dict(period_unit=pu, goal_no=g, statistic="ne41_relaxation_time", channel="behavior (Jev v3)", role="native",
                         estimate=x["forced"]["tau_relax_min"], method="decay of TV(mean state - agent mean) after forced erasures, windows 1-4",
                         null="mid-segment control anchors", unit_local="min", n=x["n_forced"], n_kind="forced erasures",
                         first_day=d0, last_day=d1, source=f"{SRC}/native_r1b.json", ci_kind="none",
                         notes=f"MSM t2*_bc {x['t2_bc']:.0f} min; prediction tau_relax within 0.5-2 x t2* failed"))
    for blk in ("A", "B", "C", "P1", "P2"):
        x = n["N2_NE43"][blk]
        rows.append(dict(period_unit=f"local:51_{blk}_{x['days'][0][5:]}_{x['days'][1][5:]}", goal_no=51, statistic="msm_t2_star_v3_bc",
                         channel="behavior (Jev v3)", role="native", estimate=fin(x["t2_bc"]), method="shifted estimator, lambda2 bias-corrected",
                         null="none", unit_local="min", n=x["n_windows"], n_kind="in-span 5-min windows", first_day=x["days"][0],
                         last_day=x["days"][1], source=f"{SRC}/native_r1b.json", ci_kind="none", notes="NE43 blocks (round 1b native N2)"))
    x = n["N3_G27"]
    rows.append(dict(period_unit="27", goal_no=27, statistic="change_point_perm_p", channel="behavior (Jev v3)", role="native",
                     estimate=x["p_perm"], method="best single split of day-level soft transition counts vs day-order permutations",
                     null="day-order permutation (1000)", first_day=x["days"][0], last_day=x["days"][-1],
                     source=f"{SRC}/native_r1b.json", ci_kind="none", notes="round 1b native N3"))
    out = E.write_estimates(rows, hypothesis="H17")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
