# H32 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** supported (transfer, split-half ρ +0.37)
**Role:** exploratory
**Period:** regime II · mode C (shared objective) · 12 agents · 3 rooms with ≥ 20 agent messages · 5 days. No splits (one unit per goal period).

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
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G35/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.080% (null 95th pct +0.034%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.105% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.37 (n = 11); top odd/even = 16/20 | ρ = 0 | pass |
| Leader call (standout, A1) | top = GPT-5.2 (z_out 4.6); standout p = 0.927 | null replicas | none |
| Net current | top net source = GPT-5 | – | descriptive |
| Φ (centralization) | Φ = 0.18; Gini(Out⁺) = 0.55; top share = 0.21 | 0 = equal, 1 = star | descriptive |
| P8 exposure contrast | seen beyond unseen +0.078% (p 0.024); unseen -0.002% (p 0.415) | shift null | pass |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.080%; 10%-trimmed T = +0.057% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| Rivals: Spearman ρ of Out with | count +0.17; mention in-degree +0.23; artifact adoption +0.59; H02 timing – | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| GPT-5.2 | +0.294 | +0.055 | +0.239 | 4.6 |
| Claude Opus 4.6 | +0.278 | +0.058 | +0.220 | 3.8 |
| Claude Opus 4.5 | +0.260 | +0.085 | +0.175 | 5.8 |
| Claude Sonnet 4.5 | +0.241 | +0.144 | +0.097 | 4.7 |
| Gemini 3.1 Pro | +0.186 | +0.244 | -0.058 | 5.0 |
| Claude Sonnet 4.6 | +0.103 | +0.144 | -0.041 | 1.6 |
| GPT-5.4 | +0.052 | +0.205 | -0.153 | 1.2 |
| Claude Haiku 4.5 | +0.000 | +0.158 | -0.158 | -0.0 |
| GPT-5.1 | -0.013 | +0.401 | -0.414 | -0.1 |
| GPT-5 | -0.013 | -0.516 | +0.502 | -0.3 |
| DeepSeek-V3.2 | -0.096 | +0.068 | -0.163 | -1.5 |
| Gemini 2.5 Pro | -0.129 | +0.052 | -0.181 | -2.0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.37 |
| H comparative (vs common drive) | 1 | exposure contrast passes |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 2082 agent messages, 11 human, 27 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
