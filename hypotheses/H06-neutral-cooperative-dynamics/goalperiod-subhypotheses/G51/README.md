# H06 × G51: Each agent: Maximize your assigned goal! (non-holdout part) (2026-07-06 → 2026-09-04 (blocks a: 07-06 → 07-10, b: 07-27 → 07-31, c: 08-24 → 08-28))

**Verdict:** supported (P7 check passes: no block 'supported'; but the free weeks fail the same way, so the check is uninformative)
**Verdict (1b):** supported (P7 check, model-free); native rivals 1/3
**Role:** exploratory (check); native (round 1b: DQ6 roles)
**Period:** regime III · mode P (private assigned roles) · 21 → 32 agents · rooms #general/#focus (pooled) · 8 h days (16 windows/day). Splits: three 5-day blocks analysed separately (the 28k intentions are clustered once, k-means only).

## Why this period
P7 check: with private assigned goals, projects should be agent-bound (fields), not copied. If the pipeline called #51 'supported', it would not distinguish fields from cooperative copying.

## Prediction
*Written 2026-10-04, before running on this period.* The card's rules (`../../README.md`, Prediction, with the amendments made after the synthetic validation and before any real-data run) applied here:
- **P7 (check):** P1's rule must *not* give 'supported' in any block. Also reported: P1–P4 and P8 as in the free weeks.

**Expectation for this period:** **P7:** not 'supported' in any block; copy-consistency low; λ̄ not above the day-shift null; NCD not adequate. The check passes if no block is 'supported'.

## Result
*Run 2026-10-04 (exploratory round 1).* Three 5-day blocks, each clustered separately. Data: `data/processed/H06-neutral-cooperative-dynamics/G51/round1_G51{a,b,c}.json`. Figures: `figures/pn_G51a.pdf` etc.

| Block | P1 verdict (rule) | λ̄ (km24) | 1/N | singletons | copy-cons. | λ̄ vs independent null (p) | joint PPC NCD / Hubbell / conf. | reproduced N / H / C | artifact P1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a (2026-07-06 → 2026-07-10) | failed | 0.06 | 0.04 | 0.95 | 0.10 | 0.09 (1.000) | 0.002 / 0.002 / 0.002 | 0 / 2 / 2 | failed |
| b (2026-07-27 → 2026-07-31) | failed | 0.05 | 0.04 | 0.97 | 0.08 | 0.05 (0.955) | 0.002 / 0.002 / 0.002 | 2 / 1 / 1 | failed |
| c (2026-08-24 → 2026-08-28) | failed | 0.05 | 0.04 | 0.97 | 0.08 | 0.05 (0.413) | 0.002 / 0.002 / 0.002 | 1 / 2 / 2 | failed |

**P7 (check): passes**: 0 of 3 blocks 'supported' under P1's rule.

Block a:

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 25 | 17.6 | 954 | 0.378 (0.011, 0.16) | 0.05 | 0.10 [0.09, 0.11] | 0.18 [0.15, 0.23] | 0.54 [0.26, 0.71] | -0.26 | -1.22 [-3.58, 0.72] | -0.10 [-1.43, 1.01] | -45.7 | -263.6 | conformist | no | 0.02 |
| km24 (primary) | 25 | 17.6 | 825 | 0.278 (0.011, 0.16) | 0.06 | 0.12 [0.11, 0.13] | 0.28 [0.20, 0.40] | 0.53 [0.24, 0.71] | 2.82 | -1.30 [-3.03, 0.21] | -0.02 [-1.04, 0.88] | -163.9 | -313.7 | conformist | no | 0.10 |
| km64 | 25 | 17.6 | 663 | 0.204 (0.011, 0.16) | 0.06 | 0.14 [0.12, 0.17] | 0.42 [0.25, 0.70] | 0.54 [0.24, 0.71] | 6.46 | -1.33 [-3.41, 0.34] | 0.05 [-1.39, 1.75] | -269.9 | -361.2 | conformist | no | 0.24 |
| wd8 | 25 | 17.6 | 875 | 0.378 (0.011, 0.16) | 0.05 | 0.10 [0.09, 0.11] | 0.14 [0.12, 0.16] | 0.53 [0.26, 0.70] | -0.27 | -1.20 [-3.37, 0.78] | -0.10 [-1.67, 1.19] | -96.7 | -228.6 | conformist | no | 0.03 |
| wd24 | 25 | 17.6 | 720 | 0.278 (0.011, 0.16) | 0.05 | 0.12 [0.11, 0.14] | 0.28 [0.21, 0.40] | 0.53 [0.24, 0.70] | 3.23 | -1.28 [-3.08, 0.58] | -0.07 [-1.11, 0.88] | -121.1 | -330.1 | conformist | no | 0.09 |
| wd64 | 25 | 17.6 | 547 | 0.204 (0.011, 0.16) | 0.06 | 0.14 [0.12, 0.17] | 0.42 [0.24, 0.69] | 0.53 [0.19, 0.72] | 1.38 | -1.31 [-3.37, 0.28] | 0.06 [-1.25, 1.48] | -135.7 | -193.0 | conformist | no | 0.24 |
| art | 25 | 15.1 | 364 | 0.204 (0.011, 0.16) | 0.08 | 0.15 [0.13, 0.18] | 0.18 [0.14, 0.24] | 0.55 [0.22, 0.73] | -0.70 | -1.40 [-3.45, 0.66] | -0.10 [-1.95, 1.37] | -0.7 | -21.0 | conformist | no | 0.53 |

