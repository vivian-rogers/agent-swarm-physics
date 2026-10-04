# H124 × G03: Holiday: do whatever you'd like! Next goal will begin soon (2025-05-12 → 2025-05-14)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 3 active days. Units: 3 (2025-05-12→2025-05-14, 3 d).

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
| 3 | 2524 calls | 1.06 | 0.378 (0.544) | 1.10 | 0.57 [0.38, 0.64] | 0.04 [0.04, 0.38] (1/4 rows) | 1.83 [0.16, 3.86] | 0.36 [0.36, 0.87] | +0.1289 / +0.0520 |

**1-min parallel grid (companion; * = partial row cover).**

| Unit | 1-min talk: nMF / TAP / MS | 1-min activity: nMF / TAP / MS |
| --- | --- | --- |
| 3 | 0.08 / 0.24* / 0.30 | 0.26 / 0.14* / 0.68 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 (HH) TAP or MS within 10% (full cover) | 0/1 units | failed |
| HH kill: no method within 25% (full cover) | 1/1 units with none | met here |
| P2 nMF > 0.10 | 1/1 units | supported |
| P5 off-diagonal J near the null | 1/1 units inside the null | supported |


## Scorecard (period-specific axes)
C 1 (exact ML wins held-out log-likelihood; stratified nMF within 0.005 nats/call) · F 1 (S4 synthetic on this regime's schedules) · H 1 (R0 fails except at weak persistence; R2 holds for plain TAP/MS when J_ii > 0.6).

## Notes
