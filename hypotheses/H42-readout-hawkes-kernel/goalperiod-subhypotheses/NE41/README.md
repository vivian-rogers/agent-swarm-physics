# H42 × NE41: Does a forced context erasure cut the read-out kernel's tail?

**Verdict:** failed (R_forced = 3.1 ± 2.5: no evidence that a forced erasure cuts the read-out tail; poorly identified)
**Role:** native (exploratory, non-holdout; regime-III units, turn-level design)
**Period:** NE41 (forced consolidation at the 41-turn cap, regime III from 2026-03-24). Units: every eligible non-holdout regime-III unit (#36b–#44b, #51a–#51l). Named exception (c): the transition (a reset between read-out and response) is the object; fits are per unit, then pooled as a ratio of sums.

## Why this period
The read-out kernel says j's message excites i at the call that reads it and, more weakly, at i's next few calls (B's tail in call-index units). If that tail lives in i's context window, a forced reset between the read-out call and a later call must remove it. Forced resets happen when a segment reaches 41 records, a counter, not a content decision, so their timing relative to any message is quasi-random. That makes NE41 an intervention on the kernel's tail inside every regime-III unit. Voluntary consolidations are agent-chosen and reported only as a contrast.

## Prediction
*Written 2026-10-04 07:45 UTC, before running this test. No erasure-split fit has been computed. The smoke fits of #38a and #51c (world B) showed B's tail (calls m ≥ 1) at roughly a quarter to a third of B's mass, so power may be limited.*
- **N1a (primary):** the surviving fraction of tail excitation after a forced reset, R_forced = Σ_b w_forced,b Z_forced,b / Σ_b w_intact,b Z_forced,b (matched on m-bins {1}, {2–3}, {4–15}), is ≤ 0.5 pooled over units, with the jackknife 95% upper bound < 1.
- **N1b:** voluntary consolidations also cut the tail (R_vol < 1), less cleanly identified.
- **Counts against:** R_forced ≥ 1, or point ≥ 0.8 with a CI including 1. If the pooled denominator (excitation that intact weights would give forced item-calls) is below 5 expected talk events, the test is **inconclusive** (underpowered), not failed.
- **Context:** H08 found forced erasure cuts the chance of addressing senders read before it by only 18% (predicted ≥ 30%), so a partial cut is plausible.

## Result
Pooled over 27 regime-III units (world B, class baselines):

| statistic | observed | prediction | verdict |
| --- | --- | --- | --- |
| N1a surviving tail fraction after a forced reset, R_forced | 3.07 (jackknife SE 2.53); pooled denominator 11.2 expected talk events | ≤ 0.5, upper bound < 1 | **failed** (counts-against R ≥ 1 met; CI covers 0 to about 8) |
| N1b voluntary consolidations, R_vol | 1.11 (SE 1.14); denominator 17.2 | < 1 | not supported (null) |
| intact tail mass relative to the read-out call (m ≥ 1 vs m = 0) | 0.56 | (context) | the tail is about a third of B's mass in this split model |

- **Per unit:** the forced-tail weight is exactly 0 in 10 units. In the others it is driven by a handful of item-calls; the per-unit ratios run from 0 to more than 10⁵ where the intact weight is ~0. The pooled ratio of sums is the only stable summary, and it is not small.
- **Reading:** no evidence that a forced context erasure removes the read-out kernel's tail. Either the tail does not live in the context window (summaries and memory carry it), or, more likely, the tail weights are not identified at these counts: talk excitation in the call-clock world is ≈ 0.01–0.05 per message in regime III, and the tail is a fraction of that.
- **Agreement with H08:** H08 found erasure cuts *addressing* by only 18%. Talk timing is an even weaker channel.

Data: `data/processed/H42-readout-hawkes-kernel/NE41/ne41.parquet`, `ne41_summary.json`.

## Notes
- Design: world-B (call-clock) TALK model with class baselines; B_0 at the read-out call; tail columns split by context status between read-out and the current call; a gated "post-reset" call term absorbs any talk burst at the first call after a consolidation. Script: `analysis/native_ne41.py`. Data: `data/processed/H42-readout-hawkes-kernel/NE41/`.
