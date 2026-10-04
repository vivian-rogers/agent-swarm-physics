# H70 × NE34: goal changes as relevance scrambles of the artifact store (nights across goal boundaries)

**Verdict:** supported (goal changes scramble the store's relevance; continuation keeps it)
**Role:** native
**Period:** see "Why this period".

## Why this period
At a new goal the agent's last repo usually stops being relevant: the store survives, its information about the next allocation should not. The #39 → #40 boundary is a continuation (#40 connects the worlds built in #39), so the store should stay informative there. Boundaries with both sides non-holdout and ≤ 7 days apart: #30→#31, #35→#36, #36→#37, #37→#38, #38→#39, #39→#40, #40→#41, #41→#42. Exception (c): the boundary is the object.

## Prediction
*Written 2026-10-04 20:05 UTC, before running this native test.*
- **N2a:** P(return to A⁻ | a commit) on the first day of a new goal ≤ 0.2, against ≥ 0.6 on within-period nights.
- **N2b:** I_A across new-goal nights ≤ 0.3 × I_A within periods.
- **N2c (continuation):** at #39 → #40, P(return) ≥ 0.4 (artifacts stay relevant).
- **Counts against:** P(return) at new goals ≥ 0.5 (the artifact store, not the goal, sets allocation; R4 fails in the other direction), or #39 → #40 indistinguishable from new goals (the goal field alone sets allocation).

## Result
*Run 2026-10-04 (`analysis/run.py: ne34`).* Nights whose previous active day is ≤ 7 days earlier; agent-cluster bootstrap for P(return); I_A permutation-corrected within agent.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N2a P(return) at new goals ≤ 0.2 vs ≥ 0.6 within | new goal 0.10 [0.02, 0.20] (n 40); within 0.80 [0.67, 0.91] (n 589) | supported |
| N2b I_A(new goal) ≤ 0.3 × I_A(within) | 0.12 bits (p 0.06) vs 0.49 (p 0.002): ratio 0.25 | supported |
| N2c continuation #39 → #40 P(return) ≥ 0.4 | 0.78 [0.44, 1.00] (n 9) | supported (n small) |

Per boundary P(return): 35->36 0.00 (n 4); 36->37 0.00 (n 1); 37->38 0.33 (n 3); 38->39 0.11 (n 9); 39->40 0.78 (n 9); 40->41 0.14 (n 7); 41->42 0.20 (n 5); 42->44 0.00 (n 11).

**Reading.** The artifact store carries allocation only while its content stays relevant. A new goal resets allocation (10% return), the #39 → #40 continuation keeps it (78%), and within a goal 80% of next-day first commits go to the last repo. The goal field, not the store, decides whether the store's allocation information survives: R4 holds at boundaries, and within a goal the store holds.

## Scorecard (period-specific axes)
- **E:** goal boundaries as relevance scrambles with the #39 → #40 continuation as the control; **G:** the continuation boundary is known structure (DQ9). The continuation arm has 9 nights with a commit.

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/natives.json` (key `NE34`).
