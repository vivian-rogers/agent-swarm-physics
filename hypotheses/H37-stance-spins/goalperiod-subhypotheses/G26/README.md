# H37 × G26: Elect a village leader (2026-01-05 → 2026-01-12)

**Verdict:** failed (stance does not track ballots; no factions)
**Role:** replication (exploratory)
**Period:** regime I · mode C · 10 agents · one room · 5 days. Approval voting over several candidates, then a runoff won by DeepSeek-V3.2 (H11 G26: abrupt jump 0.18 → 0.80).

## Why this period
An election is the one non-debate period with an explicit, recorded partisan structure (declared votes, H11). If stance tracks factions, voters with similar ballots should treat each other more positively, and rival candidates less.

## Prediction
*Written 2026-10-04 01:53 UTC, before running on this period (card predictions P10–P11).*
- **P10:** residual stance coupling correlates with ballot similarity (Jaccard of declared candidate sets), Mantel r > 0, p < 0.05, and more strongly than residual topic coupling. [0.3]
- **P11 (descriptive):** rival-candidate pairs (each named by ≥ 2 distinct voters) have lower residual stance than other pairs, permutation p < 0.05. [0.25]
- Expected backdrop: a cooperative election, few negative replies; a vote stated in reply to a candidate is labelled "support" by construction (a mechanical endorsement link, disclosed).

## Result
*Run 2026-10-04 (`analysis/explore.py`, `analysis/calibrate.py`; data `G26/results.json`; figure `figures/g26_winner_stance.pdf`).* 4,369 relevant replies among 10 agents; all 45 pairs have ≥ 3 replies.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P10 Mantel(residual stance, ballot similarity) > 0, p < 0.05, and > topic | r = +0.01 (topic −0.24) | agent permutation p = 0.47 | **fail** |
| P11 rival candidates lower stance | untestable as written: all 10 agents were named by ≥ 2 voters, so there are no non-rival pairs | | n/a |

**Power (synthetic S4, Jev noise):** Mantel power 0.25 at a ballot-similarity coupling of 1 logit, 0.42 at 2, 0.83 at 4; the failure rules out only a strong stance–ballot link.

**Detector.** Oppose/undermine share 7.7% [6.4, 9.4]; no significantly negative pair (calibrated null 0.03); camps p = 0.91 (calibrated); ARI of the stance split with modal-vote blocs −0.08. One agent flagged as an unusually negative replier (GPT-5.2, z_given −2.3); descriptive.

**Descriptive.** Stance toward the eventual winner (DeepSeek-V3.2) dips on the runoff day (01-09: +0.21 vs +0.30–0.52 earlier), the only sign of contention.

**Reading.** The election was cooperative in stance: approval voting among LLM agents did not create stance factions that the labeller can see.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | no statistic beats its null |
| G ground truth | 0 | vote blocs not recovered (ARI −0.08) |

## Notes
