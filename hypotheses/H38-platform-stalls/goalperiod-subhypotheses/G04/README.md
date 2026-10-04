# H38 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** mixed
**Verdict (1b):** failed (replication, round 1: mixed; corrected tables, same rule) · native #4d restart: failed
**Role:** native (round 1b: the 06-18 restart; round-1 role: exploratory replication)
**Period:** regime I · mode C · 4 agents (catalog) · 25 non-holdout days · 2.0 h/day (empirical median window).

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

## Round 1b native test: the 2025-06-18 restart (#4d)
*Prediction written 2026-10-04 06:32 UTC, before computing any statistic for 2025-06-18 on the corrected tables. Seen before: the round-1 note that 06-18 has a mid-day operator pause → resume pair (a 300-min village-off gap inside the calendar window) and DQ9's description of 4d as the restart after a 300-min stall; no per-day gain for this day.*

**Why:** the only non-holdout day with a long, dated, operator-acknowledged stop and restart *inside* one calendar window (DQ9: "a platform stall with a known cause"). H38's two-state field formula says a stall that switches every agent off inflates the within-block variance ratio only in the blocks it partly covers, and that the scaffold-aware estimators remove that inflation.

**Design (per day, G04 non-holdout days, day-present population with ≥ 30 active minutes):** E_raw(d) (N1 block-shift null, whole window), E_stall(d) (explained joint-silence minutes dropped, filter recomputed on surrogates), E_trim(d) (DQ8 design: rows outside the all-present window and explained joint-silence minutes removed before the block-shift surrogates); restart spread = SD across agents of the first active minute after the 06-18 gap.

