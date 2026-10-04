# H39 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I · 74 agent-days on 5 non-holdout days (2026-04-27 → 2026-05-01) · 16,920 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift. Nudger on: nudge episodes available. Regime III: forced context erasures (NE41) available.

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges (N_tgt), P1:** both: Δπ_idle < 0 and idle escape up (ln e^K_idle/e^C_idle > 0); K > 0. Against: π unchanged with K > 0 (pure catalyst, HH52) or K ≈ 0 (pure field).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Context erasure (NE41: CF forced, CV voluntary), P4:** on B6 Δπ_browse > 0 and Δπ_type+shell < 0; |K| < 0.10 on B4; CF and CV the same class.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G39`; numbers in `data/processed/H39-catalysts-vs-fields/G39/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.59, 0.05, 0.17, 0.20.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 2 | too few | | | | | |
| human messages (any) | 34 (powered) | **field** | -0.025 [-0.10, +0.08] | 0.323 | 0.005 | w -0.007, c -0.031, i +0.115, c -0.077 | -0.23 |
| human, mentioned | 2 | too few | | | | | |
| human, unmentioned | 32 (powered) | **field** | -0.017 [-0.05, +0.08] | 0.318 | 0.005 | w -0.013, c -0.030, i +0.115, c -0.072 | -0.24 |
| @-mentions | 125 (powered) | **field** | +0.040 [-0.08, +0.12] | 0.189 | 0.005 | w +0.045, c -0.028, i +0.028, c -0.045 | -0.06 |
| forced erasure (CF) | 424 (powered) | **field** | -0.284 [-0.47, +0.01] | 0.203 | 0.010 | w +0.061, c -0.005, i +0.003, c -0.060 | +0.08 |
| voluntary erasure (CV) | 70 (powered) | **both** | +0.361 [+0.19, +1.05] | 0.517 | 0.010 | w +0.175, c +0.016, i +0.124, c -0.315 | +0.13 |
| CF, no-consolidate chain (A2) | 424 (powered) | **both** | -0.193 [-0.27, -0.14] | 0.413 | 0.010 | w +0.160, c -0.033, i -0.128 | +0.10 |
| CV, no-consolidate chain (A2) | 70 (powered) | **neither** | -0.039 [-0.29, +0.09] | 0.129 | 0.099 | w +0.078, c -0.022, i -0.057 | +0.08 |

Forced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = +0.020, +0.018, +0.024, -0.002, +0.002, -0.061; K = -0.138.

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| human messages (any) | 6 | -0.21 (p 0.703) | +0.298 [+0.30, +0.30] (p 0.109) |
| @-mentions | 66 | +0.19 (p 0.050) | +0.053 [-0.23, +0.23] (p 0.287) |

**Scored predictions:** P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✗; P4 erasure: browse up, type+shell down, |K_B4| < 0.10: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 2/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.
