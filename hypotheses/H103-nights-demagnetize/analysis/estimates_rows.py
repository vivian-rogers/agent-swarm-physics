"""H103 rows for the shared per-period estimates table (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H103-nights-demagnetize/results"
SRC = "data/processed/H103-nights-demagnetize/results/"


def v(x):
    return None if (x is None or not np.isfinite(x)) else float(x)


def rows() -> list[dict]:
    out = []
    for model in ("bge_small", "gte_modernbert"):
        tag = f"{model}_style_resid"
        o1 = json.loads((DATA / f"o1_{tag}.json").read_text())
        for name, r in o1.items():
            g = r["goal_no"]
            base = {"period_unit": E.map_unit(g), "goal_no": g, "unit_local": name, "role": "replication",
                    "channel": "content", "ci_level": 0.95, "n": r["n_windows"], "n_kind": "30-min windows (incumbents)",
                    "source": SRC + f"o1_{tag}.json"}
            meth = f"kickoff remanence (decoy-corrected) on 30-min windows; clock models with slot effects; agent bootstrap [{model}]"
            out.append({**base, "statistic": "kickoff_remanence_night_factor_lambda", "estimate": v(r["nested"]["lam"]),
                        "ci_lo": v(r["lam_ci"][0]), "ci_hi": v(r["lam_ci"][1]), "ci_kind": "percentile",
                        "method": "nested lambda^N exp(-H/tau); " + meth, "null": "1 (no night step beyond active hours)",
                        "notes": f"winner {r['winner']}; verdict {r['verdict']}"})
            out.append({**base, "statistic": "kickoff_remanence_sse_ratio_H_over_N",
                        "estimate": v(r["sse"]["H"] / r["sse"]["N"]) if r["sse"]["N"] > 0 else None, "ci_lo": None,
                        "ci_hi": None, "ci_kind": "none", "method": "SSE(active-hour clock)/SSE(night clock); " + meth,
                        "null": "1", "notes": f"P(N beats H) bootstrap {r['p_N_beats_H']:.2f}"})
            out.append({**base, "statistic": "kickoff_remanence_day1_level", "estimate": v(r["level_day1"]),
                        "ci_lo": v(r["level_day1_ci"][0]), "ci_hi": v(r["level_day1_ci"][1]), "ci_kind": "percentile",
                        "method": "window-weighted mean decoy-corrected kickoff alignment on day 1; " + meth, "null": "0"})
        o3 = json.loads((DATA / f"o3_{tag}.json").read_text())
        for u, r in o3.items():
            g = r["goal_no"]
            pu = u if not u.startswith("G") else E.map_unit(g)
            for k, null in (("beta_N", "0 (no night step at fixed active lag)"), ("beta_G", "0 (break length irrelevant)"),
                            ("beta_gap", "0 (own midday gaps irrelevant)")):
                if not np.isfinite(r[k]["est"]):
                    continue
                out.append({"period_unit": pu, "goal_no": g, "unit_local": u, "role": "replication", "channel": "content",
                            "statistic": f"self_overlap_{k}", "estimate": v(r[k]["est"]), "ci_lo": v(r[k]["lo"]),
                            "ci_hi": v(r[k]["hi"]), "ci_level": 0.95, "ci_kind": "percentile", "n": r["n_pairs"],
                            "n_kind": "same-agent window pairs", "null": null, "source": SRC + f"o3_{tag}.json",
                            "method": f"pair OLS: agent FE + slot-pair FE + 0.5-h lag bins + lag polynomial; agent-cluster bootstrap [{model}]",
                            "notes": f"{r['n_cross_night']} cross-night pairs, {r['n_weekend']} weekend"})
        nat = json.loads((DATA / f"natives_{tag}.json").read_text())
        d = nat["NE43"]["delta_beta_N"]
        out.append({"period_unit": "local:NE43", "goal_no": 51, "unit_local": "NE43", "role": "native", "channel": "content",
                    "statistic": "self_overlap_beta_N_change_NE43", "estimate": v(d["est"]), "ci_lo": v(d["lo"]),
                    "ci_hi": v(d["hi"]), "ci_level": 0.95, "ci_kind": "se_z", "se": v(d["se"]),
                    "n": nat["NE43"]["before"]["n_pairs"] + nat["NE43"]["after"]["n_pairs"], "n_kind": "window pairs",
                    "method": f"beta_N after 08-05 minus before (G51) [{model}]", "null": "0", "source": SRC + f"natives_{tag}.json"})
        d = nat["NE41"]["beta_R_RE"]
        out.append({"period_unit": "local:NE41", "goal_no": None, "unit_local": "NE41", "role": "native", "channel": "content",
                    "statistic": "self_overlap_beta_R_per_reset", "estimate": v(d["est"]), "ci_lo": v(d["lo"]),
                    "ci_hi": v(d["hi"]), "ci_level": 0.95, "ci_kind": "se_z", "n": d["k"], "n_kind": "regime-III units (RE)",
                    "method": f"RE mean of the per-reset term on same-day pairs [{model}]", "null": "0",
                    "source": SRC + f"natives_{tag}.json"})
    return out


if __name__ == "__main__":
    r = rows()
    E.write_estimates(r, hypothesis="H103")
    print(len(r), "rows written")
