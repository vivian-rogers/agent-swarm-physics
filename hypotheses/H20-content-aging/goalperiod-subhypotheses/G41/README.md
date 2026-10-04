# H20 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime III · mode I · 15 agents with statements · 2 rooms with agent statements · 5 active days (74 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.08 / 0.10 / 0.09 against μ = 0.5 aging, 0.17 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.08.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.240 (p = 0.034), A_c = +0.205 (p = 0.010), A_g = +0.246 (p = 0.036), A_late = +0.126, K = -0.044; co-primary design power vs μ = 0.5: 0.14 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.044 | 0.952 | 0.750 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.240 | < 0.002 | 0.034 | > 0 (P2, co-primary) |
| A_c common removed | +0.205 | < 0.002 | 0.010 | > 0 (P2, co-primary) |
| A_g field removed | +0.246 | < 0.002 | 0.036 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.126 | 0.106 | 0.228 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.240 | < 0.002 | 0.034 | P7 input |
| A_m swarm mean | +0.206 | 0.042 | 0.190 | sign of A (P6) |
| A_m roster-stable | +0.206 | 0.042 | 0.190 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.0/8.5; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.82, 0.71, 0.83, 0.86.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.527; n16 +0.273; n64 +0.233; rarefied +0.225; calendar clock +0.240.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.37, r = 0.62, τ = 2.7 d, mean S = 0.395): co-primary 0.47 (pre-registered null), 0.14 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.018 ± 0.010 (n = 75).

Data: `data/processed/H20-content-aging/G41/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G41.pdf](figures/aging_G41.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G41/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A +0.240 (p 0.034); A_c +0.205 (p 0.010); A_late +0.126; K -0.044; power 0.14 |
| gte-modernbert | A +0.290 (p 0.006); A_c +0.262 (p 0.002); A_late -0.025; K -0.085; power 0.18 |
| restatement-deduped (bge / gte) | A +0.346 / +0.379 |
| style-residualized (bge / gte) | A +0.190 / +0.220 |

A across the 7 configurations: +0.190 to +0.379. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
