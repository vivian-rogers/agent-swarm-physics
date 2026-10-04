# H20 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime II · mode C · 12 agents with statements · 3 rooms with agent statements · 5 active days (60 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.12 / 0.12 / 0.14 against μ = 0.5 aging, 0.29 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.12.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.136 (p = 0.309), A_c = +0.200 (p = 0.070), A_g = +0.132 (p = 0.299), A_late = +0.236, K = -0.158; co-primary design power vs μ = 0.5: 0.06 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.158 | 0.998 | 0.872 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.136 | 0.134 | 0.309 | > 0 (P2, co-primary) |
| A_c common removed | +0.200 | 0.014 | 0.070 | > 0 (P2, co-primary) |
| A_g field removed | +0.132 | 0.138 | 0.299 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.236 | 0.204 | 0.343 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.136 | 0.134 | 0.309 | P7 input |
| A_m swarm mean | +0.066 | 0.383 | 0.465 | sign of A (P6) |
| A_m roster-stable | +0.066 | 0.383 | 0.465 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 3.6/9.0; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.63, 0.47, 0.52, 0.58.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.168; n16 +0.187; n64 +0.025; rarefied +0.168; calendar clock +0.136.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.29, r = 0.42, τ = 1.6 d, mean S = 0.161): co-primary 0.10 (pre-registered null), 0.06 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.018 ± 0.006 (n = 60).

Data: `data/processed/H20-content-aging/G35/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G35.pdf](figures/aging_G35.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G35/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A +0.136 (p 0.309); A_c +0.200 (p 0.070); A_late +0.236; K -0.158; power 0.06 |
| gte-modernbert | A +0.143 (p 0.299); A_c +0.227 (p 0.040); A_late +0.295; K -0.146; power 0.06 |
| restatement-deduped (bge / gte) | A +0.129 / +0.120 |
| style-residualized (bge / gte) | A +0.131 / +0.148 |

A across the 7 configurations: +0.120 to +0.148. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
