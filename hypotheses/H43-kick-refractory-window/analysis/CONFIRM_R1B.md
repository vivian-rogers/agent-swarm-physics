# H43 confirm re-freeze (r1b), 2026-10-04: prepared, NOT RUN

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. No holdout data was read. Vivian's sign-off is needed.

## What changed
- **Inputs.** The nudge target (class N) is now the leading @ only (H35 rule; shared `infra/shared/idle_gates.leading_targets`). Round 1 counted a nudge as a kick for every agent it named (ledger `ment`).
  - A nudge that names the recipient but not as its leading @ becomes `nNo`. It is not a class-N kick. It still marks the 30-min quiet window and excludes the call as a control (H39 r1b `N_oth` rule).
  - Counts are rebuilt in memory from `context_ledger_items`. Text is read in memory only and never written.
- **Inputs already current.**
  - Receiving-call timing and visibility come from the DQ1 ledger.
  - Writes come from the DQ4 work ledger.
  - `states_min` is the shared table.
  - Activity bins, outages, failures and embeddings are not inputs.
  - @-mentions (class A) keep `ment`, because the leading-@ rule is for nudges.
- **Predictions.**
  - C1, C2, C3 and C5 are unchanged; they do not involve nudges.
  - C4 keeps its thresholds and is now computed on leading-@ nudges. It is relabelled **C4-r1b**.
- **Dry run.** A G51 nudge stand-in (07-27 → 08-20, nudger on) was added so that C4 runs at a powered size.
- **Guards.** Both flags are still required; the commit check is kept; a holdout-ledger gate is added.
- **Known limit.** A call that reads an @-mention plus a non-leading nudge can still count as a "pure" A primer. This is rare and is not fixed without editing `h43lib`.

## Holdout reuse collisions (ledger, kick_response, activity timing)
- **C4 targets #45–#50: blocked.** H04's executed run measured nudge → activity responses there, so this is a same-family, same-modality second use. C4-r1b is n/a by default. `--include-ledger-blocked` enables it on Vivian's written override. The overall rule ("C1, C2 and C4-r1b or C5") then rests on C5.
- **Allowed, disclosure needed:**
  - #51 tail (C1–C3). Planned competitors: H08, H12, H19, H30, H39.
  - #1, #9, #14, #15 (C5). Planned competitors: H19, H20, H36.

## Dry run (`data/processed/H43-kick-refractory-window/confirm_r1b_dryrun/confirm_results.json`, 32 s)
- **Scores.** C1, C2, C3 and C5 pass. C4-r1b is n/a on the original stand-ins (33 idle primers).
- **Unchanged parts.** The tail and human numbers are identical to the original dry run (tail R(0,15] 0.60 [0.39, 0.91]; human E1 0.79), as expected.
- **Leading-@ effect.** It removes 12% of nudge-receiving calls on the stand-ins (249 → 219) and 29% on G51 (610 → 432).
- **G51 stand-in, C4-r1b passes:**
  - E1 on any activity: 0.41 [0.11, 0.79] (round 1 with `ment`: 0.56);
  - E1 on sustained work: −0.08;
  - re-fire R(15–60]: 1.47 (round 1: 1.28).

  The corrected target does not move C4 across a threshold, so no prediction changes.

**Recommendation: adopt.** C4-r1b stays n/a unless Vivian overrides the H04 collision.