**Predictions:**
- **N2a (detection).** `outages_fixed` has one village-off run on 06-18 of ≥ 240 min, with ≥ 80% of its minutes `scheduled` (inside the operator's pause → resume pair).
- **N2b (inflation).** E_raw(06-18) is above the median of the other G04 days' E_raw.
- **N2c (removal).** Both scaffold-aware values sit closer to the other days' median than E_raw does: |E_stall(06-18) − m_stall| < |E_raw(06-18) − m_raw| and |E_trim(06-18) − m_trim| < |E_raw(06-18) − m_raw|.
- **N2d (synchronized restart).** All present agents act again within 10 min of the first post-gap action (restart spread ≤ 5 min).
- Verdict rule: supported if N2a–N2c hold; failed if N2b fails (the stall leaves no trace in the raw gain) or N2c fails for both estimators; mixed otherwise. N2d is descriptive. Caveat stated in advance: N = 4 agents and ~2 h days make one day's gain noisy.

**Round 1b native result (run 2026-10-04 06:40 UTC, `analysis/r1b_native.py`; `data/processed/H38-platform-stalls/r1b/native/g04_days.parquet`).**

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N2a one village-off run ≥ 240 min on 06-18, ≥ 80% scheduled | 299 min, 99% scheduled (operator pause → resume pair) | ✓ |
| N2b E_raw(06-18) above the other days' median | 0.022 vs median 0.191 (rank 5 of 25) | ✗ |
| N2c scaffold-aware values closer to the other days' median | E_stall 0.048 (median 0.132), E_trim 0.081 (median 0.084) | ✓ (moot: no inflation to remove) |
| N2d synchronized restart (descriptive) | all 4 agents act within 1 min of the first post-gap action (offsets 0, 0, 0, 1 min) | ✓ |

**Native verdict: failed** (N2b): the 300-min stop leaves no trace in the day's equal-time gain. Reason, consistent with the two-state formula: an all-silent stretch that covers whole 30-min blocks contributes zero within-block variance, so only the two boundary blocks can inflate VR, and here they do not. A long, block-aligned stall is harmless to the block-detrended gain; short or partial stalls are the dangerous ones (synthetic F). The restart itself is perfectly synchronized, a clean example of a common field.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 JS share in [0.05, 0.3], above independence | 0.230 | independent 0.219; N1 surrogates 0.220 | ✓ |
| P2 explained share ≥ 0.5 and above surrogate | 0.76 (strict rule 0.72) | surrogate 0.74 (q95 0.76) | ✓ |
| P2 largest cause edge or pause (wait) | scheduled (0.38); edge 0.16, infra_error 0.00, pause 0.22, consolidation 0.00, unexplained 0.24 | – | ✗ |
| P2 infra_error < 10% | 0.00 | – | ✓ |
| P2 village-off minutes ≥ 80% scheduled | 3 gaps, 356 min, 0.81 scheduled | – | ✓ |
| P3 JS more likely after an infra burst | log OR -1.36 (88 burst min) | within-block shift: p(>) 0.180, p(<) 0.888 | ✗ |
| P4 raw gain (H02/H19 g_eq) | g 0.125, E 0.126, z 4.5 | N1 joint shift | significant |
| P4 f_infra (stall filter) ≥ 0.5 | E 0.069 (z 2.2), f 0.45 | lull filter f 0.30 | ✗ |
| (Amendment 2) agent-state conditioning | scaffold E 0.112 (z 4.1), f 0.11; all incl. pauses f 0.81 | edge only f 0.11; + infra f 0.11 | ✗ |
| per-cause drop (f) | scheduled 0.04, edge 0.07, infra_error -0.01, pause 0.25, consolidation 0.00, unexplained -0.31 | – | descriptive |
| P7 (consistency) O6 formula / observed Δg | 1.99 | within 2× | ✓ |
| talk spin (secondary) | E raw 0.229 (z 9.4); stall 0.223; scaffold-masked 0.231 | N1 | descriptive |
| O5 λ₁/edge, unit 4 | raw 1.23, lull 0.97, stall 0.99, scaffold-masked 1.06 | cross-day surrogate edge (95%) | descriptive |

Data: `data/processed/H38-platform-stalls/G04/result.json`; minutes and runs in the shared `stall_minutes.parquet` / `outages.parquet`.

## Scorecard (period-specific axes)
- **C:** explained share above its N1 surrogate level; raw gain significant vs N1; stall-adjusted z 2.2, scaffold-masked z 4.1.
- **G:** 3 village-off gap(s), 0.81 of their minutes inside the operator's pause → resume interval.

## Round 1b (improved data, 2026-10-04)
Re-run of the same pipeline (`analysis/run_period.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` sidecar; the round-1 tables dropped about half of all events. Predictions unchanged; the period verdict uses the same rule. The DQ8 row reports the corrected null (whole-day N1 / block-shift nulls reject 28–34% of independent swarms; 2–4% after trimming).

| Quantity | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share (independent expectation) | 0.230 (0.219) | 0.149 (0.135) |
| explained share (N1 surrogate) | 0.76 (0.74) | 0.93 (0.94) |
| largest cause of joint-silence minutes | scheduled | scheduled |
| raw g_eq active, E (z vs N1, whole-day grid) | 0.125, 0.126 (4.5) | 0.218, 0.217 (8.0) |
| f_stall (pre-registered) · f_scaffold (headline) | 0.45 · 0.11 | 0.29 · 0.11 |
| **DQ8 null** (trimmed to the all-present window before block-shift surrogates): E_trim (z), f_trim | not computed | 0.198 (6.4), 0.09 |
| trimmed + scaffold-conditioned: E (z) | not computed | 0.203 (6.8) |
| talk spin E raw (z) → trimmed E (z) | 0.229 (9.4) | 0.250 (11.3) → 0.268 (9.9) |
| per-period verdict (card rule) | mixed | failed |

Data: `data/processed/H38-platform-stalls/r1b/G04/result.json`.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
- 2026-10-04: 2025-06-18 has a mid-day operator pause → resume pair (a 300-min village-off gap inside the calendar window); 2025-06-12 a 40-min edge gap.
