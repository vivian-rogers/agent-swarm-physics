# H140 × G16: O2 read-weight check in chat mode (#16, 2025-10-06 → 10-10)

**Verdict:** descriptive
**Role:** exploratory (replication, O2 only, descriptive)
**Period:** regime I · chat mode · 7 agents · one room · 5 days.

## Why this period
H113 field-identified in gte. There are no computer-use context segments in chat mode, so the self-share s_self does not exist and O1 (the self-weight law) is untestable here, as the card states. Only the read-weight exponent (O2) is fitted, with p = the mean of the reader's last two same-day statements as a regressor (segment = PT day).

## Prediction
*Copied from the card and dated 2026-10-07 08:55 UTC (system clock), before running on this period.*
- **P2 (descriptive):** â ∈ [0.15, 0.40] with CI excluding 1. Counts against: â's CI includes 1 or â ≥ 0.7. Descriptive only; it does not enter the card's pooled kill.

## Result
Data: `data/processed/H140-degroot-readout-self-weight/G16/`, results `results/reg12.json`. Run 2026-10-07 (exploration data; reserved days never enter the scheme). Estimator: Amendment A1 spec (primary) and the registered spec; agent-day cluster bootstrap, 300 draws.

O2 only (spec A1 without the s_self and call-gap terms; p = mean of the reader's last two same-day statements; 1,751 rows).

| Observable | Observed | Verdict |
| --- | --- | --- |
| â (bge; gte) | 0.24 [0.05, 0.42]; gte 0.20 [0.02, 0.38] | descriptive (in band, CI excludes 1) |
| identification | bge contrast CI includes 0 (not identified); gte identified (contrast 0.024, lower bound 0.002; r 0.61) | |

Kill clause 2 (â ≥ 0.7 or CI includes 1) does not fire here. The self-weight law is untestable in chat mode.

## Scorecard (period-specific axes)
C 1 (O2 only), H 1 (beats R-linear and R-capacity).
