# H26 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm.py` (unchanged). Same targets: #46, #47 (primary), #45 (content only). Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs:** Activity: `activity_bins_fixed`, trimmed to each day's all-present window (DQ8). The outage proxy is recomputed on it. Content: statement vectors in **both models**, whitened with H01's round-1b regime-III basis per model. Dedupe uses DQ5's own-model restatement flags. Static field: shared goal fields (goal plus room kickoffs; now available for held-out goals) plus first-hour PCs. Round 1 substituted kickoff-day exogenous directions. Exogenous directions are built in each model's basis. Rooms still use the broadcast rule. The work ledger, failures and nudge targets are not inputs.
- **Predictions:** **C1-r1b** = C1 in both models. **C2-r1b** replaces C2. The gap is now real: w30 Δg_ca against trimmed activity is > 0 in #46 and #47, and > 0.15 in at least one. **C2t-r1b** (new): R2 against talk, Δg_ck ≤ 0.15 in at least one target. **C3-r1b** replaces C3: ρ_c(activity) − ρ_c(content) < 0.2 in both targets. C4 and C5 are unchanged and must hold in both models.
- **Ledger gate (new):** C2-r1b, C2t-r1b and C3-r1b are skipped under `--confirm` unless `--vivian-approved-activity-reuse` is passed.

## Why
- Round 1b withdrew the activity side of round 1: activity cross-room ρ_c fell from 0.79 to −0.05 (event-drop artifact); Δg_ca at w30 is now +0.41/+0.42 (+0.22 after trimming), 9/10 units; so the frozen C2 ("no gap") and C3 ("activity is global") predicted the artifact.
- Content g_ex is unchanged (0.52 bge / 0.47 gte).
- Holdout item 3: equal-time activity and talk gains on #46/#47 are the Curie–Weiss family of H04's executed NE21+NE23 run, so they are blocked under the reuse policy.

## Holdout reuse (ledger)
- **Content (C1, C4, C5):** allowed. Prior runs on these targets are other-modality: H02 on #45, H04 on #45–#47 and NE21+NE23.
- **Activity/talk side:** blocked on #46/#47 (same family as H04's run). This needs Vivian's override, or it is dropped.
- **Planned content users** of #45–#47: H12, H13, H16, H20, H23, H29, H30, H31, H33, H36, H39.
- Disclose in the H26, H02, H04 and H23 cards and in `LOG.md`.

## Dry run (stand-ins #41, #42, #44; no holdout day touched, asserted)
- Runs end to end in both models.
- Reproduces round-1b explore: content g_ex matches exactly (#41 day 0.767, w30 0.727; #44 0.764 / 0.716). Trimmed activity w30 is within 0.03.
- Per-model pass, bge / gte: C1 fail (median 0.764 > 0.75) / pass; C2-r1b fail (gaps +0.14, +0.07) / fail (+0.17, −0.03); C2t-r1b pass / pass; C3-r1b pass / pass; C4 pass / pass; C5 pass / fail.
- Output: `data/processed/H26-content-near-critical/confirm_r1b_dryrun/confirm.json`.

## Recommendation
**Adopt with changes.** The content criteria are ready. Vivian must decide whether the activity/talk criteria may reuse #46/#47 after H04's run. If not, H26's channel-gap claim has no holdout target left.
