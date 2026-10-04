# H38 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; corrected tables, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C · 12 agents (catalog) · 3 non-holdout days · 4.0 h/day (empirical median window).

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
| P1 JS share in [0.05, 0.3], above independence | 0.003 | independent 0.001; N1 surrogates 0.001 | ✗ |
| P2 explained share ≥ 0.5 and above surrogate | 1.00 (strict rule 1.00) | surrogate 0.07 (q95 0.52) | ✓ |
| P2 largest cause edge or pause (wait) | scheduled (0.50); edge 0.50, infra_error 0.00, pause 0.00, consolidation 0.00, unexplained 0.00 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P3 JS more likely after an infra burst | log OR -1.11 (271 burst min) | within-block shift: p(>) 1.000, p(<) 0.677 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.113, E 0.116, z 2.2 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.095 (z 1.8), f 0.18 | lull filter f 0.11 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.102 (z 2.0), f 0.12; all incl. pauses f 0.58 | edge only f 0.30; + infra f 0.12 | ✗ |
| per-cause drop (f) | scheduled 0.11, edge 0.08, infra_error -0.01, pause -0.00, consolidation 0.00, unexplained -0.07 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.45 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.068 (z 1.3); stall 0.065; scaffold-masked 0.079 | N1 | descriptive |
| O5 λ₁/edge, unit 33 | raw 1.06, lull 1.04, stall 1.04, scaffold-masked 1.10 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G33/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 1.8, scaffold-masked z 2.0.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.003 (0.001) | 0.000 (0.000) |
| explained share (N1 surrogate) | 1.00 (0.07) | 0.00 (0.00) |
| largest cause of joint-silence minutes | scheduled | – |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.113, 0.116 (2.2) | 0.133, 0.137 (2.5) |
| f_stall (pre-registered) · f_scaffold (headline) | 0.18 · 0.12 | -0.00 · 0.07 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.099 (1.7), 0.28 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.126 (2.1) |
| talk spin E raw (z) → trimmed E (z) | 0.068 (1.3) | 0.103 (2.0) → 0.087 (1.4) |
| per-period verdict (card rule) | failed | failed |

Data: `data/processed/H38-platform-stalls/r1b/G33/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: 3 days; a single joint-silence minute, so P2 is not informative.
