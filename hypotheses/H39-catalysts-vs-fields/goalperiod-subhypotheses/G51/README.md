# H39 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** mixed
**Verdict (1b):** mixed (r1 mixed); nudge K +0.16 (n 242)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode I/K · 1192 agent-days on 45 non-holdout days (2026-07-06 → 2026-09-04) · 565,242 agent-minutes on the trimmed grid.

## Why this period
Point levers (matched windows) on B4/B6 behavior states and content drift. Nudger on: nudge episodes available. Regime III: forced context erasures (NE41) available. Many human messages (public chat era / #51).

## Prediction
*Written 2026-10-04 (UTC), before running on this period.* The card's predictions (P1–P4, P7) as they apply here; a class is scored only if powered (≥ 20 episodes), otherwise reported as descriptive.
- **Per-unit class rule** (with Amendment A1, made after the synthetic validation and before any real data): field = placebo p_F < 0.05 and φ_exc ≥ 0.10; catalyst = K bootstrap CI excluding 0 and |K| ≥ 0.10.
- **Nudges (N_tgt), P1:** both: Δπ_idle < 0 and idle escape up (ln e^K_idle/e^C_idle > 0); K > 0. Against: π unchanged with K > 0 (pure catalyst, HH52) or K ≈ 0 (pure field).
- **Human messages (H_any; H_men, H_und reported), P2:** both, with the field toward chat (Δπ_chat > 0); H_men ≥ H_und in |Δπ_chat|. Content: drift toward the message > 0. Low power expected outside G04–G06 and G51.
- **@-mentions (A_men), P3:** field toward chat (Δπ_chat > 0), |K| < 0.2; content drift toward the message > 0.
- **Context erasure (NE41: CF forced, CV voluntary), P4:** on B6 Δπ_browse > 0 and Δπ_type+shell < 0; |K| < 0.10 on B4; CF and CV the same class.
- **Period verdict:** supported if every powered class matches its predicted class and direction; failed if none does; mixed otherwise; descriptive if no class is powered.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G51`; numbers in `data/processed/H39-catalysts-vs-fields/G51/results.json`. Window W = 30 min; 300 day-bootstrap resamples; 200 placebo draws. B4 occupancy of the period (work, chat, idle, consolidate): 0.38, 0.06, 0.36, 0.20.

| Lever (B4) | episodes | class (A1 rule) | K [95% CI] | φ_exc | placebo p_F | Δπ (w, c, i, c) | idle escape ln ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudges | 304 (powered) | **both** | +0.160 [+0.06, +0.25] | 0.159 | 0.005 | w +0.018, c +0.013, i -0.073, c +0.041 | +0.45 |
| human messages (any) | 407 (powered) | **neither** | -0.021 [-0.12, +0.10] | 0.000 | 0.861 | w -0.007, c -0.001, i +0.003, c +0.005 | -0.02 |
| human, mentioned | 8 (underpowered) | **neither** | +0.090 [-0.32, +0.29] | 0.000 | 0.891 | w +0.031, c +0.020, i -0.040, c -0.011 | -0.34 |
| human, unmentioned | 399 (powered) | **neither** | -0.020 [-0.12, +0.08] | 0.000 | 0.821 | w -0.001, c -0.002, i -0.003, c +0.006 | +0.01 |
| @-mentions | 3060 (powered) | **neither** | +0.002 [-0.03, +0.04] | 0.017 | 0.104 | w -0.004, c +0.005, i -0.003, c +0.002 | -0.02 |
| forced erasure (CF) | 5558 (powered) | **both** | +0.515 [+0.35, +0.68] | 0.447 | 0.005 | w +0.213, c +0.011, i +0.036, c -0.259 | +0.26 |
| voluntary erasure (CV) | 3189 (powered) | **both** | +0.647 [+0.50, +0.79] | 0.766 | 0.005 | w +0.237, c +0.026, i +0.196, c -0.459 | +0.34 |
| CF, no-consolidate chain (A2) | 5558 (powered) | **field** | -0.056 [-0.11, -0.01] | 0.516 | 0.010 | w +0.202, c +0.000, i -0.202 | +0.29 |
| CV, no-consolidate chain (A2) | 3189 (powered) | **field** | +0.081 [+0.04, +0.12] | 0.299 | 0.010 | w +0.139, c +0.013, i -0.152 | +0.33 |

Forced erasure on B6 (browse, type, shell, chat, idle, consolidate): Δπ = +0.077, +0.032, +0.094, +0.010, +0.036, -0.249; K = +0.440.

Content (O6), drift toward the kick message in SD units of the controls' drift, and diffusion (ln ratio of perpendicular squared steps):

| Lever | episodes | drift toward message | diffusion |
| --- | --- | --- | --- |
| nudges | 121 | +0.16 (p 0.109) | -0.045 [-0.17, +0.06] (p 0.228) |
| human messages (any) | 210 | +0.26 (p 0.010) | +0.015 [-0.08, +0.10] (p 0.772) |
| @-mentions | 1864 | +0.31 (p 0.010) | +0.004 [-0.03, +0.03] (p 0.693) |

**Post hoc step S20260821 (automated speaker silent from 08-21; P9).** Balanced panel of 27 agents; placebo = G51 day boundaries of the same shape.

| Window | class | K (pct) | φ pct | Δπ_idle (pct) | idle escape ln ratio (pct) |
| --- | --- | --- | --- | --- | --- |
| 2x2 days | neither | -0.049 (23) | 37 | +0.025 (66) | -0.122 (26) |
| 5x5 days | neither | -0.082 (0) | 0 | -0.005 (15) | -0.135 (10) |

P9 (neither) ✓. With the nudger off, idle escape is lower (−0.12 to −0.14, at the 26th and 10th placebo percentiles) and K is the lowest of 20 placebos in the 5 + 5 window (−0.08, below the 0.10 floor), while the idle share does not move: at swarm level the nudger's removal looks like a weak loss of catalysis, not of a field. Confounded with time in goal; post hoc.

**Scored predictions:** P1 nudges: both, idle share down, idle escape up: ✓; P2 human messages: both, chat share up: ✗; P3 @-mentions: field toward chat, |K| < 0.2: ✗; P4 erasure: browse up, type+shell down, |K_B4| < 0.10: ✗.

## Scorecard (period-specific axes)
- **C (adequacy):** 1/3 powered message levers beat the placebo-episode null on at least one component.
- **D/E:** the stationary decomposition is an unfitted statistic of matched windows; E: the 08-21 automated-speaker switch-off (post hoc, P9).

## Notes
- Matched controls use the past only and both arms are cut at the next kick (design fix from the synthetic null).
- **2026-10-04, post hoc discovery, prediction written before running it.** The automated speaker (nudges *and* the daily pause/resume bookends) is silent from **2026-08-21** on; the last nudges are on 08-20 (7 that day, ~30/day before). Not in the CHANGELOG. This is a second, non-holdout "nudger off" switch inside one goal (proposed as a new NE). **P9:** a swarm-level step at 08-21 (2 + 2 days: 08-19, 08-20 → 08-21, 08-24; and 5 + 5 days) is *neither* on B4: nudged windows cover only ~5% of agent time (≈ 1 episode per agent-day × ~22 min), so the expected idle-share change is ≈ +0.003; idle share, idle escape and K inside the G51 day-boundary placebo band. A detectable rise in the idle share would mean the nudger's aggregate effect is much larger than its per-episode effect implies (e.g. agents anticipate nudges).
- Erasure: the full B4/B6 chain mixes in the consolidation clock (consolidate is depleted right after any consolidation); the no-consolidate chain (A2) is the cleaner read.

## Round 1b (improved data, 2026-10-04)
Leading-@ nudge targets, DQ8 lever_design windows (presence-cut), Jev v3.1 states as V4. `data/processed/H39-catalysts-vs-fields/r1b/G51/results.json`. Rule unchanged: P1 nudges ✓; P2 human messages ✗; P3 @-mentions ✗; P4 erasure ✗ → **mixed**. V4 nudges: n 199, K +0.277, Δπ_wait -0.071.
