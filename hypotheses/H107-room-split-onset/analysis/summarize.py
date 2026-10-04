"""H107: verdicts by the card's pre-registered rules, period README results, estimates rows, results.json.
Usage: uv run python hypotheses/H107-room-split-onset/analysis/summarize.py"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h107lib as L  # noqa: E402

ROOT = L.R.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

CARD = HERE.parent
RES = L.DATA / "results"
IDENT = ["G37", "G39", "G41", "G42"]
PRIM, SEC = "bge_small/style_resid", "gte_modernbert/style_resid"


def fmt(x, d=2):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def ident_verdict(r):
    if r["p_F"] is None or r["p_F"] >= 0.05:
        return "descriptive"
    rep = r.get("repo", {})
    repo_hit = bool(rep.get("rule_period") or rep.get("rule_day1"))
    if r["kill_onset"] or repo_hit:
        return "failed"
    if r["r1"] is not None and r["r1"] <= 0.3:
        return "supported"
    return "mixed"


def combine(vb, vg):
    if {vb, vg} == {"supported", "failed"}:
        return "mixed"
    return vb


def main():
    raw = json.loads((RES / "raw_all.json").read_text())
    pb, pg = raw[PRIM]["periods"], raw[SEC]["periods"]
    out = {"periods": {}, "card": {}}
    # replication verdicts
    for P in IDENT:
        vb, vg = ident_verdict(pb[P]), ident_verdict(pg[P])
        out["periods"][P] = {"replication": combine(vb, vg), "bge": vb, "gte": vg}
    # natives
    for P in ("G38", "G44", "G35"):
        nb_, ng_ = pb[P]["pi1"], pg[P]["pi1"]
        v = "supported" if nb_ >= 0.6 else ("failed" if nb_ < 0.3 else "mixed")
        out["periods"][P] = {"native": v, "pi1_bge": nb_, "pi1_gte": ng_}
    def p6(r):
        a = r.get("repo", {}).get("rule_day1", False); b = r.get("prev", {}).get("rule_day1", False)
        return "failed" if (a or b) else "supported"
    out["periods"]["G39"]["native"] = combine(p6(pb["G39"]), p6(pg["G39"]))
    out["periods"]["G39"]["native_by_model"] = [p6(pb["G39"]), p6(pg["G39"])]
    mb, mg = raw[PRIM]["resplit_G41"], raw[SEC]["resplit_G41"]
    p7a = abs(mb["z"]) < 2
    p7b = not (pb["G41"].get("repo", {}).get("rule_period") or pb["G41"].get("repo", {}).get("rule_day1"))
    out["periods"]["G41"]["native"] = "supported" if (p7a and p7b) else "mixed"
    out["periods"]["G41"]["P7"] = {"z_bge": mb["z"], "z_gte": mg["z"], "cos_bge": mb["cos_dis"], "repo40_ns": p7b}
    out["periods"]["G36"] = {"replication": "descriptive"}
    # overall period verdicts (one line per README)
    final = {}
    for P, v in out["periods"].items():
        vals = [x for k, x in v.items() if k in ("replication", "native")]
        if len(vals) == 1:
            final[P] = vals[0]
        else:
            final[P] = vals[0] if len(set(vals)) == 1 else "mixed"
    out["final"] = final
    # card-level
    n_sup = sum(out["periods"][P]["replication"] == "supported" for P in IDENT)
    n_fail = sum(out["periods"][P]["replication"] == "failed" for P in IDENT)
    p4 = pb["G38"]["pi1"] >= 0.6 and pb["G44"]["pi1"] >= 0.6
    hyp = "supported" if (n_sup >= 3 and p4) else ("failed" if n_fail >= 2 else "mixed")
    out["card"] = {"n_supported": n_sup, "n_failed": n_fail, "P4": p4, "verdict": hyp,
                   "pi1_median_identical_bge": float(np.median([pb[P]["pi1"] for P in IDENT])),
                   "pi1_median_identical_gte": float(np.median([pg[P]["pi1"] for P in IDENT]))}
    (RES / "results.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["final"]), json.dumps(out["card"]))

    # ---- estimates rows
    rows = []
    for key, ch in ((PRIM, "content_bge_style_resid"), (SEC, "content_gte_style_resid")):
        for P, r in raw[key]["periods"].items():
            g = int(P[1:])
            role = "native" if P in ("G35", "G38", "G44") else "replication"
            ci = r.get("ci") or {}
            n = r["n_best"] + r["n_rest"]
            for stat, est, cik, null in (("onset_ratio_r1", r["r1"], "r1", "joint relabel (excess over random partitions)"),
                                         ("onset_projection_pi1", r["pi1"], "pi1", "joint relabel"),
                                         ("onset_cosine_c1", r["c1_raw"], "c1_raw", "joint relabel"),
                                         ("first_halfday_ratio", r.get("r_h0"), "r_h0", "joint relabel"),
                                         ("final_excess_separation_E_F", r["E_F"], "E_F", "joint relabel (2000)")):
                if est is None:
                    continue
                c = ci.get(cik)
                rows.append({"period_unit": P, "goal_no": g, "statistic": stat, "channel": ch, "estimate": est,
                             "ci_lo": c[0] if c else None, "ci_hi": c[1] if c else None, "n": n, "n_kind": "agents",
                             "method": "day-1 vs final-block excess cross-products of the #best-#rest difference (bin-centred, a_i removed)",
                             "null": null, "role": role, "ci_level": 0.95 if c else None,
                             "ci_kind": "percentile" if c else "none", "confirmatory": False, "post_hoc": False,
                             "source": f"data/processed/H107-room-split-onset/results/raw_all.json[{key}]",
                             "notes": "G36 descriptive (day 1 regime II)" if P == "G36" else None})
            rep = r.get("repo")
            if rep and rep.get("f_day1") is not None:
                rows.append({"period_unit": P, "goal_no": g, "statistic": "repo_field_share_day1", "channel": ch,
                             "estimate": rep["f_day1"], "ci_lo": None, "ci_hi": None, "n": n, "n_kind": "agents",
                             "method": "inherited pre-period repo field u_repo; split-half share (D1.u)(D2.u)/S on day 1",
                             "null": f"direction null p={rep.get('p_day1')}", "role": role, "ci_kind": "none",
                             "confirmatory": False, "post_hoc": False,
                             "source": f"data/processed/H107-room-split-onset/results/raw_all.json[{key}]"})
    E.write_estimates(rows, hypothesis="H107")
    print("estimates rows", len(rows))

    # ---- period READMEs
    for P, v in final.items():
        f = CARD / "goalperiod-subhypotheses" / P / "README.md"
        txt = f.read_text()
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {v}", txt, count=1)
        b, gte = pb[P], pg[P]
        lines = ["*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*", "",
                 "| Statistic | bge | gte |", "| --- | --- | --- |",
                 f"| agents #best / #rest | {b['n_best']} / {b['n_rest']} | |",
                 f"| final split E_F (relabel p) | {fmt(b['E_F'], 3)} ({fmt(b['p_F'], 3)}) | {fmt(gte['E_F'], 3)} ({fmt(gte['p_F'], 3)}) |",
                 f"| onset ratio r₁ = E(1)/E_F [95% CI] | {fmt(b['r1'])} {('[' + fmt((b.get('ci') or {}).get('r1', [None, None])[0]) + ', ' + fmt((b.get('ci') or {}).get('r1', [None, None])[1]) + ']') if (b.get('ci') or {}).get('r1') else ''} | {fmt(gte['r1'])} |",
                 f"| onset projection π₁ [95% CI] | {fmt(b['pi1'])} {('[' + fmt(b['ci']['pi1'][0]) + ', ' + fmt(b['ci']['pi1'][1]) + ']') if (b.get('ci') or {}).get('pi1') else ''} | {fmt(gte['pi1'])} |",
                 f"| onset cosine c₁ (E(1) p) | {fmt(b['c1_raw'])} ({fmt(b['p1'], 3)}) | {fmt(gte['c1_raw'])} ({fmt(gte['p1'], 3)}) |",
                 f"| growth: E(d)/E_F by day | {', '.join(fmt(x) for x in b['profile'])} | {', '.join(fmt(x) for x in gte['profile'])} |",
                 f"| first half-day E/E_F | {fmt(b.get('r_h0'))} | {fmt(gte.get('r_h0'))} |"]
        for nm, k in (("inherited repo field f_repo period / day 1 (p)", "repo"), ("carried content field f_prev period / day 1 (p)", "prev")):
            rb, rg = b.get(k), gte.get(k)
            if rb:
                lines.append(f"| {nm} | {fmt(rb.get('f_period'))} ({fmt(rb.get('p_period'), 3)}) / {fmt(rb.get('f_day1'))} ({fmt(rb.get('p_day1'), 3)}) | "
                             f"{fmt(rg.get('f_period'))} ({fmt(rg.get('p_period'), 3)}) / {fmt(rg.get('f_day1'))} ({fmt(rg.get('p_day1'), 3)}) |")
        lines.append(f"| work persistence κ_w | {fmt(b['kappa_w']['kappa_w'])} | |")
        if P == "G41":
            lines.append(f"| P7: #41 day 1 × #39 difference, excess z (cos) | {fmt(mb['z'])} ({fmt(mb['cos_dis'])}) | {fmt(mg['z'])} (E_39 ≈ 0) |")
        lines += ["", f"Verdict components: {json.dumps(out['periods'][P])}.", "",
                  "Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `" + P + "`), `results.json`."]
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + "\n".join(lines) + "\n\n## Scorecard", txt, flags=re.S)
        sc = {"G38": "- **G:** a known field (room kickoffs) must show a step; **E:** kickoff contrast.",
              "G44": "- **G:** a known field must show a step; **E:** kickoff contrast.",
              "G35": "- **G, E:** a known work field (forks, NE15).",
              "G39": "- **C, D:** onset shape; **E:** the 04-27 reshuffle (inherited #38 work).",
              "G41": "- **C, D:** onset shape; **E:** the NE42 re-split (room memory)."}.get(P, "- **C, D:** relabel null for E and π₁; onset shape is unfitted.")
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + sc + "\n\n## Notes", txt, flags=re.S)
        f.write_text(txt)


if __name__ == "__main__":
    main()
