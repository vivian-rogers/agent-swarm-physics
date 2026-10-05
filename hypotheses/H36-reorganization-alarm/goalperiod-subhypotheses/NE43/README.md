# H36 × NE43: The automated speaker winds down in two steps (bookends end 08-05, nudges end 08-21; inside #51)

**Verdict:** failed (native, round 1b)
**Verdict (1b):** failed (nudger-off day not silent: Z_act 3.1, R1 2.1–2.2)
**Role:** native
**Period:** regime III · #51 (private-role era) · N ≈ 25–29 · one main room. **Step a:** the daily pause/resume bookends stop after 2026-08-04 PT (day 0 = 08-05, which is also the day the #focus room opens: a room event in H36's catalog). **Step b:** nudges stop after 2026-08-20 (day 0 = 08-21). Dates corrected by H35 and `kicks_classified` (NE catalog, 2026-10-04); undocumented in the CHANGELOG.

## Why this period
DQ9's leverage for H36: a drive withdrawal at a fixed goal, roster and room, in two steps. Round 1 had neither step in its catalog. The round-1b fixes say activity co-movement is the runner's day-edge field (RE-A1, H50) and that agents still start together after the bookends stop (H38 1b), so the activity channel should *not* react to step a; step b removes a lever that wakes about 1% of agent-minutes (H35).

## Design (round 1b native test)
Daily scores from the round-1b replication (fixed activity bins and outages, both models): Z_phys, Z_act, Z_cont, R1, C3. Hit = score ≥ threshold on day −1, 0 or +1. Blind dating within #51's non-holdout active days, excluding ±1 day around other catalogued events (NE32, NE38/NE45, the side room, NE33). Step a is reported with the #focus confound.

## Prediction
*Written 2026-10-04 07:50 UTC, before any round-1b score was computed.*
- **N2a (step b, 08-21):** no alarm on Z_phys, Z_cont or R1 (all < 2 on −1..+1) [0.7]; Z_act |z| < 2 on day 0 [0.7].
- **N2b (step a, 08-05):** some content alarm (Z_cont, R1 or C3) on −1..+1 [0.5], attributable to the #focus room opening; Z_act |z| < 2 on day 0 [0.65] (the bookends do not set the activity field).
- **Reading:** silence at step b and at step a's activity channel → the alarm is not driven by the operator's message drive; the runner's schedule, unchanged by NE43, is what makes agents co-active.

## Result
<!-- R1B -->
**NE43a** (day 0 2026-08-05, #51; same day: NE-focus,NE43a; 25 candidate days for blind dating), bge:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | -0.11 | 0.52 | 0.27 | no | no | 0.68 |
| Z_act | 0.27 | 0.40 | 0.60 | no | no | 0.60 |
| Z_act_trim | 1.24 | 1.54 | 1.60 | no | no | 0.88 |
| Z_cont | -0.27 | 0.76 | -0.10 | no | no | 0.80 |
| R1 | 1.93 | -0.89 | 1.80 | no | no | 0.92 |
| C3 | 0.93 | 0.76 | 0.80 | no | no | 0.84 |

**NE43a** (day 0 2026-08-05, #51; same day: NE-focus,NE43a; 25 candidate days for blind dating), gte:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | 0.34 | 0.23 | 0.29 | no | no | 0.64 |
| Z_act | 0.27 | 0.40 | 0.60 | no | no | 0.60 |
| Z_act_trim | 1.24 | 1.54 | 1.60 | no | no | 0.88 |
| Z_cont | 0.69 | 0.16 | -0.01 | no | no | 0.84 |
| R1 | 2.42 | -1.13 | 0.72 | yes | no | 0.96 |
| C3 | 1.42 | 0.16 | -0.01 | no | no | 0.96 |

**NE43b** (day 0 2026-08-21, #51; same day: NE43b; 25 candidate days for blind dating), bge:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | -0.08 | 1.45 | 0.75 | no | no | 0.92 |
| Z_act | -0.72 | 3.10 | 0.98 | yes | no | 0.96 |
| Z_act_trim | 0.06 | 3.88 | -0.37 | yes | no | 0.92 |
| Z_cont | 0.53 | -0.50 | 0.49 | no | no | 0.76 |
| R1 | 0.28 | 2.22 | 1.10 | yes | no | 0.92 |
| C3 | 0.53 | 1.22 | 0.49 | no | no | 0.88 |

**NE43b** (day 0 2026-08-21, #51; same day: NE43b; 25 candidate days for blind dating), gte:

| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |
| --- | --- | --- | --- | --- | --- | --- |
| Z_phys | 0.10 | 1.89 | 0.84 | no | no | 0.96 |
| Z_act | -0.72 | 3.10 | 0.98 | yes | no | 0.96 |
| Z_act_trim | 0.06 | 3.88 | -0.37 | yes | no | 0.92 |
| Z_cont | 0.86 | 0.27 | 0.80 | no | no | 0.84 |
| R1 | 0.37 | 2.07 | 0.95 | yes | no | 0.92 |
| C3 | 0.86 | 1.07 | 0.80 | no | no | 0.88 |
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Intraday timing of the #focus room, 08-05 (card: Round 2, P2.4; native, exploratory). Room created 16:36 UTC; first agent move 17:39 UTC (window 3; day window opened 16:00 UTC).

| Event | event window | intraday z near the event, bge | gte |
| --- | --- | --- | --- |
| #focus first move | window 3 | w2: 2.25, w3: 0.70, w4: 1.71 | w2: 3.24, w3: 0.38, w4: 1.91 (alarm) |
| side-room 07-24 (#51) | window 9 | w8: -0.40, w9: -0.20, w10: -0.86 | w8: -0.16, w9: -0.19, w10: -1.11 |

Prediction (alarm within ±1 window of the first move) [0.35]: **mixed**: gte alarms in window 2 (z 3.2, between the room's creation and the first move); bge peaks there at 2.3, below the threshold. Side-room silent, as predicted [0.7].
<!-- /R2 -->
