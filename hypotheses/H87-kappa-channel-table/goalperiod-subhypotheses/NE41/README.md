# H87 × NE41: the pooled call-scale κ table over forced erasures (regime III, non-holdout)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III non-holdout days (#36b → #51 head, without #43, #45–#50 and the #51 tail) · forced erasures F vs pseudo-erasures P (H70's frame) · period-stratified fixed effects (agent × period strata; CLAUDE.md exception (c): the erasure is the transition object).

## Why this period
The forced erasure is the village's one exogenous, frequent scramble (timing set by the 41-call cap). It wipes the context window and leaves every other channel open, so each channel's open-channel value can be measured against the same placebo.

## Prediction
*Written 2026-10-04 ~20:07 UTC, before any new-row statistic. H70's rows A, M, R, C were seen (card, prior knowledge).*
- **P1** order κ_A > κ_C > κ_G > κ_K > κ_M ≈ 0, adjacent paired P ≥ 0.9 (expected to fail at A > C given H70).
- **P2** κ_C within ±20% of 5.2; erasure cost 35–47%.
- **P3/P4** κ_G and κ_H CIs include 0; I_G, I_H ≤ 0.05 bits; human open share < 1%.
- **P7** memory size (top vs bottom tercile) × scramble: ΔV_rel within ±0.10.
- **P8** V40: no sign flip with CI excluding 0.
- *Kill:* κ_G ≥ κ_A, or all CIs overlap.

## Result
*Run 2026-10-04 20:48–20:51 UTC (`analysis/run.py` → `results/results.json`, block `NE41`); paired agent-day bootstrap B = 300 over 1,559 clusters; 18,760 F and 19,886 P events with an own artifact; strata agent × period.*

| Row | I_c (bits) [95% CI] | ΔV_c (commits / 20 calls) [95% CI] | ΔV_rel [95% CI] | κ_c | Status (A1) |
| --- | --- | --- | --- | --- | --- |
| C context window | 0.078 [0.052, 0.104] | 0.408 [0.361, 0.448] (erasure cost) | 0.41 [0.38, 0.44] | **5.2 [3.8, 7.9]** | identified |
| A own artifact | 0.137 [0.115, 0.159] | −0.083 [−0.207, +0.038] | −0.05 [−0.13, +0.03] | −0.6 [−1.6, +0.3] | identified; κ ≈ 0 |
| M memory note | 0.038 [0.017, 0.059] | +0.039 [−0.063, +0.136] | +0.05 [−0.07, +0.18] | n.i. | κ ≈ 0 (consistent) |
| G chat reads (agent senders; = H70's R) | 0.020 [0.007, 0.034] | +0.024 [−0.109, +0.124] | +0.04 [−0.17, +0.25] | n.i. | κ ≈ 0 (consistent) |
| Q history search | 0.001 [−0.002, +0.003] | −0.080 [−0.363, +0.299] | −0.08 [−0.33, +0.47] | n.i. | κ ≈ 0 (46 open F events) |
| H human messages | 0 (no repo-naming item) | dose: +0.061 [−0.149, +0.241] | +0.09 [−0.20, +0.40] | n.i. | κ ≈ 0 (consistent) |

- **Ordering (P1):** among identified rows, P(κ_C > κ_A) = 1.00 (300/300 paired draws). The HH ordering fails at its first step. No other pair is identified.
- **Own-scramble variants:** memory size (top vs bottom within-stratum tercile) × erasure ΔV_rel +0.01 [−0.06, +0.09] (P7 pass). Any agent chat item received in calls 1–5 × erasure ΔV_rel **+0.22 [+0.08, +0.36]**: chat after an erasure raises output beyond its placebo effect, while carrying 0.02 allocation bits.
- **V40 (P8):** C cost 0.31 [0.28, 0.33]; A **−0.19 [−0.25, −0.14]** (same sign as V20, now excluding 0); M +0.02, G +0.05, Q −0.07 (CIs include 0). No sign flip.
- **Return to own artifact** (P(X⁺ = A⁻ | a commit)): after F 0.96 when re-read vs 0.80 when not (n 3,103 / 2,814); at P 0.96 vs 0.76. Memory note names A⁻: 0.96 vs 0.86 (F), 0.94 vs 0.84 (P). The re-read premium is the same at the placebo: reading precedes writing (R2).
- P2 (κ_C within ±20% of 5.2, cost 35–47%): pass (5.24; 41%). P3 (κ_G CI includes 0, I_G ≤ 0.05): pass. P4 (human open share < 1%): pass trivially (0%).

**Reading.** The context window is the one channel whose loss costs commits per bit: 5.2 commits per 20 calls per bit. The own artifact carries the most allocation bits (0.14), but an agent that re-reads it after an erasure gains no more than one that re-reads at a placebo call. Memory, chat, search and human messages each carry ≤ 0.04 bits and buy no measurable commits. Verdict *mixed*: P1's ordering fails (κ_C ≫ κ_A), while its tail (κ_M ≈ 0) and P2–P4, P7, P8 hold.

## Scorecard (period-specific axes)
- **E:** the forced erasure is exogenous in timing (41-call cap); every row is a DiD against the same placebo.
- **F:** synthetic at real counts sized the ordering rule (A1): 0 wrong-direction claims in 50 replicates; true κ_C > κ_A found 0.92.
- **H:** R1 (artifact first) rejected; R2 (reading precedes writing) fits A; R0 fits all rows but C.
