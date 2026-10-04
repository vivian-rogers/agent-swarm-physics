# H77 × G42: Run your own YouTube channel (2026-05-18 → 05-22)

**Verdict:** failed
**Role:** replication
**Period:** regime III · individual channels (own-artifact week) · 15–16 agents · #best/#rest · 5 days. Units 42a, 42b (join).

## Why this period
Own-artifact week (individual channels; H11 work ownership 0.74).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 15 recruitments, 20 births, 14 switch-outs, 10 expiries.

- σ* ≤ 0.3 if testable (0.40); likely untestable at 15 recruitments (0.5).
- Against: σ* > 0.3 with J⁺ + J⁻ ≥ 8.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| σ* ≤ 0.3 | 0.55 [−0.50, 1.60] (J⁺ 9, J⁻ 5, dilution 23) | neutral 95th pct 2.22 | failed (point above 0.3; CI includes 0.3) |
| q | 1.90 [1.04, 2.76] (13 switch-outs) | neutral-world q̂ 0.96 | (second-order-like; 13 events) |

34 of 36 recruitments went to kickoff-named repos; the top repo is named. σ* = 0.94 / 0.55 / 0.57 / 0.27 at E = 50 / 100 / 150 / 300. Data: `data/processed/H77-repos-as-replicators/GG42/`, results `.../results/GG42.json`.

## Scorecard (period-specific axes)
- C: 0. G: 1.

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
