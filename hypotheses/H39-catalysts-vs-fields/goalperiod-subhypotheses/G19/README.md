# H39 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-17)

**Verdict:** failed
**Verdict (1b):** supported (r1 failed)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C · 71 agent-days on 10 non-holdout days (2025-11-03 → 2025-11-14) · 16,912 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G19`; numbers in `data/processed/H39-catalysts-vs-fields/G19/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.49, 0.26, 0.22, 0.03.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 9 (underpowered) | **field** | +0.275 [-0.25, +2.06] | 0.741 | 0.005 | w -0.259, c +0.037, i +0.238, c -0.016 | -0.22 |
| human, mentioned | 0 | too few | | | | | |
| human, unmentioned | 9 (underpowered) | **field** | +0.275 [-0.25, +2.06] | 0.741 | 0.005 | w -0.259, c +0.037, i +0.238, c -0.016 | -0.22 |
| @-mentions | 123 (powered) | **neither** | +0.019 [-0.09, +0.13] | 0.129 | 0.055 | w +0.044, c +0.009, i -0.055, c +0.002 | +0.05 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| human messages (any) | 5 | +0.05 (p 0.624) | -0.132 [-0.74, +0.31] (p 0.505) |
| @-mentions | 51 | +0.56 (p 0.010) | -0.082 [-0.27, +0.08] (p 0.277) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 0/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G19/results.json`. Rule unchanged: P3 @-mentions ✓ → **supported**.
