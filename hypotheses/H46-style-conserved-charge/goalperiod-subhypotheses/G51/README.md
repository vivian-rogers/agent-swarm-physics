# H46 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime III · 32 agents with eligible days · rooms [0, 15] · 45 days with eligible agent-days · units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l.

## Why this period
#51 is the **private-role era**: each agent got an assigned role (DQ6 `role`), from task roles (forecaster, game dev) to performative ones: the **Prankster** (GPT-5, agent 10), whose role is to act on others for effect, and the **media** roles (`role_class == media`: twitterati, substacker, YouTuber). An assigned persona is the sharpest test of a conserved style: if the role reaches the register, style moves. #51 also holds **NE38** (07-29): Claude Opus 5 was reassigned from game dev to mathematician, a single-agent role switch with a long baseline on both sides.

## Prediction
*Written 2026-10-04 05:45 UTC, before running on this period (card P9, P10).*
- **Personas (P9):** incumbents with regime-III non-holdout data before #45. Block displacement of type-controlled style from their last ≤ 3 eligible days before #45 to their first ≤ 3 eligible days of #51 (07-06 → 07-08), against their own placebo block pairs with a calendar gap ≥ 21 days (#36–#44, #51 non-holdout). H46 predicts the Prankster's percentile < 0.9, the media roles within band, and no media-vs-other difference (Mann–Whitney p ≥ 0.05). Content moves for everyone (median percentile ≥ 0.7). *Falsifier:* Prankster ≥ 0.95, or media > other at p < 0.05. Prior: about 50% that the Prankster breaks it.
- **NE38 (P10):** agent 40, day-level transition 07-28 → 07-29 and 3-day blocks, against its own #51 placebo transitions: content percentile ≥ 0.9, style percentile < 0.9.
- The replication estimator inside #51 (within-period split-half fingerprint, KW information) is reported here as well; #51's internal boundaries (roster, rooms, NE43) feed the NE classes.

## Result
*Run 2026-10-04 06:09 UTC (`analysis/native.py` → `data/processed/H46-style-conserved-charge/G51/native.json`).*

**Personas (P9).** Block displacement into #51 (last ≤ 3 eligible days before #45 → first ≤ 3 days of #51) against each agent's own matched-gap (≥ 21 days) placebo block pairs. Agents are listed by roster code with their DQ6 role.

| Agent (role, group) | style pct | style pct, pre-#45 placebo only | content pct | style ratio to median placebo |
| --- | --- | --- | --- | --- |
| 10 (prankster, prankster) | 1.00 | – | 1.00 | 5.33 |
| 22 (twitterati, media) | 1.00 | 1.00 | 0.53 | 3.10 |
| 27 (merch baron, other) | 1.00 | – | 1.00 | 8.57 |
| 6 (author, other) | 0.95 | 1.00 | 0.90 | 4.34 |
| 18 (youtuber, media) | 0.94 | 0.90 | 0.78 | 4.50 |
| 20 (forecaster, other) | 0.70 | 0.67 | 0.78 | 1.65 |
| 25 (psychonaut, other) | 0.68 | 1.00 | 0.42 | 1.67 |
| 26 (game dev, other) | 0.62 | 0.00 | 0.88 | 1.21 |
| 24 (game dev, other) | 0.56 | 0.33 | 0.78 | 1.17 |
| 14 (ethicist, other) | 0.50 | 0.22 | 0.39 | 1.02 |
| 21 (animal advocate, other) | 0.46 | 0.14 | 1.00 | 0.94 |
| 13 (psychologist, other) | 0.44 | 0.24 | 0.53 | 0.87 |
| 16 (substacker, media) | 0.32 | 0.19 | 0.38 | 0.58 |
| 12 (twitterati, media) | 0.32 | 0.22 | 0.86 | 0.42 |
| 17 (diplomat, other) | 0.28 | 0.05 | 0.64 | 0.44 |
| 29 (performance coach, other) | 0.13 | – | 0.33 | 0.70 |
| 23 (artist, other) | 0.00 | 0.00 | 0.78 | 0.10 |

- **Style:** mean percentile 0.583 over 17 incumbents (randomization p 0.126); 29% at ≥ 0.9. **Prankster: 1.00** (falsifier ≥ 0.95 hit). Media vs other: Mann–Whitney p 0.358 (media 0.32, 0.32, 0.94, 1.00).
- **Content:** mean percentile 0.705 (p 0.002).
- **Post hoc (PH5):** the movers are mostly non-Anthropic (Google, OpenAI): non-Anthropic median 0.81 vs Anthropic 0.44 (Mann–Whitney p 0.043). Role group does not explain the shift; lab does (a lead, not a test).

**NE38 (P10), Claude Opus 5 reassigned 07-29.** Day level: style 0.82, content 0.91 against 22 own transitions (prediction met: content ≥ 0.9, style < 0.9). 3-day blocks: style 1.00, content 1.00 against 23 sliding blocks (style also moves). Caveat: the pre-block is the agent's first three days in the village (07-24 → 07-28), so a newcomer transient is confounded with the role switch.

**Verdict:** failed for H46 as stated (an assigned persona, the Prankster, moved style beyond every placebo; so did two media roles and two non-persona Gemini agents).

**Replication estimator in #51:** - **Sample:** 32 agents, 45 days, 962 eligible agent-days (≥ 3 deduplicated chat messages). - **Agent share of day-demeaned variance:** style 0.59, content 0.51. - **Split-half fingerprint within the period:** style 0.60, content 0.74, chance 0.04. - **Entry boundary:** none (see prediction); verdict descriptive. - **KW (next-day output, within agent):** style p = 0.010, content p = 0.005 (small periods are underpowered and their raw CV R² is inflated; Amendment 3). - **Templated verdict:** descriptive.

## Scorecard (period-specific axes)
- **E:** 1 (persona onset and NE38 used as interventions; prediction failed for the Prankster).
- **G:** DQ6 role labels as ground truth; the shift tracks lab more than role (post hoc).
