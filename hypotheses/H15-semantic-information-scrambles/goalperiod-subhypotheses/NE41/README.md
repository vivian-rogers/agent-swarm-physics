# H15 × NE41: forced context erasure at the 41-turn cap, memory kept (regime III, from 2026-03-24)

**Verdict:** supported
**Verdict (1b):** supported (native, 2026-10-04)
**Role:** native (round 1b, non-holdout; spans G36b–G51, one estimate per period plus a random-effects pool, exception (c))
**Period:** regime III · all non-holdout periods with forced erasures (36b, 36c, 37, 38, 39, 40, 41, 42, 44, 51 to 09-04) · DQ1 context ledger: 21,165 forced (`reset_forced`) vs 16,357 voluntary (`reset_consol & ~reset_forced`) non-holdout events.

## Why this NE
The 41-turn cap erases the context window at a time the scaffold sets, while the agent chooses what to save to memory (KW's coarse-graining f). Only this NE lets us ask whether the *agent's own* saved information (the memory written at the wipe) carries the session's semantic information: the timing is quasi-exogenous and the dose (what was saved) varies across events. Round 1 found ρ(stored dose, write-turn dip) ≈ 0 on write turns with H15's own segment rule; round 1b redoes it on the DQ1 ledger's per-call reset flags with DQ4 work commits as the output.

## Design (native)
- Calls: DQ1 `context_ledger_turns`, regime III, computer-use calls, non-holdout. Per call: agent work commits mapped forward to the first call with `t_log` ≥ commit time (≤ 10 min), real failures (DQ3 `turn_outcomes.failed`; platform `error_class` on GUI turns), write evidence.
- Forced erasure (CF) = a call with `reset_forced`; its post window = calls +1…+10 of the new segment; reference = calls −20…−11 of the erased segment (far from the cap). Relative dip = Σ post / Σ far − 1 (ratio of sums, agent-day cluster bootstrap).
- Stored dose = lines added / lines of the memory snapshot written at that consolidation (`memory_stats`, backward as-of ≤ 600 s from the first post-reset call).
- **Native statistic:** within CF, Spearman ρ(stored dose, per-event work dip post − far) per period and pooled; and the relative work dip in the top vs bottom tercile of stored dose (pooled over periods with ≥ 100 forced erasures).

## Prediction
*Written 2026-10-04, before running the round-1b NE41 analysis (the round-1b `run_scrambles.py` pass had printed the per-period CF dips and the pooled ρ = −0.04 for the old write-turn style contrast on the new call table; the dose-tercile contrast and per-period ρ on work commits had not been computed).*
- N1 (KW, agent's coarse-graining is not viability-preserving): pooled ρ(stored dose, work dip) ∈ [−0.10, +0.10] and |ρ| < 0.15 in every period with ≥ 300 forced erasures.
- N2: top-tercile minus bottom-tercile relative work dip ∈ [−0.10, +0.10] with a 95% CI that includes 0 (saving more to memory does not shrink the dip).
- N3 (replication of P5′ on the ledger): the forced-erasure relative work-commit dip is below 0 with a CI excluding 0 in ≥ 7/9 periods; random-effects pool between −0.25 and −0.50.
- Counts against: ρ > 0.15 pooled (more saved → smaller dip), or a top-minus-bottom dip difference > +0.10 with CI excluding 0.

## Result
*Run 2026-10-04 (`analysis/r1b_extra.py`; `data/processed/H15-semantic-information-scrambles/r1b/r1b_extra.json` → `NE41`, `CTX`).* 20,332 forced erasures with a memory snapshot and full windows.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N1 pooled ρ(stored dose, work dip) ∈ [−0.10, +0.10]; \|ρ\| < 0.15 in periods with ≥ 300 events | ρ = +0.013 (n 20,332); per period −0.055 (36b) … +0.136 (#42); max \|ρ\| 0.136 | **holds** |
| N2 top − bottom dose tercile dip ∈ [−0.10, +0.10], CI ∋ 0 | low dose (0.09): −0.36 [−0.41, −0.32]; high dose (0.58): −0.41 [−0.46, −0.36]; difference −0.05 [−0.10, +0.01] | **holds** |
| N3 forced work dip < 0 (CI) in ≥ 7/9 periods; pool −0.25 … −0.50 | 7/9 periods (36b and #37 n.s.); random-effects pool −0.39 [−0.42, −0.35] | **holds** |

Also on the ledger: write-evidence calls −0.26 [−0.30, −0.23] (8/9); real failures **+0.27** [+0.12, +0.42] after a forced wipe (0/9 periods below 0); voluntary consolidations dip more (work −0.53), as in round 1 (task phase). The work lost in the ten post-wipe calls is 2.5–13% of a forced segment's work (median ≈ 10%; #37 2.5%, #41 13%), matching H44's independent 4–11%.

**Reading.** Saving 7× more to memory at the wipe (dose 0.58 vs 0.09) does not shrink the output dip; if anything high-dose wipes dip slightly more. In KW terms the agent's own coarse-graining f is not what carries the session's semantic information; the dip is re-acquisition (H44: re-reading artifacts restores output), not memory.
