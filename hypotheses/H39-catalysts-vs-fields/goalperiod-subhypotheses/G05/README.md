# H39 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-26)

**Verdict:** descriptive
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 20 agent-days on 5 non-holdout days (2025-06-19 → 2025-06-25) · 2,336 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G05`; numbers in `data/processed/H39-catalysts-vs-fields/G05/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.49, 0.40, 0.09, 0.02.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 0 | too few | | | | | |
| human, mentioned | 0 | too few | | | | | |
| human, unmentioned | 0 | too few | | | | | |
| @-mentions | 0 | too few | | | | | |

**Scored predictions:** no class powered (≥ 20 episodes); descriptive only.

## Scorecard (period-specific axes)
- **C (adequacy):** 0/0 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
