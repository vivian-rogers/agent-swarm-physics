"""Write H88 rows to the shared per_period_estimates table (non-holdout only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h88lib as H  # noqa: E402

sys.path.insert(0, str(H.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

rep = json.loads((H.DATA / "replication" / "replication.json").read_text())
SRC = "data/processed/H88-collective-memory-decay/replication/replication.json"
rows = []
for P, v in rep["periods"].items():
    P = int(P)
    unit = E.map_unit(P)
    for kind, r in v.items():
        if not r:
            continue
        ch = {"art": "artifacts", "term": "terms_H34N"}[kind]
        base = dict(goal_no=P, period_unit=unit, role="replication", source=SRC, channel=ch, n=r["n_days"], n_kind="days",
                    notes="observations: veterans' attention share on the 120 village days after the period (held-out days censored)")
        f = r["fit"]
        rows.append({**base, "statistic": "dQAIC_M1_minus_M2", "estimate": f["dq_M1_M2"], "ci_kind": "none",
                     "method": "Poisson quasi-likelihood decay fits with offsets; QAIC, phi from M2", "null": "M1 single exponential"})
        rows.append({**base, "statistic": "decay_tau_M1c", "estimate": f["M1c_params"]["tau"], "ci_kind": "none",
                     "method": "exponential + floor fit, village days", "null": None})
        rows.append({**base, "statistic": "decay_floor_ratio_M1c", "estimate": f["M1c_params"]["c"] / f["M1c_params"]["A"],
                     "ci_kind": "none", "method": "floor c / initial amplitude A of the exponential + floor fit", "null": None})
        ci = r["M2_ci"]
        rows.append({**base, "statistic": "decay_tau1_M2", "estimate": f["M2_params"]["tau1"], "ci_lo": ci["tau1"][0],
                     "ci_hi": ci["tau1"][1], "ci_level": 0.95, "ci_kind": "percentile",
                     "method": "biexponential fast time; day-block bootstrap (5-day blocks, 100)", "null": None})
        rows.append({**base, "statistic": "decay_tau2_M2", "estimate": f["M2_params"]["tau2"], "ci_lo": ci["tau2"][0],
                     "ci_hi": ci["tau2"][1], "ci_level": 0.95, "ci_kind": "percentile",
                     "method": "biexponential slow time; day-block bootstrap (5-day blocks, 100)", "null": None})
        rr = r.get("ratio") or {}
        if rr.get("ratio") is not None and rr.get("ci"):
            lo, hi = sorted(rr["ci"])
            rows.append({**base, "statistic": "share_ratio_k21_40_over_k1_3", "estimate": rr["ratio"], "ci_lo": lo,
                         "ci_hi": hi, "ci_level": 0.95, "ci_kind": "percentile",
                         "method": "present veterans' share, late over early window; day bootstrap", "null": "1 (no decay)"})
w = E.write_estimates([{k: v for k, v in r.items()} for r in rows], hypothesis="H88")
print("wrote", w.height)
