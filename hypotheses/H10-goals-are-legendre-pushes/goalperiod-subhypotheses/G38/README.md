# H10 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** mixed (pair test #37 → #38a; NE34)
**Role:** exploratory
**Period:** regime III · mode C · 12 agents at start (+2 joins) · #best / #rest · 17 active days. **Splits:** NE17 (outreach approval, 04-14) and NE18 (history search, 04-20); the analyzed unit is 38a = 04-02 … 04-13; segment A = days 2+ (04-03 … 04-13). Day 1 also carries NE36 (operator corrects the Year-1 total).

## Why this period
Collaborative week after the only non-holdout regime-III free week. Long enough (~8 days in A) for a stable variance estimate; rival R5 predicts a higher loop gain here. The H10 test (free #37 → this week) is in [`../NE34/`](../NE34/README.md); this folder's verdict mirrors that pair's verdict, since the tilt predictions are statements about this week.

## Prediction
*Written 2026-10-03, before running on this period.* Card P1–P4 for the pair #37 → #38 (see the card for the rules), plus:
- **A1, the push exists.** Δ̄ > 0 along ĝ, and the swarm's daily mean alignment on every day of A is above the free week's mean.
- **A2, stationarity (axis B).** No trend across the days of A in daily mean δm along ĝ (CI contains 0); day 1 (excluded from A) differs from days 2+ (kickoff transient).
- **A3, weak coupling.** g_A < 0.5.
- **Verdict rule:** the pair's combined verdict from P1–P4 (`supported` / `failed` / `mixed`), with A1–A3 reported alongside.

## Result
Run 2026-10-03. Pair #37 → #38a, A = 04-03 … 04-13 (56 windows), N = 12.

| Prediction | Observed (90% CI) | Null / rival | Verdict |
| --- | --- | --- | --- |
| A1 push exists | Δ̄ = 0.112 [0.079, 0.141]; every day of A above the free-week mean (0.024), day 2 only just | R0 | ✓ |
| P1 Δᵢ ∝ κ2ᵢ^F | r = +0.20 (perm p = 0.27); cross-split r = +0.29; tilt LOAO error 1.4× translation's | R1 | mixed (right sign, not significant, not proportional; sign flips across robustness variants: +0.36, −0.29, −0.03, +0.21, +0.26, +0.04) |
| P2 variance by the tilt | ε = 1.92 (non-perturbative): **n/a**. Descriptive: ρ = 1.00 [−0.42, 1.94]; ×1.9 vs free week (ρ_Gauss = 0.66); transverse ρ⊥ = −0.12 | synthetic H at ε ≈ 2: ρ ≈ −0.25 to −0.5 | n/a |
| P3 (descriptive) | g 0.62 → 0.58, Δg = −0.04 [−0.53, 0.33] | R5 predicted a *rise* (collaborative) | not counted; no rise |
| P4 (descriptive) | D = −0.06 [−0.16, 0.06] | | not counted |
| A2 stationarity | day 1 is *lower* than days 2+ (−0.036); alignment keeps rising, slope +0.020 [0.010, 0.030] per day | | ✗ (slow ramp, not a step) |
| A3 g_A < 0.5 | g_A = 0.58 [0.05, 0.69] | | ✗ |

Data: `data/processed/H10-goals-are-legendre-pushes/G38/period.json` and `NE34/pairs.json`. Figures: [`figures/shape_and_drift.pdf`](figures/shape_and_drift.pdf) (whole first unit, day 1 included) and the pair figure [`../NE34/figures/pair_37-38.pdf`](../NE34/figures/pair_37-38.pdf). Card: [`../../README.md`](../../README.md).

## Scorecard (period-specific axes)
- **C:** beats R0 only. **D:** P1 inconclusive. **E:** the response is a multi-day ramp, which a static tilt cannot describe.

## Notes
- 2026-10-03: #38's alignment with its goal is still rising 10 days in; NE36 (operator correction on day 1) and per-room kickoffs complicate ĝ. The free week #37 is only 3 days with median 3 statements per agent-window.
