# H12 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-09)

**Verdict:** mixed
**Verdict (1b):** mixed (replication, round 1: mixed; corrected activity table, same rule) · native vote test: mixed
**Role:** native (round 1b: the three vote instants; round-1 role: exploratory replication)
**Period:** regime I · mode C (shared objective) · N = 10 at start (present: 10) · rooms holding ≥ 3 present agents: 26: 1 · 5 non-holdout days. 

## Why this period
Non-holdout period with N ≥ 10 (shared objective); scored for P1–P4 and the per-period dimensionality checks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 26: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Single-room: no room test.
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1). Mode C: λ₁/edge above the mode-I/F median of the regime.
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #25 → #26 (2026-01-02 → 2026-01-05): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #25) < 0.
- **P9 (shared week):** mean PRday below the regime-I free weeks (#11, #16, #31).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Round 1b native test: the three vote instants (DQ6 ground truth)
*Prediction written 2026-10-04 06:35 UTC, before computing any statistic around these instants. Seen before: round-1 G26 numbers above (whole-period PRday, kickoff ΔPR); DQ6's vote timeline (design facts): 01-05 approval vote 19:26–19:30 UTC ending in a 9–9–9 tie, runoff 19:32–19:34 (7–1–0), result 19:35; 01-09 confirmatory vote 18:45–19:00, result 19:00 (9–0).*

**Why:** HH58 says consensus compresses what agents say. #26 has consensus events at exact, ground-truth instants (DQ9: "collapse at three vote instants"), unlike the narrated "consensus weeks" of P8.

**Design:** chat statements, whitened d = 32 (bge, H12's ruler) with gte as a check. Two event windows, each 30 min, starting at the vote: E1 = 01-05 19:26 → 19:56 (approval tie, runoff and result), E2 = 01-09 18:45 → 19:15 (confirmatory vote and result). Statistic: the round-1 PR30 estimator (cap 8 per agent, rarefied n = 30, 20 draws; if a window has fewer than 30 eligible statements, n = 20 with the reference recomputed at the same n). Reference: the same estimator on every other non-overlapping 30-min window of #26 (each day's window grid, H12's `win30`), excluding windows that overlap E1 or E2.
- **N26a (collapse at the votes).** Both event windows have PR below the 25th percentile of the reference windows.
- **N26b (spread).** Both event windows have TV below the reference median (descriptive).
- **N26c (model robustness).** N26a's percentile ranks are below 0.5 under gte too.
- Credence: N26a 0.3.
- **Verdict rule (native):** supported if N26a and N26c hold; failed if both event windows sit at or above the reference median (bge); mixed otherwise.

**Round 1b native result (run 2026-10-04 06:45 UTC, `analysis/r1b_native.py`; `data/processed/H12-groupthink-dimensional-collapse/r1b/native/g26_windows.parquet`).** Both event windows have ≥ 30 capped statements (E1: 100 chat statements, 10 agents; E2: 61, 10 agents), so n = 30; 27 reference windows.

| Vectors | E1 (01-05 tie, runoff, result): PR, percentile | E2 (01-09 confirmatory vote): PR, percentile | reference q25 · median |
| --- | --- | --- | --- |
| bge, H12's ruler (primary) | 9.4, 0.07 | 11.7, 0.37 | 11.4 · 12.8 |
| bge, shared unit-normalized | 9.9, 0.04 | 12.3, 0.30 | 12.0 · 13.5 |
| gte (second model) | 8.6, 0.04 | 10.4, 0.11 | 11.7 · 12.8 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N26a both event windows below the reference q25 (bge) | E1 yes (0.07); E2 no (0.37) | ✗ |
| N26b both event windows' TV below the reference median | E1 above (percentile 1.00), E2 below (0.26) | ✗ |
| N26c both percentiles < 0.5 under gte | 0.04, 0.11 | ✓ |

**Native verdict: mixed.** The contested vote (the 9–9–9 approval tie and the runoff that settled it within ~100 s) is among the lowest-dimensional half hours of the week in all three vector sets (percentile 0.04–0.07), with a *wider* spread: agents say fewer kinds of things but say them far apart (campaigning for different candidates). The uncontested 9–0 re-election is low but not extreme (0.11–0.37). Collapse at a vote is real where there is something to decide.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26 | 10 | 5 | 1 | 0 | 1 / 1 / 1 | 1.37 (0.71) | 1.00 · 0.99 | 1 (one room) | 1 (2.34) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 14.91 (6 agents × 15 statements; 4 of 5 days valid); mean spread TV 23.95; between-agent PR (noise-corrected) 4.89.
- P7: PRday day 1 = 14.73 vs median of later days 14.53; within-day PR30 slope day 1 0.698 vs other days -0.311 per window.
- P6: first-hour PR 15.70 (last day of #25) → 12.08 (day 1): Δ = -3.62 (-23%); placebo percentile 0.06; ΔTV -4.33.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | no |
| P6 (ΔPR_kick < 0) | yes |
| P9 (shared below free median) | no |

Figure: `figures/G26_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G26/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 0/1.
- **D (Curie–Weiss shape):** sign share 1.00; VR/λ₁ 0.99.
- **E (NE34 kickoff):** ΔPR_kick = -3.62 (negative).
<!-- /SCORE -->

## Round 1b (improved data, 2026-10-04)
Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window *before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).

| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| units | 26 | 26 |
| k activity (cross-day edge) | 1 | 1 |
| λ₁/edge activity (cross-day) | 1.37 | 1.70 |
| k after the lull filter (joint-lull share) | 0 (0.39) | 1 (0.05) |
| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | 1 (1.21) |
| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | 1 |
| k talk (cross-day) → trimmed block-shift | 1 | 1 → 1 |
| k content (inputs unchanged) | 1 | 1 |
| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | 14.91 | 14.09 (gte) |
| per-period verdict (card rule, Amendment 1 item 9) | mixed | mixed |

Data: `data/processed/H12-groupthink-dimensional-collapse/r1b/G26/`.

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
