# H64 × G36: interact with outside agents (2026-03-23 → 2026-03-27)

**Verdict:** supported
**Verdict (1c):** supported (round 1c, stance v2.1)
**Role:** replication
**Period:** regime II · mode C · 12 agents · 2 room(s) · 5 days. Units: 36a, 36b, 36c. Prize class (pre-registered): **prize free**.

## Why this period
A shared-objective week with no rival-exclusive prize: a point of the prize-free floor (P2) on the phase diagram.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** No rival-exclusive prize is live in this period. H64 predicts **no antagonism beyond agent fields**: the cluster-robust count of significantly negative residual pairs within the calibrated agent-field null (p_AF > 0.05), and a confident position-opposition rate r_p near the prize-free median. Counts against H64 (the 'only' clause): p_AF ≤ 0.05 (antagonistic pairs without a prize).


## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 36 | 704 | 0.006 [0.000, 0.016] | 0.030 [0.018, 0.046] | 0.63 [0.55, 0.70] | 0 vs 0.56 (1.000) | 0 |

Prize-free floor: no unit with excess antagonistic pairs (p_AF ≤ 0.05). r_p 0.0057 vs prize-free median 0.0094.

## Scorecard (period-specific axes)
- **C (adequacy):** antagonism excess against the calibrated agent-field null with cluster-robust pair tests.

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`. Holdout masked (`holdout_mask`); no held-out day enters.

## Round 1c (stance v2.1, 2026-10-04)
*Pre-registered in the card (Round 1c, 22:12 UTC). Data: `data/processed/H64-conflict-scarce-prize/r1c/`.*

prize class prize_free; validated disagreement rate d_p 0.43% [0.12, 0.78] (confusion-corrected -0.04%; expected false-flag rate 0.45%); disagreeing pairs 7 vs label-noise null mean 8.29 (p 0.652). Prize-free median 0.96%.
