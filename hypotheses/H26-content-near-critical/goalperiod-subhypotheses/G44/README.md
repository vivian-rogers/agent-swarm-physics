# H26 × G44: Per-room goal override, leader week (2026-05-26 → 2026-06-01)

**Verdict:** mixed: content 0.76; at w30 activity 0.81 and talk 0.78 exceed content (gap -0.09)
**Role:** exploratory
**Period:** regime III · mode C · 16 agents · two rooms, one with an overridden goal · 4 days. H01 units used: 44.

## Why this period
Large room excess in H01 (0.34 vs −0.01) but with a per-room goal override (room field); 59 human messages (the most of any regime-III period), so the measured exogenous drive is largest here.

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

g_ex,c (day) ≥ 0.5 [0.6]; the exogenous projection (L2) lowers the room gain by more here than in any other period [0.5]. Verdict **mixed** [0.6]: the room field (goal override) is not removed by projection of one kickoff direction.

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G44/`. Figure: [`figures/G44_ladder.pdf`](figures/G44_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44 | 4 | 0.74 | 0.73 | 0.76 [-1.00, 0.82]  | 0.010 | 0.66 [-1.00, 0.86] | 0.76 | +0.10 [-1.00, 1.77] | 0.72 [0.65, 0.76] | 0.81 [0.56, 0.86] | 0.78 | -0.09 [-0.16, 0.14] | 0.39 / -0.05 | +0.009 | mixed (L3) |

**Prediction check and reading.** Predicted g_ex,c ≥ 0.5 [0.6]: **yes** (0.76). L2 lowers the room gain more than anywhere else [0.5]: **no** (L2 *raises* it, 0.72 → 0.77; the 59 human messages explain nothing beyond their null). Mixed [0.6]: **yes**. At w30 activity (0.81) and talk (0.78) exceed content (0.72): Δg_ca −0.09 [−0.16, 0.14]. A per-room goal override (room field) is present.

## Scorecard (period-specific axes)
- **C (adequacy):** content room excess beats the room-permutation null (N2) where p < 0.05 above; activity and talk do too in several units. Neither channel's gain is tested against held-out days.
- **D (unfitted):** not tested per period; the H26 signature (content gain ≥ 0.5 *and* > activity + 0.15, robustly) is judged pooled in the card.
- **G (ground truth):** human/automated message directions explain no room-day variance beyond their null (exo share column).

## Notes
- 2026-10-04: prediction written before the H26 estimators touched this period.
- 2026-10-04: results filled from `analysis/summarize.py` (joint bootstrap) and `analysis/explore.py`.
