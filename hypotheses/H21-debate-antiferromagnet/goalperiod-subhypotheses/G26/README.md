# H21 × G26: Elect a leader who sets the goal (2026-01-05 → 01-09)

**Verdict:** failed
**Role:** native (round 1b, non-holdout)
**Period:** regime I · one room (#general) · 10 agents · 5 days (one unit). Election rounds (DQ6 `phase`/`ballot`/`tally`, voters recovered from the ballot messages): 01-05 approval vote (9 voters; three candidates tied 9–9–9; the other four approved by 7, 7, 4 and 2) → runoff 7–1–0 in ~100 s (two non-voters) → DeepSeek-V3.2 elected 19:35 UTC; 01-09 confirmatory re-election 9–0.

## Why this period
DQ9: ballots are known camps, per election round. H21's question is whether assigned or chosen sides order as two sublattices. Here sides are chosen, not assigned: the approval ballots define how far apart two voters are. If camps self-organize like the #12 teams, voters with dissimilar ballots should anti-align (stance) or separate (content) during the contest; afterwards (and around the unanimous re-election) the order should vanish.

## Prediction
*Written 2026-10-04 07:14 UTC, before computing any #26 statistic.* Seen before: DQ6's ballots and tallies (design facts above); H37's #26 result with its own labels (stance vs ballot similarity r = 0.01, p 0.47, power 0.25–0.42 at 1–2 logit).

- **Camps.** Ballot dissimilarity d_ij = 1 − Jaccard of the two voters' approval sets (9 approval voters). The runoff split (7 vs 1) is degenerate and reported descriptively.
- **Windows.** Contest = 01-05 up to the result (19:35 UTC); after = 01-05 after the result through 01-08; re-election = 01-09.
- **Stance channel.** DQ2 `reply_pairs` (cand, labelled) between voters in the window; residual pair stance J_ij after speaker and target fields (double-centred soft means, n_ij ≥ 2). Statistic: Mantel correlation r_s = corr(J_ij, −d_ij) (AF order predicts r_s > 0: dissimilar ballots, more negative stance); null: voter-label permutation (exact or 20,000 draws).
- **Content channel.** H21's estimator generalized to graded camps: pair cosine of agent-centred, window-demeaned content means (white32, bge and gte); r_c = corr(cos_ij, −d_ij), same null.
- **Prediction.** Both r_s and r_c n.s. in the contest window (p > 0.05; credence 0.75). Chosen sides in a cooperative vote do not form sublattices. A pass in either channel (r > 0, p < 0.05) would count *for* spontaneous camp order.
- **Power caveat.** 9 voters, 36 pairs; the approval sets are nearly identical on the three tied candidates, so d varies only through the minor candidates.

## Result
*Run 2026-10-04 (round 1b), after the prediction above. Code: `analysis/r1b.py` (`native_g26`); data: `r1b/r1b.json` → `native_G26`.* Voters were recovered from the DQ6 ballot messages (9 approval voters; runoff 7 for DeepSeek-V3.2, 1 for Gemini 2.5 Pro). Ballot dissimilarity takes 8 distinct values (mean 0.27).

| Window | Replies (pairs with ≥ 2) | Stance Mantel r (p>) | Content r bge (p>) | Content r gte (p>) |
| --- | --- | --- | --- | --- |
| contest (01-05 to the result) | 244 (29) | 0.000 (0.51) | −0.065 (0.62) | +0.075 (0.25) |
| after (to 01-08) | 1,444 (35) | +0.010 (0.48) | +0.123 (0.16) | +0.052 (0.31) |
| re-election day (01-09) | 688 (35) | +0.079 (0.30) | +0.152 (0.16) | +0.103 (0.23) |

**Native verdict: failed (as predicted).** Voters with different ballots neither oppose each other in replies nor separate in content during the contest; mean stance stays positive (0.57). Chosen sides in a cooperative vote form no sublattices. Power is low (9 voters; ballots differ only on minor candidates).
