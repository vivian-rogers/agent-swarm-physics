# H38 × G02: Unsupervised agents look back on their previous goal and forward to their next (2025-05-10 → 2025-05-11)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; corrected tables, same rule)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode F · 4 agents (catalog) · 2 non-holdout days · 1.9 h/day (empirical median window).

## Why this period
One point in H38's period-by-period decomposition of joint silences and of the equal-time gain. Regime I: discrete sessions; WAIT is logged at the end of the gap it closes and is message-triggered (H09), so synchronized waiting is the coupled-lull rival here.

## Prediction
*Written 2026-10-04 01:27 UTC, before running H38 on this period.*
- Only 2 non-holdout day(s): N1 surrogates and z are weak; read as descriptive.
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
| P1 JS share in [0.05, 0.3], above independence | 0.474 | independent 0.390; N1 surrogates 0.394 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 0.97 (strict rule 0.96) | surrogate 0.96 (q95 0.99) | ✓ |
| P2 largest cause edge or pause (wait) | pause (0.81); scheduled 0.00, edge 0.17, infra_error 0.00, consolidation 0.00, unexplained 0.03 | – | ✓ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P4 raw gain (H02/H19 g_eq) | g 0.225, E 0.233, z 2.3 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.489 (z 2.9), f -1.10 | lull filter f -2.54 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.231 (z 2.3), f 0.01; all incl. pauses f 0.74 | edge only f 0.01; + infra f 0.01 | ✗ |
| per-cause drop (f) | scheduled 0.00, edge -0.03, infra_error 0.00, pause -0.68, consolidation 0.00, unexplained -0.17 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 3.00 | within 2× | ✗ |
| talk spin (secondary) | E raw 0.286 (z 3.5); stall 0.249; scaffold-masked 0.289 | N1 | descriptive |
| O5 λ₁/edge, unit 2 | raw 1.01, lull 0.86, stall 0.84, scaffold-masked 0.99 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G02/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 2.9, scaffold-masked z 2.3.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.474 (0.390) | 0.313 (0.209) |
| explained share (N1 surrogate) | 0.97 (0.96) | 0.99 (0.98) |
| largest cause of joint-silence minutes | pause | pause |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.225, 0.233 (2.3) | 0.294, 0.303 (3.0) |
| f_stall (pre-registered) · f_scaffold (headline) | -1.10 · 0.01 | -0.52 · 0.02 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.341 (3.1), -0.13 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.331 (3.0) |
| talk spin E raw (z) → trimmed E (z) | 0.286 (3.5) | 0.390 (4.2) → 0.386 (3.9) |
| per-period verdict (card rule) | failed | failed |

Data: `data/processed/H38-platform-stalls/r1b/G02/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: only 2 non-holdout days with N = 3–4 present agents; z and f are noisy (read as descriptive).
