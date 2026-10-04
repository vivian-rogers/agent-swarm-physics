# H87 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 13 agents · 5 days · 575 forced erasures (F) and 598 pseudo-erasures (P) with an own artifact.

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
| C context window | 0.082 [-0.078, 0.214] | 0.616 [0.400, 0.877] | 0.444 | n.i. | no |
| A own artifact | 0.346 [0.237, 0.466] | 0.131 [-0.699, 0.628] | 0.107 | 0.379 [-1.989, 1.943] | yes |
| M memory note | 0.160 [0.070, 0.279] | -0.342 [-1.255, 0.110] | -0.294 | -2.133 [-8.843, 0.556] | yes |
| G chat reads | 0.144 [0.055, 0.237] | -0.028 [-0.535, 0.491] | -0.032 | -0.196 [-4.163, 4.186] | yes |
| Q history search | 0.000 [0.000, 0.000] | — | — | n.i. | no |

- For C, ΔV is the erasure cost (placebo minus scramble) and ΔV_rel its share of placebo output; I_C = I_P − I_F (0.504 − 0.422).
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (the context row beats its placebo) and I (consistency of the channel ranking across periods) in the main card.
