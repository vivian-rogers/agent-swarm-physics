# H74 × G51: daily change detector on goal period #51 (2026-07-06 → 2026-09-04, non-holdout days)

**Verdict:** mixed
**Verdict (r2):** mixed
**Role:** replication
**Period:** regime III · 45 non-holdout active days scored.

## Why this period
Replication layer: the same daily detector runs on every non-holdout active day. This folder reports the period's catalogued platform and operator events (hits), its placebo days (false alarms), its goal kickoffs and its unexplained alarms.

## Prediction
*Templated from the card (written 2026-10-04 19:25 UTC, before any real-data score).* Every non-holdout scaffold, operator or undocumented event in the period is hit (fused alarm Z ≥ 4 on day −1..+1), and the per-day false-alarm rate on the period's placebo days is ≤ 0.10. Rule: supported if all such events are hit and FAR ≤ 0.10; failed if none is hit; mixed otherwise; descriptive if the period has no such event.

## Result
Data: `data/processed/H74-change-detector/scores.parquet` (rows with goal_no = 51). Fused alarm days: 16/45. Placebo days: 7, false alarms 2 (FAR 0.29).

| day 0 | class | event | window max Z | outcome |
| --- | --- | --- | --- | --- |
| 2026-07-29 | operator | human reassigns one agent's role | 26.8 | hit |
| 2026-07-29 | undocumented | search tool date fields int -> str (H56) | 26.8 | hit |
| 2026-08-05 | undocumented | daily pause/resume bookends stop (first day without) | 8.0 | hit |
| 2026-08-21 | operator | automated speaker silent (nudger off); undocumented | 9.0 | hit |
| 2026-08-21 | undocumented | nudger off (first day without) | 9.0 | hit |

Goal kickoffs (not part of the rule): 2026-07-06 (Z 116.2).

Unexplained alarms (no catalogued event within ±1 active day):
- 2026-07-14: Z 8.0, channel S
- 2026-08-07: Z 4.6, channel O (f_lines)
- 2026-08-12: Z 6.9, channel O (f_mean_line)
- 2026-08-14: Z 4.5, channel O (f_mean_line)
- 2026-08-26: Z 4.0, channel D (n_present)

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 precision monitor on this period (card: Round 2; S ∪ D3 ∪ C3, LOPO thresholds at α = 0.02; role: replication, exploratory).
*Period rule written 2026-10-05 04:05 UTC, before any round-2 statistic: supported if every non-reserved target event (scaffold tool, scaffold family, drive, undocumented, goal) is hit and no P2 placebo day alarms; failed if none is hit; mixed otherwise; descriptive if none.*

Monitor alarm days: 5/45. P2 placebo days: 16, false alarms 1 (2026-07-14).

| day 0 | class | event | monitor (channels in window) |
| --- | --- | --- | --- |
| 2026-07-06 | goal | goal #51 kickoff | hit (S) |
| 2026-07-29 | operator | human reassigns one agent's role | miss |
| 2026-07-29 | undocumented | search tool date fields int -> str (H56) | miss |
| 2026-08-05 | undocumented | daily pause/resume bookends stop (first day without) | hit (D3) |
| 2026-08-21 | operator | automated speaker silent (nudger off); undocumented | hit (D3) |
| 2026-08-21 | undocumented | nudger off (first day without) | hit (D3) |

Result under the period rule: **mixed**. Data: `data/processed/H74-change-detector/r2/monitor_days.parquet` (goal_no = 51).
<!-- /R2 -->

## Scorecard (period-specific axes)
- G (ground truth): dated events in this period are the answer key; hits as tabulated.
- C (adequacy): per-day FAR on this period's placebo days as above.

## Notes
- Templated folder (replication layer); written by `analysis/write_period_folders.py`.
