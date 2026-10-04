# H122 × G51: join event(s) in goal period #51

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** join event(s) whose day 1 falls in goal #51:
- **J2026-07-17** (Kimi K3; regime III): PRE 2026-07-10 … 2026-07-16 (5 d), P12 2026-07-17, 2026-07-20, F37 2026-07-21 … 2026-07-23 (3 d). PRE contains NE32 days; NE32 newcomers are excluded from incumbents (recent joiners).
- **J2026-07-24** (Claude Opus 5; regime III): PRE 2026-07-17 … 2026-07-23 (5 d), P12 2026-07-24, 2026-07-27, F37 2026-07-28 … 2026-08-03 (5 d). F37 crosses NE38 (07-29: a human reassigns the newcomer Claude Opus 5's role).

## Why this period
Each eligible non-holdout join is one replica of a spin addition (card, layer 1). The transition is the object (CLAUDE.md exception (c)).

## Prediction
*Written 2026-10-04 22:21 UTC, before running on this period (the card's rule, written 22:05 UTC).* Per event: **supported** if MJ (newcomer read coupling fitted on F37) beats MC (constant shift fitted on F37) on the incumbents' P12 calls (ΔLL CI > 0) and also beats the in-flight model MJ_pl; **failed** (kill) if MC beats MJ (CI < 0); **mixed** if the ΔLL CI includes 0 (inconclusive, synthetic power quoted) or MJ does not beat MJ_pl; **descriptive** if P12 has < 200 incumbent calls with a newcomer read. Regime II/III: H67's per-read coupling is small (≈ 0.008 per read; named 0.08), so MJ beats MC only if newcomer reads vary enough call to call (card P7, credence 0.25).

## Result
| Event | incumbents | P12 calls (with newcomer read) | ΔLL MC−MJ [95%] | ΔLL MJ_pl−MJ | ΔLL M_same−MJ | ΔLL M0−M0D | J_N F37 [95%] | J_N P12 [95%] | δ F37 | R²_h MC / MJ | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J2026-07-17 | 21 | 33335 (447) | -10.42 [-14.18, -7.31] | +0.28 [-0.02, +0.63] | +0.21 [-0.06, +0.51] | -0.05 [-0.10, -0.01] | +0.623 [+0.244, +0.871] | +0.530 [+0.330, +0.781] | +0.34 | 0.40 / 0.03 | failed |
| J2026-07-24 | 25 | 42005 (2581) | -0.85 [-1.71, -0.00] | -0.24 [-0.34, -0.13] | -0.29 [-0.49, -0.10] | -0.03 [-0.05, -0.02] | -0.052 [-0.172, +0.026] | +0.088 [-0.016, +0.174] | -0.24 | 0.56 / 0.03 | failed |

ΔLL in nats per 1,000 incumbent calls on days 1–2 (positive: the second model is better). J in logit per newcomer read. Data: `data/processed/H122-batch-join-spin-addition/results/events.parquet`.

## Scorecard (period-specific axes)
C (held-out days 1–2), D (F37 couplings applied back), E (the join as an intervention).

## Notes
