# H20 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-14)

**Verdict:** mixed (underpowered: not significant, μ = 0.5 aging not rejected) (Amendment-2 null; pre-registered null: failed)
**Verdict (1b):** mixed (both models, all configs)
**Role:** exploratory
**Period:** regime I · mode C · 8 agents with statements · #general only · 10 active days (71 agent-days with ≥ 8 statements).

## Why this period
A 10-day goal: an intermediate range of t_w. Secondary aging test; enters the random-effects summary (transfer within exploration).

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.38 / 0.29 / 0.36 against μ = 0.5 aging, 0.75 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = -0.060 (p = 0.661), A_c = -0.087 (p = 0.916), A_g = -0.055 (p = 0.683), A_late = -0.001, K = -0.092; co-primary design power vs μ = 0.5: 0.12 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.092 | 0.890 | 0.743 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.060 | 0.854 | 0.661 | > 0 (P2, co-primary) |
| A_c common removed | -0.087 | 0.982 | 0.916 | > 0 (P2, co-primary) |
| A_g field removed | -0.055 | 0.854 | 0.683 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.001 | 0.479 | 0.457 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.119 | 0.820 | 0.673 | P7 input |
| A_m swarm mean | -0.026 | 0.605 | 0.497 | sign of A (P6) |
| A_m roster-stable | -0.031 | 0.643 | 0.511 | reported |
| β_wk weekend gap | -0.114 | 0.014 | 0.104 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **failed (stationary within power: μ = 0.5 aging rejected)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 5.5/11.4; see the card): **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 9.22, M0b 8.64, MQ 8.33, M1 8.41, MT 10.14 (best: MQ; descriptive per Amendment 1). μ̂ = -0.43, 90% CI [-2.04, +0.30] (Amendment-2 null: [-3.00, +1.98]). M1: q = 0.34, c0 − q = 1.02, τ0 = 1.4 d. Clock (S2): M1 CV × 10³ calendar 6.72 vs active-day 8.41.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.60, 0.67, 0.67, 0.59, 0.45, 0.56, 0.50, 0.62, 0.47.
Per-agent slopes: n = 7, median A_i -0.069, share > 0 0.14, Wilcoxon p (greater) 0.992.
Robustness of A (S3): chat -0.060; n16 -0.087; n64 +0.055; rarefied -0.071; calendar clock -0.054; p under a two-timescale isotropic null 1.000.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.34, r = 0.65, τ = 0.7 d, mean S = 0.279): co-primary 0.30 (pre-registered null), 0.12 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.028 ± 0.008 (n = 71).

Data: `data/processed/H20-content-aging/G19/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G19.pdf](figures/aging_G19.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.661, A_c p = 0.916. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G19/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A -0.060 (p 0.661); A_c -0.087 (p 0.916); A_late -0.001; K -0.092; μ̂ -0.43 [-3.00, +1.98]; power 0.12 |
| gte-modernbert | A +0.021 (p 0.433); A_c -0.035 (p 0.689); A_late +0.067; K -0.121; μ̂ -0.06 [-3.00, +2.51]; power 0.13 |
| restatement-deduped (bge / gte) | A -0.047 / +0.050 |
| style-residualized (bge / gte) | A -0.097 / -0.009 |

A across the 7 configurations: -0.097 to +0.050. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
