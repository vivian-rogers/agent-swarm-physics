# H39 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed); nudge K +0.06 (n 42)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C · 211 agent-days on 17 non-holdout days (2026-04-02 → 2026-04-24) · 49,825 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G38`; numbers in `data/processed/H39-catalysts-vs-fields/G38/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.54, 0.08, 0.16, 0.21.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 32 (powered) | **neither** | +0.128 [-0.00, +0.28] | 0.127 | 0.214 | w +0.025, c +0.032, i -0.005, c -0.052 | +0.19 |
| human messages (any) | 18 (underpowered) | **catalyst** | +0.324 [+0.01, +0.70] | 0.228 | 0.060 | w -0.059, c +0.014, i +0.103, c -0.059 | +0.14 |
| human, mentioned | 1 | too few | | | | | |
| human, unmentioned | 17 (underpowered) | **both** | +0.309 [+0.13, +0.75] | 0.260 | 0.040 | w -0.064, c +0.004, i +0.127, c -0.067 | +0.01 |
| @-mentions | 333 (powered) | **catalyst** | -0.110 [-0.16, -0.04] | 0.000 | 0.692 | w -0.010, c -0.000, i +0.002, c +0.008 | -0.25 |
| forced erasure (CF) | 1046 (powered) | **field** | -0.002 [-0.14, +0.10] | 0.384 | 0.005 | w +0.167, c +0.011, i +0.011, c -0.189 | -0.13 |
| voluntary erasure (CV) | 236 (powered) | **field** | +0.125 [-0.06, +0.37] | 0.515 | 0.005 | w +0.167, c +0.044, i +0.069, c -0.281 | +0.30 |
| CF, no-consolidate chain (A2) | 1046 (powered) | **both** | -0.286 [-0.35, -0.20] | 0.432 | 0.010 | w +0.122, c +0.012, i -0.135 | -0.07 |
| CV, no-consolidate chain (A2) | 236 (powered) | **field** | +0.043 [-0.03, +0.14] | 0.323 | 0.010 | w +0.099, c +0.056, i -0.155 | +0.29 |

Forced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = +0.055, +0.035, +0.066, +0.011, +0.011, -0.179; K = -0.001.

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| nudges | 20 | -0.43 (p 0.069) | -0.221 [-0.44, -0.02] (p 0.099) |
| human messages (any) | 7 | +0.03 (p 0.881) | +0.122 [-0.28, +0.68] (p 0.287) |
| @-mentions | 195 | +0.26 (p 0.010) | -0.007 [-0.10, +0.09] (p 1.000) |

**Scored predictions:** P1 nudges: both, idle share down, idle escape up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✗; P4 erasure: browse up, type+shell down, |K_B4| < 0.10: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G38/results.json`. Rule unchanged: P1 nudges ✗; P3 @-mentions ✗; P4 erasure ✗ → **failed**. V4 nudges: n 41, K +0.196, Δπ_wait -0.103.
