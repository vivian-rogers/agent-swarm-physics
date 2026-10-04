# H38 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** supported
**Verdict (1b):** supported (round 1: supported; corrected tables, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C · 15 agents (catalog) · 5 non-holdout days · 4.1 h/day (empirical median window).

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
| P1 JS share in [0.1, 0.4], above independence | 0.045 | independent 0.026; N1 surrogates 0.026 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 0.67 (strict rule 0.44) | surrogate 0.52 (q95 0.64) | ✓ |
| P2 largest cause pause | scheduled (0.44); edge 0.02, infra_error 0.00, pause 0.00, consolidation 0.22, unexplained 0.33 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P3 JS more likely after an infra burst | log OR -0.45 (770 burst min) | within-block shift: p(>) 0.860, p(<) 0.196 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.350, E 0.346, z 7.5 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.144 (z 3.1), f 0.58 | lull filter f 0.58 | ✓ |
| (Amendment 2) agent-state conditioning | scaffold E 0.106 (z 2.4), f 0.69; all incl. pauses f 0.68 | edge only f 0.61; + infra f 0.55 | ✓ |
| per-cause drop (f) | scheduled 0.61, edge -0.01, infra_error -0.00, pause -0.00, consolidation -0.03, unexplained -0.03 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.12 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.024 (z 0.6); stall 0.014; scaffold-masked 0.016 | N1 | descriptive |
| O5 λ₁/edge, unit 40 | raw 1.64, lull 1.32, stall 1.42, scaffold-masked 1.65 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G40/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 3.1, scaffold-masked z 2.4.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.045 (0.026) | 0.016 (0.000) |
| explained share (N1 surrogate) | 0.67 (0.52) | 1.00 (0.00) |
| largest cause of joint-silence minutes | scheduled | scheduled |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.350, 0.346 (7.5) | 0.429, 0.426 (8.8) |
| f_stall (pre-registered) · f_scaffold (headline) | 0.58 · 0.69 | 0.63 · 0.95 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.073 (1.4), 0.83 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.018 (0.4) |
| talk spin E raw (z) → trimmed E (z) | 0.024 (0.6) | 0.024 (0.6) → -0.055 (-1.2) |
| per-period verdict (card rule) | supported | supported |

Data: `data/processed/H38-platform-stalls/r1b/G40/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
