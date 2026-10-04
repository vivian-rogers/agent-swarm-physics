# H105 × G51: private goals as independent two-state fields (#51 head, 51a–51l)

**Verdict:** mixed
**Role:** native
**Period:** regime III · mode I/K · 21–29 agents, each with its own `agent_goal` · rooms · 2026-07-06 → 09-04 (head; the tail 09-07 → 09-21 is held out). Units 51a–51l are analysed separately.

## Why this period
Every agent has its own field direction. If agents switch on-goal together only because a shared goal synchronizes them (a common drive or coupling along one direction), private fields should remove the collective switching.

## Prediction
*Written 2026-10-04 ~20:41 UTC, before running on this period.*
- **N1:** the occupancy of each agent's spin along its *own* goal (own 95% decoy threshold from regime-III non-#51 statements) shows no collective switching: per unit with ≥ 8 agents, the variance ratio R_own has a 90% block-bootstrap CI containing 1, the median g₂,own over units is < 0.2, and g₂,own < g₂ along the shared #51 direction (kickoff + goal text). Credence 0.55.
- Counts against: median g₂,own ≥ 0.3 with CI above 0.
- Opus 5 (agent 40) is excluded before 07-29 (its first goal has no vector).

## Result
| Statistic (12 units, 18–27 agents each) | bge-small | gte-modernbert |
| --- | --- | --- |
| own-goal occupancy p_own (range over units) | 0.25–0.39 | 0.23–0.46 |
| median g₂,own | −0.08 | +0.19 |
| units whose R_own 90% CI contains 1 | 10/12 | 7/12 |
| shared #51 direction: occupancy / median g₂ | 0.006–0.044 / +0.13 | 0.018–0.057 / +0.03 |
| units with g₂,own < g₂,shared | 7/12 | 3/12 |

**N1 mixed (model-dependent):** under bge it holds (median g₂,own −0.08 < 0.2 and below the shared direction's +0.13). Under gte the first clause holds (+0.19 < 0.2) but the second fails (shared +0.03). In both models the own-goal occupancy is high and steady (≈ 0.3 through nine weeks), and agents do not switch onto their private goals together: R_own is consistent with independent agents in most units. The shared #51 direction has almost no occupancy (≈ 0.02), as H54 found (no shared target). 51a (the first three days) is the exception in both models (g₂,own 0.46 / 0.61: everyone starts their role at once, a kickoff transient). Data: `data/processed/H105-two-state-goal-order/natives/G51.json`.

## Scorecard (period-specific axes)
- G: private goal texts from `goal_fields` (DQ6 roles).
- H: independent-agent null (R = 1) holds in 10/12 (bge) and 7/12 (gte) units.

## Notes
