"""Write H125 per-period rows to the shared per_period_estimates table (write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h125lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

Z90 = 1.645
CHAN = {"bge_white": "content_bge_small", "gte_white": "content_gte_modernbert",
        "bge_style": "content_bge_small_style", "gte_style": "content_gte_modernbert_style"}


def unit_of(goal, day):
    pu = pl.read_parquet(L.S / "period_units.parquet").filter(pl.col("goal_no") == goal)
    for r in pu.iter_rows(named=True):
        if day in r["days"]:
            return r["unit_id"]
    return f"G{goal:02d}"


def main():
    d = pl.read_parquet(L.DATA / "NE34/kickoffs_all_configs.parquet")
    k = L.kickoffs()
    fday = dict(zip(k["design"].to_list(), k["first_day"].to_list()))
    src = "data/processed/H125-kickoff-damped-oscillator/NE34/kickoffs_all_configs.parquet"
    rows = []
    for r in d.filter(pl.col("cfg").is_in(list(CHAN))).iter_rows(named=True):
        g = r["goal_no"]
        base = dict(period_unit=unit_of(g, fday[r["design"]]), goal_no=g, channel=CHAN[r["cfg"]], n=r["n_u"], n_kind="agents",
                    role="replication", source=src, first_day=fday[r["design"]])

        def add(stat, est, se, method, null, notes=None):
            if est is None or est != est:
                return
            ok = se is not None and se == se
            rows.append(dict(base, statistic=stat, estimate=est, se=se if ok else None, ci_level=0.90 if ok else None,
                             ci_lo=est - Z90 * se if ok else None, ci_hi=est + Z90 * se if ok else None,
                             ci_kind="jackknife_z" if ok else "none", method=method, null=null, notes=notes))
        add("kickoff_undershoot_U", r["U"], r["se_U"], "within-agent excess alignment along k-hat, days 4-5 minus days 2-3 (active days after t0); agent jackknife",
            f"placebo-day U (ordinary origins d>=6, same k-hat), pooled 95th pct {r['placebo_q95']:.4f}")
        add("kickoff_overshoot_E1_days45", r["E1"], r["se_E1"], "within-agent day-1 (after t0) minus days 4-5 excess alignment along k-hat", "0 (no overshoot)")
        add("kickoff_osc_vs_fade_dsse", r["dsse"], None, "(SSE_fade - SSE_osc)/SSE_fade, 30-min active-hour series days 1-5, 5 shape + 3 slot parameters each",
            "synthetic null worlds: M_osc wins 35-59% of single kickoffs")
    for name, unit, goal in (("G51", "51a", 51), ("NE38", "51f", 51), ("G38", None, 38)):
        nat = json.loads((L.DATA / f"natives/{name}.json").read_text())
        for cfg, v in nat.items():
            if cfg not in CHAN:
                continue
            u = unit or unit_of(goal, "2026-04-02")
            srcn = f"data/processed/H125-kickoff-damped-oscillator/natives/{name}.json"
            if name == "G51":
                se = v["se_U"]
                rows.append(dict(period_unit=unit_of(51, "2026-07-06"), goal_no=51, channel=CHAN[cfg], statistic="g51_own_role_undershoot_U",
                                 estimate=v["U"], se=se, ci_level=0.90, ci_lo=v["U"] - Z90 * se, ci_hi=v["U"] + Z90 * se, ci_kind="jackknife_z",
                                 n=v["n_u"], n_kind="agents", method="own-role excess alignment (decoys = other agents' roles), days 4-5 minus days 2-3",
                                 null=f"placebo origins in #51, 95th pct {v['placebo_q95']:.4f}", role="native", source=srcn))
            if name == "NE38":
                rows.append(dict(period_unit=unit_of(51, "2026-07-29"), goal_no=51, channel=CHAN[cfg], statistic="ne38_opus5_undershoot_U",
                                 estimate=v["U_opus5"], ci_kind="none", n=v["n_others"] + 1, n_kind="agents",
                                 method="Opus 5 own-new-role excess alignment, days 4-5 minus days 2-3 after the 07-29 reassignment",
                                 null=f"other agents' own-role U, 90th pct {v['others_q90']:.4f}", role="native", source=srcn))
            if name == "G38":
                rows.append(dict(period_unit=u, goal_no=38, channel=CHAN[cfg], statistic="g38_osc_vs_fade_dsse_10d", estimate=v["dsse"],
                                 ci_lo=(v.get("dsse_ci") or [None, None])[0], ci_hi=(v.get("dsse_ci") or [None, None])[1],
                                 ci_level=0.90 if v.get("dsse_ci") else None, ci_kind="percentile" if v.get("dsse_ci") else "none",
                                 n=v["n_agents"], n_kind="agents", method="M_osc vs M_fade on days 1-10 (30-min active-hour series)",
                                 null="0 (no preference)", role="native", source=srcn, notes=f"zeta_fit {v['zeta_fit']:.2f}"))
    out = E.write_estimates(rows, hypothesis="H125")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
