# H74 × NE14: the regime II → III boundary (#36; scored at 2026-03-24)

**Verdict:** supported
**Role:** native
**Period:** regime II → III · #36 · 12 agents · #best / #rest · units 36a → 36b.

## Why this period
The largest documented platform change in the non-holdout data: perma-computer-use, the consolidate tool and timer pauses replace sessions. Event types change on the day. A positive control for the platform channels; H56 (EP) and H36 (fluctuations) both missed it.

## Prediction
*Written 2026-10-04 20:30 UTC, after the synthetic study and before any real-data detector score.*
- **03-24:** fused alarm [0.9]; channel S fires (session events retire, CONSOLIDATE/PAUSE signatures appear or change share) [0.8]; channel M fires (call-kind shares jump synchronously) [0.75]; channel C need not fire (no goal change) [0.6 that z_C < 4].
- *Against:* no platform-channel alarm at the biggest scaffold change.

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H74-change-detector/native/results.json`, `scores.parquet`. Channel scores are window maxima over days −1..+1 (τ = 4).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| fused alarm on 03-24 | Z 16 | held |
| S fires | S = 16: new tool-call signatures (`pause` with `seconds`; `search_history` with `startDay/endDay/query`), new CONSOLIDATE event signature, WAIT events retire | held |
| M fires | M max 2.6 (session-stop and consolidate shares); below τ, because agents' own baselines contain the 03-11 → 03-23 staggered rollout | failed |
| C < 4 | C 1.8 | held |

The largest platform change in the non-holdout data, which EP (H56) and the fluctuation alarm (H36) missed, is dated to the day by the schema channel alone.

## Scorecard (period-specific axes)
- E (interventional): a documented scaffold intervention is detected on its day by the channel built for it.
- G: agrees with the CHANGELOG and H56's event-type switch.
