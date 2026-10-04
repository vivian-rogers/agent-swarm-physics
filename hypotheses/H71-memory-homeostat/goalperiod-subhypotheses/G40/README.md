# H71 × G40: memory size as a first-order homeostat (2026-05-04 → 2026-05-08)

**Verdict:** supported
**Role:** replication
**Period:** regime III · 15 agents with memory snapshots · 1084 compression cycles (non-holdout) · 15 agents with ≥ 15 within-period cycle pairs.

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
*Run 2026-10-04 (`analysis/run.py`, `analysis/posthoc.py`; non-holdout).* Set point (median agent mean of x⁺): 15989 characters; agent heterogeneity of φ⁺_i: τ 0.16.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| φ⁺ in (0, 0.9), CI excludes 0 and 1 | 0.72 [0.61, 0.82] (15 agents, 1069 cycle pairs) | RW 1; deadbeat 0 | met |
| AR(1) beats RW for ≥ 60% of agents | 0.73 of 15 (beats deadbeat 0.73) | – | met |
| \|AR(2)\| < 0.1 | +0.15 [+0.10, +0.20] | 0 | not met |
| clock: \|slope\| ≤ 0.1 | +0.04 [-0.06, +0.12] | wall clock ≈ −0.2 | met |
| decomposition (post hoc reading) | b 0.45, c -0.26, b(1+c) 0.33 | φ⁺ = b(1+c) for one loop | φ⁺ ≫ b(1+c) |
| post hoc: ρ₂ − ρ₁² (two timescales) | +0.088 [+0.062, +0.112]; ρ_s 0.78, slow share 0.82 | 0 for one first-order loop | two timescales |
| mixed-phase φ < 0 while φ⁺ > 0 (P3) | mixed -0.54; single-loop synthetic -0.16; two-timescale synthetic -0.48 | – | met (sampling artifact) |
| no overshoot after forced erasures (P4) | φ⁺ forced 0.65 [0.53, 0.73], voluntary 0.65; F − V -0.00 [-0.23, +0.14] | HH269: forced < 0 | met |

**Reading.** Memory size reverts toward an agent set point (φ⁺ < 1), with no overshoot. The one-step maps (b, c) explain less persistence than φ⁺ shows, so part of the persistence is a slowly drifting set point (card, post hoc two-timescale model).

## Scorecard (period-specific axes)
- **C:** φ⁺ against RW and deadbeat (out of sample); **D:** the mixed-phase sign and the clock slope are unfitted statistics; **F:** synthetic recovery at this period's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H71-memory-homeostat/results/periods.json` (key `G40`).
