# H140 × G13: O2 read-weight check in chat mode (#13, 2025-09-08 → 09-19)

**Verdict:** descriptive
**Role:** exploratory (replication, O2 only, descriptive)
**Period:** regime I · chat mode · 6 agents · one room · 10 days.

## Why this period
H113 field-identified in bge. There are no computer-use context segments in chat mode, so the self-share s_self does not exist and O1 (the self-weight law) is untestable here, as the card states. Only the read-weight exponent (O2) is fitted, with p = the mean of the reader's last two same-day statements as a regressor (segment = PT day).

## Prediction
*Copied from the card and dated 2026-10-07 08:55 UTC (system clock), before running on this period.*
- **P2 (descriptive):** â ∈ [0.15, 0.40] with CI excluding 1. Counts against: â's CI includes 1 or â ≥ 0.7. Descriptive only; it does not enter the card's pooled kill.

## Result
Data: `data/processed/H140-degroot-readout-self-weight/G13/`, results `results/reg12.json`. Run 2026-10-07 (exploration data; reserved days never enter the scheme). Estimator: Amendment A1 spec (primary) and the registered spec; agent-day cluster bootstrap, 300 draws.

O2 only (spec A1 without the s_self and call-gap terms; p = mean of the reader's last two same-day statements; 4,327 rows).

| Observable | Observed | Verdict |
| --- | --- | --- |
| â (bge; gte) | 0.28 [0.16, 0.38]; gte 0.24 [0.12, 0.36] | descriptive (in band, CI excludes 1) |
| identification | contrast 0.025 (CI > 0), r 0.59: identified in bge; gte contrast 0.021 (CI > 0), r 0.62: identified | |

Kill clause 2 (â ≥ 0.7 or CI includes 1) does not fire here. The self-weight law is untestable in chat mode.

## Scorecard (period-specific axes)
C 1 (O2 only), H 1 (beats R-linear and R-capacity).
