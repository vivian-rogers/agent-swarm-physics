"""Write the H89 period READMEs (goalperiod-subhypotheses/G<NN>/README.md and NE<NN>/README.md).

  --predict   before the real-data run: verdict pending, dated prediction
  --results   after replication.py / natives.py: fills Result and Scorecard and the verdict (prediction unchanged)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
GP = ROOT / "hypotheses/hypohypotheses/goal-periods.md"
DATA = ROOT / "data/processed/H89-price-equation-culture"
GOALS = [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38,
         39, 40, 41, 42, 44, 51]
NATIVE_G = {51}
STAMP = "2026-10-04 20:35 UTC"


def goal_meta() -> dict[int, dict]:
    txt = GP.read_text()
    out = {}
    for m in re.finditer(r"^\| (\d+) \| (\S+) → (\S+) \| (\S+) \| (\d+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \| ([^|]+) \|$", txt, re.M):
        out[int(m.group(1))] = dict(start=m.group(2), end=m.group(3), N=int(m.group(5)), regime=m.group(7),
                                    mode=m.group(9))
    for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M):
        if int(m.group(1)) in out:
            out[int(m.group(1))]["title"] = m.group(2).strip()
    return out


PRED_REP = f"""## Prediction
*Written {STAMP}, before running on this period* (after the card's predictions at 20:15 UTC and amendments A1–A5 at 20:30 UTC; no real-data Price share had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| c1 (P1) | style moves more by migration than content does: s_Mig(style) > s_Mig(content, bge) | s_Mig(style) ≤ s_Mig(content) |
| c2 (P2) | content moves by transmission: s_Trans(content, bge) ≥ 0.5 and the largest term | s_Trans < 0.5 or another term larger |
| c3 (P3) | selection is not a material share: \\|s_Sel\\| ≤ 0.2 for content, style and conventions | \\|s_Sel\\| > 0.2 for any reliable trait |
| P5 | residual R (content) ≥ 0.1 with jackknife CI > 0 | CI includes 0 (migration + kickoff explain the change) |
| P6 | persistence C (content) > 0 with CI > 0 (periods with ≥ 4 transitions) | C ≤ 0 |

**Verdict rule (card, A1):** supported = c1, c2 and c3; failed = none; mixed = otherwise; n/a = not eligible (< 2 transitions with ≥ 3 stayers or < 20 in-cone adoptions by stayers) or content or style reliability ρ_Δ < 0.3. P5 and P6 are reported, not voted here.
"""

NATIVE_TEXT = {
    "NE29": dict(title="Retirement of the longest-serving agent (#31, 2026-02-18 / 02-19)", period="G31", regime="I",
                 why="NE29: Claude Sonnet 4.6 joins on 02-18 and Claude 3.7 Sonnet, the agent present since 2025-04-02, leaves on 02-19, inside goal period #31 with no other roster change. It is the cleanest single-carrier loss in the non-holdout record. Exception (c): the transitions across the two roster events are the object; #30 and #31's other transitions are the placebos.",
                 pred="""- **N1-a:** at each roster-flow transition (into 02-18: one entrant; into 02-19: one leaver), the roster-migration share of style exceeds that of content (cross-fitted, that transition alone).
- **N1-b:** the stayers' content change (Sel + Trans) at the retirement transition is not larger than at the placebo transitions of #30 and #31: cross-fitted |Sel + Trans|² percentile < 0.9.
- Prior 0.5. **Verdict:** supported = N1-a at both transitions and N1-b; failed = neither; mixed otherwise.
- *Counts against:* content migration share ≥ style's at a roster transition; the retirement transition is the largest stayer change in #30–#31."""),
    "NE32": dict(title="Isolated newcomers merge into the village (#51, 2026-07-09 / 07-10)", period="G51", regime="III",
                 why="NE32: GPT-5.6 Sol, Terra and Luna join on 07-09 in separate isolated rooms, which close on 07-10. Isolation switches the newcomers' in-cone parentage from veterans off, then on. Exception (c): the transitions across the join and the merge are the object.",
                 pred="""- **N2-a:** at the newcomers' entry transition (07-08 → 07-09, or their first active day if a newcomer has < 6 eligible messages on 07-09), the roster-migration share of style exceeds that of content.
- **N2-b (enculturation at the merge):** the newcomers' content change from their first active day to the next points toward the veterans' centroid on the first day (cross-fitted cosine > 0), and more so than their style change does.
- Prior 0.45. **Verdict:** supported = N2-a and N2-b; failed = neither; mixed otherwise.
- *Counts against:* content migration share ≥ style's at entry; newcomer content cosine ≤ 0 or ≤ the style cosine."""),
}

