# H32 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** failed (no transfer; P5 fail, P7a pass, P7b fail, P7c pass)
**Verdict (1b):** failed (native leader test); general failed (ledger exposure: T +0.012% p 0.122, split-half ρ +0.39; gte p 0.048; style-resid p 0.190)
**Role:** native (round 1b: DQ6 leader window; round 1: exploratory)
**Period:** regime III · mode C (shared objective) · 17 agents · 2 rooms with ≥ 20 agent messages · 4 days. No splits (one unit per goal period).

## Why this period
ground truth for the leader call (card: Candidate goal periods); 59 human messages: positive control (humans as a known source); several populated rooms: exposure contrast (seen vs unseen) against the common-drive rival.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here.
- **Transfer (P1):** total exposure-conditioned content transfer T > 0 against the circular-shift null (p_T < 0.05). Mode C, so I expect T at or above the median period.
- **Stability (P3):** split-half Spearman ρ(Out_odd days, Out_even days) > 0.
- **Humans as a source (P5, positive control):** 59 human messages; the human pseudo-agent's Out exceeds the median agent's Out.
- **Exposure (P8):** ΔG for messages j saw exceeds ΔG for the same senders' simultaneous messages in rooms j was not in; the unseen gain's 90% CI includes 0.
- **P7a:** the temporary leader (agent 28) is not the top source in #best on 05-28/29: pooled Out* rank ≥ 3 among the #best agents present. [0.75]
- **P7b:** the operator (human pseudo-agent; 57 messages in #best) is the top source in #best. [0.55]
- **P7c:** same-room pair transfer exceeds cross-room; cross-room ΔG's 90% CI includes 0. [0.70]
- **Rivals (P4, P11, P12):** Out correlates with message count but ρ < 0.8; |ρ| with H02's timing influence < 0.3 where H02 covers the period; ρ with artifact adoption and mention in-degree > 0.
- **Verdict rule:** supported = p_T < 0.05 and split-half ρ > 0 (or Q p < 0.05 where not eligible); mixed = transfer without a stable or heterogeneous structure; failed = p_T ≥ 0.05. Ground-truth tests (P5–P7) decide the verdict where they apply.

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/G44/` (`result.json`, `gain.npz`). Figure: [`figures/currents.pdf`](figures/currents.pdf).* Units: % of held-out residual variance; ΔG = gain minus the median of 40 circular-shift replicas.

| Test | Observed | Null / reference | Outcome |
| --- | --- | --- | --- |
| P1 transfer T > 0 (p_T < 0.05) | T = -0.003% (null 95th pct +0.005%) | p_T = 0.220 | fail |
| N1w within-day null (A1c) | T = +0.015% | p_T = 0.095 | fail |
| P3 split-half ρ(Out) > 0 | ρ = +0.31 (n = 14); top odd/even = 25/24 | ρ = 0 | pass |
| Leader call (standout, A1) | top = Claude Opus 4.7 (z_out 3.0); standout p = 0.634 | null replicas | none |
| Net current | top net source = [Temporary] Fine-tuned Leader | – | descriptive |
| P8 exposure contrast | seen beyond unseen -0.003% (p 0.220); unseen -0.053% (p 0.707) | shift null | fail |
| A2 post hoc (folds with ≥ 20 training messages) | T = +0.124%; 10%-trimmed T = +0.073% | p_T = 0.024; trimmed p = 0.024 | post hoc |
| P5 humans as a source | human pseudo-agent Out +0.052% (rank 10 of 17; null p = 0.195); by message count it would rank 11 | – | fail |
| P7a temporary leader not top in #best | agent 28 pooled Out* rank 6 of 6 #best agents (ΔG -0.301%, z -1.5) | – | pass |
| P7b operator top in #best | humans rank 5 of 7 (ΔG +0.102%, z 1.0) | – | fail |
| P7c same-room > cross-room | same-room pairs -0.003% [-0.143, +0.122] (n 111); cross-room (unseen) -0.053% [-0.122, +0.016] (n 109) | – | pass |
| Rivals: Spearman ρ of Out with | count +0.69; mention in-degree +0.68; artifact adoption +0.46; H02 timing +0.37 | – | descriptive |

**Agent currents** (sorted by Out):

| Agent | Out (%) | In (%) | Net (%) | z_out |
| --- | --- | --- | --- | --- |
| Claude Opus 4.7 | +0.442 | +0.262 | +0.180 | 3.0 |
| GPT-5.5 | +0.335 | +0.557 | -0.222 | 1.3 |
| Claude Opus 4.5 | +0.305 | +0.156 | +0.149 | 3.2 |
| DeepSeek-V3.2 | +0.211 | +0.015 | +0.196 | 3.3 |
| Claude Opus 4.6 | +0.162 | +0.143 | +0.018 | 2.0 |
| Gemini 3.1 Pro | +0.143 | -0.079 | +0.222 | 3.2 |
| Claude Sonnet 4.6 | +0.137 | +0.235 | -0.098 | 2.6 |
| Claude Haiku 4.5 | +0.119 | +0.130 | -0.011 | 1.7 |
| Claude Sonnet 4.5 | +0.080 | +0.154 | -0.075 | 1.7 |
| Kimi K2.6 | -0.019 | +0.153 | -0.171 | 0.4 |
| GPT-5.4 | -0.032 | -0.059 | +0.028 | 0.5 |
| GPT-5.1 | -0.112 | – | – | -1.2 |
| GPT-5.2 | -0.141 | +0.067 | -0.208 | -3.2 |
| Claude Opus 4.8 | -0.593 | +0.035 | -0.628 | -3.4 |
| Gemini 3.5 Flash | -0.792 | -0.168 | -0.623 | -3.5 |
| [Temporary] Fine-tuned Leader | -0.815 | -2.280 | +1.465 | -4.2 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | p_T = 0.220 (cross-day N1), 0.095 (within-day N1w); held-out days |
| D unfitted | 1 | split-half ρ = +0.31 |
| G ground truth | 1 | P5 humans as a source: fail; P7a temporary leader not top in #best: pass; P7b operator top in #best: fail; P7c same-room > cross-room: pass |
| H comparative (vs common drive) | 0 | exposure contrast fails |

## Notes
- 2026-10-03: folder and prediction written before any H32 statistic was computed on this period. Counts used: 1743 agent messages, 59 human, 36 automated.
- 2026-10-03: round 1 run; verdict by the card's rules (amendment A1).
- 2026-10-03: P7c passes only vacuously: both same-room and cross-room pair means are ≈ 0 under the primary fit (no transfer in #44). Under post-hoc A2 (folds with ≥ 20 training messages) #44 shows transfer (+0.124%, p 0.024); the segment tests (P7a, P7b) are unaffected by A2.

## Round 1b native: the installed leader over its DQ6 window
*Prediction written 2026-10-04 16:45 UTC, before running.* **Seen beforehand:** round 1 for this period (above) and the card; DQ6's `ground_truth_labels` rows for #26, #35 and #44 (leader terms, lead designers, temporary leader; codes and times only); H29's round-1b native summary in its card status line (#35: designated leaders get 1.4x more replies per message, no broadcast pull; #26: the elected leader's broadcast pull rose most). No round-1b H32 statistic (ledger exposure, any variant) had been computed on any period.

**Why redo it.** Round 1 used #best on 05-28/29. DQ6's `temporary_finetuned_leader` row puts agent 28's term at **05-26 19:15 UTC → 06-01**; only #44's non-holdout days are used (05-26 19:15 → the end of 05-29).

**Estimator:** O9's pooled-sender gain Out*_i (CV over 30-min blocks; one shared source coefficient over all receivers in the segment; null = 40 cross-day circular shifts of the sender timelines), with round 1b's **ledger exposure**: i's message counts as seen by j's message m iff it was posted in j's room before the start (`t_call`) of the call that produced m. Segment = #best targets in the window; sources = #best agents present plus the human pseudo-agent (operator).

**Predictions:**
- **N44a:** agent 28 ranks in the bottom half of #best's agents by Out* [0.7].
- **N44b:** the operator (human pseudo-agent) is not the top source [0.6].

**Verdict rule:** *supported* if agent 28 or the operator ranks 1st with z ≥ 2; *failed* if agent 28 is in the bottom half and the operator is not top; *mixed* otherwise.

### Result (round 1b, run 2026-10-04)
`analysis/r1b.py natives` → `r1b/natives.json` (#best, 05-26 19:15 → end of 05-29; 413 targets; 40 shifts).

| Source | ΔG (%) | z |
| --- | --- | --- |
| Claude Opus 4.7 | +0.81 | 9.1 |
| Kimi K2.6 | +0.80 | 21.1 |
| Claude Opus 4.8 | +0.70 | 13.4 |
| GPT-5.5 | +0.44 | 11.9 |
| Gemini 3.5 Flash | +0.01 | 0.1 |
| operator (humans) | +0.01 | 0.1 |
| [Temporary] Fine-tuned Leader (28) | **−0.18** | **−2.4** |

N44a (agent 28 bottom half) pass: **last of 6**; N44b (operator not top) pass: **6th of 7**. **Verdict: failed**, as predicted. Over the full DQ6 window the installed leader is the weakest source in its room, again below its own base model (Kimi K2.6), confirming round 1's two-day result.
