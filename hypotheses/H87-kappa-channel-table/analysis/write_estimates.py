"""Write H87 per-period rows to the shared per_period_estimates table (infra/shared/estimates.py).

Replication: per regime-III period, I_c (bits), dV_c (commits per 20 calls) and kappa_c for rows C, A, M, G, Q.
The pooled NE41 table and the NE34 kickoff row span periods (transition designs), so they are not written here
(estimates_schema.md: "never write pooled-period fits"); they live in results.json and the card.
Usage: uv run python hypotheses/H87-kappa-channel-table/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "data/processed/H87-kappa-channel-table/results/results.json"
CH = {"A": "own_artifact", "M": "memory_note", "G": "chat_reads_agent", "Q": "history_search", "C": "context_window"}


def fin(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else float(x)


def main():
    rep = json.loads((ROOT / SRC).read_text())["replication"]
    rows = []
    for p, t in rep.items():
        g = int(p[1:])
        u = "local:G51-head" if g == 51 else (E.map_unit(g) or f"local:{p}")
        base = {"period_unit": u, "goal_no": g, "role": "replication", "source": SRC, "unit_local": p,
                "first_day": t["days"][0], "last_day": t["days"][-1], "ci_level": 0.95, "ci_kind": "percentile",
                "n": t["n_scramble"], "n_kind": "forced erasures (F); placebo P events alongside"}
        for c, r in t["rows"].items():
            ident = t["identified"][c]
            rows.append({**base, "statistic": "I_c_allocation_bits", "channel": CH[c], "estimate": fin(r["I"]),
                         "ci_lo": fin(r["I_ci"][0]), "ci_hi": fin(r["I_ci"][1]), "se": fin(r["I_se"]),
                         "method": ("I_P - I_F of X+ vs S_C" if c == "C" else "I(X+; S_c) at F") +
                                   "; Miller-Madow plug-in minus within agent x period permutation floor; paired "
                                   "agent-day bootstrap 200, recentred",
                         "null": "within-stratum permutation floor"})
            rows.append({**base, "statistic": "dV_c_commits_per20", "channel": CH[c], "estimate": fin(r["dV"]),
                         "ci_lo": fin(r["dV_ci"][0]), "ci_hi": fin(r["dV_ci"][1]), "se": fin(r["dV_se"]),
                         "method": ("erasure cost: Poisson FE (agent x period), F vs P, log1p V_pre" if c == "C" else
                                    "open x scramble Poisson DiD, stratum x arm FE, log1p V_pre (semantic_kappa)"),
                         "null": "0 (no channel value)", "notes": f"dV_rel {fin(r['dV_rel'])}"})
            rows.append({**base, "statistic": "kappa_c_commits_per20_per_bit", "channel": CH[c],
                         "estimate": fin(r["kappa"]) if ident else None,
                         "ci_lo": fin(r["kappa_ci"][0]) if ident else None,
                         "ci_hi": fin(r["kappa_ci"][1]) if ident else None, "ci_kind": "percentile" if ident else "none",
                         "method": "dV_c / I_c on paired bootstrap draws (undefined where I_c <= 0.02 bits)",
                         "null": "kappa defined only when I CI lower bound > 0.02 bits (Amendment A1)",
                         "notes": "identified" if ident else "not identified (I CI reaches 0.02 bits)"})
    E.write_estimates(rows, hypothesis="H87")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
