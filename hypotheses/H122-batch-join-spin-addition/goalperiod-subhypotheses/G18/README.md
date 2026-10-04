# H122 × G18: join event(s) in goal period #18

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** join event(s) whose day 1 falls in goal #18:
- **J2025-10-22** (Claude Haiku 4.5; regime I): PRE 2025-10-15 … 2025-10-21 (5 d), P12 2025-10-22, 2025-10-23, F37 2025-10-24 … 2025-10-30 (5 d). 

## Why this period
Each eligible non-holdout join is one replica of a spin addition (card, layer 1). The transition is the object (CLAUDE.md exception (c)).

## Prediction
*Written 2026-10-04 22:21 UTC, before running on this period (the card's rule, written 22:05 UTC).* Per event: **supported** if MJ (newcomer read coupling fitted on F37) beats MC (constant shift fitted on F37) on the incumbents' P12 calls (ΔLL CI > 0) and also beats the in-flight model MJ_pl; **failed** (kill) if MC beats MJ (CI < 0); **mixed** if the ΔLL CI includes 0 (inconclusive, synthetic power quoted) or MJ does not beat MJ_pl; **descriptive** if P12 has < 200 incumbent calls with a newcomer read. Regime I: H67 found no hop-1 read-out coupling, so J_N ≈ 0 and the ΔLL CI should include 0 (card P7: in ≥ 2/3 of regime-I events).

## Result
| Event | incumbents | P12 calls (with newcomer read) | ΔLL MC−MJ [95%] | ΔLL MJ_pl−MJ | ΔLL M_same−MJ | ΔLL M0−M0D | J_N F37 [95%] | J_N P12 [95%] | δ F37 | R²_h MC / MJ | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J2025-10-22 | 7 | 5114 (1199) | -21.73 [-33.01, -11.37] | +5.53 [+2.11, +9.32] | +7.46 [+3.93, +11.63] | -0.52 [-0.78, -0.29] | +0.249 [+0.146, +0.386] | +0.453 [+0.289, +0.685] | +0.49 | 0.72 / 0.25 | failed |

ΔLL in nats per 1,000 incumbent calls on days 1–2 (positive: the second model is better). J in logit per newcomer read. Data: `data/processed/H122-batch-join-spin-addition/results/events.parquet`.

## Scorecard (period-specific axes)
C (held-out days 1–2), D (F37 couplings applied back), E (the join as an intervention).

## Notes
