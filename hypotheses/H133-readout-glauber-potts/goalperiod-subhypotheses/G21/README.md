# H133 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-05)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime I · mode I · 8 agents · 5 non-reserved active days. Units: 21a, 21b (`period_units`).

## Why this period
Units meeting the structural precondition (>= 30 project hops (call) and >= 20 named reads about a project other than the reader's current one; counted 2026-10-07 before any outcome): 21a (31 hops, 39 named reads about another project), 21b (45 hops, 63 named reads about another project).

## Prediction
*Written 2026-10-07, before running H133 on this period.*
- Regime I (chat clock). Card P5: background switch-span elasticity eta_sw > 0 (CI > 0); gamma_nam smaller than in regime III. P1-P3 apply as replication rows but the card's P1-P3 count regime II/III units only.
- Verdict rule for this folder: supported if the period's predictions hold; failed if a kill-rule quantity fires here; descriptive if a test is unpowered by the synthetic check (power < 0.8) or a term is not estimable (< 5 chosen rows with a read).

## Result
*Run 2026-10-07 (`scheme/build.py`, `analysis/run.py`; non-reserved days; Amendments A1–A4 in the card).* Logit: Glauber conditional logit with project × active-hour effects, agent stay effects, habit ln(1 + d), held-before and share; agent-cluster sandwich CIs, agent-block bootstrap (200) where γ_nam enters. N1: within-cell permutation (1,000). η_sw: background calls (no read about another project); A2 model primary.

| Unit | hops / births | γ_nam [95%] (n.e. = < 5 chosen rows) | γ_un | γ_if | N1 p | chosen/expected: named; unnamed; in-flight (post hoc) | η_sw A2 [95%] (card model) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 21a | 22 / 9 | n.e. (0 rows) | n.e. (0) | n.e. (0) | 1.000 | 0/0.1; 0/0.3; 0/0.2 | -0.84 [-1.03, -0.64] (card -0.75) |
| 21b | 20 / 25 | n.e. (1 rows) | n.e. (0) | n.e. (0) | 0.226 | 1/0.1; 0/0.1; 0/0.1 | -0.58 [-1.06, -0.10] (card -0.60) |



**Verdict: failed.** η_sw CI < 0 in 21a, 21b: the opposite sign to P5 (η > 0).

Data: `data/processed/H133-readout-glauber-potts/<unit>/`; per-unit results in `results/units.json`.

## Scorecard (period-specific axes)
- **C:** within-cell permutation null for named reads (descriptive under A1).
- **D:** η_sw and the lag profile are not fitted by the logit.
- **F:** see the card's synthetic section (η_sw recovery bias ≤ 0.02 in non-burst worlds; γ_nam not estimable at the planted 1.0).

## Notes
- 2026-10-07: folder and prediction written before any H133 outcome statistic on this period (only the structural counts above were computed).
- 2026-10-07: result filled (verdict failed).
