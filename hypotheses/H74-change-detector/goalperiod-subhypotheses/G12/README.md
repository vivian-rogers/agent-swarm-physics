# H74 × G12: daily change detector on goal period #12 (2025-09-01 → 2025-09-05, non-holdout days)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 5 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 12). Fused alarm days: 0/5. Placebo days: 0, false alarms 0.

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2025-09-03 | scaffold prompt | [Prompt] Added the village day number to the prompt. | 2.0 | miss |
| 2025-09-05 | scaffold tool | [Tools] Added a `search_history` agent tool to query village history. | 3.7 | miss |

Goal kickoffs (not part of the rule): 2025-09-01 (Z 3.2).

Unexplained alarms (no catalogued event within ±1 active day):
- none

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
