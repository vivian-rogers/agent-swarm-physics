# H133 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** mixed
**Role:** exploratory (replication, native N2)
**Period:** regime III · mode I/K · 21 agents · 45 non-reserved active days. Units: 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l (`period_units`).

## Why this period
Units meeting the structural precondition (>= 30 project hops (call) and >= 20 named reads about a project other than the reader's current one; counted 2026-10-07 before any outcome): 51a (2712 hops, 724 named reads about another project), 51b (637 hops, 42 named reads about another project), 51c (6073 hops, 229 named reads about another project), 51d (4594 hops, 360 named reads about another project), 51e (3456 hops, 685 named reads about another project), 51f (5102 hops, 430 named reads about another project), 51g (14207 hops, 911 named reads about another project), 51h (5128 hops, 461 named reads about another project), 51i (1895 hops, 209 named reads about another project), 51j (1996 hops, 283 named reads about another project), 51k (850 hops, 125 named reads about another project), 51l (1040 hops, 77 named reads about another project).
Role: native N2 (timer-wake background elasticity; units 51a-51l).

## Prediction
*Written 2026-10-07, before running H133 on this period.*
- Regime III. Card P1: gamma_nam > 0 with bootstrap CI > 0 and N1 p < 0.05. P2: gamma_un CI includes 0 and Delta-gamma = gamma_nam - gamma_un has CI > 0. P3: gamma_nam - gamma_if > 0. P4: eta_sw CI includes 0 and excludes 1.
- Native N2 (credence 0.6): on timer-wake background calls, eta_sw CI includes 0 and excludes 1; counts against: CI includes 1.
- Verdict rule for this folder: supported if the period's predictions hold; failed if a kill-rule quantity fires here; descriptive if a test is unpowered by the synthetic check (power < 0.8) or a term is not estimable (< 5 chosen rows with a read).

## Result
*Run 2026-10-07 (`scheme/build.py`, `analysis/run.py`; non-reserved days; Amendments A1–A4 in the card).* Logit: Glauber conditional logit with project × active-hour effects, agent stay effects, habit ln(1 + d), held-before and share; agent-cluster sandwich CIs, agent-block bootstrap (200) where γ_nam enters. N1: within-cell permutation (1,000). η_sw: background calls (no read about another project); A2 model primary.

| Unit | hops / births | γ_nam [95%] (n.e. = < 5 chosen rows) | γ_un | γ_if | N1 p | chosen/expected: named; unnamed; in-flight (post hoc) | η_sw A2 [95%] (card model) | η_sw timer wakes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 2587 / 125 | +1.76 [+0.81, +2.78] | -0.65 [-1.39, +0.09] | +0.08 [-1.24, +1.40] | 0.001 | 26/9.8; 45/66.7; 7/6.6 | -0.10 [-0.23, +0.03] (card -0.11) | +0.10 [-0.71, +0.91] (360 calls) |
| 51b | 591 / 46 | n.e. (1 rows) | n.e. (2) | n.e. (0) | 0.084 | 1/0.2; 2/2.5; 0/0.0 | +0.10 [-0.07, +0.27] (card +0.06) | -1.52 [-4.06, +1.01] (79 calls) |
| 51c | 5878 / 195 | +1.12 [-0.28, +3.35] | -0.14 [-2.00, +1.72] | n.e. (2) | 0.001 | 10/6.8; 77/74.6; 2/2.7 | +0.07 [+0.02, +0.13] (card +0.07) | +0.23 [-0.40, +0.87] (861 calls) |
| 51d | 4459 / 135 | +2.74 [+1.76, +3.95] | -0.43 [-1.72, +0.86] | n.e. (3) | 0.001 | 20/4.8; 46/57.0; 3/2.4 | +0.06 [+0.01, +0.12] (card +0.06) | +0.73 [-0.07, +1.53] (540 calls) |
| 51e | 3366 / 90 | +2.87 [+1.60, +4.51] | -0.71 [-2.01, +0.59] | n.e. (3) | 0.001 | 40/12.3; 52/70.7; 3/3.3 | +0.10 [-0.05, +0.24] (card +0.09) | -0.02 [-1.41, +1.38] (146 calls) |
| 51f | 4953 / 149 | +3.74 [+1.53, +5.57] | -0.10 [-0.80, +0.59] | n.e. (3) | 0.001 | 28/8.3; 55/50.8; 3/1.2 | +0.07 [-0.07, +0.21] (card +0.07) | +0.29 [-0.21, +0.78] (899 calls) |
| 51g | 13712 / 495 | +3.63 [+2.99, +4.51] | -0.28 [-0.57, +0.02] | -0.14 [-2.41, +2.12] | 0.001 | 82/23.8; 131/149.0; 9/9.9 | +0.00 [-0.09, +0.10] (card +0.00) | +0.18 [-0.21, +0.56] (2502 calls) |
| 51h | 4960 / 168 | +1.40 [-0.35, +4.30] | -0.90 [-1.55, -0.25] | n.e. (3) | 0.001 | 11/5.6; 53/91.8; 3/3.2 | +0.02 [-0.11, +0.15] (card +0.02) | +1.00 [+0.34, +1.67] (300 calls) |
| 51i | 1798 / 97 | +2.39 [+0.27, +4.74] | -0.43 [-0.98, +0.13] | n.e. (1) | 0.001 | 7/3.0; 40/49.8; 1/1.4 | -0.05 [-0.17, +0.06] (card -0.06) | +0.38 [-1.50, +2.27] (108 calls) |
| 51j | 1895 / 101 | n.e. (4 rows) | -0.20 [-0.64, +0.23] | n.e. (0) | 0.021 | 4/0.9; 44/46.8; 0/1.0 | +0.02 [-0.19, +0.24] (card +0.02) | +0.78 [-1.46, +3.02] (68 calls) |
| 51k | 788 / 62 | +2.31 [-22.80, +6.12] | +0.69 [-0.01, +1.39] | n.e. (2) | 0.001 | 7/2.8; 25/16.5; 2/1.1 | -0.08 [-0.24, +0.07] (card -0.09) | n.e. |
| 51l | 978 / 62 | +4.71 [+1.70, +8.51] | +0.86 [+0.29, +1.44] | n.e. (1) | 0.001 | 5/0.3; 33/18.9; 1/0.2 | -0.03 [-0.10, +0.05] (card -0.03) | +2.48 [+1.12, +3.85] (103 calls) |

- **Native N2 (timer wakes):** random-effects η_sw over 11 units = +0.46 [+0.09, +0.84] (A2 model); card model +0.31 [-0.00, +0.63]. The CI excludes 1 (no wall clock) but, on the primary model, also excludes 0. N2 **fails** on its "includes 0" half. The synthetic bias on timer wakes is ≤ +0.07, and +0.22 under an attention burst (51h).
- Last column: η_sw on timer-wake background calls (A2 model).

**Verdict: mixed.** P4 fails in 51c, 51d (η_sw CI excludes 0) and holds elsewhere; Kill B does not fire (every CI excludes 1). P1–P3 untestable (A1). Native N2 fails: the timer-wake η_sw is +0.46, and its CI excludes both 0 and 1.

Data: `data/processed/H133-readout-glauber-potts/<unit>/`; per-unit results in `results/units.json`.

## Scorecard (period-specific axes)
- **C:** within-cell permutation null for named reads (descriptive under A1).
- **D:** η_sw and the lag profile are not fitted by the logit.
- **F:** see the card's synthetic section (η_sw recovery bias ≤ 0.02 in non-burst worlds; γ_nam not estimable at the planted 1.0).

## Notes
- 2026-10-07: folder and prediction written before any H133 outcome statistic on this period (only the structural counts above were computed).
- 2026-10-07: result filled (verdict mixed).
