# H39 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed); nudge K +0.42 (n 3)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C · 60 agent-days on 5 non-holdout days (2026-03-16 → 2026-03-20) · 14,290 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift. Nudger on: nudge episodes available.

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges (N_tgt), P1:** both: Δπ_idle < 0 and idle escape up (ln e^K_idle/e^C_idle > 0); K > 0. Against: π unchanged with K > 0 (pure catalyst, HH52) or K ≈ 0 (pure field).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G35`; numbers in `data/processed/H39-catalysts-vs-fields/G35/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.65, 0.14, 0.17, 0.05.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 1 | too few | | | | | |
| human messages (any) | 8 (underpowered) | **field** | -0.056 [-0.19, +0.02] | 0.570 | 0.005 | w -0.266, c -0.030, i +0.305, c -0.009 | -1.10 |
| human, mentioned | 1 | too few | | | | | |
| human, unmentioned | 7 (underpowered) | **field** | +0.035 [-0.22, +0.13] | 0.464 | 0.005 | w -0.234, c +0.021, i +0.189, c +0.024 | -0.68 |
| @-mentions | 117 (powered) | **neither** | +0.071 [+0.01, +0.13] | 0.042 | 0.264 | w -0.002, c -0.013, i +0.017, c -0.002 | +0.06 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| @-mentions | 30 | +0.16 (p 0.277) | +0.147 [+0.07, +0.20] (p 0.040) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 0/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G35/results.json`. Rule unchanged: P3 @-mentions ✗ → **failed**.
