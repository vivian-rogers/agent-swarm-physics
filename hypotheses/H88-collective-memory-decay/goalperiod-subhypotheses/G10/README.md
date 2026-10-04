# H88 × G10: the afterlife of goal period #10 (2025-08-18 → 2025-08-22)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime I · items: 1 artifacts, 11 terms · follow-up 120 village days after 2025-08-22 (held-out days censored). Channels eligible: .

## Why this period
NE27: GPT-5, Grok 4 and Claude Opus 4.1 join the four veterans on 2025-08-18 with empty memories. From that day both groups can use the items of #2–#8; only the veterans were there.

## Prediction
*Written 2026-10-04 21:04 UTC, before running (native N2).*
- **Why native:** NE27: GPT-5, Grok 4 and Claude Opus 4.1 join the four veterans on 2025-08-18 with empty memories. From that day both groups can use the items of #2–#8; only the veterans were there.
- **N2 prediction:** over 08-18 → 09-19 (non-holdout), the newcomers' standardized ratio R (observed uses / uses expected at the veterans' share on the same day, same source period) is < 1 for items whose source period ended ≤ 15 village days earlier (CI < 1), and R rises with item age: R(> 40 days) > R(≤ 15 days).
- *Counts against:* R(≤ 15) ≥ 1, or R falling with age (newcomers learn recent items as fast as veterans remember them).

## Result
*Run 2026-10-04 21:09 UTC (`analysis/replication.py`, `analysis/natives.py`) → `data/processed/H88-collective-memory-decay/replication/replication.json`, `natives/natives.json`.*

- **Artifacts (veterans):** not eligible (design) or fewer than 50 post-period veteran uses.
- **Terms (veterans):** not eligible (design) or fewer than 50 post-period veteran uses.
- **Templated verdict:** n/a (terms channel).

**N2 (NE27: three newcomers vs four veterans, 2025-08-18 → 09-19; shares within the pool of #2–#8 items).**

| Item age (village days since its period ended) | R terms [day-bootstrap CI] |
| --- | --- |
| <=15 | 0.98 [0.00, 2.68] |
| 16-40 | 0.65 [0.23, 1.36] |
| >40 | 1.02 [0.98, 1.07] |

- Uses: newcomers 462, veterans 551 (terms); artifacts 32 / 20 (too few).
- **Verdict: mixed.** The newcomers use the most recent period's (#8) terms at the veterans' rate (R 0.98, CI 0.0–2.7: uninformative), not below it. R does not rise clearly with age (0.98 → 0.65 → 1.02). Within weeks the newcomers carry the old terms as much as the veterans who coined them. Design note: the share is taken within the pool of #2–#8 items for both groups (the card's offset was all uses of the kind); this was fixed before the run.

## Scorecard (period-specific axes)
- E: 0 (no newcomer deficit for recent items; CI uninformative).
