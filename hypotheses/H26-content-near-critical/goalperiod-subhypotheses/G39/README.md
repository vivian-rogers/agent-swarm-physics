# H26 × G39: Individual tasks, pre-merge (2026-04-27 → 2026-05-04)

**Verdict:** mixed: content 0.45; activity room excess negative (cross-room above within), which inflates the gap; talk above content
**Verdict (1b):** mixed (unchanged)
**Role:** replication (exploratory)
**Period:** regime III · mode I · 15 agents · two rooms · 5 days. H01 units used: 39.

## Why this period
Individual-task week (mode I); H01: weak room excess (0.17 vs 0.08), strong lab order.

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

g_ex,c (day) < 0.5 [0.7]; verdict **failed** [0.65]. Content and activity gains both small; Δg_ca ≈ 0 ± noise.

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G39/`. Figure: [`figures/G39_ladder.pdf`](figures/G39_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 5 | 0.66 | 0.64 | 0.45 [0.25, 0.51]  | 0.055 | -1.00 [-1.00, 0.16] | 0.83 | +1.45 [0.29, 1.51] | 0.29 [-0.08, 0.44] | −∞ (→ −1) [-1.00, -1.00] | 0.80 | +1.29 [0.92, 1.44] | 0.31 / 0.05 | -0.015 | mixed (L3) |

**Prediction check and reading.** Predicted g_ex,c < 0.5 [0.7]: **yes** (0.45). Failed [0.65]: **no**, mixed, because activity's room excess is strongly negative (cross-room activity co-moves more than within-room; ρ_c 0.31 > ρ_w 0.19 at w30), which makes Δg large. Talk room excess (0.80 at w30) exceeds content (0.29).

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
| 39 | round 1 | 0.45 | < −1 | 0.83 | 0.29 | < −1 | 0.80 | 1.29 | mixed |
| 39 | 1b bge | 0.45 | < −1 | 0.86 | 0.29 | < −1 | 0.83 | 1.29 | mixed |
| 39 | 1b gte | 0.41 | < −1 | 0.86 | 0.34 | < −1 | 0.83 | 1.34 | mixed |
| 39 | 1b bge, trimmed activity | 0.45 | < −1 | 0.86 | 0.29 | < −1 | 0.80 | 1.29 | mixed |

Data: `data/processed/H26-content-near-critical/r1b/<run>/G39/`.
<!-- /R1B -->
