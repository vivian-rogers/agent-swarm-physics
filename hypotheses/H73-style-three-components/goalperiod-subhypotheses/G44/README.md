# H73 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** descriptive
**Role:** native (exploratory)
**Period:** regime III · 16 agents with eligible messages · 4 days · 1,547 eligible messages (1,547 in computer-use mode) · units 44a, 44b.

## Why this period
Native: the fine-tuned leader is a weights swap on a known base (Kimi K2.6), the only non-holdout model swap (NE30 is held out).

## Prediction
*Written 2026-10-04 19:28 UTC, before running on this period.*
- **Design (model swap, the weights component):** the temporary fine-tuned leader (agent 28; base Kimi K2.6 self-distilled, H23) posts in #44. Centroids: every main agent's regime-III messages in #36–#44 (non-holdout), day-centred; the leader's messages form one block.
- **N4 prediction (descriptive):** base Kimi K2.6 (agent 25) ranks ≤ 2 of about 17 centroids, blind and after context detrending, and detrending does not lower its rank. H46 found rank 2 (raw style rank 1) blind.
- **Replication layer:** the templated O1–O3 rule also applies (reported, not the native verdict).
- *Counts against:* Kimi rank > 3 under both variants (the fine-tune moved the weights component away from its base).

**Templated replication prediction (also reported):**
*Written 2026-10-04 19:28 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **O1 decomposition** (17-d type-controlled style; blocks: day field + time of day G, agent constant A, context C, register R where defined): the three components explain most of the non-day-field systematic variance, F3 ≥ 0.57 (0.5 plus the synthetic bias margin, Amendment A2).
- **Ordering:** the agent constant has the largest unique share (u_A > u_C, u_R). With ≥ 500 computer-use messages, the context share is positive (within-agent-day permutation p < 0.05).
- **O2 attribution** (leave-one-day-out, blocks of 5 messages): the agent-specific context model beats the blind centroid, Δ_c > 0.
- **O3 dispersion** (descriptive unless ≥ 2,000 computer-use messages): residual dispersion rises with context fill.
- **Verdict rule:** supported if F3 ≥ 0.57, u_A is the largest unique share and Δ_c > 0 (plus p_C < 0.05 where n_cu ≥ 500); failed if F3 < 0.5 and Δ_c ≤ 0; otherwise mixed.
- *Counts against:* F3 < 0.5 (agent-day jitter carries most systematic style variance) and no attribution gain from the context model.

## Result
*Run 2026-10-04 19:46 UTC (`analysis/natives.py` → `natives.json`, key G44).*

- **Sample:** 20 eligible leader messages (agent 28, #44); 17 candidate centroids from regime-III #36–#44 (non-holdout, ≥ 20 messages).
- **Rank of base Kimi K2.6:** blind 3, common-detrended 3, agent-specific context 1 of 17. Top 3 blind: Claude Sonnet 4.6, Claude Opus 4.6, Kimi K2.6; detrended: Claude Sonnet 4.6, Claude Opus 4.6, Kimi K2.6.
- **N4 (descriptive):** Kimi rank ≤ 2 in both variants and no loss from detrending: not met. Verdict: descriptive (one block of 20 messages).

**Replication layer (templated):**
- **Sample:** 1,547 messages, 16 agents, 4 days, 1,547 computer-use; 253 cells.
- **Ceiling κ** (adjusted R² of agent × day × context bin × register cells): 0.159; day field + time of day R²: 0.022.
- **F3** = 0.82 [0.61, 1.03] (delete-one-day jackknife, ±1.96 SE); unique shares u_A 0.77, u_C 0.019 (permutation p 0.010; null-corrected 0.036).
- **Attribution** (blocks of 5, 281 blocks, chance 0.06): blind 0.56, common-detrended 0.56, agent-specific context 0.57; Δ_c = +0.008, Δ_b = -0.002.
- **Dispersion slope** (residual ‖e‖² per unit z, relative to mean ‖e‖²): +0.071 (CI on raw slope [-0.55, 2.71]), descriptive (n_cu < 2,000).
- **Templated verdict:** supported.

## Scorecard (period-specific axes)
- **G (ground truth):** the leader's base model is known (H23, DQ6); the weights component should point to it.
