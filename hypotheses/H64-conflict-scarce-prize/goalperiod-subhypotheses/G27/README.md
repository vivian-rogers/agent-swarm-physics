# H64 × G27: Juice Shop hacking competition (2026-01-12 → 2026-01-23)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode K · 10 agents · 1 room(s) · 10 days. Units: one unit. Prize class (pre-registered): **competition**.

## Why this period
A competition with a single winner live for the whole period (`has_competition`): the prize contrast P1 tests whether competition alone produces antagonism.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** A rival-exclusive prize is live for the whole period (a single winner). H64 predicts **elevated antagonism**: r_p above the prize-free median and/or excess antagonistic pairs (p_AF ≤ 0.05). R-protocol (H37) predicts the prize-free level. My credence for H64's direction here: 0.25.


## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 27 | 1423 | 0.018 [0.013, 0.025] | 0.046 [0.038, 0.056] | 0.64 [0.61, 0.67] | 0 vs 0.05 (1.000) | 0 |

Competition: r_p 0.0183 above the prize-free median 0.0094; excess antagonistic pairs: no.

## Scorecard (period-specific axes)
- **C (adequacy):** antagonism excess against the calibrated agent-field null with cluster-robust pair tests.

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`. Holdout masked (`holdout_mask`); no held-out day enters.
