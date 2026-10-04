# H74 × G38: daily change detector on goal period #38 (2026-04-02 → 2026-04-24, non-holdout days)

**Verdict:** supported
**Role:** replication
**Period:** regime III · 17 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 38). Fused alarm days: 4/17. Placebo days: 3, false alarms 0 (FAR 0.00).

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2026-04-02 | operator | operator corrects Year-1 total belief | 8.0 | hit |
| 2026-04-14 | scaffold tool | [Tools/Chat] Added the unsolicited-outreach approval system: agents' u | 8.0 | hit |
| 2026-04-20 | scaffold prompt | [Prompt] Told computer-use agents to suppress codex stderr. | 7.5 | hit |
| 2026-04-20 | scaffold tool | [Tools] `search_history`: split long transcripts into verbatim segment | 7.5 | hit |
| 2026-04-20 | undocumented | search oracle swap Gemini 2.5 Pro -> Sonnet 4.6 (H56) | 7.5 | hit |
| 2026-04-24 | scaffold family | [Computer-use] Temporary hotfix for a DeepSeek "multiple tool call IDs | 31.7 | hit |

Goal kickoffs (not part of the rule): 2026-04-02 (Z 8.0).

Unexplained alarms (no catalogued event within ±1 active day):
- none

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
