# H30 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any holdout data was read. Not run on the holdout.

## What changed
- **Inputs** (the `--data r1b` paths of `scheme/build.py` and `run_period.py`):
  - activity: `activity_bins_fixed`, with outage masks rebuilt from it;
  - nudge target: the leading @;
  - kick time and recipients: the ledger receiving call;
  - design: past-only kick adjustment;
  - content: bge and gte.
- **Inputs not applicable.** DQ8 trim does not apply: this is a per-kick response with a day fixed effect, not a synchrony statistic. Failures are not used.
- **Outcome.** Active minutes, kept on purpose: χ_act is an attention response (Known issue 83).
- **Level criteria use the day-FE model:** C-act-r1b, C51-1-r1b, C51-4-r1b and C45-1-r1b.
- **Content criteria pass only under both models:** C51-2, C51-6, C45-2, C4650-1 and C4650-2 (all `-r1b`).
- **#45 is content-only by default.** `--include-g45-activity` re-enables C45-1 and #45's share of C-act, on Vivian's written override only.
- **Confirm-only change.** A copy of the round-1b operator-message loader without its exploration guard.
- **Ledger gate.** Blocks a target only on a same-family, same-modality prior run.

## Why
- Ledger items 8, 12 and 2–3. RE-V2 changed the G51 level (0.59 → 0.98) and reversed the lull rule.
- Round 1b makes the day-FE model primary. With past-only controls, the FE and no-FE models agree (0.98 vs 1.07).
- STANDARDS §2: two embedding models.
- H04 ran nudge→activity (A30) on #45–#50, which is the same statistic as χ_act.

## Holdout reuse
- **#45 activity:** blocked; same family and modality as H04's run (`check()` refuses).
- **#45 content, #46–#50 content:** `check()` reports `allowed=False` because the family tags match H04 (kick_response). The modality differs (H04 was activity timing), so policy item 2 holds. The gate passes them, but this reading is Vivian's to confirm.
- **#51 tail:** no prior run. Many planned users (H08, H12, H19, H39 same family).

## Dry run (#51 08-07..08-21, #51 08-24..09-04 with no nudges, #44, #41/#42)
- Executes, including the zero-nudge tail-like path. On that path the nudge criteria are n/a and C51-2 is computed: bge 0.023, gte 0.020, both CIs > 0.
- C51-4-r1b, C51-6-r1b, C45-1-r1b, C45-2-r1b and C4650-2-r1b pass.
- C51-1, C51-3, C51-5 and C-act fail.
- C51-2 fails on the nudge-era stand-in (degenerate CI).
- C4650-1 has no human pairs on #41/#42, as in the original dry run, so the stand-ins do not exercise it.

## Recommendation
**Adopt with changes.** On the holdout the activity primary (C-act) is untestable: the #51 tail has no nudges (they stop after 08-20) and #45–#50 belong to H04. Either retire C-act from the holdout or let Vivian override #45. Confirm the content claims (C51-2, C4650-1).
