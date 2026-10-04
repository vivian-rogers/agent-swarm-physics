# H34 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any held-out data was read. Not run on the holdout.

## What changed
- **Visibility.** DQ1 ledger (`H34_DATA=r1b`). A use is visible to agent j if it reached one of j's receiving calls no later than the call that produced j's use. This sets parents, lags, the at-risk sets (HR₁₀), the jitter null and the room contrast. The old rule was H18's call-start rule (Known issue 34).
- **Confirm-only change.** A copy of `ledger_arrays` without its exploration assertion, so that held-out calls can join.
- **C3-r1b.** The dilution fit is refitted on the round-1b non-holdout period table: b0 −2.232, b1 −0.663, s 0.367 (was −2.547, −0.549, 0.380).
- **C4-r1b.** Forecast drift σ_η = 0.245 (was 0.254), as the leave-one-period-out median on round-1b trees.
- **Method check.** The same code on round-1 tables reproduces the original constants exactly (σ_η 0.253 vs 0.254 frozen).
- **C7-r1b (new; H57 placebo).** HR_seen5 > HR_unread5 in ≥ 3 of 4 targets.
- **Unchanged.** C1, C2, C5 and C6, the targets, the stand-ins and the marker rule.
- **Sealing.** Into `results/confirm_r1b_sealed.json`.
- **Inputs not applicable.** Activity bins, outages, embeddings (ideas are hashed markers, so the two-model rule does not apply), work and failures are not inputs.

## Why
- Ledger item 15 / RE-D1: re-freeze on ledger visibility.
- The ledger changed R̂ and HR₁₀: the regime-I median goes 2.3 → 6.4. The frozen C3 fit and σ_η came from the old trees.
- STANDARDS §1: the in-flight placebo. Round 1b: seen > unread in 30/32 periods; unread carries about 56%.

## Holdout reuse (ledger L212–L215)
- No prior run on the #51 tail, #15, #22 or #28.
- Planned users of the same family:
  - tail: H08, H18, H29, H37, H39;
  - #22: H11, H28;
  - #28: H08, H11, H18, H28.
- The novelty contamination across held-out periods is unchanged and disclosed.

## Dry run (#51 08-24..09-05, #13, #25, #16)
- Executes end to end. Ledger fallback share 0 in every unit.
- All criteria pass: C1, C2, C3-r1b, C4-r1b, C5, C6 and C7-r1b.
- R̂: 0.23 / 0.15 / 0.22 / 0.10.
- HR₁₀ lower CI: 12.2 / 3.0 / 6.2 / 2.3. In the original dry run T4 was 0.56 and passed C2 by 3/4.
- HR_seen5 vs HR_unread5: 21.9 vs 4.8, 3.3 vs 2.8, 6.9 vs 3.1, 5.1 vs 4.2.
- Forecast coverage: P(s ≥ 2) 0.69, P(s ≥ 3) 0.77 over 26 days.

## Recommendation
**Adopt.**
