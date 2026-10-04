"""H22 round 1b: round 1 vs round-1b numbers per unit (both embedding models, style-residualized vectors, dedupe,
fixed talk table, DQ6 roles, H22's and the shared #51 splits), the stance channel and natives; random-effects
summaries over the counted #51 units; writes r1b/summary.json and per-period estimates.

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/r1b_summary.py [--no-estimates]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h22lib as L  # noqa: E402

DATA = ROOT / "data/processed/H22-private-goals-spin-glass"
R1B = DATA / "r1b"
H22U = {"51a": "G51", "51b": "G51", "51c": "G51", "51d": "G51", "51e": "G51", "38a": "G38", "38b": "G38", "38c": "G38",
        "40": "G40", "44": "G44"}
COUNTED = ("51b", "51c", "51d")
VARIANTS = ("bge_small_white32_none", "gte_modernbert_white32_none", "bge_small_styp_none", "gte_modernbert_styp_none",
            "bge_small_white32_restatements")


def load(p):
    return json.loads(p.read_text()) if p.exists() else None


def g(r, *ks):
    for k in ks:
        if not isinstance(r, dict):
            return None
        r = r.get(k)
    return r


def unit_digest(r):
    if r is None:
        return None
    m = g(r, "content", "moments") or {}
    t = g(r, "content", "treatment", "family_adjusted") or {}
    tt = g(r, "talk", "moments") or {}
    return {"N": r.get("N_eligible"), "rho": m.get("rho_split"), "p_rho": m.get("p_rho"), "kappa": m.get("kappa"),
            "tau3": m.get("tau3"), "tau3_dc": m.get("tau3_dc"), "tau3_dc_ci90": m.get("tau3_dc_ci90"), "rho_se": m.get("rho_split_se"),
            "T_SR": g(t, "SR", "T"), "SR_n": g(t, "SR", "n"), "SR_p_less": g(t, "SR", "p_less"), "SR_p_greater": g(t, "SR", "p_greater"),
            "SR_null_sd": g(t, "SR", "null_sd"),
            "T_OP": g(t, "OP", "T"), "OP_n": g(t, "OP", "n"), "OP_p_less": g(t, "OP", "p_less"), "OP_null_sd": g(t, "OP", "null_sd"),
            "T_SY": g(t, "SY", "T"), "SY_p_greater": g(t, "SY", "p_greater"), "SY_null_sd": g(t, "SY", "null_sd"),
            "W": g(r, "overlap", "W"), "p_W": g(r, "overlap", "p_W"), "M": g(r, "overlap", "M"),
            "talk_rho": tt.get("rho_split"), "talk_p_rho": tt.get("p_rho"),
            "talk_T_SR": g(r, "talk", "treatment", "family_adjusted", "SR", "T"),
            "static_SR": g(r, "static_role_alignment", "SR", "T"), "static_SR_p": g(r, "static_role_alignment", "SR", "p_greater")}


def re_sr(units):
    e = [u["T_SR"] for u in units if u and u["T_SR"] is not None and u["SR_null_sd"]]
    s = [u["SR_null_sd"] for u in units if u and u["T_SR"] is not None and u["SR_null_sd"]]
    return L.dl_meta(e, s)


def main():
    out = {"round1": {}, "r1b": {}}
    for u, p in H22U.items():
        out["round1"][u] = unit_digest(load(DATA / p / u / "results.json"))
    for v in VARIANTS:
        out["r1b"][v] = {}
        base = R1B / v
        for gdir in sorted(base.glob("G*")):
            for ud in sorted(gdir.iterdir()):
                if (ud / "results.json").exists():
                    out["r1b"][v][ud.name] = unit_digest(load(ud / "results.json"))
    out["RE_T_SR_counted"] = {"round1": re_sr([out["round1"][u] for u in COUNTED])}
    for v in VARIANTS:
        out["RE_T_SR_counted"][v] = re_sr([out["r1b"][v].get(u) for u in COUNTED])
        sh = [u for u in out["r1b"][v] if u.startswith("pu51")]
        out["RE_T_SR_counted"][v + "_shared_units"] = re_sr([out["r1b"][v][u] for u in sh])
    sn = load(R1B / "stance_native.json")
    if sn:
        out["stance"] = {}
        for u, r in sn["stance"].items():
            t = g(r, "treatment", "family_adjusted") or {}
            out["stance"][u] = {"n_replies": r.get("n_replies"), "n_pairs": r.get("n_pairs"), "mean_s": r.get("mean_s"),
                                "opposes_share": r.get("opposes_share"),
                                "T_SR": g(t, "SR", "T"), "SR_n": g(t, "SR", "n"), "SR_p_less": g(t, "SR", "p_less"),
                                "SR_p_greater": g(t, "SR", "p_greater"), "SR_null_sd": g(t, "SR", "null_sd"),
                                "T_OP": g(t, "OP", "T"), "OP_n": g(t, "OP", "n"), "OP_p_less": g(t, "OP", "p_less"),
                                "T_SY": g(t, "SY", "T"), "SY_p_greater": g(t, "SY", "p_greater"),
                                "tau3": g(r, "balance", "tau3"), "tau3_dc": g(r, "balance", "tau3_dc"),
                                "tau3_dc_ci90": g(r, "balance", "tau3_dc_ci90"),
                                "camp_p": g(r, "agent_field_null", "p_camp"), "neg_pairs": g(r, "agent_field_null", "neg_pairs"),
                                "neg_null": g(r, "agent_field_null", "neg_null_mean"), "neg_p": g(r, "agent_field_null", "p_neg"),
                                "rho_dc": g(r, "agent_field_null", "rho_split_dc"), "rho_dc_p": g(r, "agent_field_null", "p_rho")}
        out["stance_RE_T_SR_counted"] = re_sr([out["stance"].get(u) for u in COUNTED])
        out["native_NE38"] = sn.get("native_NE38")
        out["native_NE38_min2"] = sn.get("native_NE38_min2")
        out["native_G23"] = {k: v for k, v in (sn.get("native_G23") or {}).items() if k != "pairs"}
    (R1B / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    f = lambda x, d=3: "—" if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))
    for u in list(H22U) + sorted({k for v in out["r1b"].values() for k in v if k.startswith("pu")}):
        line = [u]
        for tag, d in [("r1", out["round1"].get(u))] + [(v.split("_")[0][:3] + v.split("_")[2][:3] + v.split("_")[3][:3], out["r1b"][v].get(u)) for v in VARIANTS]:
            if d:
                line.append(f"{tag}: rho {f(d['rho'],2)} (p {f(d['p_rho'],3)}) k {f(d['kappa'],1)} t3dc {f(d['tau3_dc'],2)} SR {f(d['T_SR'])}/{d['SR_n']} "
                            f"(p> {f(d['SR_p_greater'],3)}) OP {f(d['T_OP'])} W {f(d['W'],2)} (p {f(d['p_W'],2)}) M {f(d['M'],2)}")
        print(" | ".join(line))
    print("RE T_SR counted:", json.dumps(out["RE_T_SR_counted"], default=float)[:1500])
    if "--no-estimates" not in sys.argv:
        write_est(out)


def write_est(out):
    import estimates as E
    import polars as pl
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet")
    pud = {r["unit_id"]: (r["first_day"], r["last_day"]) for r in pu.iter_rows(named=True)}
    days = {"51a": ("2026-07-06", "2026-07-08"), "51b": ("2026-07-09", "2026-08-04"), "51c": ("2026-08-05", "2026-08-24"),
            "51d": ("2026-08-25", "2026-09-02"), "51e": ("2026-09-03", "2026-09-04"), "38a": ("2026-04-02", "2026-04-13"),
            "38b": ("2026-04-14", "2026-04-17"), "38c": ("2026-04-20", "2026-04-24"), "40": ("2026-05-04", "2026-05-08"),
            "44": ("2026-05-26", "2026-05-29")}
    rows = []
    src = "data/processed/H22-private-goals-spin-glass/r1b/summary.json"

    def unit_meta(u):
        if u.startswith("pu"):
            uid = u[2:]
            a, b = pud[uid]
            return {"period_unit": uid, "goal_no": 51, "unit_local": u, "first_day": a, "last_day": b}
        a, b = days[u]
        goal = int(u[:2])
        return {"period_unit": E.map_unit(goal, a, b) or f"local:{u}", "goal_no": goal, "unit_local": u, "first_day": a, "last_day": b}
    for v, model in (("bge_small_white32_none", "bge_small"), ("gte_modernbert_white32_none", "gte_modernbert"),
                     ("bge_small_styp_none", "bge_small:style_resid_period")):
        for u, d in out["r1b"].get(v, {}).items():
            if d is None or u == "23":
                continue
            base = {**unit_meta(u), "role": "replication", "source": src, "status": "round 1b", "n": d["N"], "n_kind": "agents"}
            if d["rho"] is not None:
                ci = None
                rows.append({**base, "statistic": "coupling_heterogeneity_rho_split", "channel": f"content:{model}", "estimate": d["rho"],
                             "se": d["rho_se"], "ci_kind": "none", "method": "cross-fitted split-half correlation of within-day content couplings",
                             "null": "per-agent day-permutation pseudo-null", "notes": f"p={d['p_rho']}"})
            if d["T_SR"] is not None:
                rows.append({**base, "statistic": "rival_coupling_T_SR", "channel": f"content:{model}", "estimate": d["T_SR"], "se": d["SR_null_sd"],
                             "ci_kind": "none", "method": "mean J(same-role rivals) - mean J(unrelated), same-lab adjusted (DQ6 roles)",
                             "null": "role-label permutation", "notes": f"n_pairs={d['SR_n']}; p_greater={d['SR_p_greater']}; p_less={d['SR_p_less']}"})
            if d["tau3_dc"] is not None:
                rows.append({**base, "statistic": "balance_tau3_dc", "channel": f"content:{model}", "estimate": d["tau3_dc"],
                             "ci_lo": (d["tau3_dc_ci90"] or [None, None])[0], "ci_hi": (d["tau3_dc_ci90"] or [None, None])[1],
                             "ci_level": 0.9, "ci_kind": "percentile", "method": "double-centred balance index tau3 on three day folds",
                             "null": "SK ~ 0, factions ~ 0.45 (synthetic)"})
    for u, d in (out.get("stance") or {}).items():
        if u in ("51all",) or d is None or d.get("T_SR") is None and d.get("tau3_dc") is None:
            continue
        base = {**unit_meta(u), "role": "replication", "source": src, "status": "round 1b (stance channel)", "n": d["n_pairs"], "n_kind": "pairs"}
        if d.get("T_SR") is not None:
            rows.append({**base, "statistic": "rival_coupling_T_SR", "channel": "stance:dq2", "estimate": d["T_SR"], "se": d["SR_null_sd"],
                         "ci_kind": "none", "method": "mean stance J(same-role rivals) - mean J(unrelated), same-lab adjusted",
                         "null": "role-label permutation", "notes": f"p_greater={d['SR_p_greater']}; p_less={d['SR_p_less']}"})
        if d.get("neg_pairs") is not None:
            rows.append({**base, "statistic": "negative_pairs_count", "channel": "stance:dq2", "estimate": float(d["neg_pairs"]),
                         "ci_kind": "none", "method": "pairs with two-way-FE residual stance z < -2",
                         "null": "calibrated agent-field ordered logit", "notes": f"null mean={d['neg_null']}; p={d['neg_p']}"})
    ne = out.get("native_NE38_min2") or out.get("native_NE38") or {}
    for model in ("bge_small", "gte_modernbert"):
        if model in ne and ne[model].get("DiD") is not None:
            rows.append({"period_unit": "51f", "goal_no": 51, "unit_local": "NE38", "first_day": "2026-07-24", "last_day": "2026-08-04",
                         "role": "native", "statistic": "rival_coupling_DiD_NE38", "channel": f"content:{model}", "estimate": ne[model]["DiD"],
                         "ci_kind": "none", "n": ne[model]["n_others_both"], "n_kind": "agents",
                         "method": "Opus 5 coupling change with game-dev rivals minus with others across its 07-29 role change",
                         "null": "exact placebo rivals", "source": src, "post_hoc": True,
                         "notes": f"variant >= 2 shared windows (pre-registered >= 5 untestable); placebo pct={ne[model]['placebo_pct']}"})
    g23 = out.get("native_G23") or {}
    if g23.get("stance"):
        rows.append({"period_unit": "23", "goal_no": 23, "unit_local": "23", "role": "native", "statistic": "opponent_stance_contrast",
                     "channel": "stance:dq2", "estimate": g23["stance"]["T_opp"], "ci_kind": "none", "n": g23["stance"]["n_opp_pairs"],
                     "n_kind": "pairs", "method": "residual stance of chess opponents minus other pairs", "null": "node-label permutation",
                     "source": src, "notes": f"p_less={g23['stance']['p_less']}; p_greater={g23['stance']['p_greater']}"})
    for model in ("bge_small", "gte_modernbert"):
        c = g23.get(f"content_{model}")
        if c:
            rows.append({"period_unit": "23", "goal_no": 23, "unit_local": "23", "role": "native", "statistic": "opponent_coupling_contrast",
                         "channel": f"content:{model}", "estimate": c["T_opp"], "ci_kind": "none", "n": c["n_opp_pairs"], "n_kind": "pairs",
                         "method": "within-day content co-movement of chess opponents minus other pairs (pseudo-days)",
                         "null": "node-label permutation", "source": src, "notes": f"p_less={c['p_less']}; p_greater={c['p_greater']}"})
    w = E.write_estimates(rows, hypothesis="H22")
    print("estimates written:", w.height)


if __name__ == "__main__":
    main()
