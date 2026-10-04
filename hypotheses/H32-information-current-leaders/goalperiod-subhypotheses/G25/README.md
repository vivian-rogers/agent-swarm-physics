# H32 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-02)

**Verdict:** supported (transfer, split-half ρ +0.10)
**Verdict (1b):** supported (ledger exposure: T +0.046% p 0.024, split-half ρ +0.10; gte p 0.048; style-resid p 0.048)
**Role:** replication (exploratory)
**Period:** regime I · mode C (shared objective) · 10 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
mode C (shared objective) comparison of transfer and centralization.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G25/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.049% (null 95th pct +0.030%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.044% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.10 (n = 10); top odd/even = 14/18 | ρ = 0 | pass |
| Leader call (standout, A1) | top = GPT-5.2 (z_out 3.2); standout p = 0.293 | null replicas | none |
| Net current | top net source = DeepSeek-V3.2 | – | descriptive |
| Φ (centralization) | Φ = 0.03; Gini(Out⁺) = 0.46; top share = 0.28 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.049%; 10%-trimmed T = +0.029% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| Rivals: Spearman ρ of Out with | count -0.20; mention in-degree +0.82; artifact adoption +0.44; H02 timing +0.42 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| GPT-5.2 | +0.141 | +0.053 | +0.088 | 3.2 |
| Claude Haiku 4.5 | +0.089 | +0.041 | +0.049 | 3.6 |
| DeepSeek-V3.2 | +0.072 | -0.072 | +0.144 | 1.6 |
| Gemini 3 Pro | +0.063 | +0.047 | +0.016 | 1.9 |
| GPT-5.1 | +0.060 | +0.132 | -0.072 | 1.2 |
| Claude Opus 4.5 | +0.037 | +0.060 | -0.023 | 1.3 |
| Claude Sonnet 4.5 | +0.024 | +0.059 | -0.035 | 0.4 |
| Claude 3.7 Sonnet | +0.014 | -0.014 | +0.028 | 0.2 |
| Gemini 2.5 Pro | -0.001 | -0.001 | -0.000 | 0.1 |
| GPT-5 | -0.013 | +0.182 | -0.195 | -0.4 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.10 |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2535 agent messages, 4 human, 9 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
