# H32 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** failed (no transfer)
**Role:** exploratory
**Period:** regime III · mode I (each agent its own objective) · 15 agents · 2 rooms with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
several populated rooms: exposure contrast (seen vs unseen) against the common-drive rival; NE42 A-B-A room merge.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode I, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Exposure (P8):** ΔG for messages j saw exceeds ΔG for the same senders' simultaneous messages in rooms j was not in; the unseen gain's 90% CI includes 0.
- **NE42 (P9):** before the merge: pairs in different rooms here are unexposed, so their ΔG ≈ 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G39/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = -0.061% (null 95th pct +0.026%) | p_T = 0.610 | fail |
| N1w within-day null (A1c) | T = +0.035% | p_T = 0.143 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.02 (n = 11); top odd/even = 23/24 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Sonnet 4.5 (z_out 3.0); standout p = 0.951 | null replicas | none |
| Net current | top net source = Gemini 3.1 Pro | – | descriptive |
| P8 exposure contrast | seen beyond unseen -0.061% (p 0.610); unseen -0.048% (p 0.463) | shift null | fail |
| A2 post hoc (folds with ≥ 20 training messages) | T = -0.115%; 10%-trimmed T = -0.024% | p_T = 0.976; trimmed p = 0.732 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.64; mention in-degree +0.11; artifact adoption +0.04; H02 timing -0.09 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Sonnet 4.5 | +0.270 | +0.016 | +0.254 | 3.0 |
| Claude Haiku 4.5 | +0.113 | -0.117 | +0.230 | 0.8 |
| GPT-5.4 | +0.041 | -0.076 | +0.117 | 0.3 |
| DeepSeek-V3.2 | +0.019 | -0.024 | +0.043 | 0.6 |
| Claude Sonnet 4.6 | +0.006 | +0.111 | -0.105 | 0.5 |
| GPT-5.1 | -0.004 | +0.517 | -0.521 | 0.6 |
| Claude Opus 4.5 | -0.072 | -0.291 | +0.220 | -0.0 |
| Claude Opus 4.6 | -0.087 | +0.116 | -0.203 | -0.4 |
| GPT-5.2 | -0.089 | -0.054 | -0.036 | -0.4 |
| Gemini 3.1 Pro | -0.219 | -2.437 | +2.218 | -0.1 |
| GPT-5.5 | -1.312 | -0.409 | -0.903 | -2.3 |
| Claude Opus 4.7 | -1.637 | -0.323 | -1.315 | -3.4 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.610 (cross-day N1), 0.143 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.02 |
| H comparative (vs common drive) | 0 | exposure contrast fails |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 865 agent messages, 13 human, 17 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
