# H70 × G30: the artifact row of the κ table (2026-02-09 → 2026-02-13)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 11 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 0, P 0, N 38, PN 46 (non-holdout). Primary scale: day scale (night vs mid-day placebo).

## Why this period
The common estimator on every non-holdout period with dense git (DQ4 from #30): the artifact channel's information about the next allocation (bits) and its value (commits per 20 calls) at the context erasures this period has. Each period is one point for the κ row of HH307.

## Prediction
*Written 2026-10-04 20:05 UTC, before running on this period (card P1, P2, P7 applied).*
- I_A > 0 (within-agent permutation p < 0.05) at the primary scale; I_A ≥ 0.3 bits expected where agents hold more than one repo in the period.
- ΔV_A (open × scramble DiD, agent-period fixed effects, V_pre covariate) > 0 with the cluster-bootstrap CI excluding 0 at the primary scale.
- P(X⁺ = A⁻ | a commit) ≥ 0.8 after the scramble, within 0.1 of the placebo.
- Counts against: I_A not significant, or ΔV_A's CI excludes 0 below zero.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; agent-day cluster bootstrap, B = 300).* Primary scale: day.

| Statistic | Observed | Null | Verdict |
| --- | --- | --- | --- |
| day: I_A (bits) | -0.038 [-0.09, -0.00]; raw 0.019, floor 0.056; p 1.000 | within-agent permutation | not met |
| day: ΔV_A (open × scramble, Poisson) | rel +nan –; +nan commits / 20 calls – (open share F/N 0.29, placebo 0.28) | 0 (reading precedes writing) | not met |
| day: κ_A | undefined (I_A ≤ 0.02) – commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.65 [-1.91, +0.92]; I_C +0.023 [-0.09, +0.14] | 0 | – |
| P(X⁺ = A⁻ \| commit) | N 0.50 (n 2), PN 0.80 (n 5) | – | not met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G30`).
