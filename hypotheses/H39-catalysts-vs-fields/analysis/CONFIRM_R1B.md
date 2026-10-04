# H39 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any holdout access. Not run on the holdout.

## What changed
- **Inputs** (round 1b):
  - nudge target: the leading @ (agents named second become N_oth, which marks busy minutes);
  - DQ8 `lever_design` presence cut (`LEVER["presence_cut"]=True`);
  - second state space: Jev v3.1 states lumped to V4 (work / coord / wait / maint, soft transitions);
  - receiving-call (`t_rc`) timing: reported as a sensitivity for every kick class.
- **Confirm-only changes.**
  - A leading-@ kick table that passes the holdout flag through.
  - A copy of `v3states.load_v3` without its exploration guard.
- **Unchanged inputs.**
  - B4/B6 come from H14's minute grid, which never read `activity_bins`.
  - C4 content drift and C7 kickoff steps stay bge-only. No gte agent-window vectors exist, and C7's placebo pool is frozen on bge. This deviates from the two-model rule; it is disclosed in the script.
- **Predictions.**
  - C1–C8 are unchanged in rule; C1, C2 and C6 now use the corrected nudge and presence design.
  - New secondaries on V4: **C1v-r1b** (pooled nudge K > 0), **C2v-r1b** (wait escape up and Δπ_wait < 0), **C6v-r1b** (erasure: Δπ_wait < 0, Δπ_work > 0).
  - The overall rule is unchanged.

## Why
- Ledger item 12 / RE-V2: re-freeze on leading-@ targets and lever_design.
- Known issue 38: never condition on future kicks or presence.
- Round 1b: the nudge passes all five clauses only on V4. The erasure field is robust across state spaces; its catalysis is not.

## Holdout reuse (ledger L256–L269)
- `check()` returns `allowed=False` on #45–#50 because the family matches H04's kick-response run. The modality differs (behavior states and message content vs H04's activity timing), so the gate passes them under policy item 2.
- B4 states are built from the same event times as activity. Vivian should decide whether "behavior states" counts as a different modality from H04's activity timing.
- #51 tail: no run. Planned same-family users: H08, H12, H18, H19, H29, H30, H34.

## Dry run (late #51; G38, G41, G42, G44; regime-III kickoffs; a G38 day pair)
- Executes end to end. Same B4 pattern as the original dry run: C1 ✗, C2 ✗, C3 ✓, C4 ✗, C5 ✓, C6 ✓, C7 ✓, C8 ✗.
- New: C1v-r1b ✓, C2v-r1b ✓, C6v-r1b ✓.
- Overall in-sample: mixed.
- The power warning stands: B4 C1 is not significant on the stand-ins.

## Recommendation
**Adopt with changes.** Vivian should rule on the modality question for #45–#50. Consider promoting C1v-r1b to primary next to C1, since V4 carries the nudge signal in round 1b; this needs a dated amendment before any run.
