# H74 × NE40: search-oracle swap shipped with NE18 (#38; 2026-04-20)

**Verdict:** failed
**Verdict (r2):** mixed
**Role:** native
**Period:** regime III · #38 · 13 agents · #best / #rest · unit 38d.

## Why this period
The history-search answerer changed (Gemini 2.5 Pro → Sonnet 4.6) silently on the day of the documented NE18 search rework. The oracle-format channel O sees the answers only through generic format counts. Disclosure: H56 dated the swap with bullet-marker counts, which O includes among 17 generic counts, so this is a recovery test, not a discovery.

## Prediction
*Written 2026-10-04 20:30 UTC, after the synthetic study and before any real-data detector score.*
- **04-20:** channel O fires within day −1..+1 [0.7]; channel S also fires (NE18 changes the search tool's arguments) [0.5].
- **03-31 / 04-01 (search outage, near-empty answers, #37):** channel O fires [0.6].
- *Against:* no O alarm within ±1 day of 04-20.

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H74-change-detector/native/results.json`, `scores.parquet`. Channel scores are window maxima over days −1..+1 (τ = 4).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| O fires within ±1 day of 04-20 | O max 2.8 (04-17 → 04-21); generic day medians of format counts do not move | failed |
| S fires at 04-20 (NE18 search rework) | S = 0 on 04-17 … 04-21: the NE18 rework kept the tool's field names and types | failed |
| O fires at the 03-31 / 04-01 search outage | O = 4.3 on 04-01 (mean line length); the fused window is 102.8 through D on 03-31 (an unusual day window containing a 513-min village-off gap) | held |

The fused alarm does fire in the 04-20 window (Z 7.5 on 04-21), but through channel M (Anthropic cache-read share), which has nothing to do with the oracle. It is not a recovery. *Post hoc (not used for the verdict):* day means instead of medians also miss it (O 1.4). The marker H56 used is present on 55/61 days and then absent. A trailing z does not see a disappearance well; a presence/retirement rule, as in channel S, would.

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readout (card: Round 2, R2 presence rule; a recovery, not blind).
| Rule | P2 false alarms (scored search days) | NE40 (04-20) |
| --- | --- | --- |
| accumulating retirement (primary, Amendment R2-A1) | 0/37 | first alarm 04-22, 2 scored days late (bullet markers `*`, 3-space `*`); outside ±1 |
| one-day retirement (pre-registered) | 1/37 | alarm on 04-20 (same markers) |
| appearance (secondary) | 0/37 | alarm on 04-20 (h2, `-` bullets, an opening-phrase class appear) |

The 03-31 search outage is not seen by any presence rule. Round-2 verdict: mixed (the primary rule dates the swap 2 days late at 0 false alarms; the pre-registered and appearance rules date it to the day).
<!-- /R2 -->

## Scorecard (period-specific axes)
- G: the oracle swap is not recovered by the generic format channel.
- F: the channel's design (day medians, trailing z) is blind to the disappearance of a minority marker.
