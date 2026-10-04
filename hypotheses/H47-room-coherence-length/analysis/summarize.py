"""Collect H47 round-1 results into summary.json (outcome vs prediction inputs) and run the post hoc cross-period
checks (labelled post hoc): C_B vs instruction type (room kickoff identity from shared goal_fields) and C_B vs
between-room separation.

Usage: uv run python hypotheses/H47-room-coherence-length/analysis/summarize.py
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402

import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

RES = L.OUT / "results"
# room kickoff identity (shared goal_fields, kind kickoff_room): cos 1.0 = identical text in both rooms
INSTR = {"G35": "forks", "G36": "identical", "G37": "identical", "G38": "room-specific", "G39": "identical",
         "G41": "identical", "G42": "identical", "G44": "room-specific", "G51": "self-made room"}


def load(name):
    return json.loads((RES / f"{name}.json").read_text())


def main():
    coh, sep, ne, g51, det, lead = (load(n) for n in ("coherence", "separation", "ne42", "g51", "detector", "leadership"))
    rows = {}
    for g, r in coh.items():
        o = r["w30"]["obs"]
        rows[g] = dict(units=r["units"], rho_w=o["rho_w"], rho_c=o["rho_c"], C_B=o["C_B"], p_DB=r["w30"].get("p_DB"),
                       G=o.get("G"), p_G=r["w30"].get("p_G_low"), verdict_rule=r["verdict_rule"],
                       C_B_day=(r["day"]["obs"]["C_B"] if r["day"] else None), p_day=(r["day"].get("p_DB") if r["day"] else None),
                       C_B_ci=r["w30"].get("boot_ci", {}).get("C_B"),
                       rob={k: (v["obs"]["C_B"] if v else None) for k, v in r["robust"].items() if k != "L1_instr_only"},
                       instr_share_all=r["instr_share_all"], instr_share_instr=r["instr_share_instr"],
                       n_agents=r["w30"]["n_agents"], n_stmt=r["w30"]["n_stmt"], instr=INSTR.get(g),
                       sep_median_F=(float(np.median([d["F"] for d in sep[g]["days"]])) if g in sep else None),
                       sep_day0=(sep[g]["days"][0]["F"] if g in sep else None))
    two = [g for g in rows if g != "G51"]
    cbs = np.array([rows[g]["C_B"] for g in rows], float)
    n_sup = sum(rows[g]["verdict_rule"] == "supported" for g in rows)
    out = dict(periods=rows, n_periods=len(rows), n_supported=n_sup,
               n_mixed=sum(rows[g]["verdict_rule"] == "mixed" for g in rows),
               n_failed=sum(rows[g]["verdict_rule"] == "failed" for g in rows),
               median_C_B=float(np.median(cbs)), median_G=float(np.median([rows[g]["G"] for g in rows])),
               sharp_count=int(sum((rows[g]["G"] or -9) > rows[g]["C_B"] for g in rows)))
    out["claim1"] = "supported" if (n_sup >= 2 / 3 * len(rows) and out["median_C_B"] <= 0.3) else "not supported"
    # ---- post hoc 1: instruction type (two-room periods with a room kickoff; G35 forks counted room-specific in a variant)
    def exact_low(groups_low, pool):
        vals = {g: rows[g]["C_B"] for g in pool}
        obs = np.mean([vals[g] for g in groups_low])
        k = len(groups_low)
        combs = list(itertools.combinations(pool, k))
        null = [np.mean([vals[g] for g in c]) for c in combs]
        return float(obs), float(np.mean([x <= obs + 1e-12 for x in null])), len(combs)
    pool7 = ["G36", "G37", "G38", "G39", "G41", "G42", "G44"]
    pool8 = pool7 + ["G35"]
    m, p, n = exact_low(["G38", "G44"], pool7)
    m2, p2, n2 = exact_low(["G38", "G44", "G35"], pool8)
    ident = [rows[g]["C_B"] for g in pool7 if INSTR[g] == "identical"]
    out["posthoc_instruction"] = dict(mean_CB_room_specific=m, p_exact=p, n_perm=n, mean_CB_identical=float(np.mean(ident)),
                                      median_CB_identical=float(np.median(ident)), with_forks=dict(mean=m2, p_exact=p2, n_perm=n2))
    # ---- post hoc 2: separation vs C_B across two-room periods
    sg = [g for g in two if rows[g]["sep_median_F"] is not None]
    x = np.array([rows[g]["sep_median_F"] for g in sg]); y = np.array([rows[g]["C_B"] for g in sg])
    rho = spearmanr(x, y).statistic
    rng = np.random.default_rng(L.SEED)
    null = np.array([spearmanr(x, rng.permutation(y)).statistic for _ in range(5000)])
    out["posthoc_separation"] = dict(periods=sg, spearman=float(rho), p_perm_two_sided=float(np.mean(np.abs(null) >= abs(rho) - 1e-12)))
    # ---- native
    out["ne42"] = dict(r_X={u: ne["obs"][u]["r_X"] for u in ne["obs"]}, DiD=ne["DiD"], p_DiD=ne["p_DiD"], DiD_ci=ne["DiD_ci"],
                       p_unit_low=ne["p_unit_low"], n_part=ne["n_part"])
    out["g51"] = dict(r_F={u: v["r_F"] for u, v in g51["r_F"].items()}, DiD=g51["DiD"], p_DiD_low=g51["p_DiD_low"],
                      focus_members=g51["focus_members"], median_G_single=g51["median_G_single"],
                      G_single={u: v["G"] for u, v in g51["single_room_G"].items()})
    out["separation"] = {g: dict(day0_F=v["day0_F"], day0_z=v["day0_z"], median_F=v["median_F"], spearman=v["spearman_F_day"]) for g, v in sep.items()}
    out["detector"] = dict(all=det["all_room_events"], clean=det["clean_room_events"], placebo_n=det["placebo_n"],
                           events={e["ref"]: {k: e.get(k) for k in ("day0", "goal_confounded", "R1_d0", "R1_room_d0", "R1_loc_d0", "R1_hit", "R1_room_hit", "R1_loc_hit", "rooms_d0", "loc_best_d0")} for e in det["events"]},
                           goal_kickoffs=det["goal_kickoffs"])
    out["leadership"] = {k: ({kk: v[kk] for kk in ("L", "p_L", "dT50_bins", "p_T50", "L_ci", "z", "n_best", "n_rest", "n_stmt_day0", "y_noise_sd", "cohorts")}
                             if k.startswith("#") else v) for k, v in lead.items()}
    syn = json.loads((L.OUT / "synthetic/synthetic_summary.json").read_text())
    out["synthetic"] = {k: syn[k] for k in ("coherence", "aba", "detector", "leadership")}
    cal = L.OUT / "synthetic/lead_calibrated_posthoc.json"
    if cal.exists():
        out["synthetic"]["lead_calibrated_posthoc"] = json.loads(cal.read_text())
    L.jdump(out, RES / "summary.json")
    print(json.dumps({k: out[k] for k in ("n_periods", "n_supported", "n_mixed", "n_failed", "median_C_B", "median_G", "sharp_count", "claim1",
                                          "posthoc_instruction", "posthoc_separation")}, indent=1))


if __name__ == "__main__":
    main()
