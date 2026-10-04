# H32 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-08-29)

**Verdict:** failed (no transfer)
**Verdict (1b):** failed (ledger exposure: T -0.024% p 0.951, split-half ρ -0.54; gte p 0.952; style-resid p 0.048)
**Role:** exploratory
**Period:** regime I · mode F (free / none) · 7 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
mode F (free / none) comparison of transfer and centralization.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode F, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G11/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = -0.023% (null 95th pct +0.030%) | p_T = 0.902 | fail |
| N1w within-day null (A1c) | T = -0.036% | p_T = 1.000 | fail |
| P3 split-half ρ(Out) > 0 | ρ = -0.61 (n = 7); top odd/even = 0/10 | ρ = 0 | fail |
| Leader call (standout, A1) | top = GPT-5 (z_out 4.2); standout p = 0.220 | null replicas | none |
| Net current | top net source = GPT-5 | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = -0.023%; 10%-trimmed T = -0.018% | p_T = 0.902; trimmed p = 0.902 | post hoc |
| Rivals: Spearman ρ of Out with | count -0.43; mention in-degree +0.61; artifact adoption +0.41; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| GPT-5 | +0.190 | -0.007 | +0.197 | 4.2 |
| o3 | +0.022 | -0.004 | +0.026 | 0.8 |
| Claude Opus 4 | -0.002 | -0.070 | +0.069 | 0.0 |
| Claude 3.7 Sonnet | -0.006 | +0.006 | -0.012 | -0.3 |
| Claude Opus 4.1 | -0.038 | -0.032 | -0.006 | -1.4 |
| Grok 4 | -0.080 | -0.046 | -0.034 | -3.0 |
| Gemini 2.5 Pro | -0.248 | -0.008 | -0.240 | -4.4 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.902 (cross-day N1), 1.000 (within-day N1w); held-out days |
| D unfitted | 0 | split-half ρ = -0.61 |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2424 agent messages, 10 human, 10 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
