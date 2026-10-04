# H03 × NE43: the drive withdrawn inside #51 (bookends stop after 2026-08-04, nudges after 2026-08-20)

**Verdict:** supported
**Role:** native
**Period:** #51 (private roles, regime III, one room plus #focus 08-05 → 08-21) at a fixed roster of 27 agents (07-29 → 08-27: no join between Claude Opus 5 on 07-24 and GLM-5.3 Flash on 08-28). Three sides: **A** 07-29 → 08-04 (daily pause/resume bookends and nudges), **B** 08-05 → 08-20 (nudges only), **C** 08-21 → 08-27 (no `automated` drive). Non-holdout (the #51 tail starts 09-07).

## Why this period
The only place in the record where the exogenous drive is switched off inside one goal, at a fixed roster, hours and goal (DQ9 cross-index: H03 → NE43). H03's question is how much activity is self-generated. A self-exciting swarm with n̂ ≈ 0.5 whose exogenous share is ~1% of events should barely notice the drive going away; a swarm that needs kicks (H03-R2: "the swarm dies without drive") should slow down.

## Prediction
*Written 2026-10-04 06:45 UTC, before any NE43 fit (round 1b; corrected inputs: `kicks_classified` exogenous drive, days split at operator-off gaps).*
- **N43-a (exogenous share).** The model-based exogenous share of TALK events (M1_B2) is ≤ 2% on every side and ≤ 0.5% on side C.
- **N43-b (self-excitation unchanged).** n̂ TALK differs between adjacent sides (A vs B, B vs C) by less than 2 day-bootstrap SDs of the difference. Same for ALL.
- **N43-c (activity sustained).** TALK events per agent-hour on side C are within ±20% of side B.
- Counts against H03's self-excitation reading: n̂ dropping by more than 2 SDs once the drive is gone, or the talk rate falling by more than 20% (H03-R2 supported instead).
- **Confounds, stated in advance:** the #focus room exists exactly 08-05 → 08-21 (side B), so B → C is also a room change; C is 5 weekdays only; the bookend stop (A → B) coincides with #focus opening.

## Result
*Run 2026-10-04 (round-1b inputs). M1_B2 per side; day-bootstrap SD (30 reps).*

| Side (days) | n̂ TALK ± SD | n̂ ALL ± SD | exogenous share of TALK events | TALK / agent-hour | ALL / agent-hour | fast n_x TALK |
| --- | --- | --- | --- | --- | --- | --- |
| A bookends + nudges (5) | 0.44 ± 0.11 | 0.41 ± 0.12 | 0.77% | 3.92 | 10.24 | 0.000 |
| B nudges only (12) | 0.35 ± 0.03 | 0.30 ± 0.09 | 1.44% | 4.12 | 10.72 | 0.023 |
| C no drive (5) | 0.47 ± 0.08 | 0.51 ± 0.11 | 0.17% | 3.66 | 9.08 | 0.000 |

- **N43-a: supported.** The exogenous share is ≤ 1.4% on every side and 0.17% once the drive is gone.
- **N43-b: supported.** n̂ TALK: B − A = −0.09 (2 SD of the difference = 0.22), C − B = +0.11 (0.17); ALL: −0.11 (0.30), +0.20 (0.29). No change beyond 2 SD; if anything n̂ is highest with no drive.
- **N43-c: supported.** TALK rate per agent-hour C vs B −11%, ALL −15% (within ±20%).
- **Verdict: supported.** Removing the bookends and then the nudger leaves the self-excitation and the activity level of #51 essentially unchanged: the swarm does not "die without drive" on a one-week scale (against H03-R2's strong form). Confounds stated in advance apply (#focus room on side B only; C is 5 days), and fast cross-triggering is at ~0 on all three sides (#51 is past the point where it is measurable; see G51).
- Source: `data/processed/H03-self-excited-criticality/r1b/native.json` (key `NE43`).

## Notes
- Code: `analysis/r1b.py native`; output `data/processed/H03-self-excited-criticality/r1b/native.json` (key `NE43`).
