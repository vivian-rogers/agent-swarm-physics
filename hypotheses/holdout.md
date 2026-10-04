# Locked holdout

Locked 2026-10-03, **before any dynamics or exploratory analysis was run.** Machine-readable copy: [`holdout.json`](holdout.json), which every analysis script reads to mask these windows. Exploratory work must exclude them. They're used only to confirm predictions written beforehand on a hypothesis card.

## What's held out

**Natural-experiment windows** (PT dates; end exclusive), reserved because they are the strongest interventional tests:

| Window | Dates | Why |
| --- | --- | --- |
| NE12 | 2026-02-23 → 03-02 | rooms channel cut (S4, S5, H01 D3.2) |
| NE21 + NE23 | 2026-06-08 → 07-06 | hours reversal (4→8→4→8 h) and nudger off/on (S3) |
| NE30 | 2026-03-05 → 03-16 | same-family succession, Gemini 3 Pro → 3.1 Pro (H01 D5.1.b) |
| #51 tail | 2026-09-07 → 09-21 | last two weeks of the private-role era |

**Goal periods** held out in full: **#1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45, #46, #47, #48, #49, #50** (16 of 51).
- **Blocked by the windows above:** #32, #34, #46–#50.
- **Drawn at random,** stratified by coupling mode (seed 20261003) from the remaining periods (excluding #51):
  - C: #1, #15, #28, #45
  - F: #9, #22
  - I: #14, #43
  - K: #29
  - M: none (only one left in the pool)

## Consequences
- S1's leader test (#45) and the memory week (#43) are now **confirmation-only**.
- The free-week pool for S6 loses #9 and #22 to confirmation; #11, #16, #31 and #37 remain for exploration.
- The quench-lab month (#46–#50) is confirmation-only. S3's predictions are already written in `promotion-shortlist.md`.

## History
The first draw started the NE21 window on Sunday 2026-06-07, which blocked #45 through a single weekend-day overlap. The window was corrected to start on Monday 06-08 (the first 8-hour weekday) and redrawn once with the same seed, still before any data had been examined. The redraw then selected #45 at random anyway. The draw stands; redrawing again would defeat the purpose.

## Reuse of a held-out period by a second hypothesis (default policy, 2026-10-03)
Set by Claude when H23 needed #45, which H02 had already used for its confirmatory run. Vivian can override. A held-out period that one hypothesis has used for confirmation may confirm a second hypothesis only if:
1. the second hypothesis's predictions and confirmatory script are committed before its run;
2. its observable is a different statistic, or a different data modality, from what earlier runs computed on that period, and nobody has examined it. Example: H02 computed #45's activity-timing couplings; nobody has looked at #45's message content;
3. the reuse is disclosed in both cards and in `LOG.md`.

Exploratory work still never touches held-out periods.

## Holdout ledger (DQ8, 2026-10-04)
Machine-readable ledger: `infra/data-quality/holdout_ledger.json`, built by `infra/shared/holdout_ledger.py` (`check()` before any confirmatory run, `record_run()` after). 269 planned or executed uses across 39 hypotheses. **Executed runs: three** (H02 on #45, failed; H04 on NE21+NE23 #46–#50 plus #45, falsified in reverse; H05 on NE12 #32 + #34 days 03-05..03-13, inconclusive).

Findings needing a decision:
1. **All three executed runs read the buggy `activity_bins`** (about half of events dropped; see `infra/README.md` Known issues). Whether to re-run them on the fixed table (a correction of a broken run, not a new test) is Vivian's call; until then their verdicts are provisional.
2. **#45 was used twice for activity timing** (H02 and H04) without mutual disclosure. H03's and H19's planned #45 Hawkes estimate duplicates H04's, so it is blocked under the reuse policy; the Curie–Weiss family (H01, H12, H16, H38) collides with H02; kick responses (H12, H16, H30, H35, H36, H39) collide with H04. #45 content has 11 planned users: whoever runs first makes all the others second users.
3. **NE21+NE23 (#46–#50):** H04's run collides with planned activity-gain tests (H01, H12, H26, H38) and kick-response tests (H09, H12, H30, H35, H36, H39).
4. **#32 and #34:** H05's run collides with H12's and H19's Curie–Weiss tests and same-modality plans (H15, H16, H35, H38). H21, H33, H36, H37 and H01's `confirm_r2.py` wrongly call H05's #34 script unrun; H10's card wrongly says #32 is unused.
5. **H19 and H38 plan the same equal-time gain statistic** on 9 held-out periods.
6. Stale status lines (H02, H04, H05 cards), uncommitted confirm scripts, and cards without a confirmatory section are listed in the ledger JSON. The estimator-family tags are regex-based and need a human pass.
7. **H43 disclosure (2026-10-04):** an early exploratory probe printed held-out nudge *counts* (no outcomes); disclosed in the H43 card.

