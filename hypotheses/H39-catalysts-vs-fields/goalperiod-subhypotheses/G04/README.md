# H39 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-19)

**Verdict:** supported
**Verdict (1b):** mixed (r1 supported)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C · 100 agent-days on 25 non-holdout days (2025-05-15 → 2025-06-18) · 13,090 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift. Many human messages (public chat era / #51).

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges:** none (the nudger starts 2026-02-13).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G04`; numbers in `data/processed/H39-catalysts-vs-fields/G04/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.37, 0.35, 0.26, 0.02.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 63 (powered) | **both** | +0.578 [+0.16, +1.06] | 0.798 | 0.005 | w +0.172, c +0.088, i -0.274, c +0.014 | +1.10 |
| human, mentioned | 2 | too few | | | | | |
| human, unmentioned | 60 (powered) | **both** | +0.561 [+0.18, +0.95] | 0.710 | 0.005 | w +0.135, c +0.102, i -0.250, c +0.014 | +1.04 |
| @-mentions | 18 (underpowered) | **catalyst** | +0.314 [+0.07, +0.61] | 0.569 | 0.139 | w +0.351, c -0.199, i -0.153, c +0.001 | +0.55 |

**Scored predictions:** P2 human messages: both, chat share up: ✓.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G04/results.json`. Rule unchanged: P2 human messages ✓; P3 @-mentions ✗ → **mixed**.
