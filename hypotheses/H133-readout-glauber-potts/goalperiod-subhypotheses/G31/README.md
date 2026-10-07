# H133 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** failed
**Role:** exploratory (replication, native N4)
**Period:** regime I · mode F · 12 agents · 5 non-reserved active days. Units: 31a, 31b, 31c, 31d (`period_units`).

## Why this period
Units meeting the structural precondition (>= 30 project hops (call) and >= 20 named reads about a project other than the reader's current one; counted 2026-10-07 before any outcome): 31a (813 hops, 101 named reads about another project), 31b (363 hops, 63 named reads about another project), 31c (275 hops, 56 named reads about another project), 31d (354 hops, 98 named reads about another project).
Role: native N4 (regime-I herding week; eta_sw > 0 expected).

## Prediction
*Written 2026-10-07, before running H133 on this period.*
- Regime I (chat clock). Card P5: background switch-span elasticity eta_sw > 0 (CI > 0); gamma_nam smaller than in regime III. P1-P3 apply as replication rows but the card's P1-P3 count regime II/III units only.
- Native N4 (credence 0.45): eta_sw > 0; counts against: eta_sw CI includes 0 at power >= 0.8.
- Verdict rule for this folder: supported if the period's predictions hold; failed if a kill-rule quantity fires here; descriptive if a test is unpowered by the synthetic check (power < 0.8) or a term is not estimable (< 5 chosen rows with a read).

## Result
*Run 2026-10-07 (`scheme/build.py`, `analysis/run.py`; non-reserved days; Amendments A1–A4 in the card).* Logit: Glauber conditional logit with project × active-hour effects, agent stay effects, habit ln(1 + d), held-before and share; agent-cluster sandwich CIs, agent-block bootstrap (200) where γ_nam enters. N1: within-cell permutation (1,000). η_sw: background calls (no read about another project); A2 model primary.

| Unit | hops / births | γ_nam [95%] (n.e. = < 5 chosen rows) | γ_un | γ_if | N1 p | chosen/expected: named; unnamed; in-flight (post hoc) | η_sw A2 [95%] (card model) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 785 / 28 | n.e. (4 rows) | -1.06 [-2.64, +0.51] | n.e. (2) | 0.002 | 4/0.9; 8/15.2; 2/0.5 | -0.26 [-0.61, +0.08] (card -0.28) |
| 31b | 338 / 25 | n.e. (1 rows) | n.e. (3) | n.e. (0) | 0.369 | 1/0.7; 3/6.7; 0/0.6 | -0.18 [-0.38, +0.02] (card -0.17) |
| 31c | 250 / 25 | n.e. (1 rows) | n.e. (1) | n.e. (0) | 0.284 | 1/0.4; 1/4.4; 0/0.2 | -0.19 [-0.55, +0.17] (card -0.19) |
| 31d | 336 / 18 | +1.89 [-0.60, +3.36] | +0.80 [-0.02, +1.61] | n.e. (1) | 0.007 | 5/1.5; 13/8.1; 1/0.9 | -0.31 [-0.65, +0.02] (card -0.43) |

- **Native N4:** random-effects η_sw over 31a–31d = -0.22 [-0.34, -0.09] (A2 model). The prediction was η_sw > 0. N4 **fails**: η is negative.

**Verdict: failed.** Each unit's η_sw CI includes 0, but the random-effects mean over 31a–31d is negative with CI < 0: the opposite sign to P5 and N4 (η > 0). P1–P3 are untestable (A1).

Data: `data/processed/H133-readout-glauber-potts/<unit>/`; per-unit results in `results/units.json`.

## Scorecard (period-specific axes)
- **C:** within-cell permutation null for named reads (descriptive under A1).
- **D:** η_sw and the lag profile are not fitted by the logit.
- **F:** see the card's synthetic section (η_sw recovery bias ≤ 0.02 in non-burst worlds; γ_nam not estimable at the planted 1.0).

## Notes
- 2026-10-07: folder and prediction written before any H133 outcome statistic on this period (only the structural counts above were computed).
- 2026-10-07: result filled (verdict failed).
