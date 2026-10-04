# H38 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 7 agents (catalog) · 5 non-holdout days · 3.0 h/day (empirical median window).

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
| P1 JS share in [0.05, 0.3], above independence | 0.218 | independent 0.200; N1 surrogates 0.200 | ✓ |
| P2 explained share ≥ 0.5 and above surrogate | 0.38 (strict rule 0.16) | surrogate 0.42 (q95 0.45) | ✗ |
| P2 largest cause edge or pause (wait) | unexplained (0.62); scheduled 0.01, edge 0.35, infra_error 0.01, pause 0.02, consolidation 0.00 | – | ✗ |
| P2 infra_error < 10% | 0.01 | – | ✓ |
| P2 village-off minutes ≥ 80% scheduled | 1 gaps, 19 min, 0.01 scheduled | – | ✗ |
| P3 JS more likely after an infra burst | log OR -0.72 (189 burst min) | within-block shift: p(>) 0.884, p(<) 0.234 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.276, E 0.282, z 5.0 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.285 (z 5.0), f -0.01 | lull filter f 0.40 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.295 (z 5.4), f -0.05; all incl. pauses f -0.05 | edge only f 0.02; + infra f -0.05 | ✗ |
| per-cause drop (f) | scheduled -0.00, edge -0.01, infra_error -0.00, pause 0.00, consolidation 0.00, unexplained 0.39 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 2.47 | within 2× | ✗ |
| talk spin (secondary) | E raw 0.252 (z 5.2); stall 0.254; scaffold-masked 0.257 | N1 | descriptive |
| O5 λ₁/edge, unit 16 | raw 1.69, lull 0.73, stall 1.44, scaffold-masked 1.44 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G16/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share not above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 5.0, scaffold-masked z 5.4.
- **G:** 1 village-off gap(s), 0.01 of their minutes inside the operator's pause → resume interval.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
