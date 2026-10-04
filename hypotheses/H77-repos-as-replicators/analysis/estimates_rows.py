"""Write H77 rows into the shared per-period estimates table (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H77-repos-as-replicators/results"
ROLE = {31: "replication", 33: "replication", 41: "replication", 39: "replication", 42: "replication", 51: "replication",
        40: "native"}
SINGLE = {33: "33", 39: "39", 40: "40", 41: "41"}
M_SIG = ("sigma* = ln[(J+ + 1/2)/(J- + 1/2)] for the top repo on its plateau (n >= 0.5 max after first reaching 0.8 max); "
         "J+ recruitments, J- switch-outs; host expiry E=100; Poisson log-ratio SE")
M_Q = "uncopying order q: Poisson GLM of switch-outs on log n, offset log host calls (call-clock bins B=200, E=100)"


def rows():
    out = []
    for g, role in ROLE.items():
        p = DATA / f"G{g:02d}.json"
        if not p.exists():
            continue
        r = json.loads(p.read_text())
        src = str(p.relative_to(ROOT))
        pu = SINGLE.get(g, f"G{g:02d}")
        s = r.get("sigma")
        if s:
            nb = r.get("neutral_null")
            out.append({"period_unit": pu, "goal_no": g, "statistic": "replicator_sigma_star", "channel": "project",
                        "estimate": s["est"], "se": s["se"], "ci_lo": s["lo"], "ci_hi": s["hi"], "ci_level": 0.95,
                        "ci_kind": "parametric", "n": s["J_plus"] + s["J_minus"], "n_kind": "events", "method": M_SIG,
                        "null": f"neutral world 95th pct {nb['q95']:.2f}" if nb else "neutral world", "role": role,
                        "status": "ok" if s["testable"] else "underpowered", "source": src})
            for u, v in (s.get("units") or {}).items():
                if len(s["units"]) > 1:
                    out.append({"period_unit": u, "goal_no": g, "statistic": "replicator_sigma_star", "channel": "project",
                                "estimate": v["est"], "se": v["se"], "ci_lo": v["est"] - 1.96 * v["se"],
                                "ci_hi": v["est"] + 1.96 * v["se"], "ci_level": 0.95, "ci_kind": "parametric",
                                "n": v["J_plus"] + v["J_minus"], "n_kind": "events", "method": M_SIG + "; unit share of the plateau",
                                "null": None, "role": role, "status": "ok" if v["J_plus"] + v["J_minus"] >= 8 else "underpowered",
                                "source": src})
        q = r.get("q")
        if q:
            out.append({"period_unit": pu, "goal_no": g, "statistic": "replicator_uncopying_order_q", "channel": "project",
                        "estimate": q["est"], "se": q["se"], "ci_lo": q["lo"], "ci_hi": q["hi"], "ci_level": 0.95,
                        "ci_kind": "se_z", "n": q["n_events"], "n_kind": "events", "method": M_Q,
                        "null": "first-order (q = 1)", "role": role, "status": "ok" if q["n_events"] >= 15 else "underpowered",
                        "source": src})
    return out


if __name__ == "__main__":
    rs = rows()
    E.write_estimates(rs, hypothesis="H77")
    print(len(rs), "rows")
