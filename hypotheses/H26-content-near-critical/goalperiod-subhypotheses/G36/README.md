# H26 × G36: Regime-III start (#36b) (2026-03-24 → 2026-03-30 (non-holdout unit #36b))

**Verdict:** mixed: content 0.53; activity excess noisy (4 days); at w30 activity exceeds content (gap -0.21)
**Role:** exploratory
**Period:** regime III · mode C · 13 agents · two rooms · 4 days. H01 units used: 36b.

## Why this period
First regime-III days after the switch to continuous computer use; H01: ρ_within 0.31 vs ρ_cross 0.15 (sizeable global component).

## Prediction
*Written 2026-10-04 ~02:05 UTC, before running on this period.* The card's rules apply (day level, L3 on two-room units): **supported** = g_ex,c ≥ 0.5, Δg_ca > 0.15 with 95% CI excluding 0, and N2 p < 0.05; **failed** = g_ex,c < 0.5 and Δg_ca ≤ 0.15; else **mixed**. Single-room units are descriptive. Bracketed numbers are my probabilities. Seen beforehand: H01's per-unit ρ_within / ρ_cross and βJ₀/n, H19's per-period activity and talk gains, the synthetic validation, scheme counts.

Borderline: g_ex,c (day) 0.3–0.6 [0.6]; the global component is large, so L3 removes more here than elsewhere. Verdict **mixed** or **failed** [0.75 combined]; Δg_ca unpowered at 4 days.

## Result
Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G36/`. Figure: [`figures/G36_ladder.pdf`](figures/G36_ladder.pdf).

| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36b | 4 | 0.82 | 0.72 | 0.53 [0.34, 0.65]  | 0.010 | -1.00 [-1.00, 0.85] | – | +1.53 [-0.40, 1.61] | 0.40 [0.33, 0.50] | 0.61 [-1.00, 0.81] | 0.28 | -0.21 [-0.44, 1.42] | 0.73 / 0.07 | -0.006 | mixed (L3) |

**Prediction check and reading.** Predicted g_ex,c 0.3–0.6 [0.6]: **yes** (0.53). Mixed or failed [0.75]: **yes** (mixed). Activity's day-level room excess is strongly negative (clipped −1; 4 days), so Δg is large but uninformative; at w30 activity exceeds content (Δg −0.21).

## Scorecard (period-specific axes)
- **C (adequacy):** content room excess beats the room-permutation null (N2) where p < 0.05 above; activity and talk do too in several units. Neither channel's gain is tested against held-out days.
- **D (unfitted):** not tested per period; the H26 signature (content gain ≥ 0.5 *and* > activity + 0.15, robustly) is judged pooled in the card.
- **G (ground truth):** human/automated message directions explain no room-day variance beyond their null (exo share column).

## Notes
- 2026-10-04: prediction written before the H26 estimators touched this period.
- 2026-10-04: results filled from `analysis/summarize.py` (joint bootstrap) and `analysis/explore.py`.
