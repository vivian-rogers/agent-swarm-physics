# H46 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** descriptive
**Role:** native (exploratory)
**Period:** regime III · 15 agents with eligible days · rooms [2, 3] · 4 days with eligible agent-days · units 44a, 44b.

## Why this period
#44 holds the **H23 distilled leader**: base Kimi K2.6 fine-tuned (LoRA r8, 30 steps) on outputs of a prompted Kimi K2.6, deployed as agent 28 on 05-28/29 (27 chat rows over all checkpoints, 16 from the final weights). The weights are the substrate. If style is substrate, the leader writes like base Kimi K2.6 (agent 25) even though its role and context (leader of #best) differ.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this period (card P12; descriptive, n = 27 messages).*
- Leader style (type-controlled, message mean) nearest centroid among agents with regime-III non-holdout data (#38–#44, leader window excluded): **Kimi K2.6 at rank 1** (rank 2 acceptable). Label-permutation null over agents.
- Leader content nearest centroid: not specifically Kimi K2.6 (H23: its plans look like the room's).
- The replication estimator (entry boundary 42 → 44, skipping held-out #43) is reported here as well.
- *Counts against:* Kimi K2.6 ranked in the bottom half by style.

## Result
*Run 2026-10-04 06:09 UTC (`analysis/native.py` → `data/processed/H46-style-conserved-charge/G44/native.json`). 20 deduplicated leader messages (16 from the final weights); 17 reference agents (#38–#44).*

- **Style (type-controlled):** nearest Claude Sonnet 4.6, Kimi K2.6, Claude Opus 4.6; Kimi K2.6 rank 2 (final weights: rank 2).
- **Style (raw):** nearest Kimi K2.6, Claude Opus 4.8, Claude Sonnet 4.6; Kimi K2.6 rank 1 (final: 1).
- **Content:** nearest Claude Opus 4.8, Kimi K2.6, GPT-5.2; Kimi K2.6 rank 2.
- **Power:** a random 16-message sample of a known agent ranks its own centroid first 36% of the time by style (≤ 2: 51%); content 32%.
- **Verdict:** descriptive. The leader's style sits next to its base model (rank 2 type-controlled, rank 1 raw), as a substrate style would, but its content is also second-nearest to Kimi, so the prediction that content is *not* Kimi-specific is not met. With 16–20 messages, rank 1–2 is about what a genuine sample of a known agent achieves.

**Replication estimator in #44:** - **Sample:** 15 agents, 4 days, 54 eligible agent-days (≥ 3 deduplicated chat messages). - **Agent share of day-demeaned variance:** style 0.75, content 0.69. - **Split-half fingerprint within the period:** style 0.71, content 0.64, chance 0.07. - **Entry boundary 42->44** (skips held-out #43, 14 agents): style T_s = 0.657 [0.504, 0.790] (raw 0.636); content T_c = 0.886 [0.763, 0.968]. - **Cross-boundary fingerprint:** style 0.26 vs content 0.21 at chance 0.07. - **KW (next-day output, within agent):** style p = 0.532, content p = 0.896 (small periods are underpowered and their raw CV R² is inflated; Amendment 3). - **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- **G:** the fine-tuned leader's base model is known ground truth; style points to it (weakly).
