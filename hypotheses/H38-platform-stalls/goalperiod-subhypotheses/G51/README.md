# H38 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; corrected tables, same rule)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode I/K · 21 agents (catalog) · 45 non-holdout days · 8.1 h/day (empirical median window).

## Why this period
One point in H38's period-by-period decomposition of joint silences and of the equal-time gain. Regime III: always-on computer use, self-scheduled PAUSE timers and CONSOLIDATE every ~40 actions, so scaffold states can synchronize (common starts, common timers).

## Prediction
*Written 2026-10-04 01:27 UTC, before running H38 on this period.*
- 8-hour days and the largest roster (private roles): more agents make K ≤ 1 rarer, so JS share near the bottom of the range; H16 saw village-off gaps on 6 days here, predicted `scheduled`.
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
| P1 JS share in [0.1, 0.4], above independence | 0.136 | independent 0.125; N1 surrogates 0.125 | ✓ |
| P2 explained share ≥ 0.5 and above surrogate | 0.95 (strict rule 0.38) | surrogate 0.97 (q95 0.97) | ✗ |
| P2 largest cause pause | scheduled (0.33); edge 0.25, infra_error 0.00, pause 0.22, consolidation 0.15, unexplained 0.05 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P2 village-off minutes ≥ 80% scheduled | 8 gaps, 927 min, 0.91 scheduled | – | ✓ |
| P3 JS more likely after an infra burst | log OR -1.15 (16669 burst min) | within-block shift: p(>) 1.000, p(<) 0.002 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.279, E 0.279, z 25.1 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.180 (z 15.3), f 0.36 | lull filter f 0.50 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.240 (z 23.0), f 0.14; all incl. pauses f 0.12 | edge only f 0.36; + infra f 0.34 | ✗ |
| per-cause drop (f) | scheduled 0.19, edge 0.13, infra_error -0.00, pause 0.00, consolidation -0.01, unexplained 0.10 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.17 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.129 (z 12.2); stall 0.121; scaffold-masked 0.108 | N1 | descriptive |
| O5 λ₁/edge, unit 51a | raw 1.64, lull 0.37, stall 0.37, scaffold-masked 0.72 | cross-day surrogate edge (95%) | descriptive |
| O5 λ₁/edge, unit 51b | raw 2.56, lull 1.66, stall 1.78, scaffold-masked 2.11 | cross-day surrogate edge (95%) | descriptive |
| O5 λ₁/edge, unit 51c | raw 2.41, lull 1.60, stall 1.61, scaffold-masked 2.13 | cross-day surrogate edge (95%) | descriptive |
| O5 λ₁/edge, unit 51d | raw 2.13, lull 1.10, stall 1.27, scaffold-masked 1.87 | cross-day surrogate edge (95%) | descriptive |
| O5 λ₁/edge, unit 51e | raw 0.93, lull 0.89, stall 0.89, scaffold-masked 0.98 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G51/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share not above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 15.3, scaffold-masked z 23.0.
- **G:** 8 village-off gap(s), 0.91 of their minutes inside the operator's pause → resume interval.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.136 (0.125) | 0.052 (0.040) |
| explained share (N1 surrogate) | 0.95 (0.97) | 0.93 (1.00) |
| largest cause of joint-silence minutes | scheduled | scheduled |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.279, 0.279 (25.1) | 0.327, 0.326 (28.9) |
| f_stall (pre-registered) · f_scaffold (headline) | 0.36 · 0.14 | 0.38 · 0.27 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.102 (8.5), 0.69 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.154 (12.2) |
| talk spin E raw (z) → trimmed E (z) | 0.129 (12.2) | 0.167 (17.2) → 0.143 (12.8) |
| per-period verdict (card rule) | failed | failed |

Data: `data/processed/H38-platform-stalls/r1b/G51/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: 45 non-holdout days (the #51 tail is held out). Village-off gaps on 07-07, 07-10, 07-28 are operator-scheduled; three short K = 0 runs (07-09, 07-17, 07-24; 10–15 min) are unexplained. The residual gain survives every adjustment (z ≈ 23).
