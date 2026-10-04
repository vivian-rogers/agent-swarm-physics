# H70 × G33: the artifact row of the κ table (2026-03-02 → 2026-03-04)

**Verdict:** descriptive
**Role:** replication
**Period:** regime II · 11 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 0, P 0, N 22, PN 32 (non-holdout). Primary scale: day scale (night vs mid-day placebo).

## Why this period
The common estimator on every non-holdout period with dense git (DQ4 from #30): the artifact channel's information about the next allocation (bits) and its value (commits per 20 calls) at the context erasures this period has. Each period is one point for the κ row of HH307.

## Prediction
*Written 2026-10-04 20:05 UTC, before running on this period (card P1, P2, P7 applied).*
- I_A > 0 (within-agent permutation p < 0.05) at the primary scale; I_A ≥ 0.3 bits expected where agents hold more than one repo in the period.
- ΔV_A (open × scramble DiD, agent-period fixed effects, V_pre covariate) > 0 with the cluster-bootstrap CI excluding 0 at the primary scale.
- P(X⁺ = A⁻ | a commit) ≥ 0.8 after the scramble, within 0.1 of the placebo.
- Counts against: I_A not significant, or ΔV_A's CI excludes 0 below zero.
- Fewer than 30 events per arm at day scale: the verdict is descriptive by the card rule.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; agent-day cluster bootstrap, B = 300).* Primary scale: day.

| Statistic | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P(X⁺ = A⁻ \| commit) | N 1.00 (n 5), PN 0.87 (n 15) | – | met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G33`).
