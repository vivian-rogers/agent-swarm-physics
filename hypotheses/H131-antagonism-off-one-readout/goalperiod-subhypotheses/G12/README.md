# H131 × G12: the debate week (#12, 2025-09-01 → 2025-09-08)

**Verdict:** supported
**Role:** exploratory (replication + natives N1–N3)
**Period:** regime I · mode M · 7 agents · one room · 10 judged debates on 2025-09-01 → 09-04 (unit 12a), each with DQ6 teams, a judge, phases (pre / deb / post) and a dated verdict message.

## Why this period
The only non-holdout period with many dated settlements of an assigned, rival-exclusive prize (10 verdicts) and rival pairs that are re-drafted each debate. H64 found the opponent contrast switches off after the verdict; H131 asks whether it switches at each agent's read-out of the verdict, and within its first post-read call.

## Prediction
*Written 2026-10-04 ~22:25 UTC, before running on this period.*
Structural facts seen before writing (no stance values): verdict read delays per debate median 10–66 s (max 366 s); **0 in-flight rival replies** (no rival reply posted after a verdict was produced by a call assembled before its speaker's read).
- **P1 (replication, read-aligned DiD, flag outcome):** Δ̂ < 0 with relation-permutation p < 0.05; γ_set CI contains 0 and |γ̂_set| < ½|γ̂_open|. Credence 0.7.
- **N1 (HH kill test):** in-flight rival replies keep the open rate. **Untestable here (0 in-flight rival replies).** The kill cannot fire.
- **N2 (one read-out):** r(k = 1) − r(k ≥ 2) 90% CI contains 0 and r(k = 1) < r_open (one-sided permutation p < 0.05). Credence 0.45. Counts against: r(k = 1) ≥ r_open.
- **N3 (switch-on):** after reading the team assignment (`pre` message), the rival flag rate at k = 1 is not below the `deb` rival rate (difference CI contains 0 or is above 0). Credence 0.4. Counts against: CI below 0 (antagonism builds up).
- Period verdict: supported if P1 and N2 pass; mixed if one passes; failed if P1 fails toward R-relation or N2 fails toward remanence; inconclusive if both are underpowered and neither passes.

## Result
*Run 2026-10-04 ~23:03 UTC, after Amendment A1 (flag outcome `disagree_validated_agent`; Δ > 0 = antagonism while open; N2 on each speaker's first post-read rival reply).*

| Prediction | Observed (95% CI unless noted) | Null | Verdict |
| --- | --- | --- | --- |
| P1 read-gated DiD | Δ +0.32 [+0.16, +0.52]; γ_open +0.35 [+0.23, +0.52]; γ_set +0.03 [−0.04, +0.18] | relation permutation p 0.0002 | **pass** |
| P1 (soft p_disagree) | Δ +0.31 [+0.15, +0.50]; γ_set +0.03 [−0.01, +0.18] | p 0.0004 | pass |
| N1 in-flight partition (kill test) | 0 in-flight rival replies (0 in-flight replies of any kind) | — | **untestable** |
| N2 first post-read rival reply | 0/21 flagged vs later post-read 0/36 vs open (`deb`) 33/74 = 0.45; difference CI (90%) [0, 0] | open > first: permutation p 0.0002 | **pass** |
| N2 (soft) | first 0.031 vs later 0.001 (90% CI of difference [+0.006, +0.058]); open 0.45 | — | residual ≈ 7% of the open level |
| N3 switch-on (descriptive after A1) | first rival reply after reading the assignment 16/36 = 0.44 vs later `deb` 18/46 = 0.39 (90% CI of difference [−0.14, +0.24]) | — | descriptive |

**Cell counts (flag):** rivals while open 34/85 (deb 33/74, pre 1/11); teammates while open 0/87; rivals after their read 0/57; teammates after 0/33. Every one of the 34 flags in the debate windows is a rival reply while the prize is open.
**Read-out timing:** verdict read delay median 20 s (90th percentile 132 s, max 366 s). The first post-read rival reply comes a median 93 s after the verdict, at post-read talk call k = 2 (only 6 rival replies sit at k = 1).

**Reading:** stance antagonism between drafted rivals is on while the prize is open (40% of their replies carry a validated disagreement, 0% of teammates' replies) and is fully off by each speaker's first reply after it reads the verdict. Because no reply falls between the verdict instant and its speaker's read, the read alignment and the wall-clock alignment cannot be told apart here.
Data: `data/processed/H131-antagonism-off-one-readout/results/results.json`.

## Scorecard (period-specific axes)
- **C: 2.** The DiD beats team permutation and two-way agent effects.
- **D: 1.** The first-reply switch-off was predicted, not fitted; the read alignment itself is untestable.
- **E: 1.** Ten dated verdicts.
- **G: 2.** DQ6 teams and verdicts.

## Notes
- The `post` phase is also the end of the debate protocol, so the drop may be a topic change as well as a field removal (H37's protocol rival). The teammate contrast (0/87 while open) shows the antagonism is relation-specific while open.
