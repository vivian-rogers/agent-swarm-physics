# H12 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode F (free) · N = 13 at start (present: 12) · rooms holding ≥ 3 present agents: 37: 2 · 3 non-holdout days. 

## Why this period
The only non-holdout free period in regime III (3 days): P9's regime-III reference; first goal in regime III; two rooms.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 37: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation). Expect λ₁/edge above the regime-I median (regime III).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Two-room unit(s) 37: a signal talk eigenvector separates the rooms (p < 0.05).
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1).
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #36 → #37 (2026-03-27 → 2026-03-30): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #36) < 0.
- **P9 (free week):** mean PRday above the median of the regime-III shared-objective weeks (#38, #40, #44).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | 12 | 3 | 1 | 0 | 1 / 1 / 1 | 1.78 (0.47) | 1.00 · 0.97 | 1 (0.130) | 1 (1.20) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 15.83 (6 agents × 15 statements; 1 of 3 days valid); mean spread TV 20.47; between-agent PR (noise-corrected) 2.55.
- P7: PRday day 1 = 15.83 vs median of later days –; within-day PR30 slope day 1 -1.814 vs other days – per window.
- P6: first-hour PR 11.81 (last day of #36) → 16.76 (day 1): Δ = 4.95 (42%); placebo percentile 0.97; ΔTV -5.71.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P6 (ΔPR_kick < 0) | no |
| P9 (free above shared median) | yes |

Figure: `figures/G37_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G37/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 0/1.
- **D (Curie–Weiss shape):** sign share 1.00; VR/λ₁ 0.97.
- **G (rooms):** talk-mode room separation p = 0.130 (– = no signal talk mode).
- **E (NE34 kickoff):** ΔPR_kick = 4.95 (not negative).
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
