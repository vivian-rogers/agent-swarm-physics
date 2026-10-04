# H71 × G12b: memory size as a first-order homeostat (2025-09-05 → 2025-09-05)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 7 agents with memory snapshots · 111 compression cycles (non-holdout) · 4 agents with ≥ 15 within-period cycle pairs. Memory-relevant split: see the card (NE04 / NE14 / NE16).

## Why this period
The common estimator (card, O1–O7) on every eligible non-holdout period: each period is one point on the (set point, gain) plane. Regime I/II: several appends per compressed session; the mixed series is dominated by growth runs, so P3 and P4 do not apply here.

## Prediction
*Written 2026-10-04 19:55 UTC, before running on this period (card predictions applied).*
- φ⁺ (half-panel-jackknife within-agent AR(1) on post-compression log size) lies in (0, 0.9) with the agent-bootstrap CI excluding 0 and 1.
- AR(1) beats the random walk out of sample for ≥ 60% of agents with ≥ 20 cycles; AR(2) adds |φ₂| < 0.1.
- Clock: |slope of φ⁺ on log cycle length| ≤ 0.1.
- Counts against: φ⁺'s CI includes 1 (random walk) or lies below 0 (overshoot), or AR(1) beats RW for < 40% of agents.
- Synthetic power at this period's counts (`synthetic/synthetic.json`, nearest skeleton): overshoot of −0.3 detected in 100% of replicates; a random walk's CI includes 1 in 85–100%.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/posthoc.py`; non-holdout).* Set point (median agent mean of x⁺): 11225 characters; agent heterogeneity of φ⁺_i: τ 0.14.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| φ⁺ in (0, 0.9), CI excludes 0 and 1 | 0.37 [-0.07, 0.80] (4 agents, 90 cycle pairs) | RW 1; deadbeat 0 | not met |
| AR(1) beats RW for ≥ 60% of agents | 0.67 of 3 (beats deadbeat 0.67) | – | met |
| \|AR(2)\| < 0.1 | -0.01 [-0.07, +0.10] | 0 | met |
| clock: \|slope\| ≤ 0.1 | -0.08 [-0.68, +0.73] | wall clock ≈ −0.2 | met |
| decomposition (post hoc reading) | b 0.12, c -0.60, b(1+c) 0.05 | φ⁺ = b(1+c) for one loop | φ⁺ ≫ b(1+c) |
| post hoc: ρ₂ − ρ₁² (two timescales) | +0.060 [-0.046, +0.105]; ρ_s 0.51, slow share 0.65 | 0 for one first-order loop | not resolved |

**Reading.** Memory size reverts toward an agent set point (φ⁺ < 1), with no overshoot. The one-step maps (b, c) explain less persistence than φ⁺ shows, so part of the persistence is a slowly drifting set point (card, post hoc two-timescale model).

## Scorecard (period-specific axes)
- **C:** φ⁺ against RW and deadbeat (out of sample); **D:** the mixed-phase sign and the clock slope are unfitted statistics; **F:** synthetic recovery at this period's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H71-memory-homeostat/results/periods.json` (key `G12b`).
