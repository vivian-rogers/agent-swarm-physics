# H123 × NE09: chat interleaved into the computer-use context (2025-12-20; G23 → G24)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · N = 10 both sides · G23 (2025-12-15 → 12-19, 5 d) vs G24 (2025-12-22 → 12-26, 5 d). The holiday season starts here; goal changes at the same boundary (a confound).

## Why this period
Native N2. Computer-use calls can read chat after NE09, so talk couplings of agents in a session should rise while the scheduler stays the same. It separates a coupling change from a scheduler change.

## Prediction
*Written 2026-10-04 ~22:03 UTC, before running.*
- The audit class is unchanged (credence 0.8).
- RMS |J_s| (exact-ML symmetric talk couplings) rises by ≥ 20% (0.4).
- σ_sweep stays < 10⁻⁴ nats/step (0.7).
- Against: an audit class change at NE09.

## Result
*Run 2026-10-04 22:06 / 22:15 UTC; data `data/processed/H123-regime1-turn-sweep/results/{audit,ep}.parquet`.* EP in 10⁻³ nats per call step.

| Quantity (talk spin) | G23 (before) | G24 (after) |
| --- | --- | --- |
| Audit class · η_ord · κ_par | self-clocked · 0.039 · 1.00 | self-clocked · 0.041 · 1.00 |
| L_name [95% CI] | 1.11 [1.04, 1.19] | 1.03 [0.96, 1.10] |
| RMS J_s (day-bootstrap 95% interval) | 0.064 [0.064, 0.135] | 0.085 [0.089, 0.136] |
| σ×(1) / σ×(2) / σ×(4) | −0.28 / −0.63 / −1.18 (floor) | +0.54 / +1.08 / +1.53 (all above the floor) |
| σ_sweep − σ_rand (lag 2) | +0.03 | +0.10 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| Audit class unchanged | unchanged | supported |
| RMS J_s rises ≥ 20% | point +33%, but the bootstrap intervals overlap almost completely (the RMS of a noisy J is biased upward by resampling) | inconclusive |
| σ_sweep < 10⁻⁴ | +0.10×10⁻³ at lag 2: at the threshold; inside the simulation spread | supported (marginal) |

**Not predicted:** G24 is one of two regime-I units where talk σ× clears the floor at every lag, including lag 1 (asymmetric, not a sweep). It sits right after NE09, which is suggestive of a read-in coupling turning on, but one unit after a boundary that also changes the goal and starts the holidays is not evidence; the 10–25% per-test floor size makes 2/31 hits expected by chance. Flagged for round 2 (a NE09 event study with several placebo boundaries).

## Scorecard (period-specific axes)
E 1 (scheduler invariant as predicted; the coupling step is not resolved).

## Notes
