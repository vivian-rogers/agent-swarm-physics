# H12 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; corrected activity table, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C (shared objective) · N = 15 at start (present: 15) · rooms holding ≥ 3 present agents: 40: 1 · 5 non-holdout days. 

## Why this period
Named consensus event: 15 agents coordinated a shared 3D universe in a dedicated room after the 05-04 room merge; strongest H02 collective co-activation (βJ₀ = 0.50).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 40: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation). Expect λ₁/edge above the regime-I median (regime III).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Single-room: no room test.
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1). Mode C: λ₁/edge above the mode-I/F median of the regime.
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #39 → #40 (2026-05-01 → 2026-05-04): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #39) < 0.
- **P8 (consensus):** PR30 declines over days 2..D (slope < 0 with time-of-day fixed effects), and the slope is below the median slope of the regime's non-consensus units.
- **P9 (shared week):** mean PRday below the regime-III free weeks (#37).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | 15 | 5 | 1 | 1 | 1 / 1 / 1 | 1.63 (1.30) | 1.00 · 0.97 | 1 (one room) | 1 (1.56) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 9.86 (6 agents × 15 statements; 5 of 5 days valid); mean spread TV 22.88; between-agent PR (noise-corrected) 3.95.
- P7: PRday day 1 = 13.08 vs median of later days 9.24; within-day PR30 slope day 1 0.009 vs other days 0.015 per window.
- P8: PR30 slope over days 2..D (window-of-day FE) 0.170 per day vs regime median of non-consensus units -0.176.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | no |
| P8 (consensus decline) | no |
| P9 (shared below free median) | yes |

Figure: `figures/G40_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G40/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 1/1.
- **D (Curie–Weiss shape):** sign share 1.00; VR/λ₁ 0.97.
<!-- /SCORE -->

## Round 1b (improved data, 2026-10-04)
Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window *before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).

| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| units | 40 | 40 |
| k activity (cross-day edge) | 1 | 1 |
| λ₁/edge activity (cross-day) | 1.63 | 1.10 |
| k after the lull filter (joint-lull share) | 1 (0.05) | 0 (0.02) |
| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | 0 (0.99) |
| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | 0 |
| k talk (cross-day) → trimmed block-shift | 1 | 0 → 0 |
| k content (inputs unchanged) | 1 | 1 |
| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | 9.86 | 9.36 (gte) |
| per-period verdict (card rule, Amendment 1 item 9) | mixed | mixed |

Data: `data/processed/H12-groupthink-dimensional-collapse/r1b/G40/`.

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
- 2026-10-03 (post hoc, after the verdict; no effect on it): the low PRday here goes with agents repeating themselves. On average 16% of chat statements per day are near-copies (cosine > 0.95) of the same agent's earlier statement that day, vs 2.8% copying another agent. Across regime-III days, Spearman(self-repetition, PRday) = −0.75. So the dimensional collapse here is looping, not groupthink. After removing self-repeats, PRday rises (see `data/processed/H12-groupthink-dimensional-collapse/posthoc_dedup.json`) but stays below the other regime-III periods.
