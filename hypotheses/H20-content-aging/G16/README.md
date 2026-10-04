# H20 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime I · mode F · 7 agents with statements · #general only · 5 active days (35 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.10 / 0.13 / 0.16 against μ = 0.5 aging, 0.19 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.10.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.122 (p = 0.271), A_c = -0.049 (p = 0.625), A_g = +0.119 (p = 0.281), A_late = +0.149, K = -0.161; co-primary design power vs μ = 0.5: 0.07 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.161 | 0.998 | 0.948 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.122 | 0.136 | 0.271 | > 0 (P2, co-primary) |
| A_c common removed | -0.049 | 0.697 | 0.625 | > 0 (P2, co-primary) |
| A_g field removed | +0.119 | 0.142 | 0.281 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.149 | 0.291 | 0.371 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.122 | 0.136 | 0.271 | P7 input |
| A_m swarm mean | +0.383 | 0.056 | 0.208 | sign of A (P6) |
| A_m roster-stable | +0.383 | 0.056 | 0.208 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 3.2/9.9; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.69, 0.40, 0.51, 0.55.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.173; n16 +0.187; n64 +0.037; rarefied +0.065; calendar clock +0.122.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.37, r = 0.57, τ = 0.6 d, mean S = 0.338): co-primary 0.16 (pre-registered null), 0.07 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope -0.004 ± 0.014 (n = 35).

Data: `data/processed/H20-content-aging/G16/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G16.pdf](figures/aging_G16.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
