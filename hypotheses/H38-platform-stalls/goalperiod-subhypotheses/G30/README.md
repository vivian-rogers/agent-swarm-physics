# H38 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-13)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; corrected tables, same rule)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C · 12 agents (catalog) · 5 non-holdout days · 4.0 h/day (empirical median window).

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
| P1 JS share in [0.05, 0.3], above independence | 0.110 | independent 0.108; N1 surrogates 0.108 | ✓ |
| P2 explained share ≥ 0.5 and above surrogate | 0.11 (strict rule 0.06) | surrogate 0.08 (q95 0.11) | ✗ |
| P2 largest cause edge or pause (wait) | unexplained (0.89); scheduled 0.03, edge 0.08, infra_error 0.00, pause 0.00, consolidation 0.00 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P3 JS more likely after an infra burst | log OR -0.23 (349 burst min) | within-block shift: p(>) 0.335, p(<) 0.770 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.103, E 0.107, z 2.4 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.080 (z 1.8), f 0.25 | lull filter f 0.21 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.074 (z 1.6), f 0.31; all incl. pauses f 0.32 | edge only f 0.43; + infra f 0.31 | ✗ |
| per-cause drop (f) | scheduled 0.29, edge -0.03, infra_error -0.00, pause -0.01, consolidation 0.00, unexplained -0.07 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.42 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.213 (z 4.4); stall 0.209; scaffold-masked 0.204 | N1 | descriptive |
| O5 λ₁/edge, unit 30 | raw 1.65, lull 1.16, stall 1.61, scaffold-masked 1.67 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G30/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share not above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 1.8, scaffold-masked z 1.6.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.110 (0.108) | 0.002 (0.000) |
| explained share (N1 surrogate) | 0.11 (0.08) | 1.00 (0.00) |
| largest cause of joint-silence minutes | unexplained | scheduled |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.103, 0.107 (2.4) | 0.177, 0.184 (4.0) |
| f_stall (pre-registered) · f_scaffold (headline) | 0.25 · 0.31 | 0.34 · 0.41 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.074 (1.6), 0.60 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.098 (2.1) |
| talk spin E raw (z) → trimmed E (z) | 0.213 (4.4) | 0.208 (5.2) → 0.190 (4.8) |
| per-period verdict (card rule) | mixed | mixed |

Data: `data/processed/H38-platform-stalls/r1b/G30/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
