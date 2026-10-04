# H20 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-19)

**Verdict:** mixed (underpowered: not significant, μ = 0.5 aging not rejected) (Amendment-2 null; pre-registered null: mixed)
**Role:** exploratory
**Period:** regime I · mode C · 6 agents with statements · #general only · 10 active days (60 agent-days with ≥ 8 statements).

## Why this period
A 10-day goal: an intermediate range of t_w. Secondary aging test; enters the random-effects summary (transfer within exploration).

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.26 / 0.19 / 0.19 against μ = 0.5 aging, 0.64 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = -0.002 (p = 0.473), A_c = +0.040 (p = 0.208), A_g = +0.008 (p = 0.437), A_late = -0.825, K = -0.047; co-primary design power vs μ = 0.5: 0.19 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.047 | 0.870 | 0.725 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.002 | 0.473 | 0.473 | > 0 (P2, co-primary) |
| A_c common removed | +0.040 | 0.088 | 0.208 | > 0 (P2, co-primary) |
| A_g field removed | +0.008 | 0.419 | 0.437 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.825 | 1.000 | 0.996 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.002 | 0.523 | 0.505 | P7 input |
| A_m swarm mean | -0.046 | 0.687 | 0.613 | sign of A (P6) |
| A_m roster-stable | -0.046 | 0.687 | 0.613 | reported |
| β_wk weekend gap | +0.094 | 1.000 | 0.966 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 3.8/10.4; see the card): **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 14.50, M0b 14.54, MQ 17.00, M1 20.30, MT 16.35 (best: M0; descriptive per Amendment 1). μ̂ = -0.13, 90% CI [-0.72, +0.48] (Amendment-2 null: [-2.75, +1.59]). M1: q = 0.50, c0 − q = 0.40, τ0 = 1.7 d. Clock (S2): M1 CV × 10³ calendar 23.27 vs active-day 20.30.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.71, 0.76, 0.49, 0.71, 0.77, 0.81, 0.77, 0.79, 0.44.
Per-agent slopes: n = 6, median A_i -0.057, share > 0 0.33, Wilcoxon p (greater) 0.781.
Robustness of A (S3): chat +0.008; n16 +0.032; n64 +0.067; rarefied -0.015; calendar clock -0.018; p under a two-timescale isotropic null 0.662.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.50, r = 0.41, τ = 1.4 d, mean S = 0.354): co-primary 0.45 (pre-registered null), 0.19 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.002 ± 0.007 (n = 60).

Data: `data/processed/H20-content-aging/G13/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G13.pdf](figures/aging_G13.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.473, A_c p = 0.208. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes
