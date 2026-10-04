"""Write the H61 replication period READMEs (goalperiod-subhypotheses/G<NN>/README.md).

  --predict   before the real-data run: verdict pending, prediction dated 2026-10-04 19:26 UTC
  --results   after explore.py: fills Result, Scorecard and the verdict (the prediction text is unchanged)
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
DATA = ROOT / "data/processed/H61-contagiousness-at-first-use"
GOALS = [5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40,
         41, 42, 44, 51]
NATIVE = {26, 35}
STAMP = "2026-10-04 19:26 UTC"
NSTAMP = "2026-10-04 19:30 UTC"
NATIVE_PRED = {
    26: f"""## Native test: the elected leader's ideas (DQ6)
*Prediction written {NSTAMP}, before any native statistic.* H34 found that the elected leader (agent 17, DQ6 `leader` term1 from 2026-01-05 19:35:22 UTC) seeds 7.5× more new markers per message and that each spreads less (P(s ≥ 2) ratio 0.36). Ideas seeded during the leader's term (to the end of the non-holdout period) by the leader vs by the other agents; logistic model for Y without poster terms.
- **N26-a (raw):** the leader's unadjusted odds ratio for Y is < 1 (expected 0.3–0.5).
- **N26-b (features explain it):** adjusted for class, focus, seed length, specificity, receptive fraction, addressed, threaded, kickoff day and room size, the leader OR rises to ≥ 0.7, or its 95% CI includes 1. **Counts against:** adjusted OR ≤ 0.5 with upper CI < 0.7 (authority, or something else about the leader, lowers fitness beyond the seed features).
- Credence 0.45. Verdict: supported = N26-a and N26-b pass; failed = N26-b fails; mixed = otherwise.
""",
    35: f"""## Native test: designated lead designers (DQ6)
