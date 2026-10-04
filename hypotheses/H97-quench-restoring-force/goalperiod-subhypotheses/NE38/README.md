# H97 × NE38: Claude Opus 5's reassignment as a one-agent kickoff (#51, 2026-07-29)

**Verdict:** supported
**Role:** native
**Period:** regime III · mode I/K (#51 private goals) · ~20 agents with ≥ 4 statements on both sides · rooms · boundary 07-28 → 07-29/30. Inside unit 51f (NE38 starts it).

## Why this period
A human reassigned one agent's private goal (game dev → mathematician, DQ6 ground truth, 16:51 UTC). It is the only kickoff in the record that acts on one spin while the others keep their fields. The other agents at the same boundary are the placebo: same day, same platform, no new field.

## Prediction
*Written 2026-10-04 ~20:41 UTC, before running on this unit.*
- **N1:** Opus 5's memory-form susceptibility χ^mem across 07-28 → 07-29 (16:51 on) + 07-30 exceeds the 90th percentile of the other agents' χ^mem at the same boundary, and its day-1 displacement points at its new goal vector (cos > 0). Credence 0.6.
- Descriptive: Opus 5's memory along the new goal direction vs transverse (isotropy for one agent); Opus 5's χ^mem at its ordinary day boundaries inside 07-24 … 08-04.
- Counts against: χ^mem inside the others' range (the field on one agent does not erase its position faster than ordinary turnover).
- Both embedding models are reported; bge-small is primary.

## Result
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| Opus 5 χ^mem (07-28 → 07-29/30) | 0.57 | 0.70 |
| others' χ^mem: median / 90th percentile (26 agents) | 0.17 / 0.47 | 0.14 / 0.40 |
| Opus 5's percentile among the others | 0.88 | 1.00 |
| Opus 5's displacement · new goal (cos) | +0.54 | +0.52 |
| Opus 5 χ^mem at its ordinary boundaries (5) | −0.03 … 0.10 | – |

**N1 supported in both models:** the one-agent field erases Opus 5's position 6× more than its own ordinary days and more than 90% of the other agents at the same boundary (bge: 3 of 26 others exceed it). The move points at the new goal. The one-agent isotropy split is not estimable (denominator ≈ 0 along k̂).

Data: `data/processed/H97-quench-restoring-force/natives/NE38.json` (both models).

## Scorecard (period-specific axes)
- C: beats two placebos (other agents, same boundary; Opus 5, ordinary boundaries).
- E: a dated, human-made one-agent intervention (DQ6); the predicted sign holds.
- G: the target is the DQ6 role text.

## Notes
- Opus 5 joined on 07-24, so it has no earlier village kickoff to compare its χ with (no agent-constancy check here).
