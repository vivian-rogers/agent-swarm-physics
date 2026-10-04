# H04 × NE44: the pause default changes from 12 h to 5 min (2026-06-11; compared across non-holdout periods)

**Verdict:** mixed
**Role:** native (round 1b, non-holdout; transition exception c; the change date itself lies inside the locked NE21+NE23 window, which is not touched)
**Period:** regime III. **Before:** #36 (from 03-24) → #44, 4 h days, two rooms (266 nudges). **After:** #51 non-holdout days, 8 h, one room (729 nudges). The 06-08 → 07-06 holdout window, which contains the change date, is excluded. Confounded with hours (4 h vs 8 h), rooms, roster and era, and with NE22 (200-event cap, same day).

## Why this unit
DQ9 and H35: before 06-11 a directed message woke a pausing agent at any trap age; after it, agents read at the next short timer gate. H04-R1 / H08 say the scaffold is the propagator: the response kernel's dead time is the wait until the next call reads the message, plus whatever comes after the read-out. If that is right, a scheduler change that moves the read-out should move the onset of the activity response by the same amount, leaving the post-read-out lag unchanged.

## Prediction
*Written 2026-10-04 06:46 UTC, before any round-1b run (round 1 pooled regime III without this split and without read-out times).*
For every nudge (leading @ target), the read-out delay r = ledger `age_s` at the target's receiving call. Response: H04's corrected kernel (round 1b design: `activity_bins_fixed`, no future isolation, past-only controls, day fixed effect), and the onset t₂₅ = first minute at which the cumulative response reaches 25% of A30.
- **N44a (read-out moves):** the median r differs before vs after, shorter before (wake-on-message) than after (read at the next 5-min gate).
- **N44b (dead time = read-out + a constant):** t₂₅ − median r is the same before and after within ±2 min.
- **N44c:** in both regimes the response starts at the receiving call: in nudges stratified by r (≤ 1, 1–3, 3–10, > 10 min), the onset tracks r with slope ≥ 0.5.

**Verdict rule (fixed now):** supported if N44a and N44b hold; failed if N44a holds but the onset does not move (|Δt₂₅| < 1 min while |Δ median r| ≥ 2 min); mixed otherwise.

## Result
*Run 2026-10-04 (`analysis/r1b.py --suite III_4h_pre_NE44 / G51`; `data/processed/H04-reversible-forcing/r1b/`). Before = #36 (from 03-24) → #44, 48 days, 263 nudges; after = #51 non-holdout, 45 days, 729 nudges.*

| Statistic | before NE44 (12 h default pause) | after NE44 (5 min) |
| --- | --- | --- |
| read-out delay, median (q25–q75) | 43 s (8–165) | 108 s (30–223) |
| receiving call after a pause (share) | 38% | 73% |
| receiving call is an early wake | 0% | 0% |
| target A30 | +0.93 [+0.25, +1.67] | +1.16 [+0.75, +1.57] |
| onset t₂₅ from the nudge | 8 min [4.0, 13.0] | 7 min [5.0, 10.0] |
| t₂₅ − median read-out | 7.3 min | 5.2 min |
| onset t₂₅ from the receiving call | 2 min [1.0, 3.0] | 1 min [1.0, 3.0] |

Kernels by read-out delay bin (median read-out · onset · A30):

| read-out bin | before | after |
| --- | --- | --- |
| le1m | 9 s · t₂₅ 3 · A30 +1.58 (n 127) | 14 s · t₂₅ 4 · A30 +1.90 (n 246) |
| 1to3m | 116 s · t₂₅ 4 · A30 +1.10 (n 58) | 112 s · t₂₅ 4 · A30 +1.55 (n 223) |
| 3to10m | 304 s · t₂₅ 19 · A30 +1.15 (n 39) | 264 s · t₂₅ 15 · A30 +0.31 (n 206) |
| gt10m | 1278 s · t₂₅ None · A30 -5.42 (n 18) | 1109 s · t₂₅ None · A30 -3.77 (n 22) |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N44a: median read-out shorter before | 43 s vs 108 s | pass |
| N44b: t₂₅ − median read-out equal within ±2 min | 7.3 vs 5.2 min (Δ 2.1; t₂₅ CIs ±4 min). Measured from the receiving call: 2 vs 1 min | fail by 0.1 min on the letter; equal on the receiving-call alignment |
| N44c: onset tracks read-out (slope ≥ 0.5) | onsets 3, 4, 19 min (before) and 4, 4, 15 min (after) for read-outs of about 0.2, 1.9 and 5 min | pass (slope about 3: paused targets respond late and weakly) |

- **Mechanism correction (for H35 and NE44's catalog note):** no nudge read-out in either regime is an early wake. Before 06-11, read-outs were shorter because fewer targets were mid-pause when nudged (38% vs 73% of receiving calls follow a pause), not because a nudge woke a sleeping agent.
- Targets whose read-out took > 10 min are far *less* active than their matched controls (A30 −5.4 before, −3.8 after): long pauses are not in the matching strata, so those cells measure the pause, not the nudge.

**Verdict: mixed** (N44a and N44c hold; N44b misses its band by 0.1 min on the pre-registered alignment).

## Notes
- 2026-10-04: folder created with the prediction (round 1b native layer, DQ9 cross-index).
