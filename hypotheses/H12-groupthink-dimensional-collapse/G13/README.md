# H12 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-19)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 6 at start (present: 6) · rooms holding ≥ 3 present agents: 13: 1 · 10 non-holdout days. 

## Why this period
Shared-objective week in regime I (N = 6), one of P9's comparison weeks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1–P5:** not scored (N < 10); random-matrix results are reported descriptively.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #12 → #13 (2025-09-05 → 2025-09-08): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #12) < 0.
- **P9 (shared week):** mean PRday below the regime-I free weeks (#11, #16, #31).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 13 (not scored) | 6 | 10 | 1 | 0 | 0 / 1 / 1 | 1.05 (0.91) | 1.00 · 0.98 | 1 (one room) | 1 (1.68) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 13.70 (6 agents × 15 statements; 10 of 10 days valid); mean spread TV 28.00; between-agent PR (noise-corrected) 3.01.
- P7: PRday day 1 = 16.87 vs median of later days 14.59; within-day PR30 slope day 1 -0.384 vs other days -0.244 per window.
- P6: first-hour PR 13.55 (last day of #12) → 13.26 (day 1): Δ = -0.29 (-2%); placebo percentile 0.46; ΔTV 1.66.

| Check | Holds |
| --- | --- |
| P7a (PRday day 1 < later) | no |
| P6 (ΔPR_kick < 0) | yes |
| P9 (shared below free median) | yes |

Figure: `figures/G13_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G13/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **E (NE34 kickoff):** ΔPR_kick = -0.29 (negative).
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
