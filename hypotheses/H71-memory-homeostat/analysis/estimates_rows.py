"""H71 rows for the shared per-period estimates table (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H71-memory-homeostat/results"
SRC = "data/processed/H71-memory-homeostat/results/"
SPLIT_UNITS = {"G12a": "12a", "G12b": "12b", "G36a": "36a", "G36b": "36b", "G36c": "36c"}


def unit(per: str) -> tuple[str, int]:
    g = int(per[1:3])
    return (SPLIT_UNITS[per] if per in SPLIT_UNITS else E.map_unit(g)), g


def rows() -> list[dict]:
    per = json.loads((DATA / "periods.json").read_text())
    ph = json.loads((DATA / "posthoc.json").read_text())
    nat = json.loads((DATA / "natives.json").read_text())
    out = []
    base = {"channel": "memory", "role": "replication", "ci_level": 0.95}
    for p, r in per.items():
        u, g = unit(p)
        common = {**base, "period_unit": u, "goal_no": g, "unit_local": p}
        out.append({**common, "statistic": "memory_phi_plus", "estimate": r["phi"]["est"], "ci_lo": r["phi"]["lo"],
                    "ci_hi": r["phi"]["hi"], "n": r["n_pairs"], "n_kind": "compression-cycle pairs",
                    "method": "half-panel-jackknife within-agent AR(1) on ln post-compression size; agent bootstrap",
                    "null": "random walk (1) / deadbeat (0)", "ci_kind": "percentile", "source": SRC + "periods.json",
                    "notes": f"AR1 beats RW out of sample for {r['oos']['ar1_beats_rw']:.2f} of {r['oos']['n_agents']} agents"})
        out.append({**common, "statistic": "memory_ar2", "estimate": r["ar2"]["est"], "ci_lo": r["ar2"]["lo"],
                    "ci_hi": r["ar2"]["hi"], "n": r["n_pairs"], "n_kind": "compression-cycle pairs",
                    "method": "AR(2) coefficient, agent-demeaned; agent bootstrap", "null": "0 (first-order loop)",
                    "ci_kind": "percentile", "source": SRC + "periods.json"})
        out.append({**common, "statistic": "memory_setpoint_chars", "estimate": r["mu_median_chars"], "ci_lo": None,
                    "ci_hi": None, "n": r["n_agents"], "n_kind": "agents", "method": "median over agents of exp(mean ln x+)",
                    "null": "none", "ci_kind": "none", "source": SRC + "periods.json"})
        if r["regime"] == "III":
            out.append({**common, "statistic": "memory_mixed_phase_phi", "estimate": r["mixed_phi"], "ci_lo": None,
                        "ci_hi": None, "n": r["n_pairs"], "n_kind": "compression-cycle pairs",
                        "method": "AR(1) on all snapshots (append + compress), H09's statistic", "null": "φ⁺ (same period)",
                        "ci_kind": "none", "source": SRC + "periods.json"})
            out.append({**common, "statistic": "memory_phi_forced_minus_voluntary", "estimate": r["f_minus_v"]["est"],
                        "ci_lo": r["f_minus_v"]["lo"], "ci_hi": r["f_minus_v"]["hi"], "n": r["n_pairs"],
                        "n_kind": "compression-cycle pairs", "method": "φ⁺ on pairs ending in forced vs voluntary consolidations",
                        "null": "0 (no overshoot after erasure)", "ci_kind": "percentile", "source": SRC + "periods.json"})
        q = ph.get(p)
        if q:
            out.append({**common, "statistic": "memory_rho2_minus_rho1sq", "estimate": q["rho2_minus_rho1sq"],
                        "ci_lo": q["rho2_minus_rho1sq_ci"][0], "ci_hi": q["rho2_minus_rho1sq_ci"][1], "n": r["n_pairs"],
                        "n_kind": "compression-cycle pairs", "method": "lag-2 minus squared lag-1 autocorrelation of x+",
                        "null": "0 (single first-order loop)", "ci_kind": "percentile", "post_hoc": True,
                        "source": SRC + "posthoc.json", "notes": f"rho_s {q['rho_s']:.2f}, slow share {q['r_slow']:.2f}"})
    for ne, g, key in (("NE14", 36, ("NE14", "wide")), ("NE04", 12, ("NE04", "paired")), ("NE16", 36, ("NE16", "paired"))):
        d = nat[key[0]][key[1]]
        common = {**base, "role": "native", "period_unit": f"local:{ne}", "goal_no": g, "unit_local": ne,
                  "source": SRC + "natives.json", "n": d["n_agents"], "n_kind": "agents (paired)", "ci_kind": "percentile"}
        out.append({**common, "statistic": "memory_phi_plus_change", "estimate": d["dphi"], "ci_lo": d["dphi_ci"][0],
                    "ci_hi": d["dphi_ci"][1], "method": "paired after - before per-agent φ⁺", "null": "0"})
        out.append({**common, "statistic": "memory_setpoint_dln", "estimate": d["dln_mu"], "ci_lo": d["dln_mu_ci"][0],
                    "ci_hi": d["dln_mu_ci"][1], "method": "paired after - before per-agent mean ln x+", "null": "0"})
    return out


if __name__ == "__main__":
    r = rows()
    E.write_estimates(r, hypothesis="H71")
    print(len(r), "rows written")
