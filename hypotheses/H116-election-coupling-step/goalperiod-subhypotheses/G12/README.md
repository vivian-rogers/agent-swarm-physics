# H116 × G12: Form two teams and debate each other, while one agent judges (2025-09-01 → 09-05)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime I · mode M · 7 agents · one room · 10 debates on 09-01..09-04, each with its own judge (DQ6 `judge`, read only after H115's blind freeze).

## Why this period
Rotating designations with out-of-role data for the same agents: each judge is a designated agent in one episode and a peer in the others.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* R: the judge's out-coupling to readers is higher in its judged debate than in debates it did not judge, beyond the same contrast for non-judges: Δout_judge > 0 with judge-label permutation p < 0.05. [0.35] Against: Δout_judge ≤ 0 or p ≥ 0.05. R-chair (H65's reply premium for judges, +0.45) favours a positive step.

## Result
*Run 2026-10-04 22:28 UTC* (`analysis/run_replication.py`; `data/processed/H116-election-coupling-step/G12/replication.json`), after H115's ranking was frozen (hash checked by the script). Role-step model over the ten debate windows (3,495 calls), λ = 4.

| Statistic | Observed | Null (judge label permuted within debate, 200) | Verdict |
| --- | --- | --- | --- |
| Δout_judge (extra out-coupling of an agent while it judges) | −0.045 ± 0.10 | mean +0.009, q95 0.12; p(≥) 0.76 | failed |
| Δin_judge | +0.028 | p(≥) 0.40 | — |
| in-flight Δout | +0.093 | — | — |

- Judging does not make others talk more after reading the judge. With H115's pooled pair-type fit (debaters' coupling to the judge J_DJ = 0.07 ± 0.07), the judge role carries no out-coupling.

## Scorecard (period-specific axes)
E (role rotation), G (DQ6 judges), I.

## Notes
- Runs only after H115's G12 ranking is frozen and hashed.
