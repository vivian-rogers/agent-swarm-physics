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

## Round 2 (2026-10-05): decomposing the drop (card R6)
*Predictions R6-P1…P5 written in the card before the run. Same windows as round 1: before 08-06 … 08-20, after 08-21 … 09-04 (11 days each). Both windows come after the last bookend (08-05), so the bookend loss is not a component of this change; it is tested as its own step.*

| Accounting | Result (day-bootstrap 95% CI) |
| --- | --- |
| total | Δ ln R = −0.190 [−0.300, −0.106] (−17.3%) |
| 1 mechanical: R = (idle reads per idle minute) × (escape per idle read) | cadence −0.132 [−0.262, −0.024] (**69%**); per-read escape −0.058 [−0.155, +0.031] (31%, n.s.) |
| 2 shift-share (27 incumbents; 5 newcomers) | within incumbents −0.0143 [−0.0302, −0.0021] (73%); reweighting among incumbents −0.0101 [−0.0180, +0.0018] (52%); newcomers and leavers **+0.0048** [+0.0010, +0.0094] (−24%) |
| 3 channels on after-PAUSE wakes (agent FE; change in mean escape −0.051 [−0.101, −0.004]) | nudge reads −0.0022 [−0.0039, −0.0007] (4%); room (#focus, peer reads, present agents) −0.0003 [−0.026, +0.031]; day edge −0.0002 [−0.0016, +0.0010]; within-agent step −0.034 [−0.074, −0.006] (logit −0.22 [−0.49, −0.04]) |
| 4 date profile (raw, vs before) | 08-21 (nudger off, two rooms): R −2.9%, cadence −4.1%, per-read +1.2% · 08-24…27 (one room, no new agents): **R −23.6%, cadence −23.5%**, per-read −0.1% · 08-28…09-02: R −16.0%, cadence −16.4% · 09-03…04 (NE33): R −15.4%, per-read −23.9% |
| step placebo (wake model, 13 splits of 11 \| 11 days before 08-21) | band [−0.21, +0.35]; observed −0.22; 1 of 13 placebo splits is more negative (08-04) |
| bookend step (08-05, raw R) | +4.8%; placebo band [−18.8%, +10.4%] |
| post hoc: declared pause | median 240 s before → 300 s on 08-21 and 08-24…27; share ≥ 600 s 0.17 → 0.34 in the one-room week; agent-FE ln pause +0.10 to +0.14 |

| Prediction | Outcome |
| --- | --- |
| R6-P1 per-read escape carries ≥ 50% | **failed**: cadence carries 69% |
| R6-P2 roster < 1/3; ≥ half the drop before any join | **holds**: newcomers raise the rate (+24% of the change); 08-24…27 already shows −23.6% |
| R6-P3 nudger + room + day edge < 1/2; nudger < 10% | **holds** (nudger 4%; room and day edge ≈ 0, room CI ±0.03) |
| R6-P4 bookend step inside its band | **holds** (+4.8%) |
| R6-P5 not a clean 08-21 step | **holds**: 08-21 itself is flat (−3%); the drop starts with the one-room week |

Reading: the NE43 drop is not the nudger. On the nudger-off day (08-21) escapes per idle minute barely move. The drop starts on 08-24, when #focus empties, and it is a cadence change: agents declare longer pauses (median 240 → 300 s; twice as many ≥ 10-min pauses), so they reach fewer timer wakes per idle minute, while the escape per wake hardly changes. Newcomers raise the rate. The room channel that a read stream would carry (peer items read, room size) explains none of it; what links the merge to longer pauses is not identified. Verdict for this folder unchanged (failed for round 1's P6a); round 2 is descriptive accounting (exception (c)).
