# H38 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-09)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 10 agents (catalog) · 5 non-holdout days · 4.0 h/day (empirical median window).

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
| P1 JS share in [0.05, 0.3], above independence | 0.391 | independent 0.383; N1 surrogates 0.383 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 0.43 (strict rule 0.06) | surrogate 0.43 (q95 0.46) | ✗ |
| P2 largest cause edge or pause (wait) | unexplained (0.57); scheduled 0.01, edge 0.23, infra_error 0.04, pause 0.14, consolidation 0.00 | – | ✗ |
| P2 infra_error < 10% | 0.04 | – | ✓ |
| P2 village-off minutes ≥ 80% scheduled | 3 gaps, 52 min, 0.00 scheduled | – | ✗ |
| P3 JS more likely after an infra burst | log OR 0.29 (248 burst min) | within-block shift: p(>) 0.906, p(<) 0.156 | ✓ |
| P4 raw gain (H02/H19 g_eq) | g 0.209, E 0.211, z 3.8 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.233 (z 3.8), f -0.10 | lull filter f 0.95 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.243 (z 4.3), f -0.15; all incl. pauses f 0.01 | edge only f -0.08; + infra f -0.15 | ✗ |
| per-cause drop (f) | scheduled 0.02, edge -0.08, infra_error 0.00, pause -0.03, consolidation 0.00, unexplained 0.90 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 8.48 | within 2× | ✗ |
| talk spin (secondary) | E raw 0.239 (z 4.6); stall 0.251; scaffold-masked 0.242 | N1 | descriptive |
| O5 λ₁/edge, unit 26 | raw 1.41, lull 0.71, stall 1.25, scaffold-masked 1.39 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G26/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share not above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 3.8, scaffold-masked z 4.3.
- **G:** 3 village-off gap(s), 0.00 of their minutes inside the operator's pause → resume interval.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
