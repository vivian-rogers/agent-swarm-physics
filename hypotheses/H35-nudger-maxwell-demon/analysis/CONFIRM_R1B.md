# H35 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any held-out outcome was read. Not run on the holdout.

## What changed
- **Inputs: no change was needed.** H35 already used the leading-@ target and active rows from `events_core` + `actions` (never `activity_bins`).
- **Outcomes** (round 1b, `r1b_outcomes.py`), replacing active minutes for work claims:
  - **glance:** any activity within 30 min;
  - **sustained:** a run of ≥ 3 active DQ1 ledger calls starts within 30 min (H43);
  - **work:** DQ4 agent work commits, excluding automated ones.
- **The post-hoc rate DiD is now pre-registered:** post 60 min minus the placebo m−30..m−16.
- **Confirm-only change.** Sources include held-out ledger turns and commits.
- **Unchanged criteria:** C1, C2, C6 (information) and C3, C4, C7 (attention-side gate).
- **Changed or new:**
  - **C5-r1b:** first-nudge glance ATT > 0 (was A30 active minutes).
  - **C8-r1b (new primary):** the pooled #47+#50 work-commit DiD CI includes 0, with half-width ≤ 1 commit/h; otherwise inconclusive.
  - **C9-r1b (new):** gate-once/logged ratio ≤ 1.25 on sustained escapes.

## Why
- Known issues 82–83 / RE-O1: active minutes measure attention. Nudges buy glances, not commits.
- The matched design fails its placebo for work and sustained outcomes (−0.35 and +0.058), so a placebo-differenced rate is required.
- Round 1b (G51): work DiD +0.22/h [−0.29, +0.82]; gate sustained ×1.03; glance ATT +0.082.
- C8 needs a power floor because a negative claim needs power (STANDARDS §3).

## Holdout reuse (ledger L216–L220)
- `check()` **blocks #45, #47 and #50**: H04's executed NE21+NE23 / #45 run is the same family (kick_response) and the same modality (activity timing).
- H35's statistics there (bits per nudge, gate slope, policy ratio, work DiD) differ from H04's A30. Under the current ledger tags the guard refuses; Vivian must re-tag or override.
- **#32, #34:** H05 ran there (other family). Planned users: H12, H16, H19, H36, H38.

## Dry run (G44→#45, G51a→#47, G51b→#50, G31→#32, G35→#34)
- Executes end to end.
- **Pass:** C1, C2, C3, C4 and C7, the same as the original dry run.
- C8-r1b passes: pooled +0.18 [−0.33, +0.68] commits/h, half-width 0.51.
- C9-r1b: G51a passes (0.68), G51b fails (1.67).
- C6: G35 passes, G31 fails.
- C5-r1b fails on both stand-ins: one first nudge each. The original C5 also failed; regimes I/II have almost no isolated first nudges.
- Overall in-sample: supported.

## Recommendation
**Adopt with changes.** The primaries cannot run until Vivian rules on the ledger family tag for #45/#47/#50. Consider retiring C5-r1b (no first nudges to test in regimes I/II).
