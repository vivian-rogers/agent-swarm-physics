# H12 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-14)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 7 at start (present: 7) · rooms holding ≥ 3 present agents: 19: 1 · 10 non-holdout days. 

## Why this period
Named consensus event: many puzzle-game concepts were brainstormed, then the swarm converged on one and shipped it (N = 7; enters P7–P9 only).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1–P5:** not scored (N < 10); random-matrix results are reported descriptively.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #18 → #19 (2025-10-31 → 2025-11-03): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #18) < 0.
- **P8 (consensus):** PR30 declines over days 2..D (slope < 0 with time-of-day fixed effects), and the slope is below the median slope of the regime's non-consensus units.
- **P9 (shared week):** mean PRday below the regime-I free weeks (#11, #16, #31).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19 (not scored) | 7 | 10 | 1 | 0 | 1 / 1 / 1 | 1.64 (0.94) | 1.00 · 0.99 | 1 (one room) | 1 (2.66) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 14.82 (6 agents × 15 statements; 10 of 10 days valid); mean spread TV 21.99; between-agent PR (noise-corrected) 3.03.
- P7: PRday day 1 = 15.95 vs median of later days 15.02; within-day PR30 slope day 1 -0.161 vs other days -0.125 per window.
- P6: first-hour PR 13.43 (last day of #18) → 13.52 (day 1): Δ = 0.09 (1%); placebo percentile 0.54; ΔTV -4.01.
- P8: PR30 slope over days 2..D (window-of-day FE) 0.160 per day vs regime median of non-consensus units 0.189.

| Check | Holds |
| --- | --- |
| P7a (PRday day 1 < later) | no |
| P6 (ΔPR_kick < 0) | no |
| P8 (consensus decline) | no |
| P9 (shared below free median) | yes |

Figure: `figures/G19_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G19/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **E (NE34 kickoff):** ΔPR_kick = 0.09 (not negative).
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
