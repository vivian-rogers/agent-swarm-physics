# H27 confirm re-freeze on round-1b inputs (batch D, 2026-10-04)
Script: `confirm_r1b.py`. `confirm_holdout.py` is unchanged. Written before any holdout data was read. **Not run.**
## What changed vs `confirm_holdout.py`
- **Labels.** Old: H11's round-1 builder, whose ties are nondeterministic (8.1% of W30 labels differ). New: shared deterministic `project_states` (w 15/30, sources all), built in the script.
  - Labels are ranked on each target's own rows. For a fully held-out period this equals the shared ranking.
  - The #51 tail is ranked on the tail alone. Old: it was ranked on all of #51.
- **C1–C4: unchanged.** Same thresholds, frozen τ\* = 0.538, O1 onset rule, lead of 1 h, and rate-matched shift null. Round 1b reproduced round 1: 21 onsets, AUC 0.62 [0.50, 0.76], τ_AR1 0.41.
- **C5 → C5-r1b.** A link is now timed at its first context-ledger read by an agent other than its poster, not at posting time. Thresholds unchanged: MH OR > 2, within-period p < 0.05, ≥ 5 onsets.
  - Reason: exposure acts at the receiving call (STANDARDS §2). The convergence impostor was open.
  - Reported beside it, not scored: an in-flight arm (links posted in the 30 min before onset but unread at window start), and a split into agent-sent and other-sent links.
- **New C6-r1b (work ledger, DQ4).** For projects with onsets in both spaces, no work-commit onset leads the attention onset by ≥ 1 window. Needs ≥ 3 pairs, else inconclusive.
  - Reason: round 1b found lag 0 or +1 in 4/4 pairs.
- **Inputs that do not apply:** `activity_bins_fixed`, `outages_fixed`, the DQ8 trim and the embedding models. H27 uses none of them.
- **New guards:** `holdout_ledger.check()` for every target (strict on `--confirm`), and a commit check that covers this file and this note.
## Holdout reuse collisions (ledger L162–L172)
`check()` allows all 11 targets. No same-family prior run. Disclosure is needed on every target:
- **Prior runs on other statistics:** H05 on #32/#34; H02 and H04 on #45; H04 on #46–#50.
- **Competing planned users:** H11 and H28 (#22, #28, #45), H31 (#29, #46, #47, #50), H01 (most targets).
- **H28 link-hazard overlap:** H28's statistic is lagged link exposure → arrival hazard. C5-r1b is a link precursor of onsets.
  - These are different statistics, but they share link timing on #22, #28 and #45.
  - Whoever runs second must disclose. Vivian should rule whether this overlap counts under policy item 2.
## Dry run (stand-ins #30, #31, #38; non-holdout; `data/processed/H27-herding-early-warning/confirm_r1b_dryrun/`)
- **Executes.** The builder check passes: the rebuilt stand-in series equal the round-1b series in 6/6 (period, W) cells.
- **Stand-in numbers (not evidence):**
  - 11 onsets, 5 evaluable;
  - composite AUC 0.74 [0.55, 0.91]; τ_AR1 0.30;
  - C1 "confirmed", C2 not, C3 and C4 confirmed (original dry run: AUC 0.74, same calls);
  - C5-r1b confirmed: 7/11, OR 9.8, p 0.001;
  - C6-r1b inconclusive (2 pairs, lags 0 and +1).
- **The ledger timing does not change the stand-ins.** Read-timed and posted-timed links give identical counts, because links are read within seconds. The in-flight arm is empty (0/11).
  - So C5-r1b removes the convergence impostor only formally. A real blind-window test would need H28's per-recipient design.
## Recommendation
**Adopt with changes.**
- Vivian rules on the H28 link-timing overlap.
- Optionally demote C5-r1b to secondary, since read and post timing coincide at 15-min resolution.
