# H80 × NE32: isolated newcomers (GPT-5.6 Sol, Terra, Luna join in separate rooms, 2026-07-09; merged 07-10)

**Verdict:** mixed
**Role:** native
**Period:** inside G51 (unit 51a/51b) · regime III · three newcomers, each alone in an onboarding room on day 1 · contrast arm: NE33 batch joiners (Muse Spark 1.3, Gemini 3.8 Flash, GPT-6 Astra, 09-03/04), who join #general directly.

## Why this period
The cleanest shared-prior test available. On day 1 the NE32 newcomers cannot read the village chat, so any high-index command motif they use comes from the model prior or from artifacts, not from chat transmission. NE33 joiners can read chat from their first call.

## Prediction
*Written 2026-10-04, before running on this period.*
- **Observable:** per agent-day, the share of sessions that contain ≥ 1 high-index, high-copy (HH-HC) command motif (a ≥ 6, ≥ 20 G51 sessions).
- **N1a:** NE32 newcomers' day-1 share ≥ 0.8 × the incumbents' share on 07-09 (prior). *Against:* < 0.5× (motifs learned in the village).
- **N1b:** NE32 and NE33 day-1 shares agree within a factor 1.5 (isolation does not matter). *Against:* NE33 > 1.5 × NE32 (chat transmits motifs).
- **N1c:** the share of HH-HC motifs used on day 1 by ≥ 1 NE32 newcomer is ≥ 0.5 of the share used by the three NE33 joiners on their day 1.

## Result
Data: `results/natives.json` (`NE32`).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N1a NE32 day-1 share ≥ 0.8 × incumbents on 07-09 | 1.65× (NE32 0.38 of 39 sessions, per agent 0.60, 0.55, 0.00, vs incumbents 0.23, 21 incumbents; incumbent bootstrap CI 0.11–0.33) | supported |
| N1b NE33 and NE32 day-1 shares within ×1.5 | NE33 joiners 0.00 (43 sessions) vs NE32 0.38 | failed (opposite to chat transmission) |
| N1c NE32 motif coverage ≥ 0.5 × NE33 | 3.9% vs 0.0% of the 562 motifs | supported |

Of the 22 high-index motifs the isolated newcomers used on day 1, 11 were already used by incumbents before 07-09, and 11 have users from non-OpenAI labs. Isolation does not delay them: they arrive with the agent. NE33 joiners use none because the motif set needs ≥ 20 session copies within G51, which joiners with 1–2 non-holdout days cannot build (a selection artifact, so N1b is uninformative).

## Scorecard (period-specific axes)
- E: 1. Isolation (no chat access on day 1) does not lower high-index motif use, consistent with agent-carried habits.

## Notes
- 2026-10-04: round 1 run.
