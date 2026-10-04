# H77 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 05-29)

**Verdict:** descriptive
**Role:** native
**Period:** regime III · two arms on the same days: assigned #best (6 agents incl. joins) vs free #rest (12) · 4 days. Units 44a, 44b.

## Why this period
Two arms on the same days and scaffold: #best was assigned one training-data/fine-tuning project, #rest chose its own goals (H06: #best concentrates beyond the null more than #rest). The field (assignment) differs between arms while the clock, roster era and days are shared.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 16 recruitments, 68 births, 66 switch-outs, 6 expiries (both arms).

- **N77-44:** σ*(#best arm) > σ*(#rest arm) (0.45), with σ*(#rest) ≤ 0.3 (0.45). Each arm is treated as a closed reactor (agents assigned to the room on most calls).
- Likely untestable in #best (6 agents; few recruitments): then *descriptive* (0.5).
- Against: σ*(#best) ≤ σ*(#rest).

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

Both arms are untestable. #best arm (6 agents): top repo σ̂* −0.59 (J⁺ 2, J⁻ 4). #rest arm (12 agents): 0.00 (J⁺ 2, J⁻ 2). The whole period: 16 recruitments, 80 births. N77-44 cannot be scored; both arms look like own-artifact weeks (births dominate). Consistent with H58: the #best team works in its own repos. Data: `data/processed/H77-repos-as-replicators/G44/arm_2/`, `arm_3/`; results `results/G44_arm2.json`, `G44_arm3.json`.

## Scorecard (period-specific axes)
- none scored (underpowered).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
