# H31 confirm re-freeze (r1b), 2026-10-04: prepared, NOT RUN

`confirm_r1b.py` replaces `confirm_holdout.py` and `frozen_rule.json` (both untouched) for any holdout run. No holdout data was read. Vivian's sign-off is needed.

## What changed
- **Inputs.**
  - Visibility and timing come from the DQ1 context ledger: a read happens at the receiving call's `t_call`, and the update at its first record. This is the round-1b `--visibility ledger` build.
  - Project states come from the shared deterministic `project_states` (W 30). The old path was H11's labels rebuilt with the tie-breaking bug.
  - E-C alignment comes from DQ5 white32 vectors under bge **and** gte. Round-1 bge is reported.
  - Activity, outages, failures and leading-@ are not inputs. λ₂^ment is in no criterion.
- **Frozen rule.** It is the round-1b exploratory rule (`r1b/frozen_rule.json`, sha aaf6d323…), with its values embedded in the script. The frozen forecast protocol now picks **M_ul2_rw** (log-RMSE 1.049 vs constant 1.075). Round 1 picked the constant.
- **Predictions.**
  - **C1-r1b:** slope-1 λ₂ rule vs constant, with intercepts refit on round-1b data (4.625 / 1.274). Credence 0.25.
  - **C1b-r1b:** free slope b 0.376.
  - **C2-r1b:** ≥ 70% of target events inside the M_ul2_rw 80% interval. Credence 0.5.
  - **C2b-r1b (new):** M_ul2_rw beats the constant.
  - **C3-r1b (new):** ≤ 1 E-C convergence event per model. The old C3 was always n/a, because no content rule was ever frozen. Rounds 1 and 1b found 0 of 35 blocks converging.
  - **Reported only:** the constant rule's interval coverage.
- **Guards.** Both flags are still required; the commit check is kept; a ledger gate is added.

## Holdout reuse collisions (ledger L188–L196)
- **No target is blocked.** #46, #47, #50 (E-P) and #49 (E-C) lie in NE21+NE23, where H04 ran activity timing (another modality).
- **Planned same-family users (project_potts):** H27 on #29, #46, #47, #50; H01 on #46, #47, #50.
- **E-C content users:** H12, H13, H20, H26, H30, H33, H36 and H39. Disclose in both cards and LOG.md.

## Dry run (`data/processed/H31-consensus-time-spectral-gap/confirm_r1b_dryrun/`, 147 s)
- **Setup.** Stand-ins #30, #41, #42, #44 (+ #39 for E-C), built through the same in-memory path.
- **Reproduction checks pass:** shared labels equal H11's round-1b label files in all 5 periods; consensus events equal the round-1b exploration (9 events, 3 frozen).
- **E-P (6 uncensored events):**
  - C1-r1b fails: RMSE 1.50 vs 1.04.
  - C1b-r1b fails: 1.17.
  - C2-r1b fails: 4/6 events inside.
  - C2b-r1b fails: 1.40 vs 1.04.
  - The constant's coverage is also 4/6.
- **E-C:** 0 convergence under both models (5/4 divergences), so C3-r1b passes.
- **Reading.** With 6 in-sample events these results check the code path only. No threshold was tuned to them.

**Recommendation: adopt with changes.** Vivian should decide whether C2-r1b keeps the protocol's M_ul2_rw pick. It won by only 2.4% (noise) and does worse than the constant on the stand-ins. The alternative is to declare the constant the operator rule before the run.
