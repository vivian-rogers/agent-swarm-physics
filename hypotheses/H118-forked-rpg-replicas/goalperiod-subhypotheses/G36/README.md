# H118 × G36: #36 Interact with outside agents (2026-03-23 → 03-27)

**Verdict:** supported
**Role:** exploratory (replication)
**Period:** 36a regime II (1 day), 36b–c regime III (4 days) · 12 agents · rooms #best/#rest · identical kickoffs.

## Why this period
Identical kickoffs: both rooms restart from one shared state. The regime-III days give a band point; 36a is the one same-basis (regime II) baseline day for G35.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- M(d ≥ 2) covers 0 and τ_D ≤ 4 active h on the regime-III days (P4) [0.45]. H107 found no final split here (E_F n.s.), so q_∞^late should sit near q_rel (rooms indistinguishable) and at the top of the band.

## Result
*Run 2026-10-04 (exploratory, non-holdout). bge style_resid; gte in its own column; agent × bin bootstrap 95% intervals. Data: `data/processed/H118-forked-rpg-replicas/results/results.json`.*

| Quantity | Prediction | bge | gte | Reference |
| --- | --- | --- | --- | --- |
| M_late (memory, days ≥ 2) | covers 0 | 0.02 [-0.05, 0.12] | -0.00 [-0.09, 0.11] | 0 |
| q_∞^late | descriptive | 0.65 [0.38, 0.73] | 0.65 [0.37, 0.71] | q_rel 0.74 (0.74) |
| τ_D (active h) | ≤ 4 (descriptive) | 80 [0.25, 80.00] | 1.3 | unpowered |
| q_eq by day (bge) | – | 0.66, 0.32, 0.66, 0.64 | – | q_lag 0.53, 0.47, 0.52, 0.56 |

Regime-III days (36b–c) only. The rooms are close to identical replicas (q_∞ 0.65 vs q_rel 0.74), matching H107's absent final split.


## Scorecard (period-specific axes)
C 1 (memory test calibrated on the real skeleton), I 1 (replicates the G35 memory result).

## Notes
