"""H20 cross-period summary: per-period verdicts (card rule + Amendment 1), random-effects summaries, P7,
card-level verdict. Writes data/processed/H20-content-aging/summary.json and prints the card tables.

Usage: uv run python hypotheses/H20-content-aging/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20lib as L  # noqa: E402
from h20lib import hc  # noqa: E402

import numpy as np  # noqa: E402


def ok(x):
    return x is not None and np.isfinite(x)


def period_verdict(g, r):
    s = r["raw"]["stats"]
    gs = r["g"]["stats"]
    A, Ac = s["A"], s["A_c"]
    f = r.get("fits", {})
    pw = r["power"]
    v = {}
    # P1 kickoff transient
    v["P1"] = "✓" if ok(s["K"]["obs"]) and s["K"]["obs"] > 0 else "✗"
    # P2 (Amendment 1: co-primary A or A_c at p < 0.025; original A at p < 0.05 reported)
    pA, pAc = A["p_upper"], Ac["p_upper"]
    route = None
    if ok(A["obs"]) and A["obs"] > 0 and pA < 0.025:
        route = "A"
    elif ok(Ac["obs"]) and Ac["obs"] > 0 and pAc < 0.025:
        route = "A_c"
    v["P2_original"] = bool(ok(A["obs"]) and A["obs"] > 0 and pA < 0.05)
    v["P2_route"] = route
    v["P2"] = "✓" if route else "✗"
    # P3 field removed (on the route's statistic)
    if route == "A":
        p3 = gs["A"]["obs"] > 0 and gs["A"]["p_upper"] < 0.10
    elif route == "A_c":
        p3 = gs["A_c"]["obs"] > 0 and gs["A_c"]["p_upper"] < 0.10
    else:
        p3 = None
    v["P3"] = "–" if p3 is None else ("✓" if p3 else "✗")
    # P4 (Amendment 1): mu CI > 0 and A_late > 0; CV reported
    if f:
        p4 = (f["mu_ci90"][0] > 0) and ok(s["A_late"]["obs"]) and s["A_late"]["obs"] > 0
        cvw = min(f["cv"], key=f["cv"].get)
        v["cv_M1_beats_M0_MQ"] = bool(f["cv"]["M1"] < min(f["cv"]["M0"], f["cv"]["MQ"]))
    else:
        p4, cvw = None, None
    v["P4"] = "–" if (p4 is None or route is None) else ("✓" if p4 else "✗")
    v["P4_any"] = p4
    v["cv_winner"] = cvw
    chat_A = r["robust"].get("chat", {}).get("stats", {}).get("A", {}).get("obs")
    med = r["agents"]["median"]
    v["consistency"] = bool(ok(chat_A) and chat_A > 0 and ok(med) and med > 0)
    role = hc.role(g)
    # labels
    if role == "short":
        verdict = "descriptive"
        cause = "stationary contrast"
    else:
        supported = route is not None and p3 and bool(p4) and v["consistency"]
        acc = ok(A["obs"]) and A["p_lower"] < 0.05 and A["obs"] < 0
        not_sig = (pA >= 0.05) and (pAc >= 0.05)
        rej_alt = (ok(pw.get("A_p_alt|mu=0.5")) and pw["A_p_alt|mu=0.5"] < 0.05
                   and ok(pw.get("A_c_p_alt|mu=0.5")) and pw["A_c_p_alt|mu=0.5"] < 0.05)
        powered = pw.get("coprimary|mu=0.5", 0) >= 0.8
        if supported:
            verdict, cause = "supported", "aging"
        elif acc:
            verdict, cause = "failed", "dynamics speed up with age, A < 0"
        elif not_sig and (rej_alt or powered):
            verdict, cause = "failed", "stationary within power: μ = 0.5 aging rejected" if rej_alt else "stationary, power ≥ 0.8"
        else:
            if route is None:
                cause = "underpowered: not significant, μ = 0.5 aging not rejected"
            elif not p3:
                cause = "field drift: A_g not significant"
            elif not p4:
                cause = "interrupted aging: no late slowing"
            elif not v["consistency"]:
                cause = "not robust: chat-only or per-agent median ≤ 0"
            else:
                cause = "other"
            verdict = "mixed"
    v["verdict_word"] = verdict
    v["cause"] = cause
    v["verdict"] = f"{verdict} ({cause})"
    return v


def scorecard_line(g, r, v):
    role = hc.role(g)
    if role == "short":
        return ("C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.")
    s = r["raw"]["stats"]
    c = "2" if v["verdict_word"] == "supported" else "1" if v["P2"] == "✓" else "0"
    return (f"C (beats the stationary null): {c} — A p = {s['A']['p_upper']:.3f}, A_c p = {s['A_c']['p_upper']:.3f}. "
            f"D (unfitted signature: A_late, μ̂ > 0): {'1' if v.get('P4_any') else '0'}. "
            f"H (rivals R1 quench, R2 field, R3 common): {'1' if v['P2'] == '✓' and v['P3'] == '✓' else '0'}. "
            f"G: –.")


def build(kind):
    fn = "result.json" if kind == "iso" else "result_aniso.json"
    res = {}
    for g in hc.ALL_PERIODS:
        f = hc.OUT / f"G{g:02d}/{fn}"
        if f.exists():
            res[g] = json.loads(f.read_text())
    verdicts, rows = {}, []
    for g, r in res.items():
        v = period_verdict(g, r)
        v["scorecard"] = scorecard_line(g, r, v)
        s = r["raw"]["stats"]
        v["summary_line"] = (f"A = {s['A']['obs']:+.3f} (p = {s['A']['p_upper']:.3f}), "
                             f"A_c = {s['A_c']['obs']:+.3f} (p = {s['A_c']['p_upper']:.3f}), A_g = {r['g']['stats']['A']['obs']:+.3f} "
                             f"(p = {r['g']['stats']['A']['p_upper']:.3f}), A_late = {s['A_late']['obs']:+.3f}, K = {s['K']['obs']:+.3f}; "
                             f"co-primary design power vs μ = 0.5: {r['power'].get('coprimary|mu=0.5', float('nan')):.2f}")
        verdicts[str(g)] = v
        f_ = r.get("fits", {})
        rows.append(dict(g=g, role=hc.role(g), regime=r["regime"], T=r["T"], N=r["n_agents"], A=s["A"]["obs"], pA=s["A"]["p_upper"],
                         pA_low=s["A"]["p_lower"], seA=s["A"]["null_sd"], zA=(s["A"]["obs"] - s["A"]["null_mean"]) / s["A"]["null_sd"],
                         Ac=s["A_c"]["obs"], pAc=s["A_c"]["p_upper"], seAc=s["A_c"]["null_sd"],
                         Ag=r["g"]["stats"]["A"]["obs"], pAg=r["g"]["stats"]["A"]["p_upper"], Am=s["A_m"]["obs"], K=s["K"]["obs"],
                         pK=s["K"]["p_upper"], seK=s["K"]["null_sd"], Ae=s["A_early"]["obs"], seAe=s["A_early"]["null_sd"],
                         Al=s["A_late"]["obs"], pAl=s["A_late"]["p_upper"],
                         mu=f_.get("mu_hat"), mu_ci=f_.get("mu_ci90"), cvw=v["cv_winner"], pow05=r["power"].get("coprimary|mu=0.5"),
                         powA=r["power"].get("A|mu=0.5"), bwk=s["bwk"]["obs"], q=r["raw"]["null_model"]["q"],
                         r_=sum(r["raw"]["null_model"]["r"]), tau=r["raw"]["null_model"]["tau"][0], meanS=r["mean_S"],
                         neff_s=r["raw"]["null_model"].get("neff_s"), neff_p=r["raw"]["null_model"].get("neff_p"),
                         mem=(r.get("memory") or {}).get("slope"), mem_se=(r.get("memory") or {}).get("se"),
                         verdict=v["verdict_word"], cause=v["cause"]))
    lm = [x for x in rows if x["role"] in ("long", "medium")]
    lo = [x for x in rows if x["role"] == "long"]
    sh = [x for x in rows if x["role"] == "short"]
    summ = dict(verdicts=verdicts, rows=rows, null_kind=kind)
    summ["RE_A_long_medium"] = L.dersimonian_laird([x["A"] for x in lm], [x["seA"] for x in lm])
    summ["RE_Ac_long_medium"] = L.dersimonian_laird([x["Ac"] for x in lm], [x["seAc"] for x in lm])
    summ["RE_A_long"] = L.dersimonian_laird([x["A"] for x in lo], [x["seA"] for x in lo])
    summ["RE_A_short"] = L.dersimonian_laird([x["A"] for x in sh], [x["seA"] for x in sh])
    summ["RE_K_all"] = L.dersimonian_laird([x["K"] for x in rows], [x["seK"] for x in rows])
    summ["RE_Alate_long_medium"] = L.dersimonian_laird([x["Al"] for x in lm], [res[x["g"]]["raw"]["stats"]["A_late"]["null_sd"] for x in lm])
    mus = [(x["mu"], (x["mu_ci"][1] - x["mu_ci"][0]) / 3.29) for x in lm if x["mu"] is not None and x["mu_ci"]]
    summ["RE_mu_long_medium"] = L.dersimonian_laird([m for m, _ in mus], [s_ for _, s_ in mus])
    re_s = L.dersimonian_laird([x["Ae"] for x in sh], [x["seAe"] for x in sh])
    re_l = L.dersimonian_laird([x["Ae"] for x in lm], [x["seAe"] for x in lm])
    diff = re_l["mean"] - re_s["mean"]
    sed = float(np.hypot(re_l["se"], re_s["se"]))
    summ["P7"] = dict(short_re=re_s, long_medium_re=re_l, diff=diff, se=sed, ci90=[diff - 1.645 * sed, diff + 1.645 * sed],
                      holds=bool(abs(diff) <= 1.645 * sed))
    for reg in ("I", "III"):
        sub = [x for x in lm if x["regime"] == reg]
        summ[f"RE_A_regime_{reg}"] = L.dersimonian_laird([x["A"] for x in sub], [x["seA"] for x in sub])
    z = np.array([x["zA"] for x in rows if np.isfinite(x["zA"])])
    summ["calibration"] = dict(z_median=float(np.median(z)), z_sd=float(z.std()),
                               z_robust_sd=float(1.4826 * np.median(np.abs(z - np.median(z)))),
                               frac_abs_z_gt2=float(np.mean(np.abs(z) > 2)), n=int(z.size))
    lv = [verdicts[str(g)]["verdict_word"] for g in hc.LONG if str(g) in verdicts]
    n_sup, n_fail = lv.count("supported"), lv.count("failed")
    re = summ["RE_A_long_medium"]
    if n_sup >= 2 and n_fail == 0 and re["mean"] > 0 and re["p"] / 2 < 0.05:
        card = "supported"
    elif n_fail >= 3 or re["mean"] <= 0:
        card = "failed"
    else:
        card = "mixed"
    summ["card_verdict"] = card
    summ["long_verdicts"] = {str(g): verdicts[str(g)]["verdict"] for g in hc.LONG if str(g) in verdicts}
    return summ


def main():
    out = {}
    for kind in ("iso", "aniso"):
        s = build(kind)
        if not s["rows"]:
            continue
        out[kind] = s
        print(f"\n===== null: {kind} =====")
        print("| Period | Role | Verdict | Key numbers |")
        print("| --- | --- | --- | --- |")
        for x in s["rows"]:
            mu = f"μ̂ {x['mu']:+.2f} [{x['mu_ci'][0]:+.2f}, {x['mu_ci'][1]:+.2f}]; " if x["mu"] is not None else ""
            print(f"| G{x['g']:02d} | {x['role']} | {x['verdict']} ({x['cause']}) | A {x['A']:+.3f} (p {x['pA']:.3f}, z {x['zA']:+.1f}); "
                  f"A_c {x['Ac']:+.3f} (p {x['pAc']:.3f}); A_g {x['Ag']:+.3f} (p {x['pAg']:.3f}); A_late {x['Al']:+.3f} (p {x['pAl']:.3f}); "
                  f"K {x['K']:+.3f}; {mu}power {x['pow05']:.2f}; neff {x['neff_s']}/{x['neff_p']} |")
        for k in ("RE_A_long_medium", "RE_Ac_long_medium", "RE_Alate_long_medium", "RE_A_long", "RE_A_short", "RE_K_all",
                  "RE_mu_long_medium", "RE_A_regime_I", "RE_A_regime_III", "calibration"):
            print(k, {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in s[k].items()})
        print("P7", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s["P7"].items() if k not in ("short_re", "long_medium_re")},
              "short", round(s["P7"]["short_re"]["mean"], 4), "long+medium", round(s["P7"]["long_medium_re"]["mean"], 4))
        print("card verdict:", s["card_verdict"], s["long_verdicts"])
    # headline = Amendment 2 (calibrated) when available; the pre-registered result is kept alongside
    head = out.get("aniso", out["iso"])
    summ = dict(head)
    summ["preregistered_iso"] = out["iso"]
    hc.write_provenance({"verdict_rules": "card + Amendment 1; headline null = Amendment 2 (estimated latent shapes)"},
                        ["H20/G*/result.json", "H20/G*/result_aniso.json"], "hypotheses/H20-content-aging/analysis/summarize.py")
    summ["example_period"] = 38
    re, cal, cali = summ["RE_A_long_medium"], summ["calibration"], out["iso"]["calibration"]
    summ["headline"] = (f"No aging. Card verdict {summ['card_verdict']} (Amendment-2 null; pre-registered null: {out['iso']['card_verdict']}). "
                        f"Random-effects aging slope over 10 long + medium goals: {re['mean']:+.3f} ± {re['se']:.3f} (I² = {re['I2']:.2f}).")
    summ["summary_lines"] = [
        "Observable: two-time correlation C(t_w + τ, t_w) of each agent's whitened day state, t_w in active days since the goal's kickoff;",
        "aging slope A = ∂C/∂log t_w at fixed lag (t_w ≥ 2), tested against a fitted stationary swarm model (parametric bootstrap).",
        f"Synthetic (village sampling): size 0.03–0.07; power 0.33–0.44 vs μ = 0.5 aging, 0.65–0.88 vs μ = 1 (long goals).",
        f"Real data: the isotropic null was anti-conservative (robust z-SD {cali['z_robust_sd']:.2f}); content fluctuates in ~5–12 dimensions, not 32.",
        f"Amendment 2 (estimated latent shapes) restores calibration (robust z-SD {cal['z_robust_sd']:.2f}).",
        "#38: strong positive A, but front-loaded: lag-1 C rises 0.66 → 0.87 over 4 days, then flat (kickoff relaxation, not aging).",
        "#51: μ = 0.5 aging rejected; a weak late slowing (μ̂ 0.22) in the intention stream only. #4, #8: nothing.",
        "Short goals: holiday days (Thanksgiving, Christmas) and phased weeks dominate; no age effect. Holdout not run.",
    ]
    (hc.OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=float))


if __name__ == "__main__":
    main()
