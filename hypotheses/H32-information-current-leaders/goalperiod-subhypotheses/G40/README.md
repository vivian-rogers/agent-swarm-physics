# H32 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** failed (no transfer)
**Role:** exploratory
**Period:** regime III · mode C (shared objective) · 15 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
NE42 A-B-A room merge.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **NE42 (P9):** merged week (#universe-coordination): pairs that were split in #39/#41 are exposed here, so their ΔG > 0 and exceeds their #39 and #41 values.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G40/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = -0.175% (null 95th pct +0.010%) | p_T = 1.000 | fail |
| N1w within-day null (A1c) | T = -0.109% | p_T = 1.000 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.01 (n = 12); top odd/even = 23/23 | ρ = 0 | pass |
| Leader call (standout, A1) | top = GPT-5.4 (z_out 2.0); standout p = 0.805 | null replicas | none |
| Net current | top net source = Gemini 2.5 Pro | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = -0.030%; 10%-trimmed T = -0.037% | p_T = 0.512; trimmed p = 1.000 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.59; mention in-degree +0.46; artifact adoption +0.12; H02 timing -0.12 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| GPT-5.4 | +0.311 | -0.001 | +0.312 | 2.0 |
| Claude Opus 4.5 | +0.233 | -0.044 | +0.277 | 1.2 |
| Gemini 3.1 Pro | +0.073 | +0.058 | +0.015 | 0.7 |
| GPT-5.5 | -0.001 | +0.159 | -0.159 | -0.3 |
| Gemini 2.5 Pro | -0.005 | -1.364 | +1.359 | 0.7 |
| Claude Haiku 4.5 | -0.075 | -0.249 | +0.175 | -0.1 |
| DeepSeek-V3.2 | -0.091 | -0.012 | -0.078 | -0.5 |
| Claude Sonnet 4.6 | -0.107 | -0.022 | -0.085 | -0.8 |
| GPT-5.2 | -0.123 | +0.205 | -0.328 | -0.6 |
| Claude Sonnet 4.5 | -0.134 | +0.029 | -0.163 | -1.4 |
| GPT-5.1 | -0.143 | – | – | -1.4 |
| Kimi K2.6 | -0.151 | -1.060 | +0.909 | -0.9 |
| Claude Opus 4.6 | -1.059 | -0.131 | -0.928 | -7.9 |
| Claude Opus 4.7 | -1.165 | -0.074 | -1.091 | -3.6 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 1.000 (cross-day N1), 1.000 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.01 |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1731 agent messages, 4 human, 21 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
