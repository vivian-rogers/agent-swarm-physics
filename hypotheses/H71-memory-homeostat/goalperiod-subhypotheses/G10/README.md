# H71 × G10: memory size as a first-order homeostat (2025-08-18 → 2025-08-22)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 7 agents with memory snapshots · 197 compression cycles (non-holdout) · 5 agents with ≥ 15 within-period cycle pairs.

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
*Run 2026-10-04 (`analysis/run.py`, `analysis/posthoc.py`; non-holdout).* Set point (median agent mean of x⁺): 10790 characters; agent heterogeneity of φ⁺_i: τ 0.19.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| φ⁺ in (0, 0.9), CI excludes 0 and 1 | 0.30 [-0.14, 0.42] (5 agents, 174 cycle pairs) | RW 1; deadbeat 0 | not met |
| AR(1) beats RW for ≥ 60% of agents | 0.50 of 4 (beats deadbeat 0.50) | – | not met |
| \|AR(2)\| < 0.1 | +0.11 [-0.10, +0.24] | 0 | not met |
| clock: \|slope\| ≤ 0.1 | -0.07 [-0.17, +0.08] | wall clock ≈ −0.2 | met |
| decomposition (post hoc reading) | b 0.27, c -0.45, b(1+c) 0.15 | φ⁺ = b(1+c) for one loop | φ⁺ ≫ b(1+c) |
| post hoc: ρ₂ − ρ₁² (two timescales) | +0.097 [-0.098, +0.223]; ρ_s 0.63, slow share 0.42 | 0 for one first-order loop | not resolved |

**Reading.** Memory size reverts toward an agent set point (φ⁺ < 1), with no overshoot. The one-step maps (b, c) explain less persistence than φ⁺ shows, so part of the persistence is a slowly drifting set point (card, post hoc two-timescale model).

## Scorecard (period-specific axes)
- **C:** φ⁺ against RW and deadbeat (out of sample); **D:** the mixed-phase sign and the clock slope are unfitted statistics; **F:** synthetic recovery at this period's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H71-memory-homeostat/results/periods.json` (key `G10`).
