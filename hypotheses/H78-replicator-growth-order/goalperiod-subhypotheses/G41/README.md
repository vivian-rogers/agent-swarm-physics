# H78 × G41: Novel research (NE42 split back) (2026-05-11 → 05-15)

**Verdict:** failed
**Role:** replication
**Period:** regime III · #rest converged on one research topic; #best on another · 15 agents · #best/#rest · 5 days. One unit.

## Why this period
Regime-III herding week; #rest convergence on one topic.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 46 recruitments, 35 births, 54 switch-outs, 14 expiries.

- p̂ ∈ [1.2, 1.5] (0.25). Cross-lab p̂_x within 0.3 of p̂ (0.5).
- Against: p̂ < 1.2 with CI below 1.2.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| p̂ ∈ [1.2, 1.5] | 1.05 [0.00, 2.09] (19) | neutral 1.03; fitness-spread 1.35–1.70 | failed (CI does not exclude the band) |
| cross-lab p̂_x within 0.3 | −0.72 [−2.76, 1.32] (16) | — | failed (uninformative CI) |
| A0 step | calibrated step: share 0.85 → 0.44 at 8.6 active h (surrogate p = 0.05); new-repo rate in the step window 3.9× the period mean | — | supported (one period) |

Variants: E 1.39/1.27/1.02/1.05; B 0.86/1.21; wall 1.01; all recruitments 1.00 [0.61, 1.38]; named stratum 0.70 [0.17, 1.22]. Touch classes: read 22, return 37, self 4, blind 1. Data: `data/processed/H78-replicator-growth-order/GG41/`, results `.../results/GG41.json`.

## Scorecard (period-specific axes)
- C: 0. D: 1 (a calibrated decoupling step from the kickoff field, with a new-repo burst). F: 1.

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
