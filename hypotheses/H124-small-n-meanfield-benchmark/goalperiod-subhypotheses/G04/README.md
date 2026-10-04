# H124 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 26 active days. Units: 4a (2025-05-15→2025-05-21, 5 d), 4b (2025-05-22→2025-05-22, 1 d), 4c (2025-05-23→2025-06-18, 19 d), 4d (2025-06-18→2025-06-18, 1 d).

## Why this period
Primary (HH names #4). The longest N = 4 period: unit 4c alone has 19 days with a fixed roster (Claude Opus 4 joins at its start); 4a has 5 days. Units 4b and 4d are one day each and are not fitted. One side of native N1 (cooperation: one shared story and event). Layer role: primary + native N1.

## Prediction
*Written 2026-10-04 ~22:03 UTC, before running on this period (card predictions applied here; per-call talk spin unless stated).*
- P1: best of TAP / MS within 10% of exact ML on off-diagonal J and on σ_J (my credence 0.35); HH kill if none within 25%.
- P2: nMF ε_J > 0.10 (0.75).
- P3: MS ≤ TAP < nMF on ε_J (0.55); TAP may fail to converge in some rows.
- P5: real off-diagonal J near the circular-shift null (0.5): then the unit is uninformative for the coupling benchmark and the comparison is carried by the self-couplings (reported as such).
- P6 (1-min grid companion): activity spins nMF ε_J > 0.25 (0.6).
- N1: exact-ML mean off-diagonal talk coupling J̄ lower in G06 than G04 (0.55); same ranking in both (0.7).

## Result
*Run 2026-10-04 22:35–22:44 UTC (`analysis/run.py`); data `data/processed/H124-small-n-meanfield-benchmark/results/{percall,grid}.json`; figure `../../figures/benchmark.pdf`.* ε_J = off-diagonal relative error against exact ML on the same data, with day-bootstrap 95% intervals (200 replicates); "(k/4 rows)" = the method has a solution on only k rows (TAP: S/a₀ > 4/27); ✓ = off-diagonal J beyond the circular-shift null.

**Per-call talk clock (primary).**

| Unit | calls | max J_ii | ‖J_off‖ (shift-null q95) | ML noise ν_J | nMF | TAP | MS | nMF\|s | held-out LL gap nMF / nMF\|s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 4738 calls | 1.05 | 0.243 (0.201) ✓ | 0.58 | 0.39 [0.27, 0.58] | 0.04 [0.01, 0.18] (1/4 rows) | 1.28 [0.16, 20.25] | 0.29 [0.17, 0.71] | -0.0049 / -0.0032 |
| 4c | 19635 calls | 0.51 | 0.110 (0.121) | 0.80 | 0.08 [0.05, 0.17] | 0.05 [0.03, 0.11] | 0.03 [0.02, 0.06] | 0.19 [0.11, 0.38] | -0.0089 / -0.0000 |

**1-min parallel grid (companion; * = partial row cover).**

| Unit | 1-min talk: nMF / TAP / MS | 1-min activity: nMF / TAP / MS |
| --- | --- | --- |
| 4a | 0.07 / 0.03 / 0.01 | 0.23 / 0.11* / 0.11 |
| 4c | 0.08 / 0.05* / 0.05 | 0.31 / —* / 17.95 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 (HH) TAP or MS within 10% (full cover) | 1/2 units | mixed |
| HH kill: no method within 25% (full cover) | 1/2 units with none | not met |
| P2 nMF > 0.10 | 1/2 units | mixed |
| P5 off-diagonal J near the null | 1/2 units inside the null | mixed |

**Native N1 (cooperation #4 vs competition #6).** Mean off-diagonal ML talk coupling J̄: 4a +0.049 [-0.000, +0.085], 4c +0.011 [-0.014, +0.036]; 6a +0.051 [+0.019, +0.068], 6b +0.004 [-0.042, +0.043]. No cooperation–competition difference (the intervals overlap; J̄ is at noise level in 3/4 units). The ranking differs between units of the same period (4c: MS < TAP < nMF; 4a, 6a, 6b: nMF best among full-cover methods), so it follows persistence, not the goal type. **N1 verdict: failed** (J̄ prediction not borne out; ranking not period-invariant).


## Scorecard (period-specific axes)
C 1 (exact ML wins held-out log-likelihood; stratified nMF within 0.005 nats/call) · F 1 (S4 synthetic on this regime's schedules) · H 1 (R0 fails except at weak persistence; R2 holds for plain TAP/MS when J_ii > 0.6).

## Notes
