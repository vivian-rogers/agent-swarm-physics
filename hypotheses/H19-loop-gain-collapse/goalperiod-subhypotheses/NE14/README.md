# H19 × NE14: regime II → III (2026-03-24), with and without the day-edge adjustment

**Verdict:** failed
**Role:** native
**Period:** last regime-II days (#35, #36 on 03-23; 6 days) vs first regime-III days (#36 from 03-24, #37; 7 days), N = 12 on both sides (H02 population rule). Transition exception (c).

## Why this period
Round 1's headline structure for H19 was the scaffold switch: talk gains fell while activity co-activation rose (g_eq active +0.11 regime III − I). H38 then attributed about two thirds of regime-III co-activation to the operator's day edges and showed the II → III rise vanishing under agent-state conditioning (NE14 +0.15 → +0.01; H19's +0.11 → +0.017), on the old tables.

## Prediction
*Not blind (disclosed): the round-1b NE14 run (2026-10-04 06:37 UTC) re-computes H38's published design on the corrected tables, so the prediction is H38's round-1 result:* the regime II → III rise in the activity gain (E = g − N1 surrogate mean) is significant raw and disappears (|ΔE| within its CI of 0) under the DQ8 trim and under H38's agent-state conditioning; the talk gain does not rise.
Verdict rule (for H19's round-1 reading "activity co-activation rises across the switch"): **supported** if the adjusted ΔE > 0 with a CI excluding 0; **failed** otherwise.

## Result
`analysis/r1b_ne14.py` → `data/processed/H19-loop-gain-collapse/r1b/NE14/result.json`. E = g − mean of 200 joint N1 surrogates drawn after the masks; ΔE = E_III − E_II ± 1.96 day-bootstrap SE.

| Channel · version | Old tables (round-1 inputs): E_II → E_III | **ΔE old** | Fixed tables: E_II → E_III | **ΔE fixed** |
| --- | --- | --- | --- | --- |
| activity · raw (round-1 definition) | 0.10 → 0.25 | **+0.145 ± 0.083** | 0.19 → 0.31 | **+0.112 ± 0.177** |
| activity · DQ8 trim (all-present window, stall mask) | 0.07 → 0.04 | −0.024 ± 0.117 | 0.15 → 0.07 | −0.080 ± 0.214 |
| activity · H38 agent-state conditioning | 0.05 → −0.01 | −0.062 ± 0.132 | 0.19 → 0.05 | −0.140 ± 0.280 |
| talk · raw | 0.18 → 0.14 | −0.033 ± 0.115 | 0.15 → 0.22 | +0.061 ± 0.092 |
| talk · DQ8 trim | 0.14 → 0.12 | −0.022 ± 0.156 | 0.12 → 0.20 | +0.084 ± 0.113 |

- **Old tables:** H38's result reproduces (+0.145 raw, gone under either adjustment).
- **Fixed tables:** the raw rise is smaller relative to its day-to-day spread and no longer excludes 0; under the day-edge adjustments the activity gain *falls* across the switch (point estimates −0.08, −0.14). The trim keeps 98% of regime-II minutes but only 70% of regime-III minutes: the regime-III excess sits in the edges.
- Dropping 2026-03-31 (a 513-min operator-off gap) changes nothing (raw +0.107, trim −0.074).
- **Verdict: failed** for H19's round-1 reading: there is no regime II → III rise in activity co-activation once day edges are handled, on old or fixed tables. The "opposite-sign channels" pattern of round 1 was the scaffold's day edges.

## Notes
- βJ₀ = g/q units for H02 are in the same file (`d_bJ0`): fixed tables raw +0.16, trim −0.23, conditioned −0.21.
