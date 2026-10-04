# H32 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** failed (no transfer)
**Verdict (1b):** failed (ledger exposure: T -0.264% p 0.951; gte p 0.048; style-resid p 1.000)
**Role:** replication (exploratory)
**Period:** regime III · mode F (free / none) · 10 agents · 2 rooms with ≥ 20 agent messages · 3 days. No splits (one unit per goal period).

## Why this period
several populated rooms: exposure contrast (seen vs unseen) against the common-drive rival.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode F, so I expect T at or below the median period (P10a).
- **Stability:** not eligible (needs ≥ 4 days and ≥ 6 agents); heterogeneity by Cochran's Q only (P2).
- **Exposure (P8):** ΔG for messages j saw exceeds ΔG for the same senders' simultaneous messages in rooms j was not in; the unseen gain's 90% CI includes 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G37/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = -0.237% (null 95th pct +0.042%) | p_T = 0.927 | fail |
| N1w within-day null (A1c) | T = -0.188% | p_T = 0.619 | fail |
| Leader call (standout, A1) | top = GPT-5.4 (z_out 3.0); standout p = 0.366 | null replicas | none |
| Net current | top net source = GPT-5.1 | – | descriptive |
| P8 exposure contrast | seen beyond unseen -0.236% (p 0.927); unseen -0.319% (p 0.951) | shift null | fail |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.079%; 10%-trimmed T = +0.002% | p_T = 0.049; trimmed p = 0.220 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.21; mention in-degree +0.14; artifact adoption +0.02; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| GPT-5.4 | +1.997 | +0.421 | +1.576 | 3.0 |
| Claude Opus 4.5 | +1.388 | -0.199 | +1.587 | 8.2 |
| Gemini 3.1 Pro | +0.194 | +0.455 | -0.261 | 1.0 |
| Claude Sonnet 4.5 | -0.013 | – | – | 0.3 |
| GPT-5.1 | -0.108 | -2.727 | +2.619 | 0.1 |
| GPT-5.2 | -0.226 | -0.052 | -0.175 | -0.5 |
| Claude Haiku 4.5 | -0.253 | +0.277 | -0.530 | -1.1 |
| Claude Opus 4.6 | -0.965 | +0.350 | -1.315 | -2.1 |
| Claude Sonnet 4.6 | -1.042 | +0.317 | -1.359 | -5.8 |
| DeepSeek-V3.2 | -2.086 | +0.081 | -2.168 | -6.6 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.927 (cross-day N1), 0.619 (within-day N1w); held-out days |
| H comparative (vs common drive) | 0 | exposure contrast fails |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 700 agent messages, 5 human, 26 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
