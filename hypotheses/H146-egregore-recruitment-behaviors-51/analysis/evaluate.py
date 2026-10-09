"""H146 round 1: apply the pre-registered rules (card §Prediction, Amendment A1) to results/real_<set>.json and
results/power_<set>.json. Writes results/verdicts_<set>.json and prints a markdown table."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
D = HERE.parents[2] / "data" / "processed" / "H146-egregore-recruitment-behaviors-51" / "results"


def p_pseudo(val, pseudo, lower=False):
    v = np.array([x for x in pseudo if x is not None], float)
    if val is None or len(v) == 0:
        return None
    k = (v <= val).sum() if lower else (v >= val).sum()
    return float((1 + k) / (len(v) + 1))


def ci(o, key="delta"):
    if not o or o.get(key) is None:
        return None
    e, se = o[key]
    return e, e - 1.96 * se, e + 1.96 * se, (e / se if se > 0 else 0.0)


def fmt(x, d=2):
    return "–" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:.{d}f}"


def evaluate(set_):
    R = json.loads((D / f"real_{set_}.json").read_text())
    Pw = json.loads((D / f"power_{set_}.json").read_text())["patterns"]
    out = {}
    for k, r in R["patterns"].items():
        s, ps, pw = r["stats"], r["pseudo"]["values"], Pw.get(k, {})
        v = {"label": r["meta"].get("candidate") or r["meta"].get("label")}
        # P1 adoption and P1b
        for key, pk, pwk in (("P1_adopt", "P1_adopt", "P1_adopt"), ("P1b", "P1b", "P1b_expr")):
            c = ci(s.get(key))
            est_ok = bool(s.get(key, {}) and s[key].get("estimable"))
            power = (pw.get(pwk) or {}).get("power")
            size = (pw.get(pwk) or {}).get("size")
            pp = p_pseudo(c[0], ps.get(pk, [])) if c else None
            pos = bool(c and est_ok and c[1] > 0 and (size is None or size <= 0.10))
            v[key] = {"est": c and c[0], "lo": c and c[1], "hi": c and c[2], "estimable": est_ok, "power": power,
                      "size": size, "p_pseudo": pp, "ci_above0": pos, "beats_pseudo": bool(pp is not None and pp <= 0.05),
                      "pass": bool(pos and pp is not None and pp <= 0.05),
                      "verdict": ("pass" if pos and pp is not None and pp <= 0.05 else
                                  "CI>0, not beyond pseudo" if pos else
                                  ("fail" if power is not None and power >= 0.8 else "inconclusive"))}
        for key in ("P1b_nohub", "P1b_nofable", "P1b_anysender"):
            c = ci(s.get(key))
            v[key] = c and {"est": c[0], "lo": c[1], "hi": c[2]}
        # P2 (only where P1 or P1b passes; also reported descriptively)
        p2 = s.get("P2b") or {}
        cn, cu, cd = ci(p2, "delta_Rm_named"), ci(p2, "delta_Rm_unnamed"), ci(p2, "delta_named_minus_unnamed")
        ratio = None
        if cn and cu:
            ratio = (math.expm1(cn[0]) / math.expm1(cu[0])) if cu[0] > 0 else (math.inf if cn[0] > 0 else None)
        p2_pass = bool(cn and cu and cd and ((ratio is not None and ratio >= 3 and cd[3] >= 1.96) or
                                            (cu[0] <= 0 < cn[0] and cn[1] > 0)))
        v["P2"] = {"named": cn and cn[0], "unnamed": cu and cu[0], "diff": cd and cd[0], "diff_lo": cd and cd[1],
                   "ratio": ratio, "p_pseudo_diff": p_pseudo(cd and cd[0], ps.get("P2b_named_minus_unnamed", [])),
                   "rule_met": p2_pass, "applies": v["P1b"]["pass"] or v["P1_adopt"]["pass"],
                   "falsified": bool(cn and cu and cn[0] <= cu[0])}
        # P3 descriptive
        p3 = (s.get("P3") or {}).get("fit")
        c = ci(p3)
        v["P3"] = {"est": c and c[0], "lo": c and c[1], "hi": c and c[2], "events": (s.get("P3") or {}).get("events"),
                   "verdict": "untestable (descriptive)"}
        # P4
        p4 = s.get("P4") or {}
        hr = p4.get("HR_F_vs_P")
        rg = p4.get("HR_read_F") or {}
        rgp = ((pw.get("P4") or {}).get("readgate_g2") or {}).get("share_readgate_ci_above1")
        v["P4"] = {"HR": hr, "ci": p4.get("ci"), "p_pseudo_low": p_pseudo(hr, ps.get("P4_HR", []), lower=True),
                   "K2_fires": bool(hr is not None and hr < 0.5), "survives": bool(hr is not None and hr >= 0.8),
                   "readgate": rg.get("est"), "readgate_ci": rg.get("ci"), "readgate_power": rgp,
                   "readgate_faster": bool(rg.get("ci") and rg["ci"][0] is not None and rg["ci"][0] > 1),
                   "events_F": p4.get("events_F"), "events_P": p4.get("events_P"), "n_F": p4.get("n_F"),
                   "n_P": p4.get("n_P")}
        # P5
        v["P5"] = {}
        for sub, o in (s.get("P5") or {}).items():
            pwr = ((pw.get("P5") or {}).get(sub) or {}).get("power")
            rr, cc = o.get("rr"), o.get("ci") or [None, None]
            ok = bool(rr is not None and rr > 1.2 and cc[0] is not None and cc[0] > 1)
            pp = p_pseudo(rr, ps.get(f"P5_{sub}", [])) if f"P5_{sub}" in ps else None
            v["P5"][sub] = {"rr": rr, "ci": cc, "power": pwr, "rule_met": ok, "p_pseudo": pp,
                            "verdict": ("pass" if ok and (pp is None or pp <= 0.05) else
                                        "rule met, not beyond pseudo" if ok else
                                        "fail" if (pwr or 0) >= 0.8 else "inconclusive")}
        # P6
        sp, om = s.get("P6_spec") or {}, s.get("P6_omega") or {}
        z = sp.get("z")
        v["P6_spec"] = {"z": z, "p_perm": sp.get("p"), "p_pseudo": p_pseudo(z, ps.get("P6_spec_z", [])),
                        "z_ge2": bool(z is not None and z >= 2)}
        v["P6_spec"]["beats_pseudo"] = bool(v["P6_spec"]["p_pseudo"] is not None and v["P6_spec"]["p_pseudo"] <= 0.05)
        o = om.get("omega_per")
        v["P6_omega"] = {"omega_per": o, "sur_p05": om.get("sur_p05"), "gauss_fr": om.get("omega_gauss_fieldremoved_per"),
                         "n_hosts": om.get("n_hosts"), "n_bins": om.get("n_bins"),
                         "rule_met": bool(o is not None and om.get("sur_p05") is not None and o < 0 and o < om["sur_p05"]),
                         "p_pseudo_low": p_pseudo(o, ps.get("P6_omega", []), lower=True)}
        out[k] = v
    (D / f"verdicts_{set_}.json").write_text(json.dumps(out, indent=1, default=lambda x: None))
    return out


def table(out):
    print("| K | label | P1b δ [CI] | p_pseudo | power | P2 ratio | P4 HR [CI] | read-gate HR [CI] | P5 wipe RR [CI] | "
          "spec z (p_pseudo) | Ω/(n−2) vs sur p05 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for k, v in out.items():
        a = v["P1b"]
        p4 = v["P4"]
        w = v["P5"].get("wipe", {})
        rgc = p4["readgate_ci"] or [None, None]
        print(f"| {k} | {v['label']} | {fmt(a['est'])} [{fmt(a['lo'])}, {fmt(a['hi'])}] | {fmt(a['p_pseudo'])} | "
              f"{fmt(a['power'])} | {fmt(v['P2']['ratio'], 1)} | {fmt(p4['HR'])} [{fmt((p4['ci'] or [None])[0])}, "
              f"{fmt((p4['ci'] or [None, None])[1])}] | {fmt(p4['readgate'])} [{fmt(rgc[0])}, {fmt(rgc[1])}] | "
              f"{fmt(w.get('rr'))} [{fmt((w.get('ci') or [None])[0])}, {fmt((w.get('ci') or [None, None])[1])}] | "
              f"{fmt(v['P6_spec']['z'], 1)} ({fmt(v['P6_spec']['p_pseudo'])}) | {fmt(v['P6_omega']['omega_per'], 3)} vs "
              f"{fmt(v['P6_omega']['sur_p05'], 3)} |")


if __name__ == "__main__":
    for s_ in sys.argv[1:] or ["h145", "candidates"]:
        if (D / f"real_{s_}.json").exists():
            print(f"\n## {s_}")
            o = evaluate(s_)
            table(o)
            for k, v in o.items():
                p5 = {a: b["verdict"] for a, b in v["P5"].items()}
                print(k, "P1a:", v["P1_adopt"]["verdict"], "| P1b:", v["P1b"]["verdict"], "| P2 met", v["P2"]["rule_met"],
                      "| P5:", p5, "| spec beats pseudo", v["P6_spec"]["beats_pseudo"], "| omega rule", v["P6_omega"]["rule_met"],
                      "| omega p_pseudo_low", fmt(v["P6_omega"]["p_pseudo_low"]))
