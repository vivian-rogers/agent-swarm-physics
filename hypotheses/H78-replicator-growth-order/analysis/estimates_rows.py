"""Write H78 rows into the shared per-period estimates table (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H78-replicator-growth-order/results"
ROLE = {31: "replication", 33: "replication", 41: "replication", 39: "replication", 42: "replication", 51: "replication",
        40: "native", 44: "native"}
METHOD = ("Poisson GLM, swarm call-clock bins B=200, offset log free calls, formation-free recruits (no blind, no "
          "kickoff-named), host expiry E=100; quasi-Poisson SE")
SINGLE = {33: "33", 39: "39", 40: "40", 41: "41"}


def rows():
    out = []
    for g, role in ROLE.items():
        p = DATA / f"G{g:02d}.json"
        if not p.exists():
            continue
        r = json.loads(p.read_text())
        pr = r["primary"]
        src = str(p.relative_to(ROOT))
        pool = pr.get("pooled")
        if pool:
            out.append({"period_unit": SINGLE.get(g, f"G{g:02d}"), "goal_no": g, "statistic": "replicator_growth_order_p",
                        "channel": "project", "estimate": pool["est"], "se": pool["se"], "ci_lo": pool["lo"], "ci_hi": pool["hi"],
                        "ci_level": 0.95, "ci_kind": "se_z", "n": pr["n_events"], "n_kind": "events",
                        "method": METHOD + ("; DerSimonian-Laird pool over units" if len(pr["units"]) > 1 else ""),
                        "null": "neutral copying p = 1", "role": role, "status": "ok" if pr["testable"] else "underpowered",
                        "source": src, "notes": "A1: parabolic p not identifiable from 1 under fitness heterogeneity"})
        if len(pr["units"]) > 1:
            for u, v in pr["units"].items():
                out.append({"period_unit": u, "goal_no": g, "statistic": "replicator_growth_order_p", "channel": "project",
                            "estimate": v["est"], "se": v["se"], "ci_lo": v["lo"], "ci_hi": v["hi"], "ci_level": 0.95,
                            "ci_kind": "se_z", "n": v["n_events"], "n_kind": "events", "method": METHOD + "; unit fit",
                            "null": "neutral copying p = 1", "role": role, "status": "ok" if v["n_events"] >= 15 else "underpowered",
                            "source": src})
        fs = r.get("formation_share")
        if fs is not None:
            out.append({"period_unit": SINGLE.get(g, f"G{g:02d}"), "goal_no": g, "statistic": "replicator_formation_share",
                        "channel": "project", "estimate": fs, "ci_kind": "none", "n": None, "method": "births + named + blind "
                        "arrivals over all arrivals (host labels E=100)", "null": None, "role": role, "status": "ok", "source": src})
    return out


if __name__ == "__main__":
    rs = rows()
    E.write_estimates(rs, hypothesis="H78")
    print(len(rs), "rows")
