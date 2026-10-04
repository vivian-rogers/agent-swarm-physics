# H12 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C (shared objective) · N = 16 at start (present: 16) · rooms holding ≥ 3 present agents: 44: 2 · 4 non-holdout days. 

## Why this period
Non-holdout period with N ≥ 10 (shared objective); scored for P1–P4 and the per-period dimensionality checks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 44: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation). Expect λ₁/edge above the regime-I median (regime III).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Two-room unit(s) 44: a signal talk eigenvector separates the rooms (p < 0.05).
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1). Mode C: λ₁/edge above the mode-I/F median of the regime.
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6:** no usable transition into #44 (previous period held out, absent, or a regime change).
- **P9 (shared week):** mean PRday below the regime-III free weeks (#37).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44 | 16 | 4 | 1 | 1 | 1 / 1 / 1 | 1.52 (1.22) | 1.00 · 0.92 | 1 (0.465) | 2 (1.37) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 16.87 (6 agents × 15 statements; 4 of 4 days valid); mean spread TV 25.74; between-agent PR (noise-corrected) 2.66.
- P7: PRday day 1 = 18.68 vs median of later days 15.78; within-day PR30 slope day 1 -0.536 vs other days -0.120 per window.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | no |
| P9 (shared below free median) | no |

Figure: `figures/G44_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G44/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 1/1.
- **D (Curie–Weiss shape):** sign share 1.00; VR/λ₁ 0.92.
- **G (rooms):** talk-mode room separation p = 0.465 (– = no signal talk mode).
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
