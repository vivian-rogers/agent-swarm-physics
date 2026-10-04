# H22 × G23: Chess tournament (2025-12-15 → 12-19)

**Verdict:** failed
**Role:** native (round 1b, non-holdout)
**Period:** regime I · one room (#general) · 10 agents · 5 days (one unit) · agents play each other on Lichess; 78 distinct game ids are linked by agents (DQ4 `work_outcomes`).

## Why this period
DQ9: explicit pairwise antagonism with known pairs. In #51 "conflict" was a coded relation between roles; here two agents sit across a board, a zero-sum game with a winner. If antagonistic objectives make negative couplings anywhere (H22's mechanism), chess opponents are the cleanest case: same room, same goal, a direct opponent. The homophily rival says opponents talk about their shared games and co-move positively.

## Prediction
*Written 2026-10-04 07:15 UTC, before building the opponent list or computing any #23 statistic.*

- **Opponent pairs (rule fixed now).** Lichess game ids (`lichess.org/<8 characters>`) are extracted in memory from #23 agent chat, intentions and command texts; a pair of agents are **opponents** if both link the same game id (≥ 1 shared id). Only codes are stored (agent pairs and counts). If fewer than 5 opponent pairs result, the test is **untestable**.
- **Stance channel (primary).** DQ2 `reply_pairs` (cand, labelled) within #23; residual pair stance after speaker and target fields (two-way fixed effects on soft stance s = p_supports − p_opposes, weighted by p_reply). T_opp(stance) = mean residual over opponent pairs − mean over non-opponent pairs.
- **Content channel.** H22's within-day co-movement J^c on day-thirds pseudo-days (5-day unit; regime I whitened, bge and gte white32); T_opp(content) likewise.
- **Null.** Node-label permutation of the opponent graph (agents relabelled, graph structure kept), 10,000 draws; one-sided in each direction reported.
- **Prediction.** H22's direction (T_opp < 0, p_less < 0.05) in stance: credence 0.15; the homophily rival (T_opp > 0, p_greater < 0.05) in content: credence 0.4; otherwise null.
- **Reading.** A negative stance contrast would be the first antagonism tied to a known adversarial relation outside assigned debate teams; a positive content contrast replicates #51's homophily in a zero-sum setting.

## Result
*Run 2026-10-04 (round 1b), after the prediction above. Code: `analysis/r1b_stance_native.py` (`g23`); data: `r1b/stance_native.json` (`native_G23`); unit `23` built by `scheme/build.py`'s round-1b settings (regime-I white32, bge and gte). Only agent codes and counts are stored.*

- **Opponent list (rule as written):** 1,139 game-id links, 78 distinct games, 28 linked by ≥ 2 agents (1 by 3), giving **21 opponent pairs** among 10 agents (testable).

| Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| Stance: T_opp < 0 (p_less < 0.05) | residual stance of opponents − other pairs = **−0.005** (21 vs 23 pairs with ≥ 2 replies); p_less 0.42; mean soft stance 0.25 | node-label permutation (10,000) | **fail** |
| Content (homophily rival): T_opp > 0, p_greater < 0.05 | +0.030 (bge, p_greater 0.083), +0.020 (gte, 0.19); mean J 0.065 / 0.080 | node-label permutation | n.s. (homophily sign) |

**Reading.** Sitting across a chess board does not make two agents treat each other worse; replies between opponents are as friendly as any other pair's, and what they talk about co-moves slightly more (their shared games), not significantly. Explicit zero-sum pairing produces no antiferromagnetic coupling in either channel.

## Scorecard (period-specific axes)
- **G (ground truth):** opponent pairs from shared game links; no antagonism in stance or content. Score 1 (known structure tested; the model's sign absent).
