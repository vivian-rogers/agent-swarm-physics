# H39 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 75 agent-days on 10 non-holdout days (2025-10-20 → 2025-10-31) · 16,956 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift. Contains the unnumbered CHANGELOG step S20251022 (2025-10-22).

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges:** none (the nudger starts 2026-02-13).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Scaffold step S20251022 (2025-10-22; prompt: keep working right up until the end of each day (activity instruction)), P7:** field (Δπ_idle < 0) if anything, most likely inside the placebo band. Judged against within-goal day-boundary placebos of the same era.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G18`; numbers in `data/processed/H39-catalysts-vs-fields/G18/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.39, 0.30, 0.29, 0.02.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 0 | too few | | | | | |
| human messages (any) | 8 (underpowered) | **neither** | +0.336 [-0.72, +0.74] | 0.512 | 0.109 | w -0.218, c +0.051, i +0.157, c +0.010 | +0.11 |
| human, mentioned | 1 | too few | | | | | |
| human, unmentioned | 7 (underpowered) | **neither** | +0.326 [-0.67, +0.64] | 0.469 | 0.144 | w -0.210, c +0.072, i +0.125, c +0.013 | +0.15 |
| @-mentions | 128 (powered) | **field** | +0.091 [-0.09, +0.27] | 0.177 | 0.020 | w +0.088, c -0.044, i -0.049, c +0.006 | +0.13 |

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| @-mentions | 11 | -0.42 (p 0.149) | -0.148 [-0.50, +0.11] (p 0.376) |

**Step S20251022** (prompt: keep working right up until the end of each day; pre 2025-10-20, 2025-10-21 → post 2025-10-22, 2025-10-23; 7 agents in the balanced panel; placebo pool: era I-4h, n = 43).

| State family | class | φ (percentile in placebo) | K (percentile) | Δπ |
| --- | --- | --- | --- | --- |
| behavior B4 | **neither** | 0.352 (91) | +0.030 (56) | work -0.135, chat +0.147, idle -0.010, consolidate -0.002 |
| content C6 | **neither** | 2.105 (86) | +0.807 (74) | (clusters) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period except the scaffold step below.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
