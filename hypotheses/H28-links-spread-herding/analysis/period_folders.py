"""Write H28 goal-period folders: predictions (before the run) and results (after).

  uv run python hypotheses/H28-links-spread-herding/analysis/period_folders.py --predictions   # before any real-data fit
  uv run python hypotheses/H28-links-spread-herding/analysis/period_folders.py --results       # fills Result / Verdict

The prediction block is written once and never rewritten (the results pass keeps it verbatim).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
from h28lib import ALL_PERIODS, OUT, PERIOD_DIR, ROLE, gname  # noqa: E402

PRED_DATE = "2026-10-04"
INFO = {
    18: dict(title="Reduce global poverty as much as you can", dates="2025-10-20 → 2025-11-03", regime="I", mode="C",
             why="Named candidate. H11: herding (βJ_CW +5.0, local-shift z +4.1) with a last-day convergence of the whole swarm onto one repo. **Pre-NE09**: chat reached computer-use calls only at session boundaries, so visibility is the next `events_core` turn.",
             expect="P1 supported but with a slower kernel (more weight in 15–60 and 60–240 min than post-NE09 periods). The last-day convergence is deadline drive, so R_link is low (0.1–0.2). P8: median excess lag > 15 min."),
    19: dict(title="Create a popular daily puzzle game like Wordle", dates="2025-11-03 → 2025-11-17", regime="I", mode="C",
             why="H11 herding (z_local +3.9) but the build repo dominated from the start (frozen consensus). Pre-NE09.",
             expect="P1 weak (most agents are already on the dominant repo, so few susceptible exposures); R_link < 0.2; slow kernel (P8)."),
    24: dict(title="Do random acts of kindness!", dates="2025-12-22 → 2025-12-29", regime="I", mode="C",
             why="H11 herding (z_local +2.4); small link volume (45 links to universe projects), post-NE09 (first period after it).",
             expect="Low power: P1 weak at best; λ imprecise."),
    25: dict(title="Create a digital museum of 2025", dates="2025-12-29 → 2026-01-05", regime="I", mode="C",
             why="H11 herding (z_local +3.0); exhibits in shared repos, ≈ 200 links.",
             expect="P1 supported, e^κ ≈ 2–4; R_link 0.1–0.3."),
    26: dict(title="Elect a village leader", dates="2026-01-05 → 2026-01-12", regime="I", mode="C",
             why="H11 herding (z_local +3.4); the week's coordination ran through chat votes, not repos; ≈ 120 links.",
             expect="P1 weak: links matter less when the coordinating object is a vote. R_link < 0.2."),
    30: dict(title="Adopt a park and get it cleaned!", dates="2026-02-09 → 2026-02-16", regime="I", mode="C",
             why="H11 herding (z_local +3.5); one shared repo plus satellites; nudger starts 2026-02-10.",
             expect="P1 supported; the nudger is controlled by `auto30` (it does not post links)."),
    31: dict(title="Pick your own goal (farewell to Claude 3.7 Sonnet)", dates="2026-02-16 → 2026-02-23", regime="I", mode="F",
             why="Named candidate and the clearest pile-on: H11 herding waves onto successive shared repos (time capsule at 11 agents in one window; βJ_CW +4.9, local-shift z +8.3). Free week, so no goal field beyond the farewell.",
             expect="P1 supported with the strongest κ of the regime-I periods (e^κ 2–5); R_link 0.15–0.35; f = 0 lowers the simulated peak occupancy by 10–30% but the time-capsule pile-on stays (≥ 50% of f = 1)."),
    37: dict(title="Pick your own goal!", dates="2026-03-30 → 2026-04-02", regime="III", mode="F",
             why="Named candidate; free 3-day period; two rooms (#best, #rest) so the other-room placebo applies; ≈ 90 links (low).",
             expect="P1 weak-to-supported; room placebo (P2c) underpowered (cross-room projects rarely overlap)."),
    38: dict(title="Choose a charity and raise as much money as you can", dates="2026-04-02 → 2026-04-27", regime="III", mode="C",
             why="Named candidate; 17 days, two rooms with different instructions, ≈ 800 links. H11: positive βJ but the herding failed the local-shift null (z +1.2) — a test of whether links carry fast herding where H11 saw little.",
             expect="P1 supported (power from 17 days) but small κ (e^κ ≈ 1.5–2.5); R_link < 0.2; room placebo κ_other ≈ 0."),
    39: dict(title="Build your own interactive world!", dates="2026-04-27 → 2026-05-04", regime="III", mode="I",
             why="Contrast (own-artifact week; H11 found spread by fields, no herding). ≈ 680 links (agents advertise their own worlds).",
             expect="P9: λ below the shared-artifact median; P1 may still pass (visits to others' worlds after a link) but R_link small."),
    40: dict(title="Connect your worlds into a 3D universe!", dates="2026-05-04 → 2026-05-11", regime="III", mode="C",
             why="Contrast (own worlds plus a fixed hub; H11 no herding, z_N2 ≈ 0). One coordination room.",
             expect="P9: λ below the shared-artifact median."),
    41: dict(title="Perform novel research!", dates="2026-05-11 → 2026-05-18", regime="III", mode="I",
             why="Named candidate; ≈ 11 #rest agents converged on one topic (H11 βJ_CW +4.3, local-shift z +4.2); two rooms with different topics.",
             expect="P1 supported (e^κ 2–4); room placebo κ_other ≈ 0; R_link 0.1–0.3."),
    42: dict(title="Run your own Youtube channel!", dates="2026-05-18 → 2026-05-25", regime="III", mode="I",
             why="Contrast (own channels; H11 no herding). ≈ 100 links.",
             expect="P9: λ below the shared-artifact median; P1 weak or failed."),
    51: dict(title="Each agent: Maximize your assigned goal!", dates="2026-07-06 → 2026-09-07 (non-holdout part; the tail to 09-21 is held out)", regime="III", mode="I/K (private roles)",
             why="Named candidate; 45 non-holdout days, 21–32 agents, ≈ 7,400 links: by far the most power. H22: a random-field system (private roles pin positions) with a weak positive room pull, so links should matter little relative to fields. #focus room from 2026-08-05 gives an other-room placebo.",
             expect="P1 supported on power but κ small (e^κ ≈ 1.3–2); R_link < 0.1; room placebo κ_other ≈ 0."),
}


def header(g, meta):
    i = INFO[g]
    nA = len(set(a for v in meta["roster_day"].values() for a in v))
    return (f"# H28 × G{g:02d}: {i['title']} ({i['dates']})\n\n"
            f"**Verdict:** pending\n**Role:** exploratory ({ROLE[g]})\n"
            f"**Period:** regime {i['regime']} · mode {i['mode']} · {nA} agents on the roster · {len(meta['days'])} non-holdout days"
            f"{' · pre-NE09 visibility rule' if meta['pre_ne09'] else ''}.\n\n")


def write_predictions():
    for g in ALL_PERIODS:
        d = PERIOD_DIR / gname(g)
        d.mkdir(parents=True, exist_ok=True)
        (d / "figures").mkdir(exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        f = d / "README.md"
        if f.exists() and "## Prediction" in f.read_text():
            print(f"{gname(g)}: prediction exists, kept")
            continue
        meta = json.loads((OUT / gname(g) / "meta.json").read_text())
        i = INFO[g]
        txt = header(g, meta)
        txt += f"## Why this period\n{i['why']}\n\n"
        txt += (f"## Prediction\n*Written {PRED_DATE}, before running on this period.*\n\n"
                f"Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.\n\n"
                f"- **Here:** {i['expect']}\n"
                f"- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.\n\n")
        txt += "## Result\npending\n\n## Scorecard (period-specific axes)\npending\n\n## Notes\n"
        f.write_text(txt)
        print(f"{gname(g)}: prediction written")


def fmt(x, n=2):
    return "–" if x is None or x != x else f"{x:+.{n}f}" if n else f"{x:.0f}"


def verdict(r):
    """P1 rule (card): supported if kappa > 0 with z_shift >= 2 and p < 0.05; weak if right sign with one; else failed."""
    if not r["tested"]:
        return "n/a"
    k, z, p = r["kappa"], r["z_shift"], r["p"]
    if k > 0 and z >= 2 and p < 0.05:
        return "supported"
    if k > 0 and (z >= 2 or p < 0.05):
        return "weak"
    return "failed"


def write_results():
    for g in ALL_PERIODS:
        f = PERIOD_DIR / gname(g) / "README.md"
        rp = OUT / gname(g) / "round1.json"
        if not rp.exists():
            continue
        r = json.loads(rp.read_text())
        txt = f.read_text()
        v = verdict(r)
        vmap = {"supported": "supported", "weak": "mixed", "failed": "failed", "n/a": "n/a"}
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {vmap[v]} (P1 {v})", txt, count=1)
        a = r["attr"]
        lam_ci = a.get("lam_ci", [float("nan")] * 2)
        R_ci = a.get("R_ci", [float("nan")] * 2)
        lead, mom = r["lead"], r["momentum"]
        rows = [
            ("P1 κ (any visible link, last 60 min)", f"{fmt(r['kappa'])} ± {r['se']:.2f} (e^κ {pow(2.718281828, r['kappa']):.2f}); p {r['p']:.3g}; z_shift {r['z_shift']:+.1f} (null {r['null']['mean']:+.2f} ± {r['null']['sd']:.2f}, n = {r['null']['n']})", "κ > 0, z ≥ 2, p < 0.05", v),
            ("P2a lead placebo", f"κ_lead {fmt(lead['lead']['b'])}; κ − κ_lead {fmt(lead['diff']['d'])} (one-sided p {lead['diff']['p']:.3g})", "κ − κ_lead > 0, p < 0.05", "pass" if lead['diff']['p'] < 0.05 and lead['diff']['d'] > 0 else "fail"),
            ("P2b momentum control", f"κ {fmt(mom['kappa']['b'])} (p {mom['kappa']['p']:.3g}); momentum {fmt(mom['mom']['b'])}", "≥ 50% of κ, p < 0.05", "pass" if r['kappa'] > 0 and mom['kappa']['b'] >= 0.5 * r['kappa'] and mom['kappa']['p'] < 0.05 else "fail"),
        ]
        if "room" in r and r["room"]["other_rows"] > 0:
            ro = r["room"]
            rows.append(("P2c other-room placebo", f"κ_same {fmt(ro['same']['b'])}; κ_other {fmt(ro['other']['b'])} ± {ro['other']['se']:.2f} ({ro['other_rows']} exposed rows, {ro['other_events']} arrivals)", "κ_other < κ_same, CI ∋ 0",
                         "pass" if (ro['other']['b'] < ro['same']['b'] and ro['other']['p'] > 0.05) else "fail"))
        es = r["event_study"]
        pre = es["pre"]["O"] / es["pre"]["E"] if es["pre"]["E"] > 0 else float("nan")
        post = es["post"]["O"] / es["post"]["E"] if es["post"]["E"] > 0 else float("nan")
        rows += [
            ("P3a naive agents", f"κ {fmt(r['naive']['b'])} ± {r['naive']['se']:.2f} (p {r['naive']['p']:.3g}); first arrivals {r['arrivals_first']}", "κ > 0", "pass" if r['naive']['b'] > 0 and r['naive']['p'] < 0.05 else "fail"),
            ("P3b pre-trend (O/E)", f"pre {pre:.2f} ({es['pre']['O']:.0f} obs), post {post:.2f} ({es['post']['O']:.0f} obs)", "pre excess < ½ post excess", "pass" if (post > 1 and (pre - 1) < 0.5 * (post - 1)) else "fail"),
            ("P4 dose", "; ".join(f"{k} {fmt(r['dose'][k]['b'])} (n_ev {r['dose_events'][k]})" for k in ("d11", "d12", "d13", "dS2")) + f"; CV complex − simple {r['cv']['complex'] - r['cv']['simple']:+.1f}", "1-link HR > 1; S2 adds < 50%", "pass" if (r['dose']['d11']['b'] > 0 and r['cv']['complex'] - r['cv']['simple'] <= 0) else "fail"),
            ("P5 λ (extra arrivals per exposure)", f"{a['lam']:.3f} [{lam_ci[0]:.3f}, {lam_ci[1]:.3f}]; N_exp {a['n_exp']:.0f}", "0.01–0.15", "pass" if 0.01 <= a['lam'] <= 0.15 else "fail"),
            ("P6 R_link", f"{a['R_link']:.2f} [{R_ci[0]:.2f}, {R_ci[1]:.2f}]; R_all (links + occupancy) {r['R_all']:.2f}", "< 0.5", "pass" if a['R_link'] < 0.5 else "fail"),
            ("P10 occupancy J", f"J {fmt(r['J'])} (pd FE {fmt(r['pd']['J']['b'])}); without links {fmt(r['J_without_links']['b'])}", "J > 0 both; drop < 50%", "pass" if (r['J'] > 0 and r['pd']['J']['b'] > 0) else "fail"),
        ]
        if "cf_summary" in r:
            cs, cc = r["cf_summary"], r["cf_calibration"]
            rows.append(("P7 counterfactual peak occupancy", f"f=0.5 ×{cs['f05']['peak_occ']:.2f}; f=0 ×{cs['f0']['peak_occ']:.2f}; cap ×{cs['cap2h']['peak_occ']:.2f}; burst f=0 ×{cs['f0']['burst60']:.2f}",
                         "f=0: 0.70–0.90 (≥ 0.5)", "pass" if 0.70 <= cs['f0']['peak_occ'] <= 0.90 else "fail"))
            rows.append(("P7 calibration (unfitted)", f"observed peak {cc['peak_occ']['obs']} vs sim [{cc['peak_occ']['lo']:.0f}, {cc['peak_occ']['hi']:.0f}]; burst {cc['burst60']['obs']} vs [{cc['burst60']['lo']:.0f}, {cc['burst60']['hi']:.0f}]",
                         "inside 90%", "pass" if cc['peak_occ']['inside'] else "fail"))
        lat = r["latency"]
        rows.append(("P8 latency (median excess lag)", f"{lat['median_excess_lag']:.0f} min; excess 0–15 {lat['excess_0_15']:+.1f}, 15–60 {lat['excess_15_60']:+.1f}, 60–240 {lat['excess_60_240']:+.1f}", "post-NE09 < pre", "–"))
        tab = "| Test | Observed | Rule | Verdict |\n| --- | --- | --- | --- |\n" + "\n".join(f"| {a_} | {b_} | {c_} | {d_} |" for a_, b_, c_, d_ in rows)
        res = (f"## Result\n*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/{gname(g)}/round1.json`).* "
               f"{r['arrivals']} arrivals ({r['arrivals_first']} first), {r['links_universe']} links to {r['K']} universe projects, "
               f"{r['exposed_arrivals']} arrivals within 60 min of a visible link. {'Tested.' if r['tested'] else 'Below the minimum data rule: descriptive only.'}\n\n" + tab + "\n\n")
        sc = ("## Scorecard (period-specific axes)\n"
              f"- **C:** link time-shift null z {r['z_shift']:+.1f}; held-out (quarter-blocked) Δ log-lik primary − occupancy-only {r['cv']['primary'] - r['cv']['occ_only']:+.1f}.\n"
              f"- **D:** simulated pile-on calibration {'inside' if r.get('cf_calibration', {}).get('peak_occ', {}).get('inside') else 'outside'} the 90% interval.\n"
              f"- **H:** lead {'beaten' if lead['diff']['p'] < 0.05 and lead['diff']['d'] > 0 else 'not beaten'}; momentum {'survived' if r['kappa'] > 0 and mom['kappa']['b'] >= 0.5 * r['kappa'] and mom['kappa']['p'] < 0.05 else 'not survived'}"
              + (f"; other-room placebo {'clean' if r['room']['other']['p'] > 0.05 and r['room']['other']['b'] < r['room']['same']['b'] else 'not clean'}" if "room" in r and r["room"]["other_rows"] > 0 else "") + ".\n\n")
        notes = ["## Notes"]
        rb = OUT / "robust_shared_labels.json"
        if rb.exists():
            x = json.loads(rb.read_text()).get(str(g))
            if x and "kappa" in x:
                notes.append(f"- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels "
                             f"(`project_states.parquet`, 30 min, window switches) κ = {x['kappa']:+.2f} ± {x['se']:.2f} "
                             f"(p {x['p']:.3g}; {x['switches']} switches), z_shift {x['z_shift']:+.1f}.")
        ph = OUT / "posthoc_round1.json"
        if ph.exists():
            x = json.loads(ph.read_text()).get(str(g))
            if x:
                notes.append(f"- *Post hoc short-lag check:* visible link in the last 15 min b = {x['b_L15']:+.2f} ± {x['se_L15']:.2f} "
                             f"(z vs shift null {x['z15']:+.1f}); link arriving in the next 15 min b = {x['b_F15']:+.2f} ± {x['se_F15']:.2f}; "
                             f"lag − lead {x['diff15']:+.2f} (one-sided p {x['p_diff15']:.3g}). Action-only latency: median excess lag "
                             f"{x['latency_action']['median_excess_lag']:.0f} min.")
        notes.append("- Holdout days: none in this period's build (non-holdout days only).")
        txt = re.sub(r"## Notes\n.*\Z", lambda _m: "\n".join(notes) + "\n", txt, flags=re.S)
        txt = re.sub(r"## Result\n.*?(?=## Notes)", res + sc, txt, flags=re.S)
        f.write_text(txt)
        print(f"{gname(g)}: {v}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    if a.predictions:
        write_predictions()
    if a.results:
        write_results()