PRED_G51 = f"""## Native test: roster growth (#51, non-holdout 07-06 → 09-04, 11 joins)
*Prediction written {STAMP}, before any native statistic.* #51 is the only long period with steady roster growth (11 joins on non-holdout days, no leaves). Over its 44 transitions, "style moves by migration" predicts that the period's net style change is mostly the newcomers.
- **N3-a:** cumulative roster-migration share of style ≥ 0.5.
- **N3-b:** cumulative roster-migration share of content (bge and gte) < that of style.
- **N3-c (reported, not voted):** energy \\|s_Sel\\| ≤ 0.2 for every trait.
- Prior 0.55. **Verdict:** supported = N3-a and N3-b; failed = neither; mixed otherwise.
- *Counts against:* cumulative style roster share < 0.5 and not above content's.

"""


def header(g: int, meta: dict, role: str) -> str:
    m = meta.get(g, {})
    title = m.get("title", f"goal period #{g}")
    return (f"# H89 × G{g:02d}: {title} ({m.get('start', '?')} → {m.get('end', '?')})\n\n"
            f"**Verdict:** pending\n**Role:** {role}\n"
            f"**Period:** regime {m.get('regime', '?')} · mode {m.get('mode', '?')} · {m.get('N', '?')} agents · "
            f"non-holdout days only (held-out days masked with `holdout_mask`).\n\n")


WHY_REP = """## Why this period
Replication layer: the common H89 estimator (cross-fitted Price partition of day-to-day change of the active population's mean trait) on every non-holdout period with H34 ideas, so periods compare as points on a phase diagram.

"""


def predict():
    meta = goal_meta()
    base = HYP / "goalperiod-subhypotheses"
    for g in GOALS:
        d = base / f"G{g:02d}"
        d.mkdir(parents=True, exist_ok=True)
        role = "native" if g in NATIVE_G else "replication"
        txt = header(g, meta, role) + WHY_REP + (PRED_G51 if g in NATIVE_G else "") + PRED_REP + \
            "\n## Result\n*(pending)*\n\n## Scorecard (period-specific axes)\n*(pending)*\n\n## Notes\n- Data: `data/processed/H89-price-equation-culture/traits/G%02d.npz`, `adoptions.parquet`.\n" % g
        (d / "README.md").write_text(txt)
    for ne, t in NATIVE_TEXT.items():
        d = base / ne
        d.mkdir(parents=True, exist_ok=True)
        txt = (f"# H89 × {ne}: {t['title']}\n\n**Verdict:** pending\n**Role:** native\n"
               f"**Period:** inside {t['period']} · regime {t['regime']} · non-holdout days only.\n\n"
               f"## Why this test\n{t['why']}\n\n## Prediction\n*Written {STAMP}, before any native statistic.*\n{t['pred']}\n\n"
               "## Result\n*(pending)*\n\n## Scorecard (period-specific axes)\n*(pending)*\n\n## Notes\n")
        (d / "README.md").write_text(txt)
    print("predictions written")


def _f(x, nd=2):
    try:
        if x is None or (isinstance(x, float) and x != x):
            return "–"
        return f"{x:+.{nd}f}"
    except (TypeError, ValueError):
        return str(x)


def _ci(r, key, nd=2):
    v, se = r.get(key), r.get(f"{key}.se")
    if v is None or se is None or not (se == se):
        return _f(v, nd)
    return f"{v:+.{nd}f} [{v - 1.96 * se:+.{nd}f}, {v + 1.96 * se:+.{nd}f}]"


