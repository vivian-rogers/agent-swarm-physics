# H39 × NE43: the operator's drive winds down in two steps inside #51 (bookends end after 08-04, nudges after 08-20)

**Verdict:** mixed
**Role:** native (round 1b, non-holdout; step test, transition exception c)
**Period:** #51 head (regime III, 8-h days, non-holdout days only). Step S1 (bookends off): pre 07-29, 07-30, 07-31, 08-03, 08-04 vs post 08-05, 08-06, 08-07, 08-10, 08-11. Step S2 (nudger off): pre 08-14, 08-17, 08-18, 08-19, 08-20 vs post 08-21, 08-24, 08-25, 08-26, 08-27 (09-03/04 NE33 excluded). Also the 2 + 2 shape used by round 1's post hoc P9.

## Why this test
Round 1 tested the nudger switch-off post hoc (P9: neither, leaning catalytic) on a single step dated 08-21. DQ9 then showed NE43 is two steps: the daily pause/resume bookends stop two weeks before the nudges. The two steps remove two different levers at fixed goal, room and hours: a schedule announcement (S1) and a targeted unsticking lever (S2). H39's question (does removing a lever change rates, occupancies or both?) gets two quasi-interventions in one period, and the second state space (Jev v3.1, V4) can check that the answer is not an artifact of the minute grid.

## Prediction
*Written 2026-10-04 07:31 UTC, before computing any round-1b step statistic. Seen before writing: round-1 P9 (08-21 step on B4, 2 + 2 and 5 + 5: neither; idle escape −12 to −14%, lowest of 20 placebos for K); H38 round 1b and H50 (agents start together after the bookends stop: the runner, not the message, starts them); the dates above.*

Statistics per step and state family (B4 minute grid; V4 soft 5-min Jev states): φ (field), K (catalysis at fixed occupancy), Δπ, idle (B4) / wait (V4) escape log ratio; judged against every within-#51 day boundary of the same shape outside the tested windows (placebo percentiles; the card's step rule: field if φ > placebo p95 and φ_exc ≥ 0.10; catalyst if K outside [p2.5, p97.5] and |K| ≥ 0.10).
- **N1 (S1, bookends off):** neither in both B4 and V4. The announcement is not a lever; the runner's schedule is.
- **N2 (S2, nudger off):** no field (Δπ_idle / Δπ_wait inside the placebo band, class not "field") but idle / wait escape at or below the placebo 25th percentile in both state families (a catalytic loss, as round 1 leaned).
- **Verdict rule:** supported if N1 and N2 hold in both state families; failed if S1 is a field or catalyst beyond the band in both families, or S2's escape percentile is ≥ 50 in both; mixed otherwise. Confounds named in advance: the #focus room opens on 08-05 (S1), the room change and joins around 08-24 (S2), roster growth throughout.

## Result
*Run 2026-10-04 ~08:40 UTC (`analysis/r1b_native.py`; `data/processed/H39-catalysts-vs-fields/r1b/steps_native.json`).*

| Step (shape) | B4 | V4 (v3 states) | placebos |
| --- | --- | --- | --- |
| bookends off (08-05) (5x5) | neither · K +0.004 (pct 0) · φ pct 0 · Δπ idle/wait +0.005 (pct 12) · escape idle/wait +0.105 (pct 88) | both · K +0.296 (pct 100) · φ pct 100 · Δπ idle/wait +0.157 (pct 100) · escape idle/wait +0.064 (pct 100) | 8 |
| nudger off (08-21) (5x5) | neither · K -0.082 (pct 0) · φ pct 0 · Δπ idle/wait -0.005 (pct 12) · escape idle/wait -0.135 (pct 12) | catalyst · K -0.131 (pct 0) · φ pct 50 · Δπ idle/wait +0.102 (pct 62) · escape idle/wait -0.337 (pct 0) | 8 |
| bookends off (08-05) (2x2) | neither · K -0.032 (pct 29) · φ pct 43 · Δπ idle/wait +0.013 (pct 57) · escape idle/wait +0.068 (pct 64) | catalyst · K +0.263 (pct 100) · φ pct 89 · Δπ idle/wait +0.187 (pct 96) · escape idle/wait -0.051 (pct 43) | 28 |
| nudger off (08-21) (2x2) | neither · K -0.049 (pct 21) · φ pct 36 · Δπ idle/wait +0.025 (pct 64) · escape idle/wait -0.122 (pct 25) | catalyst · K -0.191 (pct 4) · φ pct 71 · Δπ idle/wait +0.147 (pct 89) · escape idle/wait -0.560 (pct 0) | 28 |

- **N1 (S1 neither):** B4 ✓ (both shapes); V4 ✗ (5+5: both; 2+2: catalyst): after 08-05 agents spend more 5-min windows waiting/monitoring and switch more, on the day the self-selected #focus room opens.
- **N2 (S2: no field, escape ≤ 25th pct):** B4 ✓ (escape 12.5th / 25th pct, idle share inside the band); V4 ✓ (wait escape 0th pct both shapes, wait share inside the band; class catalyst, K −0.13 / −0.19).
- **Verdict: mixed.** The nudger stop is a catalytic loss in both state spaces (round 1's lean confirmed). The bookend stop is neutral on the minute grid (agrees with H38/H50: the runner starts agents) but not on the v3 states, where it coincides with the #focus room. Only 8 same-shape placebos for 5+5.
