# H72 × G51g: the #focus room as an input-poor room (2026-08-05 → 08-24)

**Verdict:** failed
**Role:** native
**Prediction outcome (dated, written against H72):** (a) failed, (b) held. The verdict line scores H72's claim: the room's escape difference does not run through starvation.
**Period:** regime III · #51 unit 51g (#focus opens 08-05; window to 08-24 when the room empties) · 5 agents with gates in both #focus and #general · 2412 gates (1625 in #focus).

## Why this period
Cross-room reads fall 95% when #focus opens (RE-R1, H58), so the same agent sees less input in #focus. If starvation sets escape, the room difference in escape should run through s.

## Prediction
*Written 2026-10-04, before running (card, N3).*
(a) median s_novel in #focus ≥ 2× #general [0.7]; (b) the #focus coefficient moves by < 30% of itself (or < 0.1 logit) when the s clocks are added [0.5]. Low power: 5 agents.

## Result
`analysis/native.py`; numbers in `data/processed/H72-trap-aging-input-starvation/native/native.json` (B = 200).

| Quantity | Estimate [95% CI] | Prediction |
| --- | --- | --- |
| median s_novel #focus / #general (min) | 4.0 / 2.3 (×1.76) | (a) fail |
| β_#focus without s | +0.89 [+0.06, +1.64] | |
| β_#focus with s | +0.84 [+0.09, +1.60] | |
| change | -0.05 [-0.12, +0.09] | (b) pass |

