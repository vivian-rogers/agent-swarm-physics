# H38 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** supported
**Verdict (1b):** mixed (round 1: supported; corrected tables, same rule)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime II · mode C · 13 agents (catalog) · 5 non-holdout days · 4.0 h/day (empirical median window). Splits inside the period: 2026-03-24 (regime II → III).

## Why this period
One point in H38's period-by-period decomposition of joint silences and of the equal-time gain. Split at the 2026-03-24 regime boundary (36a regime II, 36b regime III); predictions apply to each side with its regime, and the pair also enters the NE14 boundary test.

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
| P1 JS share in [0.05, 0.3], above independence | 0.076 | independent 0.062; N1 surrogates 0.062 | ✓ |
| P2 explained share ≥ 0.5 and above surrogate | 0.63 (strict rule 0.16) | surrogate 0.59 (q95 0.69) | ✓ |
| P2 largest cause edge or pause (wait) | consolidation (0.43); scheduled 0.16, edge 0.01, infra_error 0.02, pause 0.00, unexplained 0.37 | – | ✗ |
| P2 infra_error < 10% | 0.02 | – | ✓ |
| P3 JS more likely after an infra burst | log OR -0.71 (966 burst min) | within-block shift: p(>) 0.944, p(<) 0.094 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.171, E 0.173, z 4.0 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.068 (z 1.5), f 0.61 | lull filter f 0.59 | ✓ |
| (Amendment 2) agent-state conditioning | scaffold E -0.010 (z -0.2), f 1.06; all incl. pauses f 1.06 | edge only f 0.67; + infra f 0.75 | ✓ |
| per-cause drop (f) | scheduled 0.68, edge -0.02, infra_error -0.01, pause 0.00, consolidation -0.08, unexplained -0.05 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.25 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.082 (z 1.9); stall 0.077; scaffold-masked 0.077 | N1 | descriptive |
| O5 λ₁/edge, unit 36b | raw 1.57, lull 1.12, stall 1.29, scaffold-masked 1.53 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G36/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 1.5, scaffold-masked z -0.2.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.076 (0.062) | 0.009 (0.000) |
| explained share (N1 surrogate) | 0.63 (0.59) | 1.00 (0.01) |
| largest cause of joint-silence minutes | consolidation | scheduled |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.171, 0.173 (4.0) | 0.250, 0.257 (5.6) |
| f_stall (pre-registered) · f_scaffold (headline) | 0.61 · 1.06 | 0.49 · 0.74 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.058 (1.1), 0.78 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.075 (1.5) |
| talk spin E raw (z) → trimmed E (z) | 0.082 (1.9) | 0.195 (5.2) → 0.148 (3.4) |
| per-period verdict (card rule) | supported | mixed |

Data: `data/processed/H38-platform-stalls/r1b/G36/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: computed as one H19 chunk across the 2026-03-24 regime boundary; the boundary itself is tested in `NE14/`.
