# H38 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** supported
**Verdict (1b):** supported (round 1: supported; corrected tables, same rule)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode K · 4 agents (catalog) · 15 non-holdout days · 2.0 h/day (empirical median window).

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
| P1 JS share in [0.05, 0.3], above independence | 0.498 | independent 0.496; N1 surrogates 0.495 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 0.74 (strict rule 0.67) | surrogate 0.73 (q95 0.74) | ✓ |
| P2 largest cause edge or pause (wait) | scheduled (0.59); edge 0.11, infra_error 0.01, pause 0.04, consolidation 0.00, unexplained 0.26 | – | ✗ |
| P2 infra_error < 10% | 0.01 | – | ✓ |
| P2 village-off minutes ≥ 80% scheduled | 6 gaps, 839 min, 0.77 scheduled | – | ✗ |
| P3 JS more likely after an infra burst | log OR -0.41 (48 burst min) | within-block shift: p(>) 0.453, p(<) 0.713 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.070, E 0.069, z 2.1 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E -0.014 (z -0.4), f 1.21 | lull filter f 1.24 | ✓ |
| (Amendment 2) agent-state conditioning | scaffold E 0.018 (z 0.5), f 0.74; all incl. pauses f 1.21 | edge only f 0.72; + infra f 0.74 | ✓ |
| per-cause drop (f) | scheduled 0.75, edge -0.07, infra_error -0.05, pause 0.33, consolidation 0.00, unexplained -0.71 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.77 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.093 (z 2.9); stall 0.086; scaffold-masked 0.089 | N1 | descriptive |
| O5 λ₁/edge, unit 6 | raw 1.50, lull 0.54, stall 1.04, scaffold-masked 1.46 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G06/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z -0.4, scaffold-masked z 0.5.
- **G:** 6 village-off gap(s), 0.77 of their minutes inside the operator's pause → resume interval.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.498 (0.496) | 0.308 (0.303) |
| explained share (N1 surrogate) | 0.74 (0.73) | 1.00 (0.98) |
| largest cause of joint-silence minutes | scheduled | scheduled |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.070, 0.069 (2.1) | 0.217, 0.216 (6.0) |
| f_stall (pre-registered) · f_scaffold (headline) | 1.21 · 0.74 | 0.68 · 0.23 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.212 (5.7), 0.02 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.161 (4.4) |
| talk spin E raw (z) → trimmed E (z) | 0.093 (2.9) | 0.172 (6.3) → 0.174 (5.8) |
| per-period verdict (card rule) | supported | supported |

Data: `data/processed/H38-platform-stalls/r1b/G06/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: 2025-06-29 (a Sunday) has a stray early event, so its window spans a 774-min operator-scheduled gap.
