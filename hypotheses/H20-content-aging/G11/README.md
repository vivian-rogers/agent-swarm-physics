# H20 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-08-29)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime I · mode F · 7 agents with statements · #general only · 5 active days (35 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.11 / 0.12 / 0.13 against μ = 0.5 aging, 0.20 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.11.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = -0.193 (p = 0.778), A_c = -0.134 (p = 0.707), A_g = -0.270 (p = 0.840), A_late = -0.086, K = -0.170; co-primary design power vs μ = 0.5: 0.18 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.170 | 1.000 | 0.916 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | -0.193 | 0.950 | 0.778 | > 0 (P2, co-primary) |
| A_c common removed | -0.134 | 0.876 | 0.707 | > 0 (P2, co-primary) |
| A_g field removed | -0.270 | 0.984 | 0.840 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | -0.086 | 0.653 | 0.547 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | -0.193 | 0.950 | 0.778 | P7 input |
| A_m swarm mean | -0.301 | 0.874 | 0.715 | sign of A (P6) |
| A_m roster-stable | -0.301 | 0.874 | 0.715 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 2.3/7.0; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.90, 0.76, 0.59, 0.57.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat -0.140; n16 -0.225; n64 -0.233; rarefied -0.217; calendar clock -0.193.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.23, r = 0.76, τ = 1.2 d, mean S = 0.383): co-primary 0.35 (pre-registered null), 0.18 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.027 ± 0.013 (n = 35).

Data: `data/processed/H20-content-aging/G11/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G11.pdf](figures/aging_G11.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
