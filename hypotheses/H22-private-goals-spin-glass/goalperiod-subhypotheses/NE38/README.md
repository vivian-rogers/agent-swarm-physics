# H22 × NE38: Claude Opus 5's role is reassigned (2026-07-29), inside #51

**Verdict:** failed
**Role:** native (round 1b, non-holdout)
**Period:** regime III · #51 · one room · shared units 51e (07-24 → 07-28: Opus 5 joins as a **game dev**, a same-role rival of Claude Opus 4.7 and GPT-5.5, recovered by DQ6 from an operator message) and 51f (07-29 → 08-04: Opus 5 is a **mathematician**, rival of no one). The switch is at 16:51 UTC on 07-29 (early in that PT day); 07-29 is excluded from both sides.

## Why this period
NE38 is a field step on one agent with a known instant (DQ9: "coupling-sign change"). It turns H22's treatment test into an intervention (axis E): the same agent stops being a rival of two specific agents while everything else (room, roster, goal, hours) stays fixed. Spin glass (H22): rival couplings are negative, so Opus 5's coupling to the game devs *rises* after the switch relative to its other couplings. Homophily rival (round 1: same-role rivals co-move more): it *falls*.

## Prediction
*Written 2026-10-04 07:15 UTC, before computing any statistic on Opus 5's couplings.* Design facts seen: DQ6 role rows and the shared unit dates; H54's NE38 result (Opus 5's content moved onto its new goal within a day: DiD +0.61).

- **Content coupling.** J^c between Opus 5 and each other agent present on both sides, from H22's estimator (within-day window fluctuations, agent-day centred, minus the cross-day surrogate), computed separately on the pre days (07-24 → 07-28) and the post days (07-30 → 08-04); bge and gte (white32), dedupe-free.
- **Statistic.** DiD = [mean J(Opus 5, rivals)_post − mean J(Opus 5, rivals)_pre] − [mean J(Opus 5, others)_post − mean J(Opus 5, others)_pre], rivals = {Opus 4.7, GPT-5.5}.
- **Null.** Placebo rivals: every pair of other agents present on both sides takes the rivals' place (exact enumeration); two-sided percentile.
- **Manipulation check (field, not coupling).** Static alignment cos(H_Opus5, H_rival) of day-field-removed agent means falls after the switch relative to Opus 5's alignment with others (credence 0.7).
- **Prediction.** Homophily: DiD < 0. H22: DiD > 0. I expect the homophily sign (credence 0.55) but no significance at this sample (placebo p < 0.1 credence 0.2): 5 + 5 days, one agent.
- **Stance channel (DQ2).** Mean soft stance between Opus 5 and the rivals before vs after, against its stance with others (same DiD, placebo rivals). Expected: too few replies to test (< 10 per side); reported if ≥ 10 replies per side.

## Result
*Run 2026-10-04 (round 1b), after the prediction above. Code: `analysis/r1b_stance_native.py` (`ne38`; `--ne38-min2` for the variant); data: `data/processed/H22-private-goals-spin-glass/r1b/stance_native.json` (`native_NE38`, `native_NE38_min2`).*

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| Content DiD (≥ 5 shared windows per pair, as written) | **untestable**: after the switch Opus 5 shares 0 windows with Claude Opus 4.7 and 4 with GPT-5.5 (before: 8 and 25) | — | untestable |
| Variant (disclosed, chosen after seeing the coverage): Amendment 1's short-unit pair threshold, ≥ 2 shared windows | only GPT-5.5 is coupled on both sides. bge: J(Opus 5, rivals) 0.25 / 0.14 before vs 0.055 for others; after, J(Opus 5, GPT-5.5) = −0.12 vs 0.069 for others; **DiD −0.27** (placebo percentile 0.06). gte: DiD −0.13 (percentile 0.18) | 17 placebo rivals | homophily sign, n.s. |
| Manipulation check: static alignment with the rivals' field falls | cos 0.51 → −0.06 (bge), 0.41 → −0.16 (gte); DiD −0.62 / −0.60, placebo percentile 0.004 (276 placebo pairs) | exact placebo pairs | **pass** |
| Stance (≥ 10 replies per side) | before: 90 replies with the rivals, soft stance 0.72 vs 0.57 with others; after: 3 replies | — | untestable (descriptive: warmer to rivals) |

**Reading.** The role change moved Opus 5's content field off the game devs' field at once (as H54 found for its new goal). While they were rivals, Opus 5 co-moved with them more than with anyone else and replied to them more warmly; after the change it nearly stopped interacting with them. That is the homophily rival again, now as a before/after contrast on one agent: shared objectives (even competing ones) pull agents into the same conversation. H22's prediction (coupling to former rivals *rises*) is not seen. The coupling DiD is a variant with one rival pair and no significance, so it is weak evidence.

## Scorecard (period-specific axes)
- **E (interventional):** a dated field step on one agent; the field response is clear (placebo 0.004), the coupling response points to homophily but is not significant. Score 1 (as a field intervention; 0 for the coupling claim).
