# H20 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-26)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Verdict (1b):** descriptive (both models)
**Role:** exploratory
**Period:** regime I · mode C · 10 agents with statements · #general only · 5 active days (50 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.16 / 0.09 / 0.22 against μ = 0.5 aging, 0.25 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.16.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = -0.600 (p = 1.000), A_c = -0.623 (p = 1.000), A_g = -0.577 (p = 1.000), A_late = -1.507, K = -0.076; co-primary design power vs μ = 0.5: 0.17 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.076 | 1.000 | 0.962 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.600 | 1.000 | 1.000 | > 0 (P2, co-primary) |
| A_c common removed | -0.623 | 1.000 | 1.000 | > 0 (P2, co-primary) |
| A_g field removed | -0.577 | 1.000 | 1.000 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -1.507 | 1.000 | 1.000 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.600 | 1.000 | 1.000 | P7 input |
| A_m swarm mean | -0.604 | 1.000 | 0.980 | sign of A (P6) |
| A_m roster-stable | -0.604 | 1.000 | 0.980 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.2/10.1; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.90, 0.85, 0.87, 0.44.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat -0.494; n16 -0.519; n64 -0.498; rarefied -0.545; calendar clock -0.600.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.00, r = 0.99, τ = 14.5 d, mean S = 0.387): co-primary 0.33 (pre-registered null), 0.17 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.004 ± 0.006 (n = 50).

Data: `data/processed/H20-content-aging/G24/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G24.pdf](figures/aging_G24.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
- 2026-10-03: Christmas Day (12-25) breaks the last pair (lag-1 C 0.44 vs ≈ 0.87 before).

## Round 1b (improved data, 2026-10-04): replication
*Inputs: shared goal fields, gte-modernbert (DQ5), DQ5 dedupe (copies, restatements), style-residualized vectors. Data: `data/processed/H20-content-aging/G24/r1b/result_aniso_<config>.json`. Role of this row: replication.*

| Input | Statistics (Amendment-2 null) |
| --- | --- |
| round 1 (bge, H01-derived goal vectors) | see Result above |
| bge-small, shared goal fields | A -0.600 (p 1.000); A_c -0.623 (p 1.000); A_late -1.507; K -0.076; power 0.17 |
| gte-modernbert | A -0.574 (p 0.992); A_c -0.601 (p 1.000); A_late -1.378; K -0.056; power 0.13 |
| restatement-deduped (bge / gte) | A -0.607 / -0.586 |
| style-residualized (bge / gte) | A -0.460 / -0.415 |

A across the 7 configurations: -0.607 to -0.415. The shared goal fields give the same ĝ as round 1 (cos 1.0000 at n = 32: H20 averaged the room kickoffs, so H01's #38 room swap cancels), so bge numbers reproduce exactly.
