# H32 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-05)

**Verdict:** mixed (transfer, split-half ρ +0.29; P5 fail)
**Verdict (1b):** mixed (ledger exposure: T +0.015% p 0.049, split-half ρ +0.04; gte p 0.190; style-resid p 0.048)
**Role:** exploratory
**Period:** regime I · mode M (teams / hidden saboteurs) · 7 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
16 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode M: no mode-specific expectation.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 16 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G12/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.029% (null 95th pct +0.010%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.046% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.29 (n = 7); top odd/even = 9/11 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4 (z_out 7.0); standout p = 0.439 | null replicas | none |
| Net current | top net source = Claude Opus 4.1 | – | descriptive |
| Φ (centralization) | Φ = 1.13; Gini(Out⁺) = 0.65; top share = 0.46 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.029%; 10%-trimmed T = +0.003% | p_T = 0.024; trimmed p = 0.415 | post hoc |
| P5 humans as a source | human pseudo-agent Out -0.008% (rank 5 of 8; null p = 0.610); by message count it would rank 8 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.82; mention in-degree -0.61; artifact adoption +0.37; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4 | +0.143 | +0.130 | +0.013 | 7.0 |
| Claude Opus 4.1 | +0.127 | +0.050 | +0.077 | 6.8 |
| Gemini 2.5 Pro | +0.029 | +0.005 | +0.023 | 1.6 |
| Claude 3.7 Sonnet | +0.015 | +0.091 | -0.077 | 0.7 |
| o3 | -0.026 | +0.004 | -0.030 | -0.9 |
| Grok 4 | -0.042 | -0.036 | -0.006 | -2.6 |
| GPT-5 | -0.043 | -0.043 | -0.000 | -3.6 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.29 |
| G ground truth | 0 | P5 humans as a source: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 3619 agent messages, 16 human, 10 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
