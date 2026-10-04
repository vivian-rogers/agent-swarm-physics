"""H16 round 1b per-period estimates -> shared per_period_estimates (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H16-metastable-traps-kramers/r1b"
SRC = "data/processed/H16-metastable-traps-kramers/r1b"


def ok(x):
    return x if (x is not None and isinstance(x, (int, float)) and math.isfinite(x)) else None


def main():
    S = json.loads((D / "summary_r1b.json").read_text())["periods"]
    rows = []
    for p, o in S.items():
        g = int(p[1:3])
        r = json.loads((D / p / "results.json").read_text())
        days = r["days"]
        u = E.map_unit(g, days[0], days[-1]) or f"local:{g}_{days[0][5:]}_{days[-1][5:]}"
        o1 = o["r1b"]
        base = dict(period_unit=u, goal_no=g, role="replication", first_day=days[0], last_day=days[-1],
                    source=f"{SRC}/{p}/results.json", null="memoryless (beta = 0)")
        for stat, ch, b, c, ev, how in (
                ("trap_aging_slope_deep", "error loops (real failures)", o1["ts3_beta"], o1["ts3_ci"], o1["ts3_events"], "k >= 3, per turn"),
                ("trap_aging_slope_deep", "Jev blocked spells (p_blocked >= 0.5)", o1["ts5_beta"], o1["ts5_ci"], o1["ts5_events"], "k >= 2 windows"),
                ("trap_aging_slope_deep", "Jev loop spells (longest_run >= 5)", o1["ts6_beta"], o1["ts6_ci"], o1["ts6_events"], "k >= 2 windows")):
            rows.append(base | dict(statistic=stat, channel=ch, estimate=ok(b), ci_lo=ok(c[0]), ci_hi=ok(c[1]), ci_level=0.95,
                                    ci_kind="percentile", n=ok(ev), n_kind="escapes in agents with variation",
                                    method=f"agent-FE cloglog break hazard on ln k ({how}), day-bootstrap CI",
                                    notes="round 1b (2026-10-04)"))
        if ok(o1["gate_dir1"]) is not None:
            b, se = o1["gate_dir1"], o1["gate_dir1_se"]
            rows.append(base | dict(statistic="gate_kick_lnOR_directed", channel="TS2r pause gates (leading-@ nudge targets)",
                                    estimate=b, se=se, ci_lo=b - 1.96 * se, ci_hi=b + 1.96 * se, ci_level=0.95, ci_kind="se_z",
                                    method="agent-FE logit of gate escape on directed-kick dose 1 (ln k, ln declared controlled)",
                                    null="OR = 1", notes="round 1b (2026-10-04)"))
    n = json.loads((D / "native_r1b.json").read_text())
    # before NE44 = the non-holdout periods G37, G38, G39, G40, G41, G42, G44 only (no date span: #43 sits between them)
    for side, pu, d0, d1 in (("pre", "local:III_4h_G37-G42+G44_preNE44", None, None),
                             ("post", "local:51_0706_0820_postNE44", "2026-07-06", "2026-08-20")):
        x = n["N1_NE44"][side]["D_x_lnk"]
        rows.append(dict(period_unit=pu, goal_no=None if side == "pre" else 51, statistic="gate_kick_x_lnk_interaction",
                         channel="TS2r pause gates", role="native", estimate=x["beta"], se=x["se"], ci_lo=x["ci"][0], ci_hi=x["ci"][1],
                         ci_level=0.95, ci_kind="se_z", method="agent-FE logit, directed kick x ln k (period dummies before NE44)",
                         null="0", first_day=d0, last_day=d1, source=f"{SRC}/native_r1b.json", notes="round 1b native N1 (NE44)"))
    x = n["N2_NE43"]["gate_C_indicator"]["extra"]
    rows.append(dict(period_unit="local:51_0807_0902_NE43", goal_no=51, statistic="gate_escape_nudger_off_effect", channel="TS2r pause gates",
                     role="native", estimate=x["beta"], se=x["se"], ci_lo=x["ci"][0], ci_hi=x["ci"][1], ci_level=0.95, ci_kind="se_z",
                     method="agent-FE logit, indicator for 08-21..09-02 vs 08-07..08-20", null="0", first_day="2026-08-07",
                     last_day="2026-09-02", source=f"{SRC}/native_r1b.json", notes="round 1b native N2 (NE43)"))
    out = E.write_estimates(rows, hypothesis="H16")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
