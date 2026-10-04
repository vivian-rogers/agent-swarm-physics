# H32 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** supported (transfer, split-half ρ +0.57)
**Verdict (1b):** supported (ledger exposure: T +0.082% p 0.024, split-half ρ +0.58; gte p 0.048; style-resid p 0.048)
**Role:** replication (exploratory)
**Period:** regime III · mode I (each agent its own objective) · 15 agents · 2 rooms with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
several populated rooms: exposure contrast (seen vs unseen) against the common-drive rival; NE42 A-B-A room merge.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode I, so I expect T at or below the median period (P10a).
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Exposure (P8):** ΔG for messages j saw exceeds ΔG for the same senders' simultaneous messages in rooms j was not in; the unseen gain's 90% CI includes 0.
- **NE42 (P9):** after the split: the #39 cross-room pairs are again unexposed, ΔG ≈ 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G41/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.088% (null 95th pct +0.014%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.062% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.57 (n = 13); top odd/even = 26/24 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.7 (z_out 7.3); standout p = 0.293 | null replicas | none |
| Net current | top net source = Gemini 3.1 Pro | – | descriptive |
| Φ (centralization) | Φ = 0.24; Gini(Out⁺) = 0.72; top share = 0.31 | 0 = equal, 1 = star | descriptive |
| P8 exposure contrast | seen beyond unseen +0.087% (p 0.024); unseen -0.007% (p 0.366) | shift null | pass |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.088%; 10%-trimmed T = +0.049% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.33; mention in-degree -0.24; artifact adoption +0.14; H02 timing +0.31 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.7 | +0.854 | +0.542 | +0.312 | 7.3 |
| Gemini 3.1 Pro | +0.748 | +0.198 | +0.550 | 5.5 |
| GPT-5.5 | +0.633 | +0.356 | +0.277 | 4.3 |
| GPT-5.4 | +0.315 | +0.036 | +0.279 | 3.6 |
| Claude Haiku 4.5 | +0.081 | +0.027 | +0.054 | 1.1 |
| Claude Opus 4.6 | +0.057 | -0.072 | +0.130 | 1.1 |
| GPT-5.2 | +0.057 | +0.050 | +0.007 | 0.8 |
| Claude Sonnet 4.6 | +0.017 | +0.044 | -0.026 | 0.6 |
| Claude Opus 4.5 | -0.002 | +0.070 | -0.072 | 0.3 |
| Kimi K2.6 | -0.009 | +1.129 | -1.138 | 0.1 |
| Gemini 2.5 Pro | -0.022 | +0.037 | -0.060 | 0.1 |
| Claude Sonnet 4.5 | -0.039 | +0.075 | -0.115 | -0.1 |
| GPT-5.1 | -0.058 | -0.014 | -0.043 | -0.8 |
| DeepSeek-V3.2 | -0.150 | +0.004 | -0.154 | -1.3 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.57 |
| H comparative (vs common drive) | 1 | exposure contrast passes |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2146 agent messages, 7 human, 69 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
