# H32 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** mixed (transfer, standout p 0.10; P5 pass)
**Verdict (1b):** supported (ledger exposure: T +0.037% p 0.024; gte p 0.048; style-resid p 0.048)
**Role:** exploratory
**Period:** regime I · mode K (competition) · 4 agents · 1 room with ≥ 20 agent messages · 15 days. No splits (one unit per goal period).

## Why this period
443 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode K: no mode-specific expectation.
- **Stability:** not eligible (needs ≥ 4 days and ≥ 6 agents); heterogeneity by Cochran's Q only (P2).
- **Humans as a source (P5, positive control):** 443 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G06/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.038% (null 95th pct +0.024%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.026% | p_T = 0.048 | pass |
| Leader call (standout, A1) | top = Claude Opus 4 (z_out 7.4); standout p = 0.098 | null replicas | none |
| Net current | top net source = Claude Opus 4 | – | descriptive |
| Φ (centralization) | Φ = 0.83; Gini(Out⁺) = 0.62; top share = 0.81 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.038%; 10%-trimmed T = +0.009% | p_T = 0.024; trimmed p = 0.293 | post hoc |
| P5 humans as a source | human pseudo-agent Out +0.066% (rank 2 of 5; null p = 0.024); by message count it would rank 4 | – | pass |
| Rivals: Spearman ρ of Out with | count +0.80; mention in-degree +0.60; artifact adoption -0.32; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4 | +0.131 | +0.018 | +0.113 | 7.4 |
| o3 | +0.020 | -0.004 | +0.024 | 0.6 |
| Gemini 2.5 Pro | +0.012 | +0.016 | -0.004 | 0.3 |
| Claude 3.7 Sonnet | -0.010 | +0.122 | -0.132 | -1.0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| G ground truth | 2 | P5 humans as a source: pass |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2227 agent messages, 443 human, 24 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
