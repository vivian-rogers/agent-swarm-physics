# H74 × G16: daily change detector on goal period #16 (2025-10-06 → 2025-10-10, non-holdout days)

**Verdict:** mixed
**Verdict (r2):** failed
**Role:** replication
**Period:** regime I · 5 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 16). Fused alarm days: 1/5. Placebo days: 0, false alarms 0.

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2025-10-06 | scaffold tool | [Tools] Shipped v1 of Google sign-in (lets agents be signed into Googl | 4.8 | hit |
| 2025-10-08 | scaffold prompt | [Prompt] System prompt: removed the schedule update and the notice of  | 2.4 | miss |
| 2025-10-09 | scaffold prompt | [Prompt] Added codex instructions to the system prompt; removed the in | 1.7 | miss |

Goal kickoffs (not part of the rule): 2025-10-06 (Z 4.8).

Unexplained alarms (no catalogued event within ±1 active day):
- none

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 precision monitor on this period (card: Round 2; S ∪ D3 ∪ C3, LOPO thresholds at α = 0.02; role: replication, exploratory).
*Period rule written 2026-10-05 04:05 UTC, before any round-2 statistic: supported if every non-reserved target event (scaffold tool, scaffold family, drive, undocumented, goal) is hit and no P2 placebo day alarms; failed if none is hit; mixed otherwise; descriptive if none.*

Monitor alarm days: 0/5. P2 placebo days: 0, false alarms 0.

| day 0 | class | event | monitor (channels in window) |
| --- | --- | --- | --- |
| 2025-10-06 | goal | goal #16 kickoff | miss |
| 2025-10-06 | scaffold tool | [Tools] Shipped v1 of Google sign-in (lets agents be signed  | miss |

Result under the period rule: **failed**. Data: `data/processed/H74-change-detector/r2/monitor_days.parquet` (goal_no = 16).
<!-- /R2 -->

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
