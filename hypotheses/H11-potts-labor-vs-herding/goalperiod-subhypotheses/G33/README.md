# H11 × G33: Pentagon–AI news: discuss, debate, act (2026-03-02 → 2026-03-04)

**Verdict:** supported (work herds)
**Verdict (1b):** supported (work herds)
**Role:** replication (round 1b work space; templated prediction)
**Period:** regime II · 11 agents · one room (#general) · 3 active days · a shared claims database.

## Why this period
Not tested in round 1 (not a card candidate or transfer period). Round 1b adds it because the DQ4 work ledger is dense from #30 on: the work-space version of H11's coupling statistics (agent state (categorical, project, work ledger)) next to the attention version, to resolve the tension with H06 (private projects) and test HH266. Class for round 1b: shared objective with one shared database: shared-artifact week (ownership < 0.5 expected).

## Prediction
*Templated from the card's round-1b predictions R1b-2 (written 2026-10-04 07:10 UTC, before the work-space run).*  Shared-artifact weeks: work herds (βJ_CW(work) > 0, z_N2(work) ≥ 2), more weakly than attention. Own-artifact weeks: spread by fields in work (βJ_CW ≤ 0, z_N2 < 2). Minimum data: ≥ 15 room blocks with ≥ 3 labelled agents at W = 30. HH266 ("attention herds, work stays private") predicts z_N2(work) < 2 where attention herds.

## Result
`analysis/round1b.py work` → `data/processed/H11-potts-labor-vs-herding/r1b/work/G33.json` (99 nulls; 49 for #51 units). Co-location = share of labelled agents whose raw project is shared by ≥ 1 room-mate in the same 30-min window, vs its circular-shift (N2) mean.

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 247 | 24 | +3.80 (+0.2) | +22.0 | +11.2 | +1.66 | 0.94 (0.94, +0.6) | 0.06 | 0.97 |
| work | 182 | 22 | +3.62 (+0.3) | +9.0 | +4.9 | +1.97 | 0.94 (0.94, -0.1) | 0.05 | 0.97 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | work-space coupling vs the null hierarchy (table above) |
| I transfer | 1 | round-1 pattern (shared → herding; own → spread) holds in a period round 1 did not use |

## Notes
- Both spaces herd strongly on two shared repos (pentagon research, governance proposal); co-location is near-saturated (0.94) in both, so the excess over the shift null is ≈ 0 while the PL coupling is large: the herding is in timing (who works on which repo when), not in how many share a repo.
