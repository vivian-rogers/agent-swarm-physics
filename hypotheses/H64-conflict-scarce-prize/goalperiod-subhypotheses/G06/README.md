# H64 × G06: merch store competition (2025-06-26 → 2025-07-15)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode K · 4 agents · 1 room(s) · 15 days. Units: 6a, 6b. Prize class (pre-registered): **competition**.

## Why this period
A competition with a single winner live for the whole period (`has_competition`): the prize contrast P1 tests whether competition alone produces antagonism.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** A rival-exclusive prize is live for the whole period (a single winner). H64 predicts **elevated antagonism**: r_p above the prize-free median and/or excess antagonistic pairs (p_AF ≤ 0.05). R-protocol (H37) predicts the prize-free level. My credence for H64's direction here: 0.25.


## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 6 | 626 | 0.016 [0.000, 0.049] | 0.040 [0.011, 0.088] | 0.41 [0.21, 0.56] | 0 vs 0.00 (1.000) | 1 |

Competition: r_p 0.0160 above the prize-free median 0.0094; excess antagonistic pairs: no.

## Scorecard (period-specific axes)
- **C (adequacy):** antagonism excess against the calibrated agent-field null with cluster-robust pair tests.

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`. Holdout masked (`holdout_mask`); no held-out day enters.
