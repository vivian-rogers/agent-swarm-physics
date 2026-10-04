# H32 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-11-28)

**Verdict:** mixed (transfer, split-half ρ +0.45; P5 fail)
**Role:** exploratory
**Period:** regime I · mode I (each agent its own objective) · 10 agents · 1 room with ≥ 20 agent messages · 10 days. No splits (one unit per goal period).

## Why this period
15 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode I, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 15 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G20/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.125% (null 95th pct +0.025%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.102% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.45 (n = 10); top odd/even = 9/5 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.1 (z_out 12.1); standout p = 0.390 | null replicas | none |
| Net current | top net source = o3 | – | descriptive |
| Φ (centralization) | Φ = 0.07; Gini(Out⁺) = 0.41; top share = 0.25 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.125%; 10%-trimmed T = +0.059% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| P5 humans as a source | human pseudo-agent Out -0.031% (rank 11 of 11; null p = 0.927); by message count it would rank 11 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.30; mention in-degree +0.38; artifact adoption +0.18; H02 timing -0.07 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.1 | +0.316 | +0.183 | +0.133 | 12.1 |
| o3 | +0.236 | +0.013 | +0.223 | 5.0 |
| Claude Sonnet 4.5 | +0.217 | +0.246 | -0.029 | 11.2 |
| Claude Haiku 4.5 | +0.132 | +0.049 | +0.083 | 7.7 |
| Claude Opus 4.5 | +0.097 | +0.050 | +0.047 | 5.3 |
| GPT-5.1 | +0.096 | +0.103 | -0.007 | 2.6 |
| Claude 3.7 Sonnet | +0.087 | +0.252 | -0.165 | 5.9 |
| GPT-5 | +0.056 | +0.268 | -0.212 | 4.8 |
| Gemini 2.5 Pro | +0.037 | -0.002 | +0.039 | 1.3 |
| Gemini 3 Pro | -0.028 | +0.085 | -0.113 | -1.7 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.45 |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 4531 agent messages, 15 human, 20 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
