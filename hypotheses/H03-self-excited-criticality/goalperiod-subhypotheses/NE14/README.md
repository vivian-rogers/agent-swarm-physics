# H03 × NE14: regime II → III (2026-03-24), with and without the day-edge adjustment

**Verdict:** mixed
**Role:** native
**Period:** last regime-II days (#35, #36 on 03-23) vs first regime-III days (#36 from 03-24, #37), as in H38's NE14 design. Transition exception (c): the design compares the two sides of a boundary.

## Why this period
Round 1 found n̂ TALK and fast cross-triggering lower in regime III (G19 axis of H19: n̂ −0.22, fast n_x −0.06). H38 then showed that about two thirds of regime-III *equal-time* co-activation is the operator's day edges (agents starting and stopping together), and that the regime II → III rise in co-activation vanishes under adjustment. The event-time Hawkes estimators have a 30-min within-day baseline shape (B2) that should already absorb day-edge drive; this test checks that.

## Prediction
*Written 2026-10-04 06:45 UTC, before any NE14 fit in round 1b.*
- **N14-a.** Raw (untrimmed) n̂ TALK and fast n_x (M3, τ ≤ 300 s) are lower on the regime-III side than on the regime-II side (Δ < 0).
- **N14-b (day-edge robustness).** Trimming each realization to its all-present window (every active agent between its first and last active minute, from `activity_bins_fixed`) changes Δn̂ TALK by less than 0.10 and keeps its sign; fast n_x on each side stays above its agent-shift null. I.e. Hawkes triggering is not a day-edge artifact, unlike the equal-time gain.
- Counts against: Δ changing sign or by ≥ 0.10 under trimming, or fast n_x falling to its shift null once trimmed.

## Result
*Run 2026-10-04 (round-1b inputs). Sides: II = 6 days, III = 7 days; the trim keeps 98% (II) and 91% (III) of window time. M1_B2 per side; M3 fast cross-triggering against 5 agent-shift surrogates.*

| | n̂ TALK raw | n̂ TALK trimmed | n̂ ALL raw | n̂ ALL trimmed | fast n_x TALK raw (shift null max) | trimmed |
| --- | --- | --- | --- | --- | --- | --- |
| regime II | 0.09 [0.01, 0.18]* | 0.08 [0.00, 0.16] | 0.29 [0.22, 0.34] | 0.28 [0.20, 0.34] | 0.051 (0.028) | 0.042 (0.024) |
| regime III | 0.37 [0.26, 0.39] | 0.39 [0.28, 0.42] | 0.21 [0.14, 0.36] | 0.23 [0.18, 0.38] | 0.005 (0.004) | 0.000 (0.000) |
| **Δ (III − II)** | **+0.28** | **+0.31** | −0.08 | −0.05 | −0.046 | −0.042 |

\* profile CI (the regime-II day bootstrap is unstable: 0–1.6).

- **N14-a: mixed.** Fast cross-triggering falls across the switch (0.05 → ≈ 0, at its shift null in regime III) and n̂ ALL falls, as predicted; but n̂ TALK *rises* (+0.28), unlike round 1's cross-period regime contrast (regime III − I: −0.21).
- **N14-b: supported for the trim.** Trimming to the all-present window moves every Δ by ≤ 0.03 and keeps its sign: Hawkes estimates are not day-edge artifacts (the B2 within-day shape absorbs the edges), unlike the equal-time gain (H19 NE14: activity rise +0.11 → −0.08 under the same trim). The second clause (regime-III fast n_x above its null) fails, but already on the untrimmed data.
- **Verdict: mixed.** The methodological point holds (Hawkes fits are robust to the day edges); the direction of n̂ TALK at the boundary is the opposite of the between-regime contrast, so that contrast is not a scaffold step but a slower drift (size, era).

## Notes
- Code: `analysis/r1b.py native` (key `NE14`); trimming function `trim_daymap`.
