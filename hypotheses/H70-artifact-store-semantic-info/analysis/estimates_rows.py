"""H70 rows for the shared per-period estimates table (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H70-artifact-store-semantic-info/results"
SRC = "data/processed/H70-artifact-store-semantic-info/results/"
SCALE_N = {"call": "forced erasures (F) + pseudo-erasures (P)", "day": "nights (N) + mid-day placebos (PN)"}


def _row(common, stat, r, est_key, ci_key, method, null, n, post_hoc=False, notes=None):
    lo, hi = (r.get(ci_key) or [None, None])
    est = r.get(est_key)
    if est is None or est != est:
        return None
    return {**common, "statistic": stat, "estimate": est, "ci_lo": lo, "ci_hi": hi, "n": n, "method": method,
            "null": null, "ci_kind": "percentile" if lo is not None else "none", "post_hoc": post_hoc, "notes": notes}


def rows() -> list[dict]:
    per = json.loads((DATA / "periods.json").read_text())
    nat = json.loads((DATA / "natives.json").read_text())
    out = []
    for p, r in per.items():
        g = int(p[1:3])
        for scale in ("call", "day"):
            common = {"period_unit": E.map_unit(g), "goal_no": g, "unit_local": f"{p}:{scale}", "role": "replication",
                      "ci_level": 0.95, "source": SRC + "periods.json", "n_kind": SCALE_N[scale]}
            a = r.get(scale, {}).get("A")
            if a:
                n = a["n_scramble"] + a["n_placebo"]
                out += [_row({**common, "channel": f"artifact:{scale}"}, "kappa_I_bits", a, "I", "I_ci",
                             "MI(next repo; last-commit repo), Miller-Madow, minus within-agent permutation floor",
                             "within-agent permutation", a["n_scramble"]),
                        _row({**common, "channel": f"artifact:{scale}"}, "kappa_dV_rel", a, "dV_rel", "dV_rel_ci",
                             "Poisson FE (agent-period x arm): exp(b open x scramble) - 1, re-read in calls 1-5",
                             "0 (reading precedes writing)", n),
                        _row({**common, "channel": f"artifact:{scale}"}, "kappa_commits_per_bit", a, "kappa",
                             "kappa_ci", "dV (commits / 20 calls) / I_A", "0", n)]
            c = r.get(scale, {}).get("C")
            if c:
                n = c["n_scramble"] + c["n_placebo"]
                out += [_row({**common, "channel": f"context:{scale}"}, "kappa_dV_rel", c, "dV_rel", "dV_rel_ci",
                             "Poisson FE: 1 - exp(b scramble), output lost in the 20 calls after the erasure", "0", n),
                        _row({**common, "channel": f"context:{scale}"}, "kappa_I_bits", c, "I", "I_ci",
                             "I_placebo - I_scramble of MI(next repo; repo of the last 10 calls)", "0", n)]
    t = nat["NE41"]["call_regime3"]
    for ch, name in (("A", "artifact"), ("M", "memory_note"), ("R", "room"), ("C", "context")):
        r = t[ch]
        common = {"period_unit": "local:NE41", "goal_no": 51, "unit_local": "NE41 pooled regime III", "role": "native",
                  "ci_level": 0.95, "source": SRC + "natives.json", "channel": f"{name}:call", "n_kind": SCALE_N["call"]}
        n = r["n_scramble"] + r["n_placebo"]
        out += [_row(common, "kappa_I_bits", r, "I", "I_ci", "permutation-corrected MI (C: destroyed bits)", "0", n),
                _row(common, "kappa_dV_rel", r, "dV_rel", "dV_rel_ci", "Poisson FE value (C: output lost)", "0", n),
                _row(common, "kappa_commits_per_bit", r, "kappa", "kappa_ci", "dV / I", "0", n)]
    b = nat["NE34"]
    for kind in ("within", "new_goal", "continuation"):
        x = b[kind]
        if x["p_return"] is None:
            continue
        out.append({"period_unit": "local:NE34", "goal_no": 40, "unit_local": f"NE34:{kind}", "role": "native",
                    "channel": "artifact:day", "statistic": "return_to_own_artifact", "estimate": x["p_return"],
                    "ci_lo": x["p_return_ci"][0], "ci_hi": x["p_return_ci"][1], "ci_level": 0.95,
                    "ci_kind": "percentile", "n": x["n_with_commit"], "n_kind": "nights with a commit",
                    "method": "P(first commit of the day = last repo), agent-cluster bootstrap", "null": "none",
                    "source": SRC + "natives.json"})
    return [r for r in out if r is not None]


if __name__ == "__main__":
    r = rows()
    E.write_estimates(r, hypothesis="H70")
    print(len(r), "rows written")
