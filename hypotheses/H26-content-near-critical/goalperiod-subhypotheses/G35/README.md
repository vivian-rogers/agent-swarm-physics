# H26 × G35: RPG forks (#best / #rest) (2026-03-16 → 2026-03-23)

**Verdict:** mixed: content room excess 0.80 (N2 p 0.01), but activity nearly matches it at w30 once its global part is removed (gap +0.12)
**Verdict (1b):** supported
**Role:** exploratory
**Period:** regime II · mode C · 13 agents · two rooms (#best, #rest) working on separate forks of one game · 5 days. H01 units used: 35.

## Why this period
Descriptive extra (regime II). Highest within-room content co-fluctuation in H01 (ρ_within 0.66 vs ρ_cross 0.09); rooms work on different forks, so a room-specific task field competes with coupling.

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

Content L3 (day) g_ex,c ≥ 0.5 [0.65]: the room excess in H01 is very large. Activity L3 (day) is unpowered (IQR ≈ 0.9 in the synthetic), so Δg_ca will not exclude 0 → verdict **mixed** [0.6]. At w30, content > activity by > 0.15 [0.5]. The fork split is a room field the static projection cannot remove (it is not in the kickoff text), so even a high g_ex here is weak evidence for coupling.

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G35/`. Figure: [`figures/G35_ladder.pdf`](figures/G35_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | 5 | 0.87 | 0.83 | 0.80 [0.72, 0.84]  | 0.010 | 0.55 [-1.00, 0.83] | – | +0.25 [-0.02, 1.83] | 0.78 [0.74, 0.82] | 0.66 [-1.00, 0.85] | −∞ (→ −1) | +0.12 [-0.09, 1.81] | 0.86 / 0.03 | +0.036 | mixed (L3) |

**Prediction check and reading.** Predicted g_ex,c ≥ 0.5 [0.65]: **yes** (0.80). Verdict mixed [0.6]: **yes**. w30 content > activity by > 0.15 [0.5]: **no** (Δg 0.12). The largest content room excess of all units, with almost no cross-room content co-fluctuation (ρ_c 0.03). But activity is just as room-structured once its global component (ρ_c 0.86) is removed, and the rooms worked on different forks, a room field the projections cannot remove.

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
| 35 | round 1 | 0.80 | 0.55 | – | 0.78 | 0.66 | < −1 | 0.12 | mixed |
| 35 | 1b bge | 0.80 | 0.45 | < −1 | 0.78 | 0.24 | < −1 | 0.54 | supported |
| 35 | 1b gte | 0.81 | 0.45 | < −1 | 0.79 | 0.24 | < −1 | 0.55 | supported |
| 35 | 1b bge, trimmed activity | 0.80 | 0.55 | – | 0.78 | 0.25 | 0.81 | 0.53 | supported |

Data: `data/processed/H26-content-near-critical/r1b/<run>/G35/`.
<!-- /R1B -->
