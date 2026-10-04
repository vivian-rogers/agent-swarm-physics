# H32 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-19)

**Verdict:** mixed (transfer, split-half ρ +0.53; P5 fail)
**Role:** exploratory
**Period:** regime I · mode K (competition) · 10 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
23 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode K: no mode-specific expectation.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 23 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G23/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.077% (null 95th pct +0.025%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.056% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.53 (n = 10); top odd/even = 13/13 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Haiku 4.5 (z_out 12.6); standout p = 0.024 | null replicas | called |
| Net current | top net source = Claude Haiku 4.5 | – | descriptive |
| Φ (centralization) | Φ = 0.81; Gini(Out⁺) = 0.77; top share = 0.55 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.077%; 10%-trimmed T = +0.003% | p_T = 0.024; trimmed p = 0.366 | post hoc |
| P5 humans as a source | human pseudo-agent Out -0.226% (rank 11 of 11; null p = 0.902); by message count it would rank 11 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.49; mention in-degree -0.15; artifact adoption +0.11; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Haiku 4.5 | +0.579 | -0.057 | +0.637 | 12.6 |
| Claude Opus 4.5 | +0.319 | +0.085 | +0.234 | 5.9 |
| Claude 3.7 Sonnet | +0.098 | +0.312 | -0.213 | 2.2 |
| Claude Sonnet 4.5 | +0.037 | +0.578 | -0.541 | 1.1 |
| Gemini 3 Pro | +0.009 | +0.102 | -0.093 | 0.4 |
| DeepSeek-V3.2 | +0.001 | -0.005 | +0.006 | 0.1 |
| Gemini 2.5 Pro | -0.038 | -0.001 | -0.037 | -0.3 |
| GPT-5.2 | -0.054 | -0.133 | +0.080 | -1.1 |
| GPT-5.1 | -0.074 | -0.039 | -0.035 | -2.1 |
| GPT-5 | -0.109 | -0.072 | -0.038 | -3.2 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.53 |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1772 agent messages, 23 human, 10 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
