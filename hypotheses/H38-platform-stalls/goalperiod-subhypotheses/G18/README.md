# H38 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 7 agents (catalog) · 10 non-holdout days · 4.0 h/day (empirical median window).

## Why this period
One point in H38's period-by-period decomposition of joint silences and of the equal-time gain. Regime I: discrete sessions; WAIT is logged at the end of the gap it closes and is message-triggered (H09), so synchronized waiting is the coupled-lull rival here.

## Prediction
*Written 2026-10-04 01:27 UTC, before running H38 on this period.*
- **P1.** JS share in 0.05–0.30 (regime I), above the per-block independent expectation.
- **P2.** Explained share of JS minutes ≥ 0.5 and above its N1-surrogate level; largest primary cause `edge` or `wait`; `infra_error` < 10% of JS minutes; village-off minutes, if any, ≥ 80% `scheduled`.
- **P3.** If there are ≥ 20 infra-burst minutes: odds ratio of JS given a burst > 1.
- **P4.** If raw g_eq active is significant (z > 2 vs N1): f_infra ≥ 0.5 (dropping explained JS minutes removes at least half of the excess) and f_lull ≥ f_infra.
- **P7.** If the raw excess is ≥ 0.05: the O6 two-state formula predicts g_raw − g_stall within a factor of 2.
- **Per-period verdict rule** (fixed now): **supported** if (i) explained share ≥ 0.5 and above its surrogate level and (ii) f_infra ≥ 0.5 where raw g is significant; **failed** if the explained share is at or below its surrogate level, or raw g is significant with f_infra < 0.25; **mixed** otherwise. If raw g is not significant, (ii) is not scored and the verdict rests on (i).
- Against it: joint silences no more scaffold-marked than chance, or a significant raw gain that survives stall removal nearly intact.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 JS share in [0.05, 0.3], above independence | 0.165 | independent 0.156; N1 surrogates 0.156 | ✓ |
| P2 explained share ≥ 0.5 and above surrogate | 0.52 (strict rule 0.11) | surrogate 0.49 (q95 0.52) | ✓ |
| P2 largest cause edge or pause (wait) | unexplained (0.48); scheduled 0.00, edge 0.18, infra_error 0.00, pause 0.34, consolidation 0.00 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P2 village-off minutes ≥ 80% scheduled | 4 gaps, 47 min, 0.00 scheduled | – | ✗ |
| P3 JS more likely after an infra burst | log OR 0.49 (179 burst min) | within-block shift: p(>) 0.711, p(<) 0.415 | ✓ |
| P4 raw gain (H02/H19 g_eq) | g 0.117, E 0.120, z 3.6 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.082 (z 2.3), f 0.31 | lull filter f 0.06 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.131 (z 4.1), f -0.09; all incl. pauses f 0.87 | edge only f -0.09; + infra f -0.09 | ✗ |
| per-cause drop (f) | scheduled 0.03, edge -0.03, infra_error -0.00, pause 0.32, consolidation 0.00, unexplained -0.24 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.80 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.244 (z 7.7); stall 0.240; scaffold-masked 0.246 | N1 | descriptive |
| O5 λ₁/edge, unit 18 | raw 1.50, lull 0.85, stall 1.19, scaffold-masked 1.48 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G18/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 2.3, scaffold-masked z 4.1.
- **G:** 4 village-off gap(s), 0.00 of their minutes inside the operator's pause → resume interval.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
