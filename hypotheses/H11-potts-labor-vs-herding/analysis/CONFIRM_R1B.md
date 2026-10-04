# H11 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm_holdout.py` (unchanged). It imports `confirm_holdout.py`'s FROZEN dict, `run_target`, `verdict` and `overall`, and `scheme/build_r1b.py`'s label builders. Targets are unchanged: #22 (FM-free), #28 (AF), #45 (AF). Stand-ins are unchanged: #31, #25, #38. Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs:** Attention labels come from the shared deterministic `project_states` (W = 30). Round 1 used H11's own files, whose tie-break was not reproducible. Action classes use the deterministic tie-break. New work state from the DQ4 work ledger (agent commits, automated streams excluded). Labels are built in memory. Held-out rows are admitted only under `--confirm`. activity_bins, embeddings, ledger visibility, failures and nudge targets are not inputs of this design.
- **Predictions:** C1, C2 and C3 are unchanged (frozen rules imported). **C4-r1b** (new, from R1b-2a/c): work-space herding follows ownership. Work ownership < 0.5: βJ_CW(work) > 0 with |t| > t_crit and z_N2(work) ≥ 2; ownership ≥ 0.5: z_N2(work) < 2. Applies only to targets with ≥ 15 work blocks (in practice #45).
- **Disclosure:** ledger item 11 is recorded in the output. #35 contradicts C2's frozen clause in exploration (z_N2 attention −2.5).
- **Ledger:** `holdout_ledger.check()` is now called. The original did not call it.

## Why
- **Ties:** H11's labels were not bit-reproducible (about 1% of labels flipped between rebuilds). Round 1b moved 8% of labels, mostly by renumbering, and changed no verdict category.
- **Work state:** round 1b found work herds in 4/6 shared-artifact weeks and spreads in 3/3 own-artifact weeks. This is the attention result carried into an independent output channel, and it is new in round 1b.

## Holdout reuse (ledger)
- **#45:** H02 and H04 ran there, in another modality; allowed with disclosure.
- **#22, #28:** no executed run.
- **Planned same-family users:** project/herding: H27 (#22, #28, #45), H01 (#45 crews); lineage: H06, H28, H15, H23; addressing: H08, H18, H28, H34.
- Disclose in the H11, H02 and H04 cards and in `LOG.md`.

## Dry run (stand-ins; 49 nulls)
- Runs end to end. The label builder reproduces `r1b/G<NN>` exactly: 9/9 files (project, action, work × 3 stand-ins).
- Attention results equal the original dry run within Monte Carlo noise: #31: C1/C2/C3 pass (βJ_CW +4.88, z_N2 +14.3). #25: C1 fails. #38: C1 and C2 fail (z_N2 +2.18, local +1.29). Overall: "C1 not confirmed; C2 inconclusive; C3 holds", as before.
- C4-r1b: #31 pass (z_N2 work +5.8); #25 n/a (0 work blocks); #38 pass (z +2.34).
- Output: `data/processed/H11-potts-labor-vs-herding/confirm_r1b_dryrun/confirm_results.json`.

## Recommendation
**Adopt.** Inputs are switched and the frozen rules are untouched. C4-r1b adds a real work-channel test on #45. Disclose the #35 contradiction before running.
