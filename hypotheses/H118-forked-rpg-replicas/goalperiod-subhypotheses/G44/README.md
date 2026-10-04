# H118 × G44: #44 (2026-05-26 → 05-29)

**Verdict:** mixed
**Role:** exploratory (replication + native (control))
**Period:** regime III · 17–18 agents · rooms #best/#rest with room-specific kickoffs (cosine 0.81) · 4 days (roster joins 05-28).

## Why this period
Room-specific kickoffs (different fields): the second control.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- q_∞^late below the band median (P5) [0.6]. M(d ≥ 2) covers 0 (P4) [0.5].

## Result
*Run 2026-10-04 (exploratory, non-holdout). bge style_resid; gte in its own column; agent × bin bootstrap 95% intervals. Data: `data/processed/H118-forked-rpg-replicas/results/results.json`.*

| Quantity | Prediction | bge | gte | Reference |
| --- | --- | --- | --- | --- |
| M_late (memory, days ≥ 2) | covers 0 | -0.07 [-0.12, -0.00] | -0.02 [-0.09, 0.06] | 0 |
| q_∞^late | descriptive | -0.15 [-0.24, -0.02] | -0.20 [-0.33, -0.03] | q_rel 0.54 (0.56) |
| τ_D (active h) | ≤ 4 (descriptive) | 1.6 [0.25, 80.00] | 1.6 | unpowered |
| q_eq by day (bge) | – | 0.08, -0.30, -0.23, -0.08 | – | q_lag -0.06, -0.13, -0.14, -0.12 |
| control: q_∞ < band median | below | -0.15 < 0.37 | -0.20 < 0.60 | met |

Negative memory in bge (−0.07 [−0.12, −0.00]): on a given day the rooms move apart more than across days. Different room kickoffs and heavy #best operator traffic (H100) are the likely room-specific daily drives. The control clause is met.


## Scorecard (period-specific axes)
C 1, G 1 (control met), I 0 (negative memory, unexplained).

## Notes
