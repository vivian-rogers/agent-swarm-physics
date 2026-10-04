"""H01 round 1b: per-unit estimates of the round-1 (D3.1.a / D3.2) statistics in the shared schema (write_estimates).

Rows per H01 unit and instrument (bge_restate, gte_restate): P1 room-order median dH, P6 exposure slope (se_z CI),
P6 within-minus-cross residual cosine, P9 betaJ0/n (upper bound). Natives: G12 team excess T, NE42 old-partition dH.
Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import OUT, ROOT  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

UNITS = {u["unit"]: u for u in json.loads((OUT / "units.json").read_text())}
TAGS = {"bge_restate": "bge_small", "gte_restate": "gte_modernbert"}


def pu(unit):
    u = UNITS.get(unit)
    if u is None:
        return f"local:{unit}", None, None, None
    g = int(u["goal_no"]); d0, d1 = u["days"][0], u["days"][-1]
    m = E.map_unit(g, d0, d1)
    return (m if m else f"local:{unit}"), g, d0, d1


def main():
    C = json.loads((OUT / "r1b" / "compare.json").read_text())
    N = json.loads((OUT / "r1b" / "native.json").read_text())
    rows = []
    for tag, model in TAGS.items():
        r = C[tag]
        meth = f"round 1b: H01 per-regime whitening d32, shared goal fields, restatements removed (DQ5, chat); {model}"
        src = f"data/processed/H01-emergent-superagents-exist/r1b/{tag}/explore.json"
        base = dict(method=meth, source=src, role="replication", notes=f"embedding {model}")
        for unit, v in r["per_unit_P1"].items():
            if v is None:
                continue
            p, g, d0, d1 = pu(unit)
            rows.append({**base, "period_unit": p, "goal_no": g, "unit_local": unit, "first_day": d0, "last_day": d1,
                         "statistic": "room_order_dH_median", "channel": "content", "estimate": v, "ci_kind": "none",
                         "null": "1,000 size-keeping room-label permutations per day"})
        for unit, (b, se) in r["per_unit_slope"].items():
            if b is None:
                continue
            p, g, d0, d1 = pu(unit)
            lo, hi = E.ci_from_se(b, se)
            rows.append({**base, "period_unit": p, "goal_no": g, "unit_local": unit, "first_day": d0, "last_day": d1,
                         "statistic": "exposure_coupling_slope", "channel": "content", "estimate": b, "se": se, "ci_lo": lo,
                         "ci_hi": hi, "ci_level": 0.95, "ci_kind": "se_z", "null": "rotation and day-shuffle nulls (pooled)"})
        for unit, v in r["P6_wc"].items():
            p, g, d0, d1 = pu(unit)
            rows.append({**base, "period_unit": p, "goal_no": g, "unit_local": unit, "first_day": d0, "last_day": d1,
                         "statistic": "within_minus_cross_residual_cos", "channel": "content", "estimate": v, "ci_kind": "none",
                         "null": "agent-level room-label permutation (anti-conservative under room drives, DQ8)"})
        for unit, v in r["per_unit_P9"].items():
            if v is None:
                continue
            p, g, d0, d1 = pu(unit)
            rows.append({**base, "period_unit": p, "goal_no": g, "unit_local": unit, "first_day": d0, "last_day": d1,
                         "statistic": "mf_bJ0_over_n_upper_bound", "channel": "content", "estimate": v, "ci_kind": "none",
                         "null": "day-shuffle; drive-confounded upper bound (H26)"})
        g12 = N["G12"][tag]["raw"]
        rows.append({**base, "role": "native", "period_unit": E.map_unit(12, "2025-09-01", "2025-09-04") or "local:12a",
                     "goal_no": 12, "unit_local": "12a", "statistic": "team_excess_cos_T", "channel": "content",
                     "estimate": g12["T"], "ci_kind": "none", "n": float(g12["n_debates"]), "n_kind": "debates",
                     "null": f"exact team re-partitions per debate; p = {g12['p']:.3f}",
                     "source": "data/processed/H01-emergent-superagents-exist/r1b/native.json"})
        for u in ("39", "40", "41"):
            x = N["NE42"][tag][u]
            rows.append({**base, "role": "native", "period_unit": E.map_unit(int(u)), "goal_no": int(u), "unit_local": u,
                         "statistic": "ne42_old_partition_dH_median", "channel": "content", "estimate": x["p1_median_dH"],
                         "ci_kind": "none", "null": "size-keeping label permutations",
                         "source": "data/processed/H01-emergent-superagents-exist/r1b/native.json"})
    print("wrote", E.write_estimates(rows, hypothesis="H01").height)


if __name__ == "__main__":
    main()
