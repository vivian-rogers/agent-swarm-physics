# H43 × NE43: the nudger goes silent inside #51 (before 2026-07-06 → 08-20, after 08-21 → 09-04)

**Verdict:** failed
**Role:** native
**Period:** regime III · #51 (private-role era) · 21–32 agents · rooms {#general, #focus} until 08-21, {#general} from 08-24 · before: 34 non-holdout days (units 51a–51g1), after: 11 days (51g2–51l; the #51 tail from 09-07 is held out). Exception (c): the transition is the object. `period_units` predates NE43, so unit 51g is split at 08-21 here.

## Why this period
The only place where the dose-spacing data exist and then vanish. Before 08-21 the nudger re-fires on idle agents (hard floor ~15 min between nudges, median ~30 min): 302 isolated nudge primers and 196 second nudges within 4 h. From 08-21 the `automated` speaker is silent (no nudges, no daily bookends). Three tests use this:
1. **(P6a) Nudge spacing curve, before:** E2(δ)/E1 for second nudges at δ ∈ (15, 60] and (60, 240] min, on sustained escape (O1, idle recipients).
2. **(P6b) Swarm-level prediction of the switch-off:** the per-kick estimates predict how much sustained escape per idle minute should drop when nudges stop. Two accountings: *additive*, where every nudge contributes the first-kick excess E1 (risk difference); *refractory*, where re-fires contribute the measured second-kick excess for their spacing. Observed: the day-matched change, the last 11 days before vs the 11 days after. Null: the same statistic at every within-#51 split before the switch (placebo band).
3. **(P7) Invariance:** the mention curve (A, busy recipients, O2) on both sides. Refractoriness should be a property of the recipient, not of the nudger.

Confounds that cannot be removed: the room change on 08-24 (two rooms → one), roster growth after 08-28, and the loss of the daily bookends. The swarm-level comparison is therefore read against the placebo band and against the size of the prediction, not as a clean causal estimate.

## Prediction
*Written 2026-10-04, before running on this period (card P6, P7).*
- **P6a:** R(15–60 min) ≤ 0.5 with the upper CI < 1, and R(60–240) ≥ 0.7. Synthetic caveat: the null band for this statistic at G51 size is 0.53–1.10 (median 0.77), so only R below ~0.5 is distinguishable from no refractoriness.
- **P6b:** the refractory prediction is closer to the observed change than the additive one. Both predictions are much smaller in magnitude than the observed day-matched drop (H39: about −13% idle escape): the nudger's direct per-kick effects do not explain the swarm change.
- **P7:** |R_after − R_before| < 0.3 in every powered spacing range ((0, 15], (15, 60] min) for mentions on O2.
- **Against:** R(15–60) ≥ 0.7 (re-fires work as well as first nudges); the additive accounting closer to the observed change; mention curves that differ by more than 0.3 across the switch.

## Result
Run 2026-10-04 with `analysis/run_native.py --test NE43` (B = 300); numbers in `data/processed/H43-kick-refractory-window/native/NE43.json`. Before: 34 days; after: 11 days. Effects are pooled log hazard ratios (lnHR); R = E2/E1.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P6a nudge window: R(15–60) ≤ 0.5, R(60–240) ≥ 0.7 (O1, sustained escape) | **No first-nudge effect on sustained escape:** E1 = 0.07 [−0.13, 0.27] (259 idle primers), so R is undefined (R(15–60) = 1.23 [−0.66, 5.90], 110 second nudges). *Post hoc (O1a, any activity counts):* E1 = 0.56 [0.37, 0.75] (≈ H39's ×1.5), R(15–60) = **1.28 [0.66, 1.94]**, R(60–240) = 1.09 [0.53, 1.92]. Re-fired nudges work at least as well as first ones | **failed** (untestable as pre-registered; contradicted post hoc) |
| P6b swarm prediction: refractory accounting closer than additive; both ≪ the observed drop | Observed day-matched change in sustained escapes per idle minute: **−17.3% [−24.5, −8.8]**. Placebo band (13 within-#51 splits before the switch): [−18.8%, +10.2%]. Predicted: additive −0.2%, refractory −0.5% (O1); O1a: −0.6% / −1.0%. "Refractory" is closer, but only because re-fires add *more* escape than first nudges (second-nudge excess 0.11–0.14 vs 0.04 for the first, O1) | met by the letter, contradicted in substance; the nudger's direct effects explain 1–6% of the drop, and the drop is at the edge of the placebo band |
| P7 mention curve invariant (|ΔR| < 0.3) | O2 R(0–15): 0.73 [0.54, 0.96] before vs 0.89 [0.40, 1.89] after (ΔR +0.16); R(15–60): 0.96 vs 0.81 (−0.16); O2c R(0–15): 0.82 vs 0.61 | **supported** (low power after the switch) |

Other numbers (before the switch):
- **Mentions (busy recipients):** E1 = 0.81 (O2) and 1.51 (O2c). In-episode R = 0.65 [0.38, 1.00] vs busy-without-episode R = 0.81 [0.60, 1.11] (O2), far from the episode-lock signature (0.2 vs 1.0). Batched R = 0.37 (O2) and 0.25 (O2c).
- **Nudges read by busy agents:** E1 = 1.80 on the immediate reply (O2c, 43 primers); re-fires R(60–240) = 1.28.

Reading: no refractory window for nudges on either outcome. The first nudge after a quiet spell makes idle agents look, but it does not start sustained work; re-fires 15–240 min later are at least as effective. The 08-21 drop in escapes is not explained by losing the per-kick effects. Rooms, roster and the loss of the daily bookends change on the same days.
