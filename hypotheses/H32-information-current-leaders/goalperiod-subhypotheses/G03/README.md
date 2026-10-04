# H32 × G03: Holiday: do whatever you'd like! Next goal will begin soon (2025-05-12 → 2025-05-14)

**Verdict:** failed (no transfer; P5 pass)
**Role:** exploratory
**Period:** regime I · mode F (free / none) · 4 agents · 1 room with ≥ 20 agent messages · 3 days. No splits (one unit per goal period).

## Why this period
77 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode F, so I expect T at or below the median period (P10a).
- **Stability:** not eligible (needs ≥ 4 days and ≥ 6 agents); heterogeneity by Cochran's Q only (P2).
- **Humans as a source (P5, positive control):** 77 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G03/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.003% (null 95th pct +0.046%) | p_T = 0.439 | fail |
| N1w within-day null (A1c) | T = -0.143% | p_T = 0.810 | fail |
| Leader call (standout, A1) | top = Gemini 2.5 Pro (z_out 1.8); standout p = 0.707 | null replicas | none |
| Net current | top net source = Gemini 2.5 Pro | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.003%; 10%-trimmed T = +0.010% | p_T = 0.439; trimmed p = 0.439 | post hoc |
| P5 humans as a source | human pseudo-agent Out +0.060% (rank 2 of 5; null p = 0.024); by message count it would rank 5 | – | pass |
| Rivals: Spearman ρ of Out with | count -0.40; mention in-degree -0.80; artifact adoption +0.00; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Gemini 2.5 Pro | +0.141 | +0.019 | +0.123 | 1.8 |
| Claude 3.7 Sonnet | +0.041 | -0.041 | +0.082 | 0.6 |
| o3 | +0.025 | -0.044 | +0.069 | 0.7 |
| GPT-4.1 | -0.196 | +0.078 | -0.274 | -1.4 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.439 (cross-day N1), 0.810 (within-day N1w); held-out days |
| G ground truth | 2 | P5 humans as a source: pass |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1620 agent messages, 77 human, 6 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
