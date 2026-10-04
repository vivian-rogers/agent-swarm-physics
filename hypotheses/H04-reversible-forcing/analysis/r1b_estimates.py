"""H04 round 1b: write per-period estimates (infra/shared/estimates.py: write_estimates) from data/processed/.../r1b/.

  uv run python hypotheses/H04-reversible-forcing/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

R = ROOT / "data/processed/H04-reversible-forcing/r1b"
METHOD = ("matched minute-level response, sum over tau 1-30 (A30); activity_bins_fixed; leading-@ target; every nudge "
          "treated (no future-kick isolation); past-only control eligibility; strata agent x state x 15-min history x "
          "since-active x since-direct-kick x day-third; additive day FE; presence mask; day-block bootstrap (1000)")


def main():
    rows = []
    suites = {"G38": (38, None), "G41": (41, None), "G44": (44, None), "G51": (51, None),
              "III_4h_pre_NE44": (None, "local:III_4h_36to44_preNE44"), "NE10_G30_G31": (None, "local:NE10_30_31"),
              "NE43_pre": (51, "local:51_NE43_pre_0721_0804"), "NE43_on": (51, "local:51_NE43_on_0805_0820")}
    for s, (g, local) in suites.items():
        d = json.loads((R / f"{s}.json").read_text())
        unit = local or E.map_unit(g)
        role = "native" if s.startswith(("NE", "III_4h")) else "replication"
        span_ok = s.startswith("NE43")   # pooled suites skip held-out days inside their span, so give no date range
        for key, ch in (("nudge_target_all", "nudge -> target (all nudges)"), ("nudge_target_first", "nudge -> target (first nudges)"),
                        ("nudge_target_repeat", "nudge -> target (repeat nudges)"), ("nudge_bystander", "nudge -> bystanders")):
            v = d["G"].get(key, {})
            if not v.get("n_cells") or not v.get("A30"):
                continue
            rows.append(dict(period_unit=unit, goal_no=g, statistic="kick_response_A30", channel=ch, estimate=v["A30"][0],
                             ci_lo=v["A30"][1], ci_hi=v["A30"][2], ci_kind="percentile", n=float(v["n_cells"]), n_kind="kick-target cells",
                             method=METHOD, null="matched no-kick controls (past-only) with day FE", role=role,
                             source=f"data/processed/H04-reversible-forcing/r1b/{s}.json", status="round 1b",
                             notes=f"non-holdout days {d['date_range'][0]}..{d['date_range'][1]} ({d['n_days']} d)",
                             first_day=d["date_range"][0] if span_ok else None, last_day=d["date_range"][1] if span_ok else None))
        ro = d.get("readout") or {}
        if ro.get("age_s_q"):
            rows.append(dict(period_unit=unit, goal_no=g, statistic="nudge_readout_delay_median_s", channel="nudge -> target",
                             estimate=ro["age_s_q"][2], ci_lo=None, ci_hi=None, ci_kind="none",
                             n=float(ro["n_matched"]), n_kind="nudges", method="context-ledger age_s at the target's receiving call (median; interval = IQR)",
                             null="none (descriptive)", role=role, source=f"data/processed/H04-reversible-forcing/r1b/{s}.json",
                             status="round 1b", first_day=d["date_range"][0] if span_ok else None, last_day=d["date_range"][1] if span_ok else None,
                             notes=f"IQR {ro['age_s_q'][1]:.0f}-{ro['age_s_q'][3]:.0f} s; q90 {ro['age_s_q'][4]:.0f} s"))
    n43 = json.loads((R / "NE43.json").read_text())
    for w, v in n43["windows"].items():
        rows.append(dict(period_unit=f"local:51_NE43_{w}", goal_no=51, statistic="hawkes_branching_ratio_n", channel="agent chat (10 s bins)",
                         estimate=v["n_ci"][0], ci_lo=v["n_ci"][1], ci_hi=v["n_ci"][2], ci_kind="percentile", n=float(v["hawkes"]["n_events"]), n_kind="talk events",
                         method="H04 Hawkes (two exponential endogenous kernels, profiled daily baseline); 30 day-bootstrap refits",
                         null="inhomogeneous Poisson", role="native", source="data/processed/H04-reversible-forcing/r1b/NE43.json",
                         status="round 1b", first_day=v["days"][0], last_day=v["days"][1]))
    out = E.write_estimates(rows, hypothesis="H04")
    print(f"wrote {out.height} rows")


if __name__ == "__main__":
    main()
