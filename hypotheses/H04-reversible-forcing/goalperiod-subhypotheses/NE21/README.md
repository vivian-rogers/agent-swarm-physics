# H04 × NE21 (+NE23): hours switches 4 → 8 → 4 → 8 h, and the nudger off session (2026-05-26 → 07-04)

**Verdict:** failed (C1 falsified in the opposite direction; C2 inconclusive; C3 untestable; C4 partial; MF-C indistinguishable)
**Verdict (1b):** not re-run (locked holdout; re-running is Vivian's call). C1 (Hawkes n) is unaffected by the round-1b corrections; C2, C4 and MF-C read the buggy activity table and C2/C4's kernels used the future-kick isolation rule (see the Round 1b note below)
**Role:** confirmatory (locked holdout)
**Period:** spans goals #44–#50 (regime III). Segments: A1 4 h (05-26 → 06-05, #44 + #45), B1 8 h (06-08 → 06-12, #46), A2 4 h (06-15 → 06-26, #47–#49), B2 8 h (06-29 → 07-03, #50). NE23 off session: 06-13 (Saturday evening, #best agents only). Sensitivity: B1 split at the 06-11 pause-default change; A1 restricted to #45; a non-holdout 8 h extension in #51.

## Why this test
The only reversal design in the dataset (ABAB on documented daily hours), plus a nudger on/off. The prediction was HH46/S3: 8 h days spread activity out and lower the branching ratio n, reversibly.

## Prediction
Pre-registered in the main card ("Confirmatory", C1–C4 and MF-C, with two dated amendments made before any holdout use) and committed in e9bf2f7 before the run.

## Result (run 2026-10-03; `analysis/confirm_ne21_ne23.py`; `data/processed/H04-reversible-forcing/confirm_ne21_ne23.json`)
| Segment | Hours | n | a₁ (fast) | K (MF loop gain) |
| --- | --- | --- | --- | --- |
| A1 | 4 h | 0.31 | 0.31 | 0.32 |
| B1 | 8 h | **0.67** | 0.36 | 0.17 |
| A2 | 4 h | 0.46 | 0.37 | 0.25 |
| B2 | 8 h | **0.89** | 0.32 | 0.27 |

- **C1:** 0 of 3 switches have the predicted sign. All three go the other way, and there's no monotone drift. ABAB contrast (4 h − 8 h) = −0.39 [−0.46, −0.20], against a placebo |p95| of 0.42 from non-holdout week-to-week variation. **Falsified**; the reverse effect sits at the noise edge.
- **C2:** kernel ratios have CIs spanning roughly ±10× (nudges) and ±40× (humans). Inconclusive.
- **C3:** fewer than 10 kicked activations in some segment. Untestable.
- **C4 (NE23):** 9 automated "nudges" were detected in the off session, so the manipulation check fails. They may be pause/resume messages; see `infra/README.md` Known issues. Idle fraction is higher off (0.24) and inactive runs longer; n(off) − n(B1) = −0.09 [−0.40, 0.33] (unchanged, as predicted); the kernel didn't return in A2.
- **MF-C:** K differences are within the placebo; the decay-time gap (≥ 3× in every segment) didn't hold.

## Round 1b note (2026-10-04): what the corrected exploratory numbers imply for this executed run
- **C1 (n reversal, falsified in reverse):** the Hawkes series is built from `chat_core` talk events in 10-s bins, not from `activity_bins`, and n does not use the isolation rule, so neither correction reaches it. The kicks enter only the exogenous terms (round-1 nudge classification), which carry almost no likelihood. **C1's verdict stands on its inputs.**
- **C2 (kernel invariant across hours):** used the old table and the isolated nudge set. On non-holdout data the corrected design changes the kernel level (G51: 1.16 instead of 1.66 with isolation on the old table) and its shape (response from the receiving call, no 4-min dead zone). C2 was inconclusive with ratio CIs of ±10×; a corrected re-run would change the numbers, probably not the verdict.
- **C3 (Onsager T_eff):** untestable for too few activations; the corrected design treats every nudge (about 2× more cells), which might make it testable.
- **C4 (NE23):** the idle share and inactive-run lengths come from the buggy table (on non-holdout days the fix moves states for 24% of agent-minutes), and the kernel-return clause used isolation. The failed manipulation check (9 "nudges" in the off session) concerns message classification, which `kicks_classified` now does separately; it was not re-checked here (holdout).
- **MF-C (K tracks hours):** K comes from activity; on non-holdout days the fixed table raises it (III 0.26 → 0.32; 4 h 0.21 → 0.30; 8 h 0.28 → 0.33) and shrinks the 4 h vs 8 h gap. MF-C was indistinguishable from noise and probably remains so, but its numbers are void.
- **Recommendation:** C2, C4 and MF-C are corrections of a broken run, not new tests; re-running them on `activity_bins_fixed` with the round-1b kernel would be legitimate under the holdout policy. That decision is Vivian's.

- The power note in the card anticipated this: detecting an hours effect needed a contrast ≳ 0.4. The reverse contrast is about that size.
- New idea: longer sessions mean more unread context per turn, hence more activity triggered by activity (H08). Worth an HH.
