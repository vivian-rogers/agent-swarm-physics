# H133 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime I · mode C · 7 agents · 10 non-reserved active days. Units: 18a, 18b, 18c (`period_units`).

## Why this period
Units meeting the structural precondition (>= 30 project hops (call) and >= 20 named reads about a project other than the reader's current one; counted 2026-10-07 before any outcome): 18b (243 hops, 260 named reads about another project).
Units below the precondition (not tested): 18a, 18c.

## Prediction
*Written 2026-10-07, before running H133 on this period.*
- Regime I (chat clock). Card P5: background switch-span elasticity eta_sw > 0 (CI > 0); gamma_nam smaller than in regime III. P1-P3 apply as replication rows but the card's P1-P3 count regime II/III units only.
- Verdict rule for this folder: supported if the period's predictions hold; failed if a kill-rule quantity fires here; descriptive if a test is unpowered by the synthetic check (power < 0.8) or a term is not estimable (< 5 chosen rows with a read).

## Result
*Run 2026-10-07 (`scheme/build.py`, `analysis/run.py`; non-reserved days; Amendments A1–A4 in the card).* Logit: Glauber conditional logit with project × active-hour effects, agent stay effects, habit ln(1 + d), held-before and share; agent-cluster sandwich CIs, agent-block bootstrap (200) where γ_nam enters. N1: within-cell permutation (1,000). η_sw: background calls (no read about another project); A2 model primary.

| Unit | hops / births | γ_nam [95%] (n.e. = < 5 chosen rows) | γ_un | γ_if | N1 p | chosen/expected: named; unnamed; in-flight (post hoc) | η_sw A2 [95%] (card model) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 18b | 186 / 57 | +0.54 [-1.07, +2.76] | +1.03 [+0.15, +1.92] | +1.38 [-0.92, +3.68] | 0.022 | 6/3.9; 32/14.3; 5/2.5 | -0.05 [-0.23, +0.12] (card -0.05) |



**Verdict: descriptive.** η_sw CI includes 0: P5 (η > 0) not shown; the test of a small η is unpowered. P1–P3 are untestable (A1).

Data: `data/processed/H133-readout-glauber-potts/<unit>/`; per-unit results in `results/units.json`.

## Scorecard (period-specific axes)
- **C:** within-cell permutation null for named reads (descriptive under A1).
- **D:** η_sw and the lag profile are not fitted by the logit.
- **F:** see the card's synthetic section (η_sw recovery bias ≤ 0.02 in non-burst worlds; γ_nam not estimable at the planted 1.0).

## Notes
- 2026-10-07: folder and prediction written before any H133 outcome statistic on this period (only the structural counts above were computed).
- 2026-10-07: result filled (verdict descriptive).
