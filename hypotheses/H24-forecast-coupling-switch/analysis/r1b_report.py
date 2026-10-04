"""H24 round 1b: collect the corrected-input runs of explore.py (G21/r1b/explore_<tag>.json) next to round 1, apply the
round-1 verdict rules to each configuration, and write G21/r1b/report.json (+ a printed table for the card).

P1 (literal H24): dA_res(a) > q90 of N1 and of N2. P2 docs dA_res > 0. P3 snapshot betaJ0/n rises. P6 ramp rho > 0.
Usage: uv run python hypotheses/H24-forecast-coupling-switch/analysis/r1b_report.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h24lib import H24  # noqa: E402

G = H24 / "G21"


def row(tag, d, n2_list=None):
    a = d["O1"]["n32_ghat"]["a_all"]["res"]
    n2 = [x["res"]["dA"] for x in d["N2"]] if "N2" in d else []
    q90_n2 = float(np.quantile(n2, 0.9)) if n2 else np.nan
    docs = d["O1"]["n32_ghat"]["c_docs_all"]["res"]
    own = d["O1"]["n32_ghat"]["c_docs_own"]["res"]
    fc = d["O1"]["n32_ghat"]["b_forecast"]["res"]
    r = {"tag": tag, "dA_res": a["dA"], "dA_ci90": a["boot"]["dA_ci90"], "N1_q90": a["N1_q90"], "N2_q90": q90_n2,
         "N2_median": float(np.median(n2)) if n2 else np.nan, "N2_n": len(n2), "A_pre": a["A_pre"], "A_post": a["A_post"],
         "rot_q95_pre": a["N3_rot"]["A_pre_q95"], "bJ_pre": a["bJ_pre"], "bJ_post": a["bJ_post"],
         "dbJ_ci90": a["boot"]["dbJ_ci90"],
         "dA_raw": d["O1"]["n32_ghat"]["a_all"]["raw"]["dA"], "docs_dA_res": docs["dA"] if docs else None,
         "docs_ci90": docs["boot"]["dA_ci90"] if docs else None, "docs_own_dA_res": own["dA"] if own else None,
         "forecast_dA_res": fc["dA"] if fc else None, "ramp_rho": d["O3"]["rho"], "ramp_p": d["O3"]["p"],
         "step_1204": d["O3"]["step_1204"], "control_DiD": d.get("control_did", {}).get("DiD"),
         "n_statements": d.get("n_statements")}
    for t in ("n16_ghat", "n64_ghat", "n32_goal", "n32_kickoff"):
        if t in d["O1"] and d["O1"][t]["a_all"]["res"]:
            r[f"dA_res_{t}"] = d["O1"][t]["a_all"]["res"]["dA"]
    r["P1_pass"] = bool(r["dA_res"] > r["N1_q90"] and r["dA_res"] > r["N2_q90"])
    r["P1_above_N1"] = bool(r["dA_res"] > r["N1_q90"])
    r["P1_above_N2"] = bool(r["dA_res"] > r["N2_q90"])
    r["P3_rise"] = bool(r["dbJ_ci90"][0] > 0)
    return r


def main():
    rows = []
    r1 = json.loads((G / "explore.json").read_text())
    rows.append(row("round1 (bge, H24 g-hat, 1-d)", r1))
    for f in sorted((G / "r1b").glob("explore_*.json")):
        rows.append(row(f.stem.replace("explore_", ""), json.loads(f.read_text())))
    (G / "r1b" / "report.json").write_text(json.dumps(rows, indent=1, default=float))
    print("| config | dA_res [90% CI] | N1 q90 | N2 q90 | A_pre / A_post | betaJ0/n pre -> post | docs dA_res | ramp rho | P1 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        print(f"| {r['tag']} | {r['dA_res']:+.3f} [{r['dA_ci90'][0]:+.3f}, {r['dA_ci90'][1]:+.3f}] | {r['N1_q90']:.3f} | "
              f"{r['N2_q90']:.3f} | {r['A_pre']:.2f} / {r['A_post']:.2f} | {r['bJ_pre']:.2f} -> {r['bJ_post']:.2f} | "
              f"{r['docs_dA_res']:+.3f} | {r['ramp_rho']:.2f} | {'pass' if r['P1_pass'] else 'fail'} |")


if __name__ == "__main__":
    main()
