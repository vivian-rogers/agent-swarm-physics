# H39 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 55 agent-days on 5 non-holdout days (2026-02-09 → 2026-02-13) · 13,191 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift.

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges:** none (the nudger starts 2026-02-13) ; G30 has nudges only on its last day, expected underpowered.
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G30`; numbers in `data/processed/H39-catalysts-vs-fields/G30/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.58, 0.17, 0.20, 0.05.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 8 (underpowered) | **neither** | -0.105 [-0.21, +0.07] | 0.000 | 0.612 | w -0.014, c -0.021, i -0.026, c +0.061 | -0.05 |
| human, mentioned | 0 | too few | | | | | |
| human, unmentioned | 8 (underpowered) | **neither** | -0.105 [-0.21, +0.07] | 0.000 | 0.612 | w -0.014, c -0.021, i -0.026, c +0.061 | -0.05 |
| @-mentions | 98 (powered) | **field** | -0.050 [-0.08, +0.01] | 0.218 | 0.005 | w +0.105, c -0.035, i -0.060, c -0.009 | +0.03 |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G30/results.json`. Rule unchanged: P3 @-mentions ✗ → **failed**.
