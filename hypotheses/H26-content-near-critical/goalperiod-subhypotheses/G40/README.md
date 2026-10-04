# H26 × G40: Room merge week (2026-05-04 → 2026-05-11)

**Verdict:** descriptive: rooms merged (not two-room by rule); whole-room gains: content 0.75, activity 0.90
**Role:** exploratory
**Period:** regime III · mode C · 15 agents · two rooms, merged mid-week (universe-coordination room) · 5 days. H01 units used: 40.

## Why this period
Rooms merged during the week (H01 P7: residual alignment of new pairs rose). Pair type is set per pair-window, so the merge enters L3 correctly. H12: self-repetition loops.

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

g_ex,c (day) 0.3–0.6 [0.6]; verdict **mixed** [0.5]. The merge shrinks the number of cross-room pair-days, so ρ_cross is noisy.

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G40/`. Figure: [`figures/G40_ladder.pdf`](figures/G40_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | 5 | 0.89 | 0.75 | 0.75 [0.61, 0.81] (L2) | – | 0.90 [0.77, 0.92] | 0.89 | -0.15 [-0.24, -0.09] | 0.74 [0.68, 0.78] | 0.88 [0.69, 0.91] | 0.85 | -0.14 [-0.20, 0.02] | 0.79 / 0.12 | -0.018 | descriptive (L2 (one room)) |

**Prediction check and reading.** Not two-room by the pre-registered rule (rooms merged mid-week; < 30% of slots with two rooms of ≥ 2 agents), so descriptive. Predicted g_ex,c 0.3–0.6: not applicable. Whole-room (L2) gains: content 0.75, activity 0.90, talk 0.89 at day level; content is the *lowest* channel at both resolutions.

## Scorecard (period-specific axes)
- **C (adequacy):** content room excess beats the room-permutation null (N2) where p < 0.05 above; activity and talk do too in several units. Neither channel's gain is tested against held-out days.
- **D (unfitted):** not tested per period; the H26 signature (content gain ≥ 0.5 *and* > activity + 0.15, robustly) is judged pooled in the card.
- **G (ground truth):** human/automated message directions explain no room-day variance beyond their null (exo share column).

## Notes
- 2026-10-04: prediction written before the H26 estimators touched this period.
- 2026-10-04: results filled from `analysis/summarize.py` (joint bootstrap) and `analysis/explore.py`.
