# H12 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I/K (private roles (individual/competitive)) · N = 21 at start (present: 21, 24, 27, 27, 31) · rooms holding ≥ 3 present agents: 51a: 1, 51b: 1, 51c: 1, 51d: 1, 51e: 1 · 45 non-holdout days. Splits: 51a (3 d, III), 51b (19 d, III), 51c (14 d, III), 51d (7 d, III), 51e (2 d, III) (H01 step changes).

## Why this period
The private-role era (21–31 present agents, 8-h days): largest N and longest units; split at NE32, #focus and NE33.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 51a, 51b, 51c, 51d, 51e: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation). Expect λ₁/edge above the regime-I median (regime III).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Single-room: no room test.
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1).
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6:** no usable transition into #51 (previous period held out, absent, or a regime change).

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 21 | 3 | 1 | 0 | 1 / 1 / 1 | 1.64 (0.36) | 1.00 · 0.97 | 1 (one room) | 1 (1.25) |
| 51b | 24 | 19 | 1 | 1 | 1 / 3 / 1 | 2.53 (1.66) | 1.00 · 0.94 | 2 (one room) | 1 (1.51) |
| 51c | 27 | 14 | 1 | 1 | 1 / 2 / 1 | 2.45 (1.61) | 1.00 · 0.93 | 1 (one room) | 2 (1.37) |
| 51d | 27 | 7 | 1 | 1 | 1 / 3 / 1 | 2.12 (1.08) | 1.00 · 0.90 | 1 (one room) | 1 (1.15) |
| 51e | 31 | 2 | 0 | 0 | 1 / 3 / 2 | 0.93 (0.89) | 0.90 · 0.91 | 0 (one room) | 1 (1.08) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 15.91 (6 agents × 15 statements; 45 of 45 days valid); mean spread TV 29.43; between-agent PR (noise-corrected) 7.75.
- P7: PRday day 1 = 16.78 vs median of later days 15.65; within-day PR30 slope day 1 -0.033 vs other days 0.180 per window.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | no |

Figure: `figures/G51_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G51/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 4/5 unit(s); after the lull filter in 3/5.
- **D (Curie–Weiss shape):** sign share 1.00, 1.00, 1.00, 1.00, 0.90; VR/λ₁ 0.97, 0.94, 0.93, 0.90, 0.91.
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
