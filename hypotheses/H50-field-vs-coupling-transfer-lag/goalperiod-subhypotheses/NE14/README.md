# H50 × NE14: Regime I (sessions, chat mode) vs regime III (always-on computer use) (regime I units #2–#31 vs regime III units #36b–#51 (non-holdout); the boundary bundle NE14 lies between)

**Verdict:** mixed (HH167's premise and regime split rejected; gated talk coupling present in both regimes)
**Role:** native
**Period:** regime I units #2–#31 vs regime III units #36b–#51 (non-holdout); the boundary bundle NE14 lies between.

## Why this period
HH167's premise: regime-I waits are message-triggered, so co-movement there should be coupling; regime III follows inputs at once (field). DQ1 reports that regime-I chat-mode calls are scheduled (median cadence 74 s; 45% with no new message), which contradicts the premise. Exception (c) of the unit rule: the comparison of the two sides of a boundary is the object; each unit stays a separate estimate.

## Prediction
*Written 2026-10-04 07:00 UTC, before running this test.*
- P-R1 (premise check): after a room message arrives while the recipient is idle (in-flight call is a wait or pause), the share of next calls that start within 30 s is ≤ 1.2× the placebo share in regime I (scheduled chat calls) and in regime III (timer pauses). If > 1.5× in regime I, the premise holds.
- P-R2: activity field excess (full window) higher in regime III than regime I (difference of unit medians ≥ 0.15).
- P-R3: talk read-out jump J₁ > 0 in both regimes (≥ 60% of units each); κ (talk) higher in regime I.
- *Against HH167 as posed:* P-R1 fails (calls not message-triggered) or P-R3's κ ordering reverses.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/NE14/native.json`. Figure: [`figures/NE14_regimes.pdf`](figures/NE14_regimes.pdf). Units: regime I 41, II 3, III 27 (each unit its own estimate; regime summaries are medians).

| prediction | observed | verdict |
| --- | --- | --- |
| P-R1: regime-I calls not message-triggered (ratio ≤ 1.2) | chat-mode 1.050 [1.039, 1.062], wait 1.070 [1.053, 1.095] (n = 47,190); regime-III pauses 0.992 [0.977, 1.008] | yes: HH167's premise fails |
| P-R2: activity field excess III − I ≥ 0.15 | medians I 0.51, III 0.55; difference 0.03 (Mann–Whitney p 0.10) | no |
| P-R3: talk J₁ > 0 in ≥ 60% of units in both regimes | I 27/41, III 17/27; no unit < 0 | yes |
| P-R3: κ (talk) higher in regime I | medians I 0.87, III 1.02 (p 0.15) | no |

**Reading.** HH167's regime split does not hold. Regime-I calls are not message-triggered: a message arriving while an agent waits shortens the wait by a few percent at most (DQ1: chat-mode calls are scheduled). Both regimes look the same in kind: activity co-movement is a schedule field (field excess ≈ 0.5 in both), and talk carries a gated coupling with a step at hop 1. What differs is the shape of the coupling. Regime III's response decays at hop 2 (J₂ < 0 in 8/27 units), and regime I's keeps rising (J₂ > 0 in 13/41, kernel at hop 6 > 0 in 22/41). Regime-I coupling is also larger per message (pooled J₁ 0.034 vs 0.019), but smaller relative to the base talk rate (+25% vs +44%).

## Scorecard (period-specific axes)
(pending)

## Notes
