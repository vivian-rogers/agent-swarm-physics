# H73 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-05)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime I · 7 agents with eligible messages · 5 days · 3,004 eligible messages (749 in computer-use mode) · units 12a, 12b.

## Why this period
Native: the only non-holdout period with an assigned, rotating speech register inside the period (debate judges), so the register component is identified within agent.

## Prediction
*Written 2026-10-04 19:28 UTC, before running on this period.*
- **Registers (DQ6):** judge (inside a debate window the agent judges), debater (inside a window where it has a team), outside. Judges: agents 6, 5, 11, 0 (one debate each) and 9 (debates 5–10).
- **N2 predictions:** (i) the register block has a positive unique share u_R (judge-label permutation within agent, p < 0.05). (ii) Judging is a shared register: the mean cosine between a judge's own judge shift and the leave-this-agent-out mean shift of the other judges is > 0 (permutation p < 0.05). (iii) Adding the leave-agent-out judge shift to every candidate centroid raises attribution of judge-window messages (blocks of 5) by ≥ 0.05.
- **Replication layer:** the templated O1–O3 rule also applies (reported, not the native verdict).
- *Counts against:* mean cosine ≤ 0 (each judge moves in its own direction: the register is agent-specific, not assigned).

**Templated replication prediction (also reported):**
*Written 2026-10-04 19:28 UTC, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **O1 decomposition** (17-d type-controlled style; blocks: day field + time of day G, agent constant A, context C, register R where defined): the three components explain most of the non-day-field systematic variance, F3 ≥ 0.57 (0.5 plus the synthetic bias margin, Amendment A2).
- **Ordering:** the agent constant has the largest unique share (u_A > u_C, u_R). With ≥ 500 computer-use messages, the context share is positive (within-agent-day permutation p < 0.05).
- **O2 attribution** (leave-one-day-out, blocks of 5 messages): the agent-specific context model beats the blind centroid, Δ_c > 0.
- **O3 dispersion** (descriptive unless ≥ 2,000 computer-use messages): residual dispersion rises with context fill.
- **Verdict rule:** supported if F3 ≥ 0.57, u_A is the largest unique share and Δ_c > 0 (plus p_C < 0.05 where n_cu ≥ 500); failed if F3 < 0.5 and Δ_c ≤ 0; otherwise mixed.
- *Counts against:* F3 < 0.5 (agent-day jitter carries most systematic style variance) and no attribution gain from the context model.

## Result
*Run 2026-10-04 19:46 UTC (`analysis/natives.py` → `natives.json`, key G12).*

- **Messages:** 3,004 (judge 218, debater 900, outside 1886); judges with ≥ 3 judge and ≥ 3 debater messages: 5 of 5.
- **(i) Register share:** ΔR²_adj(R | G, A, C) = 0.0113 (u_R = 0.056 of the non-day systematic variance); judge-window permutation p = 0.001 (1000 draws).
- **(ii) Shared judge direction:** mean leave-agent-out cosine = +0.78 (per judge: +0.82, +0.65, +0.79, +0.82, +0.83); permutation p = 0.001; null mean +0.01.
- **(iii) Attribution of judge messages:** blocks of 5: blind 0.43 → with the shared judge shift 0.44 (Δ = +0.01; 41 blocks); whole judge windows: 0.53 → 0.43 (10 windows). Chance 0.14.
- **Verdict (rule fixed 19:28 UTC):** (i) pass, (ii) pass, (iii) fail → **mixed**.

**Replication layer (templated):**
- **Sample:** 3,004 messages, 7 agents, 5 days, 749 computer-use; 286 cells.
- **Ceiling κ** (adjusted R² of agent × day × context bin × register cells): 0.223; day field + time of day R²: 0.022.
- **F3** = 0.67 [0.58, 0.76] (delete-one-day jackknife, ±1.96 SE); unique shares u_A 0.43, u_C 0.071 (permutation p 0.005; null-corrected 0.071), u_R 0.056.
- **Attribution** (blocks of 5, 586 blocks, chance 0.14): blind 0.52, common-detrended 0.56, agent-specific context 0.58; Δ_c = +0.061, Δ_b = +0.044.
- **Dispersion slope** (residual ‖e‖² per unit z, relative to mean ‖e‖²): +0.078 (CI on raw slope [-0.34, 0.89]), descriptive (n_cu < 2,000).
- **Templated verdict:** supported.

## Scorecard (period-specific axes)
- **G (ground truth):** DQ6 judge and team windows define the register.
- **E (interventional):** the judge draw assigns the register from outside; judging moves style in a shared direction.
- **H (rivals):** a shared direction separates an assigned register from agent-specific responses.
