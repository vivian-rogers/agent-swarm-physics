# H71 × G16: memory size as a first-order homeostat (2025-10-06 → 2025-10-10)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 7 agents with memory snapshots · 483 compression cycles (non-holdout) · 7 agents with ≥ 15 within-period cycle pairs.

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
*Run 2026-10-04 (`analysis/run.py`, `analysis/posthoc.py`; non-holdout).* Set point (median agent mean of x⁺): 12172 characters; agent heterogeneity of φ⁺_i: τ 0.09.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| φ⁺ in (0, 0.9), CI excludes 0 and 1 | 0.81 [0.68, 0.91] (7 agents, 476 cycle pairs) | RW 1; deadbeat 0 | met |
| AR(1) beats RW for ≥ 60% of agents | 0.33 of 6 (beats deadbeat 0.83) | – | failed |
| \|AR(2)\| < 0.1 | +0.19 [+0.10, +0.24] | 0 | not met |
| clock: \|slope\| ≤ 0.1 | -0.05 [-0.17, +0.04] | wall clock ≈ −0.2 | met |
| decomposition (post hoc reading) | b 0.26, c -0.51, b(1+c) 0.13 | φ⁺ = b(1+c) for one loop | φ⁺ ≫ b(1+c) |
| post hoc: ρ₂ − ρ₁² (two timescales) | +0.094 [+0.049, +0.123]; ρ_s 0.83, slow share 0.84 | 0 for one first-order loop | two timescales |

**Reading.** The period fails the card's verdict rule (see the table).

## Scorecard (period-specific axes)
- **C:** φ⁺ against RW and deadbeat (out of sample); **D:** the mixed-phase sign and the clock slope are unfitted statistics; **F:** synthetic recovery at this period's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H71-memory-homeostat/results/periods.json` (key `G16`).
