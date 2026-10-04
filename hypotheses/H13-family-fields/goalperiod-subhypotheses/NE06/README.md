# H13 × NE06: Google-specific scaffold change inside #20 Substack blogs (2025-11-17 → 11-28)

**Verdict:** failed
**Role:** native (round 1b, non-holdout)
**Period:** regime I · mode I (individual blogs) · 8 → 10 agents · one room (#general) · 10 days. Units (shared `period_units`): 20a 11-17 → 11-18, 20b 11-19 (Gemini 3 Pro joins), 20c 11-20 → 11-24 (NE06 step 1: Gemini one tool call per turn, 11-20/21), 20d 11-25 → 11-28 (NE06 step 2: chain of thought added; Claude Opus 4.5 joins). Google agents: Gemini 2.5 Pro (all days) and Gemini 3 Pro (from 11-19).

## Why this period
DQ9's cross-index lists NE06 as H13's family-specific intervention: a scaffold change that hit one family only. If the behavioral family field (HH267, card Amendment 2) is partly harness rather than model disposition, Google's behavior profile should move relative to the other families' across the step, while the other families' fields stay put. It is the only non-holdout family-specific step (NE20, Anthropic, is held out; NE05 is a single-agent case). DQ9's caveat: the CHANGELOG lists all-agent system-prompt changes on the same days (11-20/21), so the difference-in-differences removes only the common part of that change.

## Prediction
*Written 2026-10-04 07:13 UTC, before computing any behavioral or content statistic on #20.* Design facts seen: roster, join dates, numbers of labelled windows per agent (136–460).

- **Observable.** The agent-day behavior state of card Amendment 2 (11 Jev state probabilities + 4 rates; z-scored within #20). For each agent, Δ_i = mean over 11-20 → 11-24 minus mean over 11-17 → 11-19 (step 1 only; step 2 days excluded). DiD vector D = mean Δ(Google) − mean Δ(others); statistic |D| (Euclidean norm).
- **Manipulation check.** Actions per turn (`n_actions / n_turns` per active window): Google's drops relative to others across 11-20 (one tool call per turn). Credence 0.6 (regime-I turn logging may not resolve parallel tool calls).
- **Null.** Relabel which agents are "treated": every choice of 2 agents among those present on both sides (exact enumeration), |D| percentile. A placebo date (11-19 → 11-20 replaced by 11-18 → 11-19, Gemini 3 Pro excluded) is reported descriptively.
- **Prediction.** |D| above the 90th percentile of the relabeling null (one-sided). Credence 0.35: only two treated agents, 3 pre days (1 for Gemini 3 Pro), and a confounded all-agent change.
- **Reading.** A pass says part of the behavioral family field is scaffold-borne (axis E for H13's field); a fail says nothing either way at this power.
- **Content channel, descriptive:** the same DiD on day-demeaned content (bge and gte, white32), to see whether a harness change moves words too.

## Result
*Run 2026-10-04 (round 1b), after the prediction above. Code: `analysis/r1b_behavior.py` (`ne06`); data: `data/processed/H13-family-fields/r1b/behavior.json` (`native_NE06`).* Nine agents are present on both sides of 11-20 (step 1); 36 ways to label two of them "treated".

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| Google's behavior profile moves more than any other pair's across step 1 (\|D\| ≥ 90th percentile) | \|D\| = 2.83 (z-units over 15 features), percentile 0.69 | exact relabeling of the 2 treated agents (36) | **fail** |
| Manipulation check: Google's actions per turn drop relative to others | Google 3.56 / 2.85 → 1.82 / 1.86 (Gemini 2.5 Pro / 3 Pro); **all other agents 3.63 → 1.80**; DiD +0.46 (Google dropped *less*), p_lower 0.94 | same relabeling | **fail** |
| Placebo date (11-17/18 → 11-19, Gemini 3 Pro excluded), descriptive | \|D\| = 4.17, percentile 0.88 (8 relabelings): a day-to-day change of this size is ordinary | — | descriptive |
| Content channel, descriptive | day-demeaned content DiD percentile 0.44 (bge), 0.33 (gte) | same relabeling | no shift |

**Reading.** No Google-specific change in behavior or words across NE06 step 1. The intended manipulation is not visible as a Google-only change in the logs: actions per turn halved for *every* agent on 11-20, consistent with DQ9's caveat that the CHANGELOG lists all-agent prompt and tool changes on the same days. So NE06 cannot serve as a family-specific intervention on the behavioral field; the test is uninformative about whether the field is harness-borne. **Data note for the NE catalog:** in the action logs the one-call-per-turn change at NE06 looks village-wide, not Google-only.

## Scorecard (period-specific axes)
- **E (interventional):** attempted; the step is not family-specific in the data, so no intervention on the family field was available. Score 0.
