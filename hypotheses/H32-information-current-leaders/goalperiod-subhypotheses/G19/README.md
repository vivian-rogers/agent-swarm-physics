# H32 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-14)

**Verdict:** supported (transfer, split-half ρ +0.43)
**Verdict (1b):** supported (ledger exposure: T +0.112% p 0.024, split-half ρ +0.43; gte p 0.048; style-resid p 0.048)
**Role:** exploratory
**Period:** regime I · mode C (shared objective) · 8 agents · 1 room with ≥ 20 agent messages · 10 days. No splits (one unit per goal period).

## Why this period
mode C (shared objective) comparison of transfer and centralization.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G19/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.118% (null 95th pct +0.013%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.107% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.43 (n = 7); top odd/even = 12/13 | ρ = 0 | pass |
| Leader call (standout, A1) | top = o3 (z_out 11.2); standout p = 0.317 | null replicas | none |
| Net current | top net source = o3 | – | descriptive |
| Φ (centralization) | Φ = 0.11; Gini(Out⁺) = 0.42; top share = 0.34 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.118%; 10%-trimmed T = +0.067% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| Rivals: Spearman ρ of Out with | count -0.21; mention in-degree +0.32; artifact adoption +0.78; H02 timing +0.82 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| o3 | +0.283 | +0.003 | +0.279 | 11.2 |
| Claude Sonnet 4.5 | +0.190 | +0.197 | -0.007 | 11.5 |
| Claude Haiku 4.5 | +0.149 | +0.040 | +0.110 | 8.0 |
| Claude Opus 4.1 | +0.090 | +0.196 | -0.106 | 6.5 |
| Claude 3.7 Sonnet | +0.068 | +0.110 | -0.041 | 4.6 |
| Gemini 2.5 Pro | +0.025 | -0.003 | +0.028 | 1.4 |
| GPT-5 | +0.017 | +0.281 | -0.263 | 1.6 |
| GPT-5.1 | – | – | – | nan |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.43 |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 5358 agent messages, 11 human, 20 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
