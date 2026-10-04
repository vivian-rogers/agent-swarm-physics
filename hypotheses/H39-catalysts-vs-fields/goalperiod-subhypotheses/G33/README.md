# H39 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-05)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C · 33 agent-days on 3 non-holdout days (2026-03-02 → 2026-03-04) · 7,736 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G33`; numbers in `data/processed/H39-catalysts-vs-fields/G33/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.45, 0.21, 0.29, 0.05.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 1 | too few | | | | | |
| human messages (any) | 0 | too few | | | | | |
| human, mentioned | 0 | too few | | | | | |
| human, unmentioned | 0 | too few | | | | | |
| @-mentions | 48 (powered) | **field** | +0.034 [-0.08, +0.46] | 0.309 | 0.010 | w -0.125, c -0.039, i +0.146, c +0.017 | -0.11 |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
