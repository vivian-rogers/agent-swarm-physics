# H36 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any holdout access. Not run on the holdout.

## What changed
- **Inputs** (`scheme/build.py` CFG: fixed, restate, trim; catalog r1b):
  - activity: `activity_bins_fixed`, with the stall mask from shared `outages_fixed` (all days kept, holdout flagged);
  - DQ8 trim: the all-present window is cut before surrogates;
  - content: bge and gte, each without restatements (DQ5 `self_repeat` per model), with R1 on the same vectors;
  - catalog r1b: new and corrected NE dates join the placebo exclusion list, and NE44 joins the C6 table.
- **Predictions.** "Both" means both models must pass.
  - **C1-r1b:** uses the **trimmed** Z_phys; both.
  - **C2-r1b:** Z_cont; both.
  - **C4-r1b:** R1 against the trimmed Z_phys; both.
  - **C5-r1b:** trimmed Z_act.
  - C3 is unchanged (bge; gte reported). Thresholds are unchanged. Failures, work and nudges are not used.
- **Guard:** adds a commit check and the ledger gate (the original had neither).

## Why
- Ledger item 8: re-freeze on fixed bins. STANDARDS §3: trim day-level synchrony statistics before surrogates. Z_phys and Z_act are synchrony statistics.
- DQ5: two models. Round 1b: Z_cont replicates in both models (0.78 / 0.74), while C3's false-alarm rate fails under gte (0.13).

## Holdout reuse (ledger L221–L238)
- No prior run of H36's statistic. H04 (#45–#50, NE21+NE23), H05 (#32, #34, NE12, NE30) and H02 (#45) ran other statistics or modalities.
- The ledger tags H36 as kick_response only because its text says "kickoff". `check()` therefore returns `allowed=False` on #45–#50. The gate passes these targets because the modality differs. Vivian should confirm this, and the tag needs the human pass from ledger item 6.
- Many planned users per target, for example #45: H12, H13, H16, H23, H30, H33, H35, H39.

## Dry run (all non-holdout days; exploratory kickoffs and placebos): executes and reproduces round 1b

| Score | bge | gte |
| --- | --- | --- |
| AUC Z_phys_trim | 0.67 | 0.65 |
| AUC Z_cont | 0.78 | 0.74 |
| AUC R1 | 0.95 | 0.97 |
| AUC Z_act_trim | 0.50 | 0.50 |

- C1-r1b, C2-r1b, C4-r1b, C5-r1b and C3 (bge) pass; C3 under gte fails. Overall in-sample: CONFIRMED.

## Recommendation
**Adopt.** The physics alarm (C1-r1b) sits near its failure boundary. The content claim (C2-r1b) is the robust one.
