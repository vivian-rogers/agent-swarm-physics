# H106 × NE27: batch join N 4 → 7 at the #10 kickoff (2025-08-18)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime I · before: #2–#8 (blocks 2025-05-10 → 08-12, N 4) · after: #10–#18 (08-18 → 10-31, N 6–7.6) · #9 (08-13 → 08-15) is held out and masked. Coincident steps: NE03 (08-20, chat messages in context limited), NE04 (09-05, history search and CoT consolidation).

## Why this period
N jumps from 4 to 7 on one day. An outside drift has no reason to change its rate on that day; a finite magnet slows by the N ratio. It is the partition contrast for P1 (STANDARDS §3).

## Prediction
*Written 2026-10-04 21:39 UTC, before running on this period.*
- Two-rate fit (α fixed 0, rate step at 08-18) on the cross-goal pairs of the window, V1 similarities. Statistic Δln k = ln(k_post/k_pre).
- **Magnet:** Δln k ≈ −ln(N̄_post/N̄_pre) ≈ −0.5. **Drift:** Δln k ≈ 0.
- **Pass (P2, Amendment A1):** Δln k below the 5th percentile of the drift-world (synthetic D) distribution on the same window, and within ±0.5 of the magnet value, both models. Only two placebo breaks fit inside the N ≥ 6 era (2025-11-03, 2025-12-15); they are reported descriptively. **Against:** Δln k ≥ 0.
- NE03 and NE04 change memory and context in the after window; a rate change could come from them, so a pass is necessary, not sufficient. Prior 0.15.

## Result
| Model | Δln k (jackknife 95% CI) | magnet prediction | drift world D: median, q05 | percentile in D | power (M below D q05) | placebo breaks |
| --- | --- | --- | --- | --- | --- | --- |
| bge_small | +0.41 [-3.37, +4.19] | -0.55 (N 4.0 → 6.9) | +0.29, -1.85 | 0.53 | 0.06 | 2025-11-03: -0.24, 2025-12-15: -0.46 |
| gte_modernbert | +0.38 [-1.60, +2.36] | -0.55 (N 4.0 → 6.9) | +0.32, -1.34 | 0.53 | 0.09 | 2025-11-03: +1.38, 2025-12-15: +2.62 |

Reading: **inconclusive (unpowered)** (card rule; power of the D-world 5% test under M: 0.09).

## Scorecard (period-specific axes)
E (interventional), D (unfitted: the jump size follows from N alone).

## Notes
- Verdict 'descriptive' = inconclusive by Amendment A3 (power of the drift-world 5% test under the magnet 0.06–0.09). The point estimate has the drift sign.
- Data: `data/processed/H106-slow-mode-finite-size/natives/natives.json`.
