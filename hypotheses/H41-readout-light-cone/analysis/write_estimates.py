"""H41 per-period rows for the shared estimates table (infra/shared/estimates.py, DQ8).

  uv run python hypotheses/H41-readout-light-cone/analysis/write_estimates.py

Reads results/period_table.parquet and results/native.json (round 1b: room-index fix, 2026-10-04) and upserts every
period's rows. write_estimates replaces all earlier H41 rows with the same (statistic, channel, method, role, source),
so every period is re-emitted here, not only the periods the fix changed. Non-holdout periods only (the table holds no
held-out data); write_estimates refuses held-out rows anyway.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

RES = ROOT / "data/processed/H41-readout-light-cone/results"
SRC_T = "data/processed/H41-readout-light-cone/results/period_table.parquet"
SRC_N = "data/processed/H41-readout-light-cone/results/native.json"
NATIVE = {31, 38, 51}
NOTE_1B = "round 1b: room index keeps open rooms_timeline segments (2026-10-04)"


def num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def rows_for(r: dict) -> list[dict]:
    g = int(r["goal"])
    base = dict(period_unit=E.map_unit(g), goal_no=g, role="native" if g in NATIVE else "replication",
                ci_level=0.95, confirmatory=False, source=SRC_T)
    out = []

    def add(stat, channel, est, lo, hi, n, n_kind, method, null, ci_kind="percentile", post_hoc=False, notes=None):
        if num(est) is None and notes is None:
            return
        d = dict(base, statistic=stat, channel=channel, estimate=num(est), ci_lo=num(lo), ci_hi=num(hi), n=num(n),
                 n_kind=n_kind, method=method, null=null, ci_kind=ci_kind, post_hoc=post_hoc,
                 notes=(notes + "; " if notes else "") + NOTE_1B)
        if d["ci_lo"] is None or d["ci_hi"] is None:
            d["ci_lo"] = d["ci_hi"] = None
        out.append(d)

    add("acausal_share_robust", "adoption", r.get("acaus_rob"), r.get("acaus_rob_ci_lo"), r.get("acaus_rob_ci_hi"),
        r.get("n_adopt"), "adoptions", "logged light cone, lenient timing, day bootstrap", "0 under pure logged relay")
    add("acausal_share_robust_within_room", "adoption", r.get("acaus_rob_within"), None, None, r.get("n_adopt"),
        "adoptions", "logged light cone, lenient timing", "0 under pure logged relay", ci_kind="none")
    if (r.get("share_cross") or 0) > 0:
        n_cross = round((r.get("share_cross") or 0) * (r.get("n_adopt") or 0))
        add("acausal_share_robust_cross_room", "adoption", r.get("acaus_rob_cross"), None, None, n_cross,
            "cross-room adoptions", "logged light cone, lenient timing; adopter's known room at t0 differs from the "
            "source room", "0 under pure logged relay; ~0.07-0.09 for two-room relay with a weak field (synthetic)",
            ci_kind="none")
    if r.get("b") is not None:
        add("cadence_elasticity_b", "hop_delay", r.get("b"), r.get("b_ci_lo"), r.get("b_ci_hi"), r.get("n_reg"),
            "hop events", "log dt_hop ~ log tau_c + log volume, agent FE, day bootstrap",
            "read-out gating: 1; volume model: 0")
    add("cycles_per_hop_median", "receiving_calls", r.get("cyc_med"), None, None, r.get("n_hops"), "hop events",
        "median receiving calls from first item exposure to use", "none", ci_kind="none")
    add("talk_calls_per_hop_median", "talk_calls", r.get("talk_med"), None, None, r.get("n_hops"), "hop events",
        "median talk calls from first item exposure to use", "none", ci_kind="none")
    jmh = r.get("J_mh")
    add("jump_inflight_vs_entry_delay_matched", "talk_adoption", jmh, r.get("J_mh_lo"), r.get("J_mh_hi"),
        r.get("risk_pre_in"), "in-flight at-risk talk calls", "Mantel-Haenszel over delay-since-t0 bins, day bootstrap B=300",
        "1 (shared field; synthetic 0.8-1.2)", post_hoc=True,
        notes="A6 post hoc; inf (no in-flight adoptions at matched delay) stored as null")
    add("jump_inflight_vs_entry_unmatched", "talk_adoption", r.get("J_in"), r.get("J_in_ci_lo"), r.get("J_in_ci_hi"),
        r.get("risk_pre_in"), "in-flight at-risk talk calls", "Haldane hazard ratio, day bootstrap B=500",
        "1 (shared field / room exposure)", notes="pre-registered J_in (rule A4)")
    return out


def main():
    tab = pl.read_parquet(RES / "period_table.parquet")
    nat = json.loads((RES / "native.json").read_text())
    rows = []
    for r in tab.iter_rows(named=True):
        rows += rows_for(r)
    for g in (39, 40, 41):
        x = nat["NE42"][f"G{g}"]
        lo, hi = (x.get("ratio_ci") or [None, None])
        rows.append(dict(period_unit=E.map_unit(g), goal_no=g, statistic="cross_group_hazard_ratio_NE42",
                         channel="talk_adoption", estimate=num(x.get("ratio_cross_within")), ci_lo=num(lo), ci_hi=num(hi),
                         ci_level=0.95, ci_kind="percentile", n=num(x.get("risk_cross")),
                         n_kind="cross-group at-risk talk calls",
                         method="hazard per talk call within 2 h, cross/within group (#39 partition), day bootstrap",
                         null="1 (no cage)", role="native", confirmatory=False, post_hoc=False, source=SRC_N,
                         notes=NOTE_1B + "; unaffected (partition from the full rooms_timeline)"))
    x = nat["G38"]
    lo, hi = x.get("b_ratio_ci") or [None, None]
    rows.append(dict(period_unit=E.map_unit(38), goal_no=38, statistic="cross_room_hazard_ratio_cage",
                     channel="talk_adoption", estimate=num(x.get("b_ratio")), ci_lo=num(lo), ci_hi=num(hi), ci_level=0.95,
                     ci_kind="percentile", n=num(x.get("n_cross")), n_kind="cross-room adoptions",
                     method="hazard per at-risk talk call within 2 h, other room / source room at t0, day bootstrap",
                     null="1 (no cage)", role="native", confirmatory=False, post_hoc=False, source=SRC_N, notes=NOTE_1B))
    x = nat["G51"]
    if x.get("n_focus_cross"):
        rows.append(dict(period_unit=E.map_unit(51), goal_no=51, statistic="focus_cross_room_in_cone_share",
                         channel="adoption", estimate=num(x.get("b_focus_cross_incone")), ci_lo=None, ci_hi=None,
                         ci_level=0.95, ci_kind="none", n=num(x.get("n_focus_cross")), n_kind="cross-room adoptions",
                         method="#general <-> #focus adoptions inside the logged light cone (best estimate)",
                         null="G38 cage: 0", role="native", confirmatory=False, post_hoc=False, source=SRC_N,
                         notes=NOTE_1B))
    df = E.write_estimates(rows, hypothesis="H41")
    print(f"wrote {df.height} H41 rows; statistics: {sorted(set(df['statistic'].to_list()))}")


if __name__ == "__main__":
    main()
