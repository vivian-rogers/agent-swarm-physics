# H133 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime II · mode C · 13 agents · 5 non-reserved active days. Units: 36a, 36b, 36c (`period_units`).

## Why this period
Units meeting the structural precondition (>= 30 project hops (call) and >= 20 named reads about a project other than the reader's current one; counted 2026-10-07 before any outcome): 36a (527 hops, 43 named reads about another project), 36b (962 hops, 32 named reads about another project), 36c (1336 hops, 56 named reads about another project).

## Prediction
*Written 2026-10-07, before running H133 on this period.*
- Regime II. Card P1: gamma_nam > 0 with bootstrap CI > 0 and N1 p < 0.05. P2: gamma_un CI includes 0 and Delta-gamma = gamma_nam - gamma_un has CI > 0. P3: gamma_nam - gamma_if > 0. P4: eta_sw CI includes 0 and excludes 1.
- Verdict rule for this folder: supported if the period's predictions hold; failed if a kill-rule quantity fires here; descriptive if a test is unpowered by the synthetic check (power < 0.8) or a term is not estimable (< 5 chosen rows with a read).

## Result
*Run 2026-10-07 (`scheme/build.py`, `analysis/run.py`; non-reserved days; Amendments A1–A4 in the card).* Logit: Glauber conditional logit with project × active-hour effects, agent stay effects, habit ln(1 + d), held-before and share; agent-cluster sandwich CIs, agent-block bootstrap (200) where γ_nam enters. N1: within-cell permutation (1,000). η_sw: background calls (no read about another project); A2 model primary.

| Unit | hops / births | γ_nam [95%] (n.e. = < 5 chosen rows) | γ_un | γ_if | N1 p | chosen/expected: named; unnamed; in-flight (post hoc) | η_sw A2 [95%] (card model) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 451 / 76 | n.e. (0 rows) | +0.13 [-1.15, +1.40] | n.e. (2) | 1.000 | 0/0.5; 7/6.4; 2/0.4 | -0.07 [-0.29, +0.15] (card -0.07) |
| 36b | 858 / 104 | +3.68 [+1.35, +6.55] | -0.07 [-0.77, +0.63] | n.e. (0) | 0.001 | 7/2.0; 5/5.2; 0/0.8 | -0.32 [-0.57, -0.06] (card -0.32) |
| 36c | 1261 / 75 | n.e. (3 rows) | +0.66 [-0.38, +1.69] | n.e. (3) | 0.028 | 3/2.4; 15/10.0; 3/2.0 | -0.32 [-0.63, +0.00] (card -0.31) |



**Verdict: mixed.** P4 fails in 36b (η_sw CI excludes 0) and holds elsewhere; Kill B does not fire (every CI excludes 1). P1–P3 untestable (A1).

Data: `data/processed/H133-readout-glauber-potts/<unit>/`; per-unit results in `results/units.json`.

## Scorecard (period-specific axes)
- **C:** within-cell permutation null for named reads (descriptive under A1).
- **D:** η_sw and the lag profile are not fitted by the logit.
- **F:** see the card's synthetic section (η_sw recovery bias ≤ 0.02 in non-burst worlds; γ_nam not estimable at the planted 1.0).

## Notes
- 2026-10-07: folder and prediction written before any H133 outcome statistic on this period (only the structural counts above were computed).
- 2026-10-07: result filled (verdict mixed).
