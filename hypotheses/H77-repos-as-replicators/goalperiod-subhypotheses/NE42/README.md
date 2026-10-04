# H77 × NE42: rooms merged into one hub room, then split back (2026-04-27 → 05-15; #39 → #40 → #41)

**Verdict:** supported
**Role:** native
**Period:** regime III · A–B–A at a fixed roster (15 agents) · goal-confounded (each side is a different goal).

## Why this period
A step change in the reactor: #39 (own worlds, two rooms) → #40 (one merged room, one kickoff-named hub) → #41 (split back, research convergence). If σ* measures selection, it should jump at the merge only if the hub wins by recruitment; if the hub is field-made (H54, H53's R = 0 wave), the hub's arrivals are formation and the rivals (own worlds) coexist.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: #39: 0 recruitments; #40: 23 recruitments, 12 births; #41: 46 recruitments, 35 births.

- **N77-NE42a:** σ*(#40 hub) ≥ 1 nat and above σ*(#39) (untestable, 0 recruitments) and σ*(#41) (0.45).
- **N77-NE42b:** the hub's arrivals are mostly formation: births + named + blind ≥ 50% of its arrivals (0.55); so a high σ* there is not selection.
- **N77-NE42c:** no rival repo goes extinct in #40 (own worlds coexist with the hub; 0.5).
- Against: σ*(#40) < 1, or hub arrivals mostly formation-free copying.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N77-NE42a σ*(#40 hub) ≥ 1 and above #39, #41 | #40 1.64 [0.80, 2.48] (J⁺ 33, J⁻ 6); #41 1.00 [−0.23, 2.22]; #39 no recruitment | supported by the letter; #40 lies inside its neutral band (95th pct 2.00) |
| N77-NE42b hub arrivals mostly formation | 49/49 hub arrivals are into the kickoff-named hub (formation by the H54 rule) | supported |
| N77-NE42c no rival goes extinct in #40 | 0 testable rivals, 0 extinct, 0 frustrated herds | supported (descriptive) |

Reading: the merge week has the highest σ* of the three, but its top repo is the field-named hub and every arrival is field-tagged. High σ* here measures how a field-made hub holds hosts (few switch-outs), not selection resolving fitness gaps. σ*(#40) = 2.75 / 1.64 / 1.41 / 0.79 at E = 50 / 100 / 150 / 300, so the ordering #40 > #41 holds at every E. Data: `results/G39.json`, `G40.json`, `G41.json`.

## Scorecard (period-specific axes)
- E: 0 (the change across the merge is in the predicted direction but inside the neutral band and field-made).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
