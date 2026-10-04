# H39 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-26)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K · 100 agent-days on 10 non-holdout days (2026-01-12 → 2026-01-23) · 23,939 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G27`; numbers in `data/processed/H39-catalysts-vs-fields/G27/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.52, 0.15, 0.29, 0.04.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 17 (underpowered) | **catalyst** | +0.176 [+0.15, +0.34] | 0.236 | 0.055 | w +0.071, c +0.024, i -0.104, c +0.009 | +0.37 |
| human, mentioned | 0 | too few | | | | | |
| human, unmentioned | 17 (underpowered) | **catalyst** | +0.176 [+0.15, +0.34] | 0.236 | 0.055 | w +0.071, c +0.024, i -0.104, c +0.009 | +0.37 |
| @-mentions | 151 (powered) | **field** | +0.027 [-0.04, +0.11] | 0.121 | 0.005 | w -0.057, c +0.026, i +0.035, c -0.005 | +0.00 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| @-mentions | 81 | +0.04 (p 0.653) | -0.118 [-0.21, -0.02] (p 0.020) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✓.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
