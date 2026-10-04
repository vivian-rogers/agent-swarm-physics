# H38 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode F · 13 agents (catalog) · 3 non-holdout days · 4.1 h/day (empirical median window).

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
| P1 JS share in [0.1, 0.4], above independence | 0.421 | independent 0.411; N1 surrogates 0.411 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 1.00 (strict rule 1.00) | surrogate 1.00 (q95 1.00) | ✗ |
| P2 largest cause pause | scheduled (1.00); edge 0.00, infra_error 0.00, pause 0.00, consolidation 0.00, unexplained 0.00 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P2 village-off minutes ≥ 80% scheduled | 1 gaps, 513 min, 1.00 scheduled | – | ✓ |
| P3 JS more likely after an infra burst | log OR -3.41 (247 burst min) | within-block shift: p(>) 0.786, p(<) 0.441 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.321, E 0.317, z 5.1 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.147 (z 2.4), f 0.54 | lull filter f 0.54 | ✓ |
| (Amendment 2) agent-state conditioning | scaffold E 0.070 (z 1.1), f 0.78; all incl. pauses f 1.02 | edge only f 0.62; + infra f 0.61 | ✓ |
| per-cause drop (f) | scheduled 0.45, edge 0.05, infra_error 0.00, pause -0.01, consolidation -0.01, unexplained 0.00 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.09 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.161 (z 3.2); stall 0.158; scaffold-masked 0.162 | N1 | descriptive |
| O5 λ₁/edge, unit 37 | raw 1.74, lull 0.47, stall 0.47, scaffold-masked 0.95 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G37/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share not above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 2.4, scaffold-masked z 1.1.
- **G:** 1 village-off gap(s), 1.00 of their minutes inside the operator's pause → resume interval.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: 2026-03-31 has a stray early-morning event, so its calendar window contains a 513-min operator-scheduled gap (H16's outage); 99.6% of those minutes are `scheduled`.
