"""H32 cross-period synthesis: evaluates the card's predictions P1-P12 from the per-period results.

Reads data/processed/H32-information-current-leaders/G<NN>/result.json (primary, pre-registered settings) and
result_A2.json (post-hoc sensitivity), segments.json, ne42.json, robust.json, synthetic/synthetic_summary.json.
Writes crossperiod.json. Comparing periods by their fitted parameters (T, Phi, rho) is the allowed cross-period
comparison (CLAUDE.md: periods as points on a phase diagram); nothing is fitted to pooled periods.

Usage: uv run python hypotheses/H32-information-current-leaders/analysis/synthesize.py
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, mannwhitneyu, spearmanr

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data/processed/H32-information-current-leaders"


def load(tag=""):
    out = {}
    for f in sorted(glob.glob(str(DATA / "G*" / ("result.json" if not tag else f"result_{tag}.json")))):
        r = json.loads(Path(f).read_text())
        out[int(r["goal_no"])] = r
    return out


def med(x):
    x = [v for v in x if v is not None and np.isfinite(v)]
    return float(np.median(x)) if x else None


def tests(E: dict, seg: dict) -> dict:
    R = {}
    gs = sorted(E)
    sigT = [g for g in gs if E[g]["p_T"] < 0.05]
    both = [g for g in sigT if E[g].get("withinday", {}).get("p_T", 1) < 0.05]
    R["P1"] = {"n_periods": len(gs), "n_sig": len(sigT), "frac": len(sigT) / len(gs), "n_sig_both_nulls": len(both),
               "sig": sigT, "sig_both": both, "pass": len(sigT) / len(gs) >= 0.6}
    if any("p_T_trim" in E[g] for g in gs):
        st = [g for g in gs if E[g].get("p_T_trim", 1) < 0.05]
        R["P1_trimmed"] = {"n_sig": len(st), "frac": len(st) / len(gs), "sig": st}
    called = [g for g in sigT if E[g]["p_standout"] < 0.05 and E[g]["p_max"] < 0.05]
    st_only = [g for g in sigT if E[g]["p_standout"] < 0.05]
    R["P2"] = {"n_called_among_sig": len(called), "called": called, "n_standout": len(st_only), "of": len(sigT),
               "pass": len(st_only) / max(len(sigT), 1) >= 0.5}
    sh = {g: E[g]["split_half"]["rho_out"] for g in gs if E[g].get("split_half") and E[g]["split_half"].get("rho_out") is not None}
    pos = sum(v > 0 for v in sh.values())
    R["P3"] = {"n_eligible": len(sh), "n_pos": pos, "median_rho": med(list(sh.values())), "rho": sh,
               "sign_p": float(binomtest(pos, len(sh), 0.5, alternative="greater").pvalue) if sh else None,
               "pass": bool(sh) and pos / len(sh) >= 2 / 3 and med(list(sh.values())) >= 0.3}
    shn = {g: E[g]["split_half"].get("rho_net") for g in sh}
    R["P3_net"] = {"median_rho_net": med(list(shn.values())), "n_pos": sum((v or 0) > 0 for v in shn.values())}
    rc = {g: E[g]["rho"]["count"] for g in gs}
    R["P4"] = {"median_rho_out_count": med(list(rc.values())), "pass_part1": (med(list(rc.values())) or 1) < 0.8}
    hum = {g: E[g]["human"] for g in gs if E[g].get("human") and E[g]["human"].get("n_msgs", 0) >= 15 and E[g]["human"].get("rank_out")}
    above = [g for g, h in hum.items() if h["above_median_agent"]]
    R["P5"] = {"n_periods": len(hum), "n_above_median": len(above), "above": above,
               "ranks": {g: [h["rank_out"], len(E[g]["nodes"]) + 1, h["rank_count"], round(h["p"], 3)] for g, h in hum.items()},
               "n_sig_positive": sum(h["p"] < 0.05 for h in hum.values()),
               "pass": len(above) / max(len(hum), 1) >= 0.7}
    better_by_out = sum(h["rank_out"] < h["rank_count"] for h in hum.values())
    R["P4_part2_humans"] = {"rank_out_better_than_count": better_by_out, "of": len(hum)}
    if seg:
        post = seg["G26_post"]; srt = sorted(post, key=lambda a: -np.nan_to_num(post[a]["dG"], nan=-9))
        o = E[26]["out"]; k = E[26]["nodes"].index(17)
        rank_w = int(1 + np.sum(np.array(o) > o[k]))
        R["P6"] = {"a_rank_whole_week": rank_w, "a_pass": rank_w > 3, "b_rank_post": srt.index("17") + 1, "b_of": len(srt),
                   "b_pass": srt.index("17") == 0, "post_top": srt[:3],
                   "post_dG": {a: post[a]["dG"] for a in srt}, "post_z": {a: post[a]["z"] for a in srt},
                   "pre_rank": sorted(seg["G26_pre_days1to4"], key=lambda a: -np.nan_to_num(seg["G26_pre_days1to4"][a]["dG"], nan=-9)).index("17") + 1}
        b = seg["G44_best_0528_29"]; srt = sorted(b, key=lambda a: -np.nan_to_num(b[a]["dG"], nan=-9))
        ag = [a for a in srt if a != "100"]
        r44 = E[44]
        same, cross = r44.get("pairs_same_room", {}), r44.get("pairs_cross_room_unseen", {})
        R["P7"] = {"a_rank28": ag.index("28") + 1, "a_of": len(ag), "a_pass": ag.index("28") + 1 >= 3,
                   "b_rank_humans": srt.index("100") + 1, "b_of": len(srt), "b_pass": srt.index("100") == 0, "order": srt,
                   "dG": {a: b[a]["dG"] for a in srt}, "z": {a: b[a]["z"] for a in srt},
                   "c_same": same, "c_cross_unseen": cross,
                   "c_pass": bool(same.get("mean") is not None and cross.get("mean") is not None and same["mean"] > cross["mean"]
                                  and cross["ci90"][0] <= 0 <= cross["ci90"][1])}
    mr = [g for g in gs if "T_unseen" in E[g]]
    if mr:
        d = [E[g]["T_seen_beyond_unseen"] - E[g]["T_unseen"] for g in mr]
        R["P8"] = {"periods": mr, "T_seen_beyond_unseen": {g: E[g]["T_seen_beyond_unseen"] for g in mr},
                   "T_unseen": {g: E[g]["T_unseen"] for g in mr}, "p_unseen": {g: E[g]["p_T_unseen"] for g in mr},
                   "p_sbu": {g: E[g]["p_T_seen_beyond_unseen"] for g in mr},
                   "n_seen_gt_unseen": int(sum(x > 0 for x in d)),
                   "sign_p": float(binomtest(int(sum(x > 0 for x in d)), len(d), 0.5, alternative="greater").pvalue),
                   "n_unseen_sig": int(sum(E[g]["p_T_unseen"] < 0.05 for g in mr)), "n_sbu_sig": int(sum(E[g]["p_T_seen_beyond_unseen"] < 0.05 for g in mr))}
        R["P8"]["pass"] = R["P8"]["sign_p"] < 0.1 and R["P8"]["n_unseen_sig"] <= 1
    ne = json.loads((DATA / "ne42.json").read_text()) if (DATA / "ne42.json").exists() else {}
    if ne:
        R["P9"] = {**ne, "pass": ne["split_pairs"].get("p_sign", 1) < 0.10 and ne["split_pairs"].get("mean_diff", 0) > 0}
    C_ = [E[g]["T"] for g in gs if E[g]["meta"]["mode"] == "C"]
    IF = [E[g]["T"] for g in gs if E[g]["meta"]["mode"] in ("I", "F")]
    u = mannwhitneyu(C_, IF, alternative="greater")
    phiC = [E[g]["cent_nullvar"]["phi"] for g in sigT if E[g]["meta"]["mode"] == "C" and np.isfinite(E[g]["cent_nullvar"]["phi"])]
    phiIF = [E[g]["cent_nullvar"]["phi"] for g in sigT if E[g]["meta"]["mode"] in ("I", "F") and np.isfinite(E[g]["cent_nullvar"]["phi"])]
    u2 = mannwhitneyu(phiC, phiIF, alternative="greater") if phiC and phiIF else None
    N = [len(E[g]["nodes"]) for g in gs]; T = [E[g]["T"] for g in gs]
    R["P10"] = {"T_median_C": med(C_), "T_median_IF": med(IF), "a_p": float(u.pvalue), "a_pass": u.pvalue < 0.10,
                "phi_median_C": med(phiC), "phi_median_IF": med(phiIF), "b_p": float(u2.pvalue) if u2 else None,
                "b_pass": bool(u2 and u2.pvalue < 0.10), "c_rho_T_N": float(spearmanr(N, T).statistic),
                "c_pass": spearmanr(N, T).statistic < 0,
                "phi_by_period": {g: E[g]["cent_nullvar"]["phi"] for g in sigT}}
    h02 = {g: E[g]["rho"]["h02_zI"] for g in gs if E[g]["rho"].get("h02_zI") is not None}
    R["P11"] = {"n": len(h02), "median_abs_rho": med([abs(v) for v in h02.values()]), "median_rho": med(list(h02.values())),
                "rho": h02, "pass": (med([abs(v) for v in h02.values()]) or 1) < 0.3}
    art = {g: E[g]["rho"]["artifact_adopt"] for g in gs if E[g]["rho"].get("artifact_adopt") is not None}
    men = {g: E[g]["rho"]["mention_indeg"] for g in gs if E[g]["rho"].get("mention_indeg") is not None}
    R["P12"] = {"median_rho_artifact": med(list(art.values())), "n_art": len(art), "median_rho_mention": med(list(men.values())),
                "n_men": len(men), "a_pass": (med(list(art.values())) or 0) > 0, "b_pass": (med(list(men.values())) or 0) > 0}
    h29 = {g: E[g]["rho"].get("h29_net") for g in gs if E[g]["rho"].get("h29_net") is not None}
    R["H29_descriptive"] = {"rho_out_vs_h29_net": h29, "median": med(list(h29.values())),
                            "rho_out_vs_h29_D": {g: E[g]["rho"].get("h29_D") for g in h29}}
    R["top_sources"] = {g: {"top_out": E[g]["leader_call"]["top_out_name"], "z": E[g]["leader_call"]["z_top"],
                            "top_net": E[g]["leader_call"]["top_net_name"], "p_standout": E[g]["p_standout"],
                            "T": E[g]["T"], "p_T": E[g]["p_T"], "phi": E[g]["cent_nullvar"]["phi"], "mode": E[g]["meta"]["mode"]}
                        for g in gs}
    return R


def main():
    E = load()
    seg = json.loads((DATA / "segments.json").read_text()) if (DATA / "segments.json").exists() else {}
    res = {"primary": tests(E, seg)}
    A2 = load("A2")
    if len(A2) == len(E):
        res["A2_posthoc"] = tests(A2, seg)
    rob = json.loads((DATA / "robust.json").read_text()) if (DATA / "robust.json").exists() else []
    if rob:
        by = {}
        for x in rob:
            by.setdefault(x["variant"], []).append(x)
        res["robust"] = {v: {"n_sig": sum(x["p_T"] < 0.05 for x in xs), "n": len(xs),
                             "median_rho_vs_primary": med([x["rho_out_vs_primary"] for x in xs]),
                             "same_top": sum(x["top"] == E[x["g"]]["leader_call"]["top_out"] for x in xs)}
                         for v, xs in by.items()}
    (DATA / "crossperiod.json").write_text(json.dumps(res, indent=1, default=float))
    p = res["primary"]
    for k in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12"):
        if k in p:
            print(k, {kk: vv for kk, vv in p[k].items() if not isinstance(vv, dict) or kk in ("c_same", "c_cross_unseen")})
    if "A2_posthoc" in res:
        a = res["A2_posthoc"]
        print("A2 P1", a["P1"]["n_sig"], a.get("P1_trimmed"), "P3", a["P3"]["median_rho"], a["P3"]["n_pos"], "/", a["P3"]["n_eligible"],
              "P5", a["P5"]["n_above_median"], "/", a["P5"]["n_periods"], "P10a p", a["P10"]["a_p"], "P8", a.get("P8", {}).get("n_seen_gt_unseen"))
    if "robust" in res:
        print("robust", res["robust"])


if __name__ == "__main__":
    main()
