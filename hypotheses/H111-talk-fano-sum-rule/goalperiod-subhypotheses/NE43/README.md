# H111 × NE43: the operator's synchronizing drive is removed (#51: 51f → 51g → 51h, 2026-07-29 → 08-27)

**Verdict:** supported
**Role:** native (exploratory)
**Period:** goal #51 · 27 agents · regime III. 51f (07-29 → 08-04: daily pause/resume bookends and nudges), 51g (08-05 → 08-21: no bookends, nudges until 08-20; rooms #general and #focus), 51h (08-24 → 08-27: no bookends, no nudges).

## Why this period
Two scheduler steps at a near-fixed roster and a flat read-out gain (H67: g_lag ≈ 0.14 over #51). Step (a), 08-05: the daily bookends stop, removing a synchronizing drive at day edges. Step (b), after 08-20: the nudger stops; nudges target single idle agents (a private input). If trimming removes the scheduler field, the trimmed Φ should not move at either step, while the untrimmed Φ should drop at step (a).

## Prediction
*Written 2026-10-04 21:30 UTC, before running on these units. Seen: H67's G51 results (g_lag flat), H36's and H39's NE43 notes. No H111 statistic.*
- **N43a (trim removes the scheduler):** trimmed Φ(15) changes by less than 0.15 from 51f to 51g and from 51g to 51h. [0.5]
- **N43b (the bookends were a field):** the untrimmed − trimmed gap of Φ(15) is smaller in 51g than in 51f. [0.45]
- **Counts against:** trimmed Φ moves by ≥ 0.3 at either step (trimming leaves scheduler field in).

## Result
*Run 2026-10-04 ~21:45 UTC.*

| Unit | windows | Φ(10) [95%] | Φ_pred | r_F | untrimmed − trimmed (per-call) | (wall) |
| --- | --- | --- | --- | --- | --- | --- |
| 51f | 182 | 1.46 [1.15, 1.74] | 1.30 | 1.13 | +0.06 | +0.23 |
| 51g | 523 | 1.45 [1.27, 1.66] | 1.36 | 1.06 | -0.09 | -0.05 |
| 51h | 114 | 1.53 [1.17, 1.96] | 1.96 | 0.78 | -0.25 | -0.23 |

- **N43a** (trimmed Φ moves < 0.15 at both steps): -0.01 (bookends stop), +0.08 (nudger off). **Supported.**
- **N43b** (the untrimmed excess shrinks when the bookends stop): per-call +0.06 → -0.09; wall clock +0.23 → -0.05. **Supported.**
- **Reading:** the operator's daily pause/resume drive added about +0.23 of untrimmed wall-clock collective variance in 51f and none after it stopped; the trimmed per-call Φ did not move at either step. Trimming removes the scheduler field the bookends created, and nudges (private inputs) leave Φ unchanged. Caveat: 51g also opens a second room (#focus).

## Scorecard (period-specific axes)
E: the change across both scheduler steps.

## Notes
