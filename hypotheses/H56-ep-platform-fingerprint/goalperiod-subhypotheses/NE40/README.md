# H56 × NE40: the undocumented history-search answerer swap (dated here to 2026-04-20)

**Verdict:** failed
**Role:** native (exploratory, round 1, non-holdout)
**Period:** non-holdout history-search events 2025-09 → 2026-09-04 (7,759 answers) for the dating; the EP test at the dated day sits in goal #38 (regime III, 12–14 agents).

## Why this period
NE40 (Gemini 2.5 Pro → Sonnet 4.6 as the answerer of `search_history`) is undocumented and undated: the ideal test of "EP as a log-only detector of changes the operator did not document". It needs an independent date first.

## Prediction
*Written 2026-10-04 06:00 UTC (card P9), before any real-data EP.* Non-text answer features (length, line count, markdown) show one dominant break in non-holdout data, dating the swap [0.6]. If dated, EP |t| at that day is a hit on V1 [0.2]; the search-sector EP (indicator pairs involving `search`, V1) changes across it [0.35].

## Result
- **Pre-registered dating (answer length, lines, markdown counts):** one dominant joint break (two-segment fit on daily medians, permutation p = 0.0035), first day after it **03-25/26** (bootstrap mode 03-26 in 163/200 resamples). It coincides with NE14b and NE16: the search event's own logging changes there too (input tokens logged as 0 before 03-24, about 25k after), so it cannot be attributed to the answerer. P9's dating step fails as posed.
- **Post hoc dating (Amendment 4, stylometric counts, numbers only):** answers with Gemini-style `*   ` bullets appear on 55 of 61 days with ≥ 3 searches up to **Friday 04-17** and on 0 of 68 days from **Monday 04-20**; `- ` bullets go from 0.4% to 25% of answers and em dashes from 45% to 85% (joint split p = 0.0005). The swap shipped on **2026-04-20, the same day as the documented NE18 search rework** (verbatim segments, 10-day window), which does not mention the model change.
- **EP at 04-20:** V1 t = −0.18 (Δ̄ −0.006, −5%; p 0.86 against the Amendment-3 null), V5 t = −0.60 (p 0.70). The search sector is untestable: only 4 agents have search transitions on both sides of the window. EP does not see the oracle swap, or the NE18 change it shipped with.
- Side findings from the same scan: answers collapse to a median of 42–383 characters on 03-31 and 04-01, with 85–98 searches a day (a search malfunction that agents retried), and the tool's date fields change from integer `startDay`/`endDay` to string `startDate`/`endDate` on **07-29** (undocumented; see G51).

Figure: `figures/ne40_stylometry.pdf`. Data: `data/processed/H56-ep-platform-fingerprint/native/NE40.json`, `ne40_search_features.parquet` (numbers only).

## Scorecard (period-specific axes)
- **G (ground truth):** an independent, log-only date for NE40 now exists (04-20), from the tool's output style, not from EP.
- **E (interventional):** 0. EP shows nothing at the dated change.

## Notes
- Suggested catalog update: NE40 dated 2026-04-20, deployed with NE18 (evidence: stylometric markers of the answers; Gemini-style bullets end on 04-17).
- Answer stylometry is a far better undocumented-change detector than behavioral EP for anything that changes a tool's output.
- **2026-10-04, ep_newton recheck (post hoc).** Held-out Newton bound. EP at 04-20: t −0.56, p 0.60 (was −0.19, p 0.83); search sector t 0.79, p 0.56. The stylometric dating does not use EP and is unchanged. The verdict stays **failed**.
