# H118 × G37: #37 Pick your own goal (2026-03-30 → 04-01)

**Verdict:** supported
**Role:** exploratory (replication)
**Period:** regime III · 12 agents · rooms #best/#rest · 3 days · identical kickoffs.

## Why this period
Identical kickoffs; H107: the split grows from zero (r₁ 0.09), so damage spreads slowly here if anywhere.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- M(d ≥ 2) covers 0 and τ_D ≤ 4 active h (P4) [0.4; H107's slow growth argues for τ_D of days here].

## Result
*Run 2026-10-04 (exploratory, non-holdout). bge style_resid; gte in its own column; agent × bin bootstrap 95% intervals. Data: `data/processed/H118-forked-rpg-replicas/results/results.json`.*

| Quantity | Prediction | bge | gte | Reference |
| --- | --- | --- | --- | --- |
| M_late (memory, days ≥ 2) | covers 0 | 0.07 [-0.03, 0.23] | 0.06 [-0.05, 0.20] | 0 |
| q_∞^late | descriptive | 0.20 [-0.06, 0.51] | 0.11 [-0.19, 0.44] | q_rel 0.51 (0.49) |
| τ_D (active h) | ≤ 4 (descriptive) | 0.55 [0.25, 80.00] | 1.6 | unpowered |
| q_eq by day (bge) | – | 0.32, 0.33, 0.03 | – | q_lag 0.01, 0.11, 0.10 |

Small rooms (3 + 9 agents, 3 days); wide intervals.


## Scorecard (period-specific axes)
C 1 (memory test calibrated on the real skeleton), I 1 (replicates the G35 memory result).

## Notes
