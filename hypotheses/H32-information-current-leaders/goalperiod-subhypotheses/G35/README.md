# H32 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** supported (transfer, split-half ρ +0.37)
**Verdict (1b):** failed (native leader test); general failed (ledger exposure: T +0.037% p 0.073, split-half ρ -0.01; gte p 0.048; style-resid p 0.048)
**Role:** native (round 1b: daily designated lead designers, DQ6; round 1: exploratory)
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

## Round 1b native: daily designated lead designers (DQ6)
*Prediction written 2026-10-04 16:45 UTC, before running.* **Seen beforehand:** round 1 for this period (above) and the card; DQ6's `ground_truth_labels` rows for #26, #35 and #44 (leader terms, lead designers, temporary leader; codes and times only); H29's round-1b native summary in its card status line (#35: designated leaders get 1.4x more replies per message, no broadcast pull; #26: the elected leader's broadcast pull rose most). No round-1b H32 statistic (ledger exposure, any variant) had been computed on any period.

**Design.** DQ6 names one lead designer per room per day on 03-16 (#rest 18, #best 23), 03-17 (19, 20) and 03-18 (6, 22). Six room-day segments; in each, Out* for every agent in that room with ≥ 3 messages in the segment. **Estimator:** O9's pooled-sender gain Out*_i (CV over 30-min blocks; one shared source coefficient over all receivers in the segment; null = 40 cross-day circular shifts of the sender timelines), with round 1b's **ledger exposure**: i's message counts as seen by j's message m iff it was posted in j's room before the start (`t_call`) of the call that produced m. Statistic: the lead designer's percentile rank within its room-day (1 = top), averaged over the six segments; null = exact permutation of ranks within segments.

**Predictions:**
- **N35a:** no leader premium: the mean percentile is not above chance at one-sided p < 0.05 [0.65].
- **N35b:** at most 3 of the 6 lead designers are in the top half of their room-day [0.6].

**Verdict rule:** *supported* (designated leaders are content sources) if the mean percentile exceeds chance at p < 0.05 and ≥ 4/6 are in the top half; *failed* if p ≥ 0.05 and ≤ 3/6; *mixed* otherwise.

### Result (round 1b, run 2026-10-04)
`analysis/r1b.py natives` → `r1b/natives.json`. Five room-days tested (on 03-17 the #rest lead designer, agent 19, posted < 3 messages in its room).

| Room-day | Lead designer | Rank / agents | z |
| --- | --- | --- | --- |
| 03-16 #rest | 18 | 7 / 9 | −1.5 |
| 03-16 #best | 23 | 3 / 3 | −0.5 |
| 03-17 #best | 20 | 1 / 3 | +1.3 |
| 03-18 #rest | 6 | 6 / 9 | +0.1 |
| 03-18 #best | 22 | 2 / 3 | +1.6 |

Mean percentile **0.43** (exact permutation p = 0.69); top half **1/5**. N35a and N35b pass (no leader premium). **Verdict (H32's leader claim here): failed**, as predicted. Designated daily leaders were not content sources; with H29 (1.4× more replies per message) this says they were *answered* more, not *followed* more in content.
