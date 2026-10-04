# H20 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime I · mode F · 12 agents with statements · #general only · 5 active days (56 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.15 / 0.10 / 0.13 against μ = 0.5 aging, 0.19 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.15.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.006 (p = 0.443), A_c = +0.068 (p = 0.317), A_g = +0.001 (p = 0.481), A_late = +0.072, K = -0.047; co-primary design power vs μ = 0.5: 0.14 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.047 | 0.874 | 0.711 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.006 | 0.435 | 0.443 | > 0 (P2, co-primary) |
| A_c common removed | +0.068 | 0.182 | 0.317 | > 0 (P2, co-primary) |
| A_g field removed | +0.001 | 0.485 | 0.481 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.072 | 0.347 | 0.401 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.006 | 0.435 | 0.443 | P7 input |
| A_m swarm mean | -0.024 | 0.551 | 0.499 | sign of A (P6) |
| A_m roster-stable | -0.086 | 0.737 | 0.613 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 3.4/9.1; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.73, 0.71, 0.72, 0.74.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat -0.047; n16 +0.062; n64 -0.039; rarefied -0.037; calendar clock +0.006.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.55, r = 0.44, τ = 0.8 d, mean S = 0.306): co-primary 0.26 (pre-registered null), 0.14 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.009 ± 0.006 (n = 56).

Data: `data/processed/H20-content-aging/G31/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G31.pdf](figures/aging_G31.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
