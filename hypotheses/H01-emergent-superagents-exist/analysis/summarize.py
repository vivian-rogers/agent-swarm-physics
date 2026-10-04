"""Collect the exploratory JSONs into: robustness_summary.json, outcome_rows.json (P1-P9 table for the summary page)
and per-goal-period result files data/processed/H01-emergent-superagents-exist/G##/results.json (+ NE32/).

Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import OUT  # noqa: E402

import numpy as np  # noqa: E402


def J(name):
    p = OUT / name
    return json.loads(p.read_text()) if p.exists() else None


def main():
    ex = J("explore.json")
    variants = {"primary (bge, d32, k40, first-day h)": "explore.json", "cross-fitted h": "explore_hcross.json",
                "k = 20": "explore_k20.json", "k = 80": "explore_k80.json", "per-message weights": "explore_wmsg.json",
                "d = 16": "explore_d16.json", "d = 64": "explore_d64.json", "lexical (tf-idf) swap": "explore_lex.json",
                **{f"seed +{s}": f"explore_seed{s}.json" for s in (1, 2, 3, 4)}}
    rob = {}
    for name, f in variants.items():
        r = J(f)
        if not r:
            continue
        e = {}
        if "p1" in r:
            e["P1_median_dH"] = r["p1"]["P1"]["median_dH"]; e["P1_frac_neg"] = r["p1"]["P1"]["frac_dH_neg"]
            e["P1_frac_p05"] = r["p1"]["P1"]["frac_p05"]; e["P1_pass"] = r["p1"]["P1"]["pass"]
            e["P3_frac_below"] = r["p1"]["P3"]["frac_below_q05"]
            if r["p1"].get("P2"):
                e["P2_lab_shrink"] = r["p1"]["P2"]["lab_shrink"]; e["P2_room_shrink"] = r["p1"]["P2"]["room_shrink"]
        if "p56" in r:
            re_ = r["p56"]["P6"]["re_slope"]
            e.update({"P6_mu": re_["mu"], "P6_se": re_["se"], "P6_p": re_["p_two"], "P6_I2": re_["I2"],
                      "P6_frac_pos": r["p56"]["P6"]["frac_pos"], "P5_n_ge_0.6": r["p56"]["P5"]["n_ge_0.6"],
                      "P5_median_r2": r["p56"]["P5"]["median_r2"], "P5_median_r2_rot": r["p56"]["P5"]["median_r2_rot"],
                      "P6_dir1": r["p56"]["P6"]["re_dir_lo_saw_hi"]["mu"], "P6_dir1_p": r["p56"]["P6"]["re_dir_lo_saw_hi"]["p_two"],
                      "P6_dir2": r["p56"]["P6"]["re_dir_hi_saw_lo"]["mu"], "P6_dir2_p": r["p56"]["P6"]["re_dir_hi_saw_lo"]["p_two"],
                      "P7_did": r["p56"]["P7"]["new"]["did"], "P7_p_perm": r["p56"]["P7"]["new"].get("p_perm_one_sided")})
        if "p9" in r:
            e["P9_median"] = r["p9"]["P9"]["median_bJn"]; e["P9_n_ge_half"] = r["p9"]["P9"]["n_bJn_ge_0.5"]; e["P9_n_units"] = r["p9"]["P9"]["n_units"]
        rob[name] = e
    seeds = [rob[k]["P1_median_dH"] for k in rob if k.startswith("seed") or k.startswith("primary")]
    rob["_P1_seed_spread"] = {"values": seeds, "mean": float(np.mean(seeds)), "sd": float(np.std(seeds, ddof=1)) if len(seeds) > 1 else None}
    (OUT / "robustness_summary.json").write_text(json.dumps(rob, indent=1))

    P1 = ex["p1"]["P1"]; P2 = ex["p1"]["P2"]; P3 = ex["p1"]["P3"]; P4 = ex["p4"].get("P4"); P5 = ex["p56"]["P5"]
    P6 = ex["p56"]["P6"]; P7 = ex["p56"]["P7"]; P8 = ex["p8"]; P9 = ex["p9"]["P9"]
    re_ = P6["re_slope"]
    rows = [
        ["P1", "rooms below random on >= 60% of days AND median dH <= -0.1 nats",
         f"{P1['frac_dH_neg']*100:.0f}% of {P1['n_days']} days < 0 (p<.05 on {P1['frac_p05']*100:.0f}%); median {P1['median_dH']:.3f}", "not met (size; direction strong)"],
        ["P2", "labs below random; removing h_i shrinks lab dH >= 50%, room dH < 50%",
         f"labs {P2['lab_raw']['frac_dH_neg']*100:.0f}% < 0, median {P2['lab_raw']['median_dH']:.3f}; shrink labs {P2['lab_shrink']*100:.0f}%, rooms {P2['room_shrink']*100:.0f}%", "failed"],
        ["P3", "room JSD day-to-day < null 5th pct on >= 60% of day pairs",
         f"{P3['frac_below_q05']*100:.0f}% of {P3['n_room_day_pairs']} pairs; median null pct {P3['median_pct']:.2f}", "failed"],
        ["P4", "#8 polarization along g-hat high, #21 lower",
         f"#8 {P4['pol_g_8']:.3f} vs #21 {P4['pol_g_21']:.3f} (ranks {P4['rank_8']}, {P4['rank_21']} of {P4['n_regime_I_units']})", "not as predicted"],
        ["P5", "fields explain >= 60% of a_ij variance in >= 2/3 of units",
         f"{P5['n_ge_0.6']}/{P5['n_units']} units; median R2 {P5['median_r2']:.2f} vs rotation null {P5['median_r2_rot']:.2f}", "met by the letter; null-level"],
        ["P6", "exposure slope > 0 in >= 2/3 units, RE > 0 at p < .01; both directions; within > cross",
         f"{P6['n_pos']}/{P6['n_units']} > 0; RE {re_['mu']:+.4f} (p={re_['p_two']:.3f}; rot p={re_['p_rot_null']:.3f}); dirs p={P6['re_dir_lo_saw_hi']['p_two']:.4f}/{P6['re_dir_hi_saw_lo']['p_two']:.4f}; rooms {sum(v['within_minus_cross']>0 for v in P6['two_room'].values())}/{len(P6['two_room'])}", "not met (RE p > .01)"],
        ["P7", "merge: new pairs' residual rises vs stay; GPT-5 no rise (direction)",
         f"DiD {P7['new']['did']:+.3f} (perm p={P7['new']['p_perm_one_sided']:.3f}); GPT-5 cut arm {P7['g5_cut']['did']:+.3f}", "as predicted (confounded)"],
        ["P8", "triplet: g-alignment ~ incumbents; high mutual; residual with incumbents rises",
         "no statements while isolated; post-merge 07-09: mutual 0.25-0.47 (inc. q90 0.28); residual w/ incumbents below inc-inc, rises only by 07-16/17", "not estimable as designed"],
        ["P9", "beta*J0 < 0.5 n in every unit, h carries the order",
         f"median beta*J0/n {P9['median_bJn']:.2f}; {P9['n_bJn_ge_0.5']}/{P9['n_units']} units >= 0.5 (upper bound: co-fluctuation is within rooms)", "failed"],
    ]
    (OUT / "outcome_rows.json").write_text(json.dumps(rows, indent=1))

    # per-goal-period result files
    gm = {}
    for u in ex["p9"]["units"]:
        g = int("".join(ch for ch in u if ch.isdigit()))
        gm.setdefault(g, []).append(u)
    exh = J("explore_hcross.json")
    for g, units in gm.items():
        d = OUT / f"G{g:02d}"; d.mkdir(exist_ok=True)
        res = {"goal_no": g, "units": units,
               "P1_days": [x for x in ex["p1"]["days"] if x["unit"] in units],
               "P1_per_unit": {u: ex["p1"]["per_unit"][u] for u in units if u in ex["p1"]["per_unit"]},
               "P3_pairs": [x for x in ex["p1"]["p3_pairs"] if x["unit"] in units],
               "P4": {u: ex["p4"]["units"][u] for u in units if u in ex["p4"]["units"]},
               "P5_P6": {u: ex["p56"]["per_unit"][u] for u in units if u in ex["p56"]["per_unit"]},
               "P5_P6_crossfit_h": {u: exh["p56"]["per_unit"][u] for u in units if exh and u in exh["p56"]["per_unit"]},
               "P9": {u: ex["p9"]["units"][u] for u in units},
               "P9_rooms": {u: ex.get("p9_rooms", {}).get(u) for u in units if u in ex.get("p9_rooms", {})}}
        if g in (39, 40):
            res["P7_merge"] = P7
        (d / "results.json").write_text(json.dumps(res, indent=1, default=str))
    d = OUT / "NE32"; d.mkdir(exist_ok=True)
    (d / "results.json").write_text(json.dumps(P8, indent=1, default=str))
    print(json.dumps(rob, indent=1)[:4000])


if __name__ == "__main__":
    main()
