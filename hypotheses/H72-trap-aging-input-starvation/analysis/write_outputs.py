"""H72: write the period folders (goalperiod-subhypotheses/G<NN>/README.md, NE43, G27, G51g natives) and the
per-period estimate rows (infra/shared/estimates.write_estimates). Reads results.json files only.
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/analysis/write_outputs.py [--no-estimates]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

HYP = Path(__file__).resolve().parents[1]
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H72-trap-aging-input-starvation"
GP = HYP / "goalperiod-subhypotheses"
SRC = "data/processed/H72-trap-aging-input-starvation"

f2 = lambda x: f"{x:+.2f}"  # noqa: E731
ci = lambda c: f"[{c[0]:+.2f}, {c[1]:+.2f}]"  # noqa: E731


def short_verdict(v):
    for k in ("supported", "failed", "mixed", "descriptive"):
        if v.startswith(k):
            return k
    return "n/a"


def period_readme(r, info):
    p = r["primary"]
    per = r["period"]
    v = p["verdict"]
    lines = [f"# H72 × {per}: trap aging vs input starvation ({info['first']} → {info['last']})", "",
             f"**Verdict:** {short_verdict(v)}", "**Role:** replication",
             f"**Period:** regime {r['regime']} · {r['agents']} agents with gates · {r['days']} non-holdout days · "
             f"{r['gates']} idle gates. No split: the hazard has agent fixed effects and day-block CIs.", "",
             "## Why this period",
             "Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). "
             "Nothing period-specific is claimed here.", "",
             "## Prediction",
             "*Written 2026-10-04, before running on this period. Templated (card, \"Per-period verdict rule\", "
             "amended A1 before real data).*",
             "If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel "
             "read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; "
             "in regime I, s barely varies.", "",
             "## Result",
             f"Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in "
             f"`{SRC}/{per}/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).", ""]
    if "beta_a0" not in p:
        lines += [f"Underpowered: {p['n_escape']} escapes in {p['n']} gates (< 30 events of one kind).", "",
                  f"Verdict: **{v}**."]
        return "\n".join(lines) + "\n"
    lines += ["| Quantity | Estimate [95% CI] |", "| --- | --- |",
              f"| gates / sustained escapes | {p['n']} / {p['n_escape']} ({p['escape_rate']:.2f}) |",
              f"| median a, s (min) | {p['median_a_min']:.1f}, {p['median_s_min']:.1f} |",
              f"| β_a0 (age only) | {f2(p['beta_a0'])} {ci(p['ci_a0'])} |",
              f"| β_a (age, s controlled) | {f2(p['beta_a'])} {ci(p['ci_a'])} |",
              f"| β_s (starvation, a controlled) | {f2(p['beta_s'])} {ci(p['ci_s'])} |",
              f"| ρ aging absorbed | {p['rho']:+.2f} {ci(p['ci_rho'])} |",
              f"| starvation-implied aging b_impl (O3b) | {f2(p['b_impl'])} {ci(p['ci_b_impl'])} |",
              f"| CV gain, s adds / a adds (nats per 1,000 gates) | {p['cv_per_1000']['s_adds']:+.1f} / "
              f"{p['cv_per_1000']['a_adds']:+.1f} |"]
    for k, x in r["variants"].items():
        lines.append(f"| variant s_{k}: β_a, β_s | {f2(x['beta_a'])} {ci(x['ci_a'])}, {f2(x['beta_s'])} {ci(x['ci_s'])} |")
    if "any" in r:
        x = r["any"]
        lines.append(f"| any escape (a_any): β_a0, β_a, β_s | {f2(x['beta_a0'])}, {f2(x['beta_a'])} {ci(x['ci_a'])}, "
                     f"{f2(x['beta_s'])} {ci(x['ci_s'])} |")
    if "placebo_v2" in r and "beta_inflight" in r["placebo_v2"]:
        x = r["placebo_v2"]
        lines.append(f"| in-flight placebo (A2 window), Wald | {f2(x['beta_inflight'])} {ci(x['ci_inflight'])} |")
    rob = r.get("robust", {})
    if rob:
        lines.append("| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | " + "; ".join(
            f"{k}: {f2(x['beta_a'])} / {f2(x['beta_s'])}" for k, x in rob.items()) + " |")
    lines += ["", f"Verdict: **{v}**.", "",
              "## Scorecard (period-specific axes)",
              f"- C: the two-clock model is scored on held-out days (5 day folds); a adds {p['cv_per_1000']['a_adds']:+.1f} "
              f"nats per 1,000 gates, s adds {p['cv_per_1000']['s_adds']:+.1f}.",
              "- H: the starvation clock is the rival here; see the verdict.", ""]
    return "\n".join(lines) + "\n"


def native_readmes(nat):
    out = {}
    n1 = nat["N1_NE43"]
    d = n1["design"]
    out["NE43"] = "\n".join([
        "# H72 × NE43: the nudger stops inside #51 (2026-08-07 → 08-20 vs 08-21 → 09-02)", "",
        "**Verdict:** descriptive",
        "**Role:** native",
        f"**Prediction outcome (dated, written against H72):** {'held' if all(n1['verdict'].values()) else ('failed' if not any(n1['verdict'].values()) else 'mixed')}. "
        "The verdict line scores H72's claim: the stop did not lengthen the directed clock, so it does not manipulate "
        "starvation and cannot test H72 (descriptive).",
        "**Period:** regime III · #51 (G51) · B = 08-07 → 08-20 (nudges on, bookends gone), C = 08-21 → 09-02 (no nudges). "
        "Exception (c): the transition is the object.", "",
        "## Why this period",
        "The nudger is the only source of directed input that switches off at a known date. If trap aging were input "
        "starvation, losing the nudges would lengthen the starvation clock and lower escape at fixed trap age.", "",
        "## Prediction", "*Written 2026-10-04, before running (card, N1).*",
        "(a) median s_dir up ≥ 20% after the stop [0.7]; (b) β_a and β_s differ by < 0.3 with CIs including 0 [0.6]; "
        "(c) a C indicator in the pooled model has a CI including 0 [0.55].", "",
        "## Result", f"`analysis/native.py`; numbers in `{SRC}/native/native.json` (B = 200 day-block draws per side).", "",
        "| Quantity | B (nudges on) | C (nudger off) | C − B [95% CI] | Prediction |", "| --- | --- | --- | --- | --- |",
        f"| gates | {d['B']['gates']} | {d['C']['gates']} | | |",
        f"| median s_dir (min) | {d['B']['median_s_dir_min']:.1f} | {d['C']['median_s_dir_min']:.1f} | ×{d['s_dir_ratio_C_over_B']:.2f} | "
        f"(a) {'pass' if n1['verdict']['a_design_sdir_up_20pct'] else 'fail'} |",
        f"| β_a | {f2(n1['fits']['B']['beta_a'])} {ci(n1['fits']['B']['ci_a'])} | {f2(n1['fits']['C']['beta_a'])} {ci(n1['fits']['C']['ci_a'])} | "
        f"{f2(n1['delta_beta_a']['est'])} {ci(n1['delta_beta_a']['ci'])} | (b) |",
        f"| β_s | {f2(n1['fits']['B']['beta_s'])} {ci(n1['fits']['B']['ci_s'])} | {f2(n1['fits']['C']['beta_s'])} {ci(n1['fits']['C']['ci_s'])} | "
        f"{f2(n1['delta_beta_s']['est'])} {ci(n1['delta_beta_s']['ci'])} | (b) {'pass' if n1['verdict']['b_invariance'] else 'fail'} |",
        f"| C indicator (pooled, agent FE) | | | {f2(n1['C_indicator']['est'])} {ci(n1['C_indicator']['ci'])} | "
        f"(c) {'pass' if n1['verdict']['c_indicator_ci_includes_0'] else 'fail'} |", ""])
    n2 = nat["N2_blocked"]
    rows = []
    for per, x in n2.items():
        rows.append(f"| {per} | {x['spells']} / {x['windows']} / {x['leaves']} | {f2(x['beta_age0'])} {ci(x['ci_age0'])} | "
                    f"{f2(x['beta_age'])} {ci(x['ci_age'])} | {f2(x['beta_s'])} {ci(x['ci_s'])} | {x['rho']:+.2f} | "
                    f"{'pass' if x['pass'] else 'fail'} |")
    vv = [x["pass"] for x in n2.values()]
    out["G27"] = "\n".join([
        "# H72 × G27: blocked spells (Jev v3.1 `p_blocked`), with G51 as the powered companion (2026-01-12 → 01-23)", "",
        f"**Verdict:** {'failed' if all(vv) else ('mixed' if any(vv) else 'supported')}",
        "**Role:** native",
        f"**Prediction outcome (dated, written against H72):** {'held' if all(vv) else ('failed' if not any(vv) else 'mixed')}. "
        "The verdict line scores H72's claim (blocked-spell aging is starvation).",
        "**Period:** regime I · #27 (10 days of long debugging traps); G51 non-holdout days as the second, powered arm. "
        "Unit: 5-min Jev windows inside blocked spells (`p_blocked` ≥ 0.5 runs; H16 TS5).", "",
        "## Why this period",
        "HH260 names Jev blocked spells as the check. #27 is the long-debugging period where blocked spells aged most "
        "(H16 round 1b β −1.24). A blocked agent is busy, so the test asks whether directed input, not idleness, "
        "sets its escape.", "",
        "## Prediction", "*Written 2026-10-04, before running (card, N2).*",
        "Blocked-spell aging survives the directed-starvation control (ρ < 0.3) in both periods, and β_s's CI "
        "includes 0 [0.65].", "",
        "## Result", f"`analysis/native.py`; numbers in `{SRC}/native/native.json` (logit, agent FE, B = 200).", "",
        "| Period | spells / windows / leaves | β_age0 | β_age (s controlled) | β_s (s_dir) | ρ | prediction |",
        "| --- | --- | --- | --- | --- | --- | --- |", *rows, ""])
    n3 = nat["N3_focus"]
    out["G51g"] = "\n".join([
        "# H72 × G51g: the #focus room as an input-poor room (2026-08-05 → 08-24)", "",
        f"**Verdict:** {'failed' if n3['pass_b'] else 'mixed'}",
        "**Role:** native",
        f"**Prediction outcome (dated, written against H72):** (a) {'held' if n3['pass_a'] else 'failed'}, (b) {'held' if n3['pass_b'] else 'failed'}. "
        "The verdict line scores H72's claim: the room's escape difference does not run through starvation.",
        "**Period:** regime III · #51 unit 51g (#focus opens 08-05; window to 08-24 when the room empties) · "
        f"{n3['agents']} agents with gates in both #focus and #general · {n3['gates']} gates ({n3['gates_focus']} in #focus).", "",
        "## Why this period",
        "Cross-room reads fall 95% when #focus opens (RE-R1, H58), so the same agent sees less input in #focus. If "
        "starvation sets escape, the room difference in escape should run through s.", "",
        "## Prediction", "*Written 2026-10-04, before running (card, N3).*",
        "(a) median s_novel in #focus ≥ 2× #general [0.7]; (b) the #focus coefficient moves by < 30% of itself (or < 0.1 "
        "logit) when the s clocks are added [0.5]. Low power: 5 agents.", "",
        "## Result", f"`analysis/native.py`; numbers in `{SRC}/native/native.json` (B = 200).", "",
        "| Quantity | Estimate [95% CI] | Prediction |", "| --- | --- | --- |",
        f"| median s_novel #focus / #general (min) | {n3['median_s_novel_min']['focus']:.1f} / {n3['median_s_novel_min']['general']:.1f} "
        f"(×{n3['s_ratio_focus_over_general']:.2f}) | (a) {'pass' if n3['pass_a'] else 'fail'} |",
        f"| β_#focus without s | {f2(n3['beta_F_without_s']['est'])} {ci(n3['beta_F_without_s']['ci'])} | |",
        f"| β_#focus with s | {f2(n3['beta_F_with_s']['est'])} {ci(n3['beta_F_with_s']['ci'])} | |",
        f"| change | {f2(n3['delta_F']['est'])} {ci(n3['delta_F']['ci'])} | (b) {'pass' if n3['pass_b'] else 'fail'} |", ""])
    return out


def estimates_rows(results, infos):
    import estimates as E
    rows = []
    for r in results:
        p = r["primary"]
        if "beta_a0" not in p:
            continue
        g = int(r["period"][1:])
        unit = E.map_unit(g)
        base = {"period_unit": unit, "goal_no": g, "channel": "idle_gate_escape_sustained", "role": "replication",
                "ci_level": 0.95, "ci_kind": "percentile", "n": float(p["n"]), "n_kind": "events",
                "unit_local": f"{r['period']} non-holdout", "first_day": infos[r["period"]]["first"],
                "last_day": infos[r["period"]]["last"], "status": "ok", "post_hoc": False,
                "source": f"{SRC}/{r['period']}/results.json",
                "null": "beta = 0; day-block bootstrap (200 draws)",
                "notes": f"verdict: {p['verdict']}"}
        m = "logit, agent FE, sustained escape at idle gates; a=a_sus, s=s_novel (ln min); day-block bootstrap 200"
        for stat, est, c in (("beta_trap_age_no_s", p["beta_a0"], p["ci_a0"]),
                             ("beta_trap_age_given_s", p["beta_a"], p["ci_a"]),
                             ("beta_input_starvation_given_a", p["beta_s"], p["ci_s"]),
                             ("aging_absorbed_rho", p["rho"], p["ci_rho"])):
            rows.append({**base, "statistic": stat, "estimate": float(est), "ci_lo": float(c[0]), "ci_hi": float(c[1]),
                         "method": m})
        rows.append({**base, "statistic": "cv_gain_trap_age_nats_per_1000", "estimate": float(p["cv_per_1000"]["a_adds"]),
                     "ci_lo": float(p["cv"]["a_adds_ci"][0] / p["n"] * 1000), "ci_hi": float(p["cv"]["a_adds_ci"][1] / p["n"] * 1000),
                     "method": "5 interleaved day folds, held-out log-lik of (a,s) minus (s); day bootstrap 1000"})
        rows.append({**base, "statistic": "cv_gain_starvation_nats_per_1000", "estimate": float(p["cv_per_1000"]["s_adds"]),
                     "ci_lo": float(p["cv"]["s_adds_ci"][0] / p["n"] * 1000), "ci_hi": float(p["cv"]["s_adds_ci"][1] / p["n"] * 1000),
                     "method": "5 interleaved day folds, held-out log-lik of (a,s) minus (a); day bootstrap 1000"})
    return rows


def main():
    g = pl.read_parquet(OUT / "gates.parquet")
    infos = {}
    for k, a, b in g.group_by("goal_no").agg(pl.col("pt_date").min().alias("a"), pl.col("pt_date").max().alias("b")).iter_rows():
        infos[f"G{k:02d}"] = {"first": a, "last": b}
    results = [json.loads(f.read_text()) for f in sorted(OUT.glob("G*/results.json"))]
    for r in results:
        d = GP / r["period"]
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(period_readme(r, infos[r["period"]]))
    nat_p = OUT / "native/native.json"
    if nat_p.exists():
        for name, txt in native_readmes(json.loads(nat_p.read_text())).items():
            d = GP / name
            (d / "figures").mkdir(parents=True, exist_ok=True)
            (d / "README.md").write_text(txt + "\n")
    if "--no-estimates" not in sys.argv:
        import estimates as E
        df = E.write_estimates(estimates_rows(results, infos), hypothesis="H72")
        print("estimate rows", df.height)


if __name__ == "__main__":
    main()
