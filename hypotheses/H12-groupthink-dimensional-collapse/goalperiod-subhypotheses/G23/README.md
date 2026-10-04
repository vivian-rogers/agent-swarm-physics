# H12 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-19)

**Verdict:** mixed
**Verdict (1b):** failed (round 1: mixed; corrected activity table, same rule)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime I · mode K (competition) · N = 10 at start (present: 10) · rooms holding ≥ 3 present agents: 23: 1 · 5 non-holdout days. 

## Why this period
Non-holdout period with N ≥ 10 (competition); scored for P1–P4 and the per-period dimensionality checks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 23: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Single-room: no room test.
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1).
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6:** no usable transition into #23 (previous period held out, absent, or a regime change).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 23 | 10 | 5 | 1 | 1 | 1 / 1 / 1 | 1.86 (1.05) | 1.00 · 0.99 | 1 (one room) | 1 (1.79) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 12.54 (6 agents × 15 statements; 5 of 5 days valid); mean spread TV 18.22; between-agent PR (noise-corrected) 4.47.
- P7: PRday day 1 = 14.07 vs median of later days 12.33; within-day PR30 slope day 1 0.016 vs other days -0.251 per window.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | no |

Figure: `figures/G23_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G23/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 1/1.
- **D (Curie–Weiss shape):** sign share 1.00; VR/λ₁ 0.99.
<!-- /SCORE -->

## Round 1b (improved data, 2026-10-04)
Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window *before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).

| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| units | 23 | 23 |
| k activity (cross-day edge) | 1 | 0 |
| λ₁/edge activity (cross-day) | 1.86 | 0.95 |
| k after the lull filter (joint-lull share) | 1 (0.20) | 0 (0.00) |
| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | 0 (0.99) |
| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | 0 |
| k talk (cross-day) → trimmed block-shift | 1 | 1 → 1 |
| k content (inputs unchanged) | 1 | 1 |
| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | 12.54 | 11.23 (gte) |
| per-period verdict (card rule, Amendment 1 item 9) | mixed | failed |

Data: `data/processed/H12-groupthink-dimensional-collapse/r1b/G23/`.

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
