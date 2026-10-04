"""H100: verdicts by the card's rules, per-period result tables (results/results.json), estimates rows and figures.

Usage: uv run python hypotheses/H100-room-symmetry-breaking/analysis/summarize.py [--estimates] [--figures]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
H = HERE.parent
ROOT = H.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h100lib as L  # noqa: E402

RES = L.DATA / "results"
NAMES = {20: "Opus 4.6", 21: "Sonnet 4.6", 22: "Gemini 3.1 Pro", 23: "GPT-5.4"}
BND_OF = {38: "04-02", 39: "04-27", 44: "05-25"}


def f2(x, n=2):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{n}f}"


def pfmt(p):
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def verdict_period(P, r, g, mv, rem):
    """r: primary (bge style_resid) decomposition; g: gte style_resid."""
    if ROLE(P) == "replication":
        if r["p"] > 0.2 and r["Q"] <= 1:
            return "failed"
        if P == 35:
            return "supported" if r["p"] < 0.05 else "mixed"
        if r.get("f_comp", 1) >= 0.7:
            return "failed"
        if r["p_res"] < 0.05 and r.get("f_comp", 1) < 0.5:
            return "supported"
        return "mixed"
    if P in (38, 44):
        field_ok = r["f_field"] >= 0.15 and r.get("f_field_p", 1) < 0.05
        spont_ok = r["p_spont"] < 0.05
        if field_ok and spont_ok:
            return "supported"
        if r["f_field"] < 0.05 and r["p_spont"] > 0.2:
            return "failed"
        return "mixed"
    if P == 39:
        ok = [m for m in mv.values() if not m.get("skip") and m["C_post_p"] < 0.05 and m["phi_post"] >= 0.5
              and m["phi_post"] - m.get("phi_comp", np.nan) >= 0.5]
        bad = [m for m in mv.values() if not m.get("skip") and m["phi_post"] < 0]
        if len(ok) >= 2:
            return "supported"
        if len(bad) >= 2:
            return "failed"
        return "mixed"
    if P == 41:
        if r["p_spont"] < 0.01 and abs(rem["z"]) < 2:
            return "supported"
        if r["p_spont"] > 0.2:
            return "failed"
        return "mixed"


def ROLE(P):
    return "replication" if P in (35, 36, 37, 42) else "native"


def period_md(P, raw):
    r = raw["bge_small/style_resid"]["periods"][f"G{P}"]
    g = raw["gte_modernbert/style_resid"]["periods"][f"G{P}"]
    w = raw["bge_small/white32"]["periods"][f"G{P}"]
    rows = [("Q (relabel excess), p", f"{f2(r['Q'])}, p {pfmt(r['p'])}", f"{f2(g['Q'])}, p {pfmt(g['p'])}",
             f"{f2(w['Q'])}, p {pfmt(w['p'])}")]
    if P != 35:
        rows += [("f_comp [95% CI]", f"{f2(r['f_comp'])} [{f2(r['f_comp_ci'][0])}, {f2(r['f_comp_ci'][1])}]" if 'f_comp_ci' in r else f2(r.get('f_comp')),
                  f"{f2(g['f_comp'])}", f"{f2(w.get('f_comp'))}"),
                 ("Q_res (composition removed), p", f"{f2(r['Q_res'])}, p {pfmt(r['p_res'])}",
                  f"{f2(g['Q_res'])}, p {pfmt(g['p_res'])}", f"{f2(w.get('Q_res'))}, p {pfmt(w.get('p_res', 1))}"),
                 ("Q_spont (and field removed), p", f"{f2(r['Q_spont'])}, p {pfmt(r['p_spont'])}",
                  f"{f2(g['Q_spont'])}, p {pfmt(g['p_spont'])}", "–"),
                 ("f_spont [95% CI]", f"{f2(r['f_spont'])} [{f2(r['f_spont_ci'][0])}, {f2(r['f_spont_ci'][1])}]" if 'f_spont_ci' in r else f2(r.get('f_spont')),
                  f2(g["f_spont"]), "–")]
    if r["field_dim"]:
        rows.append(("f_field (dims: " + ", ".join(k[4:] for k in r if k.startswith("use_")) + "), null mean, p",
                     f"{f2(r['f_field'])}, {f2(r.get('f_field_null_mean'))}, p {pfmt(r.get('f_field_p', 1))}",
                     f"{f2(g['f_field'])}, p {pfmt(g.get('f_field_p', 1))}", "–"))
    else:
        rows.append(("f_field", "no distinct room field (kickoff cos ≥ 0.95, < 3 operator messages per room)", "", ""))
    t = ("| Statistic | bge style_resid (primary) | gte style_resid | bge white32 |\n| --- | --- | --- | --- |\n"
         + "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows))
    t += (f"\n\nAgents: #best {r['n_best']}, #rest {r['n_rest']} (≥ 2 days, one room); median {f2(r['n_days_med'], 1)} days "
          f"per agent. Relabel null: 2,000 partitions; f-share CIs: agent bootstrap within rooms (500).")
    if P in BND_OF:
        mv = raw["bge_small/style_resid"]["movers"][BND_OF[P]]["movers"]
        mg = raw["gte_modernbert/style_resid"]["movers"][BND_OF[P]]["movers"]
        t += ("\n\n**Movers at " + BND_OF[P] + "** (φ: +1 = like a native of the new room, −1 = like a native of the old room; "
              "C = native contrast of the stayers, with a stayer-relabel z and p; φ is read only where C has p < 0.05).\n\n| Mover | C_pre z (p) | φ_pre | C_post z (p) | φ_post [95% CI, day bootstrap] | φ_comp | day-1 φ | stayers' φ 5th pct | gte φ_post |\n"
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
        for k, m in mv.items():
            if m.get("skip"):
                t += f"| {NAMES.get(int(k), k)} | skipped (too few stayers) | | | | | | | |\n"
                continue
            ci = m.get("phi_post_ci", [np.nan, np.nan])
            t += (f"| {NAMES.get(int(k), k)} | {f2(m.get('C_pre_z'), 1)} ({pfmt(m.get('C_pre_p', 1))}) | {f2(m.get('phi_pre'))} | "
                  f"{f2(m['C_post_z'], 1)} ({pfmt(m['C_post_p'])}) | "
                  f"{f2(m['phi_post'])} [{f2(ci[0])}, {f2(ci[1])}] | {f2(m.get('phi_comp'))} | {f2(m['phi_day1'])} | "
                  f"{f2(m['stayers_phi_p05'])} | {f2(mg[k]['phi_post']) if not mg[k].get('skip') else '–'} |\n")
    if P == 39:
        sc = raw["bge_small/style_resid"]["swap_carry"]; sg = raw["gte_modernbert/style_resid"]["swap_carry"]
        t += (f"\n**Swap-carry (#38 → #39):** R_room {f2(sc['R_room'])} (z {f2(sc['R_room_z'], 1)}, p {pfmt(sc['p_room_two'])}); "
              f"R_agent {f2(sc['R_agent'])} (z {f2(sc['R_agent_z'], 1)}, p {pfmt(sc['p_agent_two'])}); {sc['n_both']} agents in "
              f"both periods. gte: R_room {f2(sg['R_room'])} (z {f2(sg['R_room_z'], 1)}), R_agent {f2(sg['R_agent'])} "
              f"(z {f2(sg['R_agent_z'], 1)}).\n")
    if P == 41:
        rm = raw["bge_small/style_resid"]["remanence"]["39-41"]; rg = raw["gte_modernbert/style_resid"]["remanence"]["39-41"]
        rr = raw["bge_small/style_resid"]["remanence_raw"]["39-41"]
        t += (f"\n**Remanence #39 → #41 (across the NE42 merge):** R_spont {f2(rm['R'])} (z {f2(rm['z'], 1)}, p {pfmt(rm['p_two'])}); "
              f"gte {f2(rg['R'])} (z {f2(rg['z'], 1)}); raw room difference (composition kept) {f2(rr['R'])} (z {f2(rr['z'], 1)}).\n")
    return t


def build():
    raw = json.loads((RES / "raw_all.json").read_text())
    p = raw["bge_small/style_resid"]
    out = {"periods": {}, "invariance": {k: raw[k]["invariance"] for k in raw}}
    for P in L.MULTI:
        r = p["periods"][f"G{P}"]
        mv = p["movers"][BND_OF[P]]["movers"] if P in BND_OF else {}
        rem = p["remanence"].get("39-41")
        v = verdict_period(P, r, raw["gte_modernbert/style_resid"]["periods"][f"G{P}"], mv, rem)
        if P == 38 or P == 44:
            v38 = v
            # mover clause is reported but the native verdict rule is the field + spontaneous clause (card)
        out["periods"][f"G{P}"] = {"verdict": v, "result_md": "*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; "
                                   "non-holdout).*\n\n" + period_md(P, raw),
                                   "scorecard_md": SC.get(P, "- **C:** relabel null; **D:** f-shares and Q_res are not fitted; "
                                                          "**F:** synthetic recovery on this skeleton (`synthetic/synthetic_summary.json`).")}
    (RES / "results.json").write_text(json.dumps(out, indent=1))
    return out


SC = {38: "- **C:** relabel and direction nulls; **D:** field share and mover φ are unfitted; **E:** the 04-02 move; "
          "**G:** room-specific kickoffs are known structure.",
      39: "- **C:** relabel null; **D:** mover φ vs φ_comp; **E:** the 04-27 reshuffle is the interventional design; "
          "**F:** synthetic mover worlds (`synthetic/synthetic_summary.json`).",
      41: "- **C:** relabel null after composition and field removal; **E:** NE42 (remanence across the merge).",
      44: "- **C:** relabel and direction nulls; **D:** field share and mover φ; **E:** the 05-25 move; **G:** room kickoffs."}


def estimates():
    import estimates as E
    raw = json.loads((RES / "raw_all.json").read_text())
    rows = []
    for key, tag in (("bge_small/style_resid", "bge"), ("gte_modernbert/style_resid", "gte")):
        for P in L.MULTI:
            r = raw[key]["periods"][f"G{P}"]
            unit = f"G{P}"
            role = ROLE(P)
            n = r["n_best"] + r["n_rest"]
            base = {"period_unit": unit, "goal_no": P, "n": n, "n_kind": "agents", "role": role,
                    "source": f"data/processed/H100-room-symmetry-breaking/results/raw_all.json[{key}]", "post_hoc": False}
            rows.append({**base, "statistic": "room_relabel_excess_Q", "channel": f"content_{tag}_style_resid",
                         "estimate": r["Q"], "ci_lo": None, "ci_hi": None, "ci_kind": "none", "method": "split-half S / relabel-null mean",
                         "null": f"room relabel (2000); p={r['p']:.4f}"})
            if "f_comp" in r:
                rows.append({**base, "statistic": "f_comp", "channel": f"content_{tag}_style_resid", "estimate": r["f_comp"],
                             "ci_lo": r.get("f_comp_ci", [None, None])[0], "ci_hi": r.get("f_comp_ci", [None, None])[1],
                             "ci_kind": "percentile" if "f_comp_ci" in r else "none",
                             "method": "leave-period-out agent constants . room difference / S", "null": "composition only (f=1)"})
                rows.append({**base, "statistic": "room_relabel_excess_Q_spont", "channel": f"content_{tag}_style_resid",
                             "estimate": r["Q_spont"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                             "method": "Q after removing agent constants and room-field directions",
                             "null": f"room relabel (2000); p={r['p_spont']:.4f}"})
            if r["field_dim"]:
                rows.append({**base, "statistic": "f_field", "channel": f"content_{tag}_style_resid", "estimate": r["f_field"],
                             "ci_lo": r.get("f_field_ci", [None, None])[0], "ci_hi": r.get("f_field_ci", [None, None])[1],
                             "ci_kind": "percentile" if "f_field_ci" in r else "none",
                             "method": "share of split-half S along room kickoff/operator directions",
                             "null": f"random directions, empirical within-room covariance; p={r.get('f_field_p', float('nan')):.4f}"})
        for bnd, mvr in raw[key]["movers"].items():
            post = mvr["post"]
            for k, m in mvr["movers"].items():
                if m.get("skip"):
                    continue
                ci = m.get("phi_post_ci", [None, None])
                rows.append({"period_unit": f"G{post}", "goal_no": post, "statistic": f"mover_phi_post_agent{k}",
                             "channel": f"content_{tag}_style_resid", "estimate": m["phi_post"], "ci_lo": ci[0], "ci_hi": ci[1],
                             "ci_kind": "percentile" if ci[0] is not None else "none", "n": m["n_new_stayers"] + m["n_old_stayers"],
                             "n_kind": "stayers", "role": "native", "method": "mover index phi (cross-agent similarity / native contrast)",
                             "null": f"phi_comp={m.get('phi_comp', float('nan')):.3f}; C_post p={m['C_post_p']:.3f}",
                             "source": f"data/processed/H100-room-symmetry-breaking/results/raw_all.json[{key}]", "post_hoc": False})
    E.write_estimates(rows, hypothesis="H100")
    print("estimates rows", len(rows))


if __name__ == "__main__":
    out = build()
    for k, v in out["periods"].items():
        print(k, v["verdict"])
    if "--estimates" in sys.argv:
        estimates()
