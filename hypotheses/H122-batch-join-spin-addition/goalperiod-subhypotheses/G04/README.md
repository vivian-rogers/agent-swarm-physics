# H122 × G04: join event(s) in goal period #4

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** join event(s) whose day 1 falls in goal #4:
- **J2025-05-22** (o4-mini, Claude Opus 4; regime I): PRE 2025-05-15 … 2025-05-21 (5 d), P12 2025-05-22, 2025-05-23, F37 2025-05-26 … 2025-05-30 (5 d). o4-mini joins on 05-22 and leaves on 05-23; Claude Opus 4 joins on 05-23 (merged as one event).

## Why this period
Each eligible non-holdout join is one replica of a spin addition (card, layer 1). The transition is the object (CLAUDE.md exception (c)).

## Prediction
*Written 2026-10-04 22:21 UTC, before running on this period (the card's rule, written 22:05 UTC).* Per event: **supported** if MJ (newcomer read coupling fitted on F37) beats MC (constant shift fitted on F37) on the incumbents' P12 calls (ΔLL CI > 0) and also beats the in-flight model MJ_pl; **failed** (kill) if MC beats MJ (CI < 0); **mixed** if the ΔLL CI includes 0 (inconclusive, synthetic power quoted) or MJ does not beat MJ_pl; **descriptive** if P12 has < 200 incumbent calls with a newcomer read. Regime I: H67 found no hop-1 read-out coupling, so J_N ≈ 0 and the ΔLL CI should include 0 (card P7: in ≥ 2/3 of regime-I events).

## Result
| Event | incumbents | P12 calls (with newcomer read) | ΔLL MC−MJ [95%] | ΔLL MJ_pl−MJ | ΔLL M_same−MJ | ΔLL M0−M0D | J_N F37 [95%] | J_N P12 [95%] | δ F37 | R²_h MC / MJ | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J2025-05-22 | 3 | 2243 (419) | -1.74 [-15.17, +11.60] | +1.50 [-1.40, +4.46] | +1.16 [-0.44, +2.62] | +0.00 [+0.00, +0.00] | -0.081 [-0.268, +0.181] | -0.343 [-0.743, +0.037] | -0.31 | 0.34 / 0.04 | mixed |

ΔLL in nats per 1,000 incumbent calls on days 1–2 (positive: the second model is better). J in logit per newcomer read. Data: `data/processed/H122-batch-join-spin-addition/results/events.parquet`.

## Scorecard (period-specific axes)
C (held-out days 1–2), D (F37 couplings applied back), E (the join as an intervention).

## Notes
