# H87 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 15 agents · 4 days · 309 forced erasures (F) and 396 pseudo-erasures (P) with an own artifact.

## Why this period
A replication point for the common estimator (layer 1): the call-scale κ table on every regime-III non-holdout period with ≥ 300 forced erasures, so periods are comparable points, not independent tests.

## Prediction
*Templated replication prediction, written 2026-10-04 ~20:07 UTC in the card (row R), before running on this period.*
- Rows C (context), A (own artifact), M (memory note), G (chat reads), Q (history search) on F vs P events; I_c in bits (Miller–Madow, within agent × period permutation floor), ΔV_c in commits per 20 calls (Poisson DiD or scramble cost), κ_c = ΔV_c / I_c with a paired agent-day bootstrap (200 draws).
- **Verdict rule:** supported if κ_C > 0 with CI excluding 0 and κ_C exceeds every identified row's κ (Amendment A1: identified = I CI lower bound > 0.02 bits); failed if κ_C's CI includes 0; mixed otherwise.
- *Clarification after the run (2026-10-04, disclosed):* A1 is applied to the context row as well, so κ_C counts only when I_C is identified. A period whose erasure cost is positive (CI excluding 0) but whose I_C is not identified is *mixed*. Verdict under the original point rule: failed.
- *Counts against:* the context row is not the most valuable channel per bit.

## Result
*Run 2026-10-04 (`analysis/run.py` → `data/processed/H87-kappa-channel-table/results/results.json`, block `replication`).*

| Row | I (bits) [95% CI] | ΔV (commits per 20 calls) [95% CI] | ΔV_rel | κ (commits per 20 calls per bit) | identified |
| --- | --- | --- | --- | --- | --- |
| C context window | -0.092 [-0.275, 0.118] | 0.629 [0.341, 0.869] | 0.435 | n.i. | no |
| A own artifact | 0.256 [0.121, 0.381] | 0.376 [-0.860, 1.473] | 0.199 | 1.468 [-4.207, 7.384] | yes |
| M memory note | 0.081 [-0.025, 0.203] | 0.053 [-0.971, 0.952] | 0.043 | n.i. | no |
| G chat reads | 0.013 [-0.105, 0.119] | 0.530 [-1.150, 1.759] | 0.659 | n.i. | no |
| Q history search | 0.010 [-0.012, 0.041] | — | — | n.i. | no |

- For C, ΔV is the erasure cost (placebo minus scramble) and ΔV_rel its share of placebo output; I_C = I_P − I_F (0.279 − 0.371).
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (the context row beats its placebo) and I (consistency of the channel ranking across periods) in the main card.
