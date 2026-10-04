# H97 × G26: elect a leader who sets the goal (#26, kickoff 2026-01-05): native announcement test + replication

**Verdict:** mixed
**Role:** native
**Period:** regime I · mode C · 10 agents · one room · day 1 contains the operator's election kickoff (18:00 UTC) and the elected leader's goal announcement (19:36 UTC; DQ6 election result 19:35). Replication: transition #25 → #26.

Native N3 failed (confounded by the day-1 transient); replication: mixed (Δρ +0.13 ± 0.07 but Δρ∥ < 0).

## Why this period
The only kickoff whose concrete target was written by an agent. If the announcement acted as a new well, the agents' positions after it would forget their pre-announcement positions faster than at a clock-time-matched split on ordinary days. The #25 → #26 kickoff is also one replication transition.

## Prediction
*Native, written 2026-10-04 ~20:41 UTC, before running on this unit.*
- **N3:** the memory ρ across the announcement (day-1 statements 18:00–19:36 vs after 19:36) lies inside the placebo distribution of the same statistic at a 19:36 UTC split on days 2–5 (percentile 0.1–0.9). Credence 0.6.
- Descriptive: mean move toward the announcement's own statement vector, vs the placebo splits.
- Counts against: a percentile below 0.1 (extra forgetting at the announcement: an agent-authored well).

*Replication, templated from the card (~20:25 UTC, amended ~20:48 UTC):* Δρ > 0 with 90% CI above 0 and Δρ∥ > 0 (supported); Δρ ≤ 0 (failed); mixed otherwise.

## Result
### Native (N3): failed
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| memory ρ across the 19:36 announcement (day 1) | 0.37 | 0.39 |
| placebo ρ at 19:36 splits, days 3–5 (3 usable) | 0.45, 0.61, 0.77 | 0.54, 0.55, 0.73 |
| percentile among placebos | 0.0 | 0.0 |
| mean move toward the announcement vector | −0.17 (placebo −0.24 … +0.01) | −0.23 |

Memory is lower across the announcement than across clock-matched splits on later days, so N3 fails by its rule. The agents do **not** move toward the announcement's own vector, so the extra forgetting is not toward the agent-authored target. Both halves of day 1 sit inside the kickoff transient (day-1 excess relaxes over ~5 active h, H54); the later-day placebos lack it. Reading: no evidence that an agent-written target acts as a well; this design cannot separate the announcement from the day-1 transient. Data: `data/processed/H97-quench-restoring-force/natives/G26.json`.

### Replication (#25 → #26): mixed
| Statistic | bge-small | gte-modernbert | agent-centered (bge) |
| --- | --- | --- | --- |
| kickoff memory ρ_kick | +0.43 ± 0.05 | +0.40 ± 0.05 | +0.37 ± 0.07 |
| placebo memory ρ0 (median) | +0.56 | +0.52 | +0.53 |
| extra forgetting Δρ | +0.13 ± 0.07 | +0.12 ± 0.06 | +0.16 ± 0.07 |
| Δρ along k̂ (∥) | -0.22 | +0.49 | -0.18 |
| Δρ transverse (⊥) | +0.14 | +0.09 | +0.17 |
| isotropy β∥ − β⊥ | +0.54 ± 0.76 | +0.18 ± 5.06 | +0.34 ± 0.71 |
| overshoot intercept a (plateau target) | +0.34 ± 0.12 | +0.23 ± 0.87 | +0.31 ± 0.11 |

Verdict reason: Δρ CI above 0 but Δρ∥ ≤ 0. Placebo boundaries: 7. Within-transition reliability of χ^mem (upper bound): 0.91.
Data: `data/processed/H97-quench-restoring-force/G26/results.json`; all configurations in `NE34/transitions_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: native placebo (later days) not matched for the kickoff transient; replication Δρ CI just above 0.
- G: announcement time from DQ6.

## Notes
- Only 3 placebo splits had ≥ 5 agents (days 3–5).
