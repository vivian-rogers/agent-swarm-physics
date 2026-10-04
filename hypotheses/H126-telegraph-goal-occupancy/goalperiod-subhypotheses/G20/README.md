# H126 × G20: goal #20 (2025-11-17 → 2025-11-28)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · mode I · 8 agents · units 20a, 20b, 20c, 20d · 2025-11-17 → 2025-11-28.

## Why this period
An assigned (non-free) goal period outside the holdout: the goal field should hold the on-goal occupancy at 0.1–0.5 (H105), so both dwell types are observed.

## Prediction
*Written 2026-10-04 ~22:25 UTC, before running on this period.*
Replication layer (card P1–P3, per unit 20a, 20b, 20c, 20d):
- **P1 exponential dwells:** held-out-day ΔLL(M4s − M2a) per statement ≤ its parametric-bootstrap 95th percentile, or the M4s dwell CV < 2 in both states. Heavy-tailed (both conditions violated) counts against; it is the kill if it happens in > ½ of all units.
- **P2 dwells predict occupancy:** the held-out-day predicted agent-window occupancy is within 20% of the observed (|ρ_p| ≤ ln 1.2); off by > 30% counts against (kill if in > ½ of all units).
- **P3 kickoff (if this period has an eligible kickoff design from #19):** Δln k_on 90% CI above 0 and Δln k_off CI containing 0.
- Expectation for this period: regime I, mode I, N ≈ 8. Regime I/II: statements are dense on the call clock (median gap 1–4 calls).
- Unit verdict: supported if P1 and P2 hold; failed if heavy-tailed or |ρ_p| > ln 1.3; mixed otherwise. P3 is reported separately.

## Result
*Run 2026-10-04 (UTC), after Amendment A1. bge_small, deduplicated, call clock, M2a with jointly fitted emissions. P1, P2 are descriptive after A1 (P2's kill kept); P3 is the primary test. Period verdict after A1: failed if P3 counts against (k_off, or both rates move) or the P2 kill (|ρ_p| > ln 1.3) holds in > ½ of the units; supported if P3 = k_on; descriptive otherwise.*

| Unit | agents | statements | P1 dLL(M4−M2) vs N0 q95; CV max | P2 ρ_p (held-out) | p_win | p_dw | τ_on / τ_off (calls, median) | q₀ / q₁ | P5 dLL(call−wall) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | 8 | 876 | -0.0003 vs 0.0025; 1.85 (exponential) | -0.19 (between) | 0.38 | 0.57 | 326.5 / 333.4 | 0.056 / 0.59 | +0.0346 |
| 20c | 9 | 1440 | +0.0159 vs 0.0001; 1.00 (exponential) | -0.10 (within20) | 0.12 | 0.37 | 50.6 / 248.8 | 0.020 / 0.40 | -0.0361 |
| 20d | 10 | 2695 | -0.0003 vs 0.0004; 1.00 (exponential) | +0.18 (within20) | 0.02 | 0.21 | 16.6 / 131.0 | 0.005 / 0.31 | +0.0151 |

**P3 kickoff (#19 tail → #20, 8 agents):** Δln k_on -0.78 [-2.41, +0.47], Δln k_off -2.55 [-4.23, -1.62] (90% agent bootstrap); p 0.182 → 0.566; **k_off**.

Data: `data/processed/H126-telegraph-goal-occupancy/results/`.

## Scorecard (period-specific axes)
C: P2 consistency check; D: held-out-day occupancy (non-discriminating, A1); E: kickoff rates (P3) where testable; F: synthetic recovery of rates on this regime's skeleton.

## Notes
- Codes only; see the card for the pipeline.
