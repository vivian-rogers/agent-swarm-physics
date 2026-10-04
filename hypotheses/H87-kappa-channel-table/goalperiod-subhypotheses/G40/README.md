# H87 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 14 agents · 5 days · 758 forced erasures (F) and 781 pseudo-erasures (P) with an own artifact.

## Why this period
A replication point for the common estimator (layer 1): the call-scale κ table on every regime-III non-holdout period with ≥ 300 forced erasures, so periods are comparable points, not independent tests.

## Prediction
*Templated replication prediction, written 2026-10-04 ~20:07 UTC in the card (row R), before running on this period.*
- Rows C (context), A (own artifact), M (memory note), G (chat reads), Q (history search) on F vs P events; I_c in bits (Miller–Madow, within agent × period permutation floor), ΔV_c in commits per 20 calls (Poisson DiD or scramble cost), κ_c = ΔV_c / I_c with a paired agent-day bootstrap (200 draws).
- **Verdict rule:** supported if κ_C > 0 with CI excluding 0 and κ_C exceeds every identified row's κ (Amendment A1: identified = I CI lower bound > 0.02 bits); failed if κ_C's CI includes 0; mixed otherwise.
- *Clarification after the run (2026-10-04, disclosed):* A1 is applied to the context row as well, so κ_C counts only when I_C is identified. A period whose erasure cost is positive (CI excluding 0) but whose I_C is not identified is *mixed*. Verdict under the original point rule: supported.
- *Counts against:* the context row is not the most valuable channel per bit.

## Result
*Run 2026-10-04 (`analysis/run.py` → `data/processed/H87-kappa-channel-table/results/results.json`, block `replication`).*

| Row | I (bits) [95% CI] | ΔV (commits per 20 calls) [95% CI] | ΔV_rel | κ (commits per 20 calls per bit) | identified |
| --- | --- | --- | --- | --- | --- |
| C context window | 0.051 [-0.005, 0.101] | 0.561 [0.352, 0.703] | 0.336 | n.i. | no |
| A own artifact | 0.084 [0.023, 0.169] | -0.689 [-1.574, 0.088] | -0.270 | -8.182 [-41.033, 0.369] | yes |
| M memory note | -0.003 [-0.030, 0.019] | -0.209 [-0.999, 0.192] | -0.127 | n.i. | no |
| G chat reads | -0.001 [-0.020, 0.020] | -0.171 [-0.614, 0.258] | -0.171 | n.i. | no |
| Q history search | 0.000 [0.000, 0.000] | — | — | n.i. | no |

- For C, ΔV is the erasure cost (placebo minus scramble) and ΔV_rel its share of placebo output; I_C = I_P − I_F (0.209 − 0.158).
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (the context row beats its placebo) and I (consistency of the channel ranking across periods) in the main card.
