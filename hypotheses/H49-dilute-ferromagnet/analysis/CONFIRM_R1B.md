# H49 confirm re-freeze (r1b), 2026-10-04: prepared, NOT RUN

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. No holdout data was read. Vivian's sign-off is needed.

## What changed
- **Inputs.** The loader now reads `activity_bins_fixed` and `outages_fixed/{reasons,stall_minutes}`. `confirm.py` read the buggy `activity_bins`, `reasons` and `stall_minutes`, although round 1 ran on the fixed tables (Amendment 2). Holdout ledger item 17.
- **Inputs left alone.**
  - The scheduler is removed by H38's conditioning (PL-c), which `infra/README.md` accepts in place of the DQ8 trim.
  - `infra_err` comes from `turn_errors` platform classes, not `actions.error`.
  - Content, visibility, work and nudge targets are not inputs.
- **Predictions.** C1–C6 and their thresholds are unchanged. They were frozen on the fixed-bin exploration, so only the loader was wrong. No `-r1b` labels.
- **Guards added.**
  - A commit check (reuse policy item 1).
  - A holdout-ledger gate. A target with a same-family, same-modality prior run is excluded by default. `--include-ledger-blocked` overrides this.

## Holdout reuse collisions (`holdout_ledger.check`, family = Curie–Weiss gain + pairwise couplings, activity timing)
- **Blocked:**
  - #45 (45a, 45b): H02 ran Curie–Weiss and pairwise couplings there.
  - #47 and #49: H04 ran MF coupling in NE21+NE23.
  - In all three the modality is the same (activity). `confirm.py` claimed "nobody looked at conditioned bonds"; the ledger's family rule does not accept that.
- **Allowed, disclosure needed:**
  - 51m (#51 tail). Planned competitors: H03, H08, H12, H13, H15, H19, H22, H30.
  - Regime-I 14, 15b, 22a, 22b. Planned competitors: H02, H03, H19, H25, H38.
- **Consequence.** Without the override, regime III holds only 51m. C1–C4 then rest on one unit, and C3 is undefined unless 51m's excess z > 2.

## Dry run (stand-ins, `data/processed/H49-dilute-ferromagnet/confirm_r1b_dryrun/results.json`)
- **Setup.** Stand-ins: regime III 39, 41, 42b, 51h (head 51f, 51g); regime I 17, 23, 26. 200 surrogates and 200 bootstraps; 390 s. It ran clean.
- **Results.** C1 pass (median 0.018; 2.75 bonds per unit). C2 pass (loss 0.50 in III vs 0.20 in I). C3 fail (excess units 41, CV 0.38; 51h, 0.19). C4 pass. C5 pass (r 0.11). C6 pass (OR 0.73).
- **The corrected loader moves stand-in numbers** vs the old dry run: #41 z_g 0.92 → 3.17; 51h CV-C10 0.05 → 0.19; 42b positive bonds 0 → 2. They now match the fixed-bin exploration (#41 z_g 2.83, CV 0.37).
- **Why C3 fails here.** It fails only because the stand-in set has two excess units and #41 is the outlier. Over the 10 fixed-bin exploratory excess units, 9/10 have CV ≤ 0.25 and none ≥ 0.5. The threshold stays.

**Recommendation: adopt.** Vivian must rule on the #45/#47/#49 ledger collision first: override, or accept a one-unit regime-III test.
