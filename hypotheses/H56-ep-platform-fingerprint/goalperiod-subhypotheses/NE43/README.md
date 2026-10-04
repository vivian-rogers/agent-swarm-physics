# H56 × NE43: the automated speaker goes silent (2026-08-21, inside #51)

**Verdict:** descriptive
**Role:** native (exploratory, round 1, non-holdout)
**Period:** goal #51, regime III, 25–27 agents. Day 0 = Friday 2026-08-21 (first day without nudges). Confound: the #focus room closes on Monday 08-24 (structural room change).

## Why this period
An undocumented operator change: a withdrawn drive (the nudger) rather than a tool, prompt or harness change. H56 says EP should not move here; a drive-removal reading of stochastic thermodynamics says the sector the nudger acted on (idle) should become less irreversible.

## Prediction
*Written 2026-10-04 06:00 UTC (card P7), before any real-data EP.* H56: no jump on V1 or V2 (|t| below the Friday-placebo 95th percentile; p > 0.05) [0.6]. Competing drive reading (low credence): the idle-sector EP (Newton on indicator pairs involving idle, agent-only chain) falls after 08-21 relative to Friday placebos [0.3]. Null: the same statistic, with the same window shape, on every other Friday of #51 whose windows stay inside #51 (6–8 Fridays).

## Result
**Data facts (from `kicks_classified`, before EP):** the last nudge is on 08-20 (729 nudges in #51 before that), but the last daily pause/resume bookend is on **08-04**, not 08-20. NE43's two components are two and a half weeks apart; the catalog entry should be corrected.

| design | chain | agents | Δ̄ | relative | t | p (Fridays) | idle sector: relative, t, p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3 + 3 days (08-18..20 vs 08-21, 24, 25) | V1 | 27 | −0.022 | −22% | −1.55 | 0.38 (n 7) | −76%, −1.34, 0.25 |
| 3 + 3 days | V5 | 25 | −0.017 | −19% | −1.01 | 0.38 | −95%, −1.22, 0.25 |
| 3 days vs Friday only | V1 | 26 | −0.003 | −3% | −0.20 | 0.89 (n 8) | −50%, −0.55, 0.44 |
| 5 + 5 days (08-14..20 vs 08-21..27) | V1 | 27 | −0.015 | −14% | −1.08 | 0.43 (n 6) | −56%, −0.98, 0.71 |

- No jump in any design: P7's H56 part holds. The idle sector falls in point estimate in every design, but never beyond the Friday placebos: the drive reading is not supported.
- **Not diagnostic.** EP also failed to jump at scaffold changes (card, P1), so "no jump here" does not separate operator from platform changes. The Friday pool is small: with 6–8 placebos the smallest attainable p is 0.11–0.14, so no design could reach p < 0.05.

Figure: `figures/ne43_placebo.pdf`. Data: `data/processed/H56-ep-platform-fingerprint/native/NE43.json`.

## Scorecard (period-specific axes)
- **E (interventional):** 0 (null result, no discriminating power).
- **G (ground truth):** the automated speaker's timeline is directly visible in `kicks_classified`; the bookends end on 08-04.

## Notes
- Suggested shared-file change: `hypotheses/natural-experiments.md` NE43 and `infra/README.md` Known issues should say that the daily bookends end after 08-04 and the nudges after 08-20; `period_units` does not split #51 at either date.
