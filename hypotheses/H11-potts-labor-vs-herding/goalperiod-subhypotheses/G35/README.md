# H11 × G35: Test your game (forked per room) (2026-03-16 → 2026-03-20)

**Verdict:** supported (work herds)
**Verdict (1b):** supported (work herds)
**Verdict (r2):** R3 herding raises output G35: n.e.; θ < 1 G35: no
**Role:** replication (round 1b work space; templated prediction)
**Period:** regime II · 12 agents · #best / #rest (separate forks of the #34 RPG) · 5 active days.

## Why this period
Not tested in round 1 (not a card candidate or transfer period). Round 1b adds it because the DQ4 work ledger is dense from #30 on: the work-space version of H11's coupling statistics (agent state (categorical, project, work ledger)) next to the attention version, to resolve the tension with H06 (private projects) and test HH266. Class for round 1b: one shared fork per room: shared-artifact week within each room.

## Prediction
*Templated from the card's round-1b predictions R1b-2 (written 2026-10-04 07:10 UTC, before the work-space run).*  Shared-artifact weeks: work herds (βJ_CW(work) > 0, z_N2(work) ≥ 2), more weakly than attention. Own-artifact weeks: spread by fields in work (βJ_CW ≤ 0, z_N2 < 2). Minimum data: ≥ 15 room blocks with ≥ 3 labelled agents at W = 30. HH266 ("attention herds, work stays private") predicts z_N2(work) < 2 where attention herds.

## Result
`analysis/round1b.py work` → `data/processed/H11-potts-labor-vs-herding/r1b/work/G35.json` (99 nulls; 49 for #51 units). Co-location = share of labelled agents whose raw project is shared by ≥ 1 room-mate in the same 30-min window, vs its circular-shift (N2) mean.

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 399 | 71 | +5.24 (+7.9) | -2.5 | -2.4 | -0.58 | 0.98 (0.98, +1.3) | 0.01 | 0.98 |
| work | 228 | 42 | +8.32 (+0.5) | +2.2 | +1.3 | +2.77 | 1.00 (0.98, +2.5) | 0.00 | 0.98 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | work-space coupling vs the null hierarchy (table above) |
| I transfer | 0 | round-1 pattern (shared → herding; own → spread) contradicted in attention (z_N2 −2.5) in a period round 1 did not use |

## Notes
- **Against the round-1 pattern in attention:** a shared week (ownership 0.01) with z_N2(attention) = −2.5 (coupling below the circular-shift null; q = 2, one fork per room), while work has z_N2 = +2.2. With only two real states and each room on its own fork, room membership makes occupancies steadier than the shift null. The frozen confirmatory clause C2 ("refuted if any shared-artifact target has z_N2 < 0") would fail on a week like this.

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit | log RR herd vs solo, commits (R3a) | landed | matched pairs (mean log ratio) | θ crowding (R3b) | herd / solo windows |
| --- | --- | --- | --- | --- | --- |
| G35 (shared) | n.e. | n.e. | – | +0.98 [+0.51, +1.45] | 37/7 |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
