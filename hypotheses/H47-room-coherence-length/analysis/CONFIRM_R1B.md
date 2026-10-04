# H47 confirm re-freeze (r1b), 2026-10-04: prepared, NOT RUN

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. No holdout data was read. Vivian's sign-off is needed.

## What changed
- **Inputs.**
  - Village-off windows come from `outages_fixed` (the old `outages` came from the event-dropping bins).
  - The self-repeat dedupe comes from DQ5 `statement_flags`. Primary: chat restatements under either model. Copies only (`self_repeat_both`) is reported for C1. Round 1 used its own bge cosine > 0.95 rule.
  - Both embedding models are used. Each model has its own whitener, goal and kickoff field directions, raw vectors (C4) and agent-day vectors (C5).
- **Not inputs.**
  - Activity, visibility, work, failures and nudges.
  - The DQ8 trim: the room-relabel null permutes rooms within slots, so the scheduler cancels in C_B.
- **Criteria.** Each criterion must now pass under both bge and gte: C1-r1b … C5-r1b. Thresholds are unchanged. Credences drop by about 0.05 because two models must agree.
- **Guards.** Both flags are still required; the commit check is kept; a ledger gate is added.
- **Builder check.** The dry run first rebuilds with round-1 inputs and must reproduce explore.py's C_B for #41 and #44 within 0.01.

## Holdout reuse collisions (ledger, content_alignment, message content)
- **No target is blocked.**
- **Executed runs in another modality (activity), disclose:**
  - #45: H02 and H04;
  - #46, #47, #50: H04;
  - #34 (C3's pre side): H05.
- **Closest planned collision:** H26's unrun room-excess confirm on #46 and #47. Whichever runs second treats its C1 as non-independent.
- **Other planned content users** on #45–#50: H01, H12, H13, H20, H23, H29, H30, H31, H33, H36, H39.
- **NE15:** no other users.

## Dry run (`data/processed/H47-room-coherence-length/confirm/confirm_r1b_dryrun.json`, 64 s)
- **Builder check.** It reproduces explore C_B: #41 0.1747 vs 0.1747; #44 −0.0375 vs −0.0375.
- **Corrected inputs (bge / gte):**
  - C_B: #41 0.18 / −0.03 and #44 −0.04 / 0.02 (p 0.003); #42 0.53 / 0.40 (not ≤ 0.3, as in round 1).
  - Copies-only dedup changes C_B by ≤ 0.01.
  - C2 separation F: #41 7.5 / 9.3, #42 1.6 / 2.7, #44 7.5 / 10.7. The rule holds.
  - C3 analogue (#40 → #41): DiD −1.21 / −1.58, p ≤ 0.003.
  - C4 (#42): p_L 0.64 / 0.15; first-statement shift ≥ 0.84.
  - C5 (05-11): swarm z 9.0 / 11.2, so it fails. It failed in round 1 too, because that day is goal-confounded.
- **Scores.** C1–C4 pass and C5 fails, the same as round 1. No value crosses a threshold, so no prediction changes.

**Recommendation: adopt.** Coordinate the order with H26 for #46/#47.
