"""Write H68 per-period rows to the shared per_period_estimates table (write_estimates)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H68-dilution-mixture"
SRC = "data/processed/H68-dilution-mixture/results.json"


def main():
    r = json.loads((D / "results.json").read_text())
    rows = []
    for p, o in r["periods"].items():
        if "tau" not in o:
            continue
        g = int(p[1:])
        unit = E.map_unit(g)
        role = "native" if p == "G51" else "replication"
        base = dict(period_unit=unit, goal_no=g, source=SRC, post_hoc=False, role=role,
                    status=f"round 1; verdict {o['verdict']}" + ("" if o["powered"] else " (not powered)"),
                    channel="addressed (mention), ledger k", n=o["n_eligible"], n_kind="agents")
        rows.append(dict(base, statistic="dilution_beta_between_agent_sd", estimate=o["tau"], ci_lo=o["tau_ci"][0],
                         ci_hi=o["tau_ci"][1], ci_level=0.95, ci_kind="profile",
                         method="per-agent cloglog k^-beta_i with agent-day propensities; heteroscedastic RE ML",
                         null="tau = 0 (one exponent)"))
        rows.append(dict(base, statistic="dilution_beta_agent_mean", estimate=o["mu"], ci_lo=None, ci_hi=None,
                         ci_kind="none", method="RE mean of per-agent exponents", null="none"))
        m = o["mix"]
        rows.append(dict(base, statistic="dilution_mixture_LR", estimate=m["lr"], ci_lo=None, ci_hi=None, ci_kind="none",
                         method="2(ll two-component - ll unimodal), heteroscedastic", null=f"parametric bootstrap p = {m['p']:.3f}",
                         notes=f"modes {m['M2']['m_lo']:.2f}/{m['M2']['m_hi']:.2f}; H68-literal dll {m['dll_H68_U']:.2f}"))
    E.write_estimates(rows, hypothesis="H68")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
