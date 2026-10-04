# H04 × NE43: forcing withdrawn inside #51 (bookends stop after 2026-08-04 PT; nudges stop after 08-20)

**Verdict:** mixed
**Role:** native (round 1b, non-holdout; transition exception c)
**Period:** regime III · #51 non-holdout days (2026-07-06 → 09-04) · N 21 → 32 · 8 h days · #general (+ #focus 08-05 → 08-24). Two steps: (a) the daily pause/resume bookends end (last on 08-04 PT); (b) the nudger goes silent (last nudge 08-20). Undocumented in the CHANGELOG. `period_units` has no split at either step (unit 51g spans both), so the windows are set here by date.

## Why this unit
DQ9's native test for H04: the forcing regime changes inside one goal period, at a fixed goal and hours. It is the non-holdout counterpart of NE23 (nudger off/on, held out), whose manipulation check failed in the executed holdout run. H04's C4 logic: the nudger is a field on idle agents, not a coupling, so removing it should leave the self-excitation n unchanged while agents stay idle longer.

## Prediction
*Written 2026-10-04 06:45 UTC, before any round-1b run (H04 round 1 did not look at #51 after 08-04).*
Windows (PT dates, non-holdout): **on** = 2026-08-05 → 08-20 (bookends gone, nudger on); **off** = 2026-08-21 → 09-04 (both gone); **pre** = 2026-07-21 → 08-04 (both on), for the bookend step. Activity from `activity_bins_fixed`; Hawkes n from H04's fitter (agent chat, 10 s bins).
- **N43a (n is not set by the nudger):** |n(off) − n(on)| < 0.1, and in any case inside the week-to-week placebo band (round-1 p90 0.43).
- **N43b (traps lengthen without the nudger):** the mean inactive-run length of agents (runs ≥ 10 min inside presence) rises by ≥ 10% from on to off, and the idle fraction rises.
- **N43c (bookends):** |n(on) − n(pre)| < 0.1.
- **Known confounds (stated now):** #focus (08-05 → 08-24) overlaps the step; NE33 batch joins on 09-03/04 change N at the end of the off window; humans are present on 08-20.

**Verdict rule (fixed now):** supported if N43a and N43b hold; failed if N43a fails beyond the placebo band; mixed otherwise.

## Result
*Run 2026-10-04 (`analysis/r1b_native.py`; `data/processed/H04-reversible-forcing/r1b/NE43.json`; nudge kernels from `r1b.py --suite NE43_pre / NE43_on`). Hawkes n with 30 day-bootstrap refits; inactive runs ≥ 10 min inside presence; day-bootstrap relative changes.*

| Window (PT) | days | Hawkes n | mean inactive run | idle share | active share | target A30 (nudges) |
| --- | --- | --- | --- | --- | --- | --- |
| pre (07-21 → 08-04: bookends + nudges) | 11 | +0.71 [+0.52, +0.79] | 29.9 min | 0.252 | 0.502 | +1.36 [+0.78, +1.90] |
| on (08-05 → 08-20: nudges only) | 12 | +0.55 [+0.43, +0.66] | 23.9 min | 0.297 | 0.486 | +0.74 [+0.02, +1.50] |
| off (08-21 → 09-04: neither) | 11 | +0.61 [+0.43, +0.67] | 24.0 min | 0.286 | 0.497 | — |

In-period week-to-week noise (#51, 9 ISO weeks): |Δn| median 0.11, 90th percentile 0.31.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N43a: \|n(off) − n(on)\| < 0.1, inside the placebo band | Δn = +0.06 [-0.22, +0.21] | pass |
| N43b: mean inactive run +≥ 10%, idle share up | inactive run +0.5% [-8, +10]; idle share -3.5% | **fail** |
| N43c: \|n(on) − n(pre)\| < 0.1 | Δn = -0.16 [-0.33, +0.09] (inside the weekly band) | fail by point, inside noise |

- **The nudger is not holding agents out of traps at the swarm level:** switching it off changes neither n nor inactive-run lengths, consistent with H35's accounting (nudges buy about 0.5% of active minutes).
- **The bookend step does more than the nudger step:** after the daily pause/resume messages stop (08-05), inactive runs shorten by -20% [-29, -9] and the idle share rises 18%, and the nudge kernel halves (A30 1.36 → 0.74, onset t₂₅ 7 → 13 min, median read-out 104 → 156 s). Post hoc; #focus opens on the same day.

**Verdict: mixed** (N43a holds; N43b fails).

## Notes
- 2026-10-04: folder created with the prediction (round 1b native layer, DQ9 cross-index).
