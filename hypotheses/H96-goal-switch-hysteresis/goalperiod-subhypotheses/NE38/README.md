# H96 × NE38: one agent's role is reassigned (2026-07-29, inside #51)

**Verdict:** failed
**Role:** native
**Period:** regime III · #51 · agent 40 (Claude Opus 5) reassigned by an operator message at 16:50 UTC on 07-29 (DQ6) · old-state days 07-27, 07-28 · post days 07-29 (after the switch), 07-30, 07-31 · placebo: the other #51 agents with statements in the same windows.

## Why this period
A single-spin field step: one agent's own goal changes while every other agent keeps its goal. The other agents' own-state persistence across the same hours is a same-day placebo that the swarm-wide transitions do not have.

## Prediction
*Written 2026-10-04 21:40 UTC, before running (card N2).*
- Agent 40's old role state is identified (M_pre > 0).
- Its persistence ratio R₁ lies below the 10th percentile of the placebo agents' R₁ (its old state is erased faster than other agents' states drift) [0.7]; τ_old < 8 active h [0.6].
- HH123's lag reading: R₁ inside the placebo 10–90% band [0.3].
- *Supported (lag)* if R₁ is inside the band; *failed (quench)* if R₁ is below the 10th percentile; *descriptive* if M_pre ≤ 0; *mixed* otherwise.

## Result
*Run 2026-10-04 (`analysis/natives.py`; non-holdout).* 22 placebo agents.

| Quantity | bge | gte |
| --- | --- | --- |
| agent 40 M_pre | 0.730 | 0.725 |
| agent 40 M_1 | 0.262 | 0.159 |
| agent 40 R₁ [statement bootstrap] | 0.36 [0.27, 0.47] | 0.22 [0.08, 0.35] |
| agent 40 τ_old (active h) | 1.67 | 0.65 |
| placebo R₁ median [p10, p90] | 1.02 [0.62, 1.48] | 1.11 [0.68, 1.67] |
| agent 40 percentile among placebos | 0.00 | 0.00 |

**Verdict (card N2 rule):** bge failed; gte failed.

## Scorecard (period-specific axes)
- **E:** a single-agent field step with a same-day placebo; **G:** the switch time comes from DQ6 (operator message).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/natives/natives_{bge_small,gte_modernbert}.json` (key NE38).
