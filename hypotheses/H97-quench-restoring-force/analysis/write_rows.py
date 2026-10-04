"""Write H97 per-period rows to the shared per_period_estimates table (write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h97lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

Z90 = 1.645


def unit_of(goal, day):
    pu = pl.read_parquet(L.S / "period_units.parquet").filter(pl.col("goal_no") == goal)
    for r in pu.iter_rows(named=True):
        if day in r["days"]:
            return r["unit_id"]
    return f"G{goal:02d}"


def main():
    d = pl.read_parquet(L.DATA / "NE34/transitions_all_configs.parquet").filter(pl.col("same_regime"))
    src = "data/processed/H97-quench-restoring-force/NE34/transitions_all_configs.parquet"
    rows = []
    chan = {"primary": "content_bge_small", "gte": "content_gte_modernbert", "center": "content_bge_small_centered",
            "gte_center": "content_gte_modernbert_centered"}
    for r in d.filter(pl.col("cfg").is_in(list(chan))).iter_rows(named=True):
        u = unit_of(r["p"], r["first_day"])
        base = dict(period_unit=u, goal_no=r["p"], channel=chan[r["cfg"]], n=r["N"], n_kind="agents", role="replication",
                    ci_kind="se_z", ci_level=0.90, source=src, first_day=r["first_day"])
        def add(stat, est, se, method, null, notes=None):
            if est is None or se is None or not (est == est):
                return
            ok = se == se
            rows.append(dict(base, statistic=stat, estimate=est, se=se if ok else None,
                             ci_lo=est - Z90 * se if ok else None, ci_hi=est + Z90 * se if ok else None,
                             ci_kind="se_z" if ok else "none", method=method, null=null, notes=notes))
        add("kickoff_memory_rho", r["rho_full"], r["se_rho_full"], "disattenuated cross-agent memory correlation, prev last day -> day 1, split-half; jackknife SE", "none")
        if r["n_placebo"] and r["N"] >= 5:
            add("kickoff_extra_forgetting_drho", r["drho_full"], r["se_drho_full"], "placebo-day memory minus kickoff memory (rho)", "ordinary day boundaries, same agents, same k")
            add("kickoff_extra_forgetting_drho_par", r["drho_par"], r["se_drho_par"], "as drho, along the kickoff direction", "ordinary day boundaries")
            add("kickoff_extra_forgetting_drho_perp", r["drho_perp"], r["se_drho_perp"], "as drho, transverse to the kickoff direction", "ordinary day boundaries")
            add("kickoff_isotropy_beta_par_minus_perp", r["iso_diff"], r["se_iso_diff"], "IV slope along k minus transverse", "0 (scalar chi)")
        if r["cfg"] in ("center", "gte_center") and r.get("shape_a") is not None:
            add("kickoff_overshoot_intercept", r["shape_a"], r["se_shape_a"], "HH-literal intercept along k vs plateau target (agent-centered)", "0 (law through origin)")
    for name, unit, goal in (("NE38", "51f", 51), ("G44", "44a", 44), ("G26", "26", 26)):
        nat = json.loads((L.DATA / f"natives/{name}.json").read_text())
        for m, v in nat.items():
            ch = f"content_{m}"
            if name == "NE38":
                rows.append(dict(period_unit=unit, goal_no=goal, channel=ch, statistic="ne38_opus5_chi_mem", estimate=v["chi_opus5"],
                                 ci_kind="none", n=v["N"], n_kind="agents", method="one-agent memory-form susceptibility at the reassignment boundary",
                                 null=f"others' 90th percentile {v['others_q90']:.3f}", role="native", source="data/processed/H97-quench-restoring-force/natives/NE38.json"))
            if name == "G44":
                rows.append(dict(period_unit=unit, goal_no=goal, channel=ch, statistic="g44_chi_best_minus_rest", estimate=v["diff"],
                                 ci_kind="none", n=v["N"], n_kind="agents", method="room difference in mean chi_mem (#42 last day -> #44 day 1)",
                                 null=f"room-label permutation p={v['p_perm']:.3f}", role="native", source="data/processed/H97-quench-restoring-force/natives/G44.json",
                                 notes="period_unit 44a holds day 1; pre-state is #42's last day"))
            if name == "G26":
                rows.append(dict(period_unit=unit, goal_no=goal, channel=ch, statistic="g26_memory_rho_across_announcement", estimate=v["rho_announcement"],
                                 ci_kind="none", n=v["N"], n_kind="agents", method="disattenuated memory across the leader's announcement (day 1)",
                                 null=f"clock-matched splits days 2-5, percentile {v['percentile_among_placebo']:.2f}", role="native",
                                 source="data/processed/H97-quench-restoring-force/natives/G26.json"))
    out = E.write_estimates(rows, hypothesis="H97")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
