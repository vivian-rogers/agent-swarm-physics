# H26 × G37: Free week (2026-03-30 → 2026-04-02)

**Verdict:** failed: content co-fluctuation is global (within-room 0.23, cross-room 0.20): L3 only 0.15; seen during debugging
**Verdict (1b):** mixed
**Role:** exploratory
**Period:** regime III · mode F · 13 agents · two rooms · 3 days. H01 units used: 37.

## Why this period
Free week; H01 found no room excess (ρ_within 0.30 ≈ ρ_cross 0.26): co-fluctuation is global. A clean test that L3 deflates a drive-dominated week.

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

g_ex,c (day) < 0.5 [0.75], near 0 [0.5]: the co-fluctuation is cross-room, i.e. global drive. Verdict **failed** [0.7]. Only 3 days: CIs very wide.

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G37/`. Figure: [`figures/G37_ladder.pdf`](figures/G37_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | 3 | 0.76 | 0.72 | 0.15 [-1.00, 0.63]  | 0.348 | 0.40 [-1.00, 0.59] | 0.90 | -0.25 [-1.00, 1.63] | 0.35 [0.16, 0.56] | 0.29 [0.05, 0.43] | 0.67 | +0.06 [-0.21, 0.49] | 0.16 / 0.11 | -0.034 | failed (L3) |

**Prediction check and reading.** Seen during debugging (Amendment 2). Predicted g_ex,c < 0.5 [0.75]: **yes** (0.15); failed [0.7]: **yes**. Within-room and cross-room content co-fluctuation are equal (ρ_w 0.23, ρ_c 0.20): the free week's day-to-day content co-movement is global. L3 deflates H01's 0.76 to 0.15, as designed. At w30 the room excess is 0.35, similar to activity (0.29); talk is higher (0.67).

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
| 37 | round 1 | 0.15 | 0.40 | 0.90 | 0.35 | 0.29 | 0.67 | 0.06 | failed |
| 37 | 1b bge | 0.15 | < −1 | 0.67 | 0.35 | -0.39 | 0.47 | 0.75 | mixed |
| 37 | 1b gte | -0.53 | < −1 | 0.67 | 0.42 | -0.39 | 0.47 | 0.82 | mixed |
| 37 | 1b bge, trimmed activity | 0.15 | < −1 | 0.89 | 0.35 | 0.07 | 0.45 | 0.29 | mixed |

Data: `data/processed/H26-content-near-critical/r1b/<run>/G37/`.
<!-- /R1B -->
