# H125 × G20: Substack blogs (step at 2025-11-17 18:00 UTC)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime I · mode I · 8 incumbents · 1 room(s) · 10 non-holdout days analysed from day 1. The step response is the object (exception (c)).

## Why this period
One eligible kickoff (shared kickoff, ≥ 5 non-holdout days in one regime). Common estimator, templated rule.

## Prediction
*Written 2026-10-04 22:16 UTC (card) and copied here 2026-10-04 before any run on this period.*
Templated from the card (written 2026-10-04 22:16 UTC, before any real-data statistic), labelled as such. After the step at t₀ the within-agent excess alignment along k̂ overshoots on day 1 (E₁ > 0, H97/H54) and, under HH366's inertia, swings below its days 4–5 level on days 2–3: undershoot U > 0. Rule: supported if U > 0 with jackknife 90% CI above 0 and U above the 95th percentile of the pooled placebo-day U (bge, white32); failed if U ≤ 0; mixed otherwise; descriptive if fewer than 4 agents have both day pairs. The card's credence for an undershoot is 0.2, so the expected verdict here is failed or mixed.

## Result
| Statistic | bge_white | gte_white | bge_style | gte_style | bge_dedupe | gte_dedupe |
| --- | --- | --- | --- | --- | --- | --- |
| undershoot U (days 4–5 − days 2–3) | +0.000 ± 0.028 | +0.009 ± 0.020 | -0.006 ± 0.022 | +0.001 ± 0.016 | -0.001 ± 0.027 | +0.007 ± 0.019 |
| overshoot E₁ (day 1 − days 4–5) | +0.130 ± 0.050 | +0.155 ± 0.039 | +0.110 ± 0.049 | +0.137 ± 0.038 | +0.128 ± 0.049 | +0.155 ± 0.039 |
| placebo-day U, 95th pct (pooled) | +0.093 | +0.081 | +0.077 | +0.087 | +0.086 | +0.082 |
| decoy-direction percentile π_U | +0.53 | +0.63 | +0.40 | +0.50 | +0.50 | +0.63 |
| ΔSSE (M_fade − M_osc)/M_fade | +0.383 | +0.388 | +0.271 | +0.246 | +0.391 | +0.383 |
| ζ_fit (M_osc) | +0.28 | +0.34 | +0.30 | +0.36 | +0.28 | +0.34 |
| ζ_pk (peak ratio; ≥ 1 if U ≤ 0) | +0.89 | +0.67 | +1.00 | +0.85 | +1.00 | +0.70 |

Verdict reason (bge, white32): U > 0 but its 90% CI includes 0. Agents with both day pairs: 8. Human messages days 4–5 minus days 2–3: -3.
Data: `data/processed/H125-kickoff-damped-oscillator/G20/results.json`; all configurations in `NE34/kickoffs_all_configs.parquet`. Day profile: `NE34/series.json`.

## Scorecard (period-specific axes)
- C: no undershoot beyond the placebo-day null.
- D: U and ζ_pk are unfitted signatures of M_osc (U ≤ 0 and ζ ≥ 1 under M_fade).
- H: M_osc vs M_fade ΔSSE +0.383 (M_osc wins, bge white32).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
