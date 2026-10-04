# H102 × G51: #general / #focus hoppers (unit 51g) (2026-08-05 → 2026-08-21)

**Verdict:** failed
**Role:** native
**Period:** regime III · 27 agents (home room 0: 5 hopper; home room 0: 20 stayer; home room 15: 2 core) · 13 non-holdout days (unit 51g only; the rest of #51 is single-room).

## Why this period
The only unit with repeated hopping: #focus opened 08-05 as a side room; two agents live there, two hop many times, four visit briefly. Private agent goals (NE26) give each agent its own field, so R-field is a live rival.

## Prediction
*Written 2026-10-04 ~20:32 UTC, before running on this period (card predictions applied).*
- Two domains: the #focus core sits away from #general stayers (D ≥ 2 with relabel p < 0.05, two core agents; descriptive).
- P2: hoppers with ≥ 5 hop-days have s(all) above the #general stayers' 95th percentile and below 1; their s(home) (statements made in #general) exceeds the stayers' median for ≥ 2/3 of them.
- P3: κ_R > 0 (p < 0.05) and κ_R > κ_U (posted-unread placebo); hopper fixed effects.
- Counts against (HH332 kill): hoppers' s(all) within the stayers' range.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout).*

| Instrument | D | relabel D p95 | p | I (stayers) | stayers on their side |
| --- | --- | --- | --- | --- | --- |
| bge style_resid | 5.50 | 1.91 | 0.006 | 0.09 | 1.00 |
| gte style_resid | 5.35 | 1.58 | 0.004 | 0.09 | 1.00 |
| bge white32 | 6.59 | 1.72 | 0.005 | 0.09 | 1.00 |
| bge dedupe | 5.43 | 2.02 | 0.005 | 0.09 | 1.00 |

Stayers: home A (room 0) 20, home B (room 15) 2. Cross-domain read share: P_hop 0.0040 (items read while in the other room), P_dom 0.0207 (items from other-domain senders). Relabel null: 1,000 draws, axis refitted.

**Hoppers** (wall coordinate s: 0 = home domain centroid, 1 = other domain). Home stayers: median 0.06, 95th percentile 0.21.

| Hopper | statements home / other room | hop-days | s(all) | s(home) | s(statements in other room) | gte s(all) |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Fable 5 | 615 / 17 | 7 | 0.06 | 0.06 | 0.15 | 0.06 |
| Gemini 3.5 Flash | 684 / 9 | 2 | 0.09 | 0.09 | 0.51 | 0.07 |
| GLM-5.2 | 1475 / 5 | 3 | 0.01 | 0.01 | 0.26 | 0.02 |
| DeepSeek-V3.2 | 2762 / 1 | 1 | 0.25 | 0.25 | 0.49 | 0.20 |
| GPT-5.5 | 282 / 2 | 2 | -0.33 | -0.33 | -0.22 | -0.09 |

**Dose–response (bge; 65 hopper-days, 5 hoppers, hopper fixed effects):** κ_R -0.014 [-0.042, 0.024] (day bootstrap), κ_U -0.006 [-0.123, 0.026]; lagged κ_R -0.004 [-0.030, 0.038]. All #general agents (324 agent-days): κ on reads from #focus-home senders -0.0010 [-0.0095, 0.0063].

**Dose–response (gte; 65 hopper-days, 5 hoppers, hopper fixed effects):** κ_R -0.015 [-0.068, 0.068] (day bootstrap), κ_U -0.011 [-0.110, 0.040]; lagged κ_R 0.021 [-0.002, 0.036]. All #general agents (324 agent-days): κ on reads from #focus-home senders 0.0048 [-0.0037, 0.0112].

**Reverse hoppers** (#focus core members' statements in #general; s from their own home, the other core member's centroid = 0, #general = 1): Gemini 2.5 Pro s(#focus statements) 0.33, s(#general statements) 0.60; Claude Opus 4.8 s(#focus statements) 0.18, s(#general statements) 0.70.


## Scorecard (period-specific axes)
- **C:** stayer distribution and posted-unread placebo; **D:** hopper wall coordinate; **F:** synthetic power on this skeleton (Amendment 1).

## Notes
- Data: `data/processed/H102-room-domain-walls/results/results.json` (key `51g`).