Block b:

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 27 | 22.0 | 927 | 0.150 (0.010, 0.15) | 0.04 | 0.15 [0.13, 0.18] | 0.33 [0.22, 0.49] | 0.54 [0.34, 0.67] | -0.15 | -1.41 [-3.11, -0.19] | 0.02 [-0.84, 0.88] | -105.2 | -258.4 | conformist | no | 0.03 |
| km24 (primary) | 27 | 22.0 | 765 | 0.150 (0.010, 0.15) | 0.05 | 0.16 [0.14, 0.19] | 0.32 [0.21, 0.49] | 0.53 [0.19, 0.72] | -2.38 | -1.30 [-2.65, 0.01] | -0.05 [-1.09, 0.93] | -37.7 | -155.5 | conformist | no | 0.08 |
| km64 | 27 | 22.0 | 534 | 0.110 (0.010, 0.15) | 0.05 | 0.18 [0.15, 0.22] | 0.40 [0.24, 0.71] | 0.73 [0.55, 0.84] | -2.68 | -1.40 [-2.91, 0.04] | -0.02 [-1.40, 1.42] | -116.9 | 80.3 | hubbell | no | 0.26 |
| wd8 | 27 | 22.0 | 843 | 0.150 (0.010, 0.15) | 0.04 | 0.15 [0.13, 0.18] | 0.33 [0.23, 0.48] | 0.53 [0.21, 0.70] | 0.00 | -1.39 [-2.86, -0.15] | -0.02 [-1.00, 0.92] | -105.1 | -303.0 | conformist | no | 0.03 |
| wd24 | 27 | 22.0 | 655 | 0.110 (0.010, 0.15) | 0.05 | 0.18 [0.15, 0.22] | 0.33 [0.21, 0.51] | 0.53 [0.15, 0.72] | 0.29 | -1.35 [-3.03, -0.03] | 0.00 [-1.22, 1.06] | -131.2 | -284.3 | conformist | no | 0.06 |
| wd64 | 27 | 22.0 | 450 | 0.150 (0.010, 0.15) | 0.06 | 0.16 [0.13, 0.19] | 0.26 [0.18, 0.41] | 0.72 [0.54, 0.83] | 4.57 | -1.35 [-3.02, 0.27] | -0.09 [-1.51, 1.13] | -47.5 | -43.3 | hubbell | no | 0.28 |
| art | 26 | 20.2 | 401 | 0.110 (0.011, 0.16) | 0.06 | 0.18 [0.15, 0.23] | 0.22 [0.16, 0.31] | 0.53 [0.17, 0.76] | -0.11 | -1.38 [-2.97, 0.06] | -0.10 [-1.45, 1.09] | 13.5 | -41.9 | conformist | no | 0.36 |

Block c:

