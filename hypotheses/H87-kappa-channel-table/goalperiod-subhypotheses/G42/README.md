# H87 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 14 agents · 5 days · 646 forced erasures (F) and 658 pseudo-erasures (P) with an own artifact.

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
| C context window | -0.014 [-0.107, 0.071] | 0.411 [0.210, 0.573] | 0.454 | n.i. | no |
| A own artifact | 0.021 [-0.002, 0.050] | 0.220 [-0.398, 0.840] | 0.120 | n.i. | no |
| M memory note | 0.043 [-0.023, 0.117] | 0.299 [-0.119, 0.617] | 0.470 | n.i. | no |
| G chat reads | -0.015 [-0.044, 0.024] | — | — | n.i. | no |
| Q history search | 0.000 [0.000, 0.000] | — | — | n.i. | no |

- For C, ΔV is the erasure cost (placebo minus scramble) and ΔV_rel its share of placebo output; I_C = I_P − I_F (0.152 − 0.166).
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (the context row beats its placebo) and I (consistency of the channel ranking across periods) in the main card.
