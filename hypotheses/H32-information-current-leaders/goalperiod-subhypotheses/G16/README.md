# H32 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** failed (no transfer; P5 fail)
**Verdict (1b):** failed (ledger exposure: T -0.001% p 0.415, split-half ρ +0.75; gte p 0.048; style-resid p 0.524)
**Role:** exploratory
**Period:** regime I · mode F (free / none) · 7 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
27 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode F, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 27 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G16/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.005% (null 95th pct +0.016%) | p_T = 0.268 | fail |
| N1w within-day null (A1c) | T = +0.016% | p_T = 0.095 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.68 (n = 7); top odd/even = 5/11 | ρ = 0 | pass |
| Leader call (standout, A1) | top = o3 (z_out 3.5); standout p = 0.634 | null replicas | none |
| Net current | top net source = o3 | – | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.005%; 10%-trimmed T = +0.000% | p_T = 0.268; trimmed p = 0.415 | post hoc |
| P5 humans as a source | human pseudo-agent Out +0.001% (rank 5 of 8; null p = 0.415); by message count it would rank 8 | – | fail |
| Rivals: Spearman ρ of Out with | count -0.21; mention in-degree +0.46; artifact adoption +0.43; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| o3 | +0.068 | -0.030 | +0.098 | 3.5 |
| Claude Opus 4.1 | +0.046 | -0.021 | +0.066 | 1.1 |
| Claude Sonnet 4.5 | +0.022 | +0.013 | +0.009 | 1.3 |
| Grok 4 | +0.018 | -0.005 | +0.022 | 0.7 |
| GPT-5 | -0.002 | +0.021 | -0.023 | -0.1 |
| Gemini 2.5 Pro | -0.058 | -0.023 | -0.035 | -1.1 |
| Claude 3.7 Sonnet | -0.059 | +0.079 | -0.138 | -0.8 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.268 (cross-day N1), 0.095 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.68 |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1924 agent messages, 27 human, 10 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
