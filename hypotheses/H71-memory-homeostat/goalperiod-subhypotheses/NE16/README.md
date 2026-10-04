# H71 × NE16: NE16: the contradictory 'never update memory' instruction removed, 2026-03-26 (negative control)

**Verdict:** supported (negative control: no change)
**Role:** native
**Period:** see "Why this period".

## Why this period
G36b (03-24..25) vs G36c (03-26..27), same 12–13 agents, same goal. RE-O1 found memory written at 99% of forced consolidations before the fix, so the fix should change nothing in the store's dynamics.

## Prediction
*Written 2026-10-04 19:55 UTC, before running this native test.*
- **N3a (negative control):** |Δφ⁺| < 0.15 (paired over agents) and |Δ ln μ| < 0.18.
- **N3b:** the share of compressions with lines added does not change by more than 0.1.
- **Counts against:** |Δφ⁺| ≥ 0.15 with the CI excluding 0. Power is low (two days per side); a null here is weak.

## Result
*Run 2026-10-04.* Paired over agents in #36b (03-24..25) and #36c (03-26..27).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N3a \|Δφ⁺\| < 0.15 and \|Δ ln μ\| < 0.18 | Δφ⁺ -0.03 [-0.13, +0.08]; Δ ln μ +0.10 [-0.01, +0.30] (13 agents) | met (point estimates; CIs are wide) |
| N3b share of cycles with appends changes < 0.1 | 0.90 → 0.92 | met |

**Reading.** Removing the "never update memory" instruction changed nothing measurable in the store's dynamics, as RE-O1's 99% write rate before the fix implied. Two days per side: a weak null.

## Scorecard (period-specific axes)
- **E:** a documented memory-prompt change with no first stage, used as a negative control; the estimator does not invent a change.

## Notes
- Data: `data/processed/H71-memory-homeostat/results/natives.json` (key `NE16`).
