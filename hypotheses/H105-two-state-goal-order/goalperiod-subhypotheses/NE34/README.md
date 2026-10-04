# H105 × NE34: two-state goal order across kickoff transitions (cross-kickoff tests)

**Verdict:** mixed
**Role:** replication
**Period:** the three primary free → assigned pairs (#11 → #12a, #16 → #17, #37 → #38a), two secondary pairs (#3 → #4a, #5 → #6a; N = 4) and 16 eligible kickoff transitions (same regime, A's first unit has ≥ 2 days after day 1). Regimes I and III. Per-design estimates only; never one pooled fit (exception (c): the transition is the object).

## Why this period
HH130 names the pairs and the kickoffs (NE34). The cross-transition comparison of variance growth (P6) needs many transitions.

## Prediction
*Written 2026-10-04 ~20:27 UTC in the card (P1–P7); Amendment 1 (~20:51 UTC, before real data) demoted P1 and P3 to descriptive and made P2 calibrated. Restated rule: failed if the calibrated P2 fails in ≥ 2/3 pairs; mixed if it is supported in ≥ 2/3; inconclusive otherwise. (The overview has no "inconclusive" value; this folder is marked mixed and the card states "inconclusive".)*

## Result
| Test | Observed | Verdict |
| --- | --- | --- |
| P1 tilt variance (descriptive) | ρ_V = −0.71, +0.53, −2.45 (bge); rule outcomes failed / failed / inconclusive; gte +1.28, −0.02, −3.04. Calibrated quantiles in H: 0.25, 0.57, 0.00 | not identifiable; #38a far below the tilt |
| P2 logit shift (calibrated) | s = −0.60, +0.38, +2.53; inconclusive in 3/3 (H and R2 bands overlap) | inconclusive |
| P3 Δg₂ (descriptive) | +0.64, +0.26, +0.03; #12a g₂ 0.10 → 0.74 | not identifiable |
| P4 transverse | median p⊥ 0.024 → 0.008, 0.024 → 0.022, 0.027 → 0.022; median ρ_V⊥ −0.07, −0.03, +0.04 | supported |
| P5 day trajectory | #17: observed V_d is 1.0–2.5× the prediction (above it on 3/4 days); #12a below it on 3/3 days (0.4–0.6×), #38a on 6/7 days (0.04–1.4×) | failed (no pooled Spearman run; per-day ratios scatter) |
| P6 kickoffs | \|ρ_V\| < ln 1.5 in 7/16 (0.44; needed ≥ ½); Spearman(observed, predicted growth) = 0.86 (p 0.0003, n = 16) | first part failed, second supported |
| P7 day-mean removal | moves ρ_V away from 0 (#12a −0.71 → +3.17) | failed |

**Two-state picture, descriptive.** Along ĝ the on-goal occupancy rises from 0.02–0.05 (≈ the decoy rate) in free weeks to 0.23–0.44 in assigned weeks (always below ½). Its variance grows by ln 0.8–3.7 while the transverse occupancy stays at the decoy floor. Across 16 kickoffs the variance growth follows the two-state p(1 − p) scaling (ρ_s 0.86). The tilt's quantitative prediction with the free week's coupling is not identifiable: J₂ cannot be measured at p_F ≈ 0.03 with 24–30 windows.

Data: `data/processed/H105-two-state-goal-order/{replication.json, NE34/pairs_all_configs.parquet, NE34/kickoffs.parquet}`. Figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- C: transverse null passed; the tilt's variance prediction cannot be tested against R5 (synthetic).
- D: the variance growth with p(1 − p) is an unfitted scaling, but generic (any binary occupancy shows it).
- F: synthetic shows P1, P3 not identifiable and P2 biased (Amendment 1).

## Notes
- K04, K06, K12, K17, K38 are the same designs as the pairs.
