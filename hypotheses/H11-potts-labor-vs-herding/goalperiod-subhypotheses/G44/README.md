# H11 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Verdict (1b):** mixed (attention herds, work private)
**Role:** replication (round 1b work space; templated prediction)
**Period:** regime III · 17–18 agents · #best (4) / #rest (12) · 4 active days · per-room goal override.

## Why this period
Not tested in round 1 (not a card candidate or transfer period). Round 1b adds it because the DQ4 work ledger is dense from #30 on: the work-space version of H11's coupling statistics (agent state (categorical, project, work ledger)) next to the attention version, to resolve the tension with H06 (private projects) and test HH266. Class for round 1b: #best shares one fine-tuning artifact; #rest chose individual creative work (mixed ownership).

## Prediction
*Templated from the card's round-1b predictions R1b-2 (written 2026-10-04 07:10 UTC, before the work-space run).*  Shared-artifact weeks: work herds (βJ_CW(work) > 0, z_N2(work) ≥ 2), more weakly than attention. Own-artifact weeks: spread by fields in work (βJ_CW ≤ 0, z_N2 < 2). Minimum data: ≥ 15 room blocks with ≥ 3 labelled agents at W = 30. HH266 ("attention herds, work stays private") predicts z_N2(work) < 2 where attention herds.

## Result
`analysis/round1b.py work` → `data/processed/H11-potts-labor-vs-herding/r1b/work/G44.json` (99 nulls; 49 for #51 units). Co-location = share of labelled agents whose raw project is shared by ≥ 1 room-mate in the same 30-min window, vs its circular-shift (N2) mean.

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 407 | 62 | +3.79 (+11.1) | +5.0 | +2.4 | +1.98 | 0.43 (0.34, +6.0) | 0.51 | 0.80 |
| work | 297 | 61 | +1.29 (+1.1) | +1.3 | +1.2 | +0.77 | 0.18 (0.14, +2.6) | 0.74 | 0.80 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | work-space coupling vs the null hierarchy (table above) |
| I transfer | 1 | round-1 pattern (shared → herding; own → spread) holds in a period round 1 did not use |

## Notes
- Mixed ownership: attention looks across rooms (ownership 0.51, z_N2 +5.0, co-location 0.43) while work is mostly private (ownership 0.74, co-location 0.18 vs 0.14 null, z_N2 +1.3): the one non-#51 unit where "attention herds, work stays private" holds.
