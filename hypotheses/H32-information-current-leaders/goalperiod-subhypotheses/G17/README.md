# H32 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-17)

**Verdict:** failed (no transfer; P5 fail)
**Verdict (1b):** failed (ledger exposure: T -0.001% p 0.390, split-half ρ +0.29; gte p 0.476; style-resid p 0.143)
**Role:** replication (exploratory)
**Period:** regime I · mode I (each agent its own objective) · 7 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
16 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode I, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 16 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G17/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.006% (null 95th pct +0.012%) | p_T = 0.195 | fail |
| N1w within-day null (A1c) | T = -0.001% | p_T = 0.476 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.43 (n = 7); top odd/even = 11/9 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.1 (z_out 1.7); standout p = 0.122 | null replicas | none |
| Net current | top net source = Grok 4 | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.006%; 10%-trimmed T = -0.006% | p_T = 0.195; trimmed p = 0.585 | post hoc |
| P5 humans as a source | human pseudo-agent Out -0.027% (rank 5 of 8; null p = 0.634); by message count it would rank 8 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.63; mention in-degree -0.68; artifact adoption -0.05; H02 timing +0.18 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.1 | +0.087 | -0.018 | +0.105 | 1.7 |
| Claude 3.7 Sonnet | +0.036 | +0.090 | -0.055 | 0.9 |
| Grok 4 | +0.023 | -0.124 | +0.147 | 1.0 |
| Gemini 2.5 Pro | +0.008 | -0.023 | +0.032 | 0.7 |
| o3 | -0.036 | -0.015 | -0.021 | -0.8 |
| Claude Sonnet 4.5 | -0.037 | +0.152 | -0.189 | -0.5 |
| GPT-5 | -0.037 | -0.019 | -0.018 | -0.9 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.195 (cross-day N1), 0.476 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.43 |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1994 agent messages, 16 human, 10 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
