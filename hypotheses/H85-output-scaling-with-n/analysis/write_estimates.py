"""Write H85 per-unit rows to the shared per_period_estimates table (infra/shared/estimates.py).

Replication rows (one per non-holdout unit): active population N, per-agent-hour output rates (msg, ment, reply,
commit), addressing per message, reply-parent share, mean pending set at talk calls. The cross-unit exponents beta are
comparisons of units (phase-diagram slopes), not per-period fits, so they are not written here (card and report only).
Native rows: within-period room-size contrasts (G36, G38, G42, G44; day-bootstrap CIs) and the G51 day-level sweep.
NE42 spans three goal periods (a transition design) and is not written.
Usage: uv run python hypotheses/H85-output-scaling-with-n/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h85lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra" / "shared"))
import estimates as E  # noqa: E402

UNITS = "data/processed/H85-output-scaling-with-n/units.parquet"
NAT = "data/processed/H85-output-scaling-with-n/natives/natives.json"


def nz(x):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else float(x)


def main():
    u = pl.read_parquet(L.ROOT / UNITS)
    rows = []
    for r in u.iter_rows(named=True):
        base = {"period_unit": r["unit_id"], "goal_no": r["goal_no"], "role": "replication", "source": UNITS,
                "first_day": r["first_day"], "last_day": r["last_day"], "ci_kind": "none", "null": None}
        NT = r["N"] * r["T_h"]
        rows.append({**base, "statistic": "active_population_N", "channel": "population", "estimate": r["N"],
                     "n": r["n_daysw"], "n_kind": "days",
                     "method": "hour-weighted mean over unit days of agents with >= 1 record (activity_bins_fixed)"})
        for k in ("msg", "ment", "reply", "commit"):
            if k == "commit" and not r["git_dense"]:
                continue
            rows.append({**base, "statistic": "output_rate_per_agent_hour", "channel": k, "estimate": r[k] / NT,
                         "n": r["T_h"], "n_kind": "scheduled hours",
                         "method": "unit total / (N x scheduled window hours); msg chat_core, ment addressed pairs "
                                   "(mentions_roster), reply DQ2 agent parents, commit DQ4 agent work",
                         "notes": f"total {r[k]}"})
        if r["msg"] > 0:
            rows.append({**base, "statistic": "addressed_pairs_per_message", "channel": "talk", "estimate": r["ment"] / r["msg"],
                         "n": r["msg"], "n_kind": "messages", "method": "sum |mentions_roster minus sender| / agent messages"})
            rows.append({**base, "statistic": "reply_parent_share", "channel": "talk", "estimate": r["reply"] / r["msg"],
                         "n": r["msg"], "n_kind": "messages", "method": "DQ2 parent & cand & agent parent / agent messages"})
        if r["k_n"] > 0:
            rows.append({**base, "statistic": "pending_set_k_talk", "channel": "talk", "estimate": r["k_talk"],
                         "n": r["k_n"], "n_kind": "talk calls", "method": "mean context_ledger_turns.k_since_talk at talk calls"})
    nat = json.loads((L.ROOT / NAT).read_text())
    for g, v in nat["rooms"].items():
        if not g.startswith("G"):
            continue
        gn = int(g[1:])
        for k in ("msg", "ment", "ment_per_msg", "k_talk"):
            x = v[k]
            rows.append({"period_unit": g, "goal_no": gn, "role": "native", "source": NAT, "statistic": "room_size_exponent",
                         "channel": k, "estimate": nz(x["est"]), "ci_lo": nz(x["ci"][0]), "ci_hi": nz(x["ci"][1]),
                         "ci_level": 0.95, "ci_kind": "percentile", "n": v["n_days"], "n_kind": "days",
                         "method": "within-day contrast of rooms 2 vs 3: slope through origin of dlnY on dlnN_room; day bootstrap",
                         "null": None, "status": "ok" if v["identified"] else "underpowered",
                         "notes": f"SD of within-day dlnN {v['sd_dlnN']:.3f}; no room fixed effect"})
    m = nat["G51"]["main"]
    for k in ("msg", "ment", "reply", "commit", "ment_per_msg", "k"):
        rows.append({"period_unit": "G51", "goal_no": 51, "role": "native", "source": NAT, "statistic": "day_sweep_exponent",
                     "channel": k, "estimate": nz(m[k]["est"]), "ci_lo": nz(m[k]["ci"][0]), "ci_hi": nz(m[k]["ci"][1]),
                     "ci_level": 0.95, "ci_kind": "percentile", "n": nat["G51"]["n_days"], "n_kind": "days",
                     "method": "day-level ln(Y/h) on ln n_d with NE43 step dummies (08-05, 08-21); unit-cluster bootstrap",
                     "null": None, "status": "underpowered", "notes": f"SD ln n_d {nat['G51']['sd_lnn']:.3f}; non-holdout days only"})
    out = E.write_estimates(rows, hypothesis="H85")
    print(f"wrote {out.height} rows")


if __name__ == "__main__":
    main()
