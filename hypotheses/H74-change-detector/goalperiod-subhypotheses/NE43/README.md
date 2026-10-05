# H74 × NE43: the automated speaker winds down in two steps (#51; 2026-08-05 and 2026-08-21)

**Verdict:** mixed
**Verdict (r2):** supported
**Role:** native
**Period:** regime III · #51 · 27 agents · #general (+ #focus 08-05 → ~08-24) · units 51f–51h.

## Why this period
Two undocumented operator steps inside one long period with a dense, stable baseline. The bookends stop after 08-04 (first day without: 08-05, the same day #focus opens) and the nudges after 08-20 (first day without: 08-21). Channel D carries the bookend and nudge counts directly, so this is a recovery test of the drive channel and a specificity test for the rest of #51.

## Prediction
*Written 2026-10-04 20:30 UTC, after the synthetic study and before any real-data detector score.*
- **NE43a (08-05):** a fused alarm on day −1..+1 [0.75], carried by channel D (bookend count 2 → 0) [0.7].
- **NE43b (08-21):** a fused alarm on day −1..+1 [0.8], carried by channel D (nudge count → 0) [0.75].
- **Specificity:** on the other non-holdout #51 days (07-06 → 09-04) that are ≥ 2 active days from both steps, from every roster join and from NE45, the fused per-day alarm rate is ≤ 0.15 [0.5].
- *Against:* no D alarm at either step, or alarms on > 30% of the quiet #51 days.

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H74-change-detector/native/results.json`, `scores.parquet`. Channel scores are window maxima over days −1..+1 (τ = 4).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| NE43a (08-05): fused alarm, carried by D | Z 8.0 on 08-05 (D: bookend count 2 → 0); S 0, M 2.2, O 2.6, C 2.2 | held |
| NE43b (08-21): fused alarm, carried by D | Z 9.0 on 08-20 (D: 18 human messages that day) and 6.9 on 08-21 (D: nudge count → 0) | held |
| Specificity: quiet #51 days alarm ≤ 0.15 | 2/7 quiet days (0.29; both channel O, answer line length, 08-12 and 08-14); #51 is so dense with events that only 7 days qualify | failed (n = 7) |

Both undocumented operator steps are dated to the day by the drive channel's plain counters. The rest of #51 is noisy in the oracle-format channel.

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readout (card: Round 2, D3 counters with two-day persistence, LOPO threshold).
| Step | D3 window max | Threshold | Outcome |
| --- | --- | --- | --- |
| NE43a (08-05, bookends stop) | 11.0 | 2.76 | alarm |
| NE43b (08-21, nudges stop) | 10.1 | 2.76 | alarm |

Both steps alarm with one day of delay (persistence). Round-2 verdict: supported.
<!-- /R2 -->

## Scorecard (period-specific axes)
- G (ground truth): both dated steps recovered on the correct day.
- C (adequacy): specificity on quiet #51 days not met (2/7).
