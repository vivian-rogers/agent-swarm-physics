"""H93: score the card's predictions P1-P8 from results/G<NN>.json (and natives), and write the estimates rows.

  uv run python hypotheses/H93-brock-durlauf-project-choice/analysis/score.py [--write-estimates]
Writes results/score.json. A fit counts as identified when its share coefficient has SE <= 5 (CI width < 20).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H93-brock-durlauf-project-choice"
REPL = [30, 31, 33, 35, 36, 38, 39, 40, 41, 42, 51]
ALL = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
OWN = {39, 42, 51}
SE_MAX = 5.0


def load(g):
    return json.loads((DATA / "results" / f"G{g:02d}.json").read_text())


def pool(c, m, key="pool"):
    x = ((c or {}).get("fits") or {}).get(m) or {}
    p = x.get(key)
    if not p or p.get("se") is None or not np.isfinite(p["se"]) or p["se"] > SE_MAX:
        return None
    return p


def ident(c, m="M4"):
    return pool(c, m) is not None


def pmulti(c):
    """max P_multi over identified unit/period fits of M4."""
    fits = (((c or {}).get("fits") or {}).get("M4") or {})
    eq = (c or {}).get("equilibria") or {}
    out = []
    if fits.get("scope") == "units":
        for u, f in fits["units"].items():
            if f.get("gamma_se") is not None and f["gamma_se"] <= SE_MAX and u in eq and "p_multi" in eq[u]:
                out.append((u, eq[u]["p_multi"], eq[u].get("n_fp")))
    else:
        f = fits.get("fit") or {}
        if f.get("gamma_se") is not None and f["gamma_se"] <= SE_MAX and "period" in eq and "p_multi" in eq["period"]:
            out.append(("period", eq["period"]["p_multi"], eq["period"].get("n_fp")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-estimates", action="store_true")
    a = ap.parse_args()
    R = {g: load(g) for g in ALL if (DATA / "results" / f"G{g:02d}.json").exists()}
    sc = {}
    # P1: M0 > 0 with CI > 0 in >= 2/3 of testable work periods (replication periods)
    t = [(g, pool(R[g]["work"], "M0")) for g in REPL if g in R]
    t = [(g, p) for g, p in t if p]
    hits = [g for g, p in t if p["lo"] > 0]
    sc["P1"] = {"tested": [g for g, _ in t], "hits": hits, "frac": len(hits) / max(len(t), 1),
                "verdict": "supported" if len(hits) >= 2 / 3 * len(t) else "failed"}
    # P2: M2 <= 0.5 M0 in >= 2/3 of the P1 periods
    r2 = {g: (pool(R[g]["work"], "M2") or {}).get("est", np.nan) / pool(R[g]["work"], "M0")["est"] for g in hits}
    sc["P2"] = {"ratios": r2, "n_le_half": sum(v <= 0.5 for v in r2.values()),
                "verdict": "supported" if sum(v <= 0.5 for v in r2.values()) >= 2 / 3 * max(len(r2), 1) else "failed"}
    # P3: M4 CI includes 0 in >= 1/2 of testable (identified) replication periods (work)
    t3 = {g: pool(R[g]["work"], "M4") for g in REPL if g in R and pool(R[g]["work"], "M4")}
    inc = [g for g, p in t3.items() if p["lo"] <= 0 <= p["hi"]]
    pos = [g for g, p in t3.items() if p["lo"] > 0]
    neg = [g for g, p in t3.items() if p["hi"] < 0]
    sc["P3"] = {"identified": list(t3), "ci_includes_0": inc, "positive": pos, "negative": neg,
                "verdict": "supported" if len(inc) >= len(t3) / 2 else "failed"}
    # P4: P_multi < 0.5 in every testable period (both channels; identified fits)
    viol, alln = [], 0
    for g in ALL:
        if g not in R:
            continue
        for ch in ("work", "attention"):
            for u, p, nfp in pmulti(R[g][ch]):
                alln += 1
                if p >= 0.5:
                    viol.append((g, ch, u, p, nfp))
    sc["P4"] = {"fits": alln, "violations": viol, "verdict": "supported" if not viol else "failed"}
    # P5: Spearman(m*, m) >= 0.6 over replication periods (work), m* from the uniform start at the M4 fit
    xs, ys, lab = [], [], []
    for g in REPL:
        if g not in R:
            continue
        c = R[g]["work"]
        eq = c.get("equilibria") or {}
        ms = [v.get("m_star_uniform") for v in eq.values() if isinstance(v, dict) and v.get("m_star_uniform") is not None]
        if ms and c.get("m") is not None and ident(c):
            xs.append(float(np.mean(ms))); ys.append(c["m"]); lab.append(g)
    rho = spearmanr(xs, ys).statistic if len(xs) >= 4 else None
    sc["P5"] = {"periods": lab, "m_star": xs, "m": ys, "spearman": rho,
                "verdict": None if rho is None else ("supported" if rho >= 0.6 else ("failed" if rho < 0.3 else "mixed"))}
    # P6: sign agreement work vs attention (identified in both)
    agree, both = [], []
    for g in ALL:
        if g not in R:
            continue
        pw, pa = pool(R[g]["work"], "M4"), pool(R[g]["attention"], "M4")
        if pw and pa:
            both.append(g)
            if np.sign(pw["est"]) == np.sign(pa["est"]):
                agree.append(g)
    sc["P6"] = {"both": both, "agree": agree, "verdict": "supported" if len(agree) >= 2 / 3 * max(len(both), 1) else "failed"}
    # P7: read > unread (A2 proxy), in-room > other-room (two-room periods), |cross - same lab| <= 1
    p7 = {"read_gt_unread": [], "in_gt_out": [], "lab_close": [], "cross_pos": []}
    n7 = {"read": 0, "room": 0, "lab": 0}
    for g in ALL:
        if g not in R:
            continue
        c = R[g]["work"]
        if not ident(c):
            continue
        rd, nr = pool(c, "SPLIT_read", "pool_s_read"), (((c["fits"].get("SPLIT_read") or {}).get("pool_s_noread")) or None)
        if rd:
            n7["read"] += 1
            if nr is None or nr.get("se", 99) > SE_MAX or rd["est"] > nr["est"]:
                p7["read_gt_unread"].append(g)
        pin, pout = pool(c, "SPLIT_room", "pool_s_in"), ((c["fits"].get("SPLIT_room") or {}).get("pool_s_out"))
        if pin and pout:
            n7["room"] += 1
            if pout.get("se", 99) > SE_MAX or pin["est"] > pout["est"]:
                p7["in_gt_out"].append(g)
        ps, pc = pool(c, "SPLIT_lab", "pool_s_same"), pool(c, "SPLIT_lab", "pool_s_cross")
        if ps and pc:
            n7["lab"] += 1
            if abs(ps["est"] - pc["est"]) <= 1:
                p7["lab_close"].append(g)
            if pc["lo"] > 0:
                p7["cross_pos"].append(g)
    sc["P7"] = {**p7, "n": n7}
    # P8: |dLL| < 0.02 per event in >= 1/2 of periods (work)
    d8 = {g: R[g]["work"].get("dLL_M4_minus_R3_per_event") for g in ALL if g in R and ident(R[g]["work"])}
    sc["P8"] = {"dLL": d8, "ties": [g for g, v in d8.items() if v is not None and abs(v) < 0.02],
                "R3_better": [g for g, v in d8.items() if v is not None and v <= -0.02]}
    sc["P8"]["verdict"] = "supported" if len(sc["P8"]["ties"]) >= len(d8) / 2 else "failed"
    # kickoff-free placebo, attention table
    sc["nonamed"] = {g: pool(R[g]["work"], "M4_nonamed") for g in ALL if g in R}
    sc["attention_M4"] = {g: pool(R[g]["attention"], "M4") for g in ALL if g in R}
    sc["work_M4"] = {g: pool(R[g]["work"], "M4") for g in ALL if g in R}
    sc["work_M0"] = {g: pool(R[g]["work"], "M0") for g in ALL if g in R}
    (DATA / "results" / "score.json").write_text(json.dumps(sc, indent=1, default=float))
    for k in ("P1", "P2", "P3", "P4", "P5", "P6", "P8"):
        print(k, sc[k].get("verdict"), {kk: vv for kk, vv in sc[k].items() if kk not in ("verdict", "dLL", "ratios", "m_star", "m")})
    print("P7", sc["P7"])
    if a.write_estimates:
        write_rows(R)


def write_rows(R):
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import estimates as E
    rows = []
    SINGLE = {33: "33", 35: "35", 37: "37", 39: "39", 40: "40", 41: "41"}
    for g, r in R.items():
        role = "native" if g in (37, 44) else "replication"
        src = f"data/processed/H93-brock-durlauf-project-choice/results/G{g:02d}.json"
        for ch, chn in (("work", "project (work)"), ("attention", "project (attention)")):
            c = r.get(ch)
            if not c:
                continue
            for m, stat, meth in (("M4", "bd_share_coupling_betaJ", "conditional logit, share + kickoff-named + habit + "
                                   "log(1+cumulative arrivals) (M4, validated on synthetic); Wald SE; DL pool over testable units"),
                                  ("M0", "bd_share_coupling_betaJ_naive", "conditional logit, share + NEW only (M0); Wald SE; "
                                   "DL pool over testable units")):
                x = ((c.get("fits") or {}).get(m) or {})
                p = x.get("pool")
                if not p or p.get("se") is None:
                    continue
                ok = p["se"] <= SE_MAX
                multi = x.get("scope") == "units"
                rows.append({"period_unit": SINGLE.get(g, f"G{g:02d}"), "goal_no": g, "statistic": stat, "channel": chn,
                             "estimate": p["est"], "se": p["se"], "ci_lo": p["lo"], "ci_hi": p["hi"], "ci_level": 0.95,
                             "ci_kind": "se_z", "n": c["events"], "n_kind": "events",
                             "method": meth + ("" if multi else "; single fit with unit-specific NEW constants"),
                             "null": "betaJ = 0 (fields only); M4 false-positive rate <= 0.10 under static fitness spread, "
                                     "0.05-1.0 under fast repo bursts (A2)",
                             "role": role, "status": "ok" if ok else "unstable", "source": src,
                             "notes": "share coefficient; not separable from fast common repo bursts (A2)" if m == "M4" else
                             "fitness and habit confounded (A1)"})
                if multi and m == "M4":
                    for u, f in x["units"].items():
                        if f.get("gamma_se") is None:
                            continue
                        rows.append({"period_unit": u, "goal_no": g, "statistic": stat, "channel": chn,
                                     "estimate": f["gamma"], "se": f["gamma_se"], "ci_lo": f["gamma_lo"], "ci_hi": f["gamma_hi"],
                                     "ci_level": 0.95, "ci_kind": "se_z", "n": f["n_events"], "n_kind": "events",
                                     "method": meth.replace("; DL pool over testable units", "; unit fit"),
                                     "null": "betaJ = 0 (fields only)", "role": role,
                                     "status": "ok" if f["gamma_se"] <= SE_MAX else "unstable", "source": src})
            for u, pm, nfp in pmulti(c):
                rows.append({"period_unit": u if u != "period" else SINGLE.get(g, f"G{g:02d}"), "goal_no": g,
                             "statistic": "bd_p_multi_equilibria", "channel": chn, "estimate": pm, "ci_kind": "none",
                             "n": 100 if g == 51 else 200, "n_kind": "parametric draws",
                             "method": "share of parametric draws of the M4 fit with >= 2 stable Brock-Durlauf fixed points "
                                       "(logit-dynamics stability)", "null": "unique equilibrium", "role": role, "status": "ok",
                             "source": src})
            if c.get("m") is not None:
                rows.append({"period_unit": SINGLE.get(g, f"G{g:02d}"), "goal_no": g, "statistic": "bd_order_parameter_m",
                             "channel": chn, "estimate": c["m"], "ci_kind": "none", "n": c["events"], "n_kind": "events",
                             "method": "event-averaged largest-option share of the hosted agents (>= 3 hosts)", "null": None,
                             "role": role, "status": "ok", "source": src})
    E.write_estimates(rows, hypothesis="H93")
    print(len(rows), "estimate rows")


if __name__ == "__main__":
    main()
