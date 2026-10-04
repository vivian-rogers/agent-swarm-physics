# H20 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-22)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime I · mode I · 7 agents with statements · #general only · 5 active days (35 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.10 / 0.14 / 0.12 against μ = 0.5 aging, 0.18 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.10.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.103 (p = 0.072), A_c = +0.166 (p = 0.006), A_g = +0.123 (p = 0.030), A_late = -0.207, K = -0.000; co-primary design power vs μ = 0.5: 0.13 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.000 | 0.527 | 0.519 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.103 | < 0.002 | 0.072 | > 0 (P2, co-primary) |
| A_c common removed | +0.166 | < 0.002 | 0.006 | > 0 (P2, co-primary) |
| A_g field removed | +0.123 | < 0.002 | 0.030 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.207 | 1.000 | 0.946 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.103 | < 0.002 | 0.072 | P7 input |
| A_m swarm mean | +0.015 | 0.381 | 0.363 | sign of A (P6) |
| A_m roster-stable | +0.015 | 0.381 | 0.363 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.6/7.5; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.77, 0.82, 0.93, 0.87.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.041; n16 +0.118; n64 +0.118; rarefied +0.071; calendar clock +0.103.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.00, r = 0.99, τ = 16.7 d, mean S = 0.538): co-primary 0.29 (pre-registered null), 0.13 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.009 ± 0.019 (n = 35).

Data: `data/processed/H20-content-aging/G10/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G10.pdf](figures/aging_G10.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G10/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A +0.103 (p 0.072); A_c +0.166 (p 0.006); A_late -0.207; K -0.000; power 0.13 |
| gte-modernbert | A +0.093 (p 0.054); A_c +0.172 (p 0.002); A_late -0.241; K +0.037; power 0.13 |
| restatement-deduped (bge / gte) | A +0.115 / +0.103 |
| style-residualized (bge / gte) | A +0.100 / +0.086 |

A across the 7 configurations: +0.086 to +0.115. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
