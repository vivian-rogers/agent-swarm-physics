# H124 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-12)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 18 active days. Units: 8 (2025-07-18→2025-08-12, 18 d).

## Why this period
Replication, and native N2: the longest single closed-roster unit after 4c (18 days), used for the data-length curve. Layer role: replication + native N2.

## Prediction
*Written 2026-10-04 ~22:03 UTC, before running on this period (card predictions applied here; per-call talk spin unless stated).*
- P1: best of TAP / MS within 10% of exact ML on off-diagonal J and on σ_J (my credence 0.35); HH kill if none within 25%.
- P2: nMF ε_J > 0.10 (0.75).
- P3: MS ≤ TAP < nMF on ε_J (0.55); TAP may fail to converge in some rows.
- P5: real off-diagonal J near the circular-shift null (0.5): then the unit is uninformative for the coupling benchmark and the comparison is carried by the self-couplings (reported as such).
- P6 (1-min grid companion): activity spins nMF ε_J > 0.25 (0.6).
- N2: approximation bias flat in days while ML noise ν_J falls ~1/√days; ν_J below the best approximation's bias by 8 days (0.5).

## Result
*Run 2026-10-04 22:35–22:44 UTC (`analysis/run.py`); data `data/processed/H124-small-n-meanfield-benchmark/results/{percall,grid}.json`; figure `../../figures/benchmark.pdf`.* ε_J = off-diagonal relative error against exact ML on the same data, with day-bootstrap 95% intervals (200 replicates); "(k/4 rows)" = the method has a solution on only k rows (TAP: S/a₀ > 4/27); ✓ = off-diagonal J beyond the circular-shift null.

**Per-call talk clock (primary).**

| Unit | calls | max J_ii | ‖J_off‖ (shift-null q95) | ML noise ν_J | nMF | TAP | MS | nMF\|s | held-out LL gap nMF / nMF\|s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 28103 calls | 0.86 | 0.127 (0.181) | 0.90 | 0.25 [0.15, 0.38] | 0.02 [0.01, 0.08] (2/4 rows) | 0.82 [0.49, 31.11] | 0.49 [0.22, 0.85] | -0.0610 / -0.0004 |

**1-min parallel grid (companion; * = partial row cover).**

| Unit | 1-min talk: nMF / TAP / MS | 1-min activity: nMF / TAP / MS |
| --- | --- | --- |
| 8 | 0.06 / 0.04 / 0.04 | 0.50 / 0.80* / 1.17 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 (HH) TAP or MS within 10% (full cover) | 0/1 units | failed |
| HH kill: no method within 25% (full cover) | 0/1 units with none | not met |
| P2 nMF > 0.10 | 1/1 units | supported |
| P5 off-diagonal J near the null | 1/1 units inside the null | supported |

**Native N2 (data-length curve, 20 subsamples per length).** Medians: 2 d: nMF 0.30, MS 1.16, TAP 0.11 (half the rows), ML-vs-full 3.26 · 4 d: nMF 0.24, MS 1.07, TAP 0.09 (half the rows), ML-vs-full 1.81 · 8 d: nMF 0.23, MS 0.93, TAP 0.06 (half the rows), ML-vs-full 1.03 · 16 d: nMF 0.26, MS 0.83, TAP 0.02 (half the rows), ML-vs-full 0.32. The approximations' bias against same-data ML is flat in days (nMF 0.23–0.30, MS 0.83–1.16), while ML's distance to the full-data fit falls from 3.3 to 0.32. At 8 days ML noise (1.03) still exceeds nMF's bias (0.23); the crossover is near 16–18 days. **N2 verdict: mixed** (flat bias as predicted; crossover later than the predicted 8 days).


## Scorecard (period-specific axes)
C 1 (exact ML wins held-out log-likelihood; stratified nMF within 0.005 nats/call) · F 1 (S4 synthetic on this regime's schedules) · H 1 (R0 fails except at weak persistence; R2 holds for plain TAP/MS when J_ii > 0.6).

## Notes
