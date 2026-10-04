# H83 × G10: newcomers joining goal period #10 (2025-08-18 → 2025-08-22)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime I · up to 7 agents · units 10a, 10b · non-holdout days 5. Joins: Claude Opus 4.1 (2025-08-18), GPT-5 (2025-08-18), Grok 4 (2025-08-18).

## Why this period
NE27 is the only join that coincides with a goal start: GPT-5, Grok 4 and Claude Opus 4.1 join the four veterans on 2025-08-18, the first day of #10, so all seven agents get the same kickoff the same day.

## Prediction
*Written 2026-10-04 20:34 UTC, before running on this period (Amendment A1.4).*
- **Why native:** NE27 is the only join that coincides with a goal start: GPT-5, Grok 4 and Claude Opus 4.1 join the four veterans on 2025-08-18, the first day of #10, so all seven agents get the same kickoff the same day.
- **N3 prediction:** the batch's window-E gap (tenure days 2–4, veterans' same-day centroid, kickoff span projected out) is negative, Ḡ_E < 0, with a day-bootstrap 95% CI below 0: the veterans carry a component beyond the shared kickoff that the newcomers lack. The batch's mean ΔG > 0 (they close part of it by days 8–14).
- *Counts against:* Ḡ_E ≥ 0 (with the same kickoff, the newcomers align with the village as well as the veterans do). Synthetic null SD of the batch gap: 0.036, so only a gap beyond about −0.06 can show.
- The three joins also enter the card-level replication.

## Result
*Run 2026-10-04 20:36 UTC (`analysis/replication.py`, `analysis/natives.py`) → `data/processed/H83-enculturation-of-newcomers/replication/replication.json`, `natives/natives.json`.*

| Join | Ḡ_E | ΔG (bge) | ΔG (gte) | ΔK | ΔS (style) | veteran items read, days 1–7 | templated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.1 | +0.114 | -0.080 | -0.022 | +0.009 | +3.571 | 1119 | failed |
| GPT-5 | -0.009 | -0.126 | -0.173 | +0.007 | +5.186 | 1118 | failed |
| Grok 4 | -0.155 | +0.097 | -0.022 | – | +4.088 | 1085 | supported |

**N3 (NE27, kickoff-matched start).**

| Statistic | bge | gte | Null (synthetic) |
| --- | --- | --- | --- |
| Batch gap Ḡ_E (days 2025-08-19, 2025-08-20, 2025-08-21) | -0.017 [-0.103, +0.066] | +0.013 [-0.030, +0.052] | SD 0.036 |
| Batch mean ΔG | -0.037 | (card replication) | SD 0.04 |

- **Verdict: mixed (inconclusive by the A1.4 rule).** The bge gap is negative but its CI spans 0; the gte gap is positive (the prediction's "against" side). The batch's ΔG is negative (Opus 4.1 −0.08, GPT-5 −0.13, Grok 4 +0.10). With the same kickoff on the same day, the newcomers align with the four veterans about as well as the veterans align with each other.

## Scorecard (period-specific axes)
- E (interventional): 0. The only kickoff-matched join shows no veteran-only component beyond the kickoff, at power ≈ 0.3.
