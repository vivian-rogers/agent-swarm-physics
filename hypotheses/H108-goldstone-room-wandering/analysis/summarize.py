"""H108: verdicts by the card's pre-registered rules, period README results, estimates rows, results.json.
Usage: uv run python hypotheses/H108-goldstone-room-wandering/analysis/summarize.py"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h108lib as L  # noqa: E402

ROOT = L.R.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

CARD = HERE.parent
RES = L.DATA / "results"
PRIM, SEC = "bge_small/style_resid", "gte_modernbert/style_resid"
IDENT = [f"G{p}" for p in L.R.IDENTICAL]
FIELD = [f"G{p}" for p in L.R.FIELDED]


def num(x):
    if x is None:
        return np.nan
    if x == "inf":
        return np.inf
    return float(x)


def fmt(x, d=2):
    x = num(x) if not isinstance(x, (int, float)) or x is None else x
    if x is None or not np.isfinite(x):
        return "∞" if x == np.inf else "–"
    return f"{x:.{d}f}"


def verdicts(raw_key):
    per = raw_key["periods"]; g = raw_key["groups"]
    Did, Df = num(g["identical"]["D"]), num(g["fielded"]["D"])
    v = {}
    for P in IDENT:
        D = num(per[P]["D"])
        if per[P]["P1"] is None:
            v[P] = "descriptive"
        elif D >= 2 * Df:
            v[P] = "supported"
        elif D <= Df:
            v[P] = "failed"
        else:
            v[P] = "mixed"
    for P in FIELD:
        D = num(per[P]["D"])
        v[P] = "supported" if D <= 0.5 * Did else ("failed" if D >= Did else "mixed")
    return v


def combine(a, b):
    return "mixed" if {a, b} == {"supported", "failed"} else a


def main():
    raw = json.loads((RES / "raw_all.json").read_text())
    rb, rg = raw[PRIM], raw[SEC]
    vb, vg = verdicts(rb), verdicts(rg)
    out = {"periods": {P: {"replication": combine(vb[P], vg[P]), "bge": vb[P], "gte": vg[P]} for P in vb}}
    # G38 native (P4): slope of ln P(l), l = 1..6, and P(6)
    lag = {int(k): num(x) for k, x in rb["periods"]["G38"]["P_lag"].items()}
    ls = sorted(lag)
    slope = float(np.polyfit(ls, np.log([lag[l] for l in ls]), 1)[0])
    lag_g = {int(k): num(x) for k, x in rg["periods"]["G38"]["P_lag"].items()}
    slope_g = float(np.polyfit(sorted(lag_g), np.log([lag_g[l] for l in sorted(lag_g)]), 1)[0])
    p4 = slope >= -0.05 and lag[6] >= 0.5
    out["periods"]["G38"]["native"] = "supported" if p4 else "failed"
    out["periods"]["G38"]["P4"] = {"slope_bge": slope, "P6_bge": lag[6], "slope_gte": slope_g, "P6_gte": lag_g[6]}
    # G35 native (P5): no-constants omega vs pooled identical no-constants omega
    p5 = {}
    for key in ("bge_small/style_resid/noconst", "gte_modernbert/style_resid/noconst"):
        r = raw[key]
        om35 = 1 - num(r["periods"]["G35"]["P1"]); omid = num(r["groups"]["identical"]["omega"])
        p5[key] = {"omega_G35": om35, "omega_identical": omid,
                   "verdict": "supported" if om35 <= omid else ("failed" if om35 >= 2 * omid else "mixed")}
    out["periods"]["G35"] = {"native": combine(*[x["verdict"] for x in p5.values()]), "P5": p5}
    final = {}
    for P, v in out["periods"].items():
        vals = [x for k, x in v.items() if k in ("replication", "native")]
        final[P] = vals[0] if len(set(vals)) == 1 else "mixed"
    out["final"] = final
    gb, gg = rb["groups"], rg["groups"]
    RD_b, lo_b = num(gb["R_D"]), gb["R_D_ci"][0]
    hyp = ("supported" if (RD_b >= 2 and lo_b > 1 and num(gg["R_D"]) > 1) else
           "failed" if (num(gb["identical"]["D"]) <= num(gb["fielded"]["D"]) and num(gg["identical"]["D"]) <= num(gg["fielded"]["D"]))
           else "mixed")
    pers = {k: sum(1 for P, s in raw[k]["periods"].items() if s.get("persist_p") is not None and s["persist_p"] < 0.05)
            for k in (PRIM, SEC)}
    out["card"] = {"verdict": hyp, "R_D_bge": RD_b, "R_D_ci_bge": gb["R_D_ci"], "R_D_gte": num(gg["R_D"]),
                   "R_D_ci_gte": gg["R_D_ci"], "persistence_periods": pers,
                   "scaling": {"bge": rb.get("scaling"), "gte": rg.get("scaling")}}
    (RES / "results.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(final), json.dumps({k: v for k, v in out["card"].items() if k != "scaling"}))

    rows = []
    for key, ch in ((PRIM, "content_bge_style_resid"), (SEC, "content_gte_style_resid")):
        for P, s in raw[key]["periods"].items():
            g = int(P[1:]); role = "native" if P in ("G35",) else "replication"
            ci = s.get("P1_ci")
            n = s["n_best"] + s["n_rest"]
            for stat, est, c in (("room_direction_persistence_P1", num(s["P1"]), ci),
                                 ("angular_decorrelation_rate_D", num(s["D"]), None),
                                 ("persistence_split_half_Psh1", num(s["P1_sh"]), None)):
                if not np.isfinite(est):
                    continue
                rows.append({"period_unit": P, "goal_no": g, "statistic": stat, "channel": ch, "estimate": est,
                             "ci_lo": c[0] if c else None, "ci_hi": c[1] if c else None, "n": n, "n_kind": "agents",
                             "method": "lag-1 ratio of sums of joint-relabel excess cross-products of daily #best-#rest differences (a_i removed)"
                             if stat != "persistence_split_half_Psh1" else "within-day statement split halves (HH338 literal; biased low under pinning)",
                             "null": f"joint relabel; persistence p={s.get('persist_p')}", "role": role,
                             "ci_level": 0.95 if c else None, "ci_kind": "percentile" if c else "none",
                             "confirmatory": False, "post_hoc": False,
                             "source": f"data/processed/H108-goldstone-room-wandering/results/raw_all.json[{key}]",
                             "notes": "per day; D = -ln P1" if stat == "angular_decorrelation_rate_D" else None})
    E.write_estimates(rows, hypothesis="H108")
    print("estimates rows", len(rows))

    for P, v in final.items():
        f = CARD / "goalperiod-subhypotheses" / P / "README.md"
        txt = f.read_text()
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {v}", txt, count=1)
        b, g_ = rb["periods"][P], rg["periods"][P]
        ci = b.get("P1_ci"); cig = g_.get("P1_ci")
        lines = ["*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*", "",
                 "| Statistic | bge | gte |", "| --- | --- | --- |",
                 f"| agents #best / #rest; days | {b['n_best']} / {b['n_rest']}; {b['n_days']} | |",
                 f"| persistence P(1) [95% CI] | {fmt(b['P1'])} [{fmt(ci[0]) if ci else '–'}, {fmt(ci[1]) if ci else '–'}] | {fmt(g_['P1'])} [{fmt(cig[0]) if cig else '–'}, {fmt(cig[1]) if cig else '–'}] |",
                 f"| decorrelation rate D_θ = −ln P(1) (per day) | {fmt(b['D'], 3)} | {fmt(g_['D'], 3)} |",
                 f"| split-half P_sh(1) (variant, biased low) | {fmt(b['P1_sh'])} | {fmt(g_['P1_sh'])} |",
                 f"| persistence relabel p (Σ D(d)·D(d+1)) | {fmt(b.get('persist_p'), 3)} | {fmt(g_.get('persist_p'), 3)} |",
                 f"| N_eff; mean daily E | {fmt(b['N_eff'])}; {fmt(b['E_mean'], 3)} | {fmt(g_['N_eff'])}; {fmt(g_['E_mean'], 3)} |",
                 f"| pooled reference (bge): D_id {fmt(gb['identical']['D'], 3)}, D_f {fmt(gb['fielded']['D'], 3)} | | |"]
        if P == "G38":
            lines.append(f"| lag profile P(ℓ), ℓ = 1…6 | {', '.join(fmt(num(b['P_lag'][k])) for k in sorted(b['P_lag'], key=int))} | {', '.join(fmt(num(g_['P_lag'][k])) for k in sorted(g_['P_lag'], key=int))} |")
            lines.append(f"| slope of ln P(ℓ) per day; P(6) | {fmt(slope, 3)}; {fmt(lag[6])} | {fmt(slope_g, 3)}; {fmt(lag_g[6])} |")
        if P == "G35":
            for k, x in p5.items():
                lines.append(f"| P5 ({k.split('/')[0]}, no constants): ω(G35) vs pooled identical ω | {fmt(x['omega_G35'])} vs {fmt(x['omega_identical'])} | |")
        lines += ["", f"Verdict components: {json.dumps(out['periods'][P])}.", "",
                  f"Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `{P}`), `results.json`."]
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + "\n".join(lines) + "\n\n## Scorecard", txt, flags=re.S)
        sc = {"G38": "- **D:** lag profile (pinned plateau vs decay); **G:** a known field should pin.",
              "G44": "- **G:** a known field should pin.", "G35": "- **E, G:** a known work field (forks) should pin."}.get(
            P, "- **C:** joint-relabel noise correction; **D:** rotation is unfitted.")
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + sc + "\n\n## Notes", txt, flags=re.S)
        f.write_text(txt)


if __name__ == "__main__":
    main()