def result_block(r: dict) -> tuple[str, str]:
    if not r.get("eligible"):
        return "n/a", (f"**n/a.** Not eligible: {r['n_trans']} transitions with ≥ 3 stayers, {r['n_in']} in-cone "
                       f"adoptions by stayers (rule: ≥ 2 and ≥ 20).\n")
    v = r["verdict"]
    rel = r.get("reliable", {})
    lines = [f"**{v}.** {r['n_trans']} day transitions; {r['n_agents']} agents, {r['n_agent_days']} active agent-days; "
             f"{r['n_in']} in-cone adoptions by stayers (mean social weight λ̄ {r['lam_mean']:.2f}, SD of w "
             f"{r['w_sd']:.2f}); {r['n_roster_events']} roster and {r['n_presence_events']} presence entries/exits. "
             f"Reliability ρ_Δ: content {r['content_bge.rho']:.2f}, style {r['style.rho']:.2f}, conventions "
             f"{r['conv.rho']:.2f}" + ("" if all(rel.values()) else f" (unreliable, A1: {', '.join(k for k, x in rel.items() if not x)})") + ".\n",
             "| Prediction | Observed (energy shares; jackknife 95% CI) | Null / reference | Verdict |",
             "| --- | --- | --- | --- |"]
    if v == "n/a":
        return v, "\n".join(lines[:1]) + "\nContent or style change is not reliable here (A1), so the period is n/a.\n"
    c = r.get("criteria", {})
    lines.append(f"| c1 s_Mig(style) > s_Mig(content) | style {_ci(r, 'style.s_mig')}; content {_ci(r, 'content_bge.s_mig')} "
                 f"(implied day-field fraction φ̂: style {r.get('style.phi_hat')}, content {r.get('content_bge.phi_hat')}) | "
                 f"synthetic: s_Mig 0.5 needs φ ≈ 0.01 | {'pass' if c.get('c1') else 'fail'} |")
    lines.append(f"| c2 s_Trans(content) ≥ 0.5, largest | bge {_ci(r, 'content_bge.s_trans')}; gte {_ci(r, 'content_gte.s_trans')}; "
                 f"self / social {_f(r['content_bge.s_trans_self'])} / {_f(r['content_bge.s_trans_social'])} | field-only rival R1 | "
                 f"{'pass' if c.get('c2') else 'fail'} |")
    lines.append(f"| c3 \\|s_Sel\\| ≤ 0.2 | content {_f(r['content_bge.s_sel'], 3)} (p {r['content_bge.perm_p']:.2f}); style "
                 f"{_f(r['style.s_sel'], 3)} (p {r['style.perm_p']:.2f}); conventions {_f(r['conv.s_sel'], 3)} (p "
                 f"{r['conv.perm_p']:.2f}; leave-trait-out {_f(r['conv.lto_s_sel'], 3)}) | w-permutation (A2) | "
                 f"{'pass' if c.get('c3') else 'fail'} |")
    lines.append(f"| P5 residual R ≥ 0.1, CI > 0 | bge {_ci(r, 'content_bge.R')}; gte {_ci(r, 'content_gte.R')}; kickoff share "
                 f"{_f(r['content_bge.s_kick'], 3)} | kill: CI ∋ 0 | reported |")
    lines.append(f"| P6 persistence C > 0 | content {_ci(r, 'content_bge.C')} (drift ratio δ²/s {_f(r.get('content_bge.drift_ratio'))}); "
                 f"style {_f(r.get('style.C'))} | iid topics −0.5 | reported |")
    lines.append(f"| P4 convergence placebo | {r['n_plc']} unread-placebo adoptions; placebo s_Sel {_f(r['content_bge.plc_s_sel'], 3)}, "
                 f"s_Trans,social {_f(r['content_bge.plc_s_trans_social'], 3)} (read: {_f(r['content_bge.s_trans_social'], 3)}) | read vs in flight | descriptive |")
    lines.append(f"\nCumulative (net change over the period, descriptive, A5): s_Mig style {_f(r['style.cum_s_mig'])}, content "
                 f"{_f(r['content_bge.cum_s_mig'])}; s_Sel content {_f(r['content_bge.cum_s_sel'])}. Migration split (energy): "
                 f"style roster {_f(r['style.s_mig_roster'], 3)} / presence {_f(r['style.s_mig_presence'], 3)}.\n")
    return v, "\n".join(lines) + "\n"


def results():
    rep = json.loads((DATA / "replication/replication.json").read_text())["periods"]
    nat = json.loads((DATA / "natives/natives.json").read_text()) if (DATA / "natives/natives.json").exists() else {}
    base = HYP / "goalperiod-subhypotheses"
    for g in GOALS:
        p = base / f"G{g:02d}" / "README.md"
        txt = p.read_text()
        r = rep.get(str(g))
        if r is None:
            continue
        v, block = result_block(r)
        if g == 51 and "N3" in nat:
            n3 = nat["N3"]
            v = n3["verdict"]
            block = n3["text"] + "\n**Replication estimator on #51:**\n\n" + block
        txt = re.sub(r"\*\*Verdict:\*\* \S+", f"**Verdict:** {v}", txt, count=1)
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + block.replace("\\", "\\\\") + "\n## Scorecard",
                     txt, flags=re.S)
        sc = ("C (adequacy): energy shares cross-fitted between message halves (synthetic bias ≤ 0.03 at ρ ≥ 0.3); "
              "selection against the w-permutation null. D (unfitted): the style vs content migration ordering. "
              "E, G: not informed by this replication.")
        if r.get("eligible") and v != "n/a":
            txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes",
                         "## Scorecard (period-specific axes)\n" + sc + "\n\n## Notes", txt, flags=re.S)
        else:
            txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes",
                         "## Scorecard (period-specific axes)\nNot informed (n/a).\n\n## Notes", txt, flags=re.S)
        p.write_text(txt)
    for ne in ("NE29", "NE32"):
        if ne not in nat:
            continue
        p = base / ne / "README.md"
        txt = p.read_text()
        txt = re.sub(r"\*\*Verdict:\*\* \S+", f"**Verdict:** {nat[ne]['verdict']}", txt, count=1)
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + nat[ne]["text"].replace("\\", "\\\\") + "\n## Scorecard",
                     txt, flags=re.S)
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes",
                     "## Scorecard (period-specific axes)\n" + nat[ne]["scorecard"] + "\n\n## Notes", txt, flags=re.S)
        p.write_text(txt)
    print("results written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    if a.predict:
        predict()
    if a.results:
        results()
