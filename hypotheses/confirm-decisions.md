# Confirmatory decisions for Vivian

Status: **nothing has run on the holdout.** The re-frozen scripts (`analysis/confirm_r1b.py`, with notes in `analysis/CONFIRM_R1B.md`) were written beside the untouched originals and dry-run on non-holdout stand-ins only. Each script refuses to run unless it is committed and called with both confirm flags. This sheet collects every decision the re-freeze batches surfaced. Batches A, B and D will be added when they report.

## Batch C (H31, H33, H43, H47, H49), re-frozen 2026-10-04

| Hyp | Recommendation | Your decision |
| --- | --- | --- |
| H49 | Adopt. C1–C6 are already set on fixed tables. **Blocked by the ledger** on #45 (H02) and #47/#49 (H04): same statistic type on activity data. | Override the block (`--include-ledger-blocked`, log it), or test regime III on 51m alone? |
| H43 | Adopt. C4-r1b uses leading-@ nudges. **C4 is blocked** on #45–#50 (H04's nudge responses). | Override H04's collision so C4-r1b runs, or let C5 carry the "C4 or C5" clause? |
| H31 | Adopt with changes. C2-r1b uses the protocol's pick M_ul2_rw, which won by only 2.4% and did worse than the constant on the stand-ins. | Keep M_ul2_rw for C2-r1b, or declare the constant the operator rule before the run? |
| H47 | Adopt. C1–C5 must pass under both embedding models. | Run before or after H26 on #46/#47? The second runner is not independent. |
| H33 | Adopt, but low value. The null holds in both models. It would become the first user of the content and work statistics on up to 10 targets. | Run last, or retire? |

## Batch B (H28, H29, H30, H32, H34, H35, H36, H38, H39, H41), re-frozen 2026-10-04
| Hyp | Recommendation | Your decision |
| --- | --- | --- |
| H28 | Adopt. Adds R4-r1b (in-flight blind window). | none needed |
| H29 | Adopt with changes. C1-r1b uses both models, C2-r1b keeps the CI clause on the #51 tail only, C7-r1b adds the reply network. C6 relies on the unreliable content network. | Accept C2-r1b; retire or demote C6? |
| H30 | Adopt with changes: day-FE model, both models. **The activity claim has no clean target** (#51 tail has no nudges; #45–#50 are H04's). | Retire C-act from the holdout, or allow #45 activity (`--include-g45-activity`)? |
| H32 | Adopt. Adds C9-r1b (read beats unread at 60 s). | none needed |
| H34 | Adopt. C3/C4 constants refit on ledger visibility. | Accept the refit constants? |
| H35 | Adopt with changes. New primary C8-r1b (work DiD with a power floor). **Blocked** on #45, #47 and #50 (H04, same family and modality). C5-r1b untestable. | Accept C8-r1b as primary? Are bits per nudge and the gate slope a different statistic from H04's kernel? Retire C5-r1b? |
| H36 | Adopt. Z_phys becomes the trimmed version. `check()` flags #45–#50 on the "kickoff" tag only. | Accept trimmed Z_phys? |
| H38 | Adopt with changes. **Blocked** on #45 (H02), #46/#47/#49/#50 (H04) and #34 (H05). | Run regimes I/II now with `--skip-blocked`? |
| H39 | Adopt with changes. V4 state-space criteria added. `check()` flags family only. | Do behavior states count as a different modality from activity timing? Promote C1v-r1b to primary (needs a dated amendment)? |
| H41 | Adopt with changes, **after the room-index re-run** (holdout item 21). | Approve the fix (already patched in exploration code) and add H41 to `holdout_ledger.json` |

**Cross-cutting:** the ledger's estimator-family tags block several scripts on family alone (item 6's human pass is pending). Re-tag the ledger, or rule case by case.

## Standing decisions (from earlier)
- **First confirmatory runs:** H40 on NE20 (cadence; frozen and dry-run) and H08 (read-out gating).
- **Re-runs of executed holdout tests** on the fixed tables: H02 (#45), H04 (NE21+NE23 C2/C4/MF-C), H05 (NE12 C3). Each needs a pre-registration amendment.
- **H23 amendment:** exclude agent 30's messages before 2026-06-01 17:15:40 UTC (holdout item 14).
- **H41:** fix C4 (holdout item 16) before any run.
