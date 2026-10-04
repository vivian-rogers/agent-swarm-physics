"""H32 round 1b assembly (2026-10-04): round 1 vs ledger exposure (bge) vs gte / style / dedupe, the H57 unread placebo,
per-period verdict lines and per_period_estimates rows.

  uv run python hypotheses/H32-information-current-leaders/analysis/r1b_assemble.py [table|estimates|readmes]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H32-information-current-leaders"
R1B = DATA / "r1b"
PD = HERE.parent / "goalperiod-subhypotheses"
VARS = ("bge", "gte", "style", "bge_unread", "bge_dedupe", "bge_unread_tau60")


def periods():
    return [p["goal_no"] for p in json.loads((DATA / "periods.json").read_text())]


def load(v, g):
    p = (DATA / f"G{g:02d}" / "result.json") if v == "r1" else (R1B / v / f"G{g:02d}" / "result.json")
    return json.loads(p.read_text()) if p.exists() else None


def _rho(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    return float(spearmanr(a[m], b[m]).statistic) if m.sum() >= 4 else None


def table():
    out = {"periods": {}}
    gs = periods()
    for g in gs:
        r1, b = load("r1", g), load("bge", g)
        e = {"r1": dict(T=r1["T"], p=r1["p_T"], top=r1["leader_call"]["top_out"], sh=(r1.get("split_half") or {}).get("rho_out"),
                        T_unseen=r1.get("T_unseen"), p_unseen=r1.get("p_T_unseen"))}
        if b:
            e["bge"] = dict(T=b["T"], p=b["p_T"], top=b["top"], sh=(b.get("split_half") or {}).get("rho_out"), v=b["verdict_general"],
                            wd_p=(b.get("withinday") or {}).get("p_T"), T_unseen=b.get("T_unseen"), p_unseen=b.get("p_T_unseen"),
                            human=b.get("human"), p_standout=b["p_standout"], p_max=b["p_max"])
            o1 = dict(zip(r1["nodes"], r1["out"])); ob = dict(zip(b["nodes"], b["out"]))
            com = [a for a in ob if a in o1]
            e["rho_out_r1_bge"] = _rho([o1[a] for a in com], [ob[a] for a in com])
        for v in VARS[1:]:
            x = load(v, g)
            if x:
                e[v] = dict(T=x["T"], p=x["p_T"], top=x["top"], T_unseen=x.get("T_unseen"), p_unseen=x.get("p_T_unseen"),
                            kept=x.get("targets_kept_frac"))
                if b:
                    ob = dict(zip(b["nodes"], b["out"])); ox = dict(zip(x["nodes"], x["out"]))
                    com = [a for a in ob if a in ox]
                    e[v]["rho_out_vs_bge"] = _rho([ob[a] for a in com], [ox[a] for a in com])
        out["periods"][g] = e
    P = out["periods"]
    def cnt(v, key="p"):
        xs = [P[g][v] for g in gs if v in P[g]]
        return [sum(x[key] < 0.05 for x in xs), len(xs)]
    out["P1"] = {"r1": [sum(P[g]["r1"]["p"] < 0.05 for g in gs), len(gs)], **{v: cnt(v) for v in VARS if v != "bge_unread"}}
    sh = [P[g]["bge"]["sh"] for g in gs if "bge" in P[g] and P[g]["bge"]["sh"] is not None]
    sh1 = [P[g]["r1"]["sh"] for g in gs if P[g]["r1"]["sh"] is not None]
    out["P3"] = {"r1": [sum(x > 0 for x in sh1), len(sh1), float(np.median(sh1))], "bge": [sum(x > 0 for x in sh), len(sh), float(np.median(sh))]}
    out["verdicts_bge"] = {k: sum(P[g].get("bge", {}).get("v") == k for g in gs) for k in ("supported", "mixed", "failed")}
    hm = [P[g]["bge"]["human"] for g in gs if "bge" in P[g] and P[g]["bge"].get("human")]
    out["P5"] = [sum(h["above_median_agent"] for h in hm), len(hm)]
    # exposure contrast: multi-room periods where round 1 computed T_unseen
    mr = [g for g in gs if P[g]["r1"]["T_unseen"] is not None and "bge" in P[g] and P[g]["bge"]["T_unseen"] is not None]
    k = sum(P[g]["bge"]["T"] > P[g]["bge"]["T_unseen"] for g in mr)
    out["P8"] = dict(periods=mr, seen_gt_unseen=[k, len(mr)], p_sign=float(binomtest(k, len(mr), 0.5, alternative="greater").pvalue) if mr else None,
                     unseen_sig=sum(P[g]["bge"]["p_unseen"] < 0.05 for g in mr))
    # H57 placebo: unread same-room messages (S0 = unread) vs seen
    for vv in ("bge_unread", "bge_unread_tau60"):
        U = [g for g in gs if vv in P[g]]
        out["H57_" + vv] = dict(n=len(U), unread_sig=sum(P[g][vv]["p_unseen"] < 0.05 for g in U),
                                seen_sig=sum(P[g][vv]["p"] < 0.05 for g in U),
                                seen_gt_unread=sum(np.nan_to_num(P[g][vv]["T"], nan=-9) > np.nan_to_num(P[g][vv]["T_unseen"], nan=-9) for g in U),
                                median_T_seen=float(np.nanmedian([P[g][vv]["T"] for g in U])) if U else None,
                                median_T_unread=float(np.nanmedian([P[g][vv]["T_unseen"] for g in U])) if U else None,
                                periods=U)
    for v in ("gte", "style", "bge_dedupe"):
        rs = [P[g][v]["rho_out_vs_bge"] for g in gs if v in P[g] and P[g][v]["rho_out_vs_bge"] is not None]
        tops = [P[g][v]["top"] == P[g]["bge"]["top"] for g in gs if v in P[g] and "bge" in P[g]]
        out[f"agree_{v}"] = dict(median_rho_out=float(np.nanmedian(rs)) if rs else None, same_top=[sum(tops), len(tops)])
    rr = [P[g]["rho_out_r1_bge"] for g in gs if P[g].get("rho_out_r1_bge") is not None]
    out["agree_r1_bge"] = dict(median_rho_out=float(np.nanmedian(rr)), same_top=[sum(P[g]["r1"]["top"] == P[g]["bge"]["top"] for g in gs if "bge" in P[g]), len(gs)])
    (R1B / "cross_period_r1b.json").write_text(json.dumps(out, indent=1, default=float))
    for g in gs:
        e = P[g]
        print(g, {k: (round(v["T"] * 100, 3), round(v["p"], 3)) for k, v in e.items() if isinstance(v, dict) and "T" in v},
              e.get("bge", {}).get("v"), e.get("bge", {}).get("sh"))
    print(json.dumps({k: v for k, v in out.items() if k != "periods"}, indent=1, default=float))


def estimates():
    sys.path.insert(0, str(ROOT / "infra/shared"))
    from estimates import map_unit, write_estimates
    rows = []
    for v in VARS:
        for g in periods():
            x = load(v, g)
            if not x:
                continue
            base = dict(goal_no=g, period_unit=map_unit(g), role="replication", method=f"H32.r1b_{v}", channel="content",
                        null=f"cross-day circular shift ({x['n_null']})", ci_kind="none",
                        source=f"data/processed/H32-information-current-leaders/r1b/{v}/G{g:02d}/result.json")
            rows.append({**base, "statistic": "T_transfer", "estimate": x["T"], "notes": f"p_T {x['p_T']:.3f}"})
            if x.get("T_unseen") is not None:
                rows.append({**base, "statistic": "T_unread" if v == "bge_unread" else "T_unseen_other_room", "estimate": x["T_unseen"],
                             "notes": f"p {x['p_T_unseen']:.3f}"})
    nat = json.loads((R1B / "natives.json").read_text())
    for g, key, stat, val in ((26, "G26_term1", "rank_elected_leader", nat["G26_term1"]["rank_17"]),
                              (35, "G35_leads", "mean_percentile_lead_designer", nat["G35_leads"]["mean_percentile"]),
                              (44, "G44_window", "rank_installed_leader", nat["G44_window"]["rank_28_among_agents"])):
        rows.append(dict(goal_no=g, period_unit=map_unit(g), role="native", method="H32.r1b_segment_outflow", channel="content",
                         statistic=stat, estimate=val, ci_kind="none", null="cross-day circular shift (40)",
                         source="data/processed/H32-information-current-leaders/r1b/natives.json"))
    write_estimates(rows, "H32")
    print(len(rows), "rows")


def readmes():
    nat = json.loads((R1B / "natives.json").read_text())
    natv = {26: nat["G26_term1"]["verdict"], 35: nat["G35_leads"]["verdict"], 44: nat["G44_window"]["verdict"]}
    for g in periods():
        b, gt_, st = load("bge", g), load("gte", g), load("style", g)
        if not b:
            continue
        sh = (b.get("split_half") or {}).get("rho_out")
        v = b["verdict_general"]
        r1 = load("r1", g)
        if v == "supported" and (r1.get("human") or {}).get("n_msgs", 0) >= 15 and not (b.get("human") or {}).get("above_median_agent", True):
            v = "mixed"      # round-1 rule: P5 (humans as a known source) decides ground-truth periods
        line = f"**Verdict (1b):** {v} (ledger exposure: T {b['T'] * 100:+.3f}% p {b['p_T']:.3f}"
        if sh is not None:
            line += f", split-half ρ {sh:+.2f}"
        if gt_:
            line += f"; gte p {gt_['p_T']:.3f}"
        if st:
            line += f"; style-resid p {st['p_T']:.3f}"
        line += ")"
        if g in natv:
            line = line.replace("**Verdict (1b):** ", f"**Verdict (1b):** {natv[g]} (native leader test); general ")
        f = PD / f"G{g:02d}" / "README.md"
        s = f.read_text()
        s = re.sub(r"\*\*Verdict \(1b\):\*\*[^\n]*\n", "", s)
        s = re.sub(r"(\*\*Verdict:\*\*[^\n]*\n)", lambda m: m.group(1) + line + "\n", s, count=1)
        f.write_text(s)
    print("ok")


if __name__ == "__main__":
    {"table": table, "estimates": estimates, "readmes": readmes}[sys.argv[1] if len(sys.argv) > 1 else "table"]()
