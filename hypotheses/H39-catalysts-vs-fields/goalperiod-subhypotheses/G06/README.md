# H39 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-16)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K · 60 agent-days on 15 non-holdout days (2025-06-26 → 2025-07-15) · 10,479 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift. Many human messages (public chat era / #51).

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges:** none (the nudger starts 2026-02-13).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G06`; numbers in `data/processed/H39-catalysts-vs-fields/G06/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.40, 0.18, 0.40, 0.02.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 29 (powered) | **field** | -0.281 [-0.87, +0.06] | 0.739 | 0.005 | w +0.244, c -0.123, i -0.099, c -0.022 | +0.29 |
| human, mentioned | 1 | too few | | | | | |
| human, unmentioned | 28 (powered) | **field** | -0.236 [-0.83, +0.15] | 0.825 | 0.005 | w +0.271, c -0.127, i -0.122, c -0.021 | +0.38 |
| @-mentions | 23 (powered) | **field** | -0.107 [-0.45, +0.19] | 0.228 | 0.020 | w -0.123, c +0.044, i +0.058, c +0.021 | -0.15 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| human messages (any) | 9 | +0.38 (p 0.158) | +0.179 [-0.41, +0.61] (p 0.267) |
| @-mentions | 7 | +0.70 (p 0.010) | +0.005 [-0.24, +0.10] (p 0.822) |

**Scored predictions:** P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✓.

## Scorecard (period-specific axes)
- **C (adequacy):** 2/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
