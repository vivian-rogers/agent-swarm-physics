# H118 × G42: #42 (2026-05-18 → 05-22)

**Verdict:** supported
**Role:** exploratory (replication)
**Period:** regime III · 15–16 agents · rooms #best/#rest · 5 days (roster join 05-20) · identical kickoffs.

## Why this period
Identical kickoffs; H107: the split is near full size on day 1, along inherited repos.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- M(d ≥ 2) covers 0 and τ_D ≤ 4 active h (P4) [0.55].

## Result
*Run 2026-10-04 (exploratory, non-holdout). bge style_resid; gte in its own column; agent × bin bootstrap 95% intervals. Data: `data/processed/H118-forked-rpg-replicas/results/results.json`.*

| Quantity | Prediction | bge | gte | Reference |
| --- | --- | --- | --- | --- |
| M_late (memory, days ≥ 2) | covers 0 | 0.04 [-0.00, 0.07] | 0.01 [-0.01, 0.04] | 0 |
| q_∞^late | descriptive | 0.83 [0.58, 0.83] | 0.79 [0.59, 0.82] | q_rel 0.85 (0.88) |
| τ_D (active h) | ≤ 4 (descriptive) | 80 [0.25, 80.00] | 80 | unpowered |
| q_eq by day (bge) | – | 0.84, 0.83, 0.84, 0.85, 0.79 | – | q_lag 0.77, 0.78, 0.81, 0.80, 0.77 |

The rooms stay close to identical replicas all week (q_eq 0.79–0.85 vs q_rel 0.83–0.90); memory interval just touches 0.


## Scorecard (period-specific axes)
C 1 (memory test calibrated on the real skeleton), I 1 (replicates the G35 memory result).

## Notes
