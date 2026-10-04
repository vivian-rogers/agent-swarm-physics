# H70 × G38: the artifact row of the κ table (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 14 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 2149, P 2200, N 196, PN 199 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

## Why this period
The common estimator on every non-holdout period with dense git (DQ4 from #30): the artifact channel's information about the next allocation (bits) and its value (commits per 20 calls) at the context erasures this period has. Each period is one point for the κ row of HH307.

## Prediction
*Written 2026-10-04 20:05 UTC, before running on this period (card P1, P2, P7 applied).*
- I_A > 0 (within-agent permutation p < 0.05) at the primary scale; I_A ≥ 0.3 bits expected where agents hold more than one repo in the period.
- ΔV_A (open × scramble DiD, agent-period fixed effects, V_pre covariate) > 0 with the cluster-bootstrap CI excluding 0 at the primary scale.
- P(X⁺ = A⁻ | a commit) ≥ 0.8 after the scramble, within 0.1 of the placebo.
- Counts against: I_A not significant, or ΔV_A's CI excludes 0 below zero.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; agent-day cluster bootstrap, B = 300).* Primary scale: call.

| Statistic | Observed | Null | Verdict |
| --- | --- | --- | --- |
| call: I_A (bits) | +0.107 [+0.06, +0.15]; raw 0.312, floor 0.205; p 0.005 | within-agent permutation | met |
| call: ΔV_A (open × scramble, Poisson) | rel +0.16 [-0.20, +0.67]; +0.09 commits / 20 calls [-0.12, +0.28] (open share F/N 0.22, placebo 0.21) | 0 (reading precedes writing) | not met |
| call: κ_A | +0.80 [-1.41, +2.63] commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.30 [+0.12, +0.44]; I_C +0.089 [+0.04, +0.13] | 0 | – |
| day: I_A (bits) | +0.136 [+0.03, +0.23]; raw 0.515, floor 0.379; p 0.005 | within-agent permutation | met |
| day: ΔV_A (open × scramble, Poisson) | rel +0.02 [-0.62, +1.60]; +0.01 commits / 20 calls [-0.91, +0.47] (open share F/N 0.27, placebo 0.24) | 0 (reading precedes writing) | not met |
| day: κ_A | +0.09 [-6.90, +4.94] commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.21 [-0.17, +0.49]; I_C +0.063 [-0.13, +0.24] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.87 (n 303), P 0.85 (n 356), N 0.83 (n 36), PN 0.82 (n 39) | – | met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G38`).
