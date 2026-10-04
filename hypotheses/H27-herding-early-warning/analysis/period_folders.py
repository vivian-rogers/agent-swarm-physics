"""Write goalperiod-subhypotheses/G<NN>/README.md for H27.

  --predict   header + dated prediction (verdict pending), before the period is run
  --results   fills Result / Scorecard / Notes from data/processed/H27-herding-early-warning/G<NN>/round1_w*.json,
              keeping the prediction text exactly as written

No agent text is written; project names are artifact names (repos / sites) from H11's label table.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H27-herding-early-warning"
PER = HYP / "goalperiod-subhypotheses"
DATA = ROOT / "data/processed/H27-herding-early-warning"
GP = ROOT / "hypotheses/hypohypotheses/goal-periods.md"
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Prior onset counts (W = 15, O1), written 2026-10-04 before running any period; see the card's P0.
EXPECT = {
    17: ("0", "each agent builds its own personal website (own artifacts)"),
    18: ("0–1", "candidate; sparse labels (≈ 3 per window) and the last-day convergence may fail the coverage or baseline condition"),
    19: ("0–1", "the build repo held ≈ 0.6 share from the start in H11 (frozen order: no low baseline to step from)"),
    20: ("0–1", "individual blogs; little shared work"),
    24: ("0–2", "shared-objective week that herded in H11"),
    25: ("0–2", "shared museum; herded in H11"),
    26: ("0–1", "the runoff jump lives in the votes, not in project labels"),
    30: ("1–3", "shared park-cleanup documents; herded in H11; dense labels"),
    31: ("≥ 3", "candidate; H11 saw successive herding waves (time-capsule repo peaked at 11 agents in one window)"),
    33: ("0–2", "3 days only; few evaluable"),
    35: ("1–2", "game testing after the #best/#rest split; each fork is its own repo"),
    37: ("0–2", "candidate; 3 days only, so few onsets have 24 windows of history"),
    38: ("2–5", "17 days of shared charity campaign work; dense labels"),
    39: ("0", "own worlds (ownership index 1.00 in H11): spread, not herding"),
    40: ("0–1", "own worlds plus a fixed hub given by the goal"),
    41: ("1–3", "candidate; topic convergence, which may or may not show up as one repo"),
    42: ("0–1", "own channels (ownership 0.73)"),
    44: ("0–2", "fine-tuning the leader; a shared dataset repo is plausible"),
    51: ("0–3", "private assigned goals (H22: random-field system); long, so mainly a false-alarm testbed"),
}


def glance():
    rows = {}
    for line in GP.read_text().splitlines():
        m = re.match(r"^\| (\d+) \| (\S+) → (\S+) \| (\S+) \| (\d+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \|", line)
        if m:
            rows[int(m.group(1))] = dict(start=m.group(2), end=m.group(3), days=m.group(4), N=m.group(5), regime=m.group(7),
                                         mode=m.group(9))
    titles = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^### (\d+) · (.+)$", GP.read_text(), re.M)}
    return rows, titles


def header(g, verdict, cov):
    rows, titles = glance()
    r = rows.get(g, {})
    c15 = cov.get(str(g), {}).get("w15", {})
    c30 = cov.get(str(g), {}).get("w30", {})
    role = "exploratory (candidate)" if g in (18, 31, 37, 41) else "exploratory (transfer / false-alarm period)"
    extra = " Locked tail 2026-09-07 → 09-21 excluded (holdout)." if g == 51 else ""
    return (f"# H27 × G{g:02d}: {titles.get(g, '?')} ({r.get('start', '?')} → {r.get('end', '?')})\n\n"
            f"**Verdict:** {verdict}\n"
            f"**Role:** {role}\n"
            f"**Period:** regime {r.get('regime', '?')} · mode {r.get('mode', '?')} · N = {r.get('N', '?')} · "
            f"{c15.get('days', '?')} active days in the series · W = 15: {c15.get('windows', '?')} windows, q = {c15.get('q', '?')}, "
            f"{100 * c15.get('frac_n_ge3', 0):.0f}% of windows with ≥ 3 labeled agents (mean {c15.get('mean_n', 0):.1f}); "
            f"W = 30: {100 * c30.get('frac_n_ge3', 0):.0f}%.{extra}\n")


def prediction_text(g, arms):
    exp, why = EXPECT.get(g, ("0–2", "no specific expectation"))
    arm_txt = " and ".join(arms)
    return f"""## Why this period
{why[0].upper() + why[1:]}. Arms: {arm_txt} (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** {exp} herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.
"""


def write_predict(goals_arms):
    cov = json.loads((DATA / "coverage.json").read_text())
    for g, arms in goals_arms.items():
        d = PER / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        txt = header(g, "pending", cov) + "\n" + prediction_text(g, arms) + "\n## Result\n*(pending)*\n\n## Scorecard (period-specific axes)\n*(pending)*\n\n## Notes\n- 2026-10-04: prediction written before running this period.\n"
        (d / "README.md").write_text(txt)
        print("wrote", d / "README.md")


def fmt(x, nd=2):
    return "–" if x is None or (isinstance(x, float) and x != x) else f"{x:.{nd}f}"


def period_verdict(per, ops_ews):
    if per is None or per["n_eval"] == 0:
        return "descriptive", "no evaluable onset"
    hits = sum(1 for o in ops_ews["per_onset"] if o["hit"])
    n_on = ops_ews["n_onsets"]
    if per["n_eval"] == 1:
        pc = per["percentiles"][0] if per["percentiles"] else None
        return "descriptive", (f"1 evaluable onset, percentile {fmt(pc)}" if pc is not None
                               else "1 evaluable onset, no placebos")
    a = per["auc_composite"]
    if a is not None and a >= 0.7 and hits >= n_on / 2:
        return "supported", f"AUC {fmt(a)}, {hits}/{n_on} hit"
    if a is not None and a < 0.6 and hits < n_on / 2:
        return "failed", f"AUC {fmt(a)}, {hits}/{n_on} hit"
    return "mixed", f"AUC {fmt(a)}, {hits}/{n_on} hit"


def write_results(tau_star, notes_extra=None):
    cov = json.loads((DATA / "coverage.json").read_text())
    summary = []
    for d in sorted(PER.glob("G*")):
        g = int(d.name[1:])
        f15, f30 = DATA / d.name / "round1_w15.json", DATA / d.name / "round1_w30.json"
        R15 = json.loads(f15.read_text()) if f15.exists() else None
        R30 = json.loads(f30.read_text()) if f30.exists() else None
        R = R15 or R30
        if R is None:
            continue
        W = R["W"]
        txt = (d / "README.md").read_text()
        pred = txt[txt.index("## Why this period"):txt.index("## Result")]
        per, ops = R["per_period"], R["operator"]
        v, vtxt = period_verdict(per, ops["ews"])
        if R15 is None:
            v, vtxt = "descriptive", "30-min arm; " + vtxt
        projs = {}
        pf = DATA / d.name / f"projects_w{W}.parquet"
        if pf.exists():
            import polars as pl
            projs = dict(zip(pl.read_parquet(pf)["label"].to_list(), pl.read_parquet(pf)["project"].to_list()))
        lines = ["| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        po_e = {(o["project"], o["w0"]): o for o in ops["ews"]["per_onset"]}
        po_l = {(o["project"], o["w0"]): o for o in ops["level"]["per_onset"]}
        po_m = {(o["project"], o["w0"]): o for o in ops["momentum"]["per_onset"]}
        drops = R["drops"].get("4", {})
        import polars as pl
        segf = DATA / "segments_round1.parquet"
        evset = set()
        if segf.exists():
            sg = pl.read_parquet(segf).filter((pl.col("arm") == f"W{W}") & (pl.col("goal") == g) & (pl.col("lead") == 4)
                                              & (pl.col("kind") == "onset"))
            evset = {(a, te + 4) for a, te in zip(sg["project"].to_list(), sg["t_e"].to_list())}
        for o in R["onsets"]:
            key = (o["project"], o["w0"])

            def al(po):
                x = po.get(key)
                if x is None:
                    return "–"
                if x["hit"]:
                    return f"hit, lead {x['lead_windows'] * W / 60:.2f} h"
                return "miss" if x["warnable"] else "not watchable"
            import ews_core as E
            name = E.display_project(projs.get(o["project"] + 1, "?"), o["project"] + 1)
            flags = (" (day start)" if o["day_start"] else "") + (" (last day)" if o["last_day"] else "")
            lines.append(f"| w{o['w0']}{flags} | `{name}` | {o['x0']:.2f} ({o['k0']}/{o['n0']}) | {o['base_mean']:.2f} → {o['pers_mean']:.2f} | "
                         f"{'yes' if key in evset else 'no'} | {al(po_e)} | {al(po_l)} | {al(po_m)} |")
        e = ops["ews"]
        res = [f"Arm W = {W} min. τ* = {tau_star:.3f} (frozen from synthetic S0). Onsets (O1): {len(R['onsets'])}; O1-slow variant: {len(R['onsets_slow'])}. "
               f"Onsets dropped at ℓ = 4: {drops.get('onset_short', 0)} too early (< 24 windows of history), {drops.get('onset_invalid', 0)} too sparse, "
               f"{drops.get('onset_unmatched', 0)} not low at t_e.", ""]
        if R["onsets"]:
            res += lines + [""]
        res += ["| Test | Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- | --- |"]
        res.append(f"| P0 onsets | {EXPECT.get(g, ('?',))[0]} | {len(R['onsets'])} | – | {'as expected' if _in_range(len(R['onsets']), EXPECT.get(g, ('0–99',))[0]) else 'outside the expected range'} |")
        if per and per["n_eval"] >= 2:
            res.append(f"| P1 composite AUC (ℓ = 4) | < 0.6 | {fmt(per['auc_composite'])} ({per['n_eval']} onset vs {per['n_placebo']} placebo segments) | 0.5 | "
                       f"{'as predicted (chance)' if per['auc_composite'] < 0.6 else 'against my prior'} |")
            res.append(f"| P2 τ_AR1 / τ_SD / τ_SD binomial / τ_flicker / flicker level / mean share last 4 | signal only in SD or flicker, gone after standardization | "
                       f"{fmt(per['auc_tau_ar1'])} / {fmt(per['auc_tau_sd'])} / {fmt(per['auc_tau_sd_binom'])} / {fmt(per['auc_tau_flick'])} / {fmt(per['auc_flick_level'])} / {fmt(per['auc_mean_last4'])} | 0.5 | descriptive |")
        elif per and per["n_eval"] == 1 and not per["percentiles"]:
            res.append("| P1 composite percentile among placebos | < 0.9 | no placebo segments (both projects alternate dominance) | – | untestable |")
        elif per and per["n_eval"] == 1:
            res.append(f"| P1 composite percentile among placebos | < 0.9 | {fmt(per['percentiles'][0])} (vs {per['n_placebo']} placebo segments) | 0.5 | "
                       f"{'as predicted' if per['percentiles'][0] < 0.9 else 'against my prior'} |")
        neg = max(e["negatives"], 1)
        res.append(f"| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | {e['hits']}/{e['n_onsets']} hit ({e['warnable']} watchable); "
                   f"{e['false_alarms']} false alarms in {e['negatives']} watched (project, window) = {100 * e['false_alarms'] / neg:.1f}%; "
                   f"PPV {fmt(e['true_alarms'] / max(e['n_alarms'], 1))} | level alarm {ops['level']['hits']}/{ops['level']['n_onsets']} hit, "
                   f"FAR {100 * ops['level']['false_alarms'] / max(ops['level']['negatives'], 1):.1f}% | "
                   f"{'as predicted' if (e['hits'] <= e['n_onsets'] / 2) else 'against my prior'} |")
        if R30 is not None and R15 is not None:
            p30 = R30["per_period"]
            res.append(f"| W = 30 arm | – | onsets {len(R30['onsets'])}; evaluable {p30['n_eval'] if p30 else 0}; "
                       f"AUC {fmt(p30['auc_composite']) if p30 and p30['n_eval'] >= 2 else '–'}; EWS hits {R30['operator']['ews']['hits']}/{R30['operator']['ews']['n_onsets']} | – | robustness |")
        sc = ["| Axis | Score | Evidence |", "| --- | --- | --- |"]
        if per and per["n_eval"] >= 2:
            sc.append(f"| C adequacy | {1 if per['auc_composite'] >= 0.7 else 0} | composite AUC {fmt(per['auc_composite'])} vs placebo segments |")
        sc.append(f"| G ground truth | {'1' if len(R['onsets']) else '0'} | onsets found by the rule: {len(R['onsets'])} (compare H11's narrative for this period) |")
        notes = ["- 2026-10-04: prediction written before running this period.",
                 f"- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/{d.name}/round1_w*.json`."]
        if notes_extra and g in notes_extra:
            notes += notes_extra[g]
        new = (header(g, f"{v} ({vtxt})", cov) + "\n" + pred + "## Result\n" + "\n".join(res) + "\n\n## Scorecard (period-specific axes)\n"
               + "\n".join(sc) + "\n\n## Notes\n" + "\n".join(notes) + "\n")
        (d / "README.md").write_text(new)
        summary.append(dict(goal=g, verdict=v, vtxt=vtxt, n_onsets=len(R["onsets"]), n_eval=(per or {}).get("n_eval", 0),
                            auc=(per or {}).get("auc_composite"), hits=e["hits"], far=e["false_alarms"] / neg,
                            level_hits=ops["level"]["hits"], W=W))
    (DATA / "period_verdicts_round1.json").write_text(json.dumps(summary, indent=1))
    return summary


def _in_range(x, s):
    s = s.replace("≥ ", ">=")
    if s.startswith(">="):
        return x >= int(s[2:])
    if "–" in s:
        a, b = s.split("–")
        return int(a) <= x <= int(b)
    return x == int(s)


# Period notes written after the round-1 run (2026-10-04); facts from results_round1.json / assemble_round1.json.
NOTES = {
    18: ["- 2026-10-04 (post hoc): 3 of the 4 onsets land on projects never mentioned before in the period (two Netlify sites and a "
         "Google doc; 3–8 agents in the first window the project appears). No share-based indicator can warn of these. "
         "H11's last-day convergence is not an O1 onset (none of the W = 15 or W = 30 onsets is on the last day): it did not start from a low baseline."],
    19: ["- 2026-10-04 (post hoc): the build repo dominated from the start (H11: frozen order); the 3 onsets are on the landing repo and "
         "sites. One lands on a project with no prior mention."],
    30: ["- 2026-10-04 (post hoc): all 4 onsets are returns of the same shared site repo to majority after dips; the two late ones "
         "were warned by the EWS alarm (leads 1.25 h and 3 h) and the level alarm (2.5 h and 3 h); a 3-h lead is the horizon cap, i.e. "
         "the alarm was already on. The two early onsets had too little history."],
    31: ["- 2026-10-04 (post hoc): matches H11's waves. Onsets on the guardrails repo (day 2 start), the time-capsule repo, the "
         "operations handbook and the event log (H11's final-day dominant repo). The first two come within the first 1.5 days, "
         "so only 2 are evaluable; for those, τ_SD rises while τ_AR1 falls (not critical slowing down)."],
    33: ["- 2026-10-04 (post hoc): q = 2; both onsets are a last-day handover between the two projects. The low-state matching "
         "condition never holds for placebo segments, so the period informs only the operator alarm."],
    37: ["- 2026-10-04 (post hoc): 3 days; the one onset (day 1) has no history."],
    38: ["- 2026-10-04 (post hoc): 3 onsets in 17 days on the two shared campaign repos; the evaluable one shows rising variance and "
         "flickering with falling AR1."],
    41: ["- 2026-10-04 (post hoc): no onset, although H11 found strong herding (βJ_CW +4.3): agents co-move across several repos "
         "without any one reaching a majority from a low baseline. Topic convergence is not a repo pile-on."],
    51: ["- 2026-10-04 (post hoc): no onset in 45 non-holdout days (private assigned goals). The EWS alarm still fired 462 false "
         "alarms (≈ 10 per 8-h day across 8 projects): the false-alarm testbed the card expected."],
    39: ["- 2026-10-04: no onset, as predicted for own-world weeks (H11 ownership 1.00)."],
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    if a.predict:
        import explore as X
        p15 = X.period_set(15)
        p30 = X.period_set(30)
        ga = {g: (["W = 15 (primary)", "W = 30"] if g in p15 else ["W = 30 only"]) for g in sorted(set(p15) | set(p30))}
        write_predict(ga)
    if a.results:
        import explore as X
        s = write_results(X.load_tau_star(), NOTES)
        for r in s:
            print(r)
