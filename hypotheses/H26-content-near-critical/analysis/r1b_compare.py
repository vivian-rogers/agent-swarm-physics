"""H26 round 1b: round-1 headline statistics vs each round-1b run (summary.json), side by side -> r1b/compare.json.

Runs: old_check (round-1 activity table, shared goal fields, H26 dedupe rule), bge_fixed / gte_fixed (fixed activity
table, DQ5 restatement dedupe), bge_fixed_trim (activity trimmed to the all-present window).
Usage: uv run python hypotheses/H26-content-near-critical/analysis/r1b_compare.py
"""
from __future__ import annotations

import json
from pathlib import Path

D = Path(__file__).resolve().parents[3] / "data/processed/H26-content-near-critical"
RUNS = ["old_check", "bge_fixed", "gte_fixed", "bge_fixed_trim"]


def pick(S):
    m = lambda k: (S.get(k) or {}).get("median")  # noqa: E731
    ci = lambda k: (S.get(k) or {}).get("ci")  # noqa: E731
    out = {}
    for res in ("day", "w30"):
        out[f"gc_{res}"] = m(f"median_gc_{res}"); out[f"gc_{res}_ci"] = ci(f"median_gc_{res}")
        out[f"ga_{res}"] = m(f"median_ga_{res}"); out[f"gk_{res}"] = m(f"median_gk_{res}")
        out[f"dg_ca_{res}"] = m(f"median_dg_ca_{res}"); out[f"dg_ca_{res}_ci"] = ci(f"median_dg_ca_{res}")
        out[f"dg_ck_{res}"] = m(f"median_dg_ck_{res}")
        out[f"n_dg_ca_{res}_gt015"] = S.get(f"n_dg_ca_{res}_gt015")
        out[f"n_gc_ge05_{res}"] = S.get(f"n_gc_ge05_{res}")
        out[f"gc_pooled_{res}"] = m(f"median_gc_pooled_{res}"); out[f"ga_pooled_{res}"] = m(f"median_ga_pooled_{res}")
        out[f"gk_pooled_{res}"] = m(f"median_gk_pooled_{res}")
        out[f"rho_c_act_{res}"] = m(f"median_rho_c_activity_{res}"); out[f"rho_c_cont_{res}"] = m(f"median_rho_c_content_{res}")
    out["n_N2_day"] = S.get("n_N2_content_day_p05"); out["n_N2_w30"] = S.get("n_N2_content_w30_p05")
    out["h01_p9"] = m("median_h01_p9"); out["c_w30_L4"] = m("median_c_w30_L4")
    out["exo_range"] = S.get("drive_share_day_excess_range")
    out["n_supported"] = S.get("n_supported"); out["outcome"] = S.get("outcome"); out["verdicts"] = S.get("verdicts")
    return out


def main():
    res = {"r1": pick(json.loads((D / "summary.json").read_text()))}
    for r in RUNS:
        p = D / "r1b" / r / "summary.json"
        if p.exists():
            res[r] = pick(json.loads(p.read_text()))
    (D / "r1b" / "compare.json").write_text(json.dumps(res, indent=1))
    cols = list(res)
    for k in res["r1"]:
        if k == "verdicts":
            continue
        print(k.ljust(18), " | ".join(str(res[c].get(k) if not isinstance(res[c].get(k), float) else round(res[c][k], 3))[:24].rjust(14) for c in cols))
    for c in cols:
        print(c, res[c]["verdicts"])


if __name__ == "__main__":
    main()
