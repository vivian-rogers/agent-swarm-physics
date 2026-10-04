# H12 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; corrected activity table, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F (free) · N = 12 at start (present: 10) · rooms holding ≥ 3 present agents: 31: 1 · 5 non-holdout days. 

## Why this period
Free week in which about nine agents converged on the same task (competing PRs): a consensus event without a goal field, and a free week for P9.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 31: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Single-room: no room test.
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1).
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #30 → #31 (2026-02-13 → 2026-02-16): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #30) < 0.
- **P8 (consensus):** PR30 declines over days 2..D (slope < 0 with time-of-day fixed effects), and the slope is below the median slope of the regime's non-consensus units.
- **P9 (free week):** mean PRday above the median of the regime-I shared-objective weeks (#13, #18, #19, #24, #25, #26, #30).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31 | 10 | 5 | 1 | 0 | 0 / 1 / 1 | 1.60 (0.85) | 1.00 · 0.97 | 1 (one room) | 1 (1.90) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 16.23 (6 agents × 15 statements; 5 of 5 days valid); mean spread TV 24.02; between-agent PR (noise-corrected) 4.63.
- P7: PRday day 1 = 16.80 vs median of later days 15.84; within-day PR30 slope day 1 0.265 vs other days 0.034 per window.
- P6: first-hour PR 15.84 (last day of #30) → 13.18 (day 1): Δ = -2.66 (-17%); placebo percentile 0.13; ΔTV 5.77.
- P8: PR30 slope over days 2..D (window-of-day FE) -0.156 per day vs regime median of non-consensus units 0.189.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | no |
| P6 (ΔPR_kick < 0) | yes |
| P8 (consensus decline) | yes |
| P9 (free above shared median) | yes |

Figure: `figures/G31_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G31/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 0/1.
- **D (Curie–Weiss shape):** sign share 1.00; VR/λ₁ 0.97.
- **E (NE34 kickoff):** ΔPR_kick = -2.66 (negative).
<!-- /SCORE -->

## Round 1b (improved data, 2026-10-04)
Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window *before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).

| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| units | 31 | 31 |
| k activity (cross-day edge) | 1 | 0 |
| λ₁/edge activity (cross-day) | 1.60 | 0.93 |
| k after the lull filter (joint-lull share) | 0 (0.16) | 0 (0.00) |
| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | 0 (0.99) |
| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | 0 |
| k talk (cross-day) → trimmed block-shift | 1 | 1 → 1 |
| k content (inputs unchanged) | 1 | 1 |
| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | 16.23 | 14.82 (gte) |
| per-period verdict (card rule, Amendment 1 item 9) | mixed | mixed |

Data: `data/processed/H12-groupthink-dimensional-collapse/r1b/G31/`.

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
