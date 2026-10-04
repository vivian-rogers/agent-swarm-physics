# H04 × NE10: the first nudges ever (#30 2026-02-13, #31 2026-02-16 → 02-20)

**Verdict:** mixed
**Role:** native (round 1b, non-holdout; transition exception c)
**Period:** regime I · #30 (adopt a park; units 30a/30b) and #31 (free week; 31a–31d) · N ≈ 11–12 · #general. The CHANGELOG dates the auto-nudger to 02-10, but the first nudge in the record is 02-13 (12 nudges, all that day); 25 more follow in #31. #28 and #29 (before) are held out.

## Why this unit
DQ9's native test for H04: the kernel of a brand-new forcing source, with no habituation (H30, H35: first nudges work, repeats don't). Every nudge here is a first nudge to its target. Round 1 had only "too few (I: 37 nudges)" for regime I and an NE10 swarm-level comparison that came out thin.

## Prediction
*Written 2026-10-04 06:44 UTC, before any round-1b run (round 1 computed only swarm-level NE10 statistics, not these kernels).*
Corrected design (round 1b): `activity_bins_fixed`, target = the nudge's leading @, no future-kick isolation, controls eligible on past information only (no direct kick to the agent in [m − 30, m]), day fixed effect (controls from the same day and stratum where available), presence mask.
- **N10a (a brand-new source works):** target A30 point estimate ≥ 1.0 extra active minute, with a day-bootstrap CI excluding 0 (37 nudges: may be underpowered).
- **N10b (read-out is fast in chat mode):** the median delay from the nudge to the target's receiving call (ledger `age_s` at the call that received it) is ≤ 90 s (regime-I chat-mode calls are scheduled about every 74 s).
- **N10c (no spillover):** bystander A30 within ±0.5 minutes.

**Verdict rule (fixed now):** supported if N10a (CI excluding 0) and N10b hold; mixed if N10a's point estimate is ≥ 1.0 with a CI including 0, or only one of N10a/N10b holds; failed if the A30 point estimate is ≤ 0.

## Result
*Run 2026-10-04 (`analysis/r1b.py --suite NE10_G30_G31`; `data/processed/H04-reversible-forcing/r1b/NE10_G30_G31.json`). 37 nudges (12 on 02-13, 25 in #31), 34 target cells; strata fallback 41%.*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N10a: target A30 ≥ 1.0, CI excluding 0 | all target cells +0.68 [-0.12, +2.45] (day FE; +0.39 [-0.40, +2.10] without); first nudges +0.99 [+0.22, +2.38] (n = 25); aligned on the receiving call +1.39 [+0.58, +2.54] | fail (point 0.68 < 1.0, CI includes 0) |
| N10b: median read-out ≤ 90 s | 31 s to context assembly (q90 116 s); 29 of the 37 receiving calls follow a busy previous call (no pause) | pass |
| N10c: bystander A30 within ±0.5 | +0.12 [-0.29, +0.40] | pass |

- **Placebo failure:** the pre-window [−30, −16] is +1.09 [+0.24, +1.85]: nudged agents were already more active than their matched controls well before the nudge, so the A30 level is not interpretable here (regime-I discrete sessions; the nudger fires between sessions).
- The kernel aligned on the receiving call starts within minutes (t₂₅ = 4 min), as in #51.

**Verdict: mixed** (N10b holds, N10a fails; the placebo makes the level unreliable).

## Notes
- 2026-10-04: folder created with the prediction (round 1b native layer, DQ9 cross-index).
