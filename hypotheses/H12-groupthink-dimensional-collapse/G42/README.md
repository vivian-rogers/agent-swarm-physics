# H12 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I (individual objective) · N = 15 at start (present: 15) · rooms holding ≥ 3 present agents: 42: 2 · 5 non-holdout days. 

## Why this period
Non-holdout period with N ≥ 10 (individual objective); scored for P1–P4 and the per-period dimensionality checks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 42: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation). Expect λ₁/edge above the regime-I median (regime III).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Two-room unit(s) 42: a signal talk eigenvector separates the rooms (p < 0.05).
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1).
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #41 → #42 (2026-05-15 → 2026-05-18): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #41) < 0.

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 15 | 5 | 1 | 1 | 1 / 1 / 1 | 1.71 (1.10) | 1.00 · 0.98 | 0 (–) | 1 (1.46) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 16.82 (6 agents × 15 statements; 3 of 5 days valid); mean spread TV 23.01; between-agent PR (noise-corrected) 4.46.
- P7: PRday day 1 = 17.43 vs median of later days 16.52; within-day PR30 slope day 1 – vs other days -0.772 per window.
- P6: first-hour PR 11.82 (last day of #41) → 15.76 (day 1): Δ = 3.93 (33%); placebo percentile 0.92; ΔTV -6.37.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | no |
| P6 (ΔPR_kick < 0) | no |

Figure: `figures/G42_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G42/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 1/1.
- **D (Curie–Weiss shape):** sign share 1.00; VR/λ₁ 0.98.
- **G (rooms):** talk-mode room separation p = – (– = no signal talk mode).
- **E (NE34 kickoff):** ΔPR_kick = 3.93 (not negative).
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
