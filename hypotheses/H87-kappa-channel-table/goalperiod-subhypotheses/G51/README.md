# H87 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime III · 31 agents · 45 days · 12780 forced erasures (F) and 13665 pseudo-erasures (P) with an own artifact.

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
| C context window | 0.064 [0.031, 0.094] | 0.452 [0.378, 0.505] | 0.424 | 7.041 [4.858, 13.457] | yes |
| A own artifact | 0.143 [0.117, 0.171] | -0.119 [-0.280, 0.056] | -0.072 | -0.836 [-1.998, 0.390] | yes |
| M memory note | 0.040 [0.023, 0.058] | 0.076 [-0.041, 0.163] | 0.110 | 1.894 [-1.433, 4.780] | yes |
| G chat reads | 0.023 [0.007, 0.037] | 0.164 [-0.055, 0.412] | 0.263 | n.i. | no |
| Q history search | 0.001 [-0.002, 0.004] | 0.021 [-0.219, 0.443] | 0.022 | n.i. | no |

- For C, ΔV is the erasure cost (placebo minus scramble) and ΔV_rel its share of placebo output; I_C = I_P − I_F (0.323 − 0.259).
- **Templated verdict:** supported.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (the context row beats its placebo) and I (consistency of the channel ranking across periods) in the main card.
