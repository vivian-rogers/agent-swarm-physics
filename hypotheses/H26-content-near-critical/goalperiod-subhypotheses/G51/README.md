# H26 × G51: Private roles, one big room (#51a–e) (2026-07-06 → 2026-09-07 (non-holdout; tail held out))

**Verdict:** mixed: one big room: activity 0.92 to 0.95 far above content 0.25 to 0.65 (L2 upper bounds); #focus content 0.54 (N2 p 0.18)
**Verdict (1b):** unchanged (51c mixed; single-room sub-units descriptive)
**Role:** replication (exploratory)
**Period:** regime III · mode P (I/K) · 21 agents · one room (#general), plus the #focus room in 51c · 45 days. H01 units used: 51a, 51b, 51c, 51d, 51e.

## Why this period
Large single room (N 21–32) with private role goals; long sub-units (51b: 19 days, 51c: 14) give the best-powered activity estimates. Single room → no cross-room baseline except in 51c (#focus).

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

51c (#focus, two rooms): g_ex,c (day) < 0.5 [0.6] (H01: 0.06 vs 0.01). Single-room units (51a, b, d, e): L2 content gains are upper bounds; the synthetic shows a global drive alone gives g ≈ 0.75 at N = 24, T = 15, so a high value means nothing. P6: g_c ≥ g_a at day level in most sub-units [0.55]. Verdict **descriptive** for single-room units, **failed** for 51c [0.55].

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G51/`. Figure: [`figures/G51_ladder.pdf`](figures/G51_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 3 | 0.73 | 0.71 | 0.65 [0.00, 0.65] (L2) | – | 0.92 [0.73, 0.95] | 0.95 | -0.27 [-0.95, -0.21] | 0.61 [0.49, 0.70] | 0.78 [0.31, 0.87] | 0.82 | -0.16 [-0.32, 0.28] | – / – | +0.011 | descriptive (L2 (one room)) |
| 51b | 19 | 0.65 | 0.59 | 0.53 [0.01, 0.78] (L2) | – | 0.93 [0.87, 0.95] | 0.93 | -0.40 [-0.92, -0.16] | 0.53 [0.48, 0.59] | 0.90 [0.84, 0.93] | 0.90 | -0.36 [-0.43, -0.28] | 1.00 / 0.18 | +0.031 | descriptive (L2 (one room)) |
| 51c | 14 | 0.60 | 0.53 | 0.54 [-0.03, 0.71]  | 0.179 | −∞ (→ −1) [-1.00, 0.07] | 0.67 | +1.54 [0.00, 1.71] | 0.42 [0.35, 0.48] | −∞ (→ −1) [-1.00, -1.00] | 0.27 | +1.42 [1.34, 1.48] | 0.56 / 0.02 | -0.158 | mixed (L3) |
| 51d | 7 | 0.44 | 0.41 | 0.46 [0.33, 0.55] (L2) | – | 0.95 [0.94, 0.96] | 0.95 | -0.50 [-0.63, -0.40] | 0.40 [0.34, 0.48] | 0.93 [0.86, 0.95] | 0.93 | -0.52 [-0.58, -0.44] | 0.29 / 0.03 | -0.003 | descriptive (L2 (one room)) |
| 51e | 2 | 0.35 | 0.22 | 0.25 [0.24, 0.27] (L2) | – | −∞ (→ −1) [-1.00, -1.00] | 0.93 | +1.25 [1.24, 1.27] | 0.61 [0.58, 0.65] | 0.62 [0.31, 0.75] | 0.90 | -0.01 [-0.10, 0.27] | – / – | -0.002 | descriptive (L2 (one room)) |

**Prediction check and reading.** 51c (#focus): predicted g_ex,c < 0.5 [0.6]: **no** (0.54, but N2 p 0.18 and CI −0.03…0.71); failed [0.55]: **no** (mixed; activity room excess −inf). Single-room units: P6 g_c ≥ g_a at day level in most sub-units [0.55]: **no, the reverse in 4/4** (activity 0.92–0.95 vs content 0.25–0.65; Δg −0.27 to −0.50, CIs below 0 in 51a, 51b, 51d). In the big single room, activity co-fluctuates across the whole swarm far more than content does. These L2 values are upper bounds for both channels (no cross-room baseline); the synthetic shows a global drive alone gives ≈ 0.75 at N = 24, T = 15.

## Scorecard (period-specific axes)
- **C (adequacy):** content room excess beats the room-permutation null (N2) where p < 0.05 above; activity and talk do too in several units. Neither channel's gain is tested against held-out days.
- **D (unfitted):** not tested per period; the H26 signature (content gain ≥ 0.5 *and* > activity + 0.15, robustly) is judged pooled in the card.
- **G (ground truth):** human/automated message directions explain no room-day variance beyond their null (exo share column).

## Notes
- 2026-10-04: prediction written before the H26 estimators touched this period.
- 2026-10-04: results filled from `analysis/summarize.py` (joint bootstrap) and `analysis/explore.py`.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Fixed activity table (DQ8), DQ5 restatement dedupe, shared goal fields, both embedding models (card: Round 1b). Gains g = 1 − 1/VR; two-room units L3 room excess, one-room units L2 (upper bound).

| unit | run | content day | activity day | talk day | content w30 | activity w30 | talk w30 | Δg_ca w30 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51c | round 1 | 0.54 | < −1 | 0.67 | 0.42 | < −1 | 0.27 | 1.42 | mixed |
| 51c | 1b bge | 0.50 | < −1 | 0.28 | 0.40 | -0.09 | 0.72 | 0.49 | mixed |
| 51c | 1b gte | 0.14 | < −1 | 0.28 | 0.45 | -0.09 | 0.72 | 0.54 | mixed |
| 51c | 1b bge, trimmed activity | 0.50 | < −1 | 0.01 | 0.40 | 0.24 | 0.70 | 0.16 | mixed |
| 51a | round 1 | 0.65 | 0.92 | 0.95 | 0.61 | 0.78 | 0.82 | -0.16 | descriptive |
| 51a | 1b bge | 0.65 | 0.86 | 0.93 | 0.61 | 0.72 | 0.76 | -0.10 | descriptive |
| 51a | 1b gte | 0.65 | 0.86 | 0.93 | 0.62 | 0.72 | 0.76 | -0.10 | descriptive |
| 51a | 1b bge, trimmed activity | 0.65 | 0.90 | 0.95 | 0.61 | 0.49 | 0.79 | 0.12 | descriptive |
| 51b | round 1 | 0.53 | 0.93 | 0.93 | 0.53 | 0.90 | 0.90 | -0.36 | descriptive |
| 51b | 1b bge | 0.53 | 0.72 | 0.58 | 0.53 | 0.73 | 0.74 | -0.19 | descriptive |
| 51b | 1b gte | 0.53 | 0.72 | 0.58 | 0.59 | 0.73 | 0.74 | -0.14 | descriptive |
| 51b | 1b bge, trimmed activity | 0.53 | 0.76 | 0.59 | 0.53 | 0.67 | 0.71 | -0.13 | descriptive |
| 51d | round 1 | 0.46 | 0.95 | 0.95 | 0.40 | 0.93 | 0.93 | -0.52 | descriptive |
| 51d | 1b bge | 0.44 | 0.13 | < −1 | 0.40 | 0.68 | 0.75 | -0.28 | descriptive |
| 51d | 1b gte | 0.32 | 0.13 | < −1 | 0.40 | 0.68 | 0.75 | -0.28 | descriptive |
| 51d | 1b bge, trimmed activity | 0.44 | 0.08 | 0.35 | 0.40 | 0.53 | 0.70 | -0.12 | descriptive |
| 51e | round 1 | 0.25 | < −1 | 0.93 | 0.61 | 0.62 | 0.90 | -0.01 | descriptive |
| 51e | 1b bge | 0.25 | 0.81 | 0.83 | 0.61 | 0.69 | 0.89 | -0.08 | descriptive |
| 51e | 1b gte | 0.10 | 0.81 | 0.83 | 0.64 | 0.69 | 0.89 | -0.05 | descriptive |
| 51e | 1b bge, trimmed activity | 0.25 | – | – | 0.61 | 0.28 | 0.95 | 0.34 | descriptive |

Data: `data/processed/H26-content-near-critical/r1b/<run>/G51/`.
<!-- /R1B -->
