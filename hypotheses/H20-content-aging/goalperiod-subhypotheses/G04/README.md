# H20 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** mixed (underpowered: not significant, μ = 0.5 aging not rejected) (Amendment-2 null; pre-registered null: mixed)
**Verdict (1b):** mixed (both models, all configs)
**Role:** replication (exploratory)
**Period:** regime I · mode C · 6 agents with statements · #general only · 25 active days (99 agent-days with ≥ 8 statements). Roster swap inside (o4-mini one day; GPT-4.1 out, Claude Opus 4 in); start time moved 05-23.

## Why this period
One of the four long goals named in HH101 (t_w reaches 25 active days). Primary aging test. Shared objective (write a story, hold an event): a long project with phases (writing → event planning).

## Prediction
*Written 2026-10-03, before running on this period (card predictions with Amendment 1).* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.31 / 0.22 / 0.29 against μ = 0.5 aging, 0.73 against μ = 1 (a² = 0.15). 
- **P1:** K > 0 (kickoff transient).
- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, weekend covariate). The original rule (A at p < 0.05) is reported too.
- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ.
- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).
- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.
- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.
- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).

## Result
A = +0.021 (p = 0.385), A_c = +0.052 (p = 0.240), A_g = +0.014 (p = 0.401), A_late = +0.028, K = -0.078; co-primary design power vs μ = 0.5: 0.11 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.078 | 0.892 | 0.764 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.021 | 0.315 | 0.385 | > 0 (P2, co-primary) |
| A_c common removed | +0.052 | 0.118 | 0.240 | > 0 (P2, co-primary) |
| A_g field removed | +0.014 | 0.345 | 0.401 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.028 | 0.433 | 0.413 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.097 | 0.353 | 0.415 | P7 input |
| A_m swarm mean | -0.018 | 0.699 | 0.595 | sign of A (P6) |
| A_m roster-stable | -0.018 | 0.649 | 0.555 | reported |
| β_wk weekend gap | -0.041 | 0.030 | 0.120 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 7.1/10.3; see the card): **mixed (underpowered: not significant, μ = 0.5 aging not rejected)**.
Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — M0 20.90, M0b 20.82, MQ 20.69, M1 21.37, MT 22.49 (best: MQ; descriptive per Amendment 1). μ̂ = +0.30, 90% CI [-0.33, +0.93] (Amendment-2 null: [-1.17, +1.58]). M1: q = 0.28, c0 − q = 0.42, τ0 = 2 d. Clock (S2): M1 CV × 10³ calendar 21.25 vs active-day 21.37.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.63, 0.58, 0.68, 0.73, 0.47, 0.66, 0.42, 0.60, 0.55, 0.56, 0.60, 0.49, 0.77, 0.85, 0.76, 0.59, 0.77, 0.65, 0.71, 0.75, 0.50, 0.48, 0.69, 0.71.
Per-agent slopes: n = 4, median A_i +0.033, share > 0 0.75, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.024; n16 -0.000; n64 +0.020; rarefied +0.023; calendar clock +0.016; p under a two-timescale isotropic null 0.289.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.28, r = 0.42, τ = 4.0 d, mean S = 0.285): co-primary 0.35 (pre-registered null), 0.11 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.004 ± 0.006 (n = 100).

Data: `data/processed/H20-content-aging/G04/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G04.pdf](figures/aging_G04.pdf).

## Scorecard (period-specific axes)
C (beats the stationary null): 0 — A p = 0.385, A_c p = 0.240. D (unfitted signature: A_late, μ̂ > 0): 0. H (rivals R1 quench, R2 field, R3 common): 0. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G04/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A +0.021 (p 0.385); A_c +0.052 (p 0.240); A_late +0.028; K -0.078; μ̂ +0.30 [-1.17, +1.58]; power 0.11 |
| gte-modernbert | A +0.056 (p 0.222); A_c +0.044 (p 0.279); A_late +0.058; K -0.187; μ̂ +0.71 [-0.80, +2.03]; power 0.12 |
| restatement-deduped (bge / gte) | A +0.010 / +0.045 |
| style-residualized (bge / gte) | A +0.020 / +0.056 |

A across the 7 configurations: +0.010 to +0.056. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
