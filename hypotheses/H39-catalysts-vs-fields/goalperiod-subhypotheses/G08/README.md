# H39 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-13)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 72 agent-days on 18 non-holdout days (2025-07-18 → 2025-08-12) · 12,293 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift. Contains the unnumbered CHANGELOG step S20250801 (2025-08-01).

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges:** none (the nudger starts 2026-02-13).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Scaffold step S20250801 (2025-08-01; prompt: encouraged the agent to keep going (activity instruction)), P7:** field (Δπ_idle < 0) if anything, most likely inside the placebo band. Judged against within-goal day-boundary placebos of the same era.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G08`; numbers in `data/processed/H39-catalysts-vs-fields/G08/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.59, 0.23, 0.15, 0.03.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 30 (powered) | **field** | -0.010 [-0.28, +0.30] | 0.168 | 0.020 | w -0.021, c +0.005, i +0.028, c -0.012 | +0.01 |
| human, mentioned | 3 (underpowered) | **both** | +0.483 [+0.23, +0.54] | 1.081 | 0.005 | w -0.634, c -0.097, i +0.738, c -0.007 | -1.91 |
| human, unmentioned | 27 (powered) | **field** | -0.014 [-0.26, +0.29] | 0.157 | 0.040 | w +0.012, c -0.002, i +0.003, c -0.013 | +0.16 |
| @-mentions | 59 (powered) | **field** | -0.006 [-0.12, +0.15] | 0.177 | 0.010 | w -0.065, c -0.012, i +0.078, c -0.001 | -0.30 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| human messages (any) | 19 | -0.35 (p 0.139) | -0.035 [-0.26, +0.11] (p 0.842) |
| @-mentions | 28 | +0.14 (p 0.297) | +0.426 [+0.18, +0.59] (p 0.010) |

**Step S20250801** (prompt: encouraged the agent to keep going; pre 2025-07-30, 2025-07-31 → post 2025-08-01, 2025-08-04; 4 agents in the balanced panel; placebo pool: era I-early, n = 45).

| State family | class | φ (percentile in placebo) | K (percentile) | Δπ |
| --- | --- | --- | --- | --- |
| behavior B4 | **neither** | 0.065 (4) | +0.032 (49) | work +0.012, chat +0.007, idle -0.015, consolidate -0.005 |
| content C6 | **neither** | 1.437 (89) | -0.342 (11) | (clusters) |

**Scored predictions:** P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 2/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period except the scaffold step below.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G08/results.json`. Rule unchanged: P2 human messages ✗; P3 @-mentions ✗ → **failed**.
