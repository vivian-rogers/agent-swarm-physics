# H73 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime I · 6 agents with eligible messages · 25 days · 5,554 eligible messages (2,522 in computer-use mode) · units 4a, 4b, 4c, 4d.

## Why this period
A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points, not independent tests.

## Prediction
*Written 2026-10-04 19:28 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **O1 decomposition** (17-d type-controlled style; blocks: day field + time of day G, agent constant A, context C, register R where defined): the three components explain most of the non-day-field systematic variance, F3 ≥ 0.57 (0.5 plus the synthetic bias margin, Amendment A2).
- **Ordering:** the agent constant has the largest unique share (u_A > u_C, u_R). With ≥ 500 computer-use messages, the context share is positive (within-agent-day permutation p < 0.05).
- **O2 attribution** (leave-one-day-out, blocks of 5 messages): the agent-specific context model beats the blind centroid, Δ_c > 0.
- **O3 dispersion** (descriptive unless ≥ 2,000 computer-use messages): residual dispersion rises with context fill.
- **Verdict rule:** supported if F3 ≥ 0.57, u_A is the largest unique share and Δ_c > 0 (plus p_C < 0.05 where n_cu ≥ 500); failed if F3 < 0.5 and Δ_c ≤ 0; otherwise mixed.
- *Counts against:* F3 < 0.5 (agent-day jitter carries most systematic style variance) and no attribution gain from the context model.

## Result
*Run 2026-10-04 19:42 UTC (`analysis/replication.py` → `data/processed/H73-style-three-components/replication/replication.json`). Templated replication point.*

- **Sample:** 5,554 messages, 6 agents, 25 days, 2,522 computer-use; 551 cells.
- **Ceiling κ** (adjusted R² of agent × day × context bin × register cells): 0.218; day field + time of day R²: 0.063.
- **F3** = 0.64 [0.59, 0.69] (delete-one-day jackknife, ±1.96 SE); unique shares u_A 0.55, u_C 0.072 (permutation p 0.005; null-corrected 0.054).
- **Attribution** (blocks of 5, 1053 blocks, chance 0.17): blind 0.69, common-detrended 0.70, agent-specific context 0.69; Δ_c = -0.003, Δ_b = +0.008.
- **Dispersion slope** (residual ‖e‖² per unit z, relative to mean ‖e‖²): +0.093 (CI on raw slope [-0.89, 1.45]).
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the G + A baseline at the ceiling) and I (consistency across periods) in the main card.
