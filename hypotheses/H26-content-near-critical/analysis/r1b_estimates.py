"""H26 round 1b: per-unit loop gains in the shared schema (write_estimates): content, activity and talk room gains
(L3 two-room / L2 one-room) at day and w30 resolution with joint-day-bootstrap percentile CIs, for bge_fixed, gte_fixed
(content) and bge_fixed_trim (activity, talk); natives NE42 (pseudo-room excess) and G12 (motion on/off).
Usage: uv run python hypotheses/H26-content-near-critical/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H26-content-near-critical"
H01U = {u["unit"]: u for u in json.loads((ROOT / "data/processed/H01-emergent-superagents-exist/units.json").read_text())}
RUNS = {"bge_fixed": ("c", "a", "k"), "gte_fixed": ("c",), "bge_fixed_trim": ("a", "k")}
CH = {"c": "content", "a": "activity", "k": "talk"}


def fin(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


def pu(unit):
    u = H01U[unit]; g = int(u["goal_no"]); d0, d1 = u["days"][0], u["days"][-1]
    m = E.map_unit(g, d0, d1)
    return (m if m else f"local:{unit}"), g, d0, d1


def main():
    rows = []
    for run, chans in RUNS.items():
        src = f"data/processed/H26-content-near-critical/r1b/{run}/summary_units.json"
        for x in json.loads((D / "r1b" / run / "summary_units.json").read_text()):
            p, g, d0, d1 = pu(x["unit"])
            for ch in chans:
                for res in ("day", "w30"):
                    v = x.get(f"{ch}_{res}_g"); ci = x.get(f"{ch}_{res}_g_ci") or [None, None]
                    if not fin(v):
                        continue
                    lo, hi = (ci[0], ci[1]) if fin(ci[0]) and fin(ci[1]) else (None, None)
                    rows.append({"period_unit": p, "goal_no": g, "unit_local": x["unit"], "first_day": d0, "last_day": d1,
                                 "statistic": f"room_excess_gain_{res}" if x["two_room"] else f"room_gain_L2_{res}",
                                 "channel": CH[ch], "estimate": max(v, -1.0), "ci_lo": lo, "ci_hi": hi, "ci_level": 0.95,
                                 "ci_kind": "percentile", "n": float(x["n_days"]), "n_kind": "days",
                                 "method": f"round 1b ({run}): H26 equal-time loop gain g = 1 - 1/VR, split-half signal variance; "
                                           "activity_bins_fixed; DQ5 restatement dedupe; shared goal fields",
                                 "null": "N2 room permutation (anti-conservative under room drives, DQ8)", "role": "replication",
                                 "source": src, "notes": "clipped at -1"})
    N = json.loads((D / "r1b" / "native.json").read_text())
    for run in ("bge_fixed", "gte_fixed"):
        for u in ("39", "40", "41"):
            for key, v in N["NE42"][run][u].items():
                e = v["g_ex_pseudo"]
                if e is None or (isinstance(e, float) and math.isnan(e)):
                    continue
                ch, res = key.split("_")
                rows.append({"period_unit": E.map_unit(int(u)), "goal_no": int(u), "unit_local": u,
                             "statistic": f"ne42_pseudo_room_excess_{res}", "channel": CH[ch], "estimate": max(float(e), -1.0),
                             "ci_lo": v["ci_g_ex_pseudo"][0], "ci_hi": v["ci_g_ex_pseudo"][1], "ci_kind": "percentile",
                             "method": f"round 1b native ({run}): #39 partition as pseudo-rooms", "null": "day bootstrap",
                             "role": "native", "source": "data/processed/H26-content-near-critical/r1b/native.json",
                             "notes": "clipped at -1"})
    for t in ("bge_restate", "gte_restate"):
        for k in ("on", "off", "on_rm"):
            x = N["G12"][t][k]
            rows.append({"period_unit": E.map_unit(12, "2025-09-01", "2025-09-04") or "local:12a", "goal_no": 12, "unit_local": "12a",
                         "statistic": f"g12_room_gain_L2_{k}", "channel": "content", "estimate": x["g_room"],
                         "ci_lo": x["ci"][0], "ci_hi": x["ci"][1], "ci_kind": "percentile",
                         "method": f"round 1b native: 10-min slots, motion on/off ({t})", "null": "bootstrap over debates / days",
                         "role": "native", "source": "data/processed/H26-content-near-critical/r1b/native.json"})
    print("wrote", E.write_estimates(rows, hypothesis="H26").height)


if __name__ == "__main__":
    main()
