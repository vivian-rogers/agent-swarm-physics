# H74 × G36: daily change detector on goal period #36 (2026-03-23 → 2026-03-27, non-holdout days)

**Verdict:** supported
**Role:** replication
**Period:** regime II/III · 5 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 36). Fused alarm days: 2/5. Placebo days: 0, false alarms 0.

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2026-03-23 | scaffold tool | [Computer-use] Lowercase single-char key names in key/hold_key actions | 16.0 | hit |
| 2026-03-24 | scaffold tool | [Computer-use] Major change: agents are now _permanently_ in computer- | 16.0 | hit |
| 2026-03-26 | scaffold family | [Computer-use] Fixed empty API responses from Anthropic computer-use m | 5.1 | hit |
| 2026-03-26 | scaffold tool | [Memory] Fixed a contradictory "never update memory" instruction in th | 5.1 | hit |

Goal kickoffs (not part of the rule): 2026-03-23 (Z 16.0).

Unexplained alarms (no catalogued event within ±1 active day):
- none

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
