"""H36 round 2 (2026-10-05): per-period estimates in the shared schema (infra/shared/estimates.py: write_estimates).

Replication rows, one per non-holdout goal period with a scored kickoff:
  r2_intraday_r1w_kickoff_first2_max   max intraday topic-shift z in the first two 30-min windows of day 0 (bge, gte)
  r2_C3_kickoff_window_max             frozen C3 score (R1 - 1 or Z_cont; alarm >= 2) on days -1..+1 (bge, gte; restate)
  r2_Zactinv_kickoff_window_max        sampling-invariant activity score on days -1..+1
Native rows: intraday z at the room events (#focus 08-05 -> G51; merge 05-04 -> G40; split 05-11 -> G41; side-room
07-24 -> its period) and the scaffold detector z_R5 at NE14b (03-24, #36) and NE45 (07-29, #51).
ci_kind none (single-day or single-window z-scores).

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r2_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2 = L.OUT / "r2"
SRCD = "data/processed/H36-reorganization-alarm/r2/"


def row(g, stat, ch, est, n, n_kind, meth, null, role, src, unit_local, first_day=None, notes=None):
    return {"period_unit": E.map_unit(g), "goal_no": g, "statistic": stat, "channel": ch, "estimate": float(est),
            "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": float(n), "n_kind": n_kind, "method": meth, "null": null,
            "role": role, "source": src, "unit_local": unit_local, "first_day": first_day, "notes": notes}


def main():
    rows = []
    # intraday
    for tag in ("bge", "gte"):
        o = json.loads((R2 / f"intraday_{tag}.json").read_text())
        meth = (f"round 2 R2: 30-min swarm content centroid shift vs the previous 4 scored windows, robust z vs the previous "
                f"16 windows; {tag}, restatements removed; alarm z >= 3")
        for k in o["kickoffs"]:
            g = int(k["ref"][1:])
            v = [k["z_by_win"].get(str(w), k["z_by_win"].get(w)) for w in (0, 1)]
            v = [x for x in v if x is not None]
            if not v:
                continue
            rows.append(row(g, "r2_intraday_r1w_kickoff_first2_max", "content", max(v), len(v), "scored windows",
                            meth, "placebo days' first two windows", "replication", SRCD + f"intraday_{tag}.json", f"G{g:02d}",
                            k["pt_date0"], f"embedding {tag}; first alarm window {k['first_alarm_win']}"))
        for name, rec in o["rooms"].items():
            if "z_near" not in rec:
                continue
            g = {"focus_0805": 51, "merge_0504": 40, "split_0511": 41, "side_room_0724": 51}[name]
            zs = [x for x in rec["z_near"].values() if x is not None]
            if not zs:
                continue
            gg = int(pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date") == rec["t"][:10])["goal_no"][0])
            if L.holdout_mask([rec["t"][:10]], [gg])[0]:
                continue
            rows.append(row(gg, f"r2_native_{name}_r1w_max_within1", "content", max(zs), len(zs), "windows within 1 of the event",
                            meth, "per-window placebo FAR", "native", SRCD + f"intraday_{tag}.json", name, rec["t"][:10],
                            f"embedding {tag}; event window {rec['win_of_event']} ({rec['kind']})"))
    # C3 (round-2 seed, restate) and Z_act_inv per kickoff window
    inv = pl.read_parquet(R2 / "activity_inv.parquet").sort("aday")
    zi = dict(zip(inv["aday"].to_list(), inv["Z_act_inv"].to_list()))
    for tag in ("bge", "gte"):
        et = pl.read_parquet(R2 / f"rob_{tag}_restate" / "event_table.parquet").filter(pl.col("cls") == "goal")
        meth = f"round 2 robustness: frozen C3 (R1 >= 3 or Z_cont >= 2); {tag}, restatements removed, round-2 surrogate seed"
        for r in et.filter(pl.col("n_scored") > 0).iter_rows(named=True):
            g = int(r["ref"][1:]); v = r["C3_wmax"]
            if v is None or not np.isfinite(v):
                continue
            rows.append(row(g, "r2_C3_kickoff_window_max", "content", v, r["n_scored"], "scored days in window", meth,
                            "trailing 10-day baseline; alarm at >= 2.0", "replication",
                            SRCD + f"rob_{tag}_restate/event_table.parquet", f"G{g:02d}", r["pt_date0"], f"embedding {tag}"))
            if tag == "bge":
                vals = [zi.get(r["aday0"] + o) for o in (-1, 0, 1)]
                vals = [x for x in vals if x is not None and np.isfinite(x)]
                if vals:
                    rows.append(row(g, "r2_Zactinv_kickoff_window_max", "activity", max(vals), len(vals), "scored days in window",
                                    "round 2 R3: activity members on 4-agent subsets (20) in 120-min blocks of the all-present "
                                    "window, 10 surrogates each; trailing z", "trailing 10-day baseline; alarm at >= 2.0",
                                    "replication", SRCD + "activity_inv.parquet", f"G{g:02d}", r["pt_date0"]))
    # scaffold detector at named platform days
    sd = pl.read_parquet(R2 / "scaffold_days.parquet")
    for name, d, g in (("NE14b", "2026-03-24", 36), ("NE45", "2026-07-29", 51), ("NE17", "2026-04-14", 38)):
        rr = sd.filter(pl.col("pt_date") == d)
        if rr.height and rr["R5"][0] is not None and np.isfinite(rr["R5"][0]):
            rows.append(row(g, f"r2_native_{name}_zR5", "action mix", rr["R5"][0], 1, "day",
                            "round 2 R5: median within-agent u of tool mix, bash grammar, context-boundary rate; trailing z; "
                            "z_R5 = max(tool, bash, |bnd|)", "alarm at z_R5 >= 4; H74 placebo days", "native",
                            SRCD + "scaffold_days.parquet", name, d,
                            f"tool {rr['tool'][0]:.2f}, bash {rr['bash'][0] if rr['bash'][0] is not None else float('nan'):.2f}, "
                            f"schema S {rr['S'][0]:.0f}"))
    out = E.write_estimates(rows, hypothesis="H36")
    print("wrote", out.height, "rows")


if __name__ == "__main__":
    main()
