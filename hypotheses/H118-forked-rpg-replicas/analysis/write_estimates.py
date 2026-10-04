"""Write H118 round-1 rows to the shared per_period_estimates table (infra/shared/estimates.py)."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h118lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

UNIT = {"35": ("G35", 35, None, None), "36": ("local:36bc", 36, "2026-03-24", "2026-03-27"), "36a": ("36a", 36, None, None),
        "37": ("G37", 37, None, None), "38": ("G38", 38, None, None), "39": ("G39", 39, None, None),
        "41": ("G41", 41, None, None), "42": ("G42", 42, None, None), "44": ("G44", 44, None, None)}
SRC = "data/processed/H118-forked-rpg-replicas/results/results.json"


def fin(x):
    return None if x is None or not np.isfinite(x) else float(x)


def main():
    R = json.loads((L.DATA / "results" / "results.json").read_text())
    rows = []
    for key, r in R["periods"].items():
        p, m, var = key.split("|")
        if var != "main":
            continue
        unit, g, f, l = UNIT[p]
        role = "native" if p == "35" else "replication"
        ch = f"content_{m.split('_')[0]}_style_resid"
        b = r["boot_agent_bin"]
        base = dict(period_unit=unit, goal_no=g, channel=ch, role=role, n=r["n_stmt"], n_kind="statements",
                    ci_kind="percentile", ci_level=0.95, first_day=f, last_day=l, source=SRC, post_hoc=False)
        rows.append(base | dict(statistic="replica_overlap_q_late", estimate=fin(r["q_late"]), ci_lo=fin(b["q_late_ci"][0]),
                                ci_hi=fin(b["q_late_ci"][1]), method="split-half disattenuated room-centroid cosine, late block; agent x bin bootstrap",
                                null="joint relabel q_rel_late = %.3f" % r["q_rel_late"],
                                notes="leave-own-period-out regime reference; 1-h active bins"))
        if np.isfinite(r["M_late"] if r["M_late"] is not None else np.nan):
            rows.append(base | dict(statistic="equal_time_memory_M_late", estimate=fin(r["M_late"]), ci_lo=fin(b["M_late_ci"][0]),
                                    ci_hi=fin(b["M_late_ci"][1]), method="mean over days >= 2 of q_eq(d) - q_lag(d); agent x bin bootstrap",
                                    null="0 (no same-day shared state beyond the static overlap)"))
        rows.append(base | dict(statistic="damage_time_tau_D_h", estimate=fin(r["tau"]["tau"]), ci_lo=fin(b["tau_ci"][0]),
                                ci_hi=fin(b["tau_ci"][1]), method="weighted LS fit q(t) = q_inf + (q0 - q_inf) exp(-t/tau), tau grid 0.25-80 active h",
                                null="unpowered at these counts (Amendment 1)", notes=f"decays={r['tau']['decays']}"))
    code = [c for c in R["code"] if c["pt_date"] == "2026-03-20" and c["hour"] == 3][0]
    for fam in ("src", "functions", "files"):
        base = dict(period_unit="G35", goal_no=35, channel=f"code_{fam}", role="native", n=None, n_kind="ancestor keys",
                    ci_kind="none", source=SRC, post_hoc=False, first_day=None, last_day=None)
        rows.append(base | dict(statistic="code_overlap_q_code_end35", estimate=code[f"{fam}_q"], ci_lo=None, ci_hi=None,
                                method="share of ancestor keys identical in rpg-game-best and rpg-game-rest at the end of #35",
                                null="independent replicas q_ind = %.3f" % code[f"{fam}_q_ind"]))
        rows.append(base | dict(statistic="code_identity_excess_X_end35", estimate=code[f"{fam}_X"], ci_lo=None, ci_hi=None,
                                method="q_code - c_best * c_rest (correlated damage)",
                                null="hypergeometric (key permutation within family) p = %.2g" % code[f"{fam}_p_hot"]))
        rows.append(base | dict(statistic="code_frozen_core_F_end35", estimate=code[f"{fam}_F"], ci_lo=None, ci_hi=None,
                                method="share of ancestor keys unchanged in both forks", null="none"))
    E.write_estimates(rows, hypothesis="H118")
    print("rows", len(rows))


if __name__ == "__main__":
    main()
