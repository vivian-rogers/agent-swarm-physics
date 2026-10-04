# H32 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** mixed (transfer, split-half ρ -0.02)
**Verdict (1b):** supported (ledger exposure: T +0.019% p 0.024, split-half ρ +0.03; gte p 0.048; style-resid p 0.048)
**Role:** replication (exploratory)
**Period:** regime II/III · mode C (shared objective) · 12 agents · 2 rooms with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
several populated rooms: exposure contrast (seen vs unseen) against the common-drive rival.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Exposure (P8):** ΔG for messages j saw exceeds ΔG for the same senders' simultaneous messages in rooms j was not in; the unseen gain's 90% CI includes 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G36/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.039% (null 95th pct +0.001%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.084% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = -0.02 (n = 11); top odd/even = 16/13 | ρ = 0 | fail |
| Leader call (standout, A1) | top = Claude Opus 4.5 (z_out 3.5); standout p = 0.561 | null replicas | none |
| Net current | top net source = Gemini 2.5 Pro | – | descriptive |
| Φ (centralization) | Φ = 1.46; Gini(Out⁺) = 0.61; top share = 0.31 | 0 = equal, 1 = star | descriptive |
| P8 exposure contrast | seen beyond unseen +0.045% (p 0.024); unseen -0.080% (p 0.927) | shift null | pass |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.039%; 10%-trimmed T = +0.043% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| Rivals: Spearman ρ of Out with | count -0.18; mention in-degree -0.28; artifact adoption +0.00; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.5 | +0.383 | +0.127 | +0.256 | 3.5 |
| Claude Haiku 4.5 | +0.305 | -0.075 | +0.380 | 3.9 |
| Gemini 2.5 Pro | +0.202 | -0.459 | +0.661 | 3.1 |
| Claude Sonnet 4.5 | +0.125 | +0.320 | -0.195 | 1.6 |
| Gemini 3.1 Pro | +0.110 | +0.097 | +0.014 | 2.2 |
| Claude Sonnet 4.6 | +0.088 | +0.085 | +0.004 | 1.5 |
| Claude Opus 4.6 | +0.013 | -0.092 | +0.105 | 0.3 |
| GPT-5.2 | -0.052 | -0.028 | -0.024 | -0.3 |
| GPT-5.1 | -0.052 | +0.055 | -0.107 | -0.1 |
| GPT-5.4 | -0.092 | +0.083 | -0.175 | -1.7 |
| DeepSeek-V3.2 | -0.442 | +0.223 | -0.666 | -3.8 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 0 | split-half ρ = -0.02 |
| H comparative (vs common drive) | 1 | exposure contrast passes |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1584 agent messages, 8 human, 16 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
