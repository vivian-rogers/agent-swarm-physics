# H124 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 15 active days. Units: 6a (2025-06-26→2025-07-02, 6 d), 6b (2025-07-03→2025-07-15, 9 d).

## Why this period
Primary (HH names #6, the merch competition). Fixed roster of four over 15 days, split at NE02 (screenshot redaction, a tiny dose) into 6a (6 d) and 6b (9 d). One side of native N1 (competition: each agent its own store). Layer role: primary + native N1.

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
| 6a | 6825 calls | 1.00 | 0.235 (0.262) | 0.86 | 0.20 [0.09, 0.30] | 0.06 [0.04, 0.30] (2/4 rows) | 1.20 [0.64, 21.60] | 0.86 [0.44, 1.04] | -0.0462 / -0.0044 |
| 6b | 9923 calls | 1.22 | 0.171 (0.270) | 0.93 | 0.30 [0.17, 0.45] | 0.10 [0.05, 0.26] (2/4 rows) | 3.83 [0.74, 21.44] | 1.72 [0.56, 1.96] | -0.0433 / -0.0022 |

**1-min parallel grid (companion; * = partial row cover).**

| Unit | 1-min talk: nMF / TAP / MS | 1-min activity: nMF / TAP / MS |
| --- | --- | --- |
| 6a | 0.22 / 0.41* / 0.54 | 0.57 / —* / 2.65 |
| 6b | 0.09 / 0.03* / 0.05 | 0.40 / 0.34* / 0.40 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 (HH) TAP or MS within 10% (full cover) | 0/2 units | failed |
| HH kill: no method within 25% (full cover) | 1/2 units with none | not met |
| P2 nMF > 0.10 | 2/2 units | supported |
| P5 off-diagonal J near the null | 2/2 units inside the null | supported |

**Native N1 (cooperation #4 vs competition #6).** Mean off-diagonal ML talk coupling J̄: 4a +0.049 [-0.000, +0.085], 4c +0.011 [-0.014, +0.036]; 6a +0.051 [+0.019, +0.068], 6b +0.004 [-0.042, +0.043]. No cooperation–competition difference (the intervals overlap; J̄ is at noise level in 3/4 units). The ranking differs between units of the same period (4c: MS < TAP < nMF; 4a, 6a, 6b: nMF best among full-cover methods), so it follows persistence, not the goal type. **N1 verdict: failed** (J̄ prediction not borne out; ranking not period-invariant).


## Scorecard (period-specific axes)
C 1 (exact ML wins held-out log-likelihood; stratified nMF within 0.005 nats/call) · F 1 (S4 synthetic on this regime's schedules) · H 1 (R0 fails except at weak persistence; R2 holds for plain TAP/MS when J_ii > 0.6).

## Notes
