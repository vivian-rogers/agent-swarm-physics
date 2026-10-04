# H126 × G12: goal #12 (2025-09-01 → 2025-09-05)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · mode M · 7 agents · units 12a, 12b · 2025-09-01 → 2025-09-05.

## Why this period
An assigned (non-free) goal period outside the holdout: the goal field should hold the on-goal occupancy at 0.1–0.5 (H105), so both dwell types are observed.

## Prediction
*Written 2026-10-04 ~22:25 UTC, before running on this period.*
Replication layer (card P1–P3, per unit 12a, 12b):
- **P1 exponential dwells:** held-out-day ΔLL(M4s − M2a) per statement ≤ its parametric-bootstrap 95th percentile, or the M4s dwell CV < 2 in both states. Heavy-tailed (both conditions violated) counts against; it is the kill if it happens in > ½ of all units.
- **P2 dwells predict occupancy:** the held-out-day predicted agent-window occupancy is within 20% of the observed (|ρ_p| ≤ ln 1.2); off by > 30% counts against (kill if in > ½ of all units).
- **P3 kickoff (if this period has an eligible kickoff design from #11):** Δln k_on 90% CI above 0 and Δln k_off CI containing 0.
- Expectation for this period: regime I, mode M, N ≈ 7. #12 has a scheduled field (debate rounds, DQ6): P2 may fail by drift (R-drift); see native N1 below. Regime I/II: statements are dense on the call clock (median gap 1–4 calls).
- Unit verdict: supported if P1 and P2 hold; failed if heavy-tailed or |ρ_p| > ln 1.3; mixed otherwise. P3 is reported separately.

**Native N1 (G12, scheduled field):** with M2s rates split by the DQ6 debate windows (pre/deb = debate on), Δln k_on (debate − outside) 90% CI above 0 and Δln k_off CI containing 0 (credence 0.3). Counts against: Δln k_off CI below 0 with |Δln k_off| ≥ Δln k_on.

## Result
*Run 2026-10-04 (UTC), after Amendment A1. bge_small, deduplicated, call clock, M2a with jointly fitted emissions. P1, P2 are descriptive after A1 (P2's kill kept); P3 is the primary test. Period verdict after A1: failed if P3 counts against (k_off, or both rates move) or the P2 kill (|ρ_p| > ln 1.3) holds in > ½ of the units; supported if P3 = k_on; descriptive otherwise.*

| Unit | agents | statements | P1 dLL(M4−M2) vs N0 q95; CV max | P2 ρ_p (held-out) | p_win | p_dw | τ_on / τ_off (calls, median) | q₀ / q₁ | P5 dLL(call−wall) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 12a | 7 | 2719 | +0.0099 vs 0.0008; 3.57 (heavy) | +0.21 (between) | 0.55 | 0.53 | 76.7 / 52.2 | 0.073 / 0.87 | -0.0118 |

**P3 kickoff (#11 tail → #12, 7 agents):** Δln k_on +2.39 [+1.55, +3.46], Δln k_off -2.25 [-4.37, -1.64] (90% agent bootstrap); p 0.011 → 0.531; **both rates move (R-sym): counts against P3 under A1**.

**Native N1 (12a):** Δln k_on (debate − outside) +1.27 [+0.89, +2.04], Δln k_off -1.37 [-2.28, -0.35]; debate share of statements 0.32; **failed**.

Data: `data/processed/H126-telegraph-goal-occupancy/results/`.

## Scorecard (period-specific axes)
C: P2 consistency check; D: held-out-day occupancy (non-discriminating, A1); E: kickoff rates (P3) where testable; F: synthetic recovery of rates on this regime's skeleton.

## Notes
- Codes only; see the card for the pipeline.
