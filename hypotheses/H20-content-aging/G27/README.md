# H20 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-23)

**Verdict:** mixed (underpowered: not significant, μ = 0.5 aging not rejected) (Amendment-2 null; pre-registered null: mixed)
**Role:** exploratory
**Period:** regime I · mode K · 10 agents with statements · #general only · 10 active days (100 agent-days with ≥ 8 statements).

## Why this period
A 10-day goal: an intermediate range of t_w. Secondary aging test; enters the random-effects summary (transfer within exploration).

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.31 / 0.21 / 0.31 against μ = 0.5 aging, 0.70 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = -0.002 (p = 0.511), A_c = -0.099 (p = 0.964), A_g = +0.006 (p = 0.425), A_late = +0.104, K = +0.049; co-primary design power vs μ = 0.5: 0.15 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.049 | 0.044 | 0.164 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.002 | 0.557 | 0.511 | > 0 (P2, co-primary) |
| A_c common removed | -0.099 | 0.998 | 0.964 | > 0 (P2, co-primary) |
| A_g field removed | +0.006 | 0.409 | 0.425 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.104 | 0.156 | 0.232 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.063 | 0.136 | 0.281 | P7 input |
| A_m swarm mean | +0.052 | 0.020 | 0.156 | sign of A (P6) |
| A_m roster-stable | +0.052 | 0.020 | 0.156 | reported |
| β_wk weekend gap | -0.037 | 0.006 | 0.114 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 4.2/9.8; see the card): **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 3.94, M0b 4.02, MQ 3.92, M1 3.97, MT 4.71 (best: MQ; descriptive per Amendment 1). μ̂ = -0.14, 90% CI [-3.00, +3.00] (Amendment-2 null: [-3.00, +3.00]). M1: q = 0.76, c0 − q = 0.72, τ0 = 0.56 d. Clock (S2): M1 CV × 10³ calendar 3.67 vs active-day 3.97.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.82, 0.85, 0.84, 0.88, 0.73, 0.87, 0.86, 0.80, 0.82.
Per-agent slopes: n = 10, median A_i +0.032, share > 0 0.70, Wilcoxon p (greater) 0.423.
Robustness of A (S3): chat +0.054; n16 -0.023; n64 -0.012; rarefied -0.005; calendar clock -0.016; p under a two-timescale isotropic null 0.567.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.76, r = 0.23, τ = 0.4 d, mean S = 0.383): co-primary 0.16 (pre-registered null), 0.15 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.013 ± 0.006 (n = 100).

Data: `data/processed/H20-content-aging/G27/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G27.pdf](figures/aging_G27.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.511, A_c p = 0.964. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes
