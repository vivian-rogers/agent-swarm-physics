# H77 × G51: Maximize your private assigned role (2026-07-06 → 09-04 (non-holdout))

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · private roles, own artifacts · 21–32 agents · #general (+ #focus in 51g) · 45 non-holdout days. Units 51a–51l (51m is holdout).

## Why this period
Private-role era: each agent has its own repo (H11 #51 work co-location 0.04–0.21), the largest own-artifact sample (12 non-holdout units, 45 days).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 258 recruitments, 828 births, 801 switch-outs, 263 expiries/leaves.

- σ* ≤ 0.3 for the period top repo, and in ≥ 2/3 of testable units (0.40).
- q ≈ 1 (|q − 1| < 0.3; 0.45).
- Against: σ* > 0.3 in most testable units.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| σ* ≤ 0.3 | untestable: the top repo's plateau has J⁺ 0, J⁻ 4 (σ̂* −2.20) | neutral 95th pct 0.99 | n/a |
| q ≈ 1 | q = 1.46 [1.22, 1.70] (654 switch-outs) | neutral-world q̂ 0.92 | failed (second-order-like: crowded repos shed hosts) |
| resolution | 7 extinct testable rivals, all *fitter* than the top repo (ŝ < 0); fraction 0.0, permutation p = 1.0 | — | bound not satisfied; not identifiable (A1) |

The #51 top repo is not kickoff-named (the only period where it is not). 5 frustrated herds (repos that reached ≥ 3 hosts and died). σ* at E = 300 is −0.07 (J⁺ 13, J⁻ 14), at E = ∞ −0.38: near zero, as HH325 predicted for a fragmented week, but not at the primary E. Data: `data/processed/H77-repos-as-replicators/GG51/`, results `.../results/GG51.json`.

## Scorecard (period-specific axes)
- B: 0 (no plateau with flux at E = 100). D: 1 (q > 1 in an own-artifact era: per-host departures rise with n).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
