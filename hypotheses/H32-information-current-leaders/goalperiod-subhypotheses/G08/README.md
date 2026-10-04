# H32 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-12)

**Verdict:** failed (no transfer; P5 fail)
**Verdict (1b):** failed (ledger exposure: T +0.012% p 0.220; gte p 0.048; style-resid p 0.238)
**Role:** replication (exploratory)
**Period:** regime I · mode C (shared objective) · 4 agents · 1 room with ≥ 20 agent messages · 18 days. No splits (one unit per goal period).

## Why this period
39 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability:** not eligible (needs ≥ 4 days and ≥ 6 agents); heterogeneity by Cochran's Q only (P2).
- **Humans as a source (P5, positive control):** 39 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G08/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.013% (null 95th pct +0.018%) | p_T = 0.195 | fail |
| N1w within-day null (A1c) | T = +0.018% | p_T = 0.048 | pass |
| Leader call (standout, A1) | top = Claude Opus 4 (z_out 4.4); standout p = 0.634 | null replicas | none |
| Net current | top net source = Claude Opus 4 | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.013%; 10%-trimmed T = +0.000% | p_T = 0.195; trimmed p = 0.463 | post hoc |
| P5 humans as a source | human pseudo-agent Out -0.005% (rank 4 of 5; null p = 0.878); by message count it would rank 5 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.40; mention in-degree -0.40; artifact adoption +0.40; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4 | +0.061 | -0.008 | +0.069 | 4.4 |
| Gemini 2.5 Pro | +0.030 | -0.011 | +0.041 | 2.1 |
| Claude 3.7 Sonnet | +0.004 | +0.082 | -0.078 | 0.1 |
| o3 | -0.043 | -0.012 | -0.031 | -2.4 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.195 (cross-day N1), 0.048 (within-day N1w); held-out days |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 3250 agent messages, 39 human, 36 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
