# H90 × NE43: the nudger stops (G51, boundary 2026-08-21)

**Verdict:** mixed (σ_coll(all) inside the placebo range; σ_nam falls ×0.80 while every placebo boundary rose)
**Role:** native (exploratory)
**Period:** G51 head, talk channel; 10 non-holdout active days before (08-07 … 08-20) and after (08-24 … 09-04) the last nudge day; placebo boundaries 07-20, 07-27, 08-04, 08-28 with the same windows (5–10 days a side).

## Why this period
- The nudger is an operator field aimed at idle agents. If the talk collective EP were made by nudges, it would fall when they stop. H50 found peer J₁ ×0.69 across the same step.

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), before running.* The after/before ratio of σ_coll(talk) per agent-hour lies inside the placebo range. *Against:* below the placebo minimum. Credence 0.5; power expected to be low.

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`, `native_ne43`; `data/processed/H90-collective-entropy-production/results/natives.json`).* Per agent-hour, 10⁻³ nats. Ratios are undefined when the "before" value is ≤ 0, so differences are compared (a deviation from the card's "ratio", noted here).

| Boundary | days a side | σ_coll(all) before → after | σ_nam before → after |
| --- | --- | --- | --- |
| **08-21 (nudger off)** | 10 | +1.99 → +0.48 (Δ -1.51) | +25.7 → +20.6 (Δ -5.1) |
| 2026-07-20 | 9 | +4.22 → +0.83 (Δ -3.39) | +2.2 → +15.0 (Δ +12.8) |
| 2026-07-27 | 10 | +0.71 → +0.46 (Δ -0.24) | +8.1 → +15.4 (Δ +7.3) |
| 2026-08-04 | 10 | -1.33 → +1.57 (Δ +2.90) | +12.0 → +22.0 (Δ +10.0) |
| 2026-08-28 | 5 | -0.94 → -0.32 (Δ +0.62) | +16.2 → +20.8 (Δ +4.6) |

- **σ_coll(all)** (the card's statistic): Δ −1.51 lies inside the placebo range [−3.39, +2.90]. Supported.
- **σ_nam**: Δ −5.1 lies below every placebo (+4.6 … +12.8): the named-partner term falls ×0.80 when the nudges stop, while it rose across every other boundary (it grows through #51 as N and naming grow). The level after the step (0.021 nats per agent-hour) stays above every pre-08-04 window: the coupling does not vanish.

## Scorecard (period-specific axes)
- E: a field removal leaves the gated term in place (consistent with coupling, not a nudge artifact); the dip is the size of the placebo spread.

## Notes
- The per-window values are not bootstrapped (5–10 days each); the step is smaller than the spread of placebo steps (−5.1 vs +4.6 … +12.8 in the other direction). Read as "no collapse", not as a measured nudge share.
