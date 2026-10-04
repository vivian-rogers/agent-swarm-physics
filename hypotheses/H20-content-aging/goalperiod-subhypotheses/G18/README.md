# H20 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** mixed (underpowered: not significant, μ = 0.5 aging not rejected) (Amendment-2 null; pre-registered null: mixed)
**Verdict (1b):** mixed (both models, all configs)
**Role:** replication (exploratory)
**Period:** regime I · mode C · 8 agents with statements · #general only · 10 active days (74 agent-days with ≥ 8 statements).

## Why this period
A 10-day goal: an intermediate range of t_w. Secondary aging test; enters the random-effects summary (transfer within exploration).

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.23 / 0.19 / 0.28 against μ = 0.5 aging, 0.59 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = -0.038 (p = 0.611), A_c = -0.118 (p = 0.928), A_g = -0.029 (p = 0.579), A_late = +0.784, K = -0.003; co-primary design power vs μ = 0.5: 0.18 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.003 | 0.467 | 0.475 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.038 | 0.723 | 0.611 | > 0 (P2, co-primary) |
| A_c common removed | -0.118 | 0.994 | 0.928 | > 0 (P2, co-primary) |
| A_g field removed | -0.029 | 0.687 | 0.579 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.784 | 0.004 | 0.084 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.433 | 0.008 | 0.088 | P7 input |
| A_m swarm mean | -0.012 | 0.573 | 0.521 | sign of A (P6) |
| A_m roster-stable | -0.049 | 0.687 | 0.589 | reported |
| β_wk weekend gap | -0.045 | 0.208 | 0.317 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 4.9/10.3; see the card): **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 16.84, M0b 16.46, MQ 20.02, M1 18.64, MT 17.37 (best: M0b; descriptive per Amendment 1). μ̂ = -0.05, 90% CI [-0.96, +0.68] (Amendment-2 null: [-3.00, +2.12]). M1: q = 0.25, c0 − q = 0.96, τ0 = 0.9 d. Clock (S2): M1 CV × 10³ calendar 22.57 vs active-day 18.64.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.64, 0.57, 0.43, 0.81, 0.46, 0.24, 0.56, 0.66, 0.58.
Per-agent slopes: n = 8, median A_i -0.077, share > 0 0.25, Wilcoxon p (greater) 0.945.
Robustness of A (S3): chat -0.017; n16 -0.004; n64 -0.016; rarefied -0.057; calendar clock -0.046; p under a two-timescale isotropic null 0.771.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.25, r = 0.74, τ = 0.8 d, mean S = 0.290): co-primary 0.29 (pre-registered null), 0.18 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.004 ± 0.008 (n = 75).

Data: `data/processed/H20-content-aging/G18/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G18.pdf](figures/aging_G18.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.611, A_c p = 0.928. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G18/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A -0.038 (p 0.611); A_c -0.118 (p 0.928); A_late +0.784; K -0.003; μ̂ -0.05 [-3.00, +2.12]; power 0.18 |
| gte-modernbert | A -0.003 (p 0.547); A_c -0.077 (p 0.880); A_late +0.242; K -0.065; μ̂ -0.01 [-2.92, +1.95]; power 0.15 |
| restatement-deduped (bge / gte) | A -0.055 / -0.021 |
| style-residualized (bge / gte) | A -0.053 / -0.009 |

A across the 7 configurations: -0.055 to -0.003. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
