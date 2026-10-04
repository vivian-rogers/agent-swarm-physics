# H20 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-05)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime I · mode M · 7 agents with statements · #general only · 5 active days (35 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.12 / 0.15 / 0.13 against μ = 0.5 aging, 0.23 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.12.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = -0.834 (p = 1.000), A_c = -0.552 (p = 1.000), A_g = -0.650 (p = 1.000), A_late = -1.844, K = -0.081; co-primary design power vs μ = 0.5: 0.12 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.081 | 1.000 | 0.924 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.834 | 1.000 | 1.000 | > 0 (P2, co-primary) |
| A_c common removed | -0.552 | 1.000 | 1.000 | > 0 (P2, co-primary) |
| A_g field removed | -0.650 | 1.000 | 1.000 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -1.844 | 1.000 | 1.000 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.834 | 1.000 | 1.000 | P7 input |
| A_m swarm mean | -1.212 | 1.000 | 0.990 | sign of A (P6) |
| A_m roster-stable | -1.212 | 1.000 | 0.990 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 1.7/5.3; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.81, 0.82, 0.83, 0.29.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat -0.856; n16 -0.885; n64 -0.706; rarefied -0.833; calendar clock -0.834.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.00, r = 0.99, τ = 10.6 d, mean S = 0.292): co-primary 0.39 (pre-registered null), 0.12 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.006 ± 0.013 (n = 35).

Data: `data/processed/H20-content-aging/G12/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G12.pdf](figures/aging_G12.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
- 2026-10-03: the most extreme outlier (A = −0.83); the debate week is structured by day (debate, then judging), so its content is phased, not stationary.

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G12/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A -0.834 (p 1.000); A_c -0.552 (p 1.000); A_late -1.844; K -0.081; power 0.12 |
| gte-modernbert | A -0.769 (p 0.998); A_c -0.617 (p 1.000); A_late -1.705; K -0.088; power 0.09 |
| restatement-deduped (bge / gte) | A -0.765 / -0.732 |
| style-residualized (bge / gte) | A -0.878 / -0.744 |

A across the 7 configurations: -0.878 to -0.732. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
