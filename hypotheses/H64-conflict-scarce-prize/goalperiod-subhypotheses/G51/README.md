# H64 × G51: maximize your private assigned role (2026-07-06 → 2026-09-04)

**Verdict:** supported
**Verdict (1c):** supported (round 1c, stance v2.1)
**Role:** replication
**Period:** regime III · mode I/K · 32 agents · 2 room(s) · 45 days. Units: 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l. Prize class (pre-registered): **rivalry no prize**.

## Why this period
Private roles with rival pairs that compete on shared metrics but have no single winner or settlement: the contrast class for 'scarce'.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** Role holders compete on shared metrics (rival pairs by role) but there is no single winner and no settlement. H64 predicts the **prize-free level** (r_p below the prize-free 75th percentile; no excess antagonistic pairs per unit). Counts against: excess pairs in most units.


## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 51a | 2225 | 0.006 [0.003, 0.010] | 0.035 [0.018, 0.053] | 0.67 [0.59, 0.74] | 0 vs 0.23 (1.000) | 1 |
| 51b | 617 | 0.006 [0.006, 0.006] | 0.053 [0.053, 0.053] | 0.60 [0.60, 0.60] | 0 vs 0.08 (1.000) | 0 |
| 51c | 2129 | 0.013 [0.009, 0.016] | 0.049 [0.029, 0.065] | 0.63 [0.55, 0.71] | 1 vs 0.09 (0.085) | 2 |
| 51d | 3029 | 0.013 [0.007, 0.025] | 0.045 [0.032, 0.065] | 0.66 [0.64, 0.68] | 0 vs 0.14 (1.000) | 1 |
| 51e | 1755 | 0.010 [0.005, 0.014] | 0.058 [0.043, 0.071] | 0.62 [0.56, 0.66] | 0 vs 0.15 (1.000) | 0 |
| 51f | 2569 | 0.010 [0.005, 0.013] | 0.033 [0.025, 0.041] | 0.67 [0.63, 0.69] | 0 vs 0.54 (1.000) | 1 |
| 51g | 7070 | 0.010 [0.006, 0.014] | 0.035 [0.027, 0.047] | 0.68 [0.64, 0.72] | 2 vs 0.10 (0.015) | 2 |
| 51h | 1657 | 0.008 [0.003, 0.014] | 0.032 [0.024, 0.041] | 0.66 [0.59, 0.71] | 0 vs 0.14 (1.000) | 0 |
| 51i | 737 | 0.028 [0.016, 0.041] | 0.068 [0.059, 0.077] | 0.59 [0.57, 0.61] | 0 vs 0.15 (1.000) | 0 |
| 51j | 645 | 0.014 [0.007, 0.025] | 0.036 [0.025, 0.054] | 0.72 [0.64, 0.76] | 0 vs 1.31 (1.000) | 0 |
| 51k | 533 | 0.006 [0.006, 0.006] | 0.013 [0.013, 0.013] | 0.66 [0.66, 0.66] | 0 vs 0.14 (1.000) | 0 |
| 51l | 704 | 0.007 [0.007, 0.007] | 0.040 [0.040, 0.040] | 0.68 [0.68, 0.68] | 0 vs 0.45 (1.000) | 0 |

#51 (all head replies): r_p 0.0106 [0.0085, 0.0132] vs prize-free 75th percentile 0.0135; units with excess pairs: 1 of 12.

## Scorecard (period-specific axes)
- **C (adequacy):** antagonism excess against the calibrated agent-field null with cluster-robust pair tests.

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`. Holdout masked (`holdout_mask`); no held-out day enters.

## Round 1c (stance v2.1, 2026-10-04)
*Pre-registered in the card (Round 1c, 22:12 UTC). Data: `data/processed/H64-conflict-scarce-prize/r1c/`.*

12 units; validated disagreement rate d_p 0.43–2.58% (period 0.85%, below the prize-free 75th percentile 1.51%); units with excess disagreeing pairs vs the label-noise null: 1/12 (51d, p 0.005).
