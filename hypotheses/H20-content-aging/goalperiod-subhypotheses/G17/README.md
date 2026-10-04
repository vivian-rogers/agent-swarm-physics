# H20 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-17)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime I · mode I · 7 agents with statements · #general only · 5 active days (35 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.10 / 0.04 / 0.16 against μ = 0.5 aging, 0.20 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.10.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.172 (p = 0.208), A_c = +0.353 (p = 0.046), A_g = +0.219 (p = 0.178), A_late = -0.074, K = -0.033; co-primary design power vs μ = 0.5: 0.07 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.033 | 0.756 | 0.579 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.172 | 0.038 | 0.208 | > 0 (P2, co-primary) |
| A_c common removed | +0.353 | 0.004 | 0.046 | > 0 (P2, co-primary) |
| A_g field removed | +0.219 | 0.030 | 0.178 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.074 | 0.621 | 0.573 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.172 | 0.038 | 0.208 | P7 input |
| A_m swarm mean | +0.005 | 0.457 | 0.491 | sign of A (P6) |
| A_m roster-stable | +0.005 | 0.457 | 0.491 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.8/9.1; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.67, 0.57, 0.66, 0.63.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.135; n16 +0.218; n64 +0.299; rarefied +0.184; calendar clock +0.172.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.47, r = 0.52, τ = 0.4 d, mean S = 0.362): co-primary 0.12 (pre-registered null), 0.07 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.019 ± 0.015 (n = 35).

Data: `data/processed/H20-content-aging/G17/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G17.pdf](figures/aging_G17.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G17/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A +0.172 (p 0.208); A_c +0.353 (p 0.046); A_late -0.074; K -0.033; power 0.07 |
| gte-modernbert | A +0.095 (p 0.281); A_c +0.258 (p 0.100); A_late -0.032; K -0.014; power 0.13 |
| restatement-deduped (bge / gte) | A +0.055 / -0.051 |
| style-residualized (bge / gte) | A +0.138 / +0.063 |

A across the 7 configurations: -0.051 to +0.172. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
