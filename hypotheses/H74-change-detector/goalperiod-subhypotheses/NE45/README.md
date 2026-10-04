# H74 × NE45: history-search tool schema change (#51; 2026-07-29)

**Verdict:** supported
**Role:** native
**Period:** regime III · #51 · 27 agents · #general · unit 51f.

## Why this period
An undocumented tool-interface change (date fields startDay/endDay as integers become startDate/endDate as strings) inside #51, which also has eleven roster joins of several providers. A recovery test of the schema channel (S) and a specificity test of its newcomer and two-agent rules. Disclosure: H56 found this change by hand, so S is not blind to it.

## Prediction
*Written 2026-10-04 20:30 UTC, after the synthetic study and before any real-data detector score.*
- **07-29:** channel S fires within day −1..+1 (a new SEARCH_HISTORY signature and the retirement of the old one) [0.85].
- **Roster joins in #51 (11 non-holdout joins):** platform-wide S alarms at ≤ 2 of them [0.6] (new providers bring new API shapes, but only one or a few agents carry them in their first days).
- *Against:* no S alarm on 07-29, or S alarms at most #51 joins.

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H74-change-detector/native/results.json`, `scores.parquet`. Channel scores are window maxima over days −1..+1 (τ = 4).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| S fires on 07-29 | S = 12 on 07-29: the SEARCH_HISTORY signature with integer `startDay/endDay` retires, and new event and tool-call signatures with string `startDate/endDate` appear (field names and types only) | held |
| S alarms at ≤ 2 of 8 #51 roster-join days | 1/8 (the 07-10 join window, carried by the 07-13 change in the OpenAI response format of incumbent agents, not by the newcomers) | held |

The fused window score is 26.8, but that maximum comes from D on 07-28: a long window with a 36% joint-silence share, an unrelated operations event. The schema channel names the change exactly.

## Scorecard (period-specific axes)
- G: the undocumented schema change is recovered on the day, with the renamed fields listed.
- C: the newcomer rule keeps roster joins quiet (1/8).
