# H32 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** supported (transfer, split-half ρ +0.47)
**Role:** exploratory
**Period:** regime III · mode I (each agent its own objective) · 15 agents · 2 rooms with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
several populated rooms: exposure contrast (seen vs unseen) against the common-drive rival.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode I, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Exposure (P8):** ΔG for messages j saw exceeds ΔG for the same senders' simultaneous messages in rooms j was not in; the unseen gain's 90% CI includes 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G42/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.189% (null 95th pct +0.025%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.173% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.47 (n = 13); top odd/even = 17/22 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.7 (z_out 4.7); standout p = 0.098 | null replicas | none |
| Net current | top net source = DeepSeek-V3.2 | – | descriptive |
| Φ (centralization) | Φ = 0.08; Gini(Out⁺) = 0.60; top share = 0.25 | 0 = equal, 1 = star | descriptive |
| P8 exposure contrast | seen beyond unseen +0.189% (p 0.024); unseen +0.040% (p 0.024) | shift null | fail |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.165%; 10%-trimmed T = +0.091% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.33; mention in-degree +0.16; artifact adoption -0.04; H02 timing +0.62 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.7 | +0.816 | +0.832 | -0.017 | 4.7 |
| Gemini 3.1 Pro | +0.640 | +0.299 | +0.341 | 2.1 |
| DeepSeek-V3.2 | +0.510 | -0.019 | +0.529 | 4.1 |
| Claude Haiku 4.5 | +0.389 | +0.210 | +0.179 | 2.7 |
| Gemini 3.5 Flash | +0.374 | -0.130 | +0.505 | 1.8 |
| Claude Sonnet 4.5 | +0.210 | +0.577 | -0.367 | 2.1 |
| Claude Opus 4.5 | +0.201 | +0.089 | +0.111 | 1.3 |
| Claude Sonnet 4.6 | +0.114 | +0.257 | -0.142 | 0.6 |
| GPT-5.5 | +0.025 | +0.737 | -0.711 | 0.2 |
| GPT-5.2 | -0.006 | +0.078 | -0.084 | 0.2 |
| GPT-5.4 | -0.023 | -0.005 | -0.018 | 0.2 |
| GPT-5.1 | -0.046 | +0.173 | -0.220 | 0.3 |
| Claude Opus 4.6 | -0.063 | +0.003 | -0.066 | -0.1 |
| Kimi K2.6 | -0.135 | -0.017 | -0.118 | -0.3 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.47 |
| H comparative (vs common drive) | 0 | exposure contrast fails |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1218 agent messages, 10 human, 39 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
