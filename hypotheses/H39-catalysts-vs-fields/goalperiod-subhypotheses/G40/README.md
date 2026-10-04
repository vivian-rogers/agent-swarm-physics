# H39 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed); nudge K -0.04 (n 5)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode C · 75 agent-days on 5 non-holdout days (2026-05-04 → 2026-05-08) · 17,713 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G40`; numbers in `data/processed/H39-catalysts-vs-fields/G40/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.57, 0.09, 0.13, 0.21.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 4 (underpowered) | **catalyst** | +0.368 [+0.11, +1.33] | 0.000 | 0.851 | w -0.050, c +0.039, i +0.033, c -0.022 | -0.02 |
| human messages (any) | 0 | too few | | | | | |
| human, mentioned | 0 | too few | | | | | |
| human, unmentioned | 0 | too few | | | | | |
| @-mentions | 111 (powered) | **catalyst** | +0.119 [+0.02, +0.23] | 0.074 | 0.114 | w -0.043, c +0.005, i +0.026, c +0.012 | +0.10 |
| forced erasure (CF) | 321 (powered) | **field** | +0.020 [-0.29, +0.77] | 0.228 | 0.030 | w +0.070, c +0.006, i +0.004, c -0.080 | +0.23 |
| voluntary erasure (CV) | 66 (powered) | **neither** | -0.209 [-0.48, +0.74] | 0.119 | 0.169 | w +0.036, c +0.002, i +0.007, c -0.044 | +0.13 |
| CF, no-consolidate chain (A2) | 321 (powered) | **field** | -0.108 [-0.24, +0.14] | 0.463 | 0.010 | w +0.142, c -0.012, i -0.130 | +0.28 |
| CV, no-consolidate chain (A2) | 66 (powered) | **neither** | -0.162 [-0.36, +0.19] | 0.198 | 0.149 | w +0.084, c +0.015, i -0.099 | +0.05 |

Forced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = +0.017, +0.020, +0.032, +0.009, +0.006, -0.085; K = +0.248.

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| @-mentions | 33 | +0.46 (p 0.010) | +0.047 [-0.09, +0.29] (p 0.485) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗; P4 erasure: browse up, type+shell down, |K_B4| < 0.10: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G40/results.json`. Rule unchanged: P3 @-mentions ✗; P4 erasure ✗ → **failed**. V4 nudges: n 5, K -0.158, Δπ_wait -0.111.
