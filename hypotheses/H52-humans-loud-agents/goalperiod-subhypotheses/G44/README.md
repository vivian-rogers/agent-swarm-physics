# H52 × G44: the temporary fine-tuned leader (2026-05-26 → 2026-05-29)

**Verdict:** mixed — fine-tuned leader: no premium; humans n.s.
**Role:** native
**Period:** regime III · 17–18 agents · rooms #best / #rest · 4 active days (period units 44a/44b at the leader's and Opus 4.8's joins; day fixed effects). Leader: agent 28 ("[Temporary] Fine-tuned Leader") from the qwen-v3 checkpoint (05-26 19:15 UTC) on (DQ6 `leader`, `checkpoint`). 59 human messages (313 non-kickoff rows); 251 bot rows.

## Why this period
An operator-deployed agent whose explicit role is to lead. It tests deference to an appointed authority that is not human; #45 (Fine-Tuned Leader, agent 30) is the locked confirmation target for the same test.

## Prediction
*Written 2026-10-04 ~06:10 UTC (card, native N4 and the replication P1–P5), before running.*
- Leader premium ≈ 0 (content and reply CIs include 0); the human premium in the same period ≥ the leader's.
- Replication estimator for humans and the bot as on the card (low power: 4 days, message-cluster bootstrap).

## Result
In the verdict line, * marks a 95% CI that excludes 0.

(`native/n4_leaders.json`, `G44/results.json`; message-cluster bootstrap; 4 days; low power.)

| Outcome | Fine-tuned leader (27 msgs) | Humans (56 msgs) | Bot (all rows) | Agent naming |
| --- | --- | --- | --- | --- |
| content (DiD χ) | +0.007 [−0.036, 0.058] | +0.021 [−0.014, 0.052] | +0.002 | −0.034 |
| reply | −0.054 [−0.137, 0.042] | −0.027 [−0.078, 0.016] | −0.061 | +0.296 |
| activity (BC) | −0.10 [−2.38, 1.31] | +0.37 [−0.74, 1.54] | −0.22 | −0.28 |
| stance | −0.28 [−0.70, 0.03] | +0.10 [−0.06, 0.27] | −0.12 | +0.02 |

Prediction (leader ≈ 0; human ≥ leader): both hold. The weak fine-tuned leader is not deferred to; its replies lean negative (n.s.). G44 is the one replication period where the human reply premium is below zero (n.s.).

## Scorecard (period-specific axes)
- Low power (4 days; message clusters). #45's Fine-Tuned Leader (holdout) is the confirmation target (`confirm.py` C5, C6).

## Notes
- 2026-10-04: scripts `analysis/run_period.py G44`, `analysis/native.py n4`.
