# H38 × NE14: the regime II → III boundary (2026-03-24: perma computer use, consolidation, pause tool)

**Verdict:** supported
**Verdict (1b):** supported (round 1: supported; raw jump +0.150 → +0.116, interval now includes 0)
**Role:** native (round 1b re-run with the DQ8 null and the #36-only pair; round-1 role: exploratory, transition exception c)
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

## Round 1b prediction (corrected tables and the DQ8 null design)
*Written 2026-10-04 06:32 UTC, before re-running NE14 on `activity_bins_fixed` / `outages_fixed`. Seen before: the round-1 result above (old tables) and the DQ8 size table (block-shift / N1 nulls on whole-day grids reject 28–34% of independent swarms; 2–4% after trimming to the all-present window).*
- **R1b-a (replication of P9).** Δ_raw > 0, and Δ_stall ≤ Δ_raw/2 and Δ_mask_scaffold ≤ Δ_raw/2, as in round 1.
- **R1b-b (corrected null).** With rows outside the all-present window removed before the block-shift surrogates, the regime-III side has no significant excess (z_trim < 2) and the trimmed rise is at most half the raw rise (Δ_trim ≤ Δ_raw/2).
- **R1b-c (#36 only; DQ9 native: same goal across the boundary).** 03-23 (regime II) vs 03-24 → 03-27 (regime III): Δ_raw > 0 and Δ_trim ≤ Δ_raw/2. One regime-II day only, so its interval is not interpretable (descriptive sign test).
- Verdict rule (1b): supported if R1b-a and R1b-b hold; mixed if only one holds; failed if Δ_raw ≤ 0 or neither holds.

## Round 1b result (corrected tables, 2026-10-04)
Regime II side: 6 days, N = 12, JS share 0.002 (round 1: 0.031). Regime III side: 7 days, N = 12, JS share 0.241 (0.277), stall share 0.241. All-present window keeps 98% (II) and 70% (III) of minutes. `data/processed/H38-platform-stalls/r1b/NE14/result.json`.

| Variant | E regime II (z) | E regime III (z) | Δ = III − II [95% CI] | Round 1 Δ |
| --- | --- | --- | --- | --- |
| raw | 0.196 (4.7) | 0.312 (7.7) | +0.116 [−0.043, +0.274] | +0.150 [+0.070, +0.230] |
| stall | 0.196 (4.7) | 0.150 (3.7) | −0.046 [−0.224, +0.131] | +0.012 |
| mask_edge | 0.162 (4.0) | 0.103 (2.6) | −0.059 [−0.250, +0.132] | +0.005 |
| mask_scaffold | 0.188 (4.6) | 0.053 (1.0) | −0.135 [−0.387, +0.117] | −0.060 |
| **trim (DQ8 null)** | 0.156 (3.7) | 0.080 (1.7) | −0.076 [−0.260, +0.109] | – |
| trim_stall | 0.157 (3.9) | 0.079 (1.8) | −0.078 [−0.262, +0.107] | – |
| trim_scaffold | 0.194 (4.7) | 0.046 (1.0) | −0.149 [−0.403, +0.105] | – |
| raw, regime III without 03-31 | 0.196 (4.7) | 0.299 (6.4) | +0.103 [−0.058, +0.263] | +0.122 |
| **#36 only** (03-23 vs 03-24 → 03-27): raw | 0.167 (1.6) | 0.272 (4.5) | +0.105 (one regime-II day) | – |
| #36 only: trim | 0.091 (1.0) | 0.050 (0.9) | −0.041 | – |

| Prediction (1b) | Observed | Verdict |
| --- | --- | --- |
| R1b-a Δ_raw > 0; Δ_stall, Δ_mask_scaffold ≤ Δ_raw/2 | +0.116 (CI now includes 0); −0.046; −0.135 | ✓ (raw rise weaker) |
| R1b-b regime III z_trim < 2 and Δ_trim ≤ Δ_raw/2 | z_trim 1.7; Δ_trim −0.076 | ✓ |
| R1b-c #36 only: Δ_raw > 0, Δ_trim ≤ Δ_raw/2 | +0.105 → −0.041 | ✓ (descriptive) |

**Verdict (1b): supported.** The corrected tables keep the round-1 story (the regime-III rise in co-activation is day-edge synchrony; once the day is trimmed to the common running window, regime III has no significant excess), but the raw jump itself is now smaller and its 95% interval includes 0, because regime II's excess rose more than regime III's once the dropped events came back.

## Scorecard (period-specific axes)
- **E:** the raw jump is carried by scaffold states (one boundary; 6 vs 7 days). Conditioning on day edges alone (`mask_edge`: off-schedule minutes dropped, not-started / finished agent-minutes imputed) already removes the jump, with or without 03-31: the regime-III rise is agents starting and stopping together, not consolidation or pause synchrony.

## Notes
- 2026-10-04: folder created with the prediction, before the run.
