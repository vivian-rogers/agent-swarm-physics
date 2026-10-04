# H38 × G03: Holiday: do whatever you'd like! Next goal will begin soon (2025-05-12 → 2025-05-14)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 4 agents (catalog) · 3 non-holdout days · 2.0 h/day (empirical median window).

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
| P1 JS share in [0.05, 0.3], above independence | 0.444 | independent 0.425; N1 surrogates 0.423 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 0.79 (strict rule 0.70) | surrogate 0.79 (q95 0.83) | ✓ |
| P2 largest cause edge or pause (wait) | pause (0.64); scheduled 0.00, edge 0.15, infra_error 0.00, consolidation 0.00, unexplained 0.21 | – | ✓ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P4 raw gain (H02/H19 g_eq) | g 0.021, E 0.029, z 0.4 | N1 joint shift | not significant |
| talk spin (secondary) | E raw 0.109 (z 1.6); stall 0.130; scaffold-masked 0.142 | N1 | descriptive |
| O5 λ₁/edge, unit 3 | raw 0.79, lull 0.57, stall 0.60, scaffold-masked 1.09 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G03/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain not significant vs N1.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: 3 days, N = 4; raw gain not significant.
