# H52 × G35: operator-appointed lead designers (2026-03-16 → 2026-03-20)

**Verdict:** mixed — lead designers: reply +0.029*, content n.s.
**Role:** native
**Period:** regime II (rooms #best / #rest; perma-computer-use starts 03-24) · 5 active days (non-holdout; NE30 ends 03-16). Lead designers per room per day from the operator kickoff (DQ6 `leader`, 6 rows, high confidence). 11 human messages (47 non-kickoff rows): the human comparison is descriptive.

## Why this period
Authority without humanness: on 03-16, 03-17 and 03-18 the operator named one agent per room as lead designer. If agents defer to authority as such, the designated leader's messages should pull their recipients more than matched messages from other agents; if deference is to humans only (or to nothing), the leader premium is ≈ 0.

## Prediction
*Written 2026-10-04 ~06:10 UTC (card, native N4), before running.*
- Leader-sent messages get no premium over matched other-agent messages (content and reply CIs include 0; credence 0.6).
- Counts against: leader π_con or π_rep > 0 with CI excluding 0 here and in G44 (authority by role, not species).

## Result
In the verdict line, * marks a 95% CI that excludes 0.

(`native/n4_leaders.json`; 210 leader messages from the six designated agents, 1,128 rows; message-cluster bootstrap, 5 days.)

| Outcome | Leader premium | Human premium (10 messages) | Agent naming effect |
| --- | --- | --- | --- |
| content (DiD χ) | −0.012 [−0.027, 0.005] | −0.029 [−0.108, 0.059] | −0.023 |
| reply | **+0.029 [0.011, 0.053]** | +0.140 [−0.148, 0.393] | +0.164 |
| activity (BC) | −0.22 [−0.44, 0.04] | −1.64 [−4.64, 0.16] | −0.40 |
| stance | +0.045 [−0.085, 0.172] | +0.044 [−0.621, 0.415] | −0.086 |

Prediction (leader premium ≈ 0 in content and reply): content ✓, reply ✗. Appointed agent leaders are answered more often than comparable messages from other agents (by about as much as humans are in the pooled replication, +0.03), but their content is not followed more. The leader set includes the Claude Code agent (19) on 03-17 (DQ6).

## Scorecard (period-specific axes)
- G: DQ6 leader labels (operator kickoff, high confidence).
- H: authority-by-role (reply premium for leaders) vs species (humans only): the reply premium is not species-specific.

## Notes
- 2026-10-04: script `analysis/native.py n4`.
