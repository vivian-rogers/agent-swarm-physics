# H35 × NE10: the auto-nudger switched on (CHANGELOG 2026-02-10; first nudge 2026-02-13, inside #30)

**Verdict:** supported (accounting only; low information)
**Role:** native (round 1b native test below) · round 1: exploratory (natural experiment, non-holdout)
**Verdict (1b):** supported (switch-on invisible in work, z +0.92; 2026-10-04)
**Period:** regime I · before = #27 (01-12 → 01-23) + #30's nudge-free days 02-09 → 02-12 (#28, #29 held out); after = 02-13 (#30) + #31 (02-16 → 02-19; 02-20 = NE11 excluded). Data: `data/processed/H35-nudger-maxwell-demon/NE10/`.

## Why this period
The only documented switch-on of the nudger outside the holdout. H04 found the escape hazard from long inactivity fell after it (opposite to its prediction), with goal changes and roster joins as confounds.

## Prediction
*Written 2026-10-03, before running.*
- **P7:** work accounting predicts that the switch-on changes active agent-minutes by ≤ 0.5% (nudges/day × per-nudge work ÷ present agent-minutes), i.e. undetectable against day-to-day noise; the observed change is reported with a placebo split. The nudger's information in G30 + G31 is above the circular-shift null (scored per period with ≥ 15 nudges: G31 only).
- **What would count against:** an observed active-fraction change far larger than the accounting bound that survives the placebo split would mean the nudger acts through more than its direct per-nudge work (a field on everyone, HH52), or a confound.

## Result
| Quantity | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| nudges in the grid, before / after | 0 / 20 (4.0 per day after) | | |
| per-nudge work, regime I (H04 isolation set; strict isolation leaves 1 nudge) | 0.60 [-0.98, 1.81] min, n = 15; placebo 1.13 [0.12, 1.91] | 0 | placebo not clean: selection |
| accounting: predicted change in the active fraction | +0.11 pp (regime-I work), +0.27 pp [+0.13, +0.40] (G51 work transported) | ≤ 0.5 pp predicted | **supported** |
| observed change in the active fraction | +1.1 pp [-2.8, +4.9] (75.6% → 76.6%) | placebo split +1.9 pp; detectable change ≈ 7 pp | undetectable, as predicted |
| information used | G30 b = 0.64 (9 nudges, above null); G31 b = 0.20 (11 nudges, not above) | ≥ 15 nudges needed to score | n/a (too few) |

**Reading.** The switch-on bought at most a few tenths of a percent of agent-minutes, an order of magnitude below what the day-to-day noise lets one see. So NE10 cannot show the nudger's work at swarm level, and H04's lower escape hazard after the switch-on must come from the confounds it lists (goal changes, two roster joins), not from the nudges. Data: `data/processed/H35-nudger-maxwell-demon/NE10/ne10_results.json`.

## Round 1b native test (first nudges ever, with work commits)
*Role of this section: native (round 1b), in addition to round 1.*
*Prediction written 2026-10-04, before computing any round-1b outcome on 02-13.* The 12 nudges of 02-13 are the first in the record (no habituation; the work ledger is already dense in #30).
- **N1:** swarm work commits per active agent on 02-13, log(1 + ·) minus the mean of 02-10..02-12, is within ±2 SD of the same day-contrast at other #30–#44 non-holdout days (|z| < 2): the switch-on is invisible in work, as the round-1 accounting predicted for activity.
- **N2 (descriptive; n = 12):** first-nudge glance ATT positive; work-commit ATT (60 min) with a CI including 0.

**Result (round 1b native, run 2026-10-04; `r1b/r1b_summary.json` → `NE10`).**
- **N1 holds:** log(1 + work commits per active agent) on 02-13 minus 02-10..02-12: +0.30 vs null +0.05 ± 0.28 (72 day-contrasts, #30–#44 and #51): z +0.92.
- **N2 n/a:** strict past-only isolation leaves 0 first nudges (all 12 nudges fell on 02-13 among already-kicked agents).
- Native verdict: **supported** (the switch-on is invisible in work, as the accounting predicts).

## Scorecard (period-specific axes)
E 1 (the per-nudge accounting predicts an undetectable swarm-level change, and none is seen; a weak test, since a null is easy to get) · D 1 (accounting is an unfitted prediction).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled after the prediction above. Regime I has almost no strictly isolated nudges; the H04 isolation set (nudges + human messages) is used and disclosed.
