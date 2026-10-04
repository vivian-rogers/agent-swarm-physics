# H51 × NE14: the regime II → III switch inside #36 (36a → 36b, 36c)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** goal #36 · 36a regime II (03-23) → 36b, 36c regime III (03-24 → 03-27) · N ≈ 12 · rooms #best/#rest · same goal and roster on both sides.

## Why this period
The read-out coupling switches on at fixed goal, roster and N: H67 measures g_lag −0.06 [−0.15, 0.03] in 36a and 0.12 [0.06, 0.17] in 36b ∪ 36c. That is the largest within-period step in K in the non-holdout record, so it is a quasi-intervention on the dial. The rival explanation is the scaffold bundle itself (consolidation every ~40 actions, perma-computer-use), which changes loops and context independently of K.

## Prediction
*Written 2026-10-04 20:45 UTC, before running on this NE.*
- **One-dial prediction (D1):** each observable changes by b_j·ΔK, with b_j the across-period slope of Y_j on g_lag fitted on all other periods (#36 excluded) and ΔK = g_lag(36b ∪ 36c) − g_lag(36a). Observables available at sub-unit level: idea branching R̂ and loop rate (restatement share). Settling time and herding share are not defined for these sub-units.
- **Expected (card P1 reading):** the observed shifts are dominated by the scaffold change, not by K. Loop rate moves by more than the D1-predicted amount (|observed Δ| outside the D1 95% prediction band) with credence 0.6; R̂ moves in the D1-predicted direction with credence 0.5.
- **Counts for the dial:** both observables shift in the D1-predicted direction and inside its 95% band.
- **Null:** sub-unit day-block bootstrap of the observed shift; placebo split inside 36b ∪ 36c (03-24/25 vs 03-26/27), which has no K step.

## Result
*Run 2026-10-04 ~22:10 UTC (exploratory). Data: `data/processed/H51-one-dial-collapse/natives/NE14.json`.*
ΔK = g_lag(36b ∪ 36c) − g_lag(36a) = 0.122 − (−0.060) = **+0.183**. Slopes b_j are fitted across 30–32 other periods (#36 excluded). Observed shifts are on the logit scale, with a day-block bootstrap (2,000 draws; 36a is one day, so the CI comes from the 36b ∪ 36c days).

| Observable | D1 prediction b·ΔK [95%] | Observed Δ [95%] | Placebo 36b → 36c (no K step) | Reading |
| --- | --- | --- | --- | --- |
| loop rate (logit) | −1.53 [−2.36, −0.69] | −0.12 [−4.40, +0.74] | +1.32 [−4.23, +5.41] | sign agrees; point shift 13× smaller than D1 predicts; CI too wide to exclude it |
| idea branching (logit R̂) | −0.24 [−0.70, +0.21] | −0.18 [−0.46, +0.03] | **+0.41 [+0.15, +0.65]** | sign agrees, but a day-to-day shift with no K step is larger |
| herding share | −0.067 [−0.18, +0.05] | +0.030 (point) | – | opposite sign; no CI |

- **Expected (written before):** loop rate moves *more* than D1 predicts (credence 0.6): **not seen**; the loop rate barely moves (36a 0.8%, 36b 0.3%, 36c 1.2%). R̂ moves in the D1 direction (0.5): **seen**, but the no-step placebo moves R̂ by more.
- **Reading:** the largest within-period step in K on record does not produce the shifts the across-period D1 slope implies. The D1 slope for loops (−8.3 logits per unit g) is a regime-I-vs-III era contrast, not a response to the coupling: at a fixed goal and roster, switching the coupling on leaves the loop rate where it was. Low power (one regime-II day) keeps this at *mixed*, not *failed*.

## Scorecard (period-specific axes)
E: 0 (the dial does not predict the NE14 shifts beyond sign; the no-step placebo is larger than the step shift for R̂).
