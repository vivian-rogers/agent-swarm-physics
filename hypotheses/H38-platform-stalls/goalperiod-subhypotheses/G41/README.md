# H38 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** supported
**Verdict (1b):** supported (round 1: supported; corrected tables, same rule)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode I · 15 agents (catalog) · 5 non-holdout days · 4.0 h/day (empirical median window).

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
| P1 JS share in [0.1, 0.4], above independence | 0.079 | independent 0.081; N1 surrogates 0.081 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 0.66 (strict rule 0.22) | surrogate 0.62 (q95 0.68) | ✓ |
| P2 largest cause pause | unexplained (0.34); scheduled 0.17, edge 0.12, infra_error 0.04, pause 0.05, consolidation 0.27 | – | ✗ |
| P2 infra_error < 10% | 0.04 | – | ✓ |
| P3 JS more likely after an infra burst | log OR 0.15 (742 burst min) | within-block shift: p(>) 0.629, p(<) 0.483 | ✓ |
| P4 raw gain (H02/H19 g_eq) | g 0.133, E 0.135, z 2.9 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.031 (z 0.6), f 0.77 | lull filter f 0.62 | ✓ |
| (Amendment 2) agent-state conditioning | scaffold E 0.046 (z 1.0), f 0.66; all incl. pauses f 1.03 | edge only f 1.05; + infra f 1.25 | ✓ |
| per-cause drop (f) | scheduled 0.87, edge -0.08, infra_error 0.00, pause -0.00, consolidation -0.06, unexplained -0.13 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.24 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.080 (z 1.7); stall 0.077; scaffold-masked 0.039 | N1 | descriptive |
| O5 λ₁/edge, unit 41 | raw 1.42, lull 1.12, stall 1.23, scaffold-masked 1.22 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G41/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 0.6, scaffold-masked z 1.0.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.079 (0.081) | 0.010 (0.000) |
| explained share (N1 surrogate) | 0.66 (0.62) | 1.00 (0.02) |
| largest cause of joint-silence minutes | unexplained | scheduled |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.133, 0.135 (2.9) | 0.299, 0.300 (6.0) |
| f_stall (pre-registered) · f_scaffold (headline) | 0.77 · 0.66 | 0.59 · 0.51 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | -0.010 (-0.2), 1.03 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.114 (2.0) |
| talk spin E raw (z) → trimmed E (z) | 0.080 (1.7) | 0.200 (4.8) → 0.195 (4.5) |
| per-period verdict (card rule) | supported | supported |

Data: `data/processed/H38-platform-stalls/r1b/G41/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
