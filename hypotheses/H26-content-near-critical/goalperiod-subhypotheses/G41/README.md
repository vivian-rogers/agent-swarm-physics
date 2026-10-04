# H26 × G41: Same task in both rooms (2026-05-11 → 2026-05-18)

**Verdict:** mixed: best case: content 0.77 [0.72, 0.80], N2 p 0.005; activity's whole-swarm co-fluctuation is larger but global
**Verdict (1b):** mixed (unchanged)
**Role:** replication (exploratory)
**Period:** regime III · mode I · 15 agents · two rooms, identical task · 5 days. H01 units used: 41.

## Why this period
The most coupling-like week in H01 (ρ_within 0.47 vs ρ_cross 0.04) with the *same* instructions in both rooms, so room-specific fields are least plausible. The best period for H26.

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

g_ex,c (day) ≥ 0.5 [0.7]; content exceeds activity at w30 by > 0.15 [0.55]. Verdict **mixed** [0.55] (Δg_ca CI at day level likely includes 0) or **supported** [0.25].

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G41/`. Figure: [`figures/G41_ladder.pdf`](figures/G41_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 5 | 0.82 | 0.79 | 0.77 [0.72, 0.80]  | 0.005 | 0.43 [-1.00, 0.81] | 0.77 | +0.33 [-0.03, 1.79] | 0.73 [0.70, 0.76] | −∞ (→ −1) [-1.00, 0.51] | −∞ (→ −1) | +1.73 [0.22, 1.76] | 0.63 / 0.07 | -0.022 | mixed (L3) |

**Prediction check and reading.** Predicted g_ex,c ≥ 0.5 [0.7]: **yes** (0.77, CI 0.72–0.80, N2 p 0.005). w30 content > activity by > 0.15 [0.55]: **yes** (activity's w30 room excess is negative: ρ_c 0.63 > ρ_w 0.58). Mixed [0.55]: **yes** (day Δg CI −0.03…). The best case for H26: same instructions in both rooms, so room fields are least plausible, and content's room excess is large and tight. But activity's whole-swarm co-fluctuation is larger than content's (ρ_w 0.83 vs 0.45 at day level), and it is global.

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
| 41 | round 1 | 0.77 | 0.43 | 0.77 | 0.73 | < −1 | < −1 | 1.73 | mixed |
| 41 | 1b bge | 0.77 | 0.73 | 0.84 | 0.73 | 0.47 | 0.76 | 0.26 | mixed |
| 41 | 1b gte | 0.78 | 0.73 | 0.84 | 0.76 | 0.47 | 0.76 | 0.29 | mixed |
| 41 | 1b bge, trimmed activity | 0.77 | 0.81 | 0.85 | 0.73 | 0.59 | 0.76 | 0.14 | mixed |

Data: `data/processed/H26-content-near-critical/r1b/<run>/G41/`.
<!-- /R1B -->
