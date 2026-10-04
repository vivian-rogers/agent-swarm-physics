# H32 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-13)

**Verdict:** failed (transfer, split-half ρ -0.40; P5 fail)
**Role:** exploratory
**Period:** regime I · mode C (shared objective) · 11 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
15 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 15 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G30/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.091% (null 95th pct +0.026%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.107% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = -0.40 (n = 11); top odd/even = 16/14 | ρ = 0 | fail |
| Leader call (standout, A1) | top = Claude Opus 4.5 (z_out 7.0); standout p = 0.390 | null replicas | none |
| Net current | top net source = Claude Opus 4.5 | – | descriptive |
| Φ (centralization) | Φ = 0.10; Gini(Out⁺) = 0.34; top share = 0.24 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.091%; 10%-trimmed T = +0.063% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| P5 humans as a source | human pseudo-agent Out +0.058% (rank 10 of 12; null p = 0.049); by message count it would rank 12 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.76; mention in-degree +0.59; artifact adoption -0.21; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.5 | +0.269 | +0.078 | +0.190 | 7.0 |
| Claude Opus 4.6 | +0.142 | +0.059 | +0.083 | 4.3 |
| Claude 3.7 Sonnet | +0.132 | +0.096 | +0.036 | 2.8 |
| Gemini 2.5 Pro | +0.121 | +0.028 | +0.092 | 4.5 |
| GPT-5.2 | +0.109 | +0.036 | +0.073 | 2.9 |
| GPT-5.1 | +0.108 | +0.155 | -0.047 | 2.2 |
| Claude Haiku 4.5 | +0.087 | +0.221 | -0.133 | 1.9 |
| Claude Sonnet 4.5 | +0.080 | +0.130 | -0.050 | 1.5 |
| DeepSeek-V3.2 | +0.080 | -0.003 | +0.082 | 1.6 |
| GPT-5 | +0.015 | +0.139 | -0.124 | 0.8 |
| Gemini 3 Pro | -0.139 | +0.064 | -0.203 | -2.9 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 0 | split-half ρ = -0.40 |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2380 agent messages, 15 human, 22 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
