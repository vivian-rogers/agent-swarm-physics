# H38 × NE43: the operator's daily bookends stop (2026-08-05) and the nudger stops (2026-08-21), inside #51

**Verdict:** failed
**Role:** native (round 1b, non-holdout; transition exception c)
**Period:** #51 head, non-holdout days only (2026-07-06 → 2026-09-04; the #51 tail from 09-07 is held out). Three windows: **A** = 07-06 → 08-04 (daily pause/resume bookends and nudges), **B** = 08-05 → 08-20 (no bookends, nudges continue), **C** = 08-21 → 09-04 (neither). Regime III, one room (#general) plus the self-selected #focus room from 08-05.

## Why this period
H38's regime-III claim is that most collective co-activation is "agents starting and stopping together at the operator's daily resume and pause". NE43 is two steps (DQ9; `infra/README.md` Known issues): the `automated` speaker's daily "pausing / resuming the village" messages end after 2026-08-04 PT, two weeks before the nudges end (08-20). The bookend stop is the one intervention in the non-holdout record that removes the operator's start/stop *announcement* while everything else about the day (roster, goal, room, hours) stays put, so it separates two readings of the day-edge mechanism:
- **message-as-kick:** the resume message is a common field that wakes every agent at once (and the pause message stops them); then day-edge synchrony should fall at 08-05;
- **runner schedule:** the scaffold starts and stops every agent's loop at the scheduled times whether or not a message is posted; then nothing changes at 08-05. Design fact checked before writing this (calendar only): every #51 day before and after 08-05 has the same run window, starting 16:00–16:02 UTC and lasting 8.0–8.2 h (except the gap days 07-07, 07-10, 07-28).
08-21 (nudges end) is a placebo step for the day-edge component: nudges are aimed at idle agents during the day, not at day edges.

## Prediction
*Written 2026-10-04 06:31 UTC, before computing any statistic on these windows with the corrected data. Seen before writing: the round-1 G51 result (whole-period f_scaffold 0.14, edge-only f 0.36, on the old tables), the calendar windows above and the DQ9 dates of the two steps; no per-day gain, start time or joint-silence count for #51 under the fixed tables.*

Per day d (day-present population: agents with ≥ 30 active minutes that day), on `activity_bins_fixed` and `outages_fixed`:
- E_raw(d): excess equal-time gain over the N1 block-shift null on the whole day window (round-1 estimator);
- E_edge(d): the same after day-edge conditioning (`mask_edge`: scheduled minutes dropped, not-started / finished agent-minutes imputed);
- **D_edge(d) = E_raw(d) − E_edge(d)**, the day-edge share of the excess (the observable of the mechanism);
- start spread s₀(d): SD across agents of the first active minute after the window start; end spread s₁(d): SD of the last active minute.

Predictions (window means over days, one-sided permutation test over days, 10,000 permutations):
- **N1a (message-as-kick, H38 as worded in the card).** D_edge falls at the bookend stop: mean D_edge(B) < mean D_edge(A), p < 0.05; and the start spread widens: mean s₀(B) > mean s₀(A), p < 0.05.
- **N1b (placebo step).** At the nudger stop the day-edge component does not move: |mean D_edge(C) − mean D_edge(B)| < |mean D_edge(B) − mean D_edge(A)|, and p(C ≠ B) ≥ 0.05.
- **Rival (runner schedule).** D_edge and s₀ unchanged at 08-05 (p ≥ 0.05 both).
- Credence: N1a 0.3 (the run window did not move, so I expect the runner to keep starting agents together); N1b 0.7.
- **Verdict rule:** supported if N1a and N1b hold; failed if neither D_edge nor s₀ moves at 08-05 in the predicted direction (p ≥ 0.05 for both); mixed otherwise.
- Confounds (stated before the run): the #focus room opens on 08-05 (a second, self-selected room); roster joins happen inside A and C (NE32 07-09, NE33 09-03); the day-level estimates have a few hundred minutes each.

## Result
*Run 2026-10-04 06:40 UTC (`analysis/r1b_native.py`; per-day values in `data/processed/H38-platform-stalls/r1b/native/ne43_days.parquet`). 45 non-holdout days; day-present population N = 20–31; 200 joint N1 surrogates per day; 10,000 permutations over days.*

| Window | days | mean D_edge | mean E_raw | mean E_mask_edge | median E_trim (DQ8) | start spread s₀, mean / median (min) | end spread s₁, mean (min) | scheduled share of minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A (bookends + nudges) | 22 | 0.189 | 0.330 | 0.141 | 0.048 | 15.3 / 1.5 | 16.9 | 0.061 |
| B (nudges only) | 12 | 0.135 | 0.284 | 0.149 | 0.081 | 3.8 / 2.3 | 6.2 | 0.000 |
| C (no operator drive) | 11 | 0.164 | 0.287 | 0.124 | 0.109 | 26.5 / 8.2 | 12.6 | 0.001 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N1a D_edge falls at 08-05 (B < A, p < 0.05) | −0.054, p = 0.080 | ✗ |
| N1a start spread widens at 08-05 (B > A, p < 0.05) | −11.5 min (narrower), p = 0.85 | ✗ |
| N1b no D_edge step at 08-21 smaller than at 08-05, p ≥ 0.05 | +0.029 (vs 0.054), p = 0.34 | ✓ |
| Rival (runner schedule): nothing moves at 08-05 | D_edge p = 0.080, s₀ p = 0.85; E_raw p = 0.35, E_trim p = 0.64 | ✓ |

**Verdict: failed** by the pre-registered rule (neither D_edge nor the start spread moves at 08-05 at p < 0.05). The day-edge share of #51's co-activation does not depend on the operator's pause/resume *messages*: the runner keeps starting and stopping every agent at 16:00 and ~00:05 UTC, and agents start together with or without the announcement. H38's mechanism should read "the runner's daily start and stop", not "the operator's resume and pause messages". The `scheduled` mask, which is built from those messages, is empty after 08-05 (scheduled share 0.061 → 0.000), so on days without bookends only the agent-level edge conditioning (`mask_edge`, `trim`) catches the day edges.

**Post hoc (labelled; not verdict-bearing).** The start spread widens at the *nudger* stop instead: mean s₀ 3.8 → 26.5 min (C vs B, permutation p = 0.010; medians 2.3 → 8.2 min), while D_edge does not follow (p = 0.34). Reading: the nudger, not the bookends, was waking idle agents at the start of the day; when it stops, some agents start late, but the co-activation excess within the common window is unchanged. Confounded with NE33 (joins 09-03/04) and calendar time.

## Scorecard (period-specific axes)
- **E (interventional):** the bookend stop is a clean drive withdrawal at fixed roster, goal, room and hours; the day-edge component did not move (0.189 → 0.135, p = 0.08), so the message-as-kick reading fails and the runner-schedule reading stands. Round-1b score for the day-edge mechanism: the *edge* part survives (trimming still removes it), the *operator-message* part does not.
- **B (assumptions):** the `scheduled` flag depends on the operator messages and silently empties when they stop; agent-level trimming does not.

## Notes
- 2026-10-04: folder created with the prediction before the run (round 1b; DQ9 native test for H38).
- 2026-10-04: run on the corrected tables; one day (07-09, NE32 isolated newcomers) has no trimmed estimate (too few all-present minutes).
- 2026-10-04: cross-hypothesis (H50, from `call_windows`): after 08-04 agents still start within ~22 s of each other and the day-start step keeps its size, so the scaffold starts the agents, not the message; same conclusion as this test, from a different table.
