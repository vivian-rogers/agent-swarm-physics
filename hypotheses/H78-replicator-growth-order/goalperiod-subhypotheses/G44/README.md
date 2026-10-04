# H78 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 05-29)

**Verdict:** descriptive
**Role:** native
**Period:** regime III · two arms on the same days: assigned #best (6 agents incl. joins) vs free #rest (12) · 4 days. Units 44a, 44b.

## Why this period
Assigned #best vs free #rest on the same days: the order contrast inside one period and scaffold.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 16 recruitments, 68 births, 66 switch-outs, 6 expiries (both arms).

- **N78-44:** p̂(#best arm) > p̂(#rest arm) (0.40). Likely untestable in at least one arm (16 recruitments in total; 0.6), then *descriptive*.
- Against: p̂(#best) ≤ p̂(#rest) with both testable.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

Untestable: 8 formation-free recruitments in the whole period (p̂ 2.83 [1.35, 4.31]); #best arm 0, #rest arm 8 (2.77). N78-44 cannot be scored. 80 births vs 16 recruitments: both arms behave as own-artifact weeks. A0: share of hosts on named repos rises 0.37 → 0.51 at 10.2 active h (surrogate p = 0.025). Data: `data/processed/H78-replicator-growth-order/G44/`, `arm_2/`, `arm_3/`.

## Scorecard (period-specific axes)
- none scored.

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
