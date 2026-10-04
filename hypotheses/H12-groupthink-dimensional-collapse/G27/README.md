# H12 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-23)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K (competition) · N = 10 at start (present: 10) · rooms holding ≥ 3 present agents: 27: 1 · 10 non-holdout days. 

## Why this period
Non-holdout period with N ≥ 10 (competition); scored for P1–P4 and the per-period dimensionality checks.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions as they apply here (card: `../README.md`, incl. Amendment 1).

- **P1 / P1′ (activity modes):** in 27: k_cd ∈ {1, 2, 3}; also after the lull filter. Naive MP count ≥ k_cd + 1 likely.
- **P2 (market mode = Curie–Weiss mode):** if k_cd ≥ 1, majority-sign share ≥ 0.8 and VR/λ₁ ≥ 0.7; the lull filter lowers λ₁/edge by ≥ 30% (H02: lulls drive much of the co-activation).
- **P3 (talk):** k_cd(talk) ≤ k_cd(activity). Single-room: no room test.
- **P4 (content):** k_cd(content) ≥ 1 (powered per Amendment 1).
- **P5 (family mode):** descriptive only.
- **P7 (re-expansion):** PRday(day 1) < median PRday(days 2+); within day 1, PR30 rises from the first to the last hour more than on other days.
- **P6 (kickoff collapse):** transition #26 → #27 (2026-01-09 → 2026-01-12): ΔPR_kick = PR₁ₕ(day 1) − PR₁ₕ(last day of #26) < 0.

**What would count against it here:** k_cd = 0 (no collective mode beyond the schedule) or ≥ 4; a localized top mode; PRday on day 1 above later days (consensus forming over the week rather than imposed at the kickoff); a positive kickoff contrast.
**Period verdict rule (Amendment 1, item 9):** supported if every applicable headline check holds, failed if none does, mixed otherwise.

## Result
<!-- RESULT -->
**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):

| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | 10 | 10 | 1 | 1 | 1 / 1 / 1 | 1.31 (1.14) | 1.00 · 0.99 | 1 (one room) | 1 (2.34) |

**Dimensionality arm** (chat, whitened d = 32):

- Mean PRday 15.56 (6 agents × 15 statements; 10 of 10 days valid); mean spread TV 20.49; between-agent PR (noise-corrected) 3.92.
- P7: PRday day 1 = 15.91 vs median of later days 16.12; within-day PR30 slope day 1 0.797 vs other days -0.155 per window.
- P6: first-hour PR 11.53 (last day of #26) → 8.69 (day 1): Δ = -2.84 (-25%); placebo percentile 0.12; ΔTV 4.88.

| Check | Holds |
| --- | --- |
| HH77 (k_cd ∈ 1–3, uniform top mode) | yes |
| P7a (PRday day 1 < later) | yes |
| P6 (ΔPR_kick < 0) | yes |

Figure: `figures/G27_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G27/`.
<!-- /RESULT -->

## Scorecard (period-specific axes)
<!-- SCORE -->
- **C (nulls):** activity modes beyond the cross-day null in 1/1 unit(s); after the lull filter in 1/1.
- **D (Curie–Weiss shape):** sign share 1.00; VR/λ₁ 0.99.
- **E (NE34 kickoff):** ΔPR_kick = -2.84 (negative).
<!-- /SCORE -->

## Notes
- 2026-10-03: folder created and prediction written before running on this period.
- 2026-10-03: results filled by `analysis/write_period_folders.py results` from `data/processed/H12-groupthink-dimensional-collapse/`.
