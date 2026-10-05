# H11 × G51: Maximize your private assigned role (2026-07-06 → 2026-09-04 (non-holdout))

**Verdict:** supported (private in work; co-location 0.04–0.21 vs 0.18–0.30 in attention)
**Verdict (1b):** supported (private in work)
**Verdict (r2):** R1 attachment 51a work: n.s. (−), 51c work: n.s. (−), 51d work: n.s. (+), 51e work: n.s. (+), 51f work: n.s. (−), 51g work: n.s. (+), 51h work: supported, 51i work: n.s. (+); R2 stigmergy 51a work: n.s. (−), 51c work: n.s. (−), 51d work: n.s. (−), 51e work: n.s. (+), 51f work: n.s. (+), 51g work: n.s. (+), 51h work: n.s. (+), 51i work: n.s. (+); R3 herding raises output 51a: n.s. (−), 51b: n.s. (+), 51c: n.s. (−), 51d: n.s. (−), 51e: failed, 51f: n.s. (−), 51g: n.s. (−), 51h: n.s. (+), 51i: n.s. (+), 51j: n.s. (−), 51k: n.s. (−), 51l: failed; θ < 1 51a: yes, 51b: yes, 51c: yes, 51d: yes, 51e: yes, 51f: yes, 51g: yes, 51h: yes, 51i: yes, 51j: yes, 51k: no, 51l: yes
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

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \| act · OR commits \| chat (R2b) | read − lead, chat · commits (R2c) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51a · work (n = 45) | -0.06 [-1.00, +0.88] | -0.01 [-1.83, +1.81] | -0.34 [-1.54, +0.86] | ✓/✓ · ✗/✗ · ✓/✓ | -0.028 [-0.159, +0.103] | 3.02 · 2.77 | -1.52 [-2.78, -0.26] · +1.02 [+0.09, +1.94] |
| 51a · att (n = 206) | +0.20 [-0.17, +0.57] | +0.31 [-0.04, +0.65] | +0.03 [-0.44, +0.50] | ✓/✗ · ✓/✗ · ✗/✗ | -0.071 [-0.157, +0.014] | 1.89 · 1.41 | +0.23 [-0.59, +1.04] · +0.36 [-0.08, +0.81] |
| 51b · att (n = 39) | +0.27 [-0.08, +0.63] | +0.48 [-0.40, +1.35] | -0.64 [-1.87, +0.59] | ✓/✓ · ✗/✗ · ✓/✓ | – | 6.81 · 1.25 | n.e. · -0.45 [-1.78, +0.88] |
| 51c · work (n = 45) | -0.84 [-2.90, +1.23] | -0.58 [-1.49, +0.32] | -1.24 [-4.48, +2.00] | ✓/✓ · ✗/✗ · ✗/✓ | -0.047 [-0.125, +0.030] | 5.77 · 2.54 | +1.69 [-0.24, +3.62] · -0.63 [-1.92, +0.65] |
| 51c · att (n = 265) | -0.14 [-0.75, +0.47] | -0.18 [-0.62, +0.27] | +0.05 [-0.63, +0.72] | ✓/✗ · ✗/✗ · ✓/✗ | -0.058 [-0.115, -0.002] | 3.92 · 1.24 | +0.89 [-0.01, +1.79] · -0.32 [-0.86, +0.23] |
| 51d · work (n = 58) | +0.70 [-0.49, +1.88] | +0.99 [-0.06, +2.04] | +1.77 [+0.46, +3.08] | ✓/✓ · ✓/✗ · ✓/✓ | -0.043 [-0.092, +0.007] | 2.45 · 1.83 | +0.27 [-1.09, +1.64] · +1.13 [+0.05, +2.21] |
| 51d · att (n = 283) | +0.04 [-0.34, +0.42] | -0.16 [-0.59, +0.27] | +0.04 [-0.31, +0.38] | ✓/✗ · ✗/✗ · ✓/✗ | -0.010 [-0.029, +0.009] | 1.59 · 1.38 | +0.06 [-0.85, +0.96] · -0.09 [-0.51, +0.34] |
| 51e · work (n = 30) | +0.94 [-0.28, +2.16] | +1.22 [+0.18, +2.27] | +2.37 [-0.28, +5.03] | ✓/✓ · ✓/✗ · ✓/✓ | +0.154 [-0.015, +0.324] | 0.51 · 6.47 | n.e. · +1.05 [-0.47, +2.57] |
| 51e · att (n = 230) | +0.22 [-0.22, +0.66] | +0.17 [-0.34, +0.67] | -0.20 [-0.80, +0.40] | ✓/✗ · ✗/✗ · ✓/✗ | -0.051 [-0.101, -0.000] | 1.94 · 0.83 | +0.14 [-0.63, +0.91] · +0.54 [+0.07, +1.00] |
| 51f · work (n = 93) | -0.24 [-1.13, +0.66] | -0.12 [-0.53, +0.28] | -1.93 [-2.78, -1.08] | ✓/✓ · ✓/✗ · ✓/✗ | +0.016 [-0.047, +0.079] | 1.98 · 3.60 | +0.65 [-0.61, +1.90] · -0.13 [-0.94, +0.68] |
| 51f · att (n = 358) | +0.20 [-0.22, +0.63] | +0.11 [-0.25, +0.46] | +0.18 [-0.35, +0.72] | ✗/✗ · ✗/✗ · ✗/✗ | -0.032 [-0.076, +0.012] | 2.17 · 1.24 | +0.54 [-0.25, +1.34] · -0.28 [-0.95, +0.40] |
| 51g · work (n = 321) | +0.70 [-0.09, +1.49] | +1.22 [+0.58, +1.86] | +0.07 [-0.66, +0.79] | ✗/✓ · ✗/✗ · ✗/✓ | +0.001 [-0.018, +0.020] | 1.72 · 0.89 | -0.22 [-1.33, +0.89] · +0.00 [-0.84, +0.84] |
| 51g · att (n = 904) | +0.60 [+0.31, +0.90] | +0.51 [+0.22, +0.80] | -0.08 [-0.44, +0.27] | ✓/✗ · ✗/✗ · ✗/✗ | -0.065 [-0.096, -0.033] | 2.59 · 0.71 | +0.39 [+0.05, +0.72] · +0.21 [-0.15, +0.57] |
| 51h · work (n = 47) | +1.22 [+0.12, +2.33] | +0.30 [-0.56, +1.16] | +0.12 [-1.40, +1.64] | ✓/✓ · ✓/✗ · ✓/✓ | +0.037 [-0.246, +0.320] | 1.44 · 0.95 | -1.08 [-3.01, +0.86] · -0.43 [-1.79, +0.94] |
| 51h · att (n = 267) | +0.06 [-0.46, +0.58] | -0.11 [-0.54, +0.33] | -0.25 [-0.89, +0.39] | ✗/✗ · ✓/✗ · ✗/✗ | -0.055 [-0.114, +0.004] | 3.51 · 0.78 | +0.91 [+0.25, +1.57] · -1.18 [-1.84, -0.52] |
| 51i · work (n = 25) | +1.14 [-1.80, +4.09] | +2.49 [-0.26, +5.25] | +0.89 [-2.61, +4.40] | ✓/✓ · ✗/✗ · ✓/✓ | +0.027 [-0.011, +0.065] | 0.55 · 1.84 | n.e. · n.e. |
| 51i · att (n = 92) | +0.70 [+0.05, +1.34] | +0.04 [-0.85, +0.92] | +0.01 [-1.39, +1.40] | ✗/✗ · ✓/✗ · ✗/✗ | -0.009 [-0.079, +0.061] | 2.53 · 1.06 | +0.59 [-0.28, +1.45] · -0.27 [-0.97, +0.42] |
| 51j · att (n = 107) | +1.61 [+1.11, +2.10] | +1.41 [+0.75, +2.06] | +0.82 [+0.02, +1.61] | ✓/✓ · ✓/✓ · ✗/✗ | -0.037 [-0.101, +0.027] | 6.56 · 0.29 | +0.62 [-0.74, +1.99] · -0.02 [-0.81, +0.77] |
| 51k · att (n = 56) | +0.32 [-1.52, +2.16] | +0.90 [-0.68, +2.47] | -0.16 [-2.63, +2.31] | ✗/✗ · ✗/✓ · ✗/✗ | – | 2.47 · 0.30 | +0.32 [-1.23, +1.86] · -0.68 [-2.04, +0.67] |
| 51l · att (n = 82) | +1.20 [+0.64, +1.76] | +0.02 [-0.80, +0.84] | +0.29 [-0.50, +1.08] | ✓/✗ · ✗/✓ · ✗/✗ | – | 1.52 · 1.99 | +1.51 [+0.73, +2.28] · -2.25 [-3.45, -1.05] |

