"""Write H58 round-1 per-period rows to the shared estimates table (infra/shared/estimates.py: write_estimates).
Units are H01 round 2's splits, so period_unit = 'local:H01-<unit>' with first/last day. Non-holdout only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h58data as HD  # noqa: E402
import estimates as E  # noqa: E402

RES = HD.D / "results"
REPL = {"38a", "38b", "38c", "51a", "51b", "51c", "51d", "51e"}


def main():
    meta = {x["unit"]: x for x in HD.units_meta()}
    rep = json.loads((RES / "replication.json").read_text())
    rq = json.loads((RES / "reacq.json").read_text())
    nat = json.loads((RES / "natives.json").read_text())
    rows = []

    def base(u, role):
        m = meta[u]
        return {"period_unit": f"local:H01-{u}", "unit_local": u, "goal_no": m["goal_no"], "first_day": m["days"][0],
                "last_day": m["days"][-1], "role": role, "ci_kind": "none", "post_hoc": False,
                "source": "data/processed/H58-coordinated-superagents/results/replication.json"}
    for u, pu in rep["per_unit"].items():
        role = "replication" if u in REPL else "native"
        s = pu.get("search") or {}
        if s.get("g") is not None:
            rows.append({**base(u, role), "statistic": "coord_gain_search_unit", "channel": "work allocation (which repo)",
                         "estimate": s["g"], "n": None, "n_kind": "held-out working member-transitions",
                         "method": "LODO mixture M1 vs agent+own-artifact M0; calibrated subset search",
                         "null": "member-shift + outside-reference (A1-A2)",
                         "notes": f"qualifies_search={s.get('qualifies_search')}; z_spec={s.get('z_comp')}; z_shift={s.get('z_shift')}"})
        rows.append({**base(u, role), "statistic": "effective_superagent_candidate", "channel": "work allocation (which repo)",
                     "estimate": float(pu["any_candidate"]), "n": float(pu["n_multi"] + (1 if s else 0)),
                     "n_kind": "candidate units tested", "method": "card F5 decision rule (A1-A2)",
                     "null": "member-shift + outside-reference + specificity",
                     "notes": "51e qualifier is mutual avoidance (A3)" if u == "51e" else None})
        pr = rq.get("per_unit", {}).get(u)
        if pr and pr["forced_div"]["n"]:
            f = pr["forced_div"]
            rows.append({**base(u, role), "statistic": "reacq_forced_own_share", "channel": "NE41 forced erasure",
                         "estimate": f["own"], "n": float(f["n"]), "n_kind": "divergent forced erasures",
                         "method": "first commit before next reset: own vs group vs other",
                         "null": f"placebo mid-segment calls (own {pr['placebo_div']['own']:.3f})",
                         "source": "data/processed/H58-coordinated-superagents/results/reacq.json"})
    n3 = nat["N3"]
    rows.append({**base("51c", "native"), "statistic": "focus_cut_pair_gain_did", "channel": "#focus room cut",
                 "estimate": n3["did"], "ci_lo": n3["did_ci"][0], "ci_hi": n3["did_ci"][1], "ci_kind": "percentile",
                 "ci_level": 0.95, "n": float(n3["n_split"]), "n_kind": "split pairs",
                 "method": "pair coordination gain DiD 51b->51c, split vs kept", "null": "kept pairs",
                 "source": "data/processed/H58-coordinated-superagents/results/natives.json"})
    out = E.write_estimates(rows, hypothesis="H58")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
