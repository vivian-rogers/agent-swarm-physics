# H16 confirm re-freeze on round-1b inputs (batch D, 2026-10-04)
Script: `confirm_r1b.py`. `confirm.py` is unchanged; its rule functions are imported, not copied. Written before any holdout data was read. **Not run.**
## What changed vs `confirm.py`
- **Error loops (TS3 → TS3r).** Old: `actions.error` (stderr non-empty). New: real failures, from `turn_outcomes.failed` for bash/type turns and platform `error_class` for other turns.
- **Nudge target.** Old: every named agent. New: the leading @ (H35).
- **Kick recipients.** Old: the `exposure` table. New: context-ledger readers (`context_ledger_items` × `call_windows`).
  - Spell hazards keep posting-time look-backs. Inside a silence, a read-time clock would put every read at the escape call itself.
  - TS2r gates count a kick only if the gate call read it (receiving-call timing).
- **Swarm block (d): dropped.** It was descriptive. Its βJ₀ is H02's Curie–Weiss family on #45.
- **Outage sensitivity.** TS1r is now censored at `outages_fixed` all-silent runs ≥ 10 min. Old: H16's own minute grid (round 1's A3 rule).
- **Prediction changes.** Each comes from a round-1b result. Thresholds are unchanged unless stated.
  - **C45-3-r1b, C45-6-r1b, C32-2-r1b:** same rules on ledger and leading-@ inputs. In round 1b, ORs moved < 1 SE.
  - **C45-4-r1b and C32-1-r1b (secondary): TS3r does *not* age.** Old C32-1 was primary and predicted aging.
    - Reason: real-failure loops age only in #51 (3/10 point estimates).
    - Caveat: a negative without a power check.
  - **New C32-5-r1b (primary) and C45-7-r1b (secondary):** directed kicks do not raise the TS3r break hazard. Needs ≥ 30 rows. Round 1b: 9/9 powered periods.
  - **#32 primaries are now C32-2-r1b and C32-5-r1b.** Unchanged: C45-1, C45-2, C45-5, C32-3, C32-4.
- **New, descriptive:** an in-flight placebo at TS2r gates. These are directed kicks posted after the gate call's context was assembled and before its outcome, so the gate could not have read them.
- **New guard: per-prediction reuse families.** `holdout_ledger.check()` runs per (target, family). A blocked family is not computed on `--confirm`.
  - `--reuse-ruling FAMILY` records Vivian's written ruling and lifts the block.
## Holdout reuse collisions (ledger L104–L105)
- **#45, `kick_response`: blocked.** H04 ran a kick-response test on #45. Without a ruling, C45-3-r1b, C45-5, C45-6-r1b and C45-7-r1b are not computed, and #45 is scored on C45-1 and C45-2 alone.
- **#45, `behavior_states`: allowed.** Disclosure needed: H02 and H04 ran other statistics there, and 9 users plan uses.
- **#32: both families allowed.** Disclosure needed: H05's executed NE12 run, plus planned users H12, H19, H35, H36 and H38.
## Dry run (stand-ins G31 to 02-20 for #32, G44 for #45; `data/processed/H16-metastable-traps-kramers/confirm_r1b_dryrun/`)
- **Executes** in about 30 s. Kick-family predictions are computed on the stand-ins; the real #45 run would block them.
- **G44 as #45: mixed.**
  - C45-1 pass: β −0.77, Wald [−1.32, −0.22].
  - C45-2 fail: β_lnk −0.23 [−0.54, 0.08]. The original dry run also failed here.
  - C45-3-r1b pass (lnOR 0.86 ± 0.63); C45-6-r1b pass (0.30 vs null p95 0.20); C45-4-r1b (β +1.63), C45-5 and C45-7-r1b pass.
- **G31 as #32: supported.**
  - C32-1-r1b pass: β −0.77, Wald CI spans 0.
  - C32-2-r1b pass. C32-3 n/a. C32-4 fail (Kramers).
  - C32-5-r1b pass: 0.03 ± 0.32, 78 rows.
- **In-flight placebo (G44): uninformative.** Read kicks lnOR 0.71 ± 0.30 (76 gates) vs in-flight 0.49 ± 0.55 (19 gates; median window 16 s). Nudger selection is not excluded.
- **Outage sensitivity: no runs to censor.** Neither stand-in has an all-silent run ≥ 10 min on the fixed clock. The censoring code path was checked in memory.
## Recommendation
**Adopt with changes.** Vivian must rule on the #45 kick family (H04 collision). Without a ruling, #45 confirms only trap aging. She should also decide whether a non-aging prediction (C32-1-r1b, C45-4-r1b) is worth scoring without a power check.
