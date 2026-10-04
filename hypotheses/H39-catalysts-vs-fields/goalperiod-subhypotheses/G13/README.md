# H39 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-22)

**Verdict:** mixed
**Verdict (1b):** mixed (r1 mixed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 60 agent-days on 10 non-holdout days (2025-09-08 → 2025-09-19) · 10,568 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift.

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges:** none (the nudger starts 2026-02-13).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G13`; numbers in `data/processed/H39-catalysts-vs-fields/G13/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.44, 0.31, 0.22, 0.03.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 40 (powered) | **field** | +0.084 [-0.10, +0.20] | 0.305 | 0.005 | w +0.114, c -0.114, i -0.019, c +0.019 | +0.02 |
| human, mentioned | 2 | too few | | | | | |
| human, unmentioned | 38 (powered) | **field** | +0.063 [-0.06, +0.19] | 0.264 | 0.010 | w +0.088, c -0.103, i -0.006, c +0.020 | -0.00 |
| @-mentions | 55 (powered) | **field** | +0.017 [-0.10, +0.15] | 0.220 | 0.005 | w -0.104, c +0.027, i +0.076, c +0.001 | -0.08 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| human messages (any) | 7 | +1.73 (p 0.010) | +0.428 [+0.18, +0.56] (p 0.109) |
| @-mentions | 14 | -0.13 (p 0.604) | -0.123 [-0.41, +0.07] (p 0.634) |

**Scored predictions:** P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✓.

## Scorecard (period-specific axes)
- **C (adequacy):** 2/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G13/results.json`. Rule unchanged: P2 human messages ✗; P3 @-mentions ✓ → **mixed**.
