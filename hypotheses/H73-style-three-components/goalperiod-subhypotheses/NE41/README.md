# H73 × NE41: forced context erasure at the 41-turn cap (regime III, non-holdout units)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III units #36b–#51 (non-holdout days); turn level.

## Why this period
The scaffold erases the context at a fixed record count, not when the agent chooses. That is the cleanest exogenous intervention on the context component.

## Prediction
*Written 2026-10-04 19:28 UTC, before running on these data.*
- **Design:** consecutive eligible chat messages of one agent on one PT day in regime III (non-holdout), labelled forced / voluntary / within by the resets between their producing calls (DQ1 ledger flags). The context profile (bin levels and agent slopes on z = log2(1 + fill)) is fitted on within pairs of one day parity and evaluated on the other (Amendment A1).
- **N1 prediction:** the fitted drift predicts the forced-erasure jump: β ∈ [0.3, 1.5] with the agent-cluster CI excluding 0. Subtracting the predicted jump lowers the gap-matched forced-pair style percentile T_s by at least half of its excess over ½.
- **Expected:** β around 0.3–0.6 (part drift, part excursion); T_s raw about 0.55–0.57 (H46: 0.564).
- *Counts against:* β CI including 0, which means the erasure effect is not the reversal of a directed drift (R5, the directionless excursion; synthetic S2 gives T_s 0.556 with β ≈ 0).

## Result
*Run 2026-10-04 19:46 UTC (`analysis/natives.py` → `data/processed/H73-style-three-components/natives/natives.json`).*

- **Pairs** (regime III, non-holdout, copies removed): forced 7,640, other 3,938, voluntary 7,302, within 32,583.
- **Forced erasures:** β = 0.27 [0.12, 0.36] (agent-cluster bootstrap; 7,640 pairs). Predicted jump ‖Δx̂‖² = 0.344 vs observed ‖Δx‖² = 19.74 (17-d units).
- **Voluntary consolidations:** β = 0.47 [-0.03, 0.78] (7,302 pairs).
- **Gap-matched style percentile of forced pairs:** T_s raw 0.567 [0.533, 0.595] → after removing the predicted jump 0.568 [0.542, 0.597] (H46: 0.564).
- **Per goal (forced β, descriptive):** CI above 0 in 2/9 goals; G36 -0.07; G37 -0.12; G38 0.11; G39 -0.12; G40 -0.08; G41 0.06; G42 0.02; G44 -0.09; G51 0.23.
- **Restatements removed (either model):** forced β = 0.26 [0.12, 0.34].
- **Verdict rule (fixed in the card, 19:13 UTC):** β ∈ [0.3, 1.5] with CI > 0 and the T_s excess at least halved → supported; β CI including 0 → failed; otherwise mixed. **Verdict: mixed.**

## Scorecard (period-specific axes)
- **E (interventional):** the scaffold-timed erasure is the intervention; the drift fitted inside segments does not predict the erasure jump in the stated range.
- **D (unfitted):** β is an out-of-fold, unfitted statistic (Amendment A1).
- **H (rivals):** R5 (directionless excursion) predicts β ≈ 0 with T_s ≈ 0.556 (synthetic S2).

## Round 2 (2026-10-05)
**Round-2 result:** pending.
*Prediction written 2026-10-05 05:07 UTC, before the real round-2 run (card pre-registration 04:46 UTC).*
- **C0 (correction, not a test):** round 1's forced-erasure T_s (0.567) recomputed with H46's agent × unit scaling (R2-A5); expected ≈ 0.55.
- **R2-3, regime III (seen sample; H46 found the reset-and-hold shape here post hoc):** new statistics only. Carry-over ρ_carry < 0.3 (the offset is redrawn at each reset, not carried), and κ_seg ∈ [0.02, 0.10].
