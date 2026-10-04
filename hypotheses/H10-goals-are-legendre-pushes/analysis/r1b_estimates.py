"""H10 round 1b: per-period estimates for the shared table (infra/shared/estimates.py), both embedding models, shared
goal fields. Only single-period statistics are written (the free -> assigned push, the NE34 kickoff jumps and the
native transitions G44 / NE38 / G26 span two segments, which the schema keeps out of the per-period table):
  loop_gain_g_along_goal   window-level loop gain along the goal direction (free weeks along the next goal's g-hat;
                           assigned weeks along their own, first unit, segment A = days 2+)
  goal_alignment_mean      mean agent alignment with g-hat in that segment
  fluct_kappa2_along_goal  mean noise-corrected window variance along g-hat
Usage: uv run python hypotheses/H10-goals-are-legendre-pushes/analysis/r1b_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
import estimates as E  # noqa: E402

DATA = HERE.parents[2] / "data/processed/H10-goals-are-legendre-pushes"
ROOT = HERE.parents[2]
METHOD = ("H10 r1b: whitened n = 32 statement vectors, 30-min agent windows (>= 2 statements), noise-corrected (ANOVA); "
          "shared goal fields")
SEGS = {11: ("free", "11-12", "F"), 16: ("free", "16-17", "F"), 37: ("free", "37-38", "F"),
        12: ("assigned (12a, days 2+)", "11-12", "A"), 17: ("assigned (days 2+)", "16-17", "A"),
        38: ("assigned (38a, days 2+)", "37-38", "A")}


def main():
    rows = []
    for model in ("bge_small", "gte_modernbert"):
        f = DATA / "r1b" / f"{model}_shared" / "NE34" / "pairs.json"
        if not f.exists():
            continue
        P = json.loads(f.read_text())["pairs"]
        src = str(f.relative_to(ROOT))
        for g, (kind, key, side) in SEGS.items():
            r = P[key]
            gval, ci = r.get(f"g{side}"), r.get(f"g{side}_ci90")
            days = r["days_F"] if side == "F" else r["days_A"]
            unit = E.map_unit(g, days[0], days[-1]) or f"local:{g}{side}"
            base = dict(period_unit=unit, goal_no=g, first_day=days[0], last_day=days[-1], channel=f"content_{model}", role="replication", source=src, status="ok",
                        unit_local=f"{key}:{side}", notes=f"{kind} segment of pair {key}")
            if gval is not None:
                rows.append({**base, "statistic": "loop_gain_g_along_goal", "estimate": gval,
                             "ci_lo": ci[0] if ci else None, "ci_hi": ci[1] if ci else None, "ci_level": 0.90,
                             "ci_kind": "percentile" if ci else "none", "n": r["N"], "n_kind": "agents",
                             "method": METHOD + "; g = 1 - V_indep / V along g-hat, day-block bootstrap", "null": None})
            agents = r["agent_table"]
            mu = [a["muF" if side == "F" else "muA"] for a in agents]
            k2 = [a["k2F" if side == "F" else "k2A"] for a in agents]
            rows.append({**base, "statistic": "goal_alignment_mean", "estimate": float(sum(mu) / len(mu)), "ci_kind": "none",
                         "n": len(mu), "n_kind": "agents", "method": METHOD + "; mean over agents present in both segments",
                         "null": None})
            rows.append({**base, "statistic": "fluct_kappa2_along_goal", "estimate": float(sum(k2) / len(k2)), "ci_kind": "none",
                         "n": len(k2), "n_kind": "agents", "method": METHOD + "; mean over agents present in both segments",
                         "null": None})
    out = E.write_estimates(rows, hypothesis="H10")
    print(f"wrote {out.height} H10 rows")


if __name__ == "__main__":
    main()
