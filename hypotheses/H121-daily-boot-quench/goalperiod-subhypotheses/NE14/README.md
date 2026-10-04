# H121 × NE14: the regime II → III boundary inside the #35–#36 fortnight (2026-03-16 → 03-27)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime II (#35, unit 35, and 36a: 6 days) → regime III (36b ∪ 36c: 4 days) · N = 12, fixed roster · rooms #best/#rest. Splits: NE14 (perma-computer-use, 03-24), NE16 (03-26).

## Why this period
The boot changes nature at fixed roster: session starts in chat/computer-use sessions (regime II) become the runner's daily start of continuous computer use (regime III). H67 found the read-out gain switches on across this boundary (36a −0.06 [−0.15, 0.03] → 36b ∪ 36c 0.12 [0.06, 0.17]) while the call interval barely moves (13.7 → 12.0 s).

## Prediction
*Written 2026-10-04 22:08 UTC, before running on this period.*
- **Mean field (H121's model):** τ_boot/τ₀ rises by (1 − g_II)/(1 − g_III) ≈ 1.06/0.88 ≈ ×1.2 across the boundary, and K_boot stays in [0.5, 2] on both sides.
- **Expected instead (credence 0.65):** τ_boot in calls changes by more than ×1.5 (either direction) across the boundary, beyond the mean-field ×1.2: the scaffold's start-up routine, not the coupling, sets the boot. K_boot > 2 on both sides (credence 0.6).
- Counts against the expectation: |ln(τ_III/τ_II)| < ln 1.25 with K_boot in [0.5, 2] on both sides.
- Descriptive if either side has < 8 eligible agent-days or τ_boot is unresolved (CI spans > ×10).

## Result
*Registered estimator (single exponential, day-cluster bootstrap).* Regime-II side (#35 ∪ 36a, 72 agent-days): τ_boot = 0.90 [0.42, 1.38] calls, K_boot = 0.91 [0.41, 1.36]. Regime-III side (36b ∪ 36c, 48 agent-days): the fit sits at the upper bound (τ = 2000 calls, CI [0.2, 2000]): unresolved. The ratio τ_III/τ_II is therefore uninformative (CI [0.2, 3300]). Neither the mean-field ×1.2 nor the expected > ×1.5 change can be scored: **mixed**.

*Post hoc (labelled; card "Post hoc")*: the ratio estimator on the first-call spike gives τ_fast = 0.90 [0.40, 2.15] calls (II) and 0.90 [0, 2.66] calls (III). The relaxation time does not change across the boundary. The spike *amplitude* falls ×0.14 (excess at k = 0: 0.45 → 0.06). The scaffold changes how much the first call talks, not how fast the next calls relax. This is consistent with a call-clock relaxation of about one update on both sides.

Data: `data/processed/H121-daily-boot-quench/results/natives.json`, `posthoc.json`.

## Scorecard (period-specific axes)
E (prediction across a natural experiment).

## Notes
- The goal changes (#35 → #36) one day before the regime boundary; the regime-II side pools #35 and 36a.
