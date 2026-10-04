# H20 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime III · mode I · 16 agents with statements · 2 rooms with agent statements · 5 active days (78 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.13 / 0.09 / 0.18 against μ = 0.5 aging, 0.23 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.13.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.035 (p = 0.204), A_c = +0.071 (p = 0.100), A_g = +0.039 (p = 0.226), A_late = +0.042, K = +0.036; co-primary design power vs μ = 0.5: 0.06 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | +0.036 | 0.010 | 0.074 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.035 | 0.096 | 0.204 | > 0 (P2, co-primary) |
| A_c common removed | +0.071 | 0.052 | 0.100 | > 0 (P2, co-primary) |
| A_g field removed | +0.039 | 0.106 | 0.226 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.042 | 0.265 | 0.355 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.035 | 0.096 | 0.204 | P7 input |
| A_m swarm mean | +0.019 | 0.236 | 0.325 | sign of A (P6) |
| A_m roster-stable | +0.016 | 0.236 | 0.321 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.8/13.9; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.83, 0.89, 0.88, 0.89.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.038; n16 +0.035; n64 +0.042; rarefied +0.021; calendar clock +0.035.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.81, r = 0.18, τ = 0.3 d, mean S = 0.495): co-primary 0.06 (pre-registered null), 0.06 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.030 ± 0.009 (n = 78).

Data: `data/processed/H20-content-aging/G42/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G42.pdf](figures/aging_G42.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
