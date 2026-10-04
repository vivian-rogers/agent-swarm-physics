# H45 × NE03: chat messages fetched into context limited (2025-08-20)

**Verdict:** failed (no change at NE03: chat-mode prompts were already flat in the day's traffic before and after; the scaffold cap holds throughout)
**Role:** native
**Period:** regime I chat mode. Before: 2025-08-04 → 08-12 (#8) and 08-18 → 08-19 (#10a); #9 (08-13 → 08-15) is held out and excluded. After: 08-20 → 08-29 (#10b, #11). Spans a goal boundary by design (the transition is the object; CLAUDE.md exception c).

## Why this period
This is the scaffold rival in its purest form. In regime-I chat mode the scaffold rebuilt each call's prompt from the recent chat, and on 2025-08-20 it "limited the number of chat messages fetched into context" (CHANGELOG [Memory]; limit not documented). If the room share of a chat-mode context is set by the scaffold, the prompt should grow with the day's room traffic before the change and stop growing beyond a ceiling after it, whatever the agents do.

## Prediction
*Written 2026-10-04 06:32 UTC, before running any NE03 statistic.*
- **S1 (ceiling after NE03):** within agent-day, the slope of chat-mode P on m_day (room messages posted by others earlier the same day), in the upper half of each day's m_day, falls after 08-20 to ≤ 0.5 × its value before.
- **S2 (growth before):** before 08-20 the upper-half slope is > 0 (CI excludes 0): the prompt keeps growing with the day's traffic.
- **S3 (reading):** if S1 and S2 hold, the chat-mode room share is set by the scaffold's fetch window, not by the agents (the scaffold-capped class of the card).
- **Against the scaffold rival:** similar slopes before and after.
- **Confounds:** new agents and expanded hours on 08-18 (NE27); within-agent comparisons for agents present on both sides.

## Result
Chat-mode calls with prompt tokens: 1,390 before, 2,398 after; 7 agents on both sides (agent codes 0, 5, 6, 8, 9, 10, 11). Slopes of P on m_day within agent-day, day-bootstrap CIs.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| S2: before NE03, upper-half slope > 0 | 3.9 [−3.1, 7.0] tokens per message (m median 113; P median 8.2k) | ≈ 100–150 tokens per message if the day's chat accumulated in the prompt (calibrated ≈ 50 per item + 0.3 per character) | not met |
| S1: after/before upper-half slope ≤ 0.5 | after 4.6 [0.8, 8.6] (m median 294; P median 9.9k); ratio 1.19 | – | not met |
| S3: chat-mode share set by the scaffold | prompt size is flat in the day's traffic on both sides: binned medians 7.5k–9.5k (before, m 0–180) and 9.0k–10.7k (after, m 0–400) | – | supported descriptively |

**Reading.** NE03 is invisible in the prompt sizes. Before and after 2025-08-20, a regime-I chat-mode prompt stays near 8–10k tokens however many messages the room has posted that day: the recent-chat window was already bounded before the documented limit (or the limit was set above the traffic of these days). The predicted change failed, but the broader scaffold-rival reading holds for chat mode: there the room share of context is fixed by the scaffold's window, and the agent has no lever at all. The median prompt rose slightly after 08-20 (8.2k → 9.9k), which is the opposite of a tighter limit; the 08-18 roster and hours change (NE27) confounds it.

Data: `data/processed/H45-context-homeostasis/NE03/native.json`.

## Scorecard (period-specific axes)
- **E:** the documented scaffold change produced no measurable change (0 of 2 predictions).
- **G:** a known structure (chat mode rebuilds the prompt from a bounded recent-chat window, DQ1 notes) agrees with flat prompt sizes.

## Notes
- 2026-10-04 06:32 UTC: prediction written before the run. Anthropic chat-mode `tokens_in` look like full prompt totals in regime I (median 12.5k; the uncached-only pattern appears only in computer-use mode), so all labs are used here.
- 2026-10-04: results from `analysis/natives.py` (NE03).
