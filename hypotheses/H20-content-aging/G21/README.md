# H20 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-05)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime I · mode I · 9 agents with statements · #general only · 5 active days (42 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.10 / 0.04 / 0.16 against μ = 0.5 aging, 0.25 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.10.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.354 (p = 0.012), A_c = +0.011 (p = 0.385), A_g = +0.366 (p = 0.016), A_late = +0.310, K = +0.021; co-primary design power vs μ = 0.5: 0.16 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.021 | 0.214 | 0.315 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.354 | < 0.002 | 0.012 | > 0 (P2, co-primary) |
| A_c common removed | +0.011 | 0.341 | 0.385 | > 0 (P2, co-primary) |
| A_g field removed | +0.366 | < 0.002 | 0.016 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.310 | < 0.002 | 0.082 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.354 | < 0.002 | 0.012 | P7 input |
| A_m swarm mean | +0.557 | < 0.002 | 0.038 | sign of A (P6) |
| A_m roster-stable | +0.569 | < 0.002 | 0.040 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.4/8.7; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.69, 0.55, 0.74, 0.83.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.373; n16 +0.223; n64 +0.249; rarefied +0.337; calendar clock +0.354.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.00, r = 0.99, τ = 10.8 d, mean S = 0.365): co-primary 0.40 (pre-registered null), 0.16 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.053 ± 0.010 (n = 42).

Data: `data/processed/H20-content-aging/G21/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G21.pdf](figures/aging_G21.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
