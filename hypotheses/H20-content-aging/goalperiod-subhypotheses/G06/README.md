# H20 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** mixed (underpowered: not significant, μ = 0.5 aging not rejected) (Amendment-2 null; pre-registered null: supported)
**Role:** exploratory
**Period:** regime I · mode K · 4 agents with statements · #general only · 15 active days (60 agent-days with ≥ 8 statements).

## Why this period
A 15-day goal: an intermediate range of t_w. Secondary aging test; enters the random-effects summary (transfer within exploration). Competitive merch stores (mode K).

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.24 / 0.30 / 0.28 against μ = 0.5 aging, 0.61 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = +0.071 (p = 0.120), A_c = +0.063 (p = 0.202), A_g = +0.090 (p = 0.104), A_late = +0.040, K = +0.014; co-primary design power vs μ = 0.5: 0.20 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.014 | 0.391 | 0.415 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.071 | 0.020 | 0.120 | > 0 (P2, co-primary) |
| A_c common removed | +0.063 | 0.092 | 0.202 | > 0 (P2, co-primary) |
| A_g field removed | +0.090 | 0.008 | 0.104 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.040 | 0.365 | 0.397 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.061 | 0.228 | 0.297 | P7 input |
| A_m swarm mean | +0.092 | 0.014 | 0.100 | sign of A (P6) |
| A_m roster-stable | +0.092 | 0.014 | 0.100 | reported |
| β_wk weekend gap | +0.021 | 0.820 | 0.717 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **supported (aging)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 6.2/9.9; see the card): **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 15.31, M0b 15.27, MQ 21.25, M1 29.74, MT 17.59 (best: M0b; descriptive per Amendment 1). μ̂ = +1.38, 90% CI [+0.71, +2.08] (Amendment-2 null: [-0.12, +2.43]). M1: q = 0.45, c0 − q = 0.31, τ0 = 0.21 d. Clock (S2): M1 CV × 10³ calendar 78.97 vs active-day 29.74.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.83, 0.53, 0.63, 0.71, 0.64, 0.77, 0.74, 0.76, 0.70, 0.59, 0.68, 0.85, 0.78, 0.70.
Per-agent slopes: n = 4, median A_i +0.075, share > 0 1.00, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.083; n16 +0.019; n64 +0.049; rarefied +0.075; calendar clock +0.075; p under a two-timescale isotropic null 0.005.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.48, r = 0.33, τ = 2.4 d, mean S = 0.429): co-primary 0.38 (pre-registered null), 0.20 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.001 ± 0.006 (n = 60).

Data: `data/processed/H20-content-aging/G06/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G06.pdf](figures/aging_G06.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.120, A_c p = 0.202. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes
