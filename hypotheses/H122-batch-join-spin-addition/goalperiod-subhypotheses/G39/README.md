# H122 × G39: join event(s) in goal period #39

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** join event(s) whose day 1 falls in goal #39:
- **J2026-04-27** (GPT-5.5; regime III): PRE 2026-04-20 … 2026-04-24 (5 d), P12 2026-04-27, 2026-04-28, F37 2026-04-29 … 2026-05-05 (5 d). F37 crosses NE42 (05-04: #best and #rest merge into one room for #40).

## Why this period
Each eligible non-holdout join is one replica of a spin addition (card, layer 1). The transition is the object (CLAUDE.md exception (c)).

## Prediction
*Written 2026-10-04 22:21 UTC, before running on this period (the card's rule, written 22:05 UTC).* Per event: **supported** if MJ (newcomer read coupling fitted on F37) beats MC (constant shift fitted on F37) on the incumbents' P12 calls (ΔLL CI > 0) and also beats the in-flight model MJ_pl; **failed** (kill) if MC beats MJ (CI < 0); **mixed** if the ΔLL CI includes 0 (inconclusive, synthetic power quoted) or MJ does not beat MJ_pl; **descriptive** if P12 has < 200 incumbent calls with a newcomer read. Regime II/III: H67's per-read coupling is small (≈ 0.008 per read; named 0.08), so MJ beats MC only if newcomer reads vary enough call to call (card P7, credence 0.25).

## Result
| Event | incumbents | P12 calls (with newcomer read) | ΔLL MC−MJ [95%] | ΔLL MJ_pl−MJ | ΔLL M_same−MJ | ΔLL M0−M0D | J_N F37 [95%] | J_N P12 [95%] | δ F37 | R²_h MC / MJ | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J2026-04-27 | 12 | 10317 (22) | -2.47 [-3.64, -1.33] | -0.04 [-0.23, +0.08] | -0.04 [-0.27, +0.11] | -0.04 [-0.07, -0.02] | +0.212 [-0.364, +0.553] | +0.004 [-1.026, +2.918] | -0.10 | 0.27 / -0.00 | descriptive |

ΔLL in nats per 1,000 incumbent calls on days 1–2 (positive: the second model is better). J in logit per newcomer read. Data: `data/processed/H122-batch-join-spin-addition/results/events.parquet`.

## Scorecard (period-specific axes)
C (held-out days 1–2), D (F37 couplings applied back), E (the join as an intervention).

## Notes
