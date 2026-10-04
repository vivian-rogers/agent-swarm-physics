# H12 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F (free) · N = 7 at start (present: 7) · rooms holding ≥ 3 present agents: 16: 1 · 5 non-holdout days. 

## Why this period
Free week with operator rules, regime I (N = 7): the re-expansion reference for P9.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1–P5:** not scored (N < 10); random-matrix results are reported descriptively.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6:** no usable transition into #16 (previous period held out, absent, or a regime change).
- **P9 (free week):** mean PRday above the median of the regime-I shared-objective weeks (#13, #18, #19, #24, #25, #26, #30).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 (not scored) | 7 | 5 | 1 | 0 | 1 / 1 / 1 | 1.70 (0.74) | 1.00 · 0.99 | 1 (one room) | 1 (1.21) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 14.88 (6 agents × 15 statements; 5 of 5 days valid); mean spread TV 27.84; between-agent PR (noise-corrected) 3.78.
- P7: PRday day 1 = 15.05 vs median of later days 15.31; within-day PR30 slope day 1 -0.973 vs other days -0.362 per window.

| Check | Holds |
| --- | --- |
| P7a (PRday day 1 < later) | yes |
| P9 (free above shared median) | yes |

Figure: `figures/G16_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G16/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- Only the dimensionality checks apply here (N < 10).
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
