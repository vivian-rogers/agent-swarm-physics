# H125 × G30: adopt a park (step at 2026-02-09 18:00 UTC)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime I · mode C · 11 incumbents · 1 room(s) · 5 non-holdout days analysed from day 1. The step response is the object (exception (c)).

## Why this period
One eligible kickoff (shared kickoff, ≥ 5 non-holdout days in one regime). Common estimator, templated rule.

## Prediction
*Written 2026-10-04 22:16 UTC (card) and copied here 2026-10-04 before any run on this period.*
Templated from the card (written 2026-10-04 22:16 UTC, before any real-data statistic), labelled as such. After the step at t₀ the within-agent excess alignment along k̂ overshoots on day 1 (E₁ > 0, H97/H54) and, under HH366's inertia, swings below its days 4–5 level on days 2–3: undershoot U > 0. Rule: supported if U > 0 with jackknife 90% CI above 0 and U above the 95th percentile of the pooled placebo-day U (bge, white32); failed if U ≤ 0; mixed otherwise; descriptive if fewer than 4 agents have both day pairs. The card's credence for an undershoot is 0.2, so the expected verdict here is failed or mixed.

## Result
| Statistic | bge_white | gte_white | bge_style | gte_style | bge_dedupe | gte_dedupe |
| --- | --- | --- | --- | --- | --- | --- |
| undershoot U (days 4–5 − days 2–3) | +0.040 ± 0.022 | +0.022 ± 0.024 | +0.039 ± 0.022 | +0.027 ± 0.024 | +0.042 ± 0.021 | +0.024 ± 0.023 |
| overshoot E₁ (day 1 − days 4–5) | +0.028 ± 0.024 | +0.054 ± 0.026 | +0.037 ± 0.025 | +0.054 ± 0.029 | +0.027 ± 0.023 | +0.053 ± 0.025 |
| placebo-day U, 95th pct (pooled) | +0.093 | +0.081 | +0.077 | +0.087 | +0.086 | +0.082 |
| decoy-direction percentile π_U | +0.87 | +0.74 | +0.90 | +0.84 | +0.90 | +0.81 |
| ΔSSE (M_fade − M_osc)/M_fade | -0.046 | -0.002 | -0.037 | -0.002 | -0.051 | -0.005 |
| ζ_fit (M_osc) | +0.81 | +0.90 | +0.81 | +0.82 | +0.81 | +0.90 |
| ζ_pk (peak ratio; ≥ 1 if U ≤ 0) | +0.00 | +0.27 | +0.00 | +0.22 | +0.00 | +0.25 |

Verdict reason (bge, white32): U CI above 0 but within the placebo-day range. Agents with both day pairs: 11. Human messages days 4–5 minus days 2–3: 1.
Data: `data/processed/H125-kickoff-damped-oscillator/G30/results.json`; all configurations in `NE34/kickoffs_all_configs.parquet`. Day profile: `NE34/series.json`.

## Scorecard (period-specific axes)
- C: no undershoot beyond the placebo-day null.
- D: U and ζ_pk are unfitted signatures of M_osc (U ≤ 0 and ζ ≥ 1 under M_fade).
- H: M_osc vs M_fade ΔSSE -0.046 (M_fade wins, bge white32).

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
