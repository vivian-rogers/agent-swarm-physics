# H39 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-22)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K · 50 agent-days on 5 non-holdout days (2025-12-15 → 2025-12-19) · 11,903 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G23`; numbers in `data/processed/H39-catalysts-vs-fields/G23/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.66, 0.14, 0.16, 0.04.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 21 (powered) | **field** | +0.152 [-0.24, +0.34] | 0.318 | 0.005 | w +0.146, c -0.062, i -0.071, c -0.013 | +0.14 |
| human, mentioned | 1 | too few | | | | | |
| human, unmentioned | 20 (powered) | **field** | +0.186 [-0.24, +0.44] | 0.314 | 0.020 | w +0.144, c -0.069, i -0.067, c -0.008 | +0.14 |
| @-mentions | 82 (powered) | **catalyst** | +0.100 [+0.03, +0.18] | 0.000 | 0.547 | w +0.002, c -0.013, i +0.005, c +0.007 | +0.04 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| @-mentions | 22 | -0.59 (p 0.010) | -0.218 [-0.61, +0.12] (p 0.050) |

**Scored predictions:** P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 2/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
