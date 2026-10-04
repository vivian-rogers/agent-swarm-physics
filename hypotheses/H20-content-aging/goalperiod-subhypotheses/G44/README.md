# H20 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** replication (exploratory)
**Period:** regime III · mode C · 18 agents with statements · 2 rooms with agent statements · 4 active days (63 agent-days with ≥ 8 statements).

## Why this period
A 4-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.09 / 0.08 / 0.12 against μ = 0.5 aging, 0.14 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.09.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.081 (p = 0.253), A_c = +0.081 (p = 0.224), A_g = +0.075 (p = 0.295), A_late = +nan, K = -0.021; co-primary design power vs μ = 0.5: 0.07 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.021 | 0.768 | 0.613 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.081 | 0.098 | 0.253 | > 0 (P2, co-primary) |
| A_c common removed | +0.081 | 0.114 | 0.224 | > 0 (P2, co-primary) |
| A_g field removed | +0.075 | 0.194 | 0.295 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | – | – | – | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.081 | 0.098 | 0.253 | P7 input |
| A_m swarm mean | +0.139 | 0.341 | 0.373 | sign of A (P6) |
| A_m roster-stable | +0.138 | 0.251 | 0.325 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.3/10.2; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.78, 0.82, 0.85.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.240; n16 +0.057; n64 +0.083; rarefied +0.042; calendar clock +0.081.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.18, r = 0.81, τ = 4.2 d, mean S = 0.359): co-primary 0.23 (pre-registered null), 0.07 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.015 ± 0.011 (n = 65).

Data: `data/processed/H20-content-aging/G44/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G44.pdf](figures/aging_G44.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G44/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A +0.081 (p 0.253); A_c +0.081 (p 0.224); A_late +nan; K -0.021; power 0.07 |
| gte-modernbert | A -0.000 (p 0.493); A_c -0.003 (p 0.603); A_late +nan; K -0.012; power 0.07 |
| restatement-deduped (bge / gte) | A +0.209 / +0.097 |
| style-residualized (bge / gte) | A +0.017 / -0.086 |

A across the 7 configurations: -0.086 to +0.209. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
