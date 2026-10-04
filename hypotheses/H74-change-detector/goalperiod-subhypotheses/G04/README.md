# H74 × G04: daily change detector on goal period #4 (2025-05-15 → 2025-06-18, non-holdout days)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 25 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 4). Fused alarm days: 6/25. Placebo days: 14, false alarms 2 (FAR 0.14).

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2025-05-15 | scaffold prompt | [Prompt] Clarified that each model has its own computer ("you each hav | 5.4 | hit |
| 2025-05-16 | scaffold prompt | [Prompt/Chat] Updated the prompt to reduce chat spam from `send_messag | 5.4 | hit |
| 2025-05-23 | operator schedule | [Other] Updated village start time to 17:59 UTC. | 4.4 | hit |

Goal kickoffs (not part of the rule): 2025-05-15 (Z 5.4).

Unexplained alarms (no catalogued event within ±1 active day):
- 2025-06-09: Z 11.1, channel D (start_iqr_min)
- 2025-06-12: Z 33.3, channel M (cache_share)

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
