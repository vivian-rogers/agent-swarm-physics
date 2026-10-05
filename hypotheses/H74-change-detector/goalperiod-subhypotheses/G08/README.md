# H74 × G08: daily change detector on goal period #8 (2025-07-18 → 2025-08-12, non-holdout days)

**Verdict:** mixed
**Verdict (r2):** mixed
**Role:** replication
**Period:** regime I · 18 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 8). Fused alarm days: 5/18. Placebo days: 4, false alarms 2 (FAR 0.50).

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2025-07-18 | operator schedule | [Other] Moved village start time 1 hour earlier; prompt updated for th | 12.0 | hit |
| 2025-07-31 | scaffold tool | [Human-use] Handle ending a human-use session, including termination b | 1.4 | miss |
| 2025-08-01 | scaffold prompt | [Prompt] Encouraged the agent to keep going; improved the `send_messag | 1.4 | miss |
| 2025-08-05 | scaffold tool | [Human-use] Handle interaction between computer use and human use. | 2.4 | miss |
| 2025-08-07 | scaffold family | [Human-use] Added Gemini human use. | 2.7 | miss |
| 2025-08-11 | scaffold tool | [Human-use] Extended human-use support across providers (OpenAI Respon | 8.4 | hit |

Goal kickoffs (not part of the rule): 2025-07-18 (Z 12.0).

Unexplained alarms (no catalogued event within ±1 active day):
- 2025-07-25: Z 5.8, channel D (js_share)
- 2025-07-28: Z 7.8, channel M (bash_share)

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 precision monitor on this period (card: Round 2; S ∪ D3 ∪ C3, LOPO thresholds at α = 0.02; role: replication, exploratory).
*Period rule written 2026-10-05 04:05 UTC, before any round-2 statistic: supported if every non-reserved target event (scaffold tool, scaffold family, drive, undocumented, goal) is hit and no P2 placebo day alarms; failed if none is hit; mixed otherwise; descriptive if none.*

Monitor alarm days: 1/18. P2 placebo days: 6, false alarms 0.

| day 0 | class | event | monitor (channels in window) |
| --- | --- | --- | --- |
| 2025-07-18 | goal | goal #8 kickoff | hit (C3) |
| 2025-07-18 | operator schedule | [Other] Moved village start time 1 hour earlier; prompt upda | hit (C3) |
| 2025-07-31 | scaffold tool | [Human-use] Handle ending a human-use session, including ter | miss |
| 2025-08-05 | scaffold tool | [Human-use] Handle interaction between computer use and huma | miss |
| 2025-08-07 | scaffold family | [Human-use] Added Gemini human use. | miss |
| 2025-08-11 | scaffold tool | [Human-use] Extended human-use support across providers (Ope | miss |

Result under the period rule: **mixed**. Data: `data/processed/H74-change-detector/r2/monitor_days.parquet` (goal_no = 8).
<!-- /R2 -->

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
