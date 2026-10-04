# H01 × G12: Debate tournament, drafted teams as known coarse-grained units (2025-09-01 → 09-05)

**Verdict:** failed (native, round 1b)
**Verdict (1b):** failed (no team unit beyond the re-partition null, both models)
**Role:** native
**Period:** regime I · mode K (competition) · N = 7 · one room (#general) · 10 debates on 09-01 → 09-04 (unit 12a); teams re-drafted every debate (except #7 = #6), one judge per debate, sides Government (pro) vs Opposition (con). Ground truth: DQ6 `ground_truth_labels` (team 60, judge 10, phase 30 rows; `preferred & ~holdout`).

## Why this period
DQ9's leverage for H01: **10 replicate two-team samples with known labels**, to ask whether a drafted team behaves as one coarse-grained content unit. Re-drafting moves the same agent across sides, so a stable agent field (style, prior) cannot make teams look aligned in every debate; residual style is removed again with DQ5's `style_resid_period` vectors (the family field is style; H13, DQ5). This is round 1's D3.1.a / D3.2 question (is a grouping an ordered unit, through coupling or a shared field?) on a grouping whose membership is known exactly and changes every hour, which no room split offers.

## Design (round 1b native test)
- **Statements:** H01's statements (agents' chat and intentions) posted inside each debate's team window (`team.t_valid_from` → `t_valid_to`: preparation, debate and verdict), restatements removed (round-1b primary dedupe). Debaters only (judge and bench excluded); a debater needs ≥ 2 statements in the window.
- **Vectors:** agent-debate mean of unit statement vectors, four instruments: whitened bge-small, whitened gte-modernbert (H01's per-regime whitening, d = 32), and the style-residualized (within goal period) vectors of both models.
- **Statistic:** T = mean over debates of [mean within-team pair cosine − mean cross-team pair cosine] (the D3.2 room criterion with teams as rooms).
- **Null:** exact re-partitions of each debate's debaters into two groups of the observed team sizes (all of them), drawn independently per debate (20,000 Monte Carlo draws of T); one-sided p. Per-debate sign of the excess is reported.
- The P1 entropy version is not feasible here (1–30 statements per debater per debate; P1 rarefies 8).

## Prediction
*Written 2026-10-04 07:45 UTC, before any statistic was computed on #12 (seen: only the DQ6 label counts, the debate windows' lengths, 13–47 min, and per-debater statement counts, 1–30 chat messages).*
- **N1a:** T > 0 with permutation p < 0.05 in at least 3 of the 4 instruments [0.5].
- **N1b:** within − cross > 0 in ≥ 6 of 10 debates with the style-residualized bge vectors [0.55].
- **Reading:** both → a drafted team is a content unit inside one room (coupling inside the team, or a side-of-the-motion field); T ≈ 0 → the room and the motion, not the team, set what agents say (no team-level superagent in content). Embeddings handle negation poorly (DQ5), so pro and con arguments on the same motion may look alike: a null here does not mean the teams argued the same thing.

## Result
<!-- R1B -->
| instrument | T (raw) | p | debates > 0 | T (centered) | p | debates > 0 |
| --- | --- | --- | --- | --- | --- | --- |
| bge_restate | +0.043 | 0.133 | 7/10 | +0.068 | 0.216 | 5/10 |
| gte_restate | +0.027 | 0.156 | 5/10 | +0.055 | 0.239 | 5/10 |
| bge_restate_style | +0.037 | 0.072 | 6/10 | +0.093 | 0.103 | 6/10 |
| gte_restate_style | +0.023 | 0.103 | 7/10 | +0.070 | 0.142 | 7/10 |

**N1a failed** (p < 0.05 in 0 of 4 instruments; p 0.07–0.24). **N1b passed by the letter** (6/10 debates positive with style-residualized bge), which with T's null-level p means no team-level content unit beyond chance: inside one room, the motion and the room, not the drafted team, set what agents say.

Data: `data/processed/H01-emergent-superagents-exist/r1b/native.json`.
<!-- /R1B -->

## Notes
- 2026-10-04: folder created for the round-1b native layer (DQ9 cross-index: H01 → #12). Round 1 had no #12 test.
