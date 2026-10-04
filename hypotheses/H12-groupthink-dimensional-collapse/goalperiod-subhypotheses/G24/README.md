# H12 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-26)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; corrected activity table, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 10 at start (present: 10) · rooms holding ≥ 3 present agents: 24: 1 · 5 non-holdout days. 

## Why this period
Non-holdout period with N ≥ 10 (shared objective); scored for P1–P4 and the per-period dimensionality checks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 24: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Single-room: no room test.
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1). Mode C: λ₁/edge above the mode-I/F median of the regime.
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #23 → #24 (2025-12-19 → 2025-12-22): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #23) < 0.
- **P9 (shared week):** mean PRday below the regime-I free weeks (#11, #16, #31).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 24 | 10 | 5 | 0 | 0 | 0 / 1 / 0 | 0.93 (0.89) | 0.70 · 0.85 | 1 (one room) | 1 (1.73) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 13.79 (6 agents × 15 statements; 5 of 5 days valid); mean spread TV 21.54; between-agent PR (noise-corrected) 4.67.
- P7: PRday day 1 = 14.72 vs median of later days 12.44; within-day PR30 slope day 1 -0.139 vs other days -0.376 per window.
- P6: first-hour PR 11.95 (last day of #23) → 13.80 (day 1): Δ = 1.85 (16%); placebo percentile 0.73; ΔTV 3.67.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | no |
| P7a (PRday day 1 < later) | no |
| P6 (ΔPR_kick < 0) | no |
| P9 (shared below free median) | yes |

Figure: `figures/G24_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G24/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 0/1 unit(s); after the lull filter in 0/1.
- **D (Curie–Weiss shape):** sign share 0.70; VR/λ₁ 0.85.
- **E (NE34 kickoff):** ΔPR_kick = 1.85 (not negative).
<!-- /SCORE -->

## Round 1b (improved data, 2026-10-04)
Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window *before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).

| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| units | 24 | 24 |
| k activity (cross-day edge) | 0 | 0 |
| λ₁/edge activity (cross-day) | 0.93 | 0.86 |
| k after the lull filter (joint-lull share) | 0 (0.00) | 0 (0.00) |
| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | 0 (0.99) |
| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | 0 |
| k talk (cross-day) → trimmed block-shift | 1 | 1 → 1 |
| k content (inputs unchanged) | 1 | 1 |
| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | 13.79 | 13.02 (gte) |
| per-period verdict (card rule, Amendment 1 item 9) | mixed | mixed |

Data: `data/processed/H12-groupthink-dimensional-collapse/r1b/G24/`.

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
