# H125 × G38: charity fundraiser (year 2) (step at 2026-04-02 17:00 UTC)

**Verdict:** mixed
**Role:** exploratory (native (+ replication))
**Period:** regime III · mode C · 12 incumbents · 2 room(s) · 17 non-holdout days analysed from day 1. The step response is the object (exception (c)).

## Why this period
Longest regime-III period with a shared kickoff (17 non-holdout days, 12 incumbents): room for a second swing of a ringing response.

## Prediction
*Written 2026-10-04 22:16 UTC (card) and copied here 2026-10-04 before any run on this period.*
N3: on days 1–10, M_osc beats M_fade (ΔSSE > 0) with ζ_fit < 1 in both models (credence 0.15). Counts against: M_fade wins in either model. The templated replication rule also applies to days 1–5.

## Result
**N3 (native, 10-day ring-down).**

| Statistic | bge white32 | gte white32 |
| --- | --- | --- |
| ΔSSE (M_fade − M_osc)/M_fade, days 1–10 [90% agent-bootstrap CI] | +0.075 [+0.011, +0.135] | +0.113 [−0.313, +0.148] |
| ζ_fit [90% CI] | 0.56 [0.24, 0.74] | 0.04 [0.01, 0.96] |
| half-period π/ω (active h) | 12.0 | 3.4 |
| N3 size on this skeleton (no-inertia worlds: fade 3 h / fade 8 h / drift / time of day) | 0.25 / 0.01 / 0.00 / 0.19 | 0.26 / 0.00 / 0.00 / 0.19 |
| N3 power on this skeleton (M_osc, ζ 0.5) | 0.87 | 0.88 |

N3 passes by its rule in both models, but it is weak evidence: on this skeleton a fast fading field passes in 25% of worlds (post hoc size check, `analysis/synthetic_g38.py`), the two models disagree on ζ_fit (0.56 vs 0.04) and on the period (12 h vs 3.4 h, i.e. 3 vs 1 active days), and the model-free U disagrees in sign (bge +0.035, gte −0.008). There is no day-1 overshoot along k̂ in bge (E₁ −0.007). Read: something non-monotone in #38's 10 days, not a consistent damped oscillation. Data: `data/processed/H125-kickoff-damped-oscillator/natives/G38.json`, `synthetic/g38_n3_size.json`.

**Replication (days 1–5, templated rule).**

| Statistic | bge_white | gte_white | bge_style | gte_style | bge_dedupe | gte_dedupe |
| --- | --- | --- | --- | --- | --- | --- |
| undershoot U (days 4–5 − days 2–3) | +0.035 ± 0.005 | -0.008 ± 0.013 | +0.048 ± 0.010 | +0.003 ± 0.017 | +0.033 ± 0.006 | -0.008 ± 0.013 |
| overshoot E₁ (day 1 − days 4–5) | -0.007 ± 0.010 | +0.028 ± 0.016 | -0.017 ± 0.014 | +0.019 ± 0.020 | -0.008 ± 0.011 | +0.027 ± 0.016 |
| placebo-day U, 95th pct (pooled) | +0.093 | +0.081 | +0.077 | +0.087 | +0.086 | +0.082 |
| decoy-direction percentile π_U | +0.80 | +0.43 | +0.87 | +0.57 | +0.80 | +0.40 |
| ΔSSE (M_fade − M_osc)/M_fade | +0.144 | +0.191 | +0.184 | +0.224 | +0.079 | +0.197 |
| ζ_fit (M_osc) | +0.34 | +0.14 | +0.12 | +0.02 | +0.42 | +0.14 |
| ζ_pk (peak ratio; ≥ 1 if U ≤ 0) | – | +1.00 | – | +0.49 | – | +1.00 |

Verdict reason (bge, white32): U CI above 0 but within the placebo-day range. Agents with both day pairs: 12. Human messages days 4–5 minus days 2–3: -2.
Data: `data/processed/H125-kickoff-damped-oscillator/G38/results.json`; all configurations in `NE34/kickoffs_all_configs.parquet`. Day profile: `NE34/series.json`.

## Scorecard (period-specific axes)
- C: no undershoot beyond the placebo-day null.
- D: U and ζ_pk are unfitted signatures of M_osc (U ≤ 0 and ζ ≥ 1 under M_fade).
- H: M_osc vs M_fade ΔSSE +0.144 (M_osc wins, bge white32).

## Notes
- 2026-10-04: folder verdict mixed = N3 passes by rule (weak: size 0.19–0.26) and the replication is mixed (bge U > 0 within the placebo range; gte U < 0).
- Holdout masked (`holdout_mask`); #23 excluded throughout.
