"""Write H119 per-week (NE42) and per-side (switch units) estimates to the shared per_period_estimates table."""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402
import h119lib as L  # noqa: E402
import run as RUN  # noqa: E402

D = ROOT / "data/processed/H119-room-merge-adjacency"
w = json.loads((D / "ne42_weeks.json").read_text())["contrasts"]
e2 = pl.read_parquet(D / "e2_ne42.parquet")
rows = []
for wk, days in L.NE42_WEEKS.items():
    base = {"period_unit": wk, "goal_no": int(wk), "first_day": days[0], "last_day": days[-1], "role": "native",
            "channel": "talk", "n_kind": "agents", "n": 11.0, "ci_level": 0.95, "ci_kind": "se_z", "post_hoc": False}
    for cls, k in (("within", "Jw"), ("cross", "Jx")):
        est, se = w[f"{k}_{wk}"], w[f"se_{cls}_{wk}"]
        rows.append({**base, "statistic": f"ki5_class_J_{cls}", "estimate": est, "se": se, "ci_lo": est - 1.96 * se,
                     "ci_hi": est + 1.96 * se, "source": "data/processed/H119-room-merge-adjacency/ne42_weeks.json",
                     "method": "E1 KI-5 class model (per-pair J shared by NE42 pair class), recipient block fields, lam 1, cluster-robust SE",
                     "null": "relabel of the 4-vs-7 partition (secondary)"})
        r = e2.filter(pl.col("week") == wk).to_dicts()[0]
        if r[f"CRU_{cls}"] is not None and np.isfinite(r[f"CRU_{cls}"]):
            e, lo, hi = r[f"CRU_{cls}"], r[f"CRU_{cls}_lo"], r[f"CRU_{cls}_hi"]
            rows.append({**base, "statistic": f"e2_read_minus_inflight_{cls}", "estimate": e, "ci_lo": lo, "ci_hi": hi,
                         "se": (hi - lo) / (2 * 1.96), "source": "data/processed/H119-room-merge-adjacency/e2_ne42.parquet",
                         "method": "E2 pooled call-level logit: J^R (visible, [t_call-L,t_call)) minus J^U (posted in [t_call,t_call+L)) per pair class, recipient block fields, Wald CI",
                         "null": "J^U (posted-but-unread, matched window)"})
sw = pl.read_parquet(D / "switch_units.parquet")
for r in sw.iter_rows(named=True):
    bef, aft, folder, g = RUN.SWITCHES[r["name"]]
    for arm, days in (("on", aft), ("off", bef)):
        if r.get(f"e2_{arm}_CRU") is None or not np.isfinite(r[f"e2_{arm}_CRU"]):
            continue
        gg = int(pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").filter(pl.col("pt_date") == days[0])["goal_no"][0])
        e, lo, hi = r[f"e2_{arm}_CRU"], r[f"e2_{arm}_CRU_lo"], r[f"e2_{arm}_CRU_hi"]
        rows.append({"period_unit": f"local:{r['name']}_{'after' if arm == 'on' else 'before'}", "unit_local": r["name"],
                     "goal_no": gg, "first_day": days[0], "last_day": days[-1], "role": "replication", "channel": "talk",
                     "statistic": "e2_read_minus_inflight_switched_pairs", "estimate": e, "ci_lo": lo, "ci_hi": hi,
                     "se": (hi - lo) / 3.92, "ci_level": 0.95, "ci_kind": "se_z", "n": float(r["n_agents"]), "n_kind": "agents",
                     "method": "E2 pooled call-level logit for the switched pair class on the side where it shares a room",
                     "null": "J^U (posted-but-unread, matched window)", "post_hoc": False,
                     "source": "data/processed/H119-room-merge-adjacency/switch_units.parquet"})
E.write_estimates(rows, hypothesis="H119")
print(len(rows), "rows")
