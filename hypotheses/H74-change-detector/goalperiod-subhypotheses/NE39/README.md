# H74 × NE39: public chat closes (#6; ≈ 2025-07-01, undocumented)

**Verdict:** supported
**Role:** native
**Period:** regime I · #6 · unit G06.

## Why this period
Human messages per day fall from ~100–170 to ≤ 4 when the chat closes to the public. Round 1's Gaussian z on raw counts missed it. This is the test case of redirect H74-R3 (heavy-tailed baselines).

## Prediction
*Written in the card's Round 2 pre-registration (2026-10-05 03:50 UTC) and Amendment R2-A1 (~04:30 UTC), before any round-2 statistic. This folder was created after the run.*
- **P3.1** Q (empirical quantiles, 30 days) alarms on n_human within day −1..+1 of 07-01 at the LOPO-calibrated D threshold [0.75]; G (round-1 Gaussian z, raw) does not [0.8].
- Amendment R2-A1: the primary D channel became D3-L-p2 (log1p counts, Gaussian z, two-day persistence); P3.1 is read on it and on Q.

## Result
Human messages per day: 06-25 159, 06-26 98, 06-27 167, 06-29 26, 06-30 100, 07-01 4, 07-02 1, 07-03 1, 07-04 2.

| Score | NE39 window max | LOPO threshold | Outcome |
| --- | --- | --- | --- |
| G, six features, one day (round 1) | 8.0 | 11.4 | no alarm |
| Q, six features, one day (pre-registered primary) | 11.0 | 11.6 | no alarm |
| **D3-L-p2 (amended primary)** | **4.5** | **2.76** | **alarm** |

The log-count channel with persistence dates NE39 (alarm on 07-02, the second low day) at an out-of-sample per-day FAR of 1/82. Q does not: its threshold is set by heavy-tailed hours and silence features on placebo days. Round-2 verdict: supported on the amended channel; failed on the pre-registered Q.

## Scorecard (period-specific axes)
- G: the undocumented drive step is dated within one day.
- B: a log transform plus persistence handles the count tails; Q alone does not.
