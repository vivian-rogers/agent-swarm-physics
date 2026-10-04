"""Write H117 per-side estimates (each side lies inside one period unit) to the shared per_period_estimates table."""
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as RUN  # noqa: E402
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H117-coupling-invariant-rule-reset"
df = pl.read_parquet(D / "splits.parquet")
rows = []
for nm, (bef, aft, reg, role, folder, goal) in {**RUN.STEPS, **RUN.STEPS_K3}.items():
    f = D / "J" / f"{nm}.npz"
    if not f.exists():
        continue
    z = np.load(f)
    r = df.filter(pl.col("name") == nm).to_dicts()[0]
    iu = np.triu_indices(len(z["agents"]), 1)
    m = z["fixed"][iu]
    for side, days, J, SE, h in (("before", bef, z["Jb"], z["SEb"], z["hb"]), ("after", aft, z["Ja"], z["SEa"], z["ha"])):
        Js = ((J + J.T) / 2)[iu][m]; Vs = ((SE ** 2 + SE.T ** 2) / 4)[iu][m]
        g = int(pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").filter(pl.col("pt_date") == days[0])["goal_no"][0])
        unit = E.map_unit(g, days[0], days[-1]) if hasattr(E, "map_unit") else None
        base = {"period_unit": unit or f"local:{nm}_{side}", "unit_local": f"{nm}_{side}", "goal_no": g,
                "first_day": days[0], "last_day": days[-1], "role": role, "channel": "talk",
                "source": f"data/processed/H117-coupling-invariant-rule-reset/J/{nm}.npz"}
        se = float(np.sqrt(Vs.sum()) / max(len(Js), 1))
        rows.append({**base, "statistic": "ki5_block_Jsym_mean_fixed_pairs", "estimate": float(Js.mean()),
                     "ci_lo": float(Js.mean() - 1.96 * se), "ci_hi": float(Js.mean() + 1.96 * se), "se": se,
                     "ci_level": 0.95, "ci_kind": "se_z", "n": float(len(Js)), "n_kind": "pairs",
                     "method": f"E1 KI-5 talk spins, per-(day,30-min) block fields, lam 1, cluster-robust SE floored by model SE; k={len(days)} days",
                     "null": "placebo day-boundary splits (same regime, k days)", "post_hoc": False})
        if r.get(f"JRmJU_{side[0]}") is not None and np.isfinite(r[f"JRmJU_{side[0]}"]):
            e, s_ = r[f"JRmJU_{side[0]}"], r[f"JRmJU_se_{side[0]}"]
            rows.append({**base, "statistic": "e2_read_minus_inflight_per_recipient", "estimate": float(e),
                         "ci_lo": float(e - 1.96 * s_), "ci_hi": float(e + 1.96 * s_), "se": float(s_), "ci_level": 0.95,
                         "ci_kind": "se_z", "n": float(r["n_R"]), "n_kind": "agents",
                         "method": "E2 per-recipient logit on ledger calls: J^R (visible, [t_call-L,t_call)) minus J^U (same-room in-flight, [t_call,t_call+L)); mean over recipients, SE across recipients",
                         "null": "J^U (posted-but-unread at matched window length)", "post_hoc": False})
E.write_estimates(rows, hypothesis="H117")
print(len(rows), "rows")
