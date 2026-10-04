# H115 × G44: Finetune your leader! (2026-05-26 → 06-01)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · mode C · 16 agents (+2 on 05-28) · rooms #best / #rest · 4 days (units 44a, 44b). The temporary fine-tuned leader (agent 28) ran intermittently in #best from 05-26 19:15 UTC (DQ6 `leader` and `checkpoint` rows).

## Why this period
An installed leader in the regime-III computer-use scaffold, non-holdout; its permanent deployment in #45 is held out (planned confirmation).

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* R1: in each #best day window where agent 28 has ≥ 5 calls, its normalized sink rank among #best agents is u_L ≥ 0.5 (source half) in ≥ 2/3 of windows. [0.5] Against: u_L < 0.5 in ≥ 2/3. If agent 28 has too few calls in every window, the verdict is n/a.

## Result
*Run 2026-10-04 22:19–22:22 UTC* (`data/processed/H115-debate-judge-role-recovery/G44/replication.json`). #best agents' all-present trim per day; additive fit, λ = 4.

| #best day | calls | leader rank / n | u_L | in-flight u_L | skeleton-null mean u_L |
| --- | --- | --- | --- | --- | --- |
| 05-26, 05-27 | — | agent 28 has < 5 trimmed calls | | | |
| 05-28 | 1,185 | 5 / 6 | 0.80 | 0.00 | 0.57 |
| 05-29 | 970 | 1 / 6 | 0.00 | 0.00 | 0.49 |

- One window each way (source half 1 of 2). The installed leader ran intermittently (DQ6 checkpoints), so only two windows qualify; the test has no power here.

## Scorecard (period-specific axes)
G (DQ6 leader), I.

## Notes
