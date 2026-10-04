# H12 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** mixed
**Verdict (1b):** failed (round 1: mixed; corrected activity table, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I (individual objective) · N = 15 at start (present: 15) · rooms holding ≥ 3 present agents: 39: 2 · 5 non-holdout days. 

## Why this period
Non-holdout period with N ≥ 10 (individual objective); scored for P1–P4 and the per-period dimensionality checks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 39: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation). Expect λ₁/edge above the regime-I median (regime III).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Two-room unit(s) 39: a signal talk eigenvector separates the rooms (p < 0.05).
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1).
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #38 → #39 (2026-04-24 → 2026-04-27): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #38) < 0.

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 15 | 5 | 1 | 0 | 1 / 2 / 2 | 1.08 (1.00) | 0.93 · 0.93 | 1 (0.006) | 1 (1.21) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 5.67 (6 agents × 15 statements; 1 of 5 days valid); mean spread TV 22.99; between-agent PR (noise-corrected) 3.81.
- P7: PRday day 1 = – vs median of later days 5.67; within-day PR30 slope day 1 – vs other days -0.127 per window.
- P6: first-hour PR 7.73 (last day of #38) → 14.46 (day 1): Δ = 6.73 (87%); placebo percentile 1.00; ΔTV 0.34.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P6 (ΔPR_kick < 0) | no |

Figure: `figures/G39_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G39/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 0/1.
- **D (Curie–Weiss shape):** sign share 0.93; VR/λ₁ 0.93.
- **G (rooms):** talk-mode room separation p = 0.006 (– = no signal talk mode).
- **E (NE34 kickoff):** ΔPR_kick = 6.73 (not negative).
<!-- /SCORE -->

## Round 1b (improved data, 2026-10-04)
Arm (a) spins rebuilt from DQ8's `activity_bins_fixed` (`scheme/build.py`, `run_units.py`, `evaluate.py --data-version fixed`); content and PR inputs do not depend on the activity table and are unchanged (re-checked with the second embedding model). Predictions and verdict rule unchanged. The DQ8 rows use the calibrated null for λ₁: each day trimmed to its all-present window *before* drawing block-shift surrogates (size 0.05; the cross-day edge has size 0.19 on trimmed and 0.62 on whole-day grids).

| Quantity (per unit) | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| units | 39 | 39 |
| k activity (cross-day edge) | 1 | 1 |
| λ₁/edge activity (cross-day) | 1.08 | 1.15 |
| k after the lull filter (joint-lull share) | 0 (0.01) | 1 (0.01) |
| **DQ8 null:** k activity, trimmed + block-shift edge (λ₁/edge) | not computed | 0 (0.94) |
| DQ8: k activity, trimmed + H38 stall mask (replaces the lull filter) | not computed | 0 |
| k talk (cross-day) → trimmed block-shift | 1 | 1 → 1 |
| k content (inputs unchanged) | 1 | 1 |
| mean PRday: round-1 bge ruler → gte (shared 32-d, second model) | 5.67 | 5.73 (gte) |
| per-period verdict (card rule, Amendment 1 item 9) | mixed | failed |

Data: `data/processed/H12-groupthink-dimensional-collapse/r1b/G39/`.

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
- 2026-10-03 (post hoc, after the verdict; no effect on it): the low PRday here goes with agents repeating themselves. On average 60% of chat statements per day are near-copies (cosine > 0.95) of the same agent's earlier statement that day, vs 0.0% copying another agent. Across regime-III days, Spearman(self-repetition, PRday) = −0.75. So the dimensional collapse here is looping, not groupthink. After removing self-repeats, PRday rises (see `data/processed/H12-groupthink-dimensional-collapse/posthoc_dedup.json`) but stays below the other regime-III periods.