| Label set | N | labelled/win | changes | μ̂_NCD (μ_B, μ_L) | λ̄ obs | λ NCD | λ Hubbell | λ conf. | β̂ obs | β NCD | β Hubbell | LLR_NH | LLR_NC | best | NCD adequate | copy-cons. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| km8 | 28 | 22.6 | 863 | 0.204 (0.010, 0.15) | 0.05 | 0.13 [0.11, 0.15] | 0.26 [0.20, 0.35] | 0.53 [0.25, 0.69] | 1.49 | -1.39 [-2.82, 0.02] | -0.01 [-1.00, 0.75] | 7.3 | -283.0 | conformist | no | 0.04 |
| km24 (primary) | 28 | 22.6 | 679 | 0.278 (0.010, 0.15) | 0.05 | 0.11 [0.09, 0.13] | 0.38 [0.24, 0.68] | 0.73 [0.59, 0.82] | -1.91 | -1.19 [-3.59, 0.94] | 0.04 [-1.35, 1.42] | -139.2 | -85.5 | hubbell | no | 0.08 |
| km64 | 28 | 22.6 | 484 | 0.278 (0.010, 0.15) | 0.05 | 0.11 [0.09, 0.13] | 0.38 [0.22, 0.65] | 0.55 [0.14, 0.75] | 1.18 | -1.36 [-3.91, 0.82] | -0.02 [-1.39, 1.61] | -86.0 | -100.2 | conformist | no | 0.24 |
| wd8 | 28 | 22.6 | 807 | 0.204 (0.010, 0.15) | 0.05 | 0.13 [0.11, 0.15] | 0.21 [0.15, 0.29] | 0.54 [0.23, 0.70] | -0.24 | -1.36 [-2.97, -0.01] | -0.09 [-1.42, 0.88] | -79.7 | -201.5 | conformist | no | 0.02 |
| wd24 | 28 | 22.6 | 635 | 0.278 (0.010, 0.15) | 0.05 | 0.11 [0.09, 0.13] | 0.39 [0.24, 0.70] | 0.54 [0.17, 0.73] | 0.97 | -1.24 [-3.85, 0.86] | 0.03 [-1.36, 1.46] | -125.1 | -258.1 | conformist | no | 0.07 |
| wd64 | 28 | 22.6 | 415 | 0.278 (0.010, 0.15) | 0.06 | 0.11 [0.10, 0.13] | 0.39 [0.24, 0.67] | 0.55 [0.14, 0.74] | 1.63 | -1.32 [-3.69, 0.88] | 0.02 [-1.23, 1.38] | -77.8 | -122.8 | conformist | no | 0.29 |
| art | 27 | 19.7 | 335 | 0.150 (0.010, 0.15) | 0.07 | 0.16 [0.13, 0.21] | 0.17 [0.13, 0.24] | 0.55 [0.13, 0.74] | 3.08 | -1.43 [-3.71, 0.53] | -0.15 [-2.00, 1.30] | 3.2 | -61.7 | conformist | no | 0.33 |

## Scorecard (period-specific axes)
- **C/H:** see the block table; the check concerns specificity of the P1 rule (axis F/H).

## Notes
- 2026-10-04: folder created; predictions written before the real-data run.
- 2026-10-04: round 1 run; Result and Verdict filled by `analysis/period_folders.py`.

## Round 1b native: same-role rivals (DQ6 roles)
**Role (round 1b):** native. *Prediction written 2026-10-04, before computing anything on round-1b labels or DQ6 roles in H06.* Seen: the DQ6 list of 9 rival pairs (same role short name; 3 from 07-06, the rest from 07-09/10 and 07-24) and 2 opposed pairs; H11 round 1b's #51 work co-location (0.04–0.21) and attention co-location (0.18–0.30).

**Design.** Blocks 51a, 51b, 51c (non-holdout). For each window and each pair of labelled agents, same-label indicator. s_rival = mean over pairs that are DQ6 rival pairs (valid at that time), s_other = mean over all other pairs; R = s_rival / s_other. Null: agent identities permuted within the block (999 draws; the rival-pair graph moves with the permutation), p = share of permuted R ≥ observed.
- **N51-1 (a role is a topic field).** Intention clusters (`gte_sr` km24): R ≥ 3 with p < 0.05 in ≥ 2/3 blocks. Credence 0.75.
- **N51-2 (attention).** Shared `project_states` labels: R ≥ 1.5 with p < 0.05 in ≥ 2/3 blocks. Credence 0.5.
- **N51-3 (work).** Work-ledger labels: R ≥ 1.5 with p < 0.05 in ≥ 2/3 blocks. Credence 0.35 (rivals may compete, each in its own repo).
- **Reading.** If N51-1 holds and N51-3 fails, the shared-role "species" in #51 is a shared field in what agents say, not shared work: species defined by stated goals follow assignments.

### Result (round 1b, run 2026-10-04)
Data: `data/processed/H06-neutral-cooperative-dynamics/r1b/natives_r1b.json` (`G51`), `light_r1b.json`. Replication (model-free; fits not re-run for compute): `gte_sr` km24 singletons 0.96 / 0.95 / 0.97 (round 1 0.95 / 0.97 / 0.97), λ̄ ≈ 1/N, copy-consistency 0.10 / 0.10 / 0.10. One work fit (51a): all three models inadequate (joint p 0.002), singletons 0.93 vs NCD 0.63.

| Block | R intentions (p) | R attention (p) | R work (p) |
| --- | --- | --- | --- |
| 51a | 5.2 (0.012) | 1.8 (0.17) | 0.0 (1.0; 64 rival pair-windows) |
| 51b | 4.0 (0.031) | 0.7 (0.44) | 0.6 (0.26) |
| 51c | 1.8 (0.21) | 2.4 (0.11) | 1.0 (0.28) |

- **N51-1 (intentions, R ≥ 3, p < 0.05 in ≥ 2/3): supported** (2/3).
- **N51-2 (attention): failed** (0/3 significant).
- **N51-3 (work): failed** (0/3; rivals never share a work repo more than other pairs).
- **Reading.** Same-role agents write about the same things (a shared field in stated goals) but do not work on, or link, the same repos more than other pairs. In #51 the stated-goal "species" follow assignments; work stays private.
