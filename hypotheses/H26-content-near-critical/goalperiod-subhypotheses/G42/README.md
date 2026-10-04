# H26 × G42: Individual tasks (contagion candidate) (2026-05-18 → 2026-05-25)

**Verdict:** failed: content co-fluctuation is global (within-room 0.14, cross-room 0.12): L3 0.13; activity excess higher
**Verdict (1b):** failed (unchanged)
**Role:** exploratory
**Period:** regime III · mode I · 15 agents · two rooms · 5 days. H01 units used: 42.

## Why this period
Field-dominated week in H01 (goal-only R² 0.54) with little room excess (0.19 vs 0.14).

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

g_ex,c (day) < 0.5 [0.75], probably < 0.3 [0.6]; verdict **failed** [0.7].

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G42/`. Figure: [`figures/G42_ladder.pdf`](figures/G42_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 5 | 0.87 | 0.72 | 0.13 [-1.00, 0.48]  | 0.363 | 0.53 [-1.00, 0.78] | -0.48 | -0.40 [-1.00, 1.38] | 0.28 [0.09, 0.42] | 0.60 [-1.00, 0.74] | −∞ (→ −1) | -0.32 [-0.61, 1.22] | 0.62 / 0.07 | -0.009 | failed (L3) |

**Prediction check and reading.** Predicted g_ex,c < 0.5 [0.75] and < 0.3 [0.6]: **yes** (0.13); failed [0.7]: **yes**. Content co-fluctuation is mostly global (ρ_w 0.14 vs ρ_c 0.12): L3 deflates H01's 0.87 to 0.13. Activity's room excess (0.60 at w30) exceeds content's (0.28).

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
| 42 | round 1 | 0.13 | 0.53 | -0.48 | 0.28 | 0.60 | < −1 | -0.32 | failed |
| 42 | 1b bge | 0.13 | 0.47 | -0.18 | 0.28 | 0.12 | -0.58 | 0.16 | failed |
| 42 | 1b gte | 0.27 | 0.47 | -0.18 | 0.36 | 0.12 | -0.58 | 0.24 | failed |
| 42 | 1b bge, trimmed activity | 0.13 | 0.59 | 0.73 | 0.28 | -0.18 | < −1 | 0.46 | failed |

Data: `data/processed/H26-content-near-critical/r1b/<run>/G42/`.
<!-- /R1B -->
