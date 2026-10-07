# H142 × NE42: the #best/#rest merge and split back (2026-05-04 / 2026-05-11)

**Verdict:** descriptive
**Role:** exploratory (native N2)
**Period:** #39 (2026-04-27 → 05-04, two rooms) → #40 (05-04 → 05-11, one merged room #universe-coordination; GPT-5 alone in #rest) → #41 (05-11 → 05-18, the same two rooms again). Regime III. Each side is its own goal period, so the design compares fitted parameters across the boundary (CLAUDE.md exception (c)).

## Why this natural experiment
The merge raised batch sizes about ×1.5 at fixed agents (H113 N3), with no change in scaffold. If saturation is a property of how a reader turns aligned reads into a step (a field-to-moment response), n_sat should not move when k grows. A linear channel diluted by k would instead change the per-read step.

## Prediction
*Written 2026-10-07 ~12:30 UTC, before running. Seen: H113's NE42 result (|Δb̂| ≤ 0.09 while k ×1.5, weak: one side identified; #39 is field-identified in bge, #40 is not listed as identified).*
- **N2:** |ln n̂_sat(#40) − ln n̂_sat(#39)| < ln 1.5, and the same for #41 vs #40. Credence 0.3.
- Counts against: a change ≥ ln 1.5 with CI excluding 0.
- If #40 fails H113's field identification (read − in-flight contrast not > 0), N2 is descriptive.
- Confound: each boundary is also a goal change (new kickoff), so a shift in n_sat cannot be blamed on the merge alone.

## Result
*Round 1, 2026-10-07 (exploratory). Descriptive by the folder's own rule: #40 is not field-identified by H113, and no NE42 side has power ≥ 0.8 (after A4: bge #39 0.47, #40 0.62, #41 0.63; gte 0.64, 0.70, 0.68). n̂_sat sits on a grid edge (0.1 or 150) on most sides, so no side has an identified saturation scale.*
- **bge**: mean ledger k 6.3 (#39) → 10.2 (#40) → 6.7 (#41).
  - 39 → 40: n̂_sat 150.00 → 0.10; Δ ln n̂_sat -7.31 [-7.31, 6.09]; |Δ| < ln 1.5: False; counts against: False.
  - 40 → 41: n̂_sat 0.10 → 150.00; Δ ln n̂_sat 7.31 [-3.66, 7.31]; |Δ| < ln 1.5: False; counts against: False.
- **gte**: mean ledger k 6.3 (#39) → 10.2 (#40) → 6.7 (#41).
  - 39 → 40: n̂_sat 21.34 → 150.00; Δ ln n̂_sat 1.95 [-5.12, 4.70]; |Δ| < ln 1.5: False; counts against: False.
  - 40 → 41: n̂_sat 150.00 → 0.90; Δ ln n̂_sat -5.12 [-7.31, 5.12]; |Δ| < ln 1.5: False; counts against: False.

## Scorecard (period-specific axes)
E: 0 (descriptive; unpowered sides).

## Notes
- GPT-5's calls in #rest during #40 are excluded (one agent in a separate room).
