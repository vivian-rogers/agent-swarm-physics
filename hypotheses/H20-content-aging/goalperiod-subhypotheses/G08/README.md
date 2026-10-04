# H20 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-12)

**Verdict:** mixed (underpowered: not significant, μ = 0.5 aging not rejected) (Amendment-2 null; pre-registered null: mixed)
**Role:** exploratory
**Period:** regime I · mode C · 4 agents with statements · #general only · 18 active days (72 agent-days with ≥ 8 statements).

## Why this period
One of the four long goals named in HH101 (t_w reaches 18 active days). Primary aging test. Four agents designing a benchmark; o3, Opus 4 and 3.7 Sonnet wrote near-identical frameworks independently (a shared field).

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.26 / 0.23 / 0.39 against μ = 0.5 aging, 0.67 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = -0.001 (p = 0.511), A_c = +0.080 (p = 0.110), A_g = -0.008 (p = 0.571), A_late = -0.177, K = +0.092; co-primary design power vs μ = 0.5: 0.20 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.092 | 0.038 | 0.152 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.001 | 0.521 | 0.511 | > 0 (P2, co-primary) |
| A_c common removed | +0.080 | 0.020 | 0.110 | > 0 (P2, co-primary) |
| A_g field removed | -0.008 | 0.577 | 0.571 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.177 | 0.964 | 0.846 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.088 | 0.196 | 0.297 | P7 input |
| A_m swarm mean | +0.017 | 0.377 | 0.435 | sign of A (P6) |
| A_m roster-stable | +0.017 | 0.377 | 0.435 | reported |
| β_wk weekend gap | -0.040 | 0.036 | 0.150 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **mixed (interrupted aging: no late slowing)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 6.0/10.8; see the card): **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 14.85, M0b 14.82, MQ 14.63, M1 15.27, MT 15.82 (best: MQ; descriptive per Amendment 1). μ̂ = -0.30, 90% CI [-0.87, +0.21] (Amendment-2 null: [-1.80, +0.56]). M1: q = 0.40, c0 − q = 0.48, τ0 = 3.3 d. Clock (S2): M1 CV × 10³ calendar 15.09 vs active-day 15.27.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.58, 0.69, 0.75, 0.80, 0.82, 0.40, 0.54, 0.79, 0.64, 0.61, 0.80, 0.79, 0.52, 0.67, 0.58, 0.59, 0.68.
Per-agent slopes: n = 4, median A_i -0.008, share > 0 0.50, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.009; n16 -0.024; n64 +0.015; rarefied -0.008; calendar clock -0.002; p under a two-timescale isotropic null 0.517.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.39, r = 0.45, τ = 1.9 d, mean S = 0.360): co-primary 0.38 (pre-registered null), 0.20 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.023 ± 0.007 (n = 72).

Data: `data/processed/H20-content-aging/G08/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G08.pdf](figures/aging_G08.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.511, A_c p = 0.110. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes
