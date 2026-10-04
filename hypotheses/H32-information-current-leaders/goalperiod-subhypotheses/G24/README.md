# H32 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-26)

**Verdict:** failed (no transfer)
**Verdict (1b):** failed (ledger exposure: T +0.009% p 0.171, split-half ρ +0.20; gte p 0.048; style-resid p 0.667)
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
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G24/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.018% (null 95th pct +0.021%) | p_T = 0.122 | fail |
| N1w within-day null (A1c) | T = +0.085% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.39 (n = 10); top odd/even = 16/16 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.5 (z_out 2.2); standout p = 0.951 | null replicas | none |
| Net current | top net source = Claude Opus 4.5 | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.018%; 10%-trimmed T = -0.001% | p_T = 0.122; trimmed p = 0.439 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.36; mention in-degree -0.02; artifact adoption -0.22; H02 timing +0.44 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.5 | +0.134 | -0.076 | +0.210 | 2.2 |
| Claude Haiku 4.5 | +0.131 | +0.021 | +0.110 | 2.3 |
| Claude Sonnet 4.5 | +0.077 | +0.213 | -0.136 | 1.4 |
| GPT-5.2 | +0.073 | +0.014 | +0.059 | 1.3 |
| GPT-5.1 | +0.046 | +0.092 | -0.046 | 0.9 |
| GPT-5 | +0.040 | +0.076 | -0.036 | 1.1 |
| Gemini 3 Pro | +0.017 | -0.185 | +0.202 | 0.2 |
| Claude 3.7 Sonnet | -0.014 | +0.122 | -0.136 | -0.4 |
| DeepSeek-V3.2 | -0.126 | -0.074 | -0.052 | -2.1 |
| Gemini 2.5 Pro | -0.203 | -0.027 | -0.175 | -5.2 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.122 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.39 |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1586 agent messages, 6 human, 9 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
