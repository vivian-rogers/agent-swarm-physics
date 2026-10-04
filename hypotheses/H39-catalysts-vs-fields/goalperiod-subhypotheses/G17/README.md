# H39 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-20)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode I · 35 agent-days on 5 non-holdout days (2025-10-13 → 2025-10-17) · 6,278 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G17`; numbers in `data/processed/H39-catalysts-vs-fields/G17/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.32, 0.25, 0.40, 0.03.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 25 (powered) | **both** | +0.144 [+0.04, +0.49] | 0.351 | 0.020 | w +0.104, c -0.141, i +0.026, c +0.011 | +0.02 |
| human, mentioned | 3 (underpowered) | **neither** | +0.108 [-0.09, +0.77] | 0.539 | 0.308 | w -0.264, c +0.147, i +0.135, c -0.018 | +0.46 |
| human, unmentioned | 22 (powered) | **field** | +0.154 [-0.01, +0.56] | 0.452 | 0.015 | w +0.128, c -0.169, i +0.025, c +0.015 | -0.05 |
| @-mentions | 31 (powered) | **catalyst** | +0.226 [+0.00, +0.48] | 0.000 | 0.970 | w +0.012, c +0.000, i -0.015, c +0.003 | +0.44 |

**Scored predictions:** P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 2/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G17/results.json`. Rule unchanged: P2 human messages ✗; P3 @-mentions ✗ → **failed**.
