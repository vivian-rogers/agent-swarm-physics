# H32 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-25)

**Verdict:** failed (no transfer; P5 pass)
**Verdict (1b):** failed (ledger exposure: T -0.026% p 0.927; gte p 0.952; style-resid p 0.714)
**Role:** exploratory
**Period:** regime I · mode F (free / none) · 4 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
881 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode F, so I expect T at or below the median period (P10a).
- **Stability:** not eligible (needs ≥ 4 days and ≥ 6 agents); heterogeneity by Cochran's Q only (P2).
- **Humans as a source (P5, positive control):** 881 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G05/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = -0.025% (null 95th pct +0.047%) | p_T = 0.927 | fail |
| N1w within-day null (A1c) | T = -0.113% | p_T = 1.000 | fail |
| Leader call (standout, A1) | top = Gemini 2.5 Pro (z_out 0.1); standout p = 0.024 | null replicas | called |
| Net current | top net source = Gemini 2.5 Pro | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = -0.025%; 10%-trimmed T = -0.030% | p_T = 0.927; trimmed p = 0.927 | post hoc |
| P5 humans as a source | human pseudo-agent Out -0.009% (rank 2 of 5; null p = 0.732); by message count it would rank 1 | – | pass |
| Rivals: Spearman ρ of Out with | count +0.40; mention in-degree -0.74; artifact adoption -0.11; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Gemini 2.5 Pro | +0.013 | -0.036 | +0.049 | 0.1 |
| Claude 3.7 Sonnet | -0.035 | -0.008 | -0.026 | -1.0 |
| Claude Opus 4 | -0.038 | -0.060 | +0.022 | -1.4 |
| o3 | -0.040 | +0.005 | -0.045 | -1.1 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.927 (cross-day N1), 1.000 (within-day N1w); held-out days |
| G ground truth | 2 | P5 humans as a source: pass |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1119 agent messages, 881 human, 10 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
