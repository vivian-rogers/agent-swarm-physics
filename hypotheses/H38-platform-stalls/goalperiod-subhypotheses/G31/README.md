# H38 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; corrected tables, same rule)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode F · 12 agents (catalog) · 5 non-holdout days · 4.0 h/day (empirical median window).

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
| P1 JS share in [0.05, 0.3], above independence | 0.147 | independent 0.145; N1 surrogates 0.145 | ✓ |
| P2 explained share ≥ 0.5 and above surrogate | 0.09 (strict rule 0.02) | surrogate 0.11 (q95 0.13) | ✗ |
| P2 largest cause edge or pause (wait) | unexplained (0.91); scheduled 0.01, edge 0.09, infra_error 0.00, pause 0.00, consolidation 0.00 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P3 JS more likely after an infra burst | log OR 0.11 (544 burst min) | within-block shift: p(>) 0.952, p(<) 0.098 | ✓ |
| P4 raw gain (H02/H19 g_eq) | g 0.072, E 0.069, z 1.6 | N1 joint shift | not significant |
| P7 (consistency) O6 formula / observed Δg | -1.73 | within 2× | ✗ |
| talk spin (secondary) | E raw 0.126 (z 2.9); stall 0.127; scaffold-masked 0.133 | N1 | descriptive |
| O5 λ₁/edge, unit 31 | raw 1.60, lull 0.87, stall 1.56, scaffold-masked 1.51 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G31/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share not above its N1 surrogate level; raw gain not significant vs N1.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.147 (0.145) | 0.002 (0.000) |
| explained share (N1 surrogate) | 0.09 (0.11) | 0.33 (0.00) |
| largest cause of joint-silence minutes | unexplained | unexplained |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.072, 0.069 (1.6) | 0.144, 0.142 (3.5) |
| f_stall (pre-registered) · f_scaffold (headline) | – · – | 0.12 · 0.14 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.108 (2.6), 0.24 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.123 (3.0) |
| talk spin E raw (z) → trimmed E (z) | 0.126 (2.9) | 0.107 (2.9) → 0.092 (2.3) |
| per-period verdict (card rule) | failed | failed |

Data: `data/processed/H38-platform-stalls/r1b/G31/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
