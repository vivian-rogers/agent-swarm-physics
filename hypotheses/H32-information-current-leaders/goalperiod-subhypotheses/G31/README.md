# H32 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** supported (transfer, split-half ρ +0.65)
**Verdict (1b):** supported (ledger exposure: T +0.034% p 0.024, split-half ρ +0.64; gte p 0.048; style-resid p 0.476)
**Role:** replication (exploratory)
**Period:** regime I · mode F (free / none) · 12 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
mode F (free / none) comparison of transfer and centralization.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode F, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G31/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.040% (null 95th pct +0.019%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.040% | p_T = 0.143 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.65 (n = 12); top odd/even = 16/16 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.6 (z_out 4.9); standout p = 0.390 | null replicas | none |
| Net current | top net source = Claude Opus 4.6 | – | descriptive |
| Φ (centralization) | Φ = 0.25; Gini(Out⁺) = 0.66; top share = 0.30 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.040%; 10%-trimmed T = +0.023% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.65; mention in-degree +0.68; artifact adoption -0.27; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.6 | +0.178 | +0.019 | +0.159 | 4.9 |
| Claude Opus 4.5 | +0.144 | +0.128 | +0.016 | 2.6 |
| Claude Sonnet 4.5 | +0.144 | +0.217 | -0.073 | 3.3 |
| Claude Haiku 4.5 | +0.087 | +0.109 | -0.022 | 2.6 |
| GPT-5.2 | +0.020 | -0.013 | +0.033 | 0.7 |
| GPT-5.1 | +0.018 | -0.078 | +0.095 | 0.5 |
| GPT-5 | +0.010 | +0.001 | +0.008 | 0.0 |
| Claude 3.7 Sonnet | -0.008 | +0.093 | -0.100 | 0.3 |
| Claude Sonnet 4.6 | -0.010 | +0.054 | -0.065 | 0.1 |
| Gemini 2.5 Pro | -0.016 | +0.003 | -0.019 | -0.3 |
| Gemini 3 Pro | -0.036 | -0.139 | +0.104 | -1.0 |
| DeepSeek-V3.2 | -0.058 | +0.092 | -0.150 | -1.4 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | p_T = 0.024 (cross-day N1), 0.143 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.65 |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2782 agent messages, 9 human, 35 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
