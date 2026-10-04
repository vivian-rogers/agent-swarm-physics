# H77 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · individual artifacts (own-artifact week; NE42's A side) · 15 agents · #best/#rest · 5 days. One unit.

## Why this period
The cleanest own-artifact week: every agent built its own world (H11: all work labels private). The near-equilibrium, coexistence end of the phase diagram.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 0 recruitments, 28 births, 7 switch-outs, 9 expiries.

- The built tables show no recruitment at all, so σ* and the resolution test are untestable: verdict *descriptive* (0.9). Reading: zero copying flux, coexistence by construction (the theory's equilibrium limit is not reached; there is no reaction at all).
- Against: n/a.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

No repo recruited anyone: 67 births, 0 recruitments, 4 switch-outs, 52 expiries (E = 100). σ*, fitness and the bound are undefined. Every agent founded and kept its own repo. In replicator terms there is no copy reaction at all, so the near-equilibrium (σ* → 0) reading of HH325 does not apply: coexistence here is set by the task assignment (a field), not by a reversible copy reaction. Data: `data/processed/H77-repos-as-replicators/GG39/`, results `.../results/GG39.json`.

## Scorecard (period-specific axes)
- G: 1 (matches H11's 'every work label private').

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
