# H83 × G51: newcomers joining goal period #51 (2026-07-06 → 2026-09-04)

**Verdict:** n/a
**Role:** native (exploratory)
**Period:** regime III · up to 32 agents · units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l · non-holdout days 45. Joins: GPT-5.6 Sol (2026-07-09), GPT-5.6 Terra (2026-07-09), GPT-5.6 Luna (2026-07-09), Grok 4.5 (2026-07-10), Kimi K3 (2026-07-17), Claude Opus 5 (2026-07-24).

## Why this period
NE32: on 2026-07-09 GPT-5.6 Sol, Terra and Luna each start alone in an isolated onboarding room (no veteran items read; checked in the DQ1 ledger) and merge into the village on 07-10. Every other newcomer reads veterans from its first day.

## Prediction
*Written 2026-10-04 20:34 UTC, before running on this period (Amendment A1.5).*
- **Why native:** NE32: on 2026-07-09 GPT-5.6 Sol, Terra and Luna each start alone in an isolated onboarding room (no veteran items read; checked in the DQ1 ledger) and merge into the village on 07-10. Every other newcomer reads veterans from its first day.
- **N1 prediction:** d1 = the triplet's tenure-day-1 gap (statement-pooled) − the mean day-1 gap of the other newcomers < 0 (reading on the day raises alignment), and d2 = the triplet's change from day 1 to days 2–6 − the other newcomers' same change > 0 (the triplet catches up after the merge). Bootstrap over the other newcomers.
- *Counts against:* d1 ≥ 0 and d2 ≤ 0. Synthetic null SD 0.10 for both, so only large effects can show; Sol and Terra post 4 and 8 statements on 07-09.
- Caveat: #51 agents hold private roles (an agent-specific field); the own role text is projected out with the kickoff span. The #51 joins (Sol, Terra, Luna, Grok 4.5, Kimi K3, Claude Opus 5) also enter the card-level replication.

## Result
*Run 2026-10-04 20:36 UTC (`analysis/replication.py`, `analysis/natives.py`) → `data/processed/H83-enculturation-of-newcomers/replication/replication.json`, `natives/natives.json`.*

| Join | Ḡ_E | ΔG (bge) | ΔG (gte) | ΔK | ΔS (style) | veteran items read, days 1–7 | templated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.6 Sol | -0.131 | +0.248 | +0.133 | -0.050 | -1.116 | 3951 | supported |
| GPT-5.6 Terra | -0.177 | +0.165 | +0.034 | -0.027 | -1.413 | 3986 | supported |
| GPT-5.6 Luna | -0.039 | +0.054 | +0.009 | -0.009 | -1.933 | 3997 | supported |
| Grok 4.5 | +0.092 | -0.088 | -0.022 | – | +7.170 | 4667 | failed |
| Kimi K3 | -0.010 | +0.075 | -0.092 | -0.030 | -4.205 | 5179 | supported |
| Claude Opus 5 | +0.066 | -0.017 | -0.100 | +0.000 | -1.817 | 4545 | failed |

**N1 (NE32 isolated triplet): premise false.**
- The DQ1 ledger and `rooms_timeline` show that GPT-5.6 Sol, Terra and Luna left their isolated rooms (sol, terra, luna) for #general on 07-09 itself, about 1.5–2 h after joining (21:38–22:02 UTC). The rooms were deleted on 07-10. The triplet posted **no chat statement** while isolated and read 733 veteran items on 07-09.
- So "tenure day 1 without veteran reads" does not exist, and N1 has no test. The rule's numbers, for the record: d1 = -0.110 [-0.151, -0.068] (bge), -0.021 [-0.063, +0.021] (gte); d2 = +0.008 [-0.034, +0.046] (bge), -0.072 [-0.110, -0.036] (gte). The two models disagree.
- **Catalog correction (for `natural-experiments.md`):** NE32's isolation lasted about 1.5–2 h on 07-09, not until 07-10.
- H89 (coordinator note) finds the #51 newcomers' content moving toward the veterans in bge (cos +0.26) but not in gte (−0.03): the same model dependence.

## Scorecard (period-specific axes)
- E: n/a (the natural experiment did not happen as catalogued).