| Unit | log RR herd vs solo, commits (R3a) | landed | matched pairs (mean log ratio) | θ crowding (R3b) | herd / solo windows |
| --- | --- | --- | --- | --- | --- |
| 51a (own) | -0.00 [-0.21, +0.20] | +0.01 [-0.21, +0.22] | -0.15 ± 0.13 | +0.12 [-0.22, +0.45] | 56/173 |
| 51b (own) | +0.13 [-0.12, +0.39] | +0.15 [-0.09, +0.39] | +0.31 ± 0.17 | +0.25 [+0.14, +0.35] | 27/87 |
| 51c (own) | -0.15 [-0.55, +0.26] | -0.15 [-0.55, +0.25] | -0.24 ± 0.12 | -0.05 [-0.32, +0.22] | 34/167 |
| 51d (own) | -0.29 [-0.71, +0.13] | -0.34 [-0.83, +0.14] | -0.01 ± 0.15 | +0.39 [+0.19, +0.60] | 83/288 |
| 51e (own) | -0.47 [-0.82, -0.12] | -0.46 [-0.83, -0.10] | -0.25 ± 0.10 | -0.11 [-0.45, +0.24] | 63/249 |
| 51f (own) | -0.02 [-0.30, +0.27] | -0.01 [-0.31, +0.29] | +0.00 ± 0.15 | +0.46 [+0.09, +0.84] | 47/251 |
| 51g (own) | -0.10 [-0.24, +0.04] | -0.11 [-0.24, +0.01] | -0.06 ± 0.08 | +0.25 [+0.03, +0.46] | 188/704 |
| 51h (own) | +0.11 [-0.11, +0.33] | +0.13 [-0.09, +0.35] | -0.02 ± 0.10 | +0.46 [-0.02, +0.93] | 63/183 |
| 51i (own) | +0.07 [-0.21, +0.35] | +0.09 [-0.17, +0.35] | -0.13 ± 0.11 | +0.06 [-0.07, +0.20] | 60/111 |
| 51j (own) | -0.12 [-0.24, +0.01] | -0.10 [-0.23, +0.02] | -0.13 ± 0.12 | +0.07 [-0.20, +0.34] | 56/90 |
| 51k (own) | -0.19 [-0.43, +0.05] | -0.17 [-0.40, +0.06] | -0.27 ± 0.20 | +0.46 [-0.18, +1.10] | 44/80 |
| 51l (own) | -0.38 [-0.68, -0.09] | -0.41 [-0.73, -0.10] | -0.35 ± 0.10 | +0.10 [-0.22, +0.42] | 61/51 |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
