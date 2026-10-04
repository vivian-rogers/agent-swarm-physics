# H20 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-25)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime I · mode F · 4 agents with statements · #general only · 5 active days (20 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.04 / 0.07 / 0.07 against μ = 0.5 aging, 0.06 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.04.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.357 (p = 0.287), A_c = +0.420 (p = 0.323), A_g = +0.385 (p = 0.297), A_late = +0.474, K = +0.214; co-primary design power vs μ = 0.5: 0.08 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.214 | 0.004 | 0.106 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.357 | 0.146 | 0.287 | > 0 (P2, co-primary) |
| A_c common removed | +0.420 | 0.200 | 0.323 | > 0 (P2, co-primary) |
| A_g field removed | +0.385 | 0.128 | 0.297 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.474 | 0.084 | 0.269 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.357 | 0.146 | 0.287 | P7 input |
| A_m swarm mean | +0.322 | 0.232 | 0.327 | sign of A (P6) |
| A_m roster-stable | +0.322 | 0.232 | 0.327 | reported |
| β_wk weekend gap | +0.278 | 0.932 | 0.780 | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 3.0/4.6; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.25, 0.79, 0.59, 0.73.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.291; n16 +0.202; n64 +0.115; rarefied +0.353; calendar clock +0.748.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.32, r = 0.67, τ = 0.7 d, mean S = 0.200): co-primary 0.10 (pre-registered null), 0.08 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.015 ± 0.012 (n = 20).

Data: `data/processed/H20-content-aging/G05/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G05.pdf](figures/aging_G05.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
