# H124 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-25)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 5 active days. Units: 5 (2025-06-19→2025-06-25, 5 d).

## Why this period
Replication on a closed-roster N = 4 unit. Layer role: replication.

## Prediction
*Written 2026-10-04 ~22:03 UTC, before running on this period (card predictions applied here; per-call talk spin unless stated).*
- P1: best of TAP / MS within 10% of exact ML on off-diagonal J and on σ_J (my credence 0.35); HH kill if none within 25%.
- P2: nMF ε_J > 0.10 (0.75).
- P3: MS ≤ TAP < nMF on ε_J (0.55); TAP may fail to converge in some rows.
- P5: real off-diagonal J near the circular-shift null (0.5): then the unit is uninformative for the coupling benchmark and the comparison is carried by the self-couplings (reported as such).
- P6 (1-min grid companion): activity spins nMF ε_J > 0.25 (0.6).

## Result
*Run 2026-10-04 22:35–22:44 UTC (`analysis/run.py`); data `data/processed/H124-small-n-meanfield-benchmark/results/{percall,grid}.json`; figure `../../figures/benchmark.pdf`.* ε_J = off-diagonal relative error against exact ML on the same data, with day-bootstrap 95% intervals (200 replicates); "(k/4 rows)" = the method has a solution on only k rows (TAP: S/a₀ > 4/27); ✓ = off-diagonal J beyond the circular-shift null.

**Per-call talk clock (primary).**

| Unit | calls | max J_ii | ‖J_off‖ (shift-null q95) | ML noise ν_J | nMF | TAP | MS | nMF\|s | held-out LL gap nMF / nMF\|s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 5096 calls | 0.89 | 0.127 (0.208) | 1.01 | 0.17 [0.11, 0.27] | 0.04 [0.02, 0.12] (3/4 rows) | 0.31 [0.19, 6.44] | 0.62 [0.31, 0.72] | -0.0108 / -0.0009 |

**1-min parallel grid (companion; * = partial row cover).**

| Unit | 1-min talk: nMF / TAP / MS | 1-min activity: nMF / TAP / MS |
| --- | --- | --- |
| 5 | 0.03 / 0.01* / 0.01 | 0.64 / 0.63 / 0.63 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 (HH) TAP or MS within 10% (full cover) | 0/1 units | failed |
| HH kill: no method within 25% (full cover) | 0/1 units with none | not met |
| P2 nMF > 0.10 | 1/1 units | supported |
| P5 off-diagonal J near the null | 1/1 units inside the null | supported |


## Scorecard (period-specific axes)
C 1 (exact ML wins held-out log-likelihood; stratified nMF within 0.005 nats/call) · F 1 (S4 synthetic on this regime's schedules) · H 1 (R0 fails except at weak persistence; R2 holds for plain TAP/MS when J_ii > 0.6).

## Notes
