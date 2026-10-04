"""Write H65 per-period rows to the shared per_period_estimates table.

    uv run python hypotheses/H65-leaders-are-routers/analysis/estimates_rows.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H65-leaders-are-routers"


def pu_id(goal: int, unit: str) -> str:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").filter(pl.col("goal_no") == goal)
    if unit and not unit.isdigit():
        return unit
    return str(goal) if pu.height == 1 else f"G{goal:02d}"


def fin(x):
    return None if x is None or not np.isfinite(x) else float(x)


def main():
    rows = []
    for model in ("bge_small", "gte_modernbert", "style"):
        src = f"data/processed/H65-leaders-are-routers/replication/{model}/periods.json"
        for r in json.loads((ROOT / src).read_text()):
            base = {"period_unit": pu_id(r["goal"], r["unit"]), "goal_no": r["goal"], "role": "replication",
                    "source": src, "post_hoc": False, "channel": "content", "n": r["n_agents"], "n_kind": "agents"}
            ci = r.get("D_ci") or [None, None]
            rows.append({**base, "statistic": "router_alignment_D", "estimate": fin(r["D"]), "ci_lo": ci[0],
                         "ci_hi": ci[1], "method": f"H65.rglr_{model}", "null": "block_bootstrap",
                         "ci_kind": "percentile" if ci[0] is not None else "none"})
            ci = r.get("rho_RO_chi_ci") or [None, None]
            rows.append({**base, "statistic": "rho_replyout_inflow", "estimate": fin(r["rho_RO_chi"]), "ci_lo": ci[0],
                         "ci_hi": ci[1], "method": f"H65.rglr_{model}", "null": "block_bootstrap",
                         "ci_kind": "percentile" if ci[0] is not None else "none"})
            rows.append({**base, "statistic": "unread_over_read_response", "estimate": fin(r["lam_over_chi_median"]),
                         "ci_lo": None, "ci_hi": None, "method": f"H65.rglr_{model}", "null": "none",
                         "ci_kind": "none", "notes": "median over agents of lambda/chi"})
            rows.append({**base, "statistic": "inflow_chi_median", "estimate": fin(r["chi_median"]), "ci_lo": None,
                         "ci_hi": None, "method": f"H65.rglr_{model}", "null": "none", "ci_kind": "none"})
        for name, goal in (("G26", 26), ("G44", 44), ("G35", 35), ("G12", 12)):
            p = DATA / f"natives/{model}/{name}.json"
            if not p.exists():
                continue
            r = json.loads(p.read_text())
            base = {"period_unit": pu_id(goal, ""), "goal_no": goal, "role": "native", "post_hoc": False,
                    "source": str(p.relative_to(ROOT)), "channel": "content", "method": f"H65.rglr_{model}"}
            if name in ("G26", "G44"):
                ci = r["router_index_ci"]
                rows.append({**base, "statistic": "leader_router_index", "estimate": fin(r["router_index"]),
                             "ci_lo": ci[0], "ci_hi": ci[1], "ci_kind": "percentile", "n": r["n_agents"],
                             "n_kind": "agents", "null": "skeleton_synthetic_null",
                             "notes": f"pct chi {r['pct_chi']:.2f}, pct kappa {r['pct_kappa']:.2f}, p_syn {r.get('p_syn', float('nan')):.3f}"})
            else:
                for m in ("chi", "kappa", "RI", "BO"):
                    x = r[m]
                    rows.append({**base, "statistic": f"role_contrast_{m}", "estimate": fin(x["beta"]), "ci_lo": None,
                                 "ci_hi": None, "ci_kind": "none", "n": x["n"], "n_kind": "agent-windows",
                                 "channel": "content" if m in ("chi", "kappa") else "reply",
                                 "null": "role_permutation", "notes": f"p_greater {x['p_greater']:.4f}, p_less {x['p_less']:.4f}"})
    E.write_estimates(rows, hypothesis="H65")
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
