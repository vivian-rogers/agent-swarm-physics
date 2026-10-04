# H126 × G42: goal #42 (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Role:** exploratory
**Period:** regime III · mode I · 15 agents · units 42a, 42b · 2026-05-18 → 2026-05-22.

## Why this period
An assigned (non-free) goal period outside the holdout: the goal field should hold the on-goal occupancy at 0.1–0.5 (H105), so both dwell types are observed.

## Prediction
*Written 2026-10-04 ~22:25 UTC, before running on this period.*
Replication layer (card P1–P3, per unit 42a, 42b):
- **P1 exponential dwells:** held-out-day ΔLL(M4s − M2a) per statement ≤ its parametric-bootstrap 95th percentile, or the M4s dwell CV < 2 in both states. Heavy-tailed (both conditions violated) counts against; it is the kill if it happens in > ½ of all units.
- **P2 dwells predict occupancy:** the held-out-day predicted agent-window occupancy is within 20% of the observed (|ρ_p| ≤ ln 1.2); off by > 30% counts against (kill if in > ½ of all units).
- **P3 kickoff (if this period has an eligible kickoff design from #41):** Δln k_on 90% CI above 0 and Δln k_off CI containing 0.
- Expectation for this period: regime III, mode I, N ≈ 15. Regime III: call gaps between statements are 5–17 calls, so dwells are resolved on the call clock; P5 (call beats wall clock) is expected here.
- Unit verdict: supported if P1 and P2 hold; failed if heavy-tailed or |ρ_p| > ln 1.3; mixed otherwise. P3 is reported separately.

## Result
*Run 2026-10-04 (UTC), after Amendment A1. bge_small, deduplicated, call clock, M2a with jointly fitted emissions. P1, P2 are descriptive after A1 (P2's kill kept); P3 is the primary test. Period verdict after A1: failed if P3 counts against (k_off, or both rates move) or the P2 kill (|ρ_p| > ln 1.3) holds in > ½ of the units; supported if P3 = k_on; descriptive otherwise.*

| Unit | agents | statements | P1 dLL(M4−M2) vs N0 q95; CV max | P2 ρ_p (held-out) | p_win | p_dw | τ_on / τ_off (calls, median) | q₀ / q₁ | P5 dLL(call−wall) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | 13 | 827 | -0.0345 vs 0.0000; 1.22 (exponential) | -0.01 (within20) | 0.84 | 0.77 | 247.8 / 37.0 | 0.293 / 0.87 | +0.0444 |
| 42b | 15 | 1460 | -0.0086 vs 0.0022; 1.00 (exponential) | -0.01 (within20) | 0.69 | 0.71 | 243.8 / 2.1 | 0.047 / 0.76 | +0.0278 |

**P3 kickoff (#41 tail → #42, 14 agents):** Δln k_on +4.03 [+2.08, +9.43], Δln k_off -2.96 [-6.01, -1.52] (90% agent bootstrap); p 0.011 → 0.927; **both rates move (R-sym): counts against P3 under A1**.

Data: `data/processed/H126-telegraph-goal-occupancy/results/`.

## Scorecard (period-specific axes)
C: P2 consistency check; D: held-out-day occupancy (non-discriminating, A1); E: kickoff rates (P3) where testable; F: synthetic recovery of rates on this regime's skeleton.

## Notes
- Codes only; see the card for the pipeline.
