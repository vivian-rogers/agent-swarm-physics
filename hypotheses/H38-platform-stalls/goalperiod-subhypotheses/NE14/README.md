# H38 × NE14: the regime II → III boundary (2026-03-24: perma computer use, consolidation, pause tool)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout; transition exception c)
**Period:** last regime-II days (#35, 2026-03-16 → 03-20, and #36a, 03-23) vs first regime-III days (#36b, 03-24 → 03-27, and #37, 03-30 → 04-01). Each side is one window with its own present population.

## Why this period
The scaffold change that introduced CONSOLIDATE every ~40 actions and the self-pause tool. If equal-time co-activation is mostly scaffold synchrony, the jump in the raw gain across this boundary (H19: regime-III activity gains are higher) should be carried by scaffold states, and should shrink once they are conditioned on. NE30 (03-05 → 03-16) is held out, so the regime-II side starts at #35.

## Prediction
*Written 2026-10-04 01:43 UTC, before running H38 across this boundary (the card's P9).*
- Raw g_eq active rises across the boundary: Δ_raw = E_III − E_II > 0.
- The stall-adjusted rise is at most half of it: Δ_adj ≤ Δ_raw / 2 for g_stall (as written) and for the headline g_mask_scaffold (Amendment 2).
- Against it: no raw rise, or an adjusted rise that keeps most of the raw rise.

## Result
Regime II side: 6 days, N = 12, JS share 0.031, stall share 0.003. Regime III side: 7 days, N = 12, JS share 0.277, stall share 0.262.

| Variant | E regime II (z) | E regime III (z) | Δ = III − II [95% CI, day bootstrap] |
| --- | --- | --- | --- |
| raw | 0.101 (2.7) | 0.251 (6.6) | +0.150 [+0.070, +0.230] |
| lull | 0.106 (2.6) | 0.109 (2.6) | +0.003 [-0.232, +0.238] |
| stall | 0.094 (2.5) | 0.107 (2.7) | +0.012 [-0.113, +0.138] |
| field | 0.094 (2.5) | 0.107 (2.6) | +0.012 [-0.118, +0.143] |
| mask_edge | 0.085 (2.3) | 0.090 (2.3) | +0.005 [-0.101, +0.112] |
| mask_infra | 0.055 (1.4) | 0.079 (2.1) | +0.024 [-0.106, +0.154] |
| mask_scaffold | 0.055 (1.4) | -0.004 (-0.1) | -0.060 [-0.185, +0.066] |
| mask_all | 0.031 (0.8) | -0.044 (-1.2) | -0.076 [-0.152, +0.001] |
| *sensitivity (post hoc): regime-III side without 2026-03-31 (513-min scheduled gap); stall share 0.044* | | | |
| raw (no 03-31) | 0.101 (2.7) | 0.224 (5.6) | +0.122 [+0.038, +0.207] |
| stall (no 03-31) | 0.094 (2.5) | 0.097 (2.4) | +0.003 [-0.134, +0.139] |
| mask_edge (no 03-31) | 0.085 (2.3) | 0.090 (2.3) | +0.005 [-0.105, +0.114] |
| mask_scaffold (no 03-31) | 0.055 (1.4) | -0.022 (-0.5) | -0.078 [-0.215, +0.059] |
| mask_all (no 03-31) | 0.031 (0.8) | -0.052 (-1.2) | -0.083 [-0.162, -0.004] |

Prediction: Δ_raw > 0 (✓); Δ_stall ≤ Δ_raw/2 (✓); Δ_mask_scaffold ≤ Δ_raw/2 (✓). Data: `data/processed/H38-platform-stalls/NE14/result.json`.

## Scorecard (period-specific axes)
- **E:** the raw jump is carried by scaffold states (one boundary; 6 vs 7 days). Conditioning on day edges alone (`mask_edge`: off-schedule minutes dropped, not-started / finished agent-minutes imputed) already removes the jump, with or without 03-31: the regime-III rise is agents starting and stopping together, not consolidation or pause synchrony.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
