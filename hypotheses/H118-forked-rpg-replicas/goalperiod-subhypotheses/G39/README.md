# H118 × G39: #39 (2026-04-27 → 05-01)

**Verdict:** supported
**Role:** exploratory (replication)
**Period:** regime III · 15 agents · rooms #best/#rest (04-27 reshuffle: half of #best moved to #rest) · 5 days · identical kickoffs.

## Why this period
Identical kickoffs after a reshuffle; H107: split grows from zero.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- M(d ≥ 2) covers 0 and τ_D ≤ 4 active h (P4) [0.4].

## Result
*Run 2026-10-04 (exploratory, non-holdout). bge style_resid; gte in its own column; agent × bin bootstrap 95% intervals. Data: `data/processed/H118-forked-rpg-replicas/results/results.json`.*

| Quantity | Prediction | bge | gte | Reference |
| --- | --- | --- | --- | --- |
| M_late (memory, days ≥ 2) | covers 0 | 0.02 [-0.04, 0.08] | 0.00 [-0.04, 0.06] | 0 |
| q_∞^late | descriptive | 0.37 [0.11, 0.44] | 0.60 [0.33, 0.63] | q_rel 0.49 (0.66) |
| τ_D (active h) | ≤ 4 (descriptive) | 27 [0.25, 80.00] | 80 | unpowered |
| q_eq by day (bge) | – | 0.55, 0.55, 0.43, 0.40, 0.30 | – | q_lag 0.42, 0.44, 0.39, 0.40, 0.36 |

The 04-27 reshuffle period; no same-day memory.


## Scorecard (period-specific axes)
C 1 (memory test calibrated on the real skeleton), I 1 (replicates the G35 memory result).

## Notes
