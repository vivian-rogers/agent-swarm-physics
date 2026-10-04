# H20 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-19)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime I · mode K · 10 agents with statements · #general only · 5 active days (50 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.16 / 0.10 / 0.13 against μ = 0.5 aging, 0.28 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.16.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = -0.044 (p = 0.790), A_c = +0.094 (p = 0.016), A_g = -0.032 (p = 0.719), A_late = -0.125, K = +0.051; co-primary design power vs μ = 0.5: 0.08 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.051 | < 0.002 | 0.094 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.044 | 0.980 | 0.790 | > 0 (P2, co-primary) |
| A_c common removed | +0.094 | < 0.002 | 0.016 | > 0 (P2, co-primary) |
| A_g field removed | -0.032 | 0.896 | 0.719 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.125 | 0.994 | 0.878 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.044 | 0.980 | 0.790 | P7 input |
| A_m swarm mean | -0.045 | 0.946 | 0.768 | sign of A (P6) |
| A_m roster-stable | -0.045 | 0.946 | 0.768 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.4/6.5; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.87, 0.95, 0.95, 0.91.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat -0.083; n16 -0.012; n64 -0.059; rarefied -0.042; calendar clock -0.044.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.00, r = 0.99, τ = 29.9 d, mean S = 0.532): co-primary 0.22 (pre-registered null), 0.08 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.003 ± 0.007 (n = 50).

Data: `data/processed/H20-content-aging/G23/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G23.pdf](figures/aging_G23.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
