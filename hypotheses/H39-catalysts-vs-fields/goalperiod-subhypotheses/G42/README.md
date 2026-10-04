# H39 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I · 78 agent-days on 5 non-holdout days (2026-05-18 → 2026-05-22) · 18,517 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G42`; numbers in `data/processed/H39-catalysts-vs-fields/G42/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.60, 0.06, 0.13, 0.21.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 1 | too few | | | | | |
| human messages (any) | 5 (underpowered) | **catalyst** | +0.271 [+0.27, +0.27] | 0.190 | 0.403 | w -0.096, c -0.013, i +0.143, c -0.034 | -0.67 |
| human, mentioned | 0 | too few | | | | | |
| human, unmentioned | 5 (underpowered) | **catalyst** | +0.271 [+0.27, +0.27] | 0.190 | 0.403 | w -0.096, c -0.013, i +0.143, c -0.034 | -0.67 |
| @-mentions | 130 (powered) | **both** | +0.122 [+0.08, +0.17] | 0.100 | 0.010 | w +0.041, c -0.013, i +0.008, c -0.036 | +0.02 |
| forced erasure (CF) | 387 (powered) | **field** | +0.248 [-0.01, +0.52] | 0.315 | 0.010 | w +0.126, c +0.009, i +0.013, c -0.147 | -0.02 |
| voluntary erasure (CV) | 85 (powered) | **neither** | +0.084 [-0.39, +0.44] | 0.289 | 0.179 | w +0.089, c +0.013, i +0.026, c -0.128 | -0.22 |
| CF, no-consolidate chain (A2) | 387 (powered) | **both** | -0.269 [-0.44, -0.14] | 0.341 | 0.010 | w +0.102, c +0.007, i -0.109 | -0.05 |
| CV, no-consolidate chain (A2) | 85 (powered) | **catalyst** | -0.219 [-0.35, -0.10] | 0.089 | 0.267 | w +0.051, c +0.002, i -0.053 | -0.18 |

Forced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = +0.048, +0.033, +0.049, +0.012, +0.016, -0.158; K = +0.512.

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| human messages (any) | 5 | +0.34 (p 0.327) | +0.478 [+0.48, +0.48] (p 0.020) |
| @-mentions | 66 | +0.66 (p 0.010) | +0.112 [+0.05, +0.20] (p 0.139) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗; P4 erasure: browse up, type+shell down, |K_B4| < 0.10: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.
