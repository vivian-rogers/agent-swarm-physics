# H32 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-23)

**Verdict:** supported (transfer, split-half ρ +0.64)
**Role:** exploratory
**Period:** regime I · mode K (competition) · 10 agents · 1 room with ≥ 20 agent messages · 10 days. No splits (one unit per goal period).

## Why this period
mode K (competition) comparison of transfer and centralization.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode K: no mode-specific expectation.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G27/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.116% (null 95th pct +0.018%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.103% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.64 (n = 10); top odd/even = 18/16 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.5 (z_out 14.3); standout p = 0.293 | null replicas | none |
| Net current | top net source = Claude Opus 4.5 | – | descriptive |
| Φ (centralization) | Φ = 0.08; Gini(Out⁺) = 0.45; top share = 0.28 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.116%; 10%-trimmed T = +0.058% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.47; mention in-degree +0.71; artifact adoption +0.69; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.5 | +0.325 | +0.022 | +0.303 | 14.3 |
| Claude Haiku 4.5 | +0.204 | +0.073 | +0.131 | 8.4 |
| GPT-5.2 | +0.200 | -0.000 | +0.200 | 5.6 |
| Claude Sonnet 4.5 | +0.115 | +0.166 | -0.050 | 5.9 |
| Gemini 3 Pro | +0.114 | +0.039 | +0.075 | 5.0 |
| Claude 3.7 Sonnet | +0.095 | +0.288 | -0.193 | 3.5 |
| GPT-5.1 | +0.054 | +0.245 | -0.192 | 1.6 |
| GPT-5 | +0.043 | +0.119 | -0.076 | 2.5 |
| Gemini 2.5 Pro | +0.014 | -0.013 | +0.028 | 0.7 |
| DeepSeek-V3.2 | -0.004 | +0.221 | -0.225 | -0.5 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.64 |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 3743 agent messages, 7 human, 20 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
