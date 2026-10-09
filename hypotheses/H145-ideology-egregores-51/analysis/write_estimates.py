"""Write H145 round-1 rows to the shared per-period estimates table (real #51 exploration data only; no synthetic
rows). Role 'native' (#51-native design; no replication layer in round 1)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h145lib as L  # noqa: E402
import estimates as E  # noqa: E402

COMMON = dict(period_unit="G51", goal_no=51, role="native", first_day="2026-07-06", last_day="2026-09-04",
              source="data/processed/H145-ideology-egregores-51/results")


def main():
    p1 = json.loads((L.OUT / "results/p1.json").read_text())
    t = json.loads((L.OUT / "results/tests.json").read_text())
    rows = [dict(COMMON, statistic="h145_memeplex_count_hub_free", channel="clusters+markers+repos+projects",
                 estimate=float(p1["obs_hub_free"]), ci_lo=None, ci_hi=None, ci_kind="none", n=20.0, n_kind="null pipelines",
                 method="A1 discovery: activity-adjusted PPMI, BH q0.05, Louvain gamma 1, m 2, 2-h bins",
                 null=f"agent-scope element rotation x20 (A2): mean {np.mean(p1['null_counts']):.1f}, q95 {p1['null_q95']:.0f}",
                 status="P1 supported")]
    for m in t["memeplexes"]:
        p2, p3 = m["P2"], m["P3"]
        rows.append(dict(COMMON, statistic="h145_renewal_contrast_D5", channel="memeplex", unit_local=m["id"],
                         estimate=float(p2["D"]["obs"]), ci_lo=None, ci_hi=float(p2["D"]["thr"]), ci_kind="none", n=200.0,
                         n_kind="pseudo-patterns", method="D_K(5) = S_K(5) - S_H(5) (A4)",
                         null="frequency- and host-count-matched pseudo-patterns; ci_hi = null 95th pct",
                         status="pass" if p2["pass"] else "fail", notes=f"candidate {m['candidate']}"))
        if p3.get("ok"):
            sd = (p3["A"] - (p3["A"] - p3["A_excess"])) / p3["A_z"] if p3["A_z"] else np.nan
            rows.append(dict(COMMON, statistic="h145_colonial_A_excess_bits", channel="memeplex 2h", unit_local=m["id"],
                             estimate=float(p3["A_excess"]), ci_lo=float(p3["A_excess"] - 1.96 * sd) if np.isfinite(sd) else None,
                             ci_hi=float(p3["A_excess"] + 1.96 * sd) if np.isfinite(sd) else None, ci_kind="se_z",
                             se=float(sd) if np.isfinite(sd) else None, n=float(p3["n"]), n_kind="transitions",
                             method="held-out ridge-logit Krakauer A = I(S';S|E), E = phase+exo+role+activity (A5: A only)",
                             null=f"pseudo-patterns, Besag-Clifford h10 n_max200 (drawn {p3['A_n']})",
                             status=("P3a pass" if (p2["pass"] and p3["pass_A"]) else "no"), notes=f"z {p3['A_z']:.2f}, p {p3['A_p']:.3f}"))
    E.write_estimates(rows, hypothesis="H145")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
