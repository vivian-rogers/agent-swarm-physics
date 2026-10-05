"""H16 round 2 per-period estimates -> shared per_period_estimates (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H16-metastable-traps-kramers/r2"
SRC = "data/processed/H16-metastable-traps-kramers/r2"
R1B = ROOT / "data/processed/H16-metastable-traps-kramers/r1b"
NOTE = "round 2 (2026-10-05)"


def ok(x):
    return x if (x is not None and isinstance(x, (int, float)) and math.isfinite(x)) else None


def unit(p):
    g = int(p[1:3])
    days = json.loads((R1B / p / "results.json").read_text())["days"]
    return g, days, (E.map_unit(g, days[0], days[-1]) or f"local:{g}_{days[0][5:]}_{days[-1][5:]}")


def main():
    res = json.loads((D / "results_r2.json").read_text())
    ph = json.loads((D / "posthoc_r2.json").read_text())
    rows = []
    for p, o in res["gates"].items():
        g, days, u = unit(p)
        base = dict(period_unit=u, goal_no=g, first_day=days[0], last_day=days[-1], source=f"{SRC}/results_r2.json", ci_level=0.95,
                    ci_kind="percentile", notes=NOTE)
        st = o["stats"]
        gate = "idle gates (sustained escape; ledger call clock)"
        rows.append(base | dict(statistic="trap_aging_slope_gate", channel=gate, role="replication", estimate=st["beta_a0"]["est"],
                                se=st["beta_a0"]["se"], ci_lo=st["beta_a0"]["ci"][0], ci_hi=st["beta_a0"]["ci"][1], n=o["n_escapes"], n_kind="escapes",
                                method="agent-FE logit on ln trap age + nuisance, day-bootstrap CI", null="memoryless (0)"))
        for ur in ("f_call", "f_tok"):
            r = st[f"abs_{ur}.rho"]
            rows.append(base | dict(statistic="urn_absorbed_aging_rho", channel=f"{gate}; urn {ur}", role="replication", estimate=ok(r["est"]),
                                    ci_lo=ok(r["ci"][0]), ci_hi=ok(r["ci"][1]), n=o["n_gates"], n_kind="gates",
                                    method="1 - beta_a(with ln(1-f)) / beta_a(without)", null="0 (intrinsic aging)"))
        bf = st["abs_f_call.beta_f"]
        rows.append(base | dict(statistic="urn_coefficient_ln1mf", channel=f"{gate}; urn f_call", role="replication", estimate=bf["est"], se=bf["se"],
                                ci_lo=bf["ci"][0], ci_hi=bf["ci"][1], n=o["n_gates"], n_kind="gates",
                                method="agent-FE logit coefficient on ln(1 - own idle share of own calls in the segment)", null="0; urn ~ +1"))
        fr = st["reset.forced"]
        rows.append(base | dict(statistic="forced_reset_escape_lnOR", channel=f"{gate}; NE41 41-call cap inside a trap", role="native",
                                estimate=fr["est"], se=fr["se"], ci_lo=fr["ci"][0], ci_hi=fr["ci"][1], n=o["n_forced"], n_kind="forced-reset gates",
                                method="agent-FE logit, forced-reset indicator, ln k and nuisance (amendment R2-A1)", null="0 (frailty / intrinsic)"))
        for k, stat in (("kick.diff", "gate_kick_lnOR_directed_minus_undirected"), ("kick.dir", "gate_kick_lnOR_directed_read"),
                        ("kick.undir", "gate_kick_lnOR_undirected_read")):
            v = st[k]
            rows.append(base | dict(statistic=stat, channel=f"{gate}; items read at the gate (ledger)", role="replication", estimate=v["est"],
                                    se=v["se"], ci_lo=v["ci"][0], ci_hi=v["ci"][1], n=o["n_dir"] if "dir" in k else o["n_undir"],
                                    n_kind="gates with such reads", method="agent-FE logit with ln k and nuisance (R2-A1)", null="0; urn: equal per item"))
    for p, o in res["ts1r"].items():
        if not o.get("pooled"):
            continue
        g, days, u = unit(p)
        base = dict(period_unit=u, goal_no=g, first_day=days[0], last_day=days[-1], source=f"{SRC}/results_r2.json", ci_level=0.95,
                    ci_kind="percentile", notes=NOTE, role="replication", null="memoryless (0)", n_kind="deep escapes")
        for key, ch in (("within_cell", "TS1r deep; agent x kind_start x last_kind FE"), ("no_consol", "TS1r deep; consolidation-latency spells removed")):
            v = o[key]
            rows.append(base | dict(statistic="trap_aging_slope_deep", channel=ch, estimate=ok(v["beta"]), se=ok(v["se"]), ci_lo=ok(v["ci"][0]),
                                    ci_hi=ok(v["ci"][1]), n=v["events"], method="cloglog per 30-s bin on ln elapsed (>= 10 min), day-bootstrap CI"))
        v = o["by_kind"].get("pause", {})
        if v.get("beta") is not None:
            rows.append(base | dict(statistic="trap_aging_slope_deep", channel="TS1r deep; pause-start spells", estimate=ok(v["beta"]), se=ok(v["se"]),
                                    ci_lo=ok(v["ci"][0]), ci_hi=ok(v["ci"][1]), n=v["events"], method="agent-FE cloglog on ln elapsed, day-bootstrap CI"))
        if "mixture_null" in o:
            m = o["mixture_null"]
            rows.append(base | dict(statistic="trap_aging_slope_mixture_null", channel="TS1r deep; pure mixture of agent x kind cells",
                                    estimate=m["mean"], ci_lo=m["q"][0], ci_hi=m["q"][1], n=m["sims"], n_kind="null draws", ci_kind="percentile",
                                    method="constant hazard per cell, per-row draws on the real skeleton", null="observed slope must lie below"))
    s = res["r3"]["G51_agent_slopes"]
    g, days, u = unit("G51")
    rows.append(dict(period_unit=u, goal_no=g, first_day=days[0], last_day=days[-1], statistic="trap_aging_slope_agent_I2",
                     channel="TS1r deep; per-agent slopes", role="replication", estimate=s["I2"], ci_lo=None, ci_hi=None, ci_kind="none",
                     n=s["n_agents"], n_kind="agents", method="Cochran Q of per-agent cloglog slopes", null="0 (no heterogeneity)",
                     source=f"{SRC}/results_r2.json", notes=NOTE))
    p5 = ph["P5_reset_by_k"]
    rows.append(dict(period_unit=u, goal_no=g, first_day=days[0], last_day=days[-1], statistic="forced_reset_x_lnk_interaction",
                     channel="idle gates; NE41 forced reset inside a trap", role="native", estimate=p5["forced_x_lnk"], ci_lo=p5["ci_forced_x_lnk"][0],
                     ci_hi=p5["ci_forced_x_lnk"][1], ci_level=0.95, ci_kind="percentile", n=276, n_kind="forced-reset gates",
                     method="agent-FE logit, forced x (ln k - mean)", null="0", post_hoc=True, source=f"{SRC}/posthoc_r2.json", notes=NOTE + "; post hoc"))
    out = E.write_estimates(rows, hypothesis="H16")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
