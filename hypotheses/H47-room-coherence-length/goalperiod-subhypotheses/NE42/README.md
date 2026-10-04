# H47 × NE42: #best/#rest merge and split, A-B-A (2026-05-04 / 05-11)

**Verdict:** mixed
**Role:** native
**Period:** #39 (2026-04-27 → 05-01, two rooms) → #40 (05-04 → 05-08, one merged room) → #41 (05-11 → 05-15, two rooms, same partition). Regime III, 15 agents. Not held out.

## Why this period
**A-B-A:** #best/#rest in #39 (A), merged into #universe-coordination for #40 (B; GPT-5 left alone in #rest, Gemini 2.5 Pro joined late on 05-04), split back to the same partition for #41 (A, identical instructions). Goal-confounded (each phase is a new goal; #40's goal is a shared objective). If coherence follows the channel, content correlation between agents of different A-rooms should rise to within-room levels in #40 and fall back in #41. A persistent team identity (a drive following the old partition) predicts the boundary survives the merge. Also two room events for the detector test (05-04 merge, 05-11 split).

## Prediction
*Written 2026-10-04 ~06:10 UTC, before running H47 on these periods.*
- **P7a (primary):** with pairs labelled by the A partition, r_X = ρ_XP/ρ_WP ≤ 0.3 in #39 and #41 and ≥ 0.7 in #40 (w30, L1).
- **P7b:** DiD = r_X(40) − mean(r_X(39), r_X(41)) > 0.4 with partition-permutation p < 0.05.
- **P7c:** residual partition memory in #40: r_X(40) < 0.9.
- **Detector (card P3, Amendment 1):** R1_swarm and the per-room R1 (R1_room) fire within ±1 day of the merge (05-04) and the split (05-11) [goal-confounded].
- **Synthetic reading rule (card Amendment 1, from the run before real data):** under room coupling with a weak global drive, r_X in the A phases is 0.39–0.52, not ≤ 0.3, so P7a's A-phase threshold is strict; the DiD is the informative part (channel worlds: DiD 0.47, > 0.4 in 75%; team-identity worlds: DiD −0.06).
- **Against:** r_X(40) ≈ r_X(39) ≈ r_X(41) (the boundary is a team identity, not the channel).

## Result
| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| P7a (primary): r_X ≤ 0.3 in #39 and #41, ≥ 0.7 in #40 | #39 0.57 · #40 1.37 · #41 0.17 (ρ_XP / ρ_WP: 0.048/0.085, 0.251/0.184, 0.064/0.367) | partition-permutation medians 0.99, 1.03, 1.04; one-sided p (r_X low) 0.094, 0.963, < 0.001 | not met (#39 above 0.3; #40 and #41 as predicted) |
| P7b: DiD = r_X(40) − mean(r_X(39), r_X(41)) > 0.4, p < 0.05 | **DiD 1.00** [day bootstrap 0.50, 1.34], p < 0.001 | 1,000 joint partition permutations | **met** |
| P7c: residual partition memory in #40 (r_X < 0.9) | r_X(40) 1.37: cross-partition pairs correlate *more* than within-partition pairs | – | not met (no memory) |
| Detector, 05-04 merge (goal-confounded) | R1_swarm z 5.17 (hit); R1_room undefined (new room, the old #rest held one agent); R1_loc 0.67 | placebo FAR 0 at z ≥ 3 (11 multi-room placebo days) | R1_swarm only |
| Detector, 05-11 split (goal-confounded) | R1_swarm 9.02, R1_room 17.64 (both hit); R1_loc 2.68 | – | both fire |
| Leadership at #40 (cohorts = previous rooms) | L 0.19, p 0.196 (a level offset: ex-#best closer to its later content all day) | – | no lead |

Partition: 4 #best and 11 #rest agents with the same modal room in #39 and #41 (none dropped).

**Reading.** The strongest result of round 1. Content coherence follows the chat channel: agents from different A-rooms correlate at about 0.57× and 0.17× the within-room level while separated, and at 1.37× once merged, then drop back the week after (DiD 1.0, p 0.001). A persistent team identity (synthetic: DiD ≈ −0.06) is rejected. The pre-registered A-phase threshold (≤ 0.3) fails only in #39, as the synthetic warned (A-phase r_X 0.39–0.52 under coupling with a weak global drive). Caveats: every phase is a new goal (#40 a shared objective, which by itself raises cross-pair correlation as a global drive), and N = 15 agents.

Figure: `figures/NE42_h47.pdf`. Data: `results/ne42.json`, `results/detector.json`.

## Scorecard (period-specific axes)
- **C:** DiD beats 1,000 joint partition permutations (p 0.001).
- **D:** an unfitted, pre-registered contrast (P7b) met.
- **E:** the A-B-A is the interventional test: the boundary follows the channel (goal-confounded).
- **H:** beats the team-identity rival; R-global not excluded for #40 itself (shared objective).

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only). Verdict mixed by the pre-registered rule (P7a fails at #39); the informative DiD (P7b) is met.
