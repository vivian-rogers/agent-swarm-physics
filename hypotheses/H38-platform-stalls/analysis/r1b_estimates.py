"""H38 round 1b: per-period estimates (fixed tables) into the shared per_period_estimates table (infra/shared/estimates.py).
Replication rows per goal period: excess gain raw (N1 null, whole-day grid) and trimmed (DQ8 null), f_scaffold, f_trim,
joint-silence share, for activity (and talk excess gains). Native row: the 2025-06-18 stop-and-restart day (#4d test).
NE14 / NE43 are transition designs (not single-period rows; see infra/data-quality/estimates_schema.md).
Usage: uv run python hypotheses/H38-platform-stalls/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R = ROOT / "data/processed/H38-platform-stalls/r1b"
SRC = "data/processed/H38-platform-stalls/r1b/period_table.parquet"
NOTE = "round 1b: activity_bins_fixed + shared outages_fixed"


def fin(x):
    return float(x) if x is not None and np.isfinite(x) else None


def main():
    d = pl.read_parquet(R / "period_table.parquet")
    rows = []
    for r in d.iter_rows(named=True):
        g = int(r["goal_no"]); pu = E.map_unit(g)
        base = {"period_unit": pu, "goal_no": g, "role": "replication", "source": SRC, "status": "ok", "notes": NOTE,
                "n": float(r["days"]), "n_kind": "days", "ci_kind": "none"}
        res = json.loads((R / f"G{g:02d}/result.json").read_text())
        A = (res.get("o4") or {}).get("active") or {}
        T = (res.get("o4") or {}).get("talk") or {}
        for ch, blk, pre in (("activity", A, ""), ("talk", T, "t")):
            for v, stat, null in (("raw", "excess_gain_raw", "N1 block shift within (day, 30-min block), whole-day grid"),
                                  ("trim", "excess_gain_trim", "block shift within (day, 30-min block) after trimming to the all-present window (DQ8)"),
                                  ("trim_scaffold", "excess_gain_trim_scaffold", "trimmed block shift (DQ8); scheduled minutes dropped, consolidation/infra agent-minutes imputed")):
                x = blk.get(v)
                if not x:
                    continue
                rows.append({**base, "statistic": stat, "channel": ch, "estimate": fin(x["E"]), "se": fin(x["null_sd"]),
                             "method": "g = 1 - 1/VR (30-min blocks, H02/H19 chunks and present population) minus the null mean; se = null SD",
                             "null": null, "notes": f"{NOTE}; z = {fin(x['z']):.2f}" if fin(x["z"]) is not None else NOTE})
        sig = (r["z_raw"] or 0) > 2
        for stat, col, meth in (("f_scaffold", "f_mask_scaffold", "1 - E_mask_scaffold / E_raw (agent-state conditioning; significant raw gain only)"),
                                ("f_trim", "f_trim", "1 - E_trim / E_raw (share of the excess removed by trimming before surrogates; significant raw gain only)")):
            if sig and r.get(col) is not None:
                rows.append({**base, "statistic": stat, "channel": "activity", "estimate": fin(r[col]), "method": meth, "null": "N1 / trimmed block shift"})
        rows.append({**base, "statistic": "joint_silence_share", "channel": "activity", "estimate": fin(r["js"]),
                     "method": "share of window minutes with <= 1 day-present agent active (n_present >= 3); outages_fixed rule",
                     "null": f"per-block Poisson-binomial independent expectation = {fin(r['js_exp'])}"})
    nat = json.loads((R / "native/native.json").read_text())["G04_0618"]
    rows.append({"period_unit": "local:2025-06-18", "unit_local": "4 (2025-06-18, #4d stop and restart)", "goal_no": 4,
                 "statistic": "excess_gain_raw_day", "channel": "activity", "estimate": fin(nat["day"]["E_raw"]),
                 "n": 1.0, "n_kind": "days", "ci_kind": "none",
                 "method": "one-day excess gain over the N1 null (200 surrogates); other G04 days' median " + str(round(nat["others_median"]["E_raw"], 3)),
                 "null": "N1 block shift", "role": "native", "source": "data/processed/H38-platform-stalls/r1b/native/native.json",
                 "status": "ok", "notes": NOTE + "; native #4d test (failed: no inflation from the 299-min stop)"})
    # drop this script's earlier rows (same source), then upsert
    old = E.read_estimates()
    if old.height:
        keep = old.filter(~((pl.col("hypothesis") == "H38") & pl.col("source").is_in([SRC, "data/processed/H38-platform-stalls/r1b/native/native.json"])))
        if keep.height != old.height:
            keep.write_parquet(E.PATH, compression="zstd")
    out = E.write_estimates([{k: v for k, v in x.items()} for x in rows], hypothesis="H38")
    print(out.height, "rows written;", out.group_by("statistic", "channel", "role").len().sort("statistic"))


if __name__ == "__main__":
    main()
