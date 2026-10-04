# H64 × G30: adopt a park (2026-02-09 → 2026-02-13)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode C · 11 agents · 1 room(s) · 5 days. Units: 30a, 30b. Prize class (pre-registered): **prize free**.

## Why this period
A shared-objective week with no rival-exclusive prize: a point of the prize-free floor (P2) on the phase diagram.

## Prediction
*Written 2026-10-04 20:10 UTC, before running on this period (card predictions and Amendment A1).*

**Replication layer.** No rival-exclusive prize is live in this period. H64 predicts **no antagonism beyond agent fields**: the cluster-robust count of significantly negative residual pairs within the calibrated agent-field null (p_AF > 0.05), and a confident position-opposition rate r_p near the prize-free median. Counts against H64 (the 'only' clause): p_AF ≤ 0.05 (antagonistic pairs without a prize).


## Result
**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).

| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |
| --- | --- | --- | --- | --- | --- | --- |
| 30 | 961 | 0.014 [0.009, 0.019] | 0.087 [0.058, 0.113] | 0.51 [0.49, 0.55] | 0 vs 0.02 (1.000) | 0 |

Prize-free floor: no unit with excess antagonistic pairs (p_AF ≤ 0.05). r_p 0.0135 vs prize-free median 0.0094.

## Scorecard (period-specific axes)
- **C (adequacy):** antagonism excess against the calibrated agent-field null with cluster-robust pair tests.

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`. Holdout masked (`holdout_mask`); no held-out day enters.
