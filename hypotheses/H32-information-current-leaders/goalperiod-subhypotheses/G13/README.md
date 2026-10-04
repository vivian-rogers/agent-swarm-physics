# H32 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-19)

**Verdict:** mixed (transfer, split-half ρ +0.89; P5 fail)
**Role:** exploratory
**Period:** regime I · mode C (shared objective) · 6 agents · 1 room with ≥ 20 agent messages · 10 days. No splits (one unit per goal period).

## Why this period
50 human messages: positive control (humans as a known source); card candidate: a long coordination week.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 50 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Coordination week (10 days, 6 agents):** I expect an identifiable, stable top source (Q p < 0.05, split-half ρ > 0.3); no ground truth for who it is.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G13/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.047% (null 95th pct +0.011%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.038% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.89 (n = 6); top odd/even = 9/9 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.1 (z_out 14.1); standout p = 0.122 | null replicas | none |
| Net current | top net source = Claude Opus 4.1 | – | descriptive |
| Φ (centralization) | Φ = 0.48; Gini(Out⁺) = 0.67; top share = 0.59 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.047%; 10%-trimmed T = +0.011% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| P5 humans as a source | human pseudo-agent Out -0.006% (rank 6 of 7; null p = 0.756); by message count it would rank 7 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.60; mention in-degree -0.09; artifact adoption +0.55; H02 timing +0.54 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.1 | +0.173 | +0.015 | +0.157 | 14.1 |
| Gemini 2.5 Pro | +0.097 | +0.006 | +0.090 | 9.0 |
| Claude 3.7 Sonnet | +0.022 | +0.236 | -0.214 | 2.7 |
| Grok 4 | +0.001 | -0.016 | +0.017 | -0.2 |
| o3 | -0.003 | +0.040 | -0.043 | -0.5 |
| GPT-5 | -0.010 | -0.002 | -0.008 | -1.3 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.89 |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 4567 agent messages, 50 human, 20 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
