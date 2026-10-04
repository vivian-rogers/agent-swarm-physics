# H92 × G38: Choose a charity and raise money (2026-04-02 → 2026-04-24), two rooms

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime III · 12 → 14 agents · two rooms (#best, #rest) with room-specific kickoffs · 17 days · units 38a (8 days), 38b (3), 38c (1), 38d (2), 38e (3), split at NE17, NE18 and roster joins.

## Why this period
The longest two-room unit (38a) with room-specific instructions (H47): the agent correlation matrix should carry a room block next to the uniform mode. Clipping keeps a mode only above the calibrated edge. This period tests whether random-matrix cleaning keeps or erases the room structure an operator cares about.

## Prediction
*Written 2026-10-04 ~20:12 UTC, before running on this period. Credences in brackets.*
- **N2a (sanity).** The realized talk room contrast (mean within-room minus between-room pair correlation, rooms = each agent's modal room that day) is > 0 on ≥ 2/3 of target days [0.7].
- **N2b (cleaning keeps rooms).** E5's predicted talk room contrast is ≥ 50% of E2's on ≥ 2/3 of target days [0.6], and E5's contrast error is ≤ E2's on ≥ 2/3 [0.5].
- **N2c (second mode).** In talk, E5 has a lower MSE than E4 on ≥ 2/3 of target days [0.5]. Content is reported with both models.
- **Counts against:** E5 keeps < 50% of the room contrast (cleaning deletes the room block) and loses to E4.
- **Verdict rule:** *supported* if N2b and N2c hold; *failed* if N2b's first clause and N2c both fail; *mixed* otherwise.

## Result
*Run 2026-10-04 ~20:38 UTC.* Room contrast = mean within-room minus mean between-room pair correlation (modal room per agent on the target day). Expanding training window within units 38a–38e.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| N2a talk room contrast > 0 on ≥ 2/3 days | 8/10; mean 0.036 | – | pass |
| N2b clip keeps ≥ 50% of raw's talk contrast on ≥ 2/3 days | 2/10 (median kept ≈ 0); calibrated edge keeps a median 0.5 talk modes | – | fail |
| N2b clip contrast error ≤ raw's on ≥ 2/3 days (talk) | 5/10 | – | fail |
| N2c clip MSE < LW-CC MSE in talk on ≥ 2/3 days | 3/10 | – | fail |
| Content (reported) | contrast > 0 on 12/12; clip keeps 78% (bge) / 89% (gte); predicted 0.069 / 0.081 vs realized 0.067 / 0.080; raw 0.100 / 0.110 | – | clipping keeps and de-biases the content room block |

In talk, the room block sits below the calibrated edge at a unit's day-level sample size, so clipping deletes it. In content, the room block survives cleaning, and the cleaned forecast of the room contrast is closer to the realized value than the raw one, which overshoots by about 40%.

**Replication numbers (common estimator):** 12 target days, median N 12; gain over raw 0.18 (bge) / 0.17 (gte); over LW-CC −0.01 / −0.00; best estimator LW identity.

Data: `data/processed/H92-rmt-cleaned-forecast/native/results.json`, `forecasts.parquet`.

## Scorecard (period-specific axes)
- G (ground truth): 1. The room assignment is the known structure: kept in content, erased in talk.
- H (comparative): 0 in talk (loses to shrinkage), 1 in content (ties).
