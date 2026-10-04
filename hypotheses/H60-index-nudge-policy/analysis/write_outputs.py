"""H60: period folders (G51, G38 replication; G37/G41/G44 descriptive; NE43, NE44 natives) and estimate rows.
Reads results.json files only.
Usage: uv run python hypotheses/H60-index-nudge-policy/analysis/write_outputs.py [--no-estimates]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H60-index-nudge-policy"
GP = HYP / "goalperiod-subhypotheses"
SRC = "data/processed/H60-index-nudge-policy"
OCL = {"calls30": "active calls in 30 min (primary)", "sus": "sustained escape (prob.)", "any": "glance (prob.)"}
f2 = lambda x: f"{x:.2f}"  # noqa: E731
ci = lambda c: f"[{c[0]:.2f}, {c[1]:.2f}]"  # noqa: E731


def period_readme(r, info, prediction_extra=""):
    per = r["period"]
    v = r["calls30"]["verdict"]
    L = [f"# H60 × {per}: index nudge policy ({info['first']} → {info['last']})", "",
         f"**Verdict:** {v}", "**Role:** replication",
         f"**Period:** regime III · {r['agents']} agents · {r['days']} days with the nudger on"
         + (" (07-06 → 08-20; NE43 after)" if per == "G51" else "") + ". Cross-fit halves: interleaved days.", "",
         "## Why this period",
         "Replication layer: the common policy evaluation on every period with ≥ 500 idle gates and ≥ 50 gates that read "
         "a nudge to the agent. Only G51 and G38 qualify.", "",
         "## Prediction", "*Written 2026-10-04, before running (card P1–P8; A1 before real data).*",
         "Supported if V(index)/V(logged) ≥ 2.3 with CI lower bound > 1 and V(index)/V(once-early) > 1 with CI lower "
         "bound > 1 on active calls. " + prediction_extra, "",
         "## Result", f"`analysis/run_period.py`; numbers in `{SRC}/{per}/results.json`. Values are cross-fitted "
         "direct-method means of the predicted nudge effect over the gates each policy picks, at the logged budget; "
         "CIs from day-block bootstrap draws (200 for active calls, 100 for binary outcomes).", ""]
    for oc in ("calls30", "sus", "any"):
        x = r[oc]
        L += [f"**{OCL[oc]}** — {x['n_gates']} gates, {x['n_nudged']} nudged, mean outcome {x['mean_y']:.2f}; "
              f"heterogeneity (θ_a = θ_k = θ_r = 0) p = {x['het']['p']:.3g}; mean effect at nudged gates "
              f"{x['het']['mean_g_nudged']:.2f}; verdict rule: {x['verdict']}.", "",
              "| Policy | value per nudge [95% CI] | ratio to logged [95% CI] |", "| --- | --- | --- |"]
        for p in ("logged", "random", "once_early", "index_ak", "index", "index_once"):
            rr = "1" if p == "logged" else (f"{x['ratios'].get(p + '/logged', x['values'][p] / x['values']['logged']):.2f}"
                                             + (f" {ci(x['ci'][p + '/logged'])}" if p + "/logged" in x["ci"] else ""))
            L.append(f"| {p} | {x['values'][p]:.3f} {ci(x['values_ci'][p])} | {rr} |")
        L += ["", f"index / once-early {x['ratios']['index/once_early']:.2f} {ci(x['ci']['index/once_early'])}; "
              f"index / index(a,k) {x['ratios']['index/index_ak']:.2f} {ci(x['ci']['index/index_ak'])}.", ""]
    L += [f"Verdict (primary outcome): **{v}**.", "", "## Scorecard (period-specific axes)",
          "- C: policy values are cross-fitted on held-out day halves.",
          "- H: rivals R0 (flat), R1 (logged near-optimal), R2 (once-early optimal) are scored by the ratios above; "
          "R3 (selection) is not excluded by this estimator (synthetic S3).", ""]
    return "\n".join(L) + "\n"


def small_readme(r, info):
    return "\n".join([f"# H60 × {r['period']}: index nudge policy ({info['first']} → {info['last']})", "",
                      "**Verdict:** descriptive", "**Role:** replication",
                      f"**Period:** regime III · {r['days']} days · {r['n_gates']} idle gates with a sustained-run clock.", "",
                      "## Why this period", "Regime-III period with nudges, below the eligibility bar (≥ 50 nudged gates).", "",
                      "## Prediction", "*Written 2026-10-04.* Not eligible: counted only.", "",
                      "## Result", f"{r['n_nudged']} gates read a nudge to the agent. No policy value is estimated "
                      "(synthetic: gate-level policy ratios are not identifiable at ≤ 30 nudges, H35).", ""]) + "\n"


def native_readmes(nat):
    n1, n2 = nat["N1_NE43"], nat["N2_NE44"]
    a = n1["calib_ratio_targeted_over_other"]
    t1 = "\n".join([
        "# H60 × NE43: the untreated arm on nudger-free days (2026-08-07 → 08-20 vs 08-21 → 09-02)", "",
        f"**Verdict:** {'supported' if n1['pass_a'] and n1['pass_b'] else ('failed' if not (n1['pass_a'] or n1['pass_b']) else 'mixed')}",
        "**Role:** native",
        f"**Period:** regime III · #51 · {n1['agents']} agents present on both sides · B: {n1['gates_B']} gates "
        f"({n1['nudged_B']} nudged), C: {n1['gates_C']} gates (no nudges). Exception (c).", "",
        "## Why this period",
        "After 08-20 nobody selects agents for nudges, so the untreated outcome model can be checked against gates "
        "with no selection at all. A larger miss in the states the nudger targets (k ≥ 4) than elsewhere is the "
        "selection signature (R3).", "",
        "## Prediction", "*Written 2026-10-04, before running (card N1).*",
        "(a) the calibration ratio (observed / predicted active calls) differs by < 15% between targeted states (k ≥ 4) "
        "and the rest [0.5]; (b) the logged nudges buy ≤ 1% of the window's active calls [0.8].", "",
        "## Result", f"`analysis/native.py`; `{SRC}/native/native.json` (B = 200 day draws on each side).", "",
        "| Quantity | Estimate [95% CI] | Prediction |", "| --- | --- | --- |",
        f"| calibration, targeted (k ≥ 4) | {f2(n1['calib_targeted']['est'])} {ci(n1['calib_targeted']['ci'])} | |",
        f"| calibration, other states | {f2(n1['calib_other']['est'])} {ci(n1['calib_other']['ci'])} | |",
        f"| ratio targeted / other | {f2(a['est'])} {ci(a['ci'])} | (a) {'pass' if n1['pass_a'] else 'fail'} |",
        f"| active calls bought by logged nudges (B) | {n1['calls_bought_B']['est']:.0f} {ci(n1['calls_bought_B']['ci'])} of "
        f"{n1['active_calls_B']} ({100 * n1['share_bought_B']:.2f}%) | (b) {'pass' if n1['pass_b'] else 'fail'} |",
        "", "Both sides share the days' room change and roster growth, so (a) also absorbs a period shift common to all "
        "states; the comparison is between state groups.", ""])
    th_pre, th_51 = n2["pre_06_11"], n2["G51"]
    t2 = "\n".join([
        "# H60 × NE44: the index's shape across the pause-default change (regime III, 2026-03-30 → 05-29 vs #51)", "",
        f"**Verdict:** {'supported' if n2['pass'] else 'failed'}", "**Role:** native",
        f"**Period:** pre = G37–G44 pooled ({th_pre['gates']} gates, {th_pre['nudged']} nudged; agent-within-period fixed "
        "effects); post = G51 (nudger-on days). Exception (c): the transition is the object.", "",
        "## Why this period",
        "Before 06-11 a pause without a duration slept 12 h; after it, 5 min. H35 found the nudge effect rising with trap "
        "age before (G38 +1.18) and falling after (G51 −0.32). If so, the index must be refitted after a scaffold change.", "",
        "## Prediction", "*Written 2026-10-04, before running (card N2).*",
        "θ_k (nudge × ln k, active calls) ≥ 0 before and < 0 after [0.45].", "",
        "## Result", f"`analysis/native.py`; `{SRC}/native/native.json` (B = 200).", "",
        "| Term | pre-06-11 [95% CI] | G51 [95% CI] |", "| --- | --- | --- |",
        *[f"| {k} | {th_pre['theta'][k]:.2f} {ci(th_pre['theta_ci'][k])} | {th_51['theta'][k]:.2f} {ci(th_51['theta_ci'][k])} |"
          for k in ("M", "M_la", "M_lk", "M_lr")],
        "", f"Prediction {'holds' if n2['pass'] else 'fails'}: the k slope is negative on both sides and neither CI excludes 0.", ""])
    return {"NE43": t1, "NE44": t2}


def est_rows(results, infos):
    import estimates as E
    rows = []
    for r in results:
        if "calls30" not in r:
            continue
        g = int(r["period"][1:])
        for oc in ("calls30", "sus", "any"):
            x = r[oc]
            base = {"period_unit": E.map_unit(g), "goal_no": g, "channel": f"N_tgt_gate_{oc}", "role": "replication",
                    "ci_level": 0.95, "ci_kind": "percentile", "n": float(x["n_nudged"]), "n_kind": "events",
                    "unit_local": f"{r['period']} nudger-on days", "first_day": infos[r["period"]]["first"],
                    "last_day": infos[r["period"]]["last"], "status": "ok" if g == 51 else "underpowered",
                    "post_hoc": False, "source": f"{SRC}/{r['period']}/results.json", "null": "ratio = 1",
                    "notes": f"verdict rule: {x['verdict']}"}
            m = "cross-fitted direct method (day halves), agent-FE outcome model, logged budget; day-block bootstrap"
            for num in ("index", "once_early", "index_once", "random"):
                rows.append({**base, "statistic": f"policy_ratio_{num}_over_logged",
                             "estimate": float(x["values"][num] / x["values"]["logged"]),
                             "ci_lo": float(x["ci"][f"{num}/logged"][0]), "ci_hi": float(x["ci"][f"{num}/logged"][1]),
                             "method": m})
            rows.append({**base, "statistic": "nudge_effect_at_gate", "estimate": float(x["het"]["mean_g_nudged"]),
                         "ci_lo": float(x["het"]["theta_ci"]["M"][0]), "ci_hi": float(x["het"]["theta_ci"]["M"][1]),
                         "method": "agent-FE outcome model, effect at the mean nudged state (theta_0); day-block bootstrap",
                         "null": "effect = 0"})
    return rows


def main():
    g = pl.read_parquet(OUT / "gates.parquet").filter(pl.col("nudger_on"))
    infos = {f"G{k:02d}": {"first": a, "last": b} for k, a, b in
             g.group_by("goal_no").agg(pl.col("pt_date").min().alias("a"), pl.col("pt_date").max().alias("b")).iter_rows()}
    results = [json.loads(f.read_text()) for f in sorted(OUT.glob("G*/results.json"))]
    extra = {"G51": "Expected (P1/P2): not met [credences 0.3, 0.35].",
             "G38": "Expected (P8): the index/logged CI includes 1 (long pauses) [0.6]."}
    for r in results:
        d = GP / r["period"]
        (d / "figures").mkdir(parents=True, exist_ok=True)
        txt = period_readme(r, infos[r["period"]], extra.get(r["period"], "")) if "calls30" in r else small_readme(r, infos[r["period"]])
        (d / "README.md").write_text(txt)
    nat = OUT / "native/native.json"
    if nat.exists():
        for k, t in native_readmes(json.loads(nat.read_text())).items():
            (GP / k / "figures").mkdir(parents=True, exist_ok=True)
            (GP / k / "README.md").write_text(t + "\n")
    if "--no-estimates" not in sys.argv:
        import estimates as E
        print("rows", E.write_estimates(est_rows(results, infos), hypothesis="H60").height)


if __name__ == "__main__":
    main()
