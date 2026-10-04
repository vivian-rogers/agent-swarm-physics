# H12 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; corrected activity table, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 7 at start (present: 6) · rooms holding ≥ 3 present agents: 18: 1 · 10 non-holdout days. 

## Why this period
Shared-objective weeks in regime I (N = 6), one of P9's comparison weeks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1–P5:** not scored (N < 10); random-matrix results are reported descriptively.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #17 → #18 (2025-10-17 → 2025-10-20): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #17) < 0.
- **P9 (shared week):** mean PRday below the regime-I free weeks (#11, #16, #31).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18 (not scored) | 6 | 10 | 1 | 0 | 1 / 1 / 1 | 1.51 (0.85) | 1.00 · 0.99 | 1 (one room) | 1 (2.70) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 14.71 (6 agents × 15 statements; 8 of 10 days valid); mean spread TV 22.02; between-agent PR (noise-corrected) 2.92.
- P7: PRday day 1 = – vs median of later days 14.10; within-day PR30 slope day 1 -1.086 vs other days -0.367 per window.
- P6: first-hour PR 12.10 (last day of #17) → 16.40 (day 1): Δ = 4.30 (36%); placebo percentile 0.95; ΔTV 0.47.

| Check | Holds |
| --- | --- |
| P6 (ΔPR_kick < 0) | no |
| P9 (shared below free median) | yes |

Figure: `figures/G18_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G18/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **E (NE34 kickoff):** ΔPR_kick = 4.30 (not negative).
<!-- /SCORE -->

## Round 1b (improved data, 2026-10-04)
Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window *before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).

| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| units | 18 | 18 |
| k activity (cross-day edge) | 1 | 1 |
| λ₁/edge activity (cross-day) | 1.51 | 1.10 |
| k after the lull filter (joint-lull share) | 0 (0.20) | 1 (0.02) |
| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | 1 (1.13) |
| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | 1 |
| k talk (cross-day) → trimmed block-shift | 1 | 1 → 1 |
| k content (inputs unchanged) | 1 | 1 |
| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | 14.71 | 13.83 (gte) |
| per-period verdict (card rule, Amendment 1 item 9) | mixed | mixed |

Data: `data/processed/H12-groupthink-dimensional-collapse/r1b/G18/`.

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
