"""Write H73 per-period rows to the shared per_period_estimates table (infra/shared/estimates.py).

Replication rows per eligible goal period; native rows for G12, G44, G51 and the per-goal NE41 forced-erasure beta
(NE41's pooled fit spans periods, so only its per-goal fits are written).
Usage: uv run python hypotheses/H73-style-three-components/analysis/write_estimates.py
"""
from __future__ import annotations
import json
import sys

import numpy as np
import polars as pl

import h73lib as L

sys.path.insert(0, str(L.ROOT / "infra" / "shared"))
import estimates as E  # noqa: E402

REP = "data/processed/H73-style-three-components/replication/replication.json"
NAT = "data/processed/H73-style-three-components/natives/natives.json"


def unit_of(g: int) -> str:
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter((pl.col("goal_no") == g) & ~pl.col("holdout"))
    return pu["unit_id"][0] if pu.height == 1 else f"G{g:02d}"


def nz(x):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else float(x)


def main():
    rep = json.loads((L.ROOT / REP).read_text())
    nat = json.loads((L.ROOT / NAT).read_text())
    rows = []
    for k, r in rep.items():
        if k.startswith("_"):
            continue
        g = r["goal_no"]
        u = unit_of(g)
        d = r["dec"]
        a5 = r["att"].get("5") or {}
        base = {"period_unit": u, "goal_no": g, "role": "replication", "source": REP, "channel": "style"}
        rows += [
            {**base, "statistic": "F3_three_component_share", "estimate": d["F3"], "ci_lo": r["F3_ci"][0],
             "ci_hi": r["F3_ci"][1], "ci_level": 0.95, "ci_kind": "jackknife_z", "se": r["F3_se"], "n": d["n_days"],
             "n_kind": "days", "method": "trace adj-R2: (G+A+C+R - G)/(kappa_cells - G), 17-d type-controlled style",
             "null": "G + A baseline at the cell ceiling", "notes": f"{d['n']} messages; synthetic bias up to +0.07 near 0.55 (A2)"},
            {**base, "statistic": "u_agent_constant", "estimate": d["u_A"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
             "n": d["n_agents"], "n_kind": "agents", "method": "drop-one adj-R2 share of non-day systematic variance", "null": None},
            {**base, "statistic": "u_context", "estimate": d["u_C"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
             "n": d["n_cu"], "n_kind": "messages (computer-use)", "method": "drop-one adj-R2 share; bins + agent slopes on log2(1+ctx_pos)",
             "null": f"within-agent-day permutation of context state; p = {d.get('p_C')}"},
            {**base, "statistic": "attribution_gain_context_k5", "estimate": a5.get("gain_agent"), "ci_lo": None, "ci_hi": None,
             "ci_kind": "none", "n": a5.get("n_blocks"), "n_kind": "5-message blocks",
             "method": "leave-one-day-out balanced accuracy, agent-specific context minus blind centroid",
             "null": "synthetic null bias -0.006 to -0.023", "notes": f"blind accuracy {a5.get('blind')}"},
        ]
        dis = r["disp"]
        if dis.get("slope") is not None and np.isfinite(dis.get("slope", np.nan)):
            rows.append({**base, "statistic": "dispersion_slope_rel", "estimate": dis["slope_rel"],
                         "ci_lo": dis["lo"] * dis["slope_rel"] / dis["slope"] if dis["slope"] else None,
                         "ci_hi": dis["hi"] * dis["slope_rel"] / dis["slope"] if dis["slope"] else None,
                         "ci_level": 0.95, "ci_kind": "percentile", "n": dis["n_cu"], "n_kind": "messages (computer-use)",
                         "method": "residual squared norm on log2 fill, within agent, relative to mean; agent-cluster bootstrap",
                         "null": "slope 0", "notes": "descriptive unless n_cu >= 2000 (A3)"})
    for gk, v in nat["NE41"]["per_goal"].items():
        g = int(gk[1:])
        rows.append({"period_unit": unit_of(g), "goal_no": g, "role": "native", "source": NAT, "channel": "style",
                     "statistic": "ne41_forced_beta", "estimate": v["beta"], "ci_lo": v["lo"], "ci_hi": v["hi"],
                     "ci_level": 0.95, "ci_kind": "percentile", "n": v["n"], "n_kind": "forced-erasure message pairs",
                     "method": "projection of observed jump on drift-predicted jump (day cross-fit)", "null": "beta 0"})
    g12 = nat["G12"]
    rows += [{"period_unit": unit_of(12), "goal_no": 12, "role": "native", "source": NAT, "channel": "style",
              "statistic": "judge_register_cosine", "estimate": g12["coh"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
              "n": len(g12["cos"]), "n_kind": "judges", "method": "leave-agent-out cosine of judge shifts",
              "null": f"judge-window permutation p = {g12['p_coh']}"},
             {"period_unit": unit_of(12), "goal_no": 12, "role": "native", "source": NAT, "channel": "style",
              "statistic": "u_register", "estimate": g12["u_R"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
              "n": g12["n_reg"]["judge"], "n_kind": "judge messages", "method": "drop-one adj-R2 share",
              "null": f"judge-window permutation p = {g12['p_R']}"}]
    g51 = nat["G51"]
    rows.append({"period_unit": unit_of(51), "goal_no": 51, "role": "native", "source": NAT, "channel": "style",
                 "statistic": "media_register_cosine", "estimate": g51["media_cos"], "ci_lo": None, "ci_hi": None,
                 "ci_kind": "none", "n": 4, "n_kind": "agents", "method": "mean pairwise cosine of centred #51 shifts",
                 "null": f"role-label permutation p = {g51['p_coh']}"})
    g44 = nat["G44"]
    rows.append({"period_unit": unit_of(44), "goal_no": 44, "role": "native", "source": NAT, "channel": "style",
                 "statistic": "leader_base_rank_context", "estimate": g44["rank_agent"], "ci_lo": None, "ci_hi": None,
                 "ci_kind": "none", "n": g44["n_leader"], "n_kind": "messages",
                 "method": "rank of Kimi K2.6 centroid for the leader (agent-specific context model)",
                 "null": f"chance rank {(g44['n_cand'] + 1) / 2}", "notes": f"blind rank {g44['rank_blind']}"})
    for r in rows:
        for c in ("estimate", "ci_lo", "ci_hi", "se"):
            if c in r:
                r[c] = nz(r[c])
    E.write_estimates(rows, hypothesis="H73")
    print(f"wrote {len(rows)} rows")


if __name__ == "__main__":
    main()
