# H28 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm_holdout.py` (untouched) for any holdout run. Written before any holdout data was read. Not run on the holdout.

## What changed
- **Inputs.**
  - Visibility: the link reaches the recipient at its ledger receiving call (`context_ledger_items` ⋈ `call_windows`, `H28_DATA=r1b`). The old rule was the first logged turn (event turns before NE09).
  - Shift null: re-derives visibility from receiving calls.
  - Confirm path: builds the ledger exposures with a copy of `scheme/build_r1b.py`. On the stand-ins the copy reproduces `r1b/G30`, `G31`, `G41` exactly (exposures, calls, work touches).
- **Not relevant to H28:** activity bins, outages, embeddings (no DQ8 trim), failures, nudges. **C1–C4 and R1–R3 unchanged** (99 shifts).
- **New, R4-r1b (in-flight placebo).** This is the round-1b NE09 native rule N9b. Pooled over targets: E_blind 90% lower bound > 1 and E_blind ≥ 0.5·E_read. It gets its own verdict line and does not change CLAIM or PATTERN.
- **New, W-r1b (descriptive).** Work-commit arrivals (DQ4) are reported where there are ≥ 30.
- **Expectation, unchanged.** CLAIM refuted or inconclusive; PATTERN holds; R4-r1b holds.

## Why
- Ledger item 15 and RE-D1: the old turn rule mismeasured visibility before NE09. #22 is a pre-NE09 target.
- STANDARDS §1: the in-flight placebo is required against contemporaneous convergence.
- Round 1b found that recipients switch at 6.5× baseline before they can read a link.

## Holdout reuse (ledger L173–L175)
- No prior run of H28's statistic on #22, #28 or #45.
- #45: H02 and H04 ran activity timing there (another modality).
- Planned same-family users: #22 H06, H11, H34; #28 H08, H11, H18, H34; #45 H08, H11, H15, H18, H23. Same modality: H11, H27.
- Whoever runs first makes the others second users. Disclose in the cards and in `LOG.md`.

## Dry run (stand-ins #31→#22, #30→#28, #41→#45; output in scratch only)
- Executes end to end.
- CLAIM **REFUTED**, PATTERN **HOLDS**, R4-r1b **HOLDS**. These are the same verdicts as the original dry run.

| Stand-in | κ | z_shift | C1 | R_link |
| --- | --- | --- | --- | --- |
| #31 | 0.48 | 0.9 | no | 0.13 |
| #30 | 0.88 | 3.2 | yes | 0.25 |
| #41 | 0.77 | −0.6 | no | 0.18 |

- Pooled E_blind 2.02 (90% lower bound 1.43) vs E_read 2.26.
- The guard refuses without both flags, and refuses unless the scripts and the card are committed. `holdout_ledger.check()` allows all three targets.

## Recommendation
**Adopt.**
