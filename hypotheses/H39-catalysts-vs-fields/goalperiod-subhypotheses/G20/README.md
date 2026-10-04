# H39 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-12-01)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I · 92 agent-days on 10 non-holdout days (2025-11-17 → 2025-11-28) · 21,664 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G20`; numbers in `data/processed/H39-catalysts-vs-fields/G20/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.57, 0.20, 0.19, 0.04.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 17 (underpowered) | **field** | -0.004 [-0.08, +0.07] | 0.303 | 0.045 | w +0.097, c -0.075, i -0.030, c +0.007 | -0.09 |
| human, mentioned | 3 (underpowered) | **neither** | -0.007 [-0.07, +0.03] | 0.225 | 0.224 | w +0.067, c -0.057, i -0.023, c +0.014 | -0.21 |
| human, unmentioned | 14 (underpowered) | **neither** | -0.026 [-0.10, +0.07] | 0.276 | 0.085 | w +0.106, c -0.072, i -0.031, c -0.004 | -0.10 |
| @-mentions | 150 (powered) | **neither** | +0.070 [-0.04, +0.17] | 0.052 | 0.174 | w -0.033, c +0.008, i +0.021, c +0.004 | +0.05 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| human messages (any) | 5 | +0.14 (p 0.941) | +0.460 [+0.41, +0.65] (p 0.059) |
| @-mentions | 47 | +0.89 (p 0.010) | +0.265 [+0.16, +0.39] (p 0.010) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 0/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
