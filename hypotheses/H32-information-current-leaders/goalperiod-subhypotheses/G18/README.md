# H32 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** mixed (transfer, split-half ρ +0.24; P5 fail)
**Verdict (1b):** mixed (ledger exposure: T +0.177% p 0.024, split-half ρ +0.02; gte p 0.048; style-resid p 0.048)
**Role:** replication (exploratory)
**Period:** regime I · mode C (shared objective) · 8 agents · 1 room with ≥ 20 agent messages · 10 days. No splits (one unit per goal period).

## Why this period
22 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 22 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G18/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.188% (null 95th pct +0.026%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.172% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.24 (n = 8); top odd/even = 9/13 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.1 (z_out 15.0); standout p = 0.585 | null replicas | none |
| Net current | top net source = o3 | – | descriptive |
| Φ (centralization) | Φ = 0.08; Gini(Out⁺) = 0.39; top share = 0.26 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.188%; 10%-trimmed T = +0.123% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| P5 humans as a source | human pseudo-agent Out +0.170% (rank 6 of 9; null p = 0.024); by message count it would rank 9 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.29; mention in-degree +0.38; artifact adoption +0.58; H02 timing -0.24 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.1 | +0.396 | +0.276 | +0.120 | 15.0 |
| o3 | +0.290 | +0.003 | +0.287 | 8.8 |
| Claude Haiku 4.5 | +0.285 | +0.063 | +0.222 | 13.1 |
| Claude Sonnet 4.5 | +0.228 | +0.299 | -0.070 | 9.8 |
| Claude 3.7 Sonnet | +0.213 | +0.256 | -0.042 | 7.0 |
| Gemini 2.5 Pro | +0.057 | -0.006 | +0.064 | 2.1 |
| GPT-5 | +0.022 | +0.245 | -0.223 | 1.4 |
| Grok 4 | +0.014 | +0.371 | -0.357 | 1.0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.24 |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 7038 agent messages, 22 human, 20 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
