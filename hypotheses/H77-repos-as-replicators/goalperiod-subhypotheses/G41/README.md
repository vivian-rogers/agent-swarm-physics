# H77 × G41: Novel research (NE42 split back) (2026-05-11 → 05-15)

**Verdict:** failed
**Role:** replication
**Period:** regime III · #rest converged on one research topic; #best on another · 15 agents · #best/#rest · 5 days. One unit.

## Why this period
Regime-III herding week (H11: work z_N2 +3.8): #rest converged on one research topic; 26 repos.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 46 recruitments, 35 births, 54 switch-outs, 14 expiries.

- σ* ≥ 1 nat (0.35). Resolution fraction ≥ 0.9 (0.25). Nucleus ≠ winner (0.45).
- Against: σ* < 1.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| σ* ≥ 1 nat | 0.998 [−0.23, 2.22] (J⁺ 9, J⁻ 3, dilution 14) | neutral 95th pct 1.96 | failed (by 0.002; inside the neutral band either way) |
| resolution fraction ≥ 0.9 | untestable (f_T = 0; the top repo is named) | — | n/a |
| nucleus ≠ winner | true (mechanical) | — | supported (uninformative) |

σ* = 3.22 / 1.00 / 0.55 / −0.51 at E = 50 / 100 / 150 / 300. q = 0.27 [−0.24, 0.77] (35). Data: `data/processed/H77-repos-as-replicators/GG41/`, results `.../results/GG41.json`.

## Scorecard (period-specific axes)
- C: 0. F: 0 (sign changes with E). G: 1.

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
