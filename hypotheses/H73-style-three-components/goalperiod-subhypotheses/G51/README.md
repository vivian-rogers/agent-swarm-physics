# H73 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime III · 32 agents with eligible messages · 45 days · 40,069 eligible messages (40,069 in computer-use mode) · units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l.

## Why this period
Native: private roles assigned on 07-06 (Prankster, media roles) are the cleanest assigned registers in the record; the persona onset is the intervention.

## Prediction
*Written 2026-10-04 19:28 UTC, before running on this period.*
- **Design:** incumbents with ≥ 20 eligible messages in #36–#44 (non-holdout, regime III) and in #51 07-06 → 07-24. Joint fit on #36–#44 + #51 07-06 → 07-24: day field, time of day, agent constant, context, and an agent-specific #51 shift R_i (the register; exception (c), the transition is the object). Placebo shifts: the same contrast at calendar splits that do not straddle 07-06 (inside #36–#44 and inside #51 07-06 → 09-06), each with a three-week post window.
- **N3 predictions:** (i) the Prankster's (agent 10) unbiased ‖R_i‖² stays above its placebo shifts (percentile ≥ 0.95) after the context component is removed. (ii) The four incumbent media agents (12, 16, 18, 22; three labs) share a register direction: their mean pairwise cosine of R_i exceeds that of the other incumbent pairs (role-label permutation p < 0.05). Prior for (ii): 40%.
- **Replication layer:** the templated O1–O3 rule on #51 non-holdout (registers are agent-constant inside #51, so u_R is not identified there).
- *Counts against:* (i) percentile < 0.9 after detrending (the persona shift was context); (ii) p ≥ 0.05 (registers are role- or agent-specific, not shared by class).

**Templated replication prediction (also reported):**
*Written 2026-10-04 19:28 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **O1 decomposition** (17-d type-controlled style; blocks: day field + time of day G, agent constant A, context C, register R where defined): the three components explain most of the non-day-field systematic variance, F3 ≥ 0.57 (0.5 plus the synthetic bias margin, Amendment A2).
- **Ordering:** the agent constant has the largest unique share (u_A > u_C, u_R). With ≥ 500 computer-use messages, the context share is positive (within-agent-day permutation p < 0.05).
- **O2 attribution** (leave-one-day-out, blocks of 5 messages): the agent-specific context model beats the blind centroid, Δ_c > 0.
- **O3 dispersion** (descriptive unless ≥ 2,000 computer-use messages): residual dispersion rises with context fill.
- **Verdict rule:** supported if F3 ≥ 0.57, u_A is the largest unique share and Δ_c > 0 (plus p_C < 0.05 where n_cu ≥ 500); failed if F3 < 0.5 and Δ_c ≤ 0; otherwise mixed.
- *Counts against:* F3 < 0.5 (agent-day jitter carries most systematic style variance) and no attribution gain from the context model.

## Result
*Run 2026-10-04 19:46 UTC (`analysis/natives.py` → `natives.json`, key G51).*

- **Sample:** 16 incumbents with ≥ 20 eligible messages in #36–#44 (regime III, non-holdout) and in #51 07-06 → 07-24; 23,967 messages. Placebo splits: 11 (pre:2026-04-07, pre:2026-04-14, pre:2026-04-21, pre:2026-04-28, pre:2026-05-05, pre:2026-05-12, pre:2026-05-19, 51:2026-07-27, 51:2026-08-03, 51:2026-08-10, 51:2026-08-17).
- **(i) Prankster (agent 10):** unbiased ‖R‖² = 2.268 with the context component, 2.269 without; percentile among its 10 placebo shifts 0.60 (with C) and 0.60 (without C). Its rank among incumbents by ‖R‖²: 10 of 16.
- **Incumbents at percentile ≥ 0.95 (with C):** 13 (Anthropic), 21 (Anthropic), 25 (Moonshot), 27 (Google).
- **(ii) Media coherence:** mean pairwise cosine of the centred R_i among media incumbents [12, 16, 18, 22] = -0.11; other incumbent pairs -0.06; random 4-sets -0.06; permutation p = 0.563.
- **Verdict (rule fixed 19:28 UTC):** (i) fail, (ii) fail → **failed**.
- *Post hoc PH3 (H46's 3-day-block design, same era fit):* Prankster percentile 1.00 with C, 1.00 without C, among 42 of its own 3-day block pairs ≥ 21 days apart (H46: 1.00 among 15).

**Replication layer (templated):**
- **Sample:** 40,069 messages, 32 agents, 45 days, 40,069 computer-use; 4,636 cells.
- **Ceiling κ** (adjusted R² of agent × day × context bin × register cells): 0.261; day field + time of day R²: 0.035.
- **F3** = 0.71 [0.68, 0.75] (delete-one-day jackknife, ±1.96 SE); unique shares u_A 0.66, u_C 0.015 (permutation p 0.010; null-corrected 0.014).
- **Attribution** (blocks of 5, 7574 blocks, chance 0.03): blind 0.51, common-detrended 0.51, agent-specific context 0.51; Δ_c = -0.002, Δ_b = -0.000.
- **Dispersion slope** (residual ‖e‖² per unit z, relative to mean ‖e‖²): -0.018 (CI on raw slope [-0.48, -0.02]).
- **Templated verdict:** mixed.

## Scorecard (period-specific axes)
- **E (interventional):** the 07-06 role assignment is the intervention; the Prankster's shift does not exceed its placebo band once context is removed.
- **G (ground truth):** DQ6 roles and role classes.
- **H (rivals):** class coherence tests an assigned register against agent-specific responses.

## Round 2 (2026-10-05)
**Round-2 result:** pending.
*Prediction written 2026-10-05 05:07 UTC, before the real round-2 run (card pre-registration 04:46 UTC).*
- **R2-2-P1 (Prankster onset transient):** daily split-half shift S_10(k) since 07-06 (difference-in-differences against the other incumbents) fits S∞ + A e^(−k/τ) with A > 0 (CI > 0), τ ∈ [0.5, 14] days (upper bound < 30), and the k = 21–60 level inside its placebo band.
- **R2-2-P2 (general onset transients):** over the 16 incumbents, mean S(k ≤ 2) − mean S(14 ≤ k ≤ 42) > 0 in a sign test (p < 0.05).
- **R2-2b NE38 (agent 40, 07-29; descriptive):** the k = 0–2 shift exceeds all four pseudo-date values and halves by k = 7–20.
- Replication layer: the templated R2-1a/R2-1b lines also apply.
