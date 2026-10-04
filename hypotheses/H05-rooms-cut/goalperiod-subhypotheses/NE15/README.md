# H05 × NE15: the #best/#rest split (2026-03-16), with NE12 (02-25) as placebo and #voted-out

**Verdict:** mixed (pre-registered overall rule: INCONCLUSIVE. C1 and the MF J_out check passed; pooled C3 missed significance)
**Verdict (1b):** mixed (not re-run; corrected non-holdout analogues suggest C3's miss was attenuation by the activity_bins bug)
**Role:** confirmatory (locked holdout: the pre-split baseline #33–#34 and the NE12 window)
**Period:** spans #31–#35 (regimes II/III boundary region). Pre = #33 + #34 pair-days with both agents in #general (03-02 → 03-13, held out); post = #35 (03-16 → 03-20, **not held out; seen in round 1**). Placebo window 02-16 → 03-04.

## Why this test
The first real cut of the chat channel between agents (H05 found NE12 on 02-25 separated no one). Pairs split across #best/#rest are the treated arm; pairs that stayed together are the control.

## Prediction
Pre-registered in the main card ("Confirmatory predictions for the holdout", C1–C6 and MF-C, prediction hash 9df7b66d2a2a3d69), committed in e9bf2f7 before the run.

## Result (run 2026-10-03; `analysis/confirm_ne12.py`; `data/processed/H05-rooms-cut/confirm/confirm_ne12.json`)
| Prediction | Result | Verdict |
| --- | --- | --- |
| C1 (primary): cut-arm pair DiD < 0, talk | κ_x −0.022 [−0.038, −0.008], p_perm 0.021; c0_x −0.037 [−0.065, −0.004], p_perm 0.016 (18 cut, 37 stay pairs) | **pass** |
| C2: same, active spins | κ_x −0.015 (p 0.34); c0_x +0.007 (p 0.82) | n.s. (direction only) |
| C3 (primary): pooled TWFE 02-09 → 03-20, talk κ_x | β = +0.013, z = 1.40 (c0_x: z = 1.98) | **fail** |
| C4: no whole-swarm EP drop at 02-25 | CI includes 0 | ✓ (uninformative null) |
| C5: J_out → 0 after the split | +0.032 [−0.011, 0.082] → −0.033 [−0.092, 0.025] | **pass** |
| C5: J_in unchanged | +0.023 [−0.013, 0.059] → **+0.139 [0.06, 0.35]** | fail (J_in rose → HH90) |
| C6 / placebo: no pair separated on 02-25; no change | 0 separated pair-days; κ_x and c0_x changes ≈ 0 | ✓ |

## Caveat (important)
**The post-split window (#35) is not in the holdout and was analyzed in round 1.** Round 1's #35 mean-field values (J_in 0.139, J_out −0.033) are exactly the confirmatory C_post values. Only the pre-split baseline was unseen, so this is a weaker test than a fully blind one. The DiD design was pre-registered with that structure (the card lists "before-window of NE15" as the held-out part), but HH90 rests on a post-split number seen before the run.

## Notes
- Under the per-goal-period rule (adopted after this pre-registration), C1's single-boundary design is the appropriate one; C3 pools across periods.
