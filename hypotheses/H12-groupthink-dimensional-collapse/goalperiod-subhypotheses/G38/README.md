# H12 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; corrected activity table, same rule)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime III · mode C (shared objective) · N = 12 at start (present: 12, 12, 13) · rooms holding ≥ 3 present agents: 38a: 2, 38b: 2, 38c: 2 · 17 non-holdout days. Splits: 38a (8 d, III), 38b (4 d, III), 38c (5 d, III) (H01 step changes).

## Why this period
Longest shared-objective period in regime III, split at NE17 (outreach approval) and NE18 (history search).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 38a, 38b, 38c: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation). Expect λ₁/edge above the regime-I median (regime III).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Two-room unit(s) 38a, 38b, 38c: a signal talk eigenvector separates the rooms (p < 0.05).
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1). Mode C: λ₁/edge above the mode-I/F median of the regime.
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #37 → #38 (2026-04-01 → 2026-04-02): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #37) < 0.
- **P9 (shared week):** mean PRday below the regime-III free weeks (#37).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 12 | 8 | 1 | 1 | 1 / 1 / 1 | 1.42 (1.28) | 1.00 · 0.97 | 1 (0.225) | 1 (1.52) |
| 38b | 12 | 4 | 1 | 0 | 1 / 1 / 1 | 1.60 (0.72) | 1.00 · 0.97 | 1 (0.636) | 1 (1.15) |
| 38c | 13 | 5 | 1 | 0 | 1 / 1 / 1 | 1.62 (0.95) | 1.00 · 0.93 | 1 (0.015) | 2 (1.07) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 9.31 (6 agents × 15 statements; 12 of 17 days valid); mean spread TV 24.20; between-agent PR (noise-corrected) 2.38.
- P7: PRday day 1 = 14.59 vs median of later days 8.93; within-day PR30 slope day 1 -0.799 vs other days -0.086 per window.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | no |
| P9 (shared below free median) | yes |

Figure: `figures/G38_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G38/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 3/3 unit(s); after the lull filter in 1/3.
- **D (Curie–Weiss shape):** sign share 1.00, 1.00, 1.00; VR/λ₁ 0.97, 0.97, 0.93.
- **G (rooms):** talk-mode room separation p = 0.225, 0.636, 0.015 (– = no signal talk mode).
<!-- /SCORE -->

## Round 1b (improved data, 2026-10-04)
Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window *before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).

| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| units | 38a, 38b, 38c | 38a, 38b, 38c |
| k activity (cross-day edge) | 1, 1, 1 | 1, 1, 1 |
| λ₁/edge activity (cross-day) | 1.42, 1.60, 1.62 | 1.09, 1.90, 1.04 |
| k after the lull filter (joint-lull share) | 1, 0, 0 (0.01, 0.19, 0.13) | 0, 0, 0 (0.01, 0.19, 0.01) |
| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | 0, 0, 0 (0.99, 0.98, 0.93) |
| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | 0, 0, 0 |
| k talk (cross-day) → trimmed block-shift | 1, 1, 1 | 2, 1, 1 → 2, 1, 1 |
| k content (inputs unchanged) | 1, 1, 2 | 1, 1, 2 |
| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | 9.31 | 10.17 (gte) |
| per-period verdict (card rule, Amendment 1 item 9) | mixed | mixed |

Data: `data/processed/H12-groupthink-dimensional-collapse/r1b/G38/`.

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
- 2026-10-03 (post hoc, after the verdict; no effect on it): the low PRday here goes with agents repeating themselves. On average 25% of chat statements per day are near-copies (cosine > 0.95) of the same agent's earlier statement that day, vs 1.8% copying another agent. Across regime-III days, Spearman(self-repetition, PRday) = −0.75. So the dimensional collapse here is looping, not groupthink. After removing self-repeats, PRday rises (see `data/processed/H12-groupthink-dimensional-collapse/posthoc_dedup.json`) but stays below the other regime-III periods.
