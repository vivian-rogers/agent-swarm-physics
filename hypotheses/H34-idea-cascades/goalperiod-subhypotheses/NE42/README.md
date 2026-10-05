# H34 × NE42: #best and #rest merged on 2026-05-04, split back on 2026-05-11 (A-B-A)

**Verdict:** mixed
**Role:** exploratory (native, round 2; non-reserved data)
**Period:** regime III · G39 (two rooms: #best 4 agents, #rest 11) → G40 (one merged room, 14 agents; GPT-5 alone in #rest) → G41 (the G39 partition again). Each side is also a goal change.

## Why this natural experiment
The merge and split change each group's room size by a known, different amount, and then undo it. The two groups share the goal change, so the difference between groups removes it. This is H34's axis-E test (card, "Round 2 / R2"). NE15 is reserved and is not used.

## Prediction
*Written 2026-10-05 03:50 UTC in the main card (commit 62577cc), before any group-level statistic.* Rule: source-based branching R_src ∝ (N − 1)^0.451 (round-1 cross-period dilution fit).
- Merge: old #best ×1.94 (N 4 → 14), old #rest ×1.13 (11 → 14). Split: new #best ×0.52, new #rest ×0.89.
- A-B-A contrast D = DiD(merge) − DiD(split) = +1.09 (R2-P2).
- Merged week: per-pair rate for pairs from different old rooms equals that for pairs from the same old room, ρ = 1 (R2-P3).
- Verdict rule: supported if R2-P1 (β > 0 with lower CI > 0, CI includes 1) and R2-P2 pass; failed if β's upper CI < 0.3 and D ≤ 0; mixed otherwise. Amendment R2-A2 (before real data): skeleton worlds without per-read dilution give D 1.2–2.6 and β 1.4–2.5, so D and β are read against those references.

## Result
| Prediction | Observed (95% CI) | Reference | Verdict |
| --- | --- | --- | --- |
| merge, old #best Δ ln R_src | +1.56 [+1.10, +2.33] (0.069 → 0.329) | law +0.66 | larger than the law |
| merge, old #rest Δ ln R_src | +0.90 [+0.73, +1.08] (0.089 → 0.219) | law +0.12 | larger than the law |
| split, new #best Δ ln R_src | −0.49 [−0.63, −0.37] (0.329 → 0.201) | law −0.66 | direction as predicted |
| split, new #rest Δ ln R_src | +0.14 [+0.05, +0.21] (0.219 → 0.251) | law −0.12 | wrong sign |
| R2-P2 A-B-A contrast D | **+1.29 [+0.74, +2.11]** | law +1.09; skeleton 1.2–2.6 | **pass** (not specific) |
| R2-P1 slope β (6 boundaries, 14 groups) | 1.50 [−0.10, 3.10] | law 1; skeleton 1.4–2.5 | **inconclusive** (CI includes 0) |
| R2-P3 merged-week ρ (old-cross / old-same) | **1.05 [0.97, 1.15]** (1,902 transmissions) | rooms only route reading: 1; skeleton 0.83–1.14 | **pass** |

- The group that gained most room size (#best, ×4.3 in N − 1) gained most branching, and lost it at the split: the reversal holds.
- Both groups' R_src rose in the merged week far beyond the room-size rule; that common rise is the goal change (#40 "connect worlds"), absorbed by the difference.
- The size of the contrast sits between the dilution law and the skeleton's constant-per-read value, so it does not tell them apart.
- Inside the merged room, agents adopt from former other-room agents at the same per-pair rate as from former room-mates. Old room membership leaves no trace beyond who reads whom.

Data: `data/processed/H34-idea-cascades/r2/ne/` (`groups.parquet`, `summary.json`, `synth.parquet`). Code: `analysis/r2_ne.py`. Figure: `../../figures/r2_obs.pdf` (b).

## Scorecard (period-specific axes)
E (interventional): the A-B-A reversal is predicted in sign and size (D +1.29 vs +1.09), but the skeleton without dilution also predicts it, so E rises to 1, not 2. G: rooms act on idea spread only through reading (ρ 1.05).

## Notes
- Groups: agents present on both sides, keyed by modal room; GPT-5 (alone in #rest during #40) is excluded (N = 1).
- R_src counts tree offspring of the group's first uses, wherever they land. It is not net of convergence.
- CIs: Poisson idea bootstrap with one weight draw per period, shared by the groups of that period.
