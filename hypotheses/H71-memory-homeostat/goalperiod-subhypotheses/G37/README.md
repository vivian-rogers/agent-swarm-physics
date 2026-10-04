# H71 × G37: memory size as a first-order homeostat (2026-03-30 → 2026-04-01)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 12 agents with memory snapshots · 515 compression cycles (non-holdout) · 12 agents with ≥ 15 within-period cycle pairs.

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
*Run 2026-10-04 (`analysis/run.py`, `analysis/posthoc.py`; non-holdout).* Set point (median agent mean of x⁺): 15490 characters; agent heterogeneity of φ⁺_i: τ 0.26.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| φ⁺ in (0, 0.9), CI excludes 0 and 1 | 0.76 [0.49, 0.96] (12 agents, 503 cycle pairs) | RW 1; deadbeat 0 | met |
| AR(1) beats RW for ≥ 60% of agents | 0.55 of 11 (beats deadbeat 0.73) | – | not met |
| \|AR(2)\| < 0.1 | +0.20 [+0.08, +0.26] | 0 | not met |
| clock: \|slope\| ≤ 0.1 | -0.05 [-0.16, +0.16] | wall clock ≈ −0.2 | met |
| decomposition (post hoc reading) | b 0.45, c -0.04, b(1+c) 0.43 | φ⁺ = b(1+c) for one loop | φ⁺ ≫ b(1+c) |
| post hoc: ρ₂ − ρ₁² (two timescales) | +0.114 [+0.042, +0.164]; ρ_s 0.80, slow share 0.77 | 0 for one first-order loop | two timescales |
| mixed-phase φ < 0 while φ⁺ > 0 (P3) | mixed -0.51; single-loop synthetic -0.19; two-timescale synthetic -0.49 | – | met (sampling artifact) |
| no overshoot after forced erasures (P4) | φ⁺ forced 0.57 [0.42, 0.72], voluntary 0.72; F − V -0.16 [-0.28, +0.31] | HH269: forced < 0 | not met |

**Reading.** Memory size reverts toward an agent set point (φ⁺ < 1), with no overshoot. The one-step maps (b, c) explain less persistence than φ⁺ shows, so part of the persistence is a slowly drifting set point (card, post hoc two-timescale model).

## Scorecard (period-specific axes)
- **C:** φ⁺ against RW and deadbeat (out of sample); **D:** the mixed-phase sign and the clock slope are unfitted statistics; **F:** synthetic recovery at this period's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H71-memory-homeostat/results/periods.json` (key `G37`).
