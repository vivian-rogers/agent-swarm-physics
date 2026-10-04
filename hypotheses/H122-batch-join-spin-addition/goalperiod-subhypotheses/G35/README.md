# H122 × G35: join event(s) in goal period #35

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** join event(s) whose day 1 falls in goal #35:
- **J2026-03-16** (GPT-5.4; regime II): PRE 2026-03-02 … 2026-03-04 (3 d), P12 2026-03-16, 2026-03-17, F37 2026-03-18 … 2026-03-23 (4 d). Regime II; PRE is #33 (03-02 … 03-04) because NE30 (03-05 … 03-15) is held out; F37 reaches #36 (03-23).

## Why this period
Each eligible non-holdout join is one replica of a spin addition (card, layer 1). The transition is the object (CLAUDE.md exception (c)).

## Prediction
*Written 2026-10-04 22:21 UTC, before running on this period (the card's rule, written 22:05 UTC).* Per event: **supported** if MJ (newcomer read coupling fitted on F37) beats MC (constant shift fitted on F37) on the incumbents' P12 calls (ΔLL CI > 0) and also beats the in-flight model MJ_pl; **failed** (kill) if MC beats MJ (CI < 0); **mixed** if the ΔLL CI includes 0 (inconclusive, synthetic power quoted) or MJ does not beat MJ_pl; **descriptive** if P12 has < 200 incumbent calls with a newcomer read. Regime II/III: H67's per-read coupling is small (≈ 0.008 per read; named 0.08), so MJ beats MC only if newcomer reads vary enough call to call (card P7, credence 0.25).

## Result
| Event | incumbents | P12 calls (with newcomer read) | ΔLL MC−MJ [95%] | ΔLL MJ_pl−MJ | ΔLL M_same−MJ | ΔLL M0−M0D | J_N F37 [95%] | J_N P12 [95%] | δ F37 | R²_h MC / MJ | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J2026-03-16 | 10 | 14239 (68) | -7.89 [-11.17, -4.91] | -0.05 [-0.12, +0.02] | -0.07 [-0.14, -0.01] | +0.03 [+0.02, +0.04] | +0.334 [-0.191, +0.763] | -0.484 [-1.469, +0.124] | -0.62 | 0.93 / -0.01 | descriptive |

ΔLL in nats per 1,000 incumbent calls on days 1–2 (positive: the second model is better). J in logit per newcomer read. Data: `data/processed/H122-batch-join-spin-addition/results/events.parquet`.

## Scorecard (period-specific axes)
C (held-out days 1–2), D (F37 couplings applied back), E (the join as an intervention).

## Notes
