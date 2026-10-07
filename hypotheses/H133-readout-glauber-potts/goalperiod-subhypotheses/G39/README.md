# H133 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · mode I · 15 agents · 5 non-reserved active days. Units: 39 (`period_units`).

## Why this period
Units meeting the structural precondition (>= 30 project hops (call) and >= 20 named reads about a project other than the reader's current one; counted 2026-10-07 before any outcome): 39 (502 hops, 243 named reads about another project).

## Prediction
*Written 2026-10-07, before running H133 on this period.*
- Regime III. Card P1: gamma_nam > 0 with bootstrap CI > 0 and N1 p < 0.05. P2: gamma_un CI includes 0 and Delta-gamma = gamma_nam - gamma_un has CI > 0. P3: gamma_nam - gamma_if > 0. P4: eta_sw CI includes 0 and excludes 1.
- Verdict rule for this folder: supported if the period's predictions hold; failed if a kill-rule quantity fires here; descriptive if a test is unpowered by the synthetic check (power < 0.8) or a term is not estimable (< 5 chosen rows with a read).

## Result
*Run 2026-10-07 (`scheme/build.py`, `analysis/run.py`; non-reserved days; Amendments A1–A4 in the card).* Logit: Glauber conditional logit with project × active-hour effects, agent stay effects, habit ln(1 + d), held-before and share; agent-cluster sandwich CIs, agent-block bootstrap (200) where γ_nam enters. N1: within-cell permutation (1,000). η_sw: background calls (no read about another project); A2 model primary.

| Unit | hops / births | γ_nam [95%] (n.e. = < 5 chosen rows) | γ_un | γ_if | N1 p | chosen/expected: named; unnamed; in-flight (post hoc) | η_sw A2 [95%] (card model) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 475 / 27 | n.e. (1 rows) | n.e. (4) | n.e. (0) | 0.313 | 1/0.6; 4/6.9; 0/0.4 | +0.17 [-0.02, +0.36] (card +0.18) |



**Verdict: descriptive.** P4 holds (η_sw CI includes 0 and excludes 1 in every unit); P1–P3 are untestable (A1), so the period cannot be supported.

Data: `data/processed/H133-readout-glauber-potts/<unit>/`; per-unit results in `results/units.json`.

## Scorecard (period-specific axes)
- **C:** within-cell permutation null for named reads (descriptive under A1).
- **D:** η_sw and the lag profile are not fitted by the logit.
- **F:** see the card's synthetic section (η_sw recovery bias ≤ 0.02 in non-burst worlds; γ_nam not estimable at the planted 1.0).

## Notes
- 2026-10-07: folder and prediction written before any H133 outcome statistic on this period (only the structural counts above were computed).
- 2026-10-07: result filled (verdict descriptive).
