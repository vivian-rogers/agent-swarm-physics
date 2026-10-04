# H39 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** failed
**Verdict (1b):** supported (r1 failed)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 56 agent-days on 5 non-holdout days (2026-02-16 → 2026-02-20) · 13,391 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G31`; numbers in `data/processed/H39-catalysts-vs-fields/G31/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.51, 0.20, 0.25, 0.05.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 2 | too few | | | | | |
| human messages (any) | 12 (underpowered) | **neither** | -0.067 [-0.30, +0.07] | 0.119 | 0.338 | w -0.014, c -0.046, i +0.033, c +0.027 | -0.16 |
| human, mentioned | 1 | too few | | | | | |
| human, unmentioned | 11 (underpowered) | **neither** | -0.081 [-0.30, +0.05] | 0.126 | 0.294 | w -0.018, c -0.049, i +0.049, c +0.019 | -0.19 |
| @-mentions | 82 (powered) | **field** | +0.024 [-0.08, +0.11] | 0.206 | 0.005 | w -0.099, c -0.001, i +0.087, c +0.013 | -0.30 |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G31/results.json`. Rule unchanged: P3 @-mentions ✓ → **supported**.
