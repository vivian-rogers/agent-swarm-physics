# H103 × NE41: context resets inside the day as demagnetizing steps (regime III)

**Verdict:** supported
**Role:** native
**Period:** regime III · every eligible regime-III period unit · forced consolidations at the 41-call cap plus voluntary consolidations and session starts (`context_ledger_turns`).

## Why this period
In regime III the context is erased every ~41 calls inside the day, while it mostly carries over the night (H69). If HH331's mechanism (consolidation and erasure) demagnetizes content, each reset should lower an agent's self-overlap at fixed active lag.

## Prediction
*Written 2026-10-04 21:45 UTC, before running (card N2).*
- The within-day reset term β_R (per own reset between two windows, at fixed active-lag bins) has an RE mean with a CI that includes 0 and |β_R| < 0.005 [0.55] (H46: content does not move at erasures).
- *Against:* β_R < 0 with the CI excluding 0. Verdict: *supported* (no reset effect) if the CI includes 0 and |β_R| < 0.005; *failed* if the CI is below 0; *mixed* otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 15 regime-III units.

| Statistic | bge | gte |
| --- | --- | --- |
| β_R RE mean (per own reset, same-day pairs) | +0.0003 [-0.0011, +0.0018] | +0.0008 [-0.0003, +0.0020] |

Per unit (bge): 37 +0.0108 [-0.0057, +0.0227]; 38a +0.0005 [-0.0060, +0.0095]; 38b +0.0052 [-0.0015, +0.0127]; 38e +0.0061 [-0.0038, +0.0177]; 39 -0.0033 [-0.0092, +0.0047]; 40 +0.0027 [-0.0020, +0.0094]; 41 -0.0114 [-0.0233, +0.0020]; 42b -0.0083 [-0.0140, -0.0037]; 51a -0.0002 [-0.0020, +0.0018]; 51c +0.0010 [-0.0010, +0.0027]; 51d +0.0014 [-0.0005, +0.0057]; 51e +0.0005 [-0.0016, +0.0038]; 51f +0.0027 [-0.0012, +0.0056]; 51g +0.0008 [-0.0015, +0.0035]; 51h -0.0006 [-0.0055, +0.0029]

**Verdict (card N2 rule):** bge supported; gte supported.
