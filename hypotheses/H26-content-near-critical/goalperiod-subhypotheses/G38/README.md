# H26 × G38: Rooms with different instructions (#38a–c) (2026-04-02 → 2026-04-27 (units 38a, 38b, 38c split at NE17 04-14 and NE18 04-20))

**Verdict:** mixed: content 0.65, 0.55, 0.40 in 38a, b, c (N2 p up to 0.03); at w30 activity ties or exceeds content; talk higher
**Role:** exploratory
**Period:** regime III · mode C · 12 agents · two rooms given different instructions · 17 days. H01 units used: 38a, 38b, 38c.

## Why this period
Rooms received different goals (a room field). Also the period with most self-repetition loops (H12; 11–23% of chat removed by the dedupe). H20's kickoff relaxation lasts ~4 days here.

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

38a (8 days): g_ex,c (day) ≥ 0.5 [0.55]. 38b and 38c: g_ex,c < 0.5 [0.65 each]. Dedupe lowers raw content gains in 38a/38b by ≥ 0.05 [0.5]. Because room-specific instructions are a room field, a high 38a value is not evidence for coupling. Verdicts: 38a mixed, 38b/38c failed.

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G38/`. Figure: [`figures/G38_ladder.pdf`](figures/G38_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 8 | 0.74 | 0.71 | 0.65 [0.48, 0.72]  | 0.005 | 0.53 [-1.00, 0.71] | 0.62 | +0.12 [-0.20, 1.66] | 0.59 [0.45, 0.65] | 0.59 [-0.31, 0.74] | 0.71 | +0.00 [-0.21, 0.93] | 0.42 / 0.04 | +0.013 | mixed (L3) |
| 38b | 4 | 0.55 | 0.52 | 0.55 [0.16, 0.68]  | 0.010 | 0.24 [-1.00, 0.79] | 0.92 | +0.31 [-0.19, 1.54] | 0.47 [0.29, 0.55] | -1.00 [-1.00, 0.68] | 0.82 | +1.47 [-0.15, 1.50] | 0.49 / -0.00 | -0.038 | mixed (L3) |
| 38c | 5 | 0.48 | 0.47 | 0.40 [0.18, 0.54]  | 0.030 | -0.34 [-1.00, 0.76] | 0.40 | +0.74 [-0.50, 1.54] | 0.45 [0.40, 0.50] | 0.62 [0.26, 0.75] | 0.58 | -0.17 [-0.32, 0.26] | 0.51 / 0.03 | -0.018 | mixed (L3) |

**Prediction check and reading.** Predicted 38a ≥ 0.5 [0.55]: **yes** (0.65). 38b < 0.5 [0.65]: **no** (0.55). 38c < 0.5 [0.65]: **yes** (0.40). Dedupe lowers content gains by ≥ 0.05 [0.5]: **no** (38a unchanged; 38b *rises* 0.49 → 0.55). Verdicts predicted mixed/failed/failed; observed mixed ×3 because activity's day-level room excess is noisy (CIs reach −1). At w30 content and activity are tied in 38a (0.59 vs 0.59), activity is higher in 38c (0.62 vs 0.45), talk is higher than content in all three. The rooms had different instructions (a room field), so content's room excess here is not evidence for coupling.

## Scorecard (period-specific axes)
- **C (adequacy):** content room excess beats the room-permutation null (N2) where p < 0.05 above; activity and talk do too in several units. Neither channel's gain is tested against held-out days.
- **D (unfitted):** not tested per period; the H26 signature (content gain ≥ 0.5 *and* > activity + 0.15, robustly) is judged pooled in the card.
- **G (ground truth):** human/automated message directions explain no room-day variance beyond their null (exo share column).

## Notes
- 2026-10-04: prediction written before the H26 estimators touched this period.
- 2026-10-04: results filled from `analysis/summarize.py` (joint bootstrap) and `analysis/explore.py`.
