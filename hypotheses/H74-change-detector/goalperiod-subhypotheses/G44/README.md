# H74 × G44: daily change detector on goal period #44 (2026-05-26 → 2026-05-29, non-holdout days)

**Verdict:** supported
**Role:** replication
**Period:** regime III · 4 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 44). Fused alarm days: 3/4. Placebo days: 0, false alarms 0.

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2026-05-26 | scaffold family | [Prompt] Omit account info from prompts for `[Temporary]` agents. | 4.0 | hit |
| 2026-05-28 | scaffold prompt | [Prompt] Added a "keep messages short" instruction to the text-only (n | 16.5 | hit |

Goal kickoffs (not part of the rule): 2026-05-26 (Z 4.0).

Unexplained alarms (no catalogued event within ±1 active day):
- none

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
