# H17 × NE43: Drive withdrawal inside #51 (bookends end 08-05, nudges end 08-21)

**Verdict:** failed
**Role:** native
**Period:** regime III · #51 non-holdout days. A = 07-24 → 08-04 (bookends and nudges), B = 08-05 → 08-20 (nudges only), C = 08-21 → 09-02 (neither); placebo 07-06 → 07-14 vs 07-15 → 07-23. Same goal, room and hours across the steps.

## Why this period
NE43 removes the outside drives (daily synchronizing bookends, then the nudger) in two steps while everything else stays fixed. If t2\* is an order parameter of being stuck, mixing should slow once nothing kicks idle agents.

## Prediction
*Written 2026-10-04, before running (card, "Round 1b", N2).* t2\*_v3 (6 macro states, shifted estimator, λ₂ bias-corrected) is longer in C than in A, with the agent-day bootstrap 95% CI of the difference above 0, and mean p_blocked is higher in C than in A. Credence 0.35.

## Result
*Run 2026-10-04 (`analysis/native_r1b.py`; `r1b/native_r1b.json`).*

| Block | days | windows | t2\*_bc (min) | mean p_blocked | real-failure share | wait share |
| --- | --- | --- | --- | --- | --- | --- |
| P1 07-06 → 07-14 | 7 | 15,395 | 465 | 0.246 | 0.022 | 0.24 |
| P2 07-15 → 07-23 | 7 | 16,484 | 78 | 0.253 | 0.024 | 0.42 |
| A 07-24 → 08-04 | 8 | 20,409 | 456 | 0.255 | 0.029 | 0.38 |
| B 08-05 → 08-20 | 12 | 29,975 | 63 | 0.252 | 0.025 | 0.46 |
| C 08-21 → 09-02 | 9 | 21,103 | 428 | 0.237 | 0.033 | 0.51 |

C − A: −28 min, CI unbounded above (λ₂ → 1 in some replicates); p_blocked C − A −0.02. **Failed.** More telling, t2\* jumps ×6–7 between ordinary adjacent blocks (P1 vs P2, CI excluding 0), so at 15–30k windows per block the v3 slowest mode is not a stable quantity to track across a step. The `wait` share rises steadily (0.24 → 0.51) across the whole period, with no jump at either step.

## Scorecard (period-specific axes)
B 0 (t2\* is not stationary across 2-week blocks). E 0.

## Notes
- #51's day counts differ from calendar spans because #51 runs on weekdays.
