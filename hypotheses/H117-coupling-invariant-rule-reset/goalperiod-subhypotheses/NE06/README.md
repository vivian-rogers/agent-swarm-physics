# H117 × NE06: Gemini one-tool-call step, village-wide (#20, 2025-11-20)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime I · mode C/K (#20) · ~8 eligible agents · one room · before 11-18, 11-19 | after 11-20, 11-21 (k = 2). Gemini 3 Pro joins 11-19 and drops out by eligibility.

## Why this period
A rule change that halved actions per turn for every agent (RE-C2) with no room or roster change for the eligible agents: a pure scaffold-field step in the chat-mode regime, the regime of NE35.

## Prediction
*Written 2026-10-04 22:06 UTC, before running on this period.*
- Q (E1 block, fixed pairs) placebo p > 0.05 against the regime-I k = 2 pool [0.7].
- F p < 0.10 [0.45] (the step targets actions per turn, not talk).
- D_F ≤ placebo 95th percentile [0.65]. E2 not run (regime I).
- Verdict rule (card): **supported** if Q has placebo p > 0.05 and F has p < 0.10; **failed** if Q p < 0.05; **mixed** if Q p > 0.05 and F p ≥ 0.10 (no field step to test against).

## Result
*Run 2026-10-04 22:43–22:46 UTC (exploratory, non-holdout).*

| Statistic | Observed | Null (placebo pool) | Verdict |
| --- | --- | --- | --- |
| Q (E1 block, 28 fixed pairs, 8 agents) | 0.82 | p 0.38 | J within placebo |
| F (first stage) | 2.98 | p 0.38 | no field step beyond day-to-day |
| D_F | 0.40 | p 0.23 | within |
| Q-naive | 0.93 | p 0.56 | within |
| Q_MF | 0.63 | p 0.66 | within |

Pool: regime I, k = 2, 83 splits (Q median 0.70, 95th pct 1.43; F 90th pct 6.6). Mixed: J did not move, but the talk fields did not move more than across ordinary nights either. Power at this skeleton (Amendment 1): ±1.2 on half the pairs 0.88, ±0.6 0.70.
Data: `data/processed/H117-coupling-invariant-rule-reset/splits.parquet`, `J/NE06.npz`.

## Scorecard (period-specific axes)
C: placebo calibration passes (Q at the null level). E: no first stage, so not an interventional test.

## Notes
