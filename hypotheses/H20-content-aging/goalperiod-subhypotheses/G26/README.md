# H20 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-09)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime I · mode C · 10 agents with statements · #general only · 5 active days (49 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.11 / 0.09 / 0.15 against μ = 0.5 aging, 0.25 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.11.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = -0.125 (p = 0.661), A_c = +0.105 (p = 0.317), A_g = -0.272 (p = 0.854), A_late = -0.860, K = +0.002; co-primary design power vs μ = 0.5: 0.04 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.002 | 0.465 | 0.421 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.125 | 0.820 | 0.661 | > 0 (P2, co-primary) |
| A_c common removed | +0.105 | 0.202 | 0.317 | > 0 (P2, co-primary) |
| A_g field removed | -0.272 | 0.986 | 0.854 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.860 | 0.992 | 0.826 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.125 | 0.820 | 0.661 | P7 input |
| A_m swarm mean | -0.327 | 0.932 | 0.743 | sign of A (P6) |
| A_m roster-stable | -0.327 | 0.932 | 0.743 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.8/8.2; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.71, 0.52, 0.68, 0.43.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat -0.058; n16 -0.055; n64 -0.098; rarefied -0.105; calendar clock -0.125.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.43, r = 0.56, τ = 0.3 d, mean S = 0.277): co-primary 0.13 (pre-registered null), 0.04 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.013 ± 0.008 (n = 50).

Data: `data/processed/H20-content-aging/G26/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G26.pdf](figures/aging_G26.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
