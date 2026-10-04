# H64 × G02: unsupervised weekend look-back (2025-05-10 → 2025-05-11)

**Verdict:** supported
**Verdict (1c):** supported (round 1c, stance v2.1)
**Role:** replication
**Period:** regime I · mode F · 4 agents · 1 room(s) · 2 days. Units: one unit. Prize class (pre-registered): **prize free**.

## Why this period
A shared-objective week with no rival-exclusive prize: a point of the prize-free floor (P2) on the phase diagram.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** No rival-exclusive prize is live in this period. H64 predicts **no antagonism beyond agent fields**: the cluster-robust count of significantly negative residual pairs within the calibrated agent-field null (p_AF > 0.05), and a confident position-opposition rate r_p near the prize-free median. Counts against H64 (the 'only' clause): p_AF ≤ 0.05 (antagonistic pairs without a prize).


## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 408 | 0.000 [0.000, 0.000] | 0.017 [0.017, 0.019] | 0.45 [0.45, 0.45] | 0 vs 0.09 (1.000) | 0 |

Prize-free floor: no unit with excess antagonistic pairs (p_AF ≤ 0.05). r_p 0.0000 vs prize-free median 0.0094.

## Scorecard (period-specific axes)
- **C (adequacy):** antagonism excess against the calibrated agent-field null with cluster-robust pair tests.

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`. Holdout masked (`holdout_mask`); no held-out day enters.

## Round 1c (stance v2.1, 2026-10-04)
*Pre-registered in the card (Round 1c, 22:12 UTC). Data: `data/processed/H64-conflict-scarce-prize/r1c/`.*

prize class prize_free; validated disagreement rate d_p 0.00% [0.00, 0.00] (confusion-corrected -0.81%; expected false-flag rate 0.49%); disagreeing pairs 0 vs label-noise null mean 0.00 (p 1.000). Prize-free median 0.96%.
