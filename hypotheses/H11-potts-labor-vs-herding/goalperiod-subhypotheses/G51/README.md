# H11 × G51: Maximize your private assigned role (2026-07-06 → 2026-09-04 (non-holdout))

**Verdict:** supported (private in work; co-location 0.04–0.21 vs 0.18–0.30 in attention)
**Verdict (1b):** supported (private in work)
**Role:** replication (round 1b work space; templated prediction)
**Period:** regime III · 21 → 32 agents · #general (+ #focus in 51g) · 45 non-holdout days, split into period units 51a–51l; the tail 51m (09-07 → 09-18) is locked holdout and untouched.

## Why this period
Not tested in round 1 (not a card candidate or transfer period). Round 1b adds it because the DQ4 work ledger is dense from #30 on: the work-space version of H11's coupling statistics (agent state (categorical, project, work ledger)) next to the attention version, to resolve the tension with H06 (private projects) and test HH266. Class for round 1b: private roles: own-artifact (ownership ≥ 0.5 expected).

## Prediction
*Templated from the card's round-1b predictions R1b-2 (written 2026-10-04 07:10 UTC, before the work-space run).*  Shared-artifact weeks: work herds (βJ_CW(work) > 0, z_N2(work) ≥ 2), more weakly than attention. Own-artifact weeks: spread by fields in work (βJ_CW ≤ 0, z_N2 < 2). Minimum data: ≥ 15 room blocks with ≥ 3 labelled agents at W = 30. HH266 ("attention herds, work stays private") predicts z_N2(work) < 2 where attention herds.

## Result
`analysis/round1b.py work` → `data/processed/H11-potts-labor-vs-herding/r1b/work/51<unit>.json` (99 nulls; 49 for #51 units). Co-location = share of labelled agents whose raw project is shared by ≥ 1 room-mate in the same 30-min window, vs its circular-shift (N2) mean.

**51a**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 738 | 49 | -17.16 (-2.0) | +3.8 | +1.7 | +7.78 | 0.30 (0.22, +6.4) | 0.58 | 0.88 |
| work | 398 | 49 | -30.00 (–) | -0.9 | +0.5 | -2.26 | 0.06 (0.06, +0.2) | 0.96 | 0.88 |

**51c**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 1186 | 80 | -30.00 (-59.4) | +5.7 | +2.4 | +12.50 | 0.18 (0.15, +4.3) | 0.75 | 0.85 |
| work | 791 | 80 | -30.00 (–) | +1.3 | +0.3 | +3.23 | 0.09 (0.06, +2.9) | 0.90 | 0.85 |

**51d**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 1317 | 80 | -30.00 (–) | +2.8 | +1.1 | +9.01 | 0.24 (0.21, +4.0) | 0.60 | 0.82 |
| work | 994 | 80 | -30.00 (–) | -1.3 | -0.3 | -3.51 | 0.21 (0.18, +3.7) | 0.71 | 0.82 |

**51e**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 926 | 48 | -30.00 (–) | +0.6 | +0.8 | +2.27 | 0.27 (0.22, +4.9) | 0.59 | 0.76 |
| work | 655 | 48 | -30.00 (–) | -4.4 | -1.5 | -14.41 | 0.21 (0.17, +3.7) | 0.74 | 0.76 |

**51f**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 1332 | 80 | -30.00 (–) | +1.4 | +1.4 | +5.03 | 0.24 (0.20, +4.3) | 0.57 | 0.76 |
| work | 1001 | 80 | -30.00 (–) | +3.0 | +1.1 | +7.88 | 0.20 (0.17, +3.4) | 0.71 | 0.76 |

**51g**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 3371 | 211 | -23.85 (-4.4) | -0.7 | -0.6 | -0.58 | 0.18 (0.15, +7.0) | 0.70 | 0.63 |
| work | 2530 | 208 | -30.00 (–) | -4.4 | -2.7 | -12.28 | 0.04 (0.03, +1.0) | 0.97 | 0.63 |

**51h**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess | co-location (N2 mean, z) | ownership | work repo = attention project |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 1016 | 66 | -13.52 (-2.6) | +0.6 | +0.3 | +0.97 | 0.20 (0.18, +2.6) | 0.70 | 0.56 |
| work | 768 | 65 | -30.00 (–) | – | – | +0.00 | 0.21 (0.18, +5.4) | 0.75 | 0.56 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | work-space coupling vs the null hierarchy (table above) |
| I transfer | 1 | round-1 pattern (shared → herding; own → spread) holds in a period round 1 did not use |

## Notes
- Each agent works on its own role repo, so most work agent-windows merge into "other" (q ≤ 8): the uniform-field βJ_CW sits at the grid bound (−30) and the agent-field PL z swings from −4.4 to +3.0 between units. Read co-location instead: attention is shared more than work in every unit except 51h (51a 0.30 vs 0.06, 51c 0.18 vs 0.09, 51g 0.18 vs 0.04). This is HH266's pattern, in the private-role era.
- Units with < 3 active days (51b, 51i–51l) are skipped; the locked tail 51m is never read.
