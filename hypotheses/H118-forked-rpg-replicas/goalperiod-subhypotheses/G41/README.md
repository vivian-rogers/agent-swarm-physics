# H118 × G41: #41 (2026-05-11 → 05-15)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · 15 agents · rooms #best/#rest re-formed after the NE42 merge · 5 days · identical kickoffs.

## Why this period
Identical kickoffs; H107: the split is at 70–90% of final size within two hours (fast).

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- M(d ≥ 2) covers 0 and τ_D ≤ 4 active h (P4) [0.6].

## Result
*Run 2026-10-04 (exploratory, non-holdout). bge style_resid; gte in its own column; agent × bin bootstrap 95% intervals. Data: `data/processed/H118-forked-rpg-replicas/results/results.json`.*

| Quantity | Prediction | bge | gte | Reference |
| --- | --- | --- | --- | --- |
| M_late (memory, days ≥ 2) | covers 0 | -0.04 [-0.11, 0.03] | -0.14 [-0.19, -0.05] | 0 |
| q_∞^late | descriptive | 0.01 [-0.12, 0.13] | -0.22 [-0.36, -0.04] | q_rel 0.51 (0.45) |
| τ_D (active h) | ≤ 4 (descriptive) | 6.3 [2.15, 80.00] | 5.7 | unpowered |
| q_eq by day (bge) | – | 0.47, 0.36, 0.05, -0.08, 0.08 | – | q_lag 0.23, 0.29, 0.15, 0.05, 0.10 |

bge covers 0; gte gives negative memory (same-day anti-alignment: on days 3–5 the rooms point apart, q_eq −0.32 to −0.10 in gte). The verdict is downgraded to mixed by the two-model rule.


## Scorecard (period-specific axes)
C 1, I 0 (gte negative memory).

## Notes
