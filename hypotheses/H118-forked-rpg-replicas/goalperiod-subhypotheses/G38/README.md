# H118 × G38: #38 Charity drive (2026-04-02 → 04-24)

**Verdict:** supported
**Role:** exploratory (replication + native (control))
**Period:** regime III · 12–14 agents · rooms #best/#rest with room-specific kickoffs (cosine 0.86) · 17 days. Splits: NE17 (04-14), roster joins 04-17 and 04-22, NE18 (04-20); the estimator uses the whole period as one relaxation after the kickoff (descriptive across the splits).

## Why this period
Room-specific kickoffs: the rooms are not replicas of one dynamics (different fields). The control for the overlap instrument: its late overlap should be below the identical-kickoff band.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- q_∞^late below the band median (P5) [0.6]. M(d ≥ 2) covers 0 (P4) [0.5].

## Result
*Run 2026-10-04 (exploratory, non-holdout). bge style_resid; gte in its own column; agent × bin bootstrap 95% intervals. Data: `data/processed/H118-forked-rpg-replicas/results/results.json`.*

| Quantity | Prediction | bge | gte | Reference |
| --- | --- | --- | --- | --- |
| M_late (memory, days ≥ 2) | covers 0 | 0.01 [-0.01, 0.03] | 0.01 [-0.01, 0.03] | 0 |
| q_∞^late | descriptive | 0.06 [-0.03, 0.13] | 0.17 [0.05, 0.25] | q_rel 0.66 (0.69) |
| τ_D (active h) | ≤ 4 (descriptive) | 0.25 [0.25, 80.00] | 11 | unpowered |
| q_eq by day (bge) | – | -0.04, 0.13, 0.02, 0.15, 0.07, 0.03, 0.01, 0.00, 0.07, 0.13, 0.11, 0.13, -0.02, -0.03, 0.01, -0.01, 0.11 | – | q_lag 0.05, 0.06, 0.02, 0.09, 0.06, 0.04, 0.02, 0.02, 0.05, 0.06, 0.06, 0.07, 0.03, 0.02, 0.04, 0.02, 0.03 |
| control: q_∞ < band median | below | 0.06 < 0.37 | 0.17 < 0.60 | met |

17 days spanning NE17, NE18 and two roster joins, read as one relaxation after the kickoff (descriptive across the splits). The rooms had different kickoffs, and their late overlap is the second lowest of all periods.


## Scorecard (period-specific axes)
C 1 (memory calibrated), G 1 (control met), I 1 (replication).

## Notes
