# H20 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-02)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime I · mode C · 10 agents with statements · #general only · 5 active days (49 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.12 / 0.09 / 0.11 against μ = 0.5 aging, 0.21 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.12.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.330 (p = 0.018), A_c = +0.148 (p = 0.002), A_g = +0.216 (p = 0.024), A_late = +0.281, K = -0.099; co-primary design power vs μ = 0.5: 0.13 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.099 | 1.000 | 0.940 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.330 | < 0.002 | 0.018 | > 0 (P2, co-primary) |
| A_c common removed | +0.148 | < 0.002 | < 0.002 | > 0 (P2, co-primary) |
| A_g field removed | +0.216 | < 0.002 | 0.024 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.281 | < 0.002 | 0.066 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.330 | < 0.002 | 0.018 | P7 input |
| A_m swarm mean | +0.397 | < 0.002 | 0.046 | sign of A (P6) |
| A_m roster-stable | +0.397 | < 0.002 | 0.046 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.3/9.5; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.78, 0.71, 0.81, 0.89.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.306; n16 +0.306; n64 +0.434; rarefied +0.339; calendar clock +0.330.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.00, r = 0.99, τ = 18.4 d, mean S = 0.352): co-primary 0.20 (pre-registered null), 0.13 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.019 ± 0.009 (n = 49).

Data: `data/processed/H20-content-aging/G25/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G25.pdf](figures/aging_G25.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G25/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A +0.330 (p 0.018); A_c +0.148 (p 0.002); A_late +0.281; K -0.099; power 0.13 |
| gte-modernbert | A +0.515 (p 0.030); A_c +0.189 (p 0.002); A_late +0.207; K -0.173; power 0.14 |
| restatement-deduped (bge / gte) | A +0.302 / +0.460 |
| style-residualized (bge / gte) | A +0.223 / +0.353 |

A across the 7 configurations: +0.223 to +0.515. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
