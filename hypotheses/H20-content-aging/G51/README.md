# H20 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-18)

**Verdict:** failed (stationary within power: μ = 0.5 aging rejected) (Amendment-2 null; pre-registered null: mixed)
**Role:** exploratory
**Period:** regime III · mode I/K · 32 agents with statements · 4 rooms with agent statements · 45 active days (1080 agent-days with ≥ 8 statements). Step changes inside (kept in one unit; tested as rejuvenation, exception (c)): 2026-07-09, 2026-08-05, 2026-08-25, 2026-09-03. Holdout tail 09-07 → 09-18 excluded; non-holdout days 07-06 → 09-04 (d = 1–45).

## Why this period
One of the four long goals named in HH101 (t_w reaches 45 active days). Primary aging test. Private, stable individual roles (HH102: glassy); 21 → 32 agents (joins at 07-09/10, 07-17, 07-24/29, 08-28/31, 09-01, 09-03/04); the longest window. Joiners test the agent's own clock vs the kickoff clock.

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.42 / 0.48 / 0.48 against μ = 0.5 aging, 0.86 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ and the agent's own goal ĝ_i.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **#51:** high plateau q; aging present (credence 0.5). A_c is the better-powered statistic here (many agents). Joiners: A_i on the own-join clock vs the kickoff clock, descriptive. Rejuvenation at 07-09 / 08-05 / 08-25 / 09-03, descriptive.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = +0.012 (p = 0.078), A_c = +0.009 (p = 0.146), A_g = +0.014 (p = 0.060), A_late = +0.111, K = +0.060; co-primary design power vs μ = 0.5: 1.00 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.060 | < 0.002 | < 0.002 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.012 | 0.048 | 0.078 | > 0 (P2, co-primary) |
| A_c common removed | +0.009 | 0.124 | 0.146 | > 0 (P2, co-primary) |
| A_g field removed | +0.014 | 0.026 | 0.060 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.111 | < 0.002 | < 0.002 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.020 | 0.764 | 0.743 | P7 input |
| A_m swarm mean | +0.046 | 0.124 | 0.150 | sign of A (P6) |
| A_m roster-stable | +0.003 | 0.469 | 0.461 | reported |
| β_wk weekend gap | +0.006 | 0.940 | 0.926 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 9.4/25.2; see the card): **failed (stationary within power: μ = 0.5 aging rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 2.07, M0b 1.95, MQ 1.91, M1 2.00, MT 2.02 (best: MQ; descriptive per Amendment 1). μ̂ = +0.22, 90% CI [+0.08, +0.39] (Amendment-2 null: [+0.07, +0.41]). M1: q = 0.50, c0 − q = 0.34, τ0 = 4.5 d. Clock (S2): M1 CV × 10³ calendar 2.10 vs active-day 2.00.
Rejuvenation (S5) at 2026-07-09, 2026-08-05, 2026-08-25, 2026-09-03: straddling-pair M1 residual +0.007 (M1-simulated null -0.000 ± 0.008; p_lower 0.806).
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.83, 0.86, 0.85, 0.83, 0.84, 0.84, 0.86, 0.83, 0.84, 0.73, 0.82, 0.83, 0.79, 0.86, 0.86, 0.83, 0.79, 0.83, 0.81, 0.81, 0.78, 0.80, 0.77, 0.76, 0.83, 0.83, 0.74, 0.87, 0.88, 0.82, 0.86, 0.87, 0.87, 0.82, 0.88, 0.84, 0.88, 0.88, 0.83, 0.84, 0.88, 0.90, 0.90, 0.90.
Per-agent slopes: n = 27, median A_i +0.020, share > 0 0.59, Wilcoxon p (greater) 0.140.
Robustness of A (S3): chat -0.001; n16 +0.008; n64 +0.001; rarefied +0.012; calendar clock +0.010; p under a two-timescale isotropic null 0.045.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.50, r = 0.33, τ = 8.9 d, mean S = 0.356): co-primary 1.00 (pre-registered null), 1.00 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.007 ± 0.002 (n = 1189).
Joiners (S4, n = 6): median A_i on the kickoff clock +0.045, on their own clock -0.010.

Data: `data/processed/H20-content-aging/G51/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G51.pdf](figures/aging_G51.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.078, A_c p = 0.146. D (unfitted signature: A_late, μ̂ > 0): 1. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes
- 2026-10-03: aging of μ = 0.5 size is rejected; a weak late slowing remains (A_late +0.11, μ̂ 0.22 [0.07, 0.41]), carried by the intention stream (chat-only A ≈ 0). Joins and the #focus room cause no rejuvenation detectable at this resolution.
