# H32 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** mixed (transfer, split-half ρ +0.82; P5 fail)
**Verdict (1b):** supported (ledger exposure: T +0.209% p 0.024, split-half ρ +0.76; gte p 0.048; style-resid p 0.048)
**Role:** replication (exploratory)
**Period:** regime III · mode C (shared objective) · 14 agents · 2 rooms with ≥ 20 agent messages · 17 days. No splits (one unit per goal period).

## Why this period
28 human messages: positive control (humans as a known source); several populated rooms: exposure contrast (seen vs unseen) against the common-drive rival.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 28 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Exposure (P8):** ΔG for messages j saw exceeds ΔG for the same senders' simultaneous messages in rooms j was not in; the unseen gain's 90% CI includes 0.
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G38/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = +0.229% (null 95th pct +0.049%) | p_T = 0.024 | pass |
| N1w within-day null (A1c) | T = +0.187% | p_T = 0.048 | pass |
| P3 split-half ρ(Out) > 0 | ρ = +0.82 (n = 12); top odd/even = 16/20 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Sonnet 4.6 (z_out 7.3); standout p = 0.366 | null replicas | none |
| Net current | top net source = Gemini 3.1 Pro | – | descriptive |
| Φ (centralization) | Φ = 0.12; Gini(Out⁺) = 0.58; top share = 0.25 | 0 = equal, 1 = star | descriptive |
| P8 exposure contrast | seen beyond unseen +0.229% (p 0.024); unseen +0.017% (p 0.073) | shift null | pass |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.229%; 10%-trimmed T = +0.126% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| P5 humans as a source | human pseudo-agent Out +0.106% (rank 8 of 14; null p = 0.024); by message count it would rank 13 | – | fail |
| Rivals: Spearman ρ of Out with | count +0.12; mention in-degree -0.01; artifact adoption +0.55; H02 timing +0.06 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Sonnet 4.6 | +0.841 | +0.814 | +0.027 | 7.3 |
| Claude Opus 4.6 | +0.807 | +0.926 | -0.119 | 5.6 |
| Gemini 3.1 Pro | +0.544 | +0.114 | +0.430 | 6.3 |
| GPT-5.2 | +0.411 | +0.044 | +0.367 | 5.9 |
| Claude Opus 4.5 | +0.290 | -0.010 | +0.300 | 4.4 |
| GPT-5.1 | +0.137 | +0.288 | -0.152 | 2.3 |
| Claude Opus 4.7 | +0.133 | +0.529 | -0.395 | 3.2 |
| GPT-5.4 | +0.076 | -0.006 | +0.082 | 0.8 |
| Claude Sonnet 4.5 | +0.052 | +0.286 | -0.233 | 1.1 |
| Claude Haiku 4.5 | +0.046 | +0.028 | +0.017 | 0.3 |
| GPT-5 | +0.031 | +0.152 | -0.121 | 0.4 |
| Kimi K2.6 | +0.006 | – | – | 0.5 |
| DeepSeek-V3.2 | -0.128 | +0.051 | -0.179 | -2.0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | p_T = 0.024 (cross-day N1), 0.048 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.82 |
| G ground truth | 0 | P5 humans as a source: fail |
| H comparative (vs common drive) | 1 | exposure contrast passes |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 4558 agent messages, 28 human, 144 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
