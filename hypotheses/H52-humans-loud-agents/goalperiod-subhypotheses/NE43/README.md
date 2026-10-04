# H52 × NE43: the bot falls silent (2026-08-20 / 08-21, inside #51)

**Verdict:** mixed — content unchanged; reply premium −0.039* after the stop
**Role:** native
**Period:** #51, regime III. Before: 07-06 → 08-20 (nudges on; pause/resume bookends stop after 08-05). After: 08-21 → 09-04 (no automated messages). Exception (c) on the card: the transition is the object.

## Why this period
The only clean on/off switch of the third sender class outside the holdout. If agents' treatment of humans depends on the presence of a competing non-agent channel (attention competition), the human premium should change when the bot stops; H52 (salience only) and R1 (deference) both predict no change.

## Prediction
*Written 2026-10-04 ~06:10 UTC (card, native N3), before running.*
- The human premium (content, reply, activity) does not change across the stop: |after − before| < 2 × its SE.
- An attention-competition reading predicts a larger human activity premium after the stop.
- The bot premium is estimable only before (P5).

## Result
In the verdict line, * marks a 95% CI that excludes 0.

(`native/n3_NE43.json`; per-window CEM with day-block bootstrap; the difference uses independent-window SEs.)

| Outcome | Before (34 days; 93 human msgs, 729 nudges) | After (11 days; 16 human msgs) | After − before | Prediction |
| --- | --- | --- | --- | --- |
| content (DiD χ) | +0.013 [0.007, 0.021] | +0.017 [−0.003, 0.032] | +0.003 [−0.016, 0.023] | no change ✓ |
| reply | +0.037 [0.014, 0.068] | −0.002 [−0.026, 0.017] | **−0.039 [−0.072, −0.005]** (2.3 SE) | no change ✗ |
| activity (BC) | +0.45 [−0.16, 0.90] | +0.05 [−0.41, 0.52] | −0.41 [−1.11, 0.30] | no change ✓ (attention competition predicted a rise: not seen) |
| stance | +0.07 [−0.10, 0.29] | +0.23 [0.09, 0.33] (7 replies) | +0.16 [−0.07, 0.38] | — |

Bot before the stop: content −0.001, reply −0.001, named-target activity −0.11 (not different from matched agent messages); stance of replies −0.97 [−1.15, −0.79].

Reading: the content premium does not depend on the bot channel. The reply premium vanishes after the stop, but with 16 human messages, three outcomes tested and other late-#51 changes in the same window (NE33 roster joins on 09-03), this is weak evidence. It is not the attention-competition signature (which predicted larger human effects once nudges stop).

## Scorecard (period-specific axes)
- E: the only interventional test in round 1; one of three predictions failed (reply), at 2.3 SE with 16 messages after.

## Notes
- 2026-10-04: script `analysis/native.py n3`; data `data/processed/H52-humans-loud-agents/native/n3_NE43.json`.
