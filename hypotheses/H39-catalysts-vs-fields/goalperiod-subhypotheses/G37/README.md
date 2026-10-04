# H39 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed); nudge K +0.39 (n 6)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode F · 36 agent-days on 3 non-holdout days (2026-03-30 → 2026-04-01) · 8,502 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G37`; numbers in `data/processed/H39-catalysts-vs-fields/G37/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.49, 0.08, 0.21, 0.22.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 9 (underpowered) | **both** | +0.264 [+0.17, +1.21] | 1.130 | 0.005 | w +0.174, c +0.008, i -0.411, c +0.228 | +0.96 |
| human messages (any) | 0 | too few | | | | | |
| human, mentioned | 0 | too few | | | | | |
| human, unmentioned | 0 | too few | | | | | |
| @-mentions | 62 (powered) | **neither** | +0.086 [+0.07, +0.23] | 0.000 | 0.955 | w +0.003, c +0.001, i +0.006, c -0.010 | +0.11 |
| forced erasure (CF) | 144 (powered) | **field** | +1.549 [-0.12, +2.19] | 0.323 | 0.005 | w +0.233, c +0.013, i +0.031, c -0.276 | +0.13 |
| voluntary erasure (CV) | 33 (powered) | **both** | +0.736 [+0.30, +0.93] | 0.794 | 0.005 | w +0.169, c +0.104, i +0.121, c -0.394 | +0.38 |
| CF, no-consolidate chain (A2) | 144 (powered) | **neither** | -0.053 [-0.06, +0.03] | 0.000 | 0.653 | w +0.023, c -0.015, i -0.008 | +0.23 |
| CV, no-consolidate chain (A2) | 33 (powered) | **field** | +0.044 [-0.32, +0.44] | 0.384 | 0.050 | w +0.098, c +0.106, i -0.204 | +0.39 |

Forced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = +0.164, +0.032, +0.027, +0.011, +0.022, -0.257; K = +0.801.

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| @-mentions | 13 | +0.49 (p 0.020) | -0.053 [-0.47, +0.15] (p 0.554) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗; P4 erasure: browse up, type+shell down, |K_B4| < 0.10: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 0/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G37/results.json`. Rule unchanged: P3 @-mentions ✗; P4 erasure ✗ → **failed**. V4 nudges: n 5, K +0.370, Δπ_wait -0.006.
