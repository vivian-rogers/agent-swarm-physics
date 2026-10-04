# H52 × G51: private roles, role conflict and the bot (2026-07-06 → 2026-09-04, non-holdout part)

**Verdict:** mixed — content +0.014*, reply +0.029*; reply premium only on-role
**Role:** native
**Period:** regime III · 21–32 agents · one main room (#general; #focus 08-05 → 08-21) · 45 non-holdout active days; human messages on 22 of them (109 non-kickoff messages, 2,112 rows). Bot (automated nudges, leading @ = named) until 08-20. Twelve `period_units` (roster joins, NE32, NE38, rooms) absorbed by day fixed effects (named exception (d) on the card). The #51 tail (09-07 → 09-21) is held out.

## Why this period
Two leverage points no other period has: (1) every agent carries a private role (DQ6 `role`; `goals.parquet` agent-goal vectors), so a message can be scored as aligned with or pulling away from the recipient's plan; (2) the operator's bot is a third sender class with thousands of rows and a clean target (leading @), before it falls silent (NE43, separate folder).

## Prediction
*Written 2026-10-04 ~06:10 UTC (card, native N2 and P5), before running on this period.*
- **Replication estimator:** as the card's P1–P4 (author's expectation: content premium > 0 here; reply premium > 0; activity premium CI includes 0; stance premium > 0). H52 predicts content and activity premia equivalent to 0.
- **N2 role conflict:** split at the median of cos(message, recipient's role vector). R1 deference predicts π_con(off-role) ≥ π_con(on-role) > 0; H52 predicts both ≈ 0. Author's expectation (credence 0.4): π_con(on-role) > π_con(off-role) ≈ 0.
- **P5 bot = neither:** π_act(bot, named) > 0 (≈ 0.5–1.5 min; H30's level was computed on the buggy `activity_bins` table and is provisional), π_con(bot) ≤ 0, π_rep(bot) < 0 relative to matched agent messages. Counts against: bot content or reply premium ≥ the human premium with CI excluding 0.

## Result
In the verdict line, * marks a 95% CI that excludes 0.

**Replication estimator** (`G51/results.json`; 92 non-kickoff human messages on 22 days; day-block bootstrap; powered).

| Outcome | Human premium [95% CI] | Naive | Matched agent mean | Agent naming effect | Verdict |
| --- | --- | --- | --- | --- | --- |
| content (DiD χ) | **+0.014 [0.008, 0.021]** | +0.013 | −0.001 | −0.018 | premium (CI beyond δ_con 0.0073); H30 orthogonalized +0.018 [0.007, 0.026] (whose naming effect is +0.032, i.e. the premium ≈ half the naming effect); gte +0.011 [0.004, 0.020]; style-residualized +0.012 [0.005, 0.023]; joint +0.013 [0.006, 0.020]; clean controls +0.014; excluding uncertain rows +0.017; named human rows +0.036 [0.005, 0.080], unnamed +0.013 [0.007, 0.019] |
| reply | **+0.029 [0.008, 0.052]** | +0.026 | 0.028 | +0.320 | premium (inside δ_rep 0.064): human messages answered about twice as often as matched agent messages, a tenth of the naming effect; the candidate-rule bias against humans affects ≤ 0.9% of rows |
| activity (BC) | +0.36 [−0.07, 0.72] | +0.40 | — | −0.04 | inconclusive |
| stance | +0.08 [−0.07, 0.27] | +0.06 | 0.67 | +0.05 | inconclusive |

#51 segments (H29's five; `native/g51_segments.json`): content +0.010, +0.014, +0.015, +0.018, +0.004 (CI > 0 in 51b, 51c); pooled +0.013 [0.006, 0.020]. Reply +0.005, +0.027, +0.057, −0.025, +0.017; pooled +0.011 [−0.015, 0.037]. H29 boundary design: human − agent jump (unnamed) +0.038 [−0.096, 0.151] (few human boundary rows); agent named 0.067 vs unnamed 0.012 (5.4×, H29's ratio reproduced).

**Native N2 (role conflict)** (`native/n2_G51_roles.json`; role alignment = cos(message, recipient's private-role vector), median split at −0.03; 318k rows with a role):

| Messages | Content premium | Reply premium |
| --- | --- | --- |
| on-role (≥ median) | +0.014 [0.005, 0.022] | **+0.037 [0.013, 0.066]** |
| off-role (< median) | +0.011 [−0.003, 0.030] | +0.007 [−0.013, 0.023] |
| bottom tercile ("pulls away from the plan") | −0.000 [−0.017, 0.019] | −0.007 [−0.021, 0.010] |
| on − off | +0.003 [−0.019, 0.020] | **+0.035 [0.012, 0.062]** |

R1 deference (π_off ≥ π_on > 0) is rejected for replies; H52 (both ≈ 0) is rejected on-role. My expectation (π_on > π_off ≈ 0) holds for replies and is undecided for content. Agents answer humans more when the message fits their assigned role, and not when it pulls away from it.

**Bot (P5)** (07-06 → 08-20, 729 nudges, named = leading @): content −0.001 [−0.003, 0.002] (not interpretable: synthetic bias −0.024 for templated messages); reply (all) −0.001 [−0.005, 0.004], named −0.017 [−0.093, 0.073]; activity of the named target vs a matched named agent message −0.11 [−0.82, 0.75]; stance of replies to the bot **−0.97 [−1.15, −0.79]** relative to matched agent messages (agents mostly decline or correct the nudge; aggregate only). P5's "neither" fails: given read-out, the bot is treated like an agent message of the same salience, except that replies to it push back. (H30's nudge effect is relative to no message, not to an agent message, and was computed on the buggy `activity_bins`.)

## Scorecard (period-specific axes)
- C: content and reply premia beat the matched-agent null (day-block); placebo-class null descriptive only (anti-conservative).
- D: segment replication (content positive in 5/5 segments); H29's 5.4× naming ratio reproduced on the boundary.
- F: synthetic G51 skeleton recovers content (bias −0.006), reply, activity (BC) and stance.
- G: DQ6 roles (N2); named > unnamed for replies (+0.32).

## Notes
- 2026-10-04: scripts `analysis/run_period.py G51` and `analysis/native.py n2`.
