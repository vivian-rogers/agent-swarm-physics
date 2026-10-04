# H32 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-09)

**Verdict:** mixed (transfer, split-half ρ +0.21; P6a pass, P6b fail)
**Role:** exploratory
**Period:** regime I · mode C (shared objective) · 10 agents · 1 room with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

## Why this period
ground truth for the leader call (card: Candidate goal periods).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **P6a:** over the whole week, DeepSeek-V3.2 (agent 17, the elected leader) is not the top source (Out rank > 3 of 10). [0.55]
- **P6b:** after the election decision (2026-01-09 18:59:29 UTC, H11 vote codes) to the end of that day, DeepSeek's pooled Out* is the largest of all agents. [0.30]
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G26/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.056% (null 95th pct +0.018%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.071% | p_T = 0.143 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.21 (n = 10); top odd/even = 15/18 | ρ = 0 | pass |
| Leader call (standout, A1) | top = GPT-5.2 (z_out 7.3); standout p = 0.366 | null replicas | none |
| Net current | top net source = GPT-5.2 | – | descriptive |
| Φ (centralization) | Φ = 1.00; Gini(Out⁺) = 0.70; top share = 0.36 | 0 = equal, 1 = star | descriptive |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.056%; 10%-trimmed T = -0.007% | p_T = 0.024; trimmed p = 0.610 | post hoc |
| P6a DeepSeek not top over the week | DeepSeek-V3.2 Out rank 5 of 10 | – | pass |
| P6b DeepSeek top after the decision | pooled Out* after 01-09 18:59: DeepSeek rank 7 of 10 (ΔG -0.001%, z 0.1); top = Claude Haiku 4.5 (+0.655%, z 7.0) | – | fail |
| Rivals: Spearman ρ of Out with | count -0.33; mention in-degree +0.03; artifact adoption +0.22; H02 timing -0.14 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| GPT-5.2 | +0.333 | -0.052 | +0.385 | 7.3 |
| Claude Opus 4.5 | +0.301 | -0.008 | +0.309 | 7.8 |
| Gemini 3 Pro | +0.255 | +0.045 | +0.210 | 6.6 |
| GPT-5 | +0.040 | +0.225 | -0.185 | 1.5 |
| DeepSeek-V3.2 | -0.006 | +0.050 | -0.055 | 0.0 |
| Claude 3.7 Sonnet | -0.007 | -0.207 | +0.200 | -0.1 |
| Claude Haiku 4.5 | -0.067 | +0.176 | -0.243 | -1.6 |
| GPT-5.1 | -0.079 | +0.325 | -0.404 | -2.1 |
| Claude Sonnet 4.5 | -0.085 | +0.010 | -0.095 | -1.7 |
| Gemini 2.5 Pro | -0.122 | -0.000 | -0.122 | -4.5 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | p_T = 0.024 (cross-day N1), 0.143 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.21 |
| G ground truth | 1 | P6a DeepSeek not top over the week: pass; P6b DeepSeek top after the decision: fail |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2112 agent messages, 2 human, 10 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
