# H38 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C · 13 agents (catalog) · 5 non-holdout days · 4.0 h/day (empirical median window).

## Why this period
One point in H38's period-by-period decomposition of joint silences and of the equal-time gain. Regime II: discrete sessions; WAIT is logged at the end of the gap it closes and is message-triggered (H09), so synchronized waiting is the coupled-lull rival here.

## Prediction
*Written 2026-10-04 01:27 UTC, before running H38 on this period.*
- **P1.** JS share in 0.05–0.30 (regime II), above the per-block independent expectation.
- **P2.** Explained share of JS minutes ≥ 0.5 and above its N1-surrogate level; largest primary cause `edge` or `wait`; `infra_error` < 10% of JS minutes; village-off minutes, if any, ≥ 80% `scheduled`.
- **P3.** If there are ≥ 20 infra-burst minutes: odds ratio of JS given a burst > 1.
- **P4.** If raw g_eq active is significant (z > 2 vs N1): f_infra ≥ 0.5 (dropping explained JS minutes removes at least half of the excess) and f_lull ≥ f_infra.
- **P7.** If the raw excess is ≥ 0.05: the O6 two-state formula predicts g_raw − g_stall within a factor of 2.
- **Per-period verdict rule** (fixed now): **supported** if (i) explained share ≥ 0.5 and above its surrogate level and (ii) f_infra ≥ 0.5 where raw g is significant; **failed** if the explained share is at or below its surrogate level, or raw g is significant with f_infra < 0.25; **mixed** otherwise. If raw g is not significant, (ii) is not scored and the verdict rests on (i).
- Against it: joint silences no more scaffold-marked than chance, or a significant raw gain that survives stall removal nearly intact.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 JS share in [0.05, 0.3], above independence | 0.037 | independent 0.040; N1 surrogates 0.040 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 0.07 (strict rule 0.02) | surrogate 0.04 (q95 0.09) | ✗ |
| P2 largest cause edge or pause (wait) | unexplained (0.93); scheduled 0.02, edge 0.05, infra_error 0.00, pause 0.00, consolidation 0.00 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P3 JS more likely after an infra burst | log OR 0.48 (567 burst min) | within-block shift: p(>) 0.864, p(<) 0.317 | ✓ |
| P4 raw gain (H02/H19 g_eq) | g 0.098, E 0.103, z 2.2 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.104 (z 2.3), f -0.01 | lull filter f -0.13 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.056 (z 1.3), f 0.45; all incl. pauses f 0.73 | edge only f 0.06; + infra f 0.45 | ✗ |
| per-cause drop (f) | scheduled 0.00, edge -0.01, infra_error -0.00, pause -0.00, consolidation 0.00, unexplained -0.11 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 4.65 | within 2× | ✗ |
| talk spin (secondary) | E raw 0.183 (z 3.8); stall 0.183; scaffold-masked 0.184 | N1 | descriptive |
| O5 λ₁/edge, unit 35 | raw 1.88, lull 1.61, stall 1.86, scaffold-masked 1.87 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G35/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share not above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 2.3, scaffold-masked z 1.3.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
