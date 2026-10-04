# H20 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** mixed (interrupted aging: no late slowing) (Amendment-2 null; pre-registered null: mixed)
**Role:** exploratory
**Period:** regime III · mode C · 14 agents with statements · 2 rooms with agent statements · 17 active days (208 agent-days with ≥ 8 statements). Step changes inside (kept in one unit; tested as rejuvenation, exception (c)): 2026-04-14, 2026-04-20.

## Why this period
One of the four long goals named in HH101 (t_w reaches 17 active days). Primary aging test. Shared objective (charity fundraiser), regime III (continuous computer use with consolidation). Two scaffold step changes inside (NE17 outreach approval, NE18 history search): do they rejuvenate?

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.34 / 0.38 / 0.46 against μ = 0.5 aging, 0.83 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Rejuvenation (S5):** pairs straddling 04-14 / 04-20 have lower C than the M1 fit predicts (negative step residual); descriptive.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = +0.102 (p = 0.002), A_c = +0.072 (p = 0.002), A_g = +0.111 (p = 0.002), A_late = -0.043, K = +0.117; co-primary design power vs μ = 0.5: 0.48 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.117 | < 0.002 | < 0.002 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.102 | < 0.002 | < 0.002 | > 0 (P2, co-primary) |
| A_c common removed | +0.072 | < 0.002 | < 0.002 | > 0 (P2, co-primary) |
| A_g field removed | +0.111 | < 0.002 | < 0.002 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.043 | 0.924 | 0.766 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.162 | 0.006 | 0.020 | P7 input |
| A_m swarm mean | +0.142 | < 0.002 | 0.042 | sign of A (P6) |
| A_m roster-stable | +0.156 | < 0.002 | 0.036 | reported |
| β_wk weekend gap | -0.003 | 0.333 | 0.383 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **mixed (interrupted aging: no late slowing)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 4.6/12.5; see the card): **mixed (interrupted aging: no late slowing)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 5.82, M0b 5.80, MQ 1.21, M1 2.45, MT 6.64 (best: MQ; descriptive per Amendment 1). μ̂ = +1.36, 90% CI [+1.08, +1.61] (Amendment-2 null: [+0.86, +1.84]). M1: q = 0.38, c0 − q = 0.51, τ0 = 0.79 d. Clock (S2): M1 CV × 10³ calendar 1.94 vs active-day 2.45.
Rejuvenation (S5) at 2026-04-14, 2026-04-20: straddling-pair M1 residual +0.012 (M1-simulated null -0.001 ± 0.011; p_lower 0.900).
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.66, 0.72, 0.78, 0.87, 0.85, 0.90, 0.92, 0.91, 0.87, 0.89, 0.91, 0.89, 0.90, 0.91, 0.86, 0.91.
Per-agent slopes: n = 13, median A_i +0.060, share > 0 0.62, Wilcoxon p (greater) 0.108.
Robustness of A (S3): chat +0.150; n16 +0.074; n64 +0.100; rarefied +0.104; calendar clock +0.093; p under a two-timescale isotropic null 0.005.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.42, r = 0.48, τ = 11.0 d, mean S = 0.529): co-primary 0.90 (pre-registered null), 0.48 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.026 ± 0.004 (n = 211).

Data: `data/processed/H20-content-aging/G38/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G38.pdf](figures/aging_G38.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 1 — A p = 0.002, A_c p = 0.002. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 1. G: –.

## Notes
- 2026-10-03: the lag-1 correlation rises over the first four days after kickoff (0.66 → 0.87) and is flat at ≈ 0.9 afterwards: a kickoff relaxation with τ_q ≈ 2 active days (interrupted aging), not slowing with age. MQ wins the LODO-CV by a factor 2–5. Day 1 carried the operator's Year-1 correction (NE36). NE17/NE18 cause no rejuvenation.
