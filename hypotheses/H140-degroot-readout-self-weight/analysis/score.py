"""H140 round-1 scoring: pools, verdicts by the card's rules, estimates rows, figures and markdown tables.

Usage: uv run python .../analysis/score.py [--write-estimates]
Reads data/processed/H140-degroot-readout-self-weight/results/*.json and synthetic/summary_*.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h140lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
DATA = ROOT / "data/processed/H140-degroot-readout-self-weight"
RES = DATA / "results"
FIG = HERE.parent / "figures"
MIN_ROWS = 300


def load_units() -> dict:
    out = {}
    for p in sorted(RES.glob("units_G*.json")):
        out.update(json.loads(p.read_text()))
    return out


def g(d, *ks, default=None):
    for k in ks:
        if not isinstance(d, dict) or k not in d or d[k] is None:
            return default
        d = d[k]
    return d


def pool(units, tag, fit, key, only=None):
    est, se, names = [], [], []
    for u, r in units.items():
        if only is not None and u not in only:
            continue
        f = g(r, tag, fit)
        if f and f.get(key) is not None and f.get(f"{key}_se") is not None:
            est.append(f[key]); se.append(f[f"{key}_se"]); names.append(u)
    p = L.dl_pool(est, se)
    p["units"] = names
    return p


def fmt(x, n=2):
    return "–" if x is None else f"{x:.{n}f}"


def ci(f, key, n=2):
    if not f or f.get(key) is None:
        return "–"
    lo, hi = f.get(f"{key}_lo"), f.get(f"{key}_hi")
    return f"{fmt(f[key], n)} [{fmt(lo, n)}, {fmt(hi, n)}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-estimates", action="store_true")
    a = ap.parse_args()
    U = load_units()
    testable = [u for u, r in U.items() if g(r, "bge", "n_scored", default=0) >= MIN_ROWS]
    S = {"testable": testable, "units": list(U)}
    # ---------------- P1
    for tag in ("bge", "gte", "bgeF", "bgeW"):
        S[f"P1_A1_{tag}"] = pool(U, tag, "A1", "w1")
    S["P1_main_bge"] = pool(U, "bge", "main", "w1")
    S["P1_main_gte"] = pool(U, "gte", "main", "w1")
    S["P1_noDn_bge"] = pool(U, "bge", "noDn", "w1")
    S["P1_A1noDn_bge"] = pool(U, "bge", "A1noDn", "w1")
    S["P1_A1_bge_testable"] = pool(U, "bge", "A1", "w1", only=set(testable))
    for v in ("A1chat", "A1ols", "A1p1", "A1_norepeat"):
        S[f"P1_{v}_bge"] = pool(U, "bge", v, "w1")
    S["P1_units_pos"] = {tag: [u for u in testable if (g(U[u], tag, "A1", "w1_lo") or -1) > 0] for tag in ("bge", "gte")}
    S["P1_units_neg"] = {tag: [u for u in testable if (g(U[u], tag, "A1", "w1_hi") or 1) < 0] for tag in ("bge", "gte")}
    # ---------------- P2 (identified units only)
    for tag in ("bge", "gte"):
        ident = [u for u, r in U.items() if g(r, tag, "identified")]
        S[f"ident_{tag}"] = ident
        S[f"P2_a_{tag}"] = pool(U, tag, "A1", "a", only=set(ident))
        S[f"P2_a_all_{tag}"] = pool(U, tag, "A1", "a")
    # ---------------- P3
    S["P3_w2_bge"] = pool(U, "bge", "A1", "w2"); S["P3_w2_gte"] = pool(U, "gte", "A1", "w2")
    S["P3_w2_main_bge"] = pool(U, "bge", "main", "w2")
    for tag in ("bge", "gte"):
        w_with, w_wo = S[f"P1_A1_{tag}"].get("est"), pool(U, tag, "A1noDn", "w1").get("est")
        S[f"P3_reduction_{tag}"] = None if not w_wo else 1 - w_with / w_wo
    S["P3_reduction_main_bge"] = 1 - S["P1_main_bge"]["est"] / S["P1_noDn_bge"]["est"] if S["P1_noDn_bge"].get("est") else None
    # ---------------- P4
    for tag in ("bge", "gte"):
        pg1, pgF = pool(U, tag, "A1", "gamma1"), pool(U, tag, "A1", "gammaF")
        S[f"P4_gamma1_{tag}"], S[f"P4_gammaF_{tag}"] = pg1, pgF
        S[f"P4_ratio_{tag}"] = pgF["est"] / pg1["est"] if pg1.get("est") else None
        ratios = [g(r, tag, "A1", "gammaF") / g(r, tag, "A1", "gamma1") for r in U.values()
                  if g(r, tag, "A1", "gamma1") and abs(g(r, tag, "A1", "gamma1")) > 1e-9]
        S[f"P4_ratio_median_units_{tag}"] = float(np.median(ratios)) if ratios else None
        est = [g(r, tag, "contrast", "contrast") for r in U.values() if g(r, tag, "contrast", "se")]
        se = [g(r, tag, "contrast", "se") for r in U.values() if g(r, tag, "contrast", "se")]
        S[f"P4_contrast_{tag}"] = L.dl_pool(est, se)
    # ---------------- P5 closure per k bin
    for tag in ("bge",):
        bins = {}
        for u, r in U.items():
            for row in g(r, tag, "closure", default=[]) or []:
                if row.get("se"):
                    bins.setdefault(row["bin"], ([], []))
                    bins[row["bin"]][0].append(row["Sigma"]); bins[row["bin"]][1].append(row["se"])
        S[f"P5_closure_{tag}"] = {b: L.dl_pool(e, s) for b, (e, s) in bins.items()}
        inb = [b for b, p in S[f"P5_closure_{tag}"].items() if p.get("est") is not None and 0.8 <= p["est"] <= 1.2]
        S[f"P5_inband_{tag}"] = (len(inb), len(S[f"P5_closure_{tag}"]))
    # ---------------- N1 / N2 nulls
    S["N1_sur"] = {u: g(r, "bge", "N1_sur") for u, r in U.items()}
    S["N2_perm"] = {u: g(r, "bge", "N2_perm") for u, r in U.items()}
    # ---------------- NE41
    ne = json.loads((RES / "ne41.json").read_text()) if (RES / "ne41.json").exists() else {}
    for tag in ("bge", "gte"):
        for kind in ("forced", "vol"):
            rr = [v for v in ne.values() if v["model"] == tag and v["kind"] == kind and v.get("fit")]
            p = L.dl_pool([v["fit"]["dw_first"] for v in rr], [v["fit"]["dw_first_se"] for v in rr])
            ds = float(np.average([v["ds"] for v in rr], weights=[v["n_first"] for v in rr])) if rr else None
            pb = L.dl_pool([v["fit"]["w_base"] for v in rr], [v["fit"]["w_base_se"] for v in rr])
            S[f"NE41_{tag}_{kind}"] = {"dw": p, "ds_weighted": ds, "w_base": pb, "n_units": len(rr),
                                       "n_first": int(sum(v["n_first"] for v in rr)),
                                       "ratio": (p["est"] / ds) if (p.get("est") is not None and ds) else None}
    # ---------------- wakes
    wk = json.loads((RES / "wakes.json").read_text()) if (RES / "wakes.json").exists() else {}
    for tag in ("bge", "gte"):
        rr = {k.split("|")[0]: v for k, v in wk.items() if v["model"] == tag}
        pw = L.dl_pool([g(v, "A1", "w1") for v in rr.values() if g(v, "A1", "w1_se")],
                       [g(v, "A1", "w1_se") for v in rr.values() if g(v, "A1", "w1_se")])
        pa = L.dl_pool([g(v, "A1", "a") for v in rr.values() if g(v, "A1", "a_se")],
                       [g(v, "A1", "a_se") for v in rr.values() if g(v, "A1", "a_se")])
        pt = pool(U, tag, "A1", "w1", only={u for u in U if u.startswith("51")})
        S[f"N2wake_{tag}"] = {"w1": pw, "a": pa, "w1_talk51": pt,
                              "dw1": (pw["est"] - pt["est"]) if pw.get("est") is not None and pt.get("est") is not None else None,
                              "n_rows": int(sum(v.get("n_scored", 0) for v in rr.values()))}
    reg = json.loads((RES / "reg12.json").read_text()) if (RES / "reg12.json").exists() else {}
    S["reg12"] = {k: {"n": v["n_scored"], "a": g(v, "o2A1", "a"), "a_lo": g(v, "o2A1", "a_lo"), "a_hi": g(v, "o2A1", "a_hi"),
                      "contrast": g(v, "contrast", "contrast"), "c_lo": g(v, "contrast", "lo"), "r": v.get("r")} for k, v in reg.items()}
    (RES / "score.json").write_text(json.dumps(S, indent=1, default=float))
    # ---------------- per-unit table
    print("| Unit | n | ŵ₁ A1 (bge) | ŵ₁ registered | ŵ₂ A1 | â A1 | γ_F/γ₁ | contrast | r | id | ŵ₁ A1 (gte) |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for u in sorted(U, key=lambda x: (int(''.join(c for c in x if c.isdigit())), x)):
        r = U[u]; b = r["bge"]
        rat = (g(b, "A1", "gammaF") / g(b, "A1", "gamma1")) if g(b, "A1", "gamma1") else None
        c = b.get("contrast", {}) or {}
        print(f"| {u} | {b['n_scored']} | {ci(b.get('A1'), 'w1')} | {ci(b.get('main'), 'w1')} | {ci(b.get('A1'), 'w2')} | "
              f"{ci(b.get('A1'), 'a')} | {fmt(rat)} | {fmt(c.get('contrast'), 3)} [{fmt(c.get('lo'), 3)}, {fmt(c.get('hi'), 3)}] | "
              f"{fmt(b.get('r'))} | {'y' if b.get('identified') else 'n'} | {ci(r['gte'].get('A1'), 'w1')} |")
    keys = ["P1_A1_bge", "P1_A1_gte", "P1_A1_bge_testable", "P1_main_bge", "P1_main_gte", "P1_noDn_bge", "P1_A1noDn_bge",
            "P1_A1_bgeF", "P1_A1_bgeW", "P1_A1chat_bge", "P1_A1ols_bge", "P1_A1p1_bge", "P1_A1_norepeat_bge", "P2_a_bge", "P2_a_gte",
            "P2_a_all_bge", "P3_w2_bge", "P3_w2_gte", "P3_w2_main_bge", "P4_gamma1_bge", "P4_gammaF_bge", "P4_contrast_bge", "P4_contrast_gte"]
    for k in keys:
        p = S[k]
        print(k, {kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in p.items() if kk != "units"}, "k_units", p.get("k"))
    for k in ("P1_units_pos", "P1_units_neg", "ident_bge", "ident_gte", "P3_reduction_bge", "P3_reduction_gte", "P3_reduction_main_bge",
              "P4_ratio_bge", "P4_ratio_gte", "P4_ratio_median_units_bge", "P5_inband_bge"):
        print(k, S[k])
    print("P5", {b: (round(p.get("est", np.nan), 3), round(p.get("lo", np.nan), 3), round(p.get("hi", np.nan), 3))
                 for b, p in S["P5_closure_bge"].items()})
    for k in [k for k in S if k.startswith("NE41") or k.startswith("N2wake")]:
        print(k, json.dumps(S[k], default=lambda x: round(float(x), 4)))
    print("reg12", json.dumps(S["reg12"], default=lambda x: round(float(x), 3)))
    print("N1", json.dumps({u: v for u, v in S["N1_sur"].items()}, default=lambda x: round(float(x), 3)))
    print("N2", json.dumps({u: v for u, v in S["N2_perm"].items()}, default=lambda x: round(float(x), 3)))
    if a.write_estimates:
        write_estimates(U, ne, wk)


def write_estimates(U, ne, wk):
    import estimates as E
    rows = []
    base = {"ci_level": 0.95, "ci_kind": "percentile", "n_kind": "talk calls", "source": "data/processed/H140-degroot-readout-self-weight/results"}

    def add(unit, goal, stat, chan, est, lo, hi, n, method, null, role, se=None, notes=None):
        if est is None:
            return
        rows.append({"hypothesis": "H140", "period_unit": unit, "goal_no": goal, "statistic": stat, "channel": chan, "estimate": est,
                     "ci_lo": lo, "ci_hi": hi, "n": float(n), "method": method, "null": null, "role": role, "se": se, "notes": notes,
                     "post_hoc": False, **base})
    for u, r in U.items():
        goal = int(r["goal_no"])
        for tag, model in (("bge", "bge_small"), ("gte", "gte_modernbert")):
            b = r.get(tag, {})
            f = b.get("A1")
            if not f:
                continue
            n = b["n_scored"]
            m = "IV 2SLS over 32 coords, A1 spec (s_self, call gap, wall-clock gap, log(1+k), log(1+kF) terms), b profiled; agent-day cluster bootstrap 300"
            add(u, goal, "h140_selfweight_slope_w1", f"{model}|style_resid32", f["w1"], f["w1_lo"], f["w1_hi"], n, m,
                "w1 = 0 (bootstrap CI); N2 within-agent-day permutation", "replication", f.get("w1_se"))
            add(u, goal, "h140_selfweight_callgap_w2", f"{model}|style_resid32", f["w2"], f["w2_lo"], f["w2_hi"], n, m, "w2 = 0",
                "replication", f.get("w2_se"))
            add(u, goal, "h140_readweight_exponent", f"{model}|style_resid32", f["a"], f["a_lo"], f["a_hi"], n, m,
                "a = 1 (linear) and a = 0 (one read per call); N1 cross-day surrogate batches", "replication", f.get("a_se"),
                notes=f"identified={b.get('identified')} (H113 A1 rule: contrast CI > 0 and r < 0.7)")
            if f.get("gamma1"):
                rows.append({"hypothesis": "H140", "period_unit": u, "goal_no": goal, "statistic": "h140_inflight_ratio",
                                 "channel": f"{model}|style_resid32", "estimate": f["gammaF"] / f["gamma1"], "ci_lo": None, "ci_hi": None,
                                 "n": float(n), "method": m, "null": "gammaF/gamma1 = 1 (convergence)", "role": "replication",
                                 "ci_kind": "none", "n_kind": "talk calls", "source": base["source"], "post_hoc": False})
            for row in b.get("closure", []) or []:
                add(u, goal, "h140_closure_sum", f"{model}|style_resid32|k={row['bin']}", row["Sigma"], row.get("lo"), row.get("hi"),
                    row["n"], m + "; closure at bin means", "Sigma = 1 (literal DeGroot)", "replication", row.get("se"))
    for k, v in ne.items():
        f = v.get("fit")
        if not f:
            continue
        model = "bge_small" if v["model"] == "bge" else "gte_modernbert"
        add(v["unit"], int(v["goal_no"]), "h140_erasure_selfweight_step", f"{model}|style_resid32|{v['kind']}", f["dw_first"],
            f["dw_first_lo"], f["dw_first_hi"], v["n_first"] + v["n_ctrl"],
            "IV fit with a first-post-reset indicator on p (p = last pre-reset content); A1 nuisance terms; cluster bootstrap 300",
            "dw = 0 (R-well)", "native", f.get("dw_first_se"), notes=f"ds_self={v.get('ds')}; n_first={v['n_first']}")
    for k, v in wk.items():
        f = v.get("A1")
        if not f:
            continue
        model = "bge_small" if v["model"] == "bge" else "gte_modernbert"
        add(v["unit"], 51, "h140_selfweight_slope_w1", f"{model}|style_resid32|timer_wakes", f["w1"], f["w1_lo"], f["w1_hi"],
            v["n_scored"], "A1 spec on #51 timer-wake batches (D2)", "w1 = 0", "native", f.get("w1_se"))
        add(v["unit"], 51, "h140_readweight_exponent", f"{model}|style_resid32|timer_wakes", f["a"], f["a_lo"], f["a_hi"],
            v["n_scored"], "A1 spec on #51 timer-wake batches (D2)", "a = 1", "native", f.get("a_se"))
    E.write_estimates(rows, hypothesis="H140")
    print("estimates rows:", len(rows))


if __name__ == "__main__":
    main()
