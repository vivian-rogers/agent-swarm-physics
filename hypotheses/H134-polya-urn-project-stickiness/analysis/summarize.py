"""H134 round 1: combine per-unit results (results/<unit>.json) into the card's predictions and kill rules, write
results/summary.json and the shared estimates rows.

  P1  beta_F (model b) CI > 0 in >= 2/3 of testable units
  P2  beta_F CI contains 1 in >= 1/2 of units, and the random-effects mean CI contains 1
  P3  eps(F) over the G51 units (per-day held-out LL summed over units) above the synthetic proxy band (Kill B)
  P4  gamma and KM(100), KM(300) inside the O3 bands in >= 1/2 of units (Kill A: gamma or KM(100) outside in >= 1/2)
  P5  beta_d < 0 with CI < 0 in G51 (random-effects mean over the G51 units)
  N1  pooled G51 reset step (inverse-variance mean of unit MH log ORs) > 0 with CI > 0; obs/pred in [0.5, 2];
      placebo CI contains 0 (Kill C)
  N2  RE mean beta_F own-role (39, 42a, 42b) minus shared-goal (37, 38a, 38b, 38e, 41): |diff| < 0.3, CI contains 0
  N3  G38 simulated gamma vs H129's ranges (descriptive)
Usage: uv run python .../analysis/summarize.py [--write-estimates]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h134lib as L  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))

OWN = ("39", "42a", "42b")
SHARED = ("37", "38a", "38b", "38e", "41")
Z = 1.959964


def re_mean(est, se):
    """DerSimonian-Laird random-effects mean, SE, tau^2."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    w = 1 / se ** 2
    m0 = np.sum(w * est) / w.sum()
    Q = np.sum(w * (est - m0) ** 2)
    k = len(est)
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - np.sum(w ** 2) / w.sum())) if k > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    m = np.sum(ws * est) / ws.sum()
    return float(m), float(np.sqrt(1 / ws.sum())), float(tau2), int(k)


def ci_se(ci):
    return (ci[1] - ci[0]) / (2 * Z) if ci and ci[0] is not None and ci[1] is not None else float("nan")


