# H20 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-13)

**Verdict:** descriptive (stationary contrast) (Amendment-2 null; pre-registered null: descriptive)
**Role:** exploratory
**Period:** regime I · mode C · 11 agents with statements · #general only · 5 active days (55 agent-days with ≥ 8 statements).

## Why this period
A 5-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).

## Prediction
*Written 2026-10-03, before running on this period.* Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): 0.14 / 0.10 / 0.10 against μ = 0.5 aging, 0.29 against μ = 1 (a² = 0.15). Matched-window power (A_early, μ = 0.5, a² = 0.15): 0.14.
- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).
- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).
- **Verdict rule:** descriptive (stationary contrast).

## Result
A = +0.153 (p = 0.226), A_c = +0.106 (p = 0.134), A_g = +0.137 (p = 0.206), A_late = +0.174, K = -0.082; co-primary design power vs μ = 0.5: 0.07 (Amendment-2 null).

| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |
| --- | --- | --- | --- | --- |
| K kickoff transient | -0.082 | 0.958 | 0.786 | > 0 (P1) |
| A aging slope (t_w ≥ 2) | +0.153 | 0.036 | 0.226 | > 0 (P2, co-primary) |
| A_c common removed | +0.106 | 0.048 | 0.134 | > 0 (P2, co-primary) |
| A_g field removed | +0.137 | 0.076 | 0.206 | > 0 if P2 (P3) |
| A_late (t_w ≥ median) | +0.174 | 0.138 | 0.303 | > 0 if P2 (P4) |
| A_early (t_w 2–4, τ ≤ 2) | +0.153 | 0.036 | 0.226 | P7 input |
| A_m swarm mean | +0.162 | 0.092 | 0.271 | sign of A (P6) |
| A_m roster-stable | +0.162 | 0.092 | 0.271 | reported |
| β_wk weekend gap | – | – | – | < 0 (S1) |

Verdict under the pre-registered isotropic null: **descriptive (stationary contrast)**. Under the Amendment-2 null (latent shapes estimated, n_eff shared/private = 3.3/8.7; see the card): **descriptive (stationary contrast)**.
Lag-1 correlation C(t_w, t_w + 1) by t_w: 0.73, 0.74, 0.82, 0.87.
Per-agent slopes: n = 0, median A_i –, share > 0 –, Wilcoxon p (greater) –.
Robustness of A (S3): chat +0.151; n16 +0.201; n64 +0.129; rarefied +0.142; calendar clock +0.153.
Design power against μ = 0.5 at the fitted nuisance parameters (q = 0.11, r = 0.81, τ = 6.4 d, mean S = 0.288): co-primary 0.12 (pre-registered null), 0.07 (Amendment-2 null).
Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope +0.008 ± 0.008 (n = 55).

Data: `data/processed/H20-content-aging/G30/` (result.json = pre-registered null, result_aniso.json = Amendment 2, matrices.npz). Figure: [figures/aging_G30.pdf](figures/aging_G30.pdf).

## Scorecard (period-specific axes)
C: – (no per-period test). D: K and A_early reported as P7 inputs. G: –.

## Notes
