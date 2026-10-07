"""Write H137 round-1 rows to per_period_estimates (descriptive: S0 failed, so no row is a powered test).
Usage: uv run python hypotheses/H137-nonreciprocal-potts-named-pairs/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h137lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

NOTE = "descriptive: S0 failed (pooled synthetic power 0.18 at J=1); A1/A2/A3 amended estimators"


def f(x):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else float(x)


def main():
    U = pl.read_parquet(L.D / "results/units.parquet").filter(pl.col("testable"))
    R = json.loads((L.D / "results/round1.json").read_text())
    rows = []
    for r in U.iter_rows(named=True):
        base = {"period_unit": r["unit"], "goal_no": r["goal_no"], "channel": "project_follow", "role": "replication",
                "ci_kind": "percentile", "ci_level": 0.95, "notes": NOTE, "source": "results/units.parquet"}
        rows.append({**base, "statistic": "h137_theta_name", "estimate": f(r["theta_act"]), "ci_lo": f(r["theta_act_lo"]),
                     "ci_hi": f(r["theta_act_hi"]), "n": r["n_rows_z"], "n_kind": "follow-hop rows in one-way pairs",
                     "method": "weighted logit, pop+indeg+propensity controls (A1), pair bootstrap",
                     "null": f"N2 class permutation within popularity strata p={r['theta_act_p']:.3f}"})
        for c, st in (("one", "h137_pair_ep_oneway"), ("none", "h137_pair_ep_none")):
            if r.get(f"sig_{c}") is None:
                continue
            rows.append({**base, "statistic": st, "estimate": f(r[f"sig_{c}"]), "ci_lo": f(r[f"sig_{c}_lo"]),
                         "ci_hi": f(r[f"sig_{c}_hi"]), "n": r[f"sig_{c}_n"], "n_kind": "pairs with a follow hop",
                         "method": "Schnakenberg pair term, class mean, pair bootstrap",
                         "null": f"N1b propensity-adjusted direction null p={r[f'sig_{c}_p_adj']:.3f}"
                         if r.get(f"sig_{c}_p_adj") is not None else "N1b"})
        if r.get("o4") is not None:
            rows.append({**base, "statistic": "h137_follow_read_vs_inflight", "estimate": f(r["o4"]), "ci_lo": f(r["o4_lo"]),
                         "ci_hi": f(r["o4_hi"]), "n": r["o4_n_read"] + r["o4_n_if"], "n_kind": "(call, sender) rows",
                         "method": "follow rate after read named minus after in-flight named, agent-day bootstrap",
                         "null": "in-flight placebo (matched lag)"})
    n1 = R["natives"]["N1_G51"]["theta_act"]
    rows.append({"period_unit": "G51", "goal_no": 51, "channel": "project_follow", "role": "native", "statistic": "h137_theta_name",
                 "estimate": f(n1["est"]), "ci_lo": f(n1["lo"]), "ci_hi": f(n1["hi"]), "ci_kind": "percentile", "ci_level": 0.95,
                 "n": R["natives"]["N1_G51"]["n_rows_z"], "n_kind": "follow-hop rows in one-way pairs",
                 "method": "N1 native: 51a-51l pooled, A1 logit, pair bootstrap within unit",
                 "null": f"N2 p={n1['p_n2']:.3f}", "notes": NOTE, "source": "results/round1.json"})
    g38 = R["natives"].get("N2_G38", {})
    for part in ("same_room", "cross_room"):
        d = g38.get(part, {}).get("theta_act")
        if d and d.get("est") is not None:
            rows.append({"period_unit": "G38", "goal_no": 38, "channel": f"project_follow_{part}", "role": "native",
                         "statistic": "h137_theta_name", "estimate": f(d["est"]), "ci_lo": f(d["lo"]), "ci_hi": f(d["hi"]),
                         "ci_kind": "percentile", "ci_level": 0.95, "n": g38[part]["n_rows_z"],
                         "n_kind": "follow-hop rows in one-way pairs", "method": f"N2 native: G38 {part} pairs, A1 logit",
                         "null": f"N2 p={d['p_n2']:.3f}" if d.get("p_n2") is not None else "N2",
                         "notes": NOTE, "source": "results/round1.json"})
    rows = [r for r in rows if r["estimate"] is not None]
    df = E.write_estimates(rows, hypothesis="H137")
    print(f"wrote {df.height} rows")


if __name__ == "__main__":
    main()
