# H55 × G16: free week with operator rules (2025-10-06 → 2025-10-10)

**Verdict:** mixed
**Verdict (1c):** descriptive (round 1c, stance v2.1; fewer than 5 validated disagreement flags in the period)
**Role:** native
**Period:** regime I · mode F · 7 agents · #general · 5 days; one unit (16).

## Why this period
The operator opened the week with two rules against named behaviours: no more spreadsheets, and stop reporting self-caused bugs. That is an exogenous norm with a known start, in a free week. If agents act as each other's immune system, some of them should enforce the rules on the others; if HH210 is right, enforcement stays with the operator and peer enforcement is rare.

## Prediction
*Written 2026-10-04 06:41 UTC, before any H55 statistic on this period.* Rule topics are matched lexically in memory (spreadsheet / Google Sheet / sheet; bug report / reporting a bug / self-caused), only counts stored. Baselines: G13 and G11 (regime I, same roster size, no such rule), and G17 (the week after).
- **N16a (HH210, peer enforcement rare):** agent messages addressed to another agent that mention a rule topic and are a Jev correction or carry a lexical norm cue are ≤ 1% of G16's addressed agent messages. [0.7]
- **N16b (operator field):** the share of agent messages mentioning spreadsheets in G16 is < 0.5 × its share in G13 and in G11; for bug-report mentions < 0.7 ×. [0.6 / 0.4]
- **N16c:** G16's overall Jev correction rate (per addressed agent message with a DQ2 parent) is not above the regime-I median of eligible periods. [0.6]
- *Against:* peer enforcement of the rules is common (> 3% of addressed messages), i.e. agents police the operator's norm themselves.

## Result
*Run 2026-10-04 (`analysis/native.py`; data `data/processed/H55-norm-enforcer-immunity/G16/native.json`). Topic matches computed in memory; counts only.*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| N16a peer enforcement ≤ 1% of addressed messages | 7 candidates of 834 (0.84%): 2 Jev corrections, 5 lexical norm cues on a rule topic | G13 (no rule): 18 of 2,119 (0.85%) by the same rule | **pass**: rare and *not above* the no-rule baseline |
| N16b spreadsheet mentions < 0.5 × baseline | share 0.102 vs 0.093 (G13), 0.083 (G11): ratio 1.09 / 1.22 | | **fail** (daily: 0.13, 0.16, 0.11, 0.04, 0.06; fell only late in the week; 0.0005 in G17 after the goal changed) |
| N16b bug-report mentions < 0.7 × baseline | share 0.034 vs 0.093 / 0.142: ratio 0.37 / 0.24 | | pass (rises over the week: 0.014 → 0.066) |
| N16c correction rate not above regime-I median | S_p 1.39 vs median 1.53 Jev corrections per 100 parented messages | | pass |

**Reading.** The operator's two rules were not enforced by the agents on each other: rule-topic corrections and norm cues are as rare as in a week without the rule. The bug-report behaviour dropped (an operator field), while spreadsheet talk did not drop until the last two days. HH210's picture holds here: enforcement stays with the operator.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| E interventional | 1 | an operator norm with a known start: one targeted behaviour falls, peer enforcement does not rise |
| G ground truth | 0 | no ground truth for who enforced; lexical topic matching only |

## Notes
- "Sheet" mentions include agents discussing the rule itself; the lexical match cannot tell compliance talk from violation.

## Round 1c (stance v2.1, 2026-10-04)
*Pre-registered in the card (Round 1c, 22:14 UTC; A1c). Data: `data/processed/H55-norm-enforcer-immunity/r1c/`.*

P1-v2 ρ(c_j, ν^D_j) +0.83 (6 agents; p greater 0.03, less 0.98). Replies 459, validated disagreement flags 1, replies to C_v2 messages 12. Immune contrasts are pooled across periods (card).
