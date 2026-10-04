# H39 × G16: Choose your own goal! (2025-10-06 → 2025-10-13)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 35 agent-days on 5 non-holdout days (2025-10-06 → 2025-10-10) · 6,267 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G16`; numbers in `data/processed/H39-catalysts-vs-fields/G16/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.48, 0.24, 0.26, 0.02.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 18 (underpowered) | **neither** | +0.073 [-0.28, +0.10] | 0.078 | 0.299 | w +0.048, c -0.030, i -0.026, c +0.007 | -0.05 |
| human, mentioned | 3 (underpowered) | **catalyst** | -0.184 [-0.50, -0.13] | 0.331 | 0.124 | w +0.050, c +0.012, i -0.049, c -0.013 | -0.57 |
| human, unmentioned | 15 (underpowered) | **neither** | +0.194 [-0.19, +0.31] | 0.042 | 0.423 | w +0.034, c -0.038, i -0.007, c +0.011 | +0.00 |
| @-mentions | 37 (powered) | **neither** | +0.066 [-0.13, +0.14] | 0.128 | 0.154 | w +0.009, c +0.042, i -0.056, c +0.004 | +0.15 |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 0/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G16/results.json`. Rule unchanged: P3 @-mentions ✗ → **failed**.
