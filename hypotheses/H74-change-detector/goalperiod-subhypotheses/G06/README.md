# H74 × G06: daily change detector on goal period #6 (2025-06-26 → 2025-07-15, non-holdout days)

**Verdict:** mixed
**Verdict (r2):** mixed
**Role:** replication
**Period:** regime I · 15 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 6). Fused alarm days: 3/15. Placebo days: 0, false alarms 0.

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2025-06-26 | scaffold tool | [Prompt/Computer-use] Timezone standardization; ensure early events ar | 3.6 | miss |
| 2025-07-01 | undocumented | public chat closed (DQ9) | 8.0 | hit |
| 2025-07-03 | scaffold tool | [Computer-use] Added screenshot redaction: screenshots are run through | 8.0 | hit |
| 2025-07-07 | scaffold prompt | [Prompt] Added a prompt instruction to not say/remember sensitive pers | 1.5 | miss |
| 2025-07-10 | scaffold family | [Prompt] Gave Gemini an extra reminder to get pixel coordinates. | 4.0 | hit |

Goal kickoffs (not part of the rule): 2025-06-26 (Z 3.6).

Unexplained alarms (no catalogued event within ±1 active day):
- 2025-06-29: Z 125.0, channel D (start_tod_min)

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 precision monitor on this period (card: Round 2; S ∪ D3 ∪ C3, LOPO thresholds at α = 0.02; role: replication, exploratory).
*Period rule written 2026-10-05 04:05 UTC, before any round-2 statistic: supported if every non-reserved target event (scaffold tool, scaffold family, drive, undocumented, goal) is hit and no P2 placebo day alarms; failed if none is hit; mixed otherwise; descriptive if none.*

Monitor alarm days: 1/15. P2 placebo days: 2, false alarms 0.

| day 0 | class | event | monitor (channels in window) |
| --- | --- | --- | --- |
| 2025-06-26 | goal | goal #6 kickoff | miss |
| 2025-06-26 | scaffold tool | [Prompt/Computer-use] Timezone standardization; ensure early | miss |
| 2025-07-01 | undocumented | public chat closed (DQ9) | hit (D3) |
| 2025-07-03 | scaffold tool | [Computer-use] Added screenshot redaction: screenshots are r | hit (D3) |
| 2025-07-10 | scaffold family | [Prompt] Gave Gemini an extra reminder to get pixel coordina | miss |

Result under the period rule: **mixed**. Data: `data/processed/H74-change-detector/r2/monitor_days.parquet` (goal_no = 6).
<!-- /R2 -->

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
