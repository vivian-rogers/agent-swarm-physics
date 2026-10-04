# H12 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-08-29)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F (free) · N = 7 at start (present: 7) · rooms holding ≥ 3 present agents: 11: 1 · 5 non-holdout days. 

## Why this period
Free week, regime I (N = 7): the re-expansion reference for P9.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1–P5:** not scored (N < 10); random-matrix results are reported descriptively.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #10 → #11 (2025-08-22 → 2025-08-25): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #10) < 0.
- **P9 (free week):** mean PRday above the median of the regime-I shared-objective weeks (#13, #18, #19, #24, #25, #26, #30).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11 (not scored) | 7 | 5 | 1 | 1 | 1 / 1 / 1 | 1.35 (1.03) | 1.00 · 0.99 | 1 (one room) | 1 (1.43) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 13.61 (6 agents × 15 statements; 4 of 5 days valid); mean spread TV 26.01; between-agent PR (noise-corrected) 3.60.
- P7: PRday day 1 = 10.49 vs median of later days 14.69; within-day PR30 slope day 1 0.597 vs other days -0.156 per window.
- P6: first-hour PR 6.43 (last day of #10) → 8.26 (day 1): Δ = 1.83 (28%); placebo percentile 0.73; ΔTV 5.96.

| Check | Holds |
| --- | --- |
| P7a (PRday day 1 < later) | yes |
| P6 (ΔPR_kick < 0) | no |
| P9 (free above shared median) | no |

Figure: `figures/G11_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G11/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **E (NE34 kickoff):** ΔPR_kick = 1.83 (not negative).
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
