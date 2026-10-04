# H38 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C · 12 agents (catalog) · 17 non-holdout days · 4.0 h/day (empirical median window).

## Why this period
One point in H38's period-by-period decomposition of joint silences and of the equal-time gain. Regime III: always-on computer use, self-scheduled PAUSE timers and CONSOLIDATE every ~40 actions, so scaffold states can synchronize (common starts, common timers).

## Prediction
*Written 2026-10-04 01:27 UTC, before running H38 on this period.*
- **P1.** JS share in 0.10–0.40 (regime III), above the per-block independent expectation.
- **P2.** Explained share of JS minutes ≥ 0.5 and above its N1-surrogate level; largest primary cause `timer_pause`; `infra_error` < 10% of JS minutes; village-off minutes, if any, ≥ 80% `scheduled`.
- **P3.** If there are ≥ 20 infra-burst minutes: odds ratio of JS given a burst > 1.
- **P4.** If raw g_eq active is significant (z > 2 vs N1): f_infra ≥ 0.5 (dropping explained JS minutes removes at least half of the excess) and f_lull ≥ f_infra.
- **P7.** If the raw excess is ≥ 0.05: the O6 two-state formula predicts g_raw − g_stall within a factor of 2.
- **Per-period verdict rule** (fixed now): **supported** if (i) explained share ≥ 0.5 and above its surrogate level and (ii) f_infra ≥ 0.5 where raw g is significant; **failed** if the explained share is at or below its surrogate level, or raw g is significant with f_infra < 0.25; **mixed** otherwise. If raw g is not significant, (ii) is not scored and the verdict rests on (i).
- Against it: joint silences no more scaffold-marked than chance, or a significant raw gain that survives stall removal nearly intact.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 JS share in [0.1, 0.4], above independence | 0.091 | independent 0.081; N1 surrogates 0.081 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 0.88 (strict rule 0.67) | surrogate 0.88 (q95 0.90) | ✗ |
| P2 largest cause pause | scheduled (0.66); edge 0.05, infra_error 0.02, pause 0.01, consolidation 0.14, unexplained 0.12 | – | ✗ |
| P2 infra_error < 10% | 0.02 | – | ✓ |
| P2 village-off minutes ≥ 80% scheduled | 1 gaps, 213 min, 0.99 scheduled | – | ✓ |
| P3 JS more likely after an infra burst | log OR -1.42 (2778 burst min) | within-block shift: p(>) 0.603, p(<) 0.451 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.147, E 0.149, z 6.1 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.035 (z 1.4), f 0.76 | lull filter f 0.75 | ✓ |
| (Amendment 2) agent-state conditioning | scaffold E 0.017 (z 0.7), f 0.89; all incl. pauses f 1.03 | edge only f 0.83; + infra f 0.78 | ✓ |
| per-cause drop (f) | scheduled 0.73, edge -0.02, infra_error 0.01, pause 0.01, consolidation -0.02, unexplained -0.02 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.28 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.056 (z 2.3); stall 0.050; scaffold-masked 0.051 | N1 | descriptive |
| O5 λ₁/edge, unit 38a | raw 1.41, lull 1.26, stall 1.26, scaffold-masked 1.29 | cross-day surrogate edge (95%) | descriptive |
| O5 λ₁/edge, unit 38b | raw 1.59, lull 0.72, stall 0.72, scaffold-masked 0.85 | cross-day surrogate edge (95%) | descriptive |
| O5 λ₁/edge, unit 38c | raw 1.63, lull 0.96, stall 1.21, scaffold-masked 1.41 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G38/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share not above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 1.4, scaffold-masked z 0.7.
- **G:** 1 village-off gap(s), 0.99 of their minutes inside the operator's pause → resume interval.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: 2026-04-16 has a 213-min operator-scheduled gap; λ₁ unit 38b loses its market mode under the stall filter.
