# H125 × G51: maximize your private assigned role (step at 2026-07-06 16:00 UTC)

**Verdict:** failed
**Role:** exploratory (native N1 + shared-kickoff replication)
**Period:** regime III · mode I/K · 21 incumbents · 1 room(s) · 45 non-holdout days analysed from day 1. The step response is the object (exception (c)).

## Why this period
#51 kickoff 2026-07-06: ~21 agents receive private roles at once. Each agent has its own target, so the own-role excess alignment (decoys = the other agents' roles) gives a step response with N ≈ 21, the largest single-kickoff N in the data.

## Prediction
*Written 2026-10-04 22:16 UTC (card) and copied here 2026-10-04 before any run on this period.*
N1: own-role excess alignment undershoots: U_own > 0 with 90% CI above 0 in both models (credence 0.15). Counts against: U_own ≤ 0 or CI includes 0. H54 saw no decay of own-goal alignment over 9 weeks, so a flat response is the expectation. The shared-kickoff replication (templated rule) is reported beside it.

## Result
**N1 (native, own roles; the verdict line).**

| Statistic | bge white32 | gte white32 | bge style | gte style |
| --- | --- | --- | --- | --- |
| own-role undershoot U_own (± jackknife SE) | −0.009 ± 0.016 | −0.026 ± 0.015 | −0.007 ± 0.018 | −0.025 ± 0.017 |
| own-role overshoot E₁ | +0.055 ± 0.026 | +0.054 ± 0.025 | +0.055 ± 0.027 | +0.055 ± 0.026 |
| placebo-day U in #51 (95th pct, 36 origins) | +0.031 | +0.020 | +0.032 | +0.022 |
| ΔSSE (M_fade − M_osc)/M_fade | −0.14 | −0.05 | −0.12 | −0.04 |

N1 fails in both models: the own-role excess overshoots on day 1 (E₁ ≈ +0.055, N = 21) and keeps falling into days 4–5 (U_own ≤ 0; gte's 90% CI just below 0). M_fade beats M_osc in every configuration. Data: `data/processed/H125-kickoff-damped-oscillator/natives/G51.json`.

**Shared-kickoff replication (templated rule, mixed).** #51's shared kickoff is not the target agents follow (H54); the table below is along that kickoff.

| Statistic | bge_white | gte_white | bge_style | gte_style | bge_dedupe | gte_dedupe |
| --- | --- | --- | --- | --- | --- | --- |
| undershoot U (days 4–5 − days 2–3) | +0.010 ± 0.006 | +0.008 ± 0.007 | +0.009 ± 0.007 | +0.008 ± 0.007 | +0.010 ± 0.006 | +0.007 ± 0.007 |
| overshoot E₁ (day 1 − days 4–5) | -0.020 ± 0.009 | +0.009 ± 0.008 | -0.016 ± 0.010 | +0.011 ± 0.009 | -0.021 ± 0.008 | +0.009 ± 0.008 |
| placebo-day U, 95th pct (pooled) | +0.093 | +0.081 | +0.077 | +0.087 | +0.086 | +0.082 |
| decoy-direction percentile π_U | +0.84 | +0.72 | +0.78 | +0.69 | +0.84 | +0.66 |
| ΔSSE (M_fade − M_osc)/M_fade | +0.082 | +0.037 | +0.040 | +0.019 | +0.072 | +0.046 |
| ζ_fit (M_osc) | +0.34 | +0.17 | +0.50 | +0.28 | +0.34 | +0.10 |
| ζ_pk (peak ratio; ≥ 1 if U ≤ 0) | – | +0.04 | – | +0.11 | – | +0.10 |

Verdict reason (bge, white32): U CI above 0 but within the placebo-day range. Agents with both day pairs: 21. Human messages days 4–5 minus days 2–3: 18.
Data: `data/processed/H125-kickoff-damped-oscillator/G51/results.json`; all configurations in `NE34/kickoffs_all_configs.parquet`. Day profile: `NE34/series.json`.

## Scorecard (period-specific axes)
- C: no undershoot beyond the placebo-day null.
- D: U and ζ_pk are unfitted signatures of M_osc (U ≤ 0 and ζ ≥ 1 under M_fade).
- H: M_osc vs M_fade ΔSSE +0.082 (M_osc wins, bge white32).

## Notes
- 2026-10-04: verdict = N1 (failed); the shared-kickoff replication is mixed (U > 0 but inside the placebo range; no day-1 overshoot along the shared kickoff in bge).
- Holdout masked (`holdout_mask`); #23 excluded throughout.
