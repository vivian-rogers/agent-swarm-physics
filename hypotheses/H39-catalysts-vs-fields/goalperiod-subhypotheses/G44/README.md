# H39 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** mixed
**Verdict (1b):** failed (r1 mixed); nudge K +0.10 (n 9)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode C · 65 agent-days on 4 non-holdout days (2026-05-26 → 2026-05-29) · 14,992 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift. Nudger on: nudge episodes available. Regime III: forced context erasures (NE41) available. Contains the unnumbered CHANGELOG step S20260528 (2026-05-28).

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges (N_tgt), P1:** both: Δπ_idle < 0 and idle escape up (ln e^K_idle/e^C_idle > 0); K > 0. Against: π unchanged with K > 0 (pure catalyst, HH52) or K ≈ 0 (pure field).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Context erasure (NE41: CF forced, CV voluntary), P4:** on B6 Δπ_browse > 0 and Δπ_type+shell < 0; |K| < 0.10 on B4; CF and CV the same class.
- **Scaffold step S20260528 (2026-05-28; prompt: keep messages short (text-only models); first-person # bash comments (style)), P7:** neither on behavior; a content (C6) field if anything. Judged against within-goal day-boundary placebos of the same era.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G44`; numbers in `data/processed/H39-catalysts-vs-fields/G44/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.49, 0.11, 0.21, 0.19.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 10 (underpowered) | **neither** | +0.058 [-0.04, +0.36] | 0.307 | 0.149 | w -0.025, c -0.045, i +0.096, c -0.026 | -0.15 |
| human messages (any) | 21 (powered) | **neither** | +0.196 [-0.01, +0.38] | 0.223 | 0.100 | w +0.081, c +0.002, i -0.008, c -0.074 | +0.13 |
| human, mentioned | 3 (underpowered) | **catalyst** | +0.242 [+0.24, +0.33] | 0.339 | 0.224 | w +0.202, c -0.001, i -0.129, c -0.072 | +0.61 |
| human, unmentioned | 18 (underpowered) | **neither** | +0.054 [-0.01, +0.19] | 0.226 | 0.124 | w +0.098, c -0.009, i -0.014, c -0.074 | -0.16 |
| @-mentions | 69 (powered) | **field** | +0.050 [-0.10, +0.22] | 0.190 | 0.045 | w +0.043, c +0.013, i -0.075, c +0.019 | +0.17 |
| forced erasure (CF) | 124 (powered) | **field** | +0.594 [-0.12, +1.64] | 0.618 | 0.005 | w +0.333, c +0.012, i +0.060, c -0.406 | +0.28 |
| voluntary erasure (CV) | 42 (powered) | **both** | +0.861 [+0.03, +1.80] | 0.775 | 0.010 | w +0.272, c +0.075, i +0.151, c -0.498 | -0.08 |
| CF, no-consolidate chain (A2) | 124 (powered) | **field** | +0.054 [-0.12, +0.45] | 0.416 | 0.010 | w +0.167, c -0.003, i -0.164 | +0.44 |
| CV, no-consolidate chain (A2) | 42 (powered) | **neither** | -0.150 [-0.49, +0.24] | 0.000 | 0.990 | w +0.010, c +0.001, i -0.011 | -0.15 |

Forced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = +0.132, +0.102, +0.107, +0.027, +0.103, -0.471; K = +1.550.

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| nudges | 6 | +1.03 (p 0.010) | +0.112 [-0.39, +0.56] (p 0.059) |
| @-mentions | 7 | +0.29 (p 0.337) | +0.248 [-0.03, +0.50] (p 0.228) |

**Step S20260528** (prompt: keep messages short (text-only); first-person # bash comments; pre 2026-05-26, 2026-05-27 → post 2026-05-28, 2026-05-29; 15 agents in the balanced panel; placebo pool: era III-4h, n = 12).

| State family | class | φ (percentile in placebo) | K (percentile) | Δπ |
| --- | --- | --- | --- | --- |
| behavior B4 | **neither** | 0.108 (58) | +0.011 (67) | work -0.054, chat +0.009, idle +0.021, consolidate +0.024 |
| content C6 | **neither** | 1.183 (83) | +0.468 (75) | (clusters) |

**Scored predictions:** P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✓; P4 erasure: browse up, type+shell down, |K_B4| < 0.10: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/2 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; no natural experiment inside the period except the scaffold step below.

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G44/results.json`. Rule unchanged: P2 human messages ✗; P3 @-mentions ✗; P4 erasure ✗ → **failed**. V4 nudges: n 7, K +0.272, Δπ_wait -0.098.
