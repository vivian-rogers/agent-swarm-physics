# H73 × G03: Holiday: do whatever you'd like! Next goal will begin soon (2025-05-12 → 2025-05-14)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime I · 4 agents with eligible messages · 3 days · 1,280 eligible messages (365 in computer-use mode) · units 3.

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

- **Sample:** 1,280 messages, 4 agents, 3 days, 365 computer-use; 55 cells.
- **Ceiling κ** (adjusted R² of agent × day × context bin × register cells): 0.193; day field + time of day R²: 0.077.
- **F3** = 1.03 [0.47, 1.59] (delete-one-day jackknife, ±1.96 SE); unique shares u_A 0.73, u_C 0.177 (permutation p 0.005; null-corrected 0.174).
- **Attribution** (blocks of 5, 250 blocks, chance 0.25): blind 0.72, common-detrended 0.71, agent-specific context 0.68; Δ_c = -0.040, Δ_b = -0.012.
- **Dispersion slope** (residual ‖e‖² per unit z, relative to mean ‖e‖²): +0.116 (CI on raw slope [-2.81, 1.72]), descriptive (n_cu < 2,000).
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (beats the G + A baseline at the ceiling) and I (consistency across periods) in the main card.

## Round 2 (2026-10-05)
**Round-2 result:** pending.
*Prediction written 2026-10-05 05:07 UTC, before the real round-2 run (card pre-registration 04:46 UTC; templated, layer 1).*
- **R2-1a conversation state:** the unique share of conversation state (received items, pending @-mentions, pending nudge, DQ2 thread depth) u_Cv is positive (within-agent-day permutation p < 0.05); in regime III it exceeds the unique share of own fill u_Cf.
- **R2-1b accommodation** (read vs in-flight sources at the read boundary): the unit's γ is reported if the unit has ≥ 200 read and ≥ 200 in-flight pairs; the verdict is card-level (pooled), not per unit.
- **R2-3 reset-and-hold** (regime I/II periods with ≥ 150 one-reset pairs): ΔC(1) > 0 and T > ½ reported (descriptive per period).
