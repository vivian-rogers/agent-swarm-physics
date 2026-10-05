# H11 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Verdict (1b):** mixed (attention herds, work private)
**Verdict (r2):** R1 attachment G44 work: supported; R2 stigmergy G44 work: n.s. (−); R3 herding raises output G44: n.s. (−); θ < 1 G44: yes
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

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \| act · OR commits \| chat (R2b) | read − lead, chat · commits (R2c) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G44 · work (n = 39) | +1.39 [+0.24, +2.55] | +0.81 [-0.74, +2.36] | +2.19 [+0.53, +3.85] | ✓/✓ · ✓/✓ · ✓/✗ | -0.109 [-0.276, +0.059] | 5.61 · – | -0.40 [-2.61, +1.81] · -0.05 [-1.35, +1.25] |
| G44 · att (n = 102) | +1.17 [+0.46, +1.87] | +0.66 [-0.05, +1.37] | +0.21 [-0.96, +1.38] | ✓/✗ · ✓/✓ · ✗/✗ | +0.006 [-0.163, +0.174] | 3.00 · 1.18 | -0.91 [-1.81, -0.00] · +0.72 [+0.00, +1.43] |

| Unit | log RR herd vs solo, commits (R3a) | landed | matched pairs (mean log ratio) | θ crowding (R3b) | herd / solo windows |
| --- | --- | --- | --- | --- | --- |
| G44 (own) | -0.19 [-0.53, +0.15] | -0.19 [-0.53, +0.14] | -0.35 ± 0.15 | +0.65 [+0.34, +0.96] | 61/101 |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
