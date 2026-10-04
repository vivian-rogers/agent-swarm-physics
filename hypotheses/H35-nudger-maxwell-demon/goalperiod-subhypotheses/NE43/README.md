# H35 × NE43: the `automated` speaker goes silent inside #51 (last nudge 2026-08-20)

**Verdict:** mixed
**Role:** exploratory (natural experiment, non-holdout)
**Period:** regime III · #51 · before = 2026-07-06 → 08-19 (nudger on, 33 days, ~20 nudges/day); after = 08-21 → 09-02 (9 days, no automated messages; NE33's batch join on 09-03 excluded); 08-20 (transition day) dropped. Data: `data/processed/H35-nudger-maxwell-demon/G51/`, `G51off/`.

## Why this period
H35 found this step in its structural check before any analysis: no CHANGELOG entry, 5 nudges on 08-20, then none. NE43 in the shared catalog was added in parallel. It is the only nudger-off step outside the holdout in the short-pause scaffold. Data note: the daily pause/resume bookends had already stopped on **08-05**, not 08-21 as the catalog row says. On 08-20 itself 18 human messages appear (unusual).

## Prediction
*Written 2026-10-03 in the card and in `../G51/README.md` (P6), before any analysis; copied here verbatim.*
- **P6 (off-step, 08-21 → 09-02):** (a) nudges buy ≤ 1% of active agent-minutes, so the active-fraction change after 08-20 is within 2 day-SDs; (b) gate DiD (trigger region vs below, after − before) < 0, with size near the accounting prediction (sign only; low power).

## Result
| Quantity | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| nudges per day before | 19.9 | | |
| nudge-attributable share of active agent-minutes (per-nudge A30 1.45 × rate) | 0.50% | ≤ 1% predicted | (a) supported |
| active fraction before → after | 47.5% → 46.1%; change -1.4 pp [-4.8, +2.0] | predicted -0.24 pp; placebo split (last 9 days before vs rest) -2.9 pp; day SD 8.2 pp | (a) supported: invisible |
| trigger region (from the before period) | chain-age bins k 4–9 and ≥ 10 (nudge rate per gate 0.051 vs 0.012 below) | | |
| gate escape, trigger region vs below | before 0.145 / 0.437; after 0.136 / 0.478 | | |
| DiD (after − before, trigger − below) | -0.050 [-0.099, -0.005] | predicted -0.005; placebo split -0.032 [-0.066, +0.009] | (b) inconclusive: right sign, 10× the accounting, matches the in-period drift |
| P(chain reaches k ≥ 10, given it reaches k ≥ 4) | 0.245 → 0.296 | | direction as expected; no CI |

**Reading.** Switching the nudger off removed about half a percent of the swarm's activity. That matches the per-nudge accounting and is far below day-to-day noise. Deep pause chains lost escape probability relative to shallow ones after the stop, but a similar drift appears inside the nudger-on period (traps deepen over the goal, H16), so this cannot be attributed to the nudges. Data: `data/processed/H35-nudger-maxwell-demon/G51off/offstep_results.json`.

## Scorecard (period-specific axes)
E 1 (the accounting prediction holds; the mechanism-level DiD is not attributable) · D 1 (accounting is unfitted).

## Notes
- 2026-10-03: folder created after the run for the catalog's NE43; the prediction predates the run (G51 folder and card). Analysis: `analysis/offstep.py`.
