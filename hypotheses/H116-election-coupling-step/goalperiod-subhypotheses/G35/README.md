# H116 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 03-20)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime II · mode C · 13 agents · rooms #best / #rest · 5 days. Daily lead designers per room on 03-16, 03-17, 03-18 (DQ6 `leader`).

## Why this period
Daily designations with the same agents as peers on other days, in the computer-use scaffold where the per-call clock holds (H40).

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* R: a lead designer's out-coupling on its leader day exceeds its out-coupling on its other days in the same room, beyond the same day-to-day contrast for non-leaders: Δout_lead > 0 with leader-label permutation (within room-day) p < 0.05. [0.35] Against: ≤ 0 or p ≥ 0.05.

## Result
*Run 2026-10-04 22:31 UTC* (`data/processed/H116-election-coupling-step/G35/replication.json`). Role-step model over 10 room-days (42,572 calls), 5 lead-designer room-days (03-17 #rest's lead is the Claude Code agent, never a ledger recipient, so excluded), λ = 4.

| Statistic | Observed | Null (lead label permuted within room-day, 200) | Verdict |
| --- | --- | --- | --- |
| Δout_lead | −0.025 ± 0.11 | mean +0.073, q95 0.23; p(≥) 0.83 | failed |
| Δin_lead | −0.048 | p(≥) 0.92 | — |

- Being the day's lead designer does not raise an agent's per-call out-coupling in its room.

## Scorecard (period-specific axes)
E (daily rotation), G (DQ6 lead designers), I.

## Notes
