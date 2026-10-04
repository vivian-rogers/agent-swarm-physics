# H32 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** supported (transfer, split-half ρ +0.30; P5 pass)
**Role:** exploratory
**Period:** regime I · mode C (shared objective) · 6 agents · 1 room with ≥ 20 agent messages · 25 days. No splits (one unit per goal period).

## Why this period
1713 human messages: positive control (humans as a known source).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 1713 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G04/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.032% (null 95th pct +0.011%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.022% | p_T = 0.095 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.30 (n = 5); top odd/even = 5/0 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude 3.7 Sonnet (z_out 4.9); standout p = 0.049 | null replicas | called |
| Net current | top net source = o3 | – | descriptive |
| Φ (centralization) | Φ = 0.03; Gini(Out⁺) = 0.24; top share = 0.37 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.032%; 10%-trimmed T = +0.021% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| P5 humans as a source | human pseudo-agent Out +0.078% (rank 1 of 7; null p = 0.024); by message count it would rank 2 | – | pass |
| Rivals: Spearman ρ of Out with | count +0.10; mention in-degree +0.20; artifact adoption +0.50; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude 3.7 Sonnet | +0.058 | +0.057 | +0.001 | 4.9 |
| o3 | +0.036 | -0.003 | +0.039 | 4.1 |
| GPT-4.1 | +0.023 | -0.007 | +0.030 | 1.8 |
| Gemini 2.5 Pro | +0.020 | -0.009 | +0.029 | 1.5 |
| Claude Opus 4 | +0.019 | +0.141 | -0.122 | 1.6 |
| o4-mini | – | – | – | nan |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | p_T = 0.024 (cross-day N1), 0.095 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.30 |
| G ground truth | 2 | P5 humans as a source: pass |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 6544 agent messages, 1713 human, 50 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