*Prediction written {NSTAMP}, before any native statistic.* DQ6 names two lead designers per day on 2026-03-16 to 03-18 (6 agent-days). Ideas seeded by an agent on its lead day vs ideas seeded on the same days by others. Two models: features without poster terms, and features + poster terms (the role effect within agent).
- **N35-a (raw):** unadjusted OR for Y of lead-day seeds vs others: 95% CI includes 1 (H34: 1.11 [0.82, 1.45]).
- **N35-b (role adds nothing beyond features and identity):** with features + poster terms, the lead-day OR has a 95% CI that includes 1. **Counts against:** OR > 1.5 with lower CI > 1.
- Credence 0.6. Verdict: supported = N35-b passes; failed = N35-b fails; mixed = N35-b passes but N35-a fails.
""",
}
NE42_PRED = f"""## Prediction
*Written {NSTAMP}, before any native statistic.* NE42: #best and #rest merge into one room on 2026-05-04 (#40) and split back to the same partition on 05-11 (#41), at a fixed roster (#39 → #40 → #41). The merge raises the number of agents present per room (H34 N_room 11 → 14 → 11). The goal changes too (#40 is a shared objective), which confounds the merge.
Model F⁺ = F with the receptive *count* log(1 + n_receptive) and log room size in place of the receptive fraction (counts transfer across room sizes; fractions do not).
- **N42-a (transfer):** F⁺ fitted on all of #39 forecasts #40 better than B3 fitted on #39 (ΔLL > 0, idea-cluster CI > 0), and F⁺ fitted on #40 forecasts #41 better than B3 fitted on #40.
- **N42-b (calibration):** the #39 F⁺ model's mean predicted P(Y) for #40 is closer to #40's observed rate than B3's (B3 has no room-size or receptive term).
- **N42-c (stable sign):** the receptive-count coefficient, fitted separately in #39, #40 and #41, is > 0 in all three.
- Credence 0.4 (the goal change and small rate shifts, about +13% from H34's N^0.45 scaling, limit power). Verdict: supported = N42-a and N42-b pass; failed = N42-a fails in both transfers; mixed = otherwise.
"""


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


PRED = f"""## Prediction
*Written {STAMP}, before running on this period* (after the card's predictions at 19:15 UTC and synthetic amendment A1; first written 19:26, rewritten with the native sections at 19:30 UTC; no H61 feature–outcome statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | Seed features forecast spread beyond the strongest baseline: ΔLL(F − B4) > 0 with lower 95% CI > 0 (B4 = class + poster + kickoff day + room size; A1) | CI includes 0 or ΔLL ≤ 0 |
| P2 | AUC of F for "reaches a second agent within 24 h" exceeds the class-only AUC | AUC_F ≤ AUC_B1 |
| P3 | Focus (log novel items in the seed message) < 0; poster reply in-degree CI includes 0; receptive fraction > 0 | focus ≥ 0 with CI; in-degree CI > 0 |
| P4 | Top-decile lift for Y ≥ 2 | lift < 1.5 |
| P5 | If ≥ 15 read-5 and ≥ 15 unread-5 events: the F − B1 AUC gain is larger for read-5 than for unread-5 adoption | gain for unread-5 ≥ gain for read-5 |

**Verdict rule (card, with A1):** supported = ΔLL(F − B4) lower 95% CI > 0 and top-decile lift for Y ≥ 1.5; failed = ΔLL(F − B4) ≤ 0; mixed = otherwise; n/a = < 300 test ideas or < 20 positive test ideas.
"""


def fmt(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


def card(g: int, meta: dict, r: dict | None, natives: dict | None = None) -> str:
    m = meta.get(g, {})
    role = "native (with the replication estimator)" if g in NATIVE else "replication"
    nat = (natives or {}).get(f"G{g:02d}")
    verdict = (nat["verdict"] if nat else "pending") if g in NATIVE else (r["verdict"] if r else "pending")
    head = (f"# H61 × G{g:02d}: {m.get('title', f'goal #{g}')} ({m.get('start', '?')} → {m.get('end', '?')})\n\n"
            f"**Verdict:** {verdict}\n**Role:** {role}\n"
            f"**Period:** regime {m.get('regime', '?')} · mode {m.get('mode', '?')} · {m.get('N', '?')} agents · "
            f"non-holdout days only (held-out days masked with `holdout_mask`).\n")
    why = ("\n## Why this period\nReplication layer: the common H61 estimator (forward-chained fitness model of idea "
           "spread at first use) on every period H34 analysed, so periods compare as points on a phase diagram."
           + (" This period also hosts a native test (section below), with its own dated prediction." if g in NATIVE else "")
           + "\n\n")
    res = "## Result\n(pending: run `analysis/explore.py`)\n"
    sc = "## Scorecard (period-specific axes)\n(pending)\n"
    if r:
        if not r.get("eligible"):
            res = (f"## Result\n**n/a.** {r.get('n_test', 0)} test ideas, {r.get('n_pos', 0)} that reached a second agent "
                   f"(eligibility: ≥ 300 and ≥ 20).\n")
            sc = "## Scorecard (period-specific axes)\nNot informative (ineligible).\n"
        else:
            c = r["coef"]
            cv = r.get("conv", {})
            p5 = (f"G_read {fmt(cv['g_read'], 3)} vs G_unread {fmt(cv['g_unread'], 3)}; difference "
                  f"{fmt(cv['diff'], 3)} [{fmt(cv['diff_lo'], 3)}, {fmt(cv['diff_hi'], 3)}]"
                  if cv.get("eligible") else f"not testable ({cv.get('n_read5', 0)} read-5, {cv.get('n_unread5', 0)} unread-5 events)")
            def co(f):
                b, s = c[f]
                return f"{b:+.2f} [{b - 1.96 * s:+.2f}, {b + 1.96 * s:+.2f}]"
            res = (f"## Result\n**{verdict}.** {r['n_ideas']} agent-seeded ideas (uncensored), {r['n_test']} on "
                   f"{r['n_days_test']} forward-chained test days; {r['n_pos']} test ideas reached a second agent within 24 h "
                   f"(base rate {r['base']:.3f}).\n\n"
                   "| Prediction | Observed | Reference | Verdict |\n| --- | --- | --- | --- |\n"
                   f"| P1 ΔLL(F − B4) > 0, CI > 0 | {fmt(r['dll_F_B4'])} [{fmt(r['dll_F_B4_lo'])}, {fmt(r['dll_F_B4_hi'])}] millinats/idea; "
                   f"vs B3 {fmt(r['dll_F_B3'])} [{fmt(r['dll_F_B3_lo'])}, {fmt(r['dll_F_B3_hi'])}]; gte specificity "
                   f"{fmt(r.get('dll_F_B4_gte'))} [{fmt(r.get('dll_F_B4_gte_lo'))}, {fmt(r.get('dll_F_B4_gte_hi'))}] | synthetic null size 0.07 | "
                   f"{'pass' if r['dll_F_B4_lo'] > 0 else 'fail'} |\n"
                   f"| P2 AUC_F > AUC_B1 | F {fmt(r['auc_F'], 3)}, B1 {fmt(r['auc_B1'], 3)}, B2 {fmt(r['auc_B2'], 3)}, B4 {fmt(r['auc_B4'], 3)}; "
                   f"Spearman ρ with reach F {fmt(r['rho_F'], 3)} vs B1 {fmt(r['rho_B1'], 3)} | class only | "
                   f"{'pass' if r['auc_F'] > r['auc_B1'] else 'fail'} |\n"
                   f"| P3 focus < 0; in-degree CI ∋ 0; receptive > 0 | focus {co('lg_novel')}; in-degree {co('indeg')}; "
                   f"receptive {co('f_rec')}; specificity {co('spec')}; length {co('lg_len')}; addressed {co('addressed')}; "
                   f"threaded {co('threaded')} (standardised log-odds, in-sample) | 0 | descriptive |\n"
                   f"| P4 top-decile lift for Y ≥ 2 | {fmt(r['lift_y'])} (Y3: {fmt(r['lift_y3'])}) | 1 | "
                   f"{'pass' if r['lift_y'] >= 2 else 'fail'} |\n"
                   f"| P5 G_read > G_unread | {p5} | synthetic: centred on 0 (SD 0.03) | "
                   f"{('pass' if cv['diff'] > 0 else 'fail') if cv.get('eligible') else 'n/a'} |\n\n"
                   f"Data: `data/processed/H61-contagiousness-at-first-use/G{g:02d}/` (`ideas.parquet`, `pred_y.parquet`); "
                   f"numbers from `analysis/explore.py` → `results/periods.json`.\n")
            sc = ("## Scorecard (period-specific axes)\n"
                  f"C (adequacy): F vs the strongest baseline B4 on held-out days, ΔLL {fmt(r['dll_F_B4'])} "
                  f"[{fmt(r['dll_F_B4_lo'])}, {fmt(r['dll_F_B4_hi'])}]. D (unfitted): held-out ranking, AUC {fmt(r['auc_F'], 3)}, "
                  f"lift {fmt(r['lift_y'])}. H (rivals): class-only AUC {fmt(r['auc_B1'], 3)}, poster-only {fmt(r['auc_B2'], 3)}. "
                  "E, G: not informed by this replication.\n")
    notes = "\n## Notes\n- Ideas whose 24-h window runs past the last non-holdout agent message are dropped (censoring).\n"
    nblock = ""
    if g in NATIVE:
        nblock = NATIVE_PRED[g] + "\n" + (nat["text"] if nat else "(native result pending: run `analysis/natives.py`)\n") + "\n"
        res = res.replace("## Result", "## Result (replication estimator)") + (
            f"\nReplication verdict for this period: **{r['verdict']}**.\n" if r else "")
    return head + why + nblock + PRED + "\n" + res + "\n" + sc + notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    meta = goal_meta()
    rows = {}
    natives = {}
    if a.results:
        rows = {r["goal"]: r for r in json.loads((DATA / "results/periods.json").read_text())}
        npath = DATA / "results/natives.json"
        natives = json.loads(npath.read_text()) if npath.exists() else {}
    for g in GOALS:
        d = HYP / f"goalperiod-subhypotheses/G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(card(g, meta, rows.get(g), natives))
    d = HYP / "goalperiod-subhypotheses/NE42"
    (d / "figures").mkdir(parents=True, exist_ok=True)
    nat = natives.get("NE42")
    (d / "README.md").write_text(
        "# H61 × NE42: rooms merged then split at a fixed roster (#39 → #40 → #41; 2026-05-04 / 2026-05-11)\n\n"
        f"**Verdict:** {nat['verdict'] if nat else 'pending'}\n**Role:** native\n"
        "**Period:** #39 (two rooms), #40 (merged, regime III, mode C), #41 (split back); 15 agents; non-holdout days. "
        "Exception (c) of CLAUDE.md: the transition is the object, so models fitted in one week are scored in the next.\n\n"
        "## Why this period\nThe only A-B-A change of room size at a fixed roster: an intervention on the receptive count "
        "(axis E).\n\n" + NE42_PRED + "\n## Result\n" + (nat["text"] if nat else "(pending: run `analysis/natives.py`)\n"))
    print(f"wrote {len(GOALS)} period READMEs ({'results' if a.results else 'predictions'})")


if __name__ == "__main__":
    main()
