# H32 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04)

**Verdict:** failed (no transfer)
**Verdict (1b):** failed (ledger exposure: T +0.023% p 0.341; gte p 0.476; style-resid p 0.381)
**Role:** replication (exploratory)
**Period:** regime II · mode C (shared objective) · 11 agents · 1 room with ≥ 20 agent messages · 3 days. No splits (one unit per goal period).

## Why this period
mode C (shared objective) comparison of transfer and centralization.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability:** not eligible (needs ≥ 4 days and ≥ 6 agents); heterogeneity by Cochran's Q only (P2).
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G33/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.025% (null 95th pct +0.073%) | p_T = 0.341 | fail |
| N1w within-day null (A1c) | T = -0.154% | p_T = 0.952 | fail |
| Leader call (standout, A1) | top = GPT-5 (z_out 3.6); standout p = 0.146 | null replicas | none |
| Net current | top net source = GPT-5 | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.037%; 10%-trimmed T = +0.027% | p_T = 0.244; trimmed p = 0.317 | post hoc |
| Rivals: Spearman ρ of Out with | count -0.37; mention in-degree +0.05; artifact adoption +0.17; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| GPT-5 | +0.254 | -0.092 | +0.346 | 3.6 |
| Claude Sonnet 4.5 | +0.117 | -0.018 | +0.135 | 2.0 |
| GPT-5.1 | +0.051 | +0.032 | +0.019 | 0.3 |
| Gemini 2.5 Pro | +0.033 | +0.198 | -0.165 | 0.5 |
| Gemini 3 Pro | +0.033 | +0.156 | -0.123 | 0.6 |
| GPT-5.2 | +0.021 | +0.025 | -0.003 | 0.5 |
| Claude Opus 4.6 | -0.009 | -0.001 | -0.008 | -0.4 |
| Claude Opus 4.5 | -0.054 | +0.083 | -0.136 | -0.8 |
| DeepSeek-V3.2 | -0.054 | -0.019 | -0.035 | -0.7 |
| Claude Haiku 4.5 | -0.055 | -0.055 | +0.000 | -0.4 |
| Claude Sonnet 4.6 | -0.057 | -0.028 | -0.029 | -0.6 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.341 (cross-day N1), 0.952 (within-day N1w); held-out days |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1766 agent messages, 1 human, 28 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
