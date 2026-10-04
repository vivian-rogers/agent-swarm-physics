# H45 × NE42: #best/#rest merge and split, A-B-A (#39 → #40 → #41, 2026-04-27 → 05-15)

**Verdict:** failed (the set point follows inflow: leak φ 1.07 [0.51, 1.20], within-agent slope 1.06 [0.95, 1.11] × passive)
**Role:** native
**Period:** #39 (04-27 → 05-01, two rooms) → #40 (05-04 → 05-08, one merged room, #universe-coordination) → #41 (05-11 → 05-15, the same two rooms). Regime III, 15 agents, fixed roster. Not held out.

## Why this period
The merge puts all agents in one room for a week, so the room traffic each agent receives per call jumps, then falls back at the split, with the roster fixed. Under passive accumulation each agent's set point s\* rises in #40 by about (1 − s̄)·Δ ln λ (in logs) and returns in #41. A homeostat holds s\* near its level despite the flood. Goal-confounded: each phase is a new goal (#40 is a shared build).

## Prediction
*Written 2026-10-04 06:32 UTC, before running H45 on these periods.*
- **A1:** the median inflow per call λ rises in #40 relative to both #39 and #41 for a majority of agents present in all three periods (the flood exists).
- **A2 (leak):** φ = Δ ln s\* / ((1 − s̄) Δ ln λ), with Δ = #40 minus the mean of #39 and #41, per agent: H45 predicts median φ ≤ 0.3 (the set point holds); passive predicts φ ≈ 1. Expected (my prior): φ ≈ 1.
- **A3:** the within-agent slope of ln s\* on ln λ across the three periods (agent fixed effects) divided by (1 − s̄): H45 ≤ 0.3; passive ≈ 1.
- **Against H45:** φ ≥ 0.7 with a bootstrap CI (over agents) excluding 0.3.

## Result
10 agents with set points (≥ 50 band calls) in all three periods; s̄ 0.10.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| A1: λ rises in #40 vs the mean of #39 and #41 for a majority | 9/10 agents; median Δ ln λ +0.25. Period medians: λ 74 → 194 → 165 room tokens per call; new items per call 0.23 → 0.55 → 0.53 | – | met (but λ did not fall back in #41) |
| A2 (H45): leak φ ≤ 0.3 | φ median **1.07** [0.51, 1.20] (median Δ ln s\* +0.22) | passive 1 | **failed** (passive) |
| A3: within-agent slope of ln s\* on ln λ / (1 − s̄) ≤ 0.3 | **1.06** [0.95, 1.11] | passive 1 | **failed** (passive) |

**Reading.** The merge flooded the agents (median room share 0.048 in #39, 0.107 in #40), and each agent's set point moved exactly as passive accumulation predicts (slope 1.06 × passive). The split did not undo the flood: #41's #rest room (11 agents doing parallel research) kept inflow per call near #40's level, and the share stayed up (0.098). So the A-B-A is A-B-B′ in inflow. The within-agent slope across the three periods uses all three points and is the cleaner statistic. Goal-confounded as always at NE42.

Data: `data/processed/H45-context-homeostasis/NE42/native.json`.

## Scorecard (period-specific axes)
- **C/H:** the passive model (slope 1) is inside the CI; the homeostat (≤ 0.3) is excluded.
- **E:** the merge is the intervention; the set point tracks the change in inflow it caused.

## Notes
- 2026-10-04 06:32 UTC: prediction written before the run.
- 2026-10-04: results from `analysis/natives.py` (NE42).
