# H126 × G04: goal #4 (2025-05-15 → 2025-06-18)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · mode C · 4 agents · units 4a, 4b, 4c, 4d · 2025-05-15 → 2025-06-18.

## Why this period
An assigned (non-free) goal period outside the holdout: the goal field should hold the on-goal occupancy at 0.1–0.5 (H105), so both dwell types are observed.

## Prediction
*Written 2026-10-04 ~22:25 UTC, before running on this period.*
Replication layer (card P1–P3, per unit 4a, 4b, 4c, 4d):
- **P1 exponential dwells:** held-out-day ΔLL(M4s − M2a) per statement ≤ its parametric-bootstrap 95th percentile, or the M4s dwell CV < 2 in both states. Heavy-tailed (both conditions violated) counts against; it is the kill if it happens in > ½ of all units.
- **P2 dwells predict occupancy:** the held-out-day predicted agent-window occupancy is within 20% of the observed (|ρ_p| ≤ ln 1.2); off by > 30% counts against (kill if in > ½ of all units).
- **P3 kickoff (if this period has an eligible kickoff design from #3):** Δln k_on 90% CI above 0 and Δln k_off CI containing 0.
- Expectation for this period: regime I, mode C, N ≈ 4. Regime I/II: statements are dense on the call clock (median gap 1–4 calls).
- Unit verdict: supported if P1 and P2 hold; failed if heavy-tailed or |ρ_p| > ln 1.3; mixed otherwise. P3 is reported separately.

## Result
*Run 2026-10-04 (UTC), after Amendment A1. bge_small, deduplicated, call clock, M2a with jointly fitted emissions. P1, P2 are descriptive after A1 (P2's kill kept); P3 is the primary test. Period verdict after A1: failed if P3 counts against (k_off, or both rates move) or the P2 kill (|ρ_p| > ln 1.3) holds in > ½ of the units; supported if P3 = k_on; descriptive otherwise.*

| Unit | agents | statements | P1 dLL(M4−M2) vs N0 q95; CV max | P2 ρ_p (held-out) | p_win | p_dw | τ_on / τ_off (calls, median) | q₀ / q₁ | P5 dLL(call−wall) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 4 | 1275 | +0.0020 vs 0.0073; 3.04 (exponential) | -0.06 (within20) | 0.14 | 0.30 | 52.3 / 215.8 | 0.037 / 0.57 | +0.0048 |
| 4c | 4 | 4798 | +0.0104 vs 0.0007; 3.28 (heavy) | -0.06 (within20) | 0.32 | 0.39 | 68.9 / 122.9 | 0.071 / 0.67 | -0.0042 |

**P3 kickoff (#3 tail → #4, 4 agents):** Δln k_on -1.48 [-2.17, -0.40], Δln k_off -1.56 [-2.15, -0.38] (90% agent bootstrap); p 0.320 → 0.336; **k_off**.

Data: `data/processed/H126-telegraph-goal-occupancy/results/`.

## Scorecard (period-specific axes)
C: P2 consistency check; D: held-out-day occupancy (non-discriminating, A1); E: kickoff rates (P3) where testable; F: synthetic recovery of rates on this regime's skeleton.

## Notes
- Codes only; see the card for the pipeline.
