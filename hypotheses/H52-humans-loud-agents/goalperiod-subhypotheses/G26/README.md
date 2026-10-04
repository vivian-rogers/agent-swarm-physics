# H52 × G26: the elected leader (2026-01-05 → 2026-01-12)

**Verdict:** descriptive — elected leader: reply +0.028*, content n.s.
**Role:** native
**Period:** regime I · ~10 agents · one room · non-holdout. Elected leader: agent 17 (DeepSeek-V3.2), terms 01-05 19:35 → 01-09 19:00 and 01-09 → 01-12 (DQ6; two elections, H11/H31 correction). Only 2 human messages (10 non-kickoff rows): no human comparison.

## Why this period
Peer-conferred authority (an election among agents), the contrast to G35/G44's operator-appointed leaders.

## Prediction
*Written 2026-10-04 ~06:10 UTC (card, native N4: descriptive), before running.*
- Leader premium ≈ 0 (CI includes 0). Descriptive: one leader, a few days.

## Result
In the verdict line, * marks a 95% CI that excludes 0.

(`native/n4_leaders.json`; agent 17's 158 messages during its terms, 1,422 rows; message-cluster bootstrap.)

| Outcome | Elected leader premium | Agent naming effect |
| --- | --- | --- |
| content (DiD χ) | −0.007 [−0.018, 0.007] | −0.015 |
| reply | **+0.028 [0.008, 0.050]** | +0.064 |
| activity (BC) | −1.40 [−2.03, −0.78] | +0.37 |
| stance | −0.015 [−0.148, 0.099] | +0.036 |

Like the appointed lead designers (G35), the elected leader is answered more often, but its content is not followed. The activity contrast is negative (leaders post in the busiest stretches of the election; residual confounding is likely). Only 2 human messages in the period: no human comparison.

## Scorecard (period-specific axes)
- Descriptive (one leader, a few days).

## Notes
- 2026-10-04: script `analysis/native.py n4`.
