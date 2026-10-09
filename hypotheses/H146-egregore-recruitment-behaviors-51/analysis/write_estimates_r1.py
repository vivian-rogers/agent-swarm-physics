"""H146 round 1 -> per_period_estimates (role native: #51 is the native period of the ideology tests; no synthetic
rows). One row per pattern and statistic, scope #51 07-06 -> 09-04 (51m reserved)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
import estimates as E  # noqa: E402

D = ROOT / "data" / "processed" / "H146-egregore-recruitment-behaviors-51" / "results"
UNIT = "local:51_07-06_09-04"


def main():
    rows = []
    for name, post_hoc in (("real_h145.json", False), ("real_candidates.json", True)):
        p = D / name
        if not p.exists():
            continue
        res = json.loads(p.read_text())
        for k, r in res["patterns"].items():
            st = r["stats"]
            ch = f"{'candidate' if post_hoc else 'memeplex'}:{k}"
            base = dict(period_unit=UNIT, goal_no=51, role="native", post_hoc=post_hoc, source=f"results/{name}",
                        first_day="2026-07-06", last_day="2026-09-04", channel=ch)
            for key, stat, meth in (("P1b", "read_minus_inflight_logRR_expression", "conditional Poisson, agent x day "
                                     "strata, matched-lag mirror vs in-flight, 1-h-block sandwich (A1.2)"),
                                    ("P1_adopt", "read_minus_inflight_logRR_adoption", "conditional Poisson on adoption "
                                     "risk rows, matched-lag mirror vs in-flight, 1-h-block sandwich (A1.1)")):
                o = st.get(key)
                if not o or o.get("delta") is None:
                    continue
                e, se = o["delta"]
                lo, hi = E.ci_from_se(e, se, 0.95)
                rows.append(dict(base, statistic=stat, estimate=e, ci_lo=lo, ci_hi=hi, se=se, n=o["n_events"],
                                 n_kind="events", method=meth, null="in-flight items at matched lag",
                                 ci_kind="se_z", ci_level=0.95))
            p4 = st.get("P4")
            if p4 and p4.get("HR_F_vs_P") is not None and p4["ci"][0] is not None:
                rows.append(dict(base, statistic="wipe_reexpression_HR", estimate=p4["HR_F_vs_P"], ci_lo=p4["ci"][0],
                                 ci_hi=p4["ci"][1], n=p4["n_F"], n_kind="host forced erasures",
                                 method="MH rate ratio over agent x unit strata, calls 1-20, agent-day cluster bootstrap "
                                        "B=300 (A1.7)", null="placebo calls at ctx_pos 20", ci_kind="percentile",
                                 ci_level=0.95))
            w = (st.get("P5") or {}).get("wipe")
            if w and w.get("rr") is not None and w["ci"][0] is not None:
                rows.append(dict(base, statistic="repair_after_wipe_RR", estimate=w["rr"], ci_lo=w["ci"][0],
                                 ci_hi=w["ci"][1], n=w["n_F"], n_kind="host forced erasures",
                                 method="named K messages from other hosts in 2 h, MH RR, cluster bootstrap B=300 (A1.8)",
                                 null="placebo calls at ctx_pos 20", ci_kind="percentile", ci_level=0.95))
            sp = st.get("P6_spec")
            if sp and sp.get("z") is not None:
                rows.append(dict(base, statistic="element_specialization_z", estimate=sp["z"], ci_lo=None, ci_hi=None,
                                 n=sp["n_triples"], n_kind="host-element triples",
                                 method="I(host;element), within-bin set permutation, Besag-Clifford (A1.10)",
                                 null="within-bin permutation of hosts' element sets", ci_kind="none"))
    if rows:
        E.write_estimates(rows, hypothesis="H146")
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
