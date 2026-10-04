# H20 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime III · mode I · 15 agents with statements · 2 rooms with agent statements · 5 active days (73 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.08 / 0.07 / 0.12 against μ = 0.5 aging, 0.17 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.08.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = -0.035 (p = 0.754), A_c = -0.048 (p = 0.806), A_g = -0.045 (p = 0.852), A_late = +0.010, K = +0.039; co-primary design power vs μ = 0.5: 0.24 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.039 | 0.010 | 0.064 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.035 | 0.872 | 0.754 | > 0 (P2, co-primary) |
| A_c common removed | -0.048 | 0.914 | 0.806 | > 0 (P2, co-primary) |
| A_g field removed | -0.045 | 0.952 | 0.852 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.010 | 0.433 | 0.447 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.035 | 0.872 | 0.754 | P7 input |
| A_m swarm mean | -0.010 | 0.517 | 0.523 | sign of A (P6) |
| A_m roster-stable | -0.011 | 0.553 | 0.553 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.9/11.7; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.83, 0.86, 0.84, 0.85.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat -0.077; n16 -0.037; n64 +0.020; rarefied -0.022; calendar clock -0.035.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.66, r = 0.29, τ = 2.2 d, mean S = 0.531): co-primary 0.41 (pre-registered null), 0.24 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.049 ± 0.009 (n = 74).

Data: `data/processed/H20-content-aging/G39/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G39.pdf](figures/aging_G39.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G39/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A -0.035 (p 0.754); A_c -0.048 (p 0.806); A_late +0.010; K +0.039; power 0.24 |
| gte-modernbert | A -0.033 (p 0.741); A_c -0.006 (p 0.517); A_late -0.027; K +0.011; power 0.22 |
| restatement-deduped (bge / gte) | A -0.072 / -0.047 |
| style-residualized (bge / gte) | A -0.046 / +0.002 |

A across the 7 configurations: -0.072 to +0.002. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
