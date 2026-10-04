# H20 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-11-28)

**Verdict:** failed (dynamics speed up with age, A < 0) (Amendment-2 null; pre-registered null: failed)
**Verdict (1b):** failed (both models, all configs)
**Role:** replication (exploratory)
**Period:** regime I · mode I · 10 agents with statements · #general only · 10 active days (92 agent-days with ≥ 8 statements).

## Why this period
A 10-day goal: an intermediate range of t_w. Secondary aging test; enters the random-effects summary (transfer within exploration).

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.29 / 0.22 / 0.30 against μ = 0.5 aging, 0.70 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = -0.214 (p = 0.982), A_c = -0.109 (p = 0.930), A_g = -0.226 (p = 0.992), A_late = -0.863, K = +0.192; co-primary design power vs μ = 0.5: 0.27 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.192 | < 0.002 | 0.046 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.214 | 1.000 | 0.982 | > 0 (P2, co-primary) |
| A_c common removed | -0.109 | 0.994 | 0.930 | > 0 (P2, co-primary) |
| A_g field removed | -0.226 | 1.000 | 0.992 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.863 | 1.000 | 0.994 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.365 | < 0.002 | 0.058 | P7 input |
| A_m swarm mean | -0.355 | 1.000 | 0.934 | sign of A (P6) |
| A_m roster-stable | -0.347 | 1.000 | 0.930 | reported |
| β_wk weekend gap | +0.064 | 0.942 | 0.766 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **failed (dynamics speed up with age, A < 0)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 4.5/9.2; see the card): **failed (dynamics speed up with age, A < 0)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 28.02, M0b 28.21, MQ 21.37, M1 19.90, MT 30.12 (best: M1; descriptive per Amendment 1). μ̂ = -1.46, 90% CI [-2.06, -1.01] (Amendment-2 null: [-3.00, -0.45]). M1: q = 0.19, c0 − q = 0.75, τ0 = 28 d. Clock (S2): M1 CV × 10³ calendar 25.91 vs active-day 19.90.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.42, 0.64, 0.83, 0.85, 0.76, 0.53, 0.82, 0.48, 0.30.
Per-agent slopes: n = 9, median A_i -0.182, share > 0 0.00, Wilcoxon p (greater) 1.000.
Robustness of A (S3): chat -0.179; n16 -0.122; n64 -0.164; rarefied -0.232; calendar clock -0.212; p under a two-timescale isotropic null 1.000.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.17, r = 0.74, τ = 2.4 d, mean S = 0.327): co-primary 0.75 (pre-registered null), 0.27 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.014 ± 0.006 (n = 92).

Data: `data/processed/H20-content-aging/G20/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G20.pdf](figures/aging_G20.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.982, A_c p = 0.930. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes
- 2026-10-03: the negative slope comes from the last two days (Thanksgiving 11-27/28): lag-1 C falls to 0.48 and 0.30. A holiday perturbation, not age-dependent speed-up.

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G20/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A -0.214 (p 0.982); A_c -0.109 (p 0.930); A_late -0.863; K +0.192; μ̂ -1.46 [-3.00, -0.45]; power 0.27 |
| gte-modernbert | A -0.197 (p 0.960); A_c -0.075 (p 0.880); A_late -0.995; K +0.134; μ̂ -1.58 [-3.00, -0.48]; power 0.33 |
| restatement-deduped (bge / gte) | A -0.213 / -0.194 |
| style-residualized (bge / gte) | A -0.177 / -0.152 |

A across the 7 configurations: -0.214 to -0.152. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
