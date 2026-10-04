"""H13 round 1b: collect round 1 vs round-1b numbers (both embedding models, both style rivals, dedupe, fixed talk
table, behavior channel), write r1b/summary.json, per-period estimates (infra/shared/estimates.py) and the page-2 figure.

Usage: uv run python hypotheses/H13-family-fields/analysis/r1b_summary.py [--no-estimates]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
DATA = ROOT / "data/processed/H13-family-fields"
R1B = DATA / "r1b"
FIG = HERE.parent / "figures"
COUNTED = ["35", "36b", "37", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51a", "51b", "51c", "51d"]
TWO_ROOM = {"35", "36b", "37", "38a", "38b", "38c", "39", "41", "42", "44"}
ONE_ROOM = {"40", "51a", "51b", "51c", "51d"}
UNIT_DAYS = {"35": ("2026-03-16", "2026-03-20"), "36b": ("2026-03-24", "2026-03-27"), "37": ("2026-03-30", "2026-04-01"),
             "38a": ("2026-04-02", "2026-04-13"), "38b": ("2026-04-14", "2026-04-17"), "38c": ("2026-04-20", "2026-04-24"),
             "39": ("2026-04-27", "2026-05-01"), "40": ("2026-05-04", "2026-05-08"), "41": ("2026-05-11", "2026-05-15"),
             "42": ("2026-05-18", "2026-05-22"), "44": ("2026-05-26", "2026-05-29"), "51a": ("2026-07-06", "2026-07-08"),
             "51b": ("2026-07-09", "2026-08-04"), "51c": ("2026-08-05", "2026-08-24"), "51d": ("2026-08-25", "2026-09-02"),
             "51e": ("2026-09-03", "2026-09-04")}


def load(p):
    return json.loads(p.read_text()) if p.exists() else None


def digest(ex):
    """The round-1 primary statistics from one explore json."""
    U = ex["units"]
    cu = [u for u in COUNTED if u in U]
    g = lambda u, *k: _get(U[u], k)
    d = {"P1_count": sum(1 for u in cu if (g(u, "a1", "p") or 1) < 0.05), "P1_RE": ex["meta"]["T_field"],
         "P2_count_in_P1": sum(1 for u in cu if (g(u, "a1", "p") or 1) < 0.05 and (g(u, "a2", "p") or 1) < 0.05),
         "P2_RE": ex["meta"]["T_field_style"],
         "P2_median_retention": float(np.nanmedian([g(u, "a2", "retention") if g(u, "a2", "retention") is not None else np.nan
                                                    for u in cu if (g(u, "a1", "p") or 1) < 0.05])),
         "P3": {k: ex["cross"]["a3"][k] for k in ("family_cos", "family_median", "null_regroup_median_mean", "p_regroup", "agent_median")},
         "P4_count": sum(1 for v in ex["cross"]["a4"].values() if (v.get("p_proj") or 1) < 0.05), "P4_n": len(ex["cross"]["a4"]),
         "P5_oneroom_ns": sum(1 for u in cu if u in ONE_ROOM and (g(u, "b1", "p_perm") or 0) >= 0.05),
         "P5_oneroom_n": sum(1 for u in cu if u in ONE_ROOM and g(u, "b1", "p_perm") is not None),
         "P5_tworoom_blab_ns": sum(1 for u in cu if u in TWO_ROOM and (g(u, "c", "y1_talk", "p_lab") or 0) >= 0.05),
         "P5_RE": ex["meta"]["delta_talk"], "P5_RE_oneroom": ex["meta"]["delta_talk_oneroom"],
         "P6_count": sum(1 for u in cu if (g(u, "b2", "p_perm") or 1) < 0.05), "P6_RE": ex["meta"]["delta_content"],
         "P7_y1_room_gt_lab": sum(1 for u in cu if u in TWO_ROOM and (g(u, "c", "y1_talk", "b_room") or 0) > (g(u, "c", "y1_talk", "b_lab") or 0)),
         "P7_y2_lab_p05": sum(1 for u in cu if u in TWO_ROOM and (g(u, "c", "y2_field", "p_lab") or 1) < 0.05),
         "P7_y2_room_p05": sum(1 for u in cu if u in TWO_ROOM and (g(u, "c", "y2_field", "p_room") or 1) < 0.05),
         "P7_y3_room_gt_lab": sum(1 for u in cu if u in TWO_ROOM and (g(u, "c", "y3_comove", "b_room") or 0) > (g(u, "c", "y3_comove", "b_lab") or 0)),
         "P8_loo": sum(1 for u in cu if (g(u, "d1", "p") or 1) < 0.05), "P8_Tlex": sum(1 for u in cu if (g(u, "a5", "T_lex", "p") or 1) < 0.05),
         "P8_newcomers": {k: ex["cross"]["d2"][k] for k in ("accuracy", "chance", "n", "p_binom")},
         "per_unit": {u: {"T": g(u, "a1", "obs"), "p": g(u, "a1", "p"), "se": g(u, "a1", "se_jack"), "T_sty": g(u, "a2", "obs"),
                          "p_sty": g(u, "a2", "p"), "se_sty": g(u, "a2", "se_jack"), "talk_delta": g(u, "b1", "delta"),
                          "talk_p": g(u, "b1", "p_perm"), "talk_se": g(u, "b1", "delta_se"), "talk_ci": g(u, "b1", "delta_ci95"),
                          "content_delta": g(u, "b2", "delta"), "content_p": g(u, "b2", "p_perm"), "N": U[u].get("N"),
                          "y2_p_lab": g(u, "c", "y2_field", "p_lab"), "y2_b_lab": g(u, "c", "y2_field", "b_lab")}
                      for u in U}}
    return d


def _get(r, ks):
    for k in ks:
        if not isinstance(r, dict):
            return None
        r = r.get(k)
    return r


def period_verdict(units, dg):
    """Round-1 rule (period_results.py): failed if no unit detects a family field (a1 p < 0.05 or y2 b_lab p < 0.05);
    otherwise mixed (P2 failed everywhere, so 'supported' is unreachable)."""
    det = [u for u in units if (dg["per_unit"].get(u, {}).get("p") or 1) < 0.05 or (dg["per_unit"].get(u, {}).get("y2_p_lab") or 1) < 0.05]
    return ("mixed" if det else "failed"), det


def main():
    out = {}
    r1 = load(DATA / "explore.json")
    out["round1"] = digest(r1)
    variants = {}
    for name in ("bge_small_none", "gte_modernbert_none", "bge_small_restatements", "gte_modernbert_restatements", "bge_small_copies"):
        ex = load(R1B / name / "explore.json")
        if ex is not None:
            variants[name] = digest(ex)
        exp = load(R1B / name / "explore_styp.json")
        if exp is not None:
            variants[name + "_styp"] = digest(exp)
    out["r1b"] = variants
    beh = load(R1B / "behavior.json")
    if beh is not None:
        out["behavior"] = {"summary": beh["summary"], "NE32": beh["native_NE32"]["summary"], "NE06": {k: v for k, v in beh["native_NE06"].items() if k not in ("pre", "post")},
                           "G35": beh["native_G35"]}
    sty = load(ROOT / "data/processed/shared/embeddings/style_resid_check.json")
    if sty:
        out["dq5_style_check"] = {k: {"n_p05": v["n_p05"], "re": v["re"]} for k, v in sty.items() if isinstance(v, dict) and "n_p05" in v}
    (R1B / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    # console table
    rows = [("round 1 (bge, own S-a, old talk)", out["round1"])] + [(k, v) for k, v in variants.items()]
    for name, d in rows:
        print(f"{name:34s} P1 {d['P1_count']}/15 RE {d['P1_RE']['mu']:.3f} [{d['P1_RE']['lo']:.3f},{d['P1_RE']['hi']:.3f}] | "
              f"P2 {d['P2_count_in_P1']}/{d['P1_count']} RE {d['P2_RE']['mu']:.3f} [{d['P2_RE']['lo']:.3f},{d['P2_RE']['hi']:.3f}] ret {d['P2_median_retention']:.2f} | "
              f"P3 {d['P3']['family_median']:.2f} vs {d['P3']['null_regroup_median_mean']:.2f} p {d['P3']['p_regroup']:.3f} ag {d['P3']['agent_median']:.2f} | "
              f"P4 {d['P4_count']}/{d['P4_n']} | P5 1room ns {d['P5_oneroom_ns']}/{d['P5_oneroom_n']} RE {d['P5_RE']['mu']:.3f} [{d['P5_RE']['lo']:.3f},{d['P5_RE']['hi']:.3f}] | "
              f"P6 {d['P6_count']}/15 RE {d['P6_RE']['mu']:.3f} | y2 lab {d['P7_y2_lab_p05']}/10 room {d['P7_y2_room_p05']}/10 | y3 {d['P7_y3_room_gt_lab']}/10 | "
              f"LOO {d['P8_loo']} new {d['P8_newcomers']['accuracy']:.2f}")
    # period verdicts (1b) on the bge and gte primary variants
    periods = {"G35": ["35"], "G36": ["36b"], "G37": ["37"], "G38": ["38a", "38b", "38c"], "G39": ["39"], "G40": ["40"],
               "G41": ["41"], "G42": ["42"], "G44": ["44"], "G51": ["51a", "51b", "51c", "51d"]}
    pv = {}
    for g, us in periods.items():
        pv[g] = {m: period_verdict(us, variants[m]) for m in ("bge_small_none", "gte_modernbert_none") if m in variants}
    out["period_verdicts_1b"] = pv
    (R1B / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    for g, v in pv.items():
        print(g, v)
    if "--no-estimates" not in sys.argv:
        write_est(out, variants, beh)


def write_est(out, variants, beh):
    import estimates as E
    rows = []
    src = "data/processed/H13-family-fields/r1b/summary.json"
    for model, key in (("bge_small", "bge_small_none"), ("gte_modernbert", "gte_modernbert_none")):
        d = variants.get(key)
        ds = variants.get(key + "_styp")
        if d is None:
            continue
        for u, v in d["per_unit"].items():
            a, b = UNIT_DAYS[u]
            pu = E.map_unit(int(u[:2]), a, b) or f"local:{u}"
            base = {"period_unit": pu, "goal_no": int(u[:2]), "unit_local": u, "first_day": a, "last_day": b, "role": "replication",
                    "source": src, "status": "round 1b", "ci_kind": "jackknife_z", "n_kind": "agents", "n": v["N"]}
            if v["T"] is not None:
                lo, hi = E.ci_from_se(v["T"], v["se"])
                rows.append({**base, "statistic": "family_field_T", "channel": f"content:{model}", "estimate": v["T"], "se": v["se"],
                             "ci_lo": lo, "ci_hi": hi, "method": "within-minus-across family cosine of day-demeaned agent fields (r1b, shared white32)",
                             "null": "lab-label permutation", "notes": f"p={v['p']}"})
            if v["T_sty"] is not None:
                lo, hi = E.ci_from_se(v["T_sty"], v["se_sty"])
                rows.append({**base, "statistic": "family_field_T_style_resid", "channel": f"content:{model}", "estimate": v["T_sty"],
                             "se": v["se_sty"], "ci_lo": lo, "ci_hi": hi, "method": "T_field after H13 within-unit style OLS (S-a), r1b",
                             "null": "lab-label permutation", "notes": f"p={v['p_sty']}"})
            if ds and ds["per_unit"].get(u, {}).get("T_sty") is not None:
                w = ds["per_unit"][u]
                lo, hi = E.ci_from_se(w["T_sty"], w["se_sty"])
                rows.append({**base, "statistic": "family_field_T_style_resid_period", "channel": f"content:{model}", "estimate": w["T_sty"],
                             "se": w["se_sty"], "ci_lo": lo, "ci_hi": hi, "method": "T_field on shared DQ5 style_resid_period vectors",
                             "null": "lab-label permutation", "notes": f"p={w['p_sty']}"})
            if model == "bge_small" and v["talk_delta"] is not None:
                ci = v["talk_ci"] or [None, None]
                rows.append({**base, "statistic": "family_coupling_delta", "channel": "talk:activity_bins_fixed", "estimate": v["talk_delta"],
                             "se": v["talk_se"], "ci_lo": ci[0], "ci_hi": ci[1], "ci_kind": "percentile",
                             "method": "J_in - J_out from family mean-field inversion of talk-spin excess correlations (fixed table)",
                             "null": "lab-label permutation; cross-day surrogate", "notes": f"p={v['talk_p']}"})
    if beh is not None:
        for u, r in beh["units"].items():
            B = r.get("B", {})
            if "field" not in B:
                continue
            a, b = UNIT_DAYS[u]
            pu = E.map_unit(int(u[:2]), a, b) or f"local:{u}"
            f = B["field"]
            lo, hi = E.ci_from_se(f["obs"], f.get("se_jack"))
            rows.append({"period_unit": pu, "goal_no": int(u[:2]), "unit_local": u, "first_day": a, "last_day": b, "role": "replication",
                         "statistic": "family_field_T", "channel": "behavior:jev_v3", "estimate": f["obs"], "se": f.get("se_jack"),
                         "ci_lo": lo, "ci_hi": hi, "ci_kind": "jackknife_z", "n": B["N"], "n_kind": "agents",
                         "method": "within-minus-across family cosine of day-demeaned agent behavior fields (11 Jev v3 state probabilities + 4 rates)",
                         "null": "lab-label permutation", "source": "data/processed/H13-family-fields/r1b/behavior.json",
                         "status": "round 1b (HH267)", "notes": f"p={f['p']}"})
        # natives
        ne = beh["native_NE06"]
        rows.append({"period_unit": "G20", "goal_no": 20, "unit_local": "NE06", "role": "native", "statistic": "family_behavior_DiD_norm",
                     "channel": "behavior:jev_v3", "estimate": ne["behavior"]["D_norm"], "ci_kind": "none", "n": ne["behavior"]["n_agents"],
                     "n_kind": "agents", "method": "|mean change Google - mean change others| across NE06 step 1", "null": "exact treated-label relabeling",
                     "source": "data/processed/H13-family-fields/r1b/behavior.json", "notes": f"percentile={ne['behavior']['percentile']}"})
        n32 = beh["native_NE32"]["summary"]["behavior"]
        rows.append({"period_unit": "G51", "goal_no": 51, "unit_local": "NE32-newcomers", "role": "native", "statistic": "newcomer_family_accuracy",
                     "channel": "behavior:jev_v3", "estimate": n32["accuracy"], "ci_kind": "none", "n": n32["n"], "n_kind": "agents",
                     "method": "newcomer classified by incumbents' behavioral family fields", "null": f"chance {n32['chance']:.3f} (binomial)",
                     "source": "data/processed/H13-family-fields/r1b/behavior.json", "notes": f"p={n32['p_binom']}"})
        g35 = beh["native_G35"]["famroom"]
        rows.append({"period_unit": "35", "goal_no": 35, "unit_local": "35", "role": "native", "statistic": "behavior_b_lab_given_room",
                     "channel": "behavior:jev_v3", "estimate": g35["b_lab"], "se": g35.get("se_lab"), "ci_kind": "none", "n": g35["n_pairs"],
                     "n_kind": "pairs", "method": "pair OLS of behavior-field alignment on same-lab and same-room", "null": "node permutation",
                     "source": "data/processed/H13-family-fields/r1b/behavior.json", "notes": f"p_lab={g35['p_lab']}; b_room={g35['b_room']}"})
    w = E.write_estimates(rows, hypothesis="H13")
    print("estimates written:", w.height)


if __name__ == "__main__":
    main()
