# H71 × G41: memory size as a first-order homeostat (2026-05-11 → 2026-05-15)

**Verdict:** supported
**Role:** replication
**Period:** regime III · 15 agents with memory snapshots · 987 compression cycles (non-holdout) · 15 agents with ≥ 15 within-period cycle pairs.

## Why this period
The common estimator (card, O1–O7) on every eligible non-holdout period: each period is one point on the (set point, gain) plane. Regime III: one append and one compression per consolidation, so the mixed-phase series should show the sampling artifact (P3); forced vs voluntary cycles are both present (P4).

## Prediction
*Written 2026-10-04 19:55 UTC, before running on this period (card predictions applied).*
- φ⁺ (half-panel-jackknife within-agent AR(1) on post-compression log size) lies in (0, 0.9) with the agent-bootstrap CI excluding 0 and 1.
- AR(1) beats the random walk out of sample for ≥ 60% of agents with ≥ 20 cycles; AR(2) adds |φ₂| < 0.1.
- Clock: |slope of φ⁺ on log cycle length| ≤ 0.1.
- Mixed-phase φ < 0 while φ⁺ > 0 (P3); φ⁺(forced) ≥ 0 and within 0.15 of φ⁺(voluntary) (P4).
- Counts against: φ⁺'s CI includes 1 (random walk) or lies below 0 (overshoot), or AR(1) beats RW for < 40% of agents.
- Synthetic power at this period's counts (`synthetic/synthetic.json`, nearest skeleton): overshoot of −0.3 detected in 100% of replicates; a random walk's CI includes 1 in 85–100%.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/posthoc.py`; non-holdout).* Set point (median agent mean of x⁺): 15788 characters; agent heterogeneity of φ⁺_i: τ 0.16.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| φ⁺ in (0, 0.9), CI excludes 0 and 1 | 0.74 [0.52, 0.91] (15 agents, 972 cycle pairs) | RW 1; deadbeat 0 | met |
| AR(1) beats RW for ≥ 60% of agents | 0.67 of 15 (beats deadbeat 0.87) | – | met |
| \|AR(2)\| < 0.1 | +0.16 [+0.08, +0.21] | 0 | not met |
| clock: \|slope\| ≤ 0.1 | +0.02 [-0.07, +0.11] | wall clock ≈ −0.2 | met |
| decomposition (post hoc reading) | b 0.41, c -0.26, b(1+c) 0.30 | φ⁺ = b(1+c) for one loop | φ⁺ ≫ b(1+c) |
| post hoc: ρ₂ − ρ₁² (two timescales) | +0.094 [+0.049, +0.131]; ρ_s 0.77, slow share 0.81 | 0 for one first-order loop | two timescales |
| mixed-phase φ < 0 while φ⁺ > 0 (P3) | mixed -0.42; single-loop synthetic -0.11; two-timescale synthetic -0.45 | – | met (sampling artifact) |
| no overshoot after forced erasures (P4) | φ⁺ forced 0.58 [0.45, 0.68], voluntary 0.68; F − V -0.11 [-0.23, +0.06] | HH269: forced < 0 | met |

**Reading.** Memory size reverts toward an agent set point (φ⁺ < 1), with no overshoot. The one-step maps (b, c) explain less persistence than φ⁺ shows, so part of the persistence is a slowly drifting set point (card, post hoc two-timescale model).

## Scorecard (period-specific axes)
- **C:** φ⁺ against RW and deadbeat (out of sample); **D:** the mixed-phase sign and the clock slope are unfitted statistics; **F:** synthetic recovery at this period's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H71-memory-homeostat/results/periods.json` (key `G41`).
