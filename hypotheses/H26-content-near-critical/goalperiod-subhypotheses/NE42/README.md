# H26 × NE42: Content room excess under the old partition across merge and split (#39 → #40 → #41)

**Verdict:** supported (native, round 1b)
**Verdict (1b):** supported (content and talk, both models; activity uninformative)
**Role:** native
**Period:** regime III · #39 (two rooms, 04-27 → 05-01), #40 (one merged room from 05-04; GPT-5 alone in #rest), #41 (split back to the same partition, 05-11 → 05-15). N = 15 at a fixed roster. #40 is a shared-objective week (goal-confounded).

## Why this period
DQ9: "content loop gain in one vs two rooms" (H26-R1 in round 1's redirects). Round 1 could not separate room coupling from room-specific drives (L3 reads unmeasured room drives as coupling one-for-one). The A-B-A changes the channel at a fixed roster: if the room excess is coupling through the room channel, the excess measured with the **#39 partition as pseudo-rooms** should vanish in #40 (everyone can read everyone) and come back in #41. If it is a drive attached to agents (each agent's own task, style), it should persist.

## Design (round 1b native test)
- Pseudo-room = each agent's modal #39 room (best / rest), applied to every slot of #39, #40 and #41; GPT-5 excluded.
- H26's pre-registered estimator on round-1b inputs: g_ex = room excess (L3 = L2 deviations, within minus cross pseudo-room, normalized by the cross-room share), split-half signal variances; resolutions day and w30; channels content (restatements removed; bge-small and gte-modernbert), activity and talk (fixed `activity_bins`, outage windows dropped).
- CIs: day bootstrap (400 draws). The difference #40 − mean(#39, #41) is reported with a bootstrap over days within periods.

## Prediction
*Written 2026-10-04 07:45 UTC, before running the pseudo-room estimator on any of the three periods. Not blind: I have seen H26 round 1 (#39 content L3 0.45, #41 0.77; #40 whole-room content 0.75 vs activity 0.90) and H47's NE42 coherence result (0.57× → 1.37× → 0.17×).*
- **N1a (content, w30):** pseudo-room g_ex in #40 < 0.15, while #39 and #41 are ≥ 0.3 [0.55].
- **N1b (activity, w30):** pseudo-room activity excess changes by less than 0.2 between #40 and the mean of #39 and #41 [0.5] (activity co-moves village-wide; the channel does not carry it).
- **N1c (talk, w30):** talk's pseudo-room excess collapses in #40 like content (< 0.15) [0.45].
- **Reading:** N1a → the content room excess is channel-borne (coupling or a room task drive that the merge removes); a persistent excess → an agent-attached drive. The shared objective in #40 is a confound in the same direction as coupling.

## Result
<!-- R1B -->
| run | period | content day | content w30 | activity w30 | talk w30 | content w30 ρ_w / ρ_c |
| --- | --- | --- | --- | --- | --- | --- |
| bge_fixed | #39 | 0.49 | 0.36 | < −1 | 0.80 | 0.14 / 0.05 |
| bge_fixed | #40 | < −1 | < −1 | -0.03 | < −1 | 0.21 / 0.29 |
| bge_fixed | #41 | 0.76 | 0.71 | 0.43 | 0.74 | 0.42 / 0.07 |
| gte_fixed | #39 | 0.52 | 0.41 | – | – | 0.11 / -0.00 |
| gte_fixed | #40 | < −1 | < −1 | – | – | 0.23 / 0.34 |
| gte_fixed | #41 | 0.78 | 0.74 | – | – | 0.44 / -0.01 |

Pseudo-room excess g_ex with the #39 partition (GPT-5 excluded); '< −1' = cross-partition pairs co-move more than within-partition pairs. **N1a passed** (both models), **N1c passed** (talk), **N1b uninformative** (activity's pseudo-room excess is already negative in #39). The room excess is channel-borne; #40's shared objective confounds.
<!-- /R1B -->

## Notes
- 2026-10-04: folder created for the round-1b native layer. Round 1's #40 descriptive result stays in [`G40/`](../G40/README.md).
