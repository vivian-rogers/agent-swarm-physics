# H32 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-05)

**Verdict:** failed (no transfer)
**Role:** exploratory
**Period:** regime I · mode I (each agent its own objective) · 9 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
mode I (each agent its own objective) comparison of transfer and centralization.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode I, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G21/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.019% (null 95th pct +0.016%) | p_T = 0.073 | fail |
| N1w within-day null (A1c) | T = +0.017% | p_T = 0.238 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.79 (n = 9); top odd/even = 13/16 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Haiku 4.5 (z_out 6.7); standout p = 0.439 | null replicas | none |
| Net current | top net source = Claude Haiku 4.5 | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.019%; 10%-trimmed T = -0.003% | p_T = 0.073; trimmed p = 0.512 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.50; mention in-degree -0.25; artifact adoption +0.71; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Haiku 4.5 | +0.240 | -0.004 | +0.245 | 6.7 |
| Claude Opus 4.5 | +0.187 | +0.006 | +0.181 | 3.9 |
| Claude 3.7 Sonnet | +0.147 | +0.194 | -0.047 | 3.4 |
| Claude Sonnet 4.5 | +0.042 | +0.309 | -0.267 | 0.9 |
| GPT-5 | -0.029 | -0.249 | +0.220 | -0.3 |
| GPT-5.1 | -0.063 | -0.003 | -0.060 | -2.1 |
| Gemini 2.5 Pro | -0.068 | -0.008 | -0.059 | -0.8 |
| Gemini 3 Pro | -0.084 | -0.019 | -0.065 | -2.1 |
| DeepSeek-V3.2 | -0.206 | -0.058 | -0.149 | -3.5 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.073 (cross-day N1), 0.238 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.79 |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2437 agent messages, 5 human, 10 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
