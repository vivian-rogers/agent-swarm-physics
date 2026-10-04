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

## Standing decisions (from earlier)
- **First confirmatory runs:** H40 on NE20 (cadence; frozen and dry-run) and H08 (read-out gating).
- **Re-runs of executed holdout tests** on the fixed tables: H02 (#45), H04 (NE21+NE23 C2/C4/MF-C), H05 (NE12 C3). Each needs a pre-registration amendment.
- **H23 amendment:** exclude agent 30's messages before 2026-06-01 17:15:40 UTC (holdout item 14).
- **H41:** fix C4 (holdout item 16) before any run.
