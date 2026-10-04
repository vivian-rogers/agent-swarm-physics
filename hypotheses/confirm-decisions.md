# Confirmatory decisions for Vivian

Status: **nothing has run on the holdout.** The re-frozen scripts (`analysis/confirm_r1b.py`, with notes in `analysis/CONFIRM_R1B.md`) were written beside the untouched originals and dry-run on non-holdout stand-ins only. Each script refuses to run unless it is committed and called with both confirm flags. This sheet collects every decision the re-freeze batches surfaced. All four batches (30 scripts) are in.

## Cross-cutting decisions (affect many scripts)
1. **The ledger's estimator-family tags.** Many scripts are blocked on targets that H02, H04 or H05's executed runs used: activity or talk spectra and kick responses on #32, #34, #45–#50. Either re-tag the ledger (holdout item 6's human pass), or rule case by case with the override flags. Without overrides:
   - H26's channel-gap claim has no held-out target;
   - H12's activity and talk claims rest on 3 units;
   - H30's activity claim has no clean target.
2. **The both-model rule.** Many r1b predictions now need both embedding models (bge and gte) to pass. When they disagree, a new outcome label, **model-dependent**, applies. Accept it?
3. **Reversed or new primaries written from round-1b exploration.** These need explicit approval:
   - H12 (C1 reversed, C1t, C2 threshold 0.7);
   - H26 (C2-r1b and C3-r1b reversed);
   - H19 (post-hoc k_llm model as primary);
   - H35 (C8-r1b);
   - H16 (C32-5-r1b);
   - H31 (C2-r1b rule choice).
4. **Frozen data files in gitignored `data/`.** These must not be rebuilt; the scripts hash-check them:
   - H19 `r1b/results_trim/frozen_kllm_model_r1b.json` plus the refit channel and P1 models;
   - H25 `r1b/results/frozen_confirm_r1b.json`;
   - H23's gte corpus cache in `G44/r1b/`.
5. **Disclosure lines.** Every run needs reuse disclosure lines in both cards and in LOG.md before it runs. Each script checks this.

## Batch A (H01, H08, H11, H12, H15, H18, H19, H23, H25, H26), re-frozen 2026-10-04
| Hyp | Recommendation | Your decision |
| --- | --- | --- |
| H01 | Adopt with changes: both models, a style variant, a new label "model-dependent"; drops P9. | Accept the both-model rule? |
| H08 | Adopt. Adds CF1b-r1b (reply author). Retires CF3 (round 1b reversed it; the kernel belongs to H04/H43). | Approve retiring CF3 |
| H11 | Adopt. Adds C4-r1b (work herding follows ownership, #45). C2 keeps the #35 contradiction disclosed. | none needed |
| H12 | Adopt with changes. C1 reversed, C1t new, C2 threshold 0.7, C3 retired. **Activity and talk blocked** except on #28, #29 and the #51 tail. | Approve the changes; override the activity reuse? |
| H15 | Adopt. Uses the re-chosen V*; the dip is measured on work commits. | Is C1 on NE30 acceptable? It shares a modality with H05's #34 run but measures a different statistic. |
| H18 | Adopt. No prediction changes (exponents moved ≤ 0.1). | none needed |
| H19 | Adopt with changes. New primary C1-r1b, post hoc but hash-locked. #32, #34 and #45 dropped. | Approve the post-hoc primary? |
| H23 | Adopt with changes. C0-r1b applies the agent-30 exclusion (item 14). | Approve item 14, then commit the card |
| H25 | Adopt with changes. Adds a gte agreement clause; Stage B re-frozen on the trimmed tables. | Accept the gte agreement clause, or order a gte exploratory run first? |
| H26 | Adopt with changes. C2/C3 reversed (the content–activity gap is real). **Activity and talk on #46/#47 blocked.** | Override the block, or the gap claim has no target |

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

## Batch D (H06, H13, H16, H24, H27), re-frozen 2026-10-04
| Hyp | Recommendation | Your decision |
| --- | --- | --- |
| H06 | Adopt. C2/C3 must hold in both models. New C5-r1b (work) and C6-r1b (copying) are secondary. | Keep or drop C5/C6-r1b (likely underpowered on a regime-I free week)? |
| H13 | Adopt with changes. Every C is scored per model; overall only when both models agree. Fixes the original's crash (item 22). | May C5-r1b's talk statistic be a second activity-modality use on #45–#50, or score it on the #51 tail only? |
| H16 | Adopt with changes. Real failures, leading-@, ledger recipients. New primary C32-5-r1b. **#45 kick-response family blocked** (H04). | Is the gate kick-odds statistic distinct from H04's kick response (`--reuse-ruling kick_response`)? Score the "no aging" predictions, which have no power check? |
| H24 | Adopt with changes. Shared ĝ with multi-direction removal, both models. New C4-r1b (reading DiD). | C4-r1b primary or secondary? (#14 has N = 6 and may yield few reading events.) |
| H27 | Adopt with changes. Ledger-timed links; new C6-r1b (work never leads attention). | Ruling on the overlap with H28's link statistic on #22/#28/#45; demote C5-r1b to secondary? |

## Standing decisions (from earlier)
- **First confirmatory runs:** H40 on NE20 (cadence; frozen and dry-run) and H08 (read-out gating).
- **Re-runs of executed holdout tests** on the fixed tables: H02 (#45), H04 (NE21+NE23 C2/C4/MF-C), H05 (NE12 C3). Each needs a pre-registration amendment.
- **H23 amendment:** exclude agent 30's messages before 2026-06-01 17:15:40 UTC (holdout item 14).
- **H41:** fix C4 (holdout item 16) before any run.
