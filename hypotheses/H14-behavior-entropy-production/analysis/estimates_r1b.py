"""H14 round 1b per-period estimates -> shared per_period_estimates (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

import os  # noqa: E402

# H14_EP=heldout (ep_gauss_crossfit recheck, 2026-10-04): rows from r1b/recheck_epfix/, method tagged; the round-1b
# rows stay (write_estimates keys on statistic, channel, method, role, source).
EP = os.environ.get("H14_EP", "xprod")
D = ROOT / "data/processed/H14-behavior-entropy-production/r1b" / ("" if EP == "xprod" else "recheck_epfix")
SRC = "data/processed/H14-behavior-entropy-production/r1b" + ("" if EP == "xprod" else "/recheck_epfix")
NOTE = "round 1b (2026-10-04)" if EP == "xprod" else "ep_gauss_crossfit recheck (2026-10-04): supersedes the legacy-Newton row"
TAG = "" if EP == "xprod" else " [held-out Newton, per-column ridge]"


def main():
    s = json.loads((D / "summary_r1b.json").read_text())["periods"]
    rows = []
    for p, o in s.items():
        g = int(p[1:])
        r = json.loads((D / p / "results.json").read_text())
        days = r["days"]
        u = E.map_unit(g, days[0], days[-1]) or f"G{g:02d}"
        base = dict(period_unit=u, goal_no=g, role="replication", first_day=days[0], last_day=days[-1],
                    source=f"{SRC}/{p}/results.json", ci_kind="none")
        for var, ch in (("act_sh", "fine actions + shell sub-classes"), ("act_sh_b3", "fine actions, agent-only, burn-in 3"),
                        ("coarse_b3", "coarse states, agent-only, burn-in 3")):
            rows.append(base | dict(statistic="frac_agents_ep_above_null", channel=ch, estimate=o.get(f"{var}_frac_above_null"),
                                    n=o.get(f"{var}_n_test"), n_kind="test agents (>= 1000 transitions)",
                                    method="share of agents with cross-fitted Newton EP above the DB-surrogate p95",
                                    null="detailed-balance surrogate (200 / 100)", notes=NOTE))
            rows.append(base | dict(statistic="median_ep_excess", channel=ch, estimate=o.get(f"{var}_median_exc"),
                                    method="median over agents of Newton EP minus DB-null mean", null="detailed-balance surrogate",
                                    unit_local="nats/transition", notes=NOTE))
        for b3, ch in (("P9_coarse_b3_median_share_kept", "coarse states"), ("P9_act_sh_b3_median_share_kept", "fine actions + shell sub-classes")):
            rows.append(base | dict(statistic="ep_share_kept_after_scaffold_removal", channel=ch, estimate=o.get(b3),
                                    method="median agent ratio of excess, agent-only chain with burn-in 3 / full chain", null="none",
                                    notes=NOTE))
        v = o["pooled_v3s"]
        rows.append(base | dict(statistic="pooled_ep_soft_v3", channel="behavior (Jev v3)", estimate=v.get("newton"),
                                n=v.get("n_trans"), n_kind="5-min transitions", unit_local="nats/transition",
                                method="cross-fitted Newton on soft antisymmetric observables, all agents pooled, day folds",
                                null="block-flip (1-h blocks, 200)", notes=f"{NOTE}; flip p {v.get('flip_p')}, null p95 {v.get('flip_null_p95')}"))
    n = json.loads((D / "native_r1b.json").read_text())
    for b, x in n["N1_NE43"]["boundaries"].items():
        rows.append(dict(period_unit=f"local:51_NE43_boundary_{b[5:]}", goal_no=51, statistic="ep_relative_change_at_boundary",
                         channel="behavior (Jev v3)", role="native", estimate=x["v3s_rel_change"], first_day=None, last_day=None,
                         method="pooled soft v3 EP, 5 days after / 5 days before - 1", null="placebo boundaries",
                         source=f"{SRC}/native_r1b.json", ci_kind="none", notes=f"{x['kind']}; round 1b native N1"))
        rows.append(dict(period_unit=f"local:51_NE43_boundary_{b[5:]}", goal_no=51, statistic="ep_relative_change_at_boundary",
                         channel="fine actions, agent-only, burn-in 3", role="native", estimate=x["act_sh_b3_rel_change"],
                         method="pooled act_sh_b3 EP, 5 days after / 5 days before - 1", null="placebo boundaries",
                         source=f"{SRC}/native_r1b.json", ci_kind="none", notes=f"{x['kind']}; round 1b native N1"))
    x = n["N2_NE14"]
    for ch, k in (("coarse states", "coarse"), ("fine actions + shell sub-classes", "act_sh"), ("behavior (Jev v3)", "v3s")):
        rows.append(dict(period_unit="local:36_NE14_03-24_03-27_over_03-23", goal_no=36, statistic="ep_ratio_after_over_before",
                         channel=ch, role="native", estimate=x[k]["ratio"], ci_lo=x[k]["ratio_ci"][0], ci_hi=x[k]["ratio_ci"][1],
                         ci_level=0.95, ci_kind="percentile", method="pooled EP with agent folds, 03-24..03-27 / 03-23",
                         null="none", source=f"{SRC}/native_r1b.json", first_day="2026-03-23", last_day="2026-03-27",
                         notes="round 1b native N2 (regime II -> III)"))
    for g in (38, 39, 40):
        y = n["N3_loops"][f"G{g}"]
        rows.append(dict(period_unit=E.map_unit(g), goal_no=g, statistic="ep_productive_minus_stuck", channel="behavior (Jev v3)",
                         role="native", estimate=y.get("diff"), ci_lo=y.get("diff_ci", [None, None])[0], ci_hi=y.get("diff_ci", [None, None])[1],
                         ci_level=0.95, ci_kind="percentile", method="pooled soft v3 EP on productive-productive minus stuck-stuck transitions",
                         null="agent-day bootstrap", source=f"{SRC}/native_r1b.json", notes="round 1b native N3"))
    if TAG:
        for r in rows:
            r["method"] = r["method"] + TAG
            r["post_hoc"] = True
    out = E.write_estimates(rows, hypothesis="H14")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