def eps_pooled(res_units):
    """eps(F) and G(A) over several units: per-day held-out contributions concatenated across units; day bootstrap."""
    per = {m: np.concatenate([np.array(r["O2"]["per"][m]) for r in res_units]) for m in ("B", "B+A", "B+F", "B+F+A")}
    n = sum(r["n_rows"] for r in res_units)
    GA = per["B+A"] - per["B"]; left = per["B+F+A"] - per["B+F"]; gF = per["B+F"] - per["B"]
    rng = np.random.default_rng(L.SEED)
    nd = len(GA)
    bs_e, bs_g, bs_f = [], [], []
    for _ in range(2000):
        i = rng.integers(0, nd, nd)
        g = GA[i].sum()
        bs_g.append(g * 1000 / n); bs_f.append(gF[i].sum() * 1000 / n)
        bs_e.append(1 - left[i].sum() / g if g > 0 else np.nan)
    return {"eps_F": float(1 - left.sum() / GA.sum()), "eps_F_ci": L.pct(bs_e), "G_A": float(GA.sum() * 1000 / n),
            "G_A_ci": L.pct(bs_g), "G_F": float(gF.sum() * 1000 / n), "G_F_ci": L.pct(bs_f), "n_days": int(nd)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-estimates", action="store_true")
    a = ap.parse_args()
    counts = {r["unit_id"]: r for r in json.loads((L.OUT / "counts.json").read_text())}
    R = {}
    for p in sorted((L.OUT / "results").glob("*.json")):
        if p.stem in counts and counts[p.stem]["testable"]:
            R[p.stem] = json.loads(p.read_text())
    syn = json.loads((L.OUT / "synthetic" / "summary.json").read_text())
    units = sorted(R)
    S = {"units": units, "per_unit": {}}
    bF, bFse, bd, bdse = [], [], [], []
    for u in units:
        r = R[u]
        b = r["O1"]["b"]; aa = r["O1"]["a"]
        row = {"bF_b": b["F"]["est"], "bF_b_ci": b["F"]["ci"], "bF_a": aa["F"]["est"], "bF_a_ci": aa["F"]["ci"],
               "bd_b": b["A"]["est"], "bd_b_ci": b["A"]["ci"], "bK_b": b["K"]["est"], "bK_b_ci": b["K"]["ci"],
               "n_rows": r["n_rows"], "n_leave": r["O1"]["n_leave"], "n_visits": r["n_visits"], "mean_f": r["mean_f"]}
        row["P1"] = row["bF_b_ci"][0] > 0
        row["P2"] = row["bF_b_ci"][0] <= 1 <= row["bF_b_ci"][1]
        o3 = r["O3"]
        row["O3"] = {k: o3[k] for k in ("gamma", "km10", "km30", "km100", "km300", "p90") if k in o3}
        row["O3_n_completed"] = o3.get("n_completed")
        if "O3pp" in r:
            row["O3pp"] = {k: r["O3pp"][k] for k in ("gamma", "km10", "km30", "km100", "km300")}
        row["O2"] = {k: r["O2"][k] for k in ("G_A", "G_A_ci", "G_F", "G_F_ci", "eps_F", "eps_F_ci")} if "O2" in r else None
        row["O4"] = r["O4"]
        row["variants"] = r["O1_variants"]
        row["O5"] = r["O5"]
        S["per_unit"][u] = row
        bF.append(row["bF_b"]); bFse.append(ci_se(row["bF_b_ci"]))
        bd.append(row["bd_b"]); bdse.append(ci_se(row["bd_b_ci"]))
    pu = S["per_unit"]
    k = len(units)
    S["P1"] = {"n_pass": sum(pu[u]["P1"] for u in units), "k": k}
    S["P1"]["holds"] = S["P1"]["n_pass"] >= 2 * k / 3
    m, se, tau2, kk = re_mean(bF, bFse)
    S["P2"] = {"n_pass": sum(pu[u]["P2"] for u in units), "k": k, "re_mean": m, "re_ci": [m - Z * se, m + Z * se],
               "tau2": tau2}
    S["P2"]["holds"] = S["P2"]["n_pass"] >= k / 2 and S["P2"]["re_ci"][0] <= 1 <= S["P2"]["re_ci"][1]
    m, se, tau2, _ = re_mean(bd, bdse)
    S["beta_d_all"] = {"re_mean": m, "re_ci": [m - Z * se, m + Z * se], "tau2": tau2}
    g51 = [u for u in units if u.startswith("51")]
    m, se, tau2, _ = re_mean([pu[u]["bd_b"] for u in g51], [ci_se(pu[u]["bd_b_ci"]) for u in g51])
    S["P5"] = {"re_mean": m, "re_ci": [m - Z * se, m + Z * se], "holds": m + Z * se < 0,
               "n_neg": sum(pu[u]["bd_b_ci"][1] < 0 for u in g51), "k": len(g51)}
    m, se, tau2, _ = re_mean([pu[u]["bF_b"] for u in g51], [ci_se(pu[u]["bF_b_ci"]) for u in g51])
    S["beta_F_G51"] = {"re_mean": m, "re_ci": [m - Z * se, m + Z * se], "tau2": tau2}
    # P3 (eps over G51)
    band = max(syn[u]["eps_band_97_5"] for u in ("51c", "51h") if u in syn and "eps_band_97_5" in syn[u])
    E = eps_pooled([R[u] for u in g51 if R[u].get("O2")])
    S["P3"] = {**E, "band": band, "readable": E["G_A_ci"][0] > 0, "above_band": E["eps_F_ci"][0] > band}
    # P4 (O3), primary design per amendment (see card) chosen in O3_PRIMARY
    prim = json.loads((L.OUT / "synthetic" / "o3_choice.json").read_text())["primary"] if \
        (L.OUT / "synthetic" / "o3_choice.json").exists() else "O3"
    key = "O3pp" if prim == "pp" else "O3"
    ins = {u: pu[u].get(key) for u in units}
    def inside(u, s):
        v = ins[u].get(s, {}).get("inside") if ins[u] else None
        return v
    S["P4"] = {"design": key,
               "gamma_inside": sum(inside(u, "gamma") is True for u in units),
               "km100_inside": sum(inside(u, "km100") is True for u in units),
               "km300_inside": sum(inside(u, "km300") is True for u in units),
               "km100_scored": sum(inside(u, "km100") is not None for u in units),
               "km300_scored": sum(inside(u, "km300") is not None for u in units), "k": k}
    allin = [u for u in units if inside(u, "gamma") is True and inside(u, "km100") in (True, None)
             and inside(u, "km300") in (True, None)]
    S["P4"]["n_all_inside"] = len(allin)
    S["P4"]["holds"] = len(allin) >= k / 2
    killA = [u for u in units if inside(u, "gamma") is False or inside(u, "km100") is False]
    S["killA"] = {"n_out": len(killA), "k": k, "fires": len(killA) >= k / 2}
    # N1 / Kill C
    def pool(us, key):
        lor = np.array([pu[u]["O4"][key]["lor"] if key else pu[u]["O4"]["lor"] for u in us], float)
        se = np.array([pu[u]["O4"][key]["se"] if key else pu[u]["O4"]["se"] for u in us], float)
        ok = np.isfinite(lor) & np.isfinite(se) & (se > 0)
        w = 1 / se[ok] ** 2
        m = float(np.sum(w * lor[ok]) / w.sum()); s = float(np.sqrt(1 / w.sum()))
        return m, s
    for per, us in (("G51", g51), ("G38", [u for u in units if u.startswith("38")])):
        m, s = pool(us, None)
        nt = np.array([pu[u]["O4"]["n_treated"] for u in us], float)
        pr = np.array([pu[u]["O4"]["pred"] if pu[u]["O4"]["pred"] is not None else np.nan for u in us], float)
        pred = float(np.nansum(pr * nt) / nt[np.isfinite(pr)].sum())
        pm, ps = pool(us, "placebo")
        S[f"N1_{per}"] = {"lor": m, "ci": [m - Z * s, m + Z * s], "pred": pred, "ratio": m / pred if pred else None,
                          "n_treated": int(nt.sum()), "placebo": pm, "placebo_ci": [pm - Z * ps, pm + Z * ps]}
    n1 = S["N1_G51"]
    n1["holds"] = n1["ci"][0] > 0 and n1["ratio"] is not None and 0.5 <= n1["ratio"] <= 2 and \
        n1["placebo_ci"][0] <= 0 <= n1["placebo_ci"][1]
    # N2
    mo, so, _, _ = re_mean([pu[u]["bF_b"] for u in OWN if u in pu], [ci_se(pu[u]["bF_b_ci"]) for u in OWN if u in pu])
    ms, ss, _, _ = re_mean([pu[u]["bF_b"] for u in SHARED if u in pu], [ci_se(pu[u]["bF_b_ci"]) for u in SHARED if u in pu])
    dd, ds = mo - ms, float(np.hypot(so, ss))
    S["N2"] = {"own": [mo, mo - Z * so, mo + Z * so], "shared": [ms, ms - Z * ss, ms + Z * ss],
               "diff": [dd, dd - Z * ds, dd + Z * ds]}
    S["N2"]["holds"] = abs(dd) < 0.3 and S["N2"]["diff"][1] <= 0 <= S["N2"]["diff"][2]
    # N3
    S["N3"] = {u: {"gamma_obs": pu[u]["O3"]["gamma"]["obs"], "gamma_sim": pu[u]["O3"]["gamma"]["sim_med"],
                   "band": pu[u]["O3"]["gamma"]["band"]} for u in units if u.startswith("38")}
    L.jdump(S, L.OUT / "results" / "summary.json")
    print(json.dumps({k: v for k, v in S.items() if k != "per_unit"}, indent=1, default=str))
    for u in units:
        r = pu[u]
        print(f"{u:4s} bF_b {r['bF_b']:+.2f} [{r['bF_b_ci'][0]:+.2f},{r['bF_b_ci'][1]:+.2f}] bF_a {r['bF_a']:+.2f} "
              f"bd {r['bd_b']:+.2f} [{r['bd_b_ci'][0]:+.2f},{r['bd_b_ci'][1]:+.2f}] "
              f"gamma obs {r['O3']['gamma']['obs']:+.2f} sim {r['O3']['gamma']['sim_med']:+.2f} "
              f"{'pp ' + format(r['O3pp']['gamma']['sim_med'], '+.2f') if 'O3pp' in r else ''} "
              f"O4 {r['O4']['lor']}±{r['O4']['se']} pred {r['O4']['pred']} "
              f"GA {r['O2']['G_A'] if r['O2'] else None}")
    if a.write_estimates:
        write_est(S, R)


def write_est(S, R):
    import estimates as E
    rows = []
    src = "data/processed/H134-polya-urn-project-stickiness/results/summary.json"
    for u, r in S["per_unit"].items():
        g = int(u[:2])
        base = {"period_unit": u, "goal_no": g, "channel": "project_call", "role": "replication", "source": src,
                "ci_level": 0.95, "n_kind": "risk calls", "n": float(r["n_rows"])}
        rows.append({**base, "statistic": "h134_beta_urn", "estimate": r["bF_b"], "ci_lo": r["bF_b_ci"][0],
                     "ci_hi": r["bF_b_ci"][1], "ci_kind": "percentile", "method": "agent-FE logit B+F+lnd+K, agent-day block bootstrap 200",
                     "null": "beta_F = 0 (urn predicts 1)"})
        rows.append({**base, "statistic": "h134_beta_dwell", "estimate": r["bd_b"], "ci_lo": r["bd_b_ci"][0],
                     "ci_hi": r["bd_b_ci"][1], "ci_kind": "percentile", "method": "agent-FE logit B+F+lnd+K, agent-day block bootstrap 200",
                     "null": "beta_d = 0"})
        if r["O2"] and r["O2"]["eps_F_ci"][0] is not None:
            rows.append({**base, "statistic": "h134_eps_selfshare", "estimate": r["O2"]["eps_F"], "ci_lo": r["O2"]["eps_F_ci"][0],
                         "ci_hi": r["O2"]["eps_F_ci"][1], "ci_kind": "percentile", "method": "day-blocked CV, day bootstrap 1000",
                         "null": "proxy band (synthetic W2-W4)", "notes": f"G_A {r['O2']['G_A']:.2f} nats/1000 calls"})
        key = "O3pp" if S["P4"]["design"] == "O3pp" else "O3"
        gm = r[key]["gamma"]
        rows.append({**base, "statistic": "h134_tail_calibration", "estimate": gm["obs"] - gm["sim_med"],
                     "ci_lo": gm["obs"] - gm["band"][1], "ci_hi": gm["obs"] - gm["band"][0], "ci_kind": "parametric",
                     "method": f"observed dwell slope gamma minus simulated ({key}), 95% simulation band",
                     "null": "0 (the per-call rule reproduces the dwell slope)"})
        o4 = r["O4"]
        if o4["se"] is not None and o4["lor"] is not None and np.isfinite(o4["se"]):
            rows.append({**base, "statistic": "h134_reset_step", "estimate": o4["lor"], "se": o4["se"],
                         "ci_lo": o4["lor"] - Z * o4["se"], "ci_hi": o4["lor"] + Z * o4["se"], "ci_kind": "se_z",
                         "method": "MH log OR leave at first call after forced reset vs matched calls (agent x dwell decile x f decile)",
                         "null": "0 (R-store)", "n": float(o4["n_treated"]), "n_kind": "forced resets in visits d>=10",
                         "role": "native"})
    for per, g in (("G51", 51), ("G38", 38)):
        n1 = S[f"N1_{per}"]
        rows.append({"period_unit": per, "goal_no": g, "channel": "project_call", "role": "native", "source": src,
                     "statistic": "h134_reset_step_pooled", "estimate": n1["lor"], "ci_lo": n1["ci"][0], "ci_hi": n1["ci"][1],
                     "ci_kind": "se_z", "ci_level": 0.95, "n": float(n1["n_treated"]), "n_kind": "forced resets in visits d>=10",
                     "method": "inverse-variance mean of unit MH log ORs", "null": "0 (R-store)",
                     "notes": f"urn prediction {n1['pred']:.3f}; placebo {n1['placebo']:.3f} [{n1['placebo_ci'][0]:.3f}, {n1['placebo_ci'][1]:.3f}]"})
    p3 = S["P3"]
    rows.append({"period_unit": "G51", "goal_no": 51, "channel": "project_call", "role": "replication", "source": src,
                 "statistic": "h134_eps_selfshare_pooled", "estimate": p3["eps_F"], "ci_lo": p3["eps_F_ci"][0],
                 "ci_hi": p3["eps_F_ci"][1], "ci_kind": "percentile", "ci_level": 0.95, "n": float(p3["n_days"]),
                 "n_kind": "unit-days", "method": "day-blocked CV per unit, per-day LL summed over G51 units, day bootstrap",
                 "null": f"proxy band {p3['band']:.3f}"})
    E.write_estimates(rows, hypothesis="H134")
    print("estimates rows", len(rows))


if __name__ == "__main__":
    main()
