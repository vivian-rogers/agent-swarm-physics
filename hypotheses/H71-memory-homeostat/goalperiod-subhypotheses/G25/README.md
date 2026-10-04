# H71 × G25: memory size as a first-order homeostat (2025-12-29 → 2026-01-02)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 10 agents with memory snapshots · 1163 compression cycles (non-holdout) · 10 agents with ≥ 15 within-period cycle pairs.

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
*Run 2026-10-04 (`analysis/run.py`, `analysis/posthoc.py`; non-holdout).* Set point (median agent mean of x⁺): 13929 characters; agent heterogeneity of φ⁺_i: τ 0.14.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| φ⁺ in (0, 0.9), CI excludes 0 and 1 | 0.67 [0.48, 0.88] (10 agents, 1153 cycle pairs) | RW 1; deadbeat 0 | met |
| AR(1) beats RW for ≥ 60% of agents | 0.50 of 10 (beats deadbeat 0.80) | – | not met |
| \|AR(2)\| < 0.1 | +0.21 [+0.14, +0.29] | 0 | not met |
| clock: \|slope\| ≤ 0.1 | +0.02 [-0.06, +0.07] | wall clock ≈ −0.2 | met |
| decomposition (post hoc reading) | b 0.12, c -0.58, b(1+c) 0.05 | φ⁺ = b(1+c) for one loop | φ⁺ ≫ b(1+c) |
| post hoc: ρ₂ − ρ₁² (two timescales) | +0.140 [+0.085, +0.198]; ρ_s 0.81, slow share 0.70 | 0 for one first-order loop | two timescales |

**Reading.** Memory size reverts toward an agent set point (φ⁺ < 1), with no overshoot. The one-step maps (b, c) explain less persistence than φ⁺ shows, so part of the persistence is a slowly drifting set point (card, post hoc two-timescale model).

## Scorecard (period-specific axes)
- **C:** φ⁺ against RW and deadbeat (out of sample); **D:** the mixed-phase sign and the clock slope are unfitted statistics; **F:** synthetic recovery at this period's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H71-memory-homeostat/results/periods.json` (key `G25`).
