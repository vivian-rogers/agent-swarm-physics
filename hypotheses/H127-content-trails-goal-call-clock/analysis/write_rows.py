"""Write H127 per-period rows to the shared per_period_estimates table (write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h127lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

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
    k = L.tables()["k"]
    fday = dict(zip(k["design"].to_list(), k["first_day"].to_list()))
    src = "data/processed/H127-content-trails-goal-call-clock/NE34/kickoffs_all_configs.parquet"
    rows = []
    for r in d.iter_rows(named=True):
        base = dict(period_unit=unit_of(r["goal_no"], fday[r["design"]]), goal_no=r["goal_no"], channel=CHAN[r["cfg"]],
                    role="replication", source=src, first_day=fday[r["design"]], n_kind="agents")
        if r.get("n_fit") and r["n_fit"] >= 1 and r["s"] == r["s"]:
            ok = r.get("s_lo") is not None and r["s_lo"] == r["s_lo"]
            rows.append(dict(base, statistic="halftime_callrate_slope_s", estimate=r["s"], n=r["n_fit"],
                             ci_lo=r["s_lo"] if ok else None, ci_hi=r["s_hi"] if ok else None, ci_level=0.90 if ok else None,
                             ci_kind="percentile" if ok else "none",
                             method="Theil-Sen slope of log half-alignment time (hours from t0, free day-1 amplitude) on log day-1 call rate; agent bootstrap",
                             null="0 (hour clock); -1 call clock"))
        if r.get("imm_ro") is not None and r["imm_ro"] == r["imm_ro"]:
            rows.append(dict(base, statistic="readout_immediate_share", estimate=r["imm_ro"], n=r["n_rise"], ci_kind="none",
                             method="share of rising agents whose day-1 plateau is reached at the read-out call (fit at the 0.36-s grid floor)",
                             null="synthetic: <= 0.20 for relaxation worlds; 0.42-0.47 for a read-out jump"))
        if r.get("dsse_ro") is not None and r["dsse_ro"] == r["dsse_ro"]:
            rows.append(dict(base, statistic="clock_gain_dsse_readout", estimate=r["dsse_ro"], n=r["n_rise"], ci_kind="none",
                             method="(SSE_hours - SSE_calls)/(SSE_norise - min SSE), common tau from the read-out call", null="0"))
    for cfg in ("bge_white", "gte_white"):
        ne = json.loads((L.DATA / "natives/NE38.json").read_text())[cfg]
        rows.append(dict(period_unit=unit_of(51, "2026-07-29"), goal_no=51, channel=CHAN[cfg], statistic="ne38_opus5_halftime_h",
                         estimate=ne["opus5_TH"], ci_kind="none", n=1, n_kind="agents", role="native",
                         method="Opus 5 half time of its day-1 plateau (own new role) after the 07-29 16:51 UTC reassignment, hours",
                         null=f"call-clock prediction {ne['pred_call_clock_h']:.4f} h; hour-clock {ne['pred_hour_clock_h']:.4f} h",
                         source="data/processed/H127-content-trails-goal-call-clock/natives/NE38.json"))
        g = json.loads((L.DATA / "natives/G51.json").read_text())[cfg]
        rows.append(dict(period_unit=unit_of(51, "2026-07-06"), goal_no=51, channel=CHAN[cfg], statistic="g51_own_role_readout_immediate_share",
                         estimate=g["imm_ro"], ci_kind="none", n=g["n_rise"], n_kind="agents", role="native",
                         method="share of rising agents (own roles) at the read-out-call grid floor", null="synthetic <= 0.20 for relaxation",
                         source="data/processed/H127-content-trails-goal-call-clock/natives/G51.json"))
    out = E.write_estimates(rows, hypothesis="H127")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
