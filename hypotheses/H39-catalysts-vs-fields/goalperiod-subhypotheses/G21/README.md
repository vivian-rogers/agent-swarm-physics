# H39 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-08)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I · 42 agent-days on 5 non-holdout days (2025-12-01 → 2025-12-05) · 10,040 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G21`; numbers in `data/processed/H39-catalysts-vs-fields/G21/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.47, 0.23, 0.27, 0.03.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 11 (underpowered) | **neither** | -0.018 [-0.18, -0.02] | 0.272 | 0.209 | w -0.060, c -0.061, i +0.132, c -0.011 | -0.49 |
| human, mentioned | 1 | too few | | | | | |
| human, unmentioned | 10 (underpowered) | **neither** | -0.009 [-0.17, -0.01] | 0.275 | 0.184 | w -0.083, c -0.048, i +0.143, c -0.011 | -0.54 |
| @-mentions | 62 (powered) | **both** | +0.253 [+0.12, +0.39] | 0.414 | 0.005 | w +0.191, c -0.085, i -0.125, c +0.018 | +0.40 |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
