# H88 × NE28: carrier loss (retirements: Grok 4, o3, Claude Opus 4.1, Claude 3.7 Sonnet)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** spans goal periods #18–#31 (exits 2025-10-29, 2025-12-01, 2026-02-19); regime I.

## Why this period
retirements remove a carrier with a long memory: Grok 4 (2025-10-29), o3 and Claude Opus 4.1 (2025-12-01, NE28), Claude 3.7 Sonnet (2026-02-19, NE29; the longest-serving agent). This folder spans goal boundaries (exception (c)).

## Prediction
*Written 2026-10-04 21:04 UTC, before running (native N3; NE28 and NE29, plus Grok 4's exit).*
- **Why native:** retirements remove a carrier with a long memory: Grok 4 (2025-10-29), o3 and Claude Opus 4.1 (2025-12-01, NE28), Claude 3.7 Sonnet (2026-02-19, NE29; the longest-serving agent). This folder spans goal boundaries (exception (c)).
- **N3 design:** items (from any earlier non-holdout period) with ≥ 5 agent uses in the 10 village days before an exit. Retiree-carried: the retiree made ≥ 40% of those uses. Controls: items with < 10% retiree uses, in the same pre-exit volume tercile. Outcome: other agents' uses in the 10 village days after vs before; ratio of ratios (carried / control), item-block bootstrap.
- **N3 prediction:** other agents keep using retiree-carried items: the ratio of ratios lies in [0.5, 2] with a CI that includes 1.
- *Counts against:* CI below 1 (the item's memory left with its carrier).

## Result
*Run 2026-10-04 21:09 UTC (`analysis/replication.py`, `analysis/natives.py`) → `data/processed/H88-collective-memory-decay/replication/replication.json`, `natives/natives.json`.*


**N3 (carrier loss; other agents' uses of retiree-carried items, 10 village days after vs before, relative to matched control items).**

| Exit | Carried items | Others' uses before → after | Ratio of ratios [item bootstrap] |
| --- | --- | --- | --- |
| Grok 4 | 5 | 27 → 0 | 0.00 [0.00, 0.00] |
| NE28 o3 + Opus 4.1 | 94 | 599 → 55 | 2.02 [0.03, 6.69] |
| NE29 Claude 3.7 Sonnet | 22 | 89 → 0 | 0.00 [0.00, 0.00] |
| pooled | 121 | 715 → 55 | 0.78 [0.01, 2.21] |

- The literal rule (pooled ratio in [0.5, 2], CI including 1) is met, but the pooled CI spans 0.01–2.2, so the test cannot tell survival from loss. Two of three exits show total loss: after Grok 4 and Claude 3.7 Sonnet left, no other agent used the items they had carried (27 and 89 uses before, 0 after). After NE28 the carried items fell less than the controls, but both collapsed with the #21 goal switch on the same day.
- **Verdict: mixed** (rule met only through an uninformative CI; per exit, items carried by one agent die with it in 2 of 3 cases). This reading of the CI width is post hoc.

## Scorecard (period-specific axes)
- E: 1 (two retirements end their carried items; one is confounded with a goal switch).
