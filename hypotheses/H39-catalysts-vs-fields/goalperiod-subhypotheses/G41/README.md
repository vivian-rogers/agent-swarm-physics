# H39 × G41: Perform novel research! (2026-05-11 → 2026-05-18)

**Verdict:** failed
**Verdict (1b):** failed (r1 failed); nudge K +0.47 (n 5)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode I · 75 agent-days on 5 non-holdout days (2026-05-11 → 2026-05-15) · 17,699 agent-minutes on the trimmed grid.

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
Run 2026-10-04 with `analysis/run_period.py --period G41`; numbers in `data/processed/H39-catalysts-vs-fields/G41/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.52, 0.11, 0.18, 0.18.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 7 (underpowered) | **neither** | +0.468 [-0.12, +0.86] | 0.544 | 0.075 | w +0.232, c +0.002, i -0.255, c +0.021 | +1.02 |
| human messages (any) | 14 (underpowered) | **neither** | +0.036 [-0.84, +0.10] | 0.167 | 0.144 | w +0.022, c -0.017, i +0.037, c -0.042 | +0.20 |
| human, mentioned | 2 | too few | | | | | |
| human, unmentioned | 12 (underpowered) | **neither** | +0.154 [-0.84, +0.20] | 0.000 | 0.532 | w -0.040, c -0.004, i +0.060, c -0.016 | +0.38 |
| @-mentions | 110 (powered) | **neither** | -0.035 [-0.18, +0.13] | 0.046 | 0.313 | w -0.020, c -0.009, i +0.027, c +0.003 | -0.02 |
| forced erasure (CF) | 181 (powered) | **field** | +0.450 [-0.12, +0.60] | 0.599 | 0.005 | w +0.321, c +0.030, i +0.039, c -0.390 | +0.10 |
| voluntary erasure (CV) | 39 (powered) | **neither** | +0.262 [-0.01, +0.63] | 0.536 | 0.159 | w +0.238, c +0.074, i -0.042, c -0.271 | +0.83 |
| CF, no-consolidate chain (A2) | 181 (powered) | **both** | -0.167 [-0.21, -0.10] | 0.244 | 0.010 | w +0.073, c +0.008, i -0.080 | +0.06 |
| CV, no-consolidate chain (A2) | 39 (powered) | **field** | +0.215 [-0.13, +0.74] | 0.771 | 0.010 | w +0.179, c +0.103, i -0.283 | +0.75 |

Forced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = +0.058, +0.082, +0.181, +0.033, +0.040, -0.395; K = +0.530.

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| @-mentions | 7 | +0.69 (p 0.030) | -0.237 [-0.75, +0.06] (p 0.495) |

**Scored predictions:** P3 @-mentions: field toward chat, |K| < 0.2: ✗; P4 erasure: browse up, type+shell down, |K_B4| < 0.10: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 0/1 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G41/results.json`. Rule unchanged: P3 @-mentions ✗; P4 erasure ✗ → **failed**. V4 nudges: n 7, K +0.715, Δπ_wait -0.140.
