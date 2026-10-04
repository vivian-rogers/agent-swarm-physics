# H39 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-09-01)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 35 agent-days on 5 non-holdout days (2025-08-25 → 2025-08-29) · 6,195 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G11`; numbers in `data/processed/H39-catalysts-vs-fields/G11/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.42, 0.30, 0.26, 0.03.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 22 (powered) | **field** | -0.076 [-0.38, +0.09] | 0.294 | 0.035 | w -0.129, c +0.040, i +0.111, c -0.022 | -0.15 |
| human, mentioned | 1 | too few | | | | | |
| human, unmentioned | 21 (powered) | **field** | -0.073 [-0.43, +0.17] | 0.352 | 0.035 | w -0.157, c +0.048, i +0.132, c -0.023 | -0.16 |
| @-mentions | 38 (powered) | **neither** | +0.088 [+0.03, +0.18] | 0.137 | 0.189 | w -0.074, c +0.050, i +0.035, c -0.012 | +0.34 |

**Scored predictions:** P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G11/results.json`. Rule unchanged: P2 human messages ✗; P3 @-mentions ✗ → **failed**.
