# Research goals

**Mission.** Build a quantitative physics of LLM agent swarms that someone running, steering or aligning one can use. The physics should give measured constants, fitted models with error bars, and laws that survive the four impostors (`STANDARDS.md` §1) and the locked holdout. The AI Village is the system. Each goal period is one point on a phase diagram.

**Status as of 2026-10-04:**
- Round 1b covers H01–H39. Round 1 is done for H40–H80 and H85–H86; H51, H81–H84, H87–H105 are running.
- 81 hypotheses carry multi-rater v2 scores (coordinator plus a blind rater; disagreements adjudicated).
- Nothing is holdout-confirmed yet.
- Measured constants are listed in `interpretation/swarm-constants.json`.
- The synthesis is in `writeup/round1b-synthesis/`.

## The questions
Every hypothesis serves one of these. A new hypothesis card names its question (Q1–Q7).

| Q | Question | Where it stands | What settles it | Main hypotheses |
| --- | --- | --- | --- | --- |
| **Q1** | **What couples agents?** | Coupling runs through reading, at the recipient's next call. It runs on a per-call clock in the computer-use scaffold (η ≈ 0). It is address-gated: named messages couple and unnamed ones do not. Rooms couple only because they route reading. | Holdout confirmation of read-out gating (H08) and the call clock (H40 on NE20); a dose–response in cadence | H08, H40, H42, H50, H29, H05, H41, H18 |
| **Q2** | **What is field and what is coupling?** | 70–80% of synchrony is the scheduler. Day-1 content lands on the kickoff (quench). About a third to a half of apparent influence is convergence. Family fields are style. | A per-period field gauge (pair-covariance c_× from H86, excess vs housekeeping) reported for every unit; the impostor decomposition in one table | H38, H50, H54, H26, H49, H13, H57, HH310, H76 |
| **Q3** | **Is there collective order beyond fields?** | Talk and content modes are real (H12). Every unit is subcritical (H03, H25, H34). No coordination superagent (H01, H58). No spin glass and no antiferromagnet in content. **First positive (H81):** a regime-I collective slow mode in content beyond composition (τ ≈ 25 d), surviving turnover; round 2 narrowed the external-drift rival (operator directions beyond the centroid and outside-world topics excluded; the read artifact record is not the carrier), but calendar-time drift stays open (calendar and goal-count clocks are not identifiable). H106: the 1/N finite-size test is untestable in one village (power 0.00); post hoc, the slow mode is confined to the N < 8 era (May–Oct 2025), which a constant-rate outside drift would not give. H82 places the boundary trace in members, not the record; H89 finds no persistent attractor within periods. | The egregore tests: culture beyond composition, remanence, enculturation, synergy and autonomy against size-matched nulls, with fields removed | HH290–HH306, HH311, HH317, HH321, H58 |
| **Q4** | **Where does the swarm's information live, and what is it worth?** | The context window carries call-scale information. Memory carries ≈ 0 day-scale semantic information. Agents recover through their own artifacts. | The κ table: commits per bit by channel (HH307); the artifact store (H70); collective memory decay (HH316) | H15, H44, H45, H58, H70, H71, HH307 |
| **Q5** | **What can an operator do?** | Nudges buy about 1 active minute, not commits. Naming is a one-hop content lever. Erasure costs about 10% of output. Cadence is a coupling knob. No single lever model fits all inputs (H59). | Holdout-confirmed effect sizes for each lever; an index nudge policy (H60) | H04, H30, H35, H39, H43, H59, H60, `interpretation/lever-table.md` |
| **Q6** | **Thermodynamics and selection.** | Fine-action irreversibility is real; the platform does not own it (H56). The thermodynamic tests (speed limit, excess vs housekeeping, selection resolution) are running. | H75–H78 results; collective entropy production beyond the parts (HH311) | H14, H56, H75–H80, HH311, HH312 |
| **Q7** | **What transfers outside the village?** | Ideas only (HH191–HH210). | Signatures computable from public logs: agent-vs-script (H80), read-out gating, convention dynamics | H80, HH191–HH210, HH314, HH315 |

## Deliverables
1. **Paper.** Working title: "Read-out gating, fields and the missing collective: the statistical physics of an LLM agent village".
   - Core claims: Q1 (gating and the call clock), Q2 (the field decomposition), Q3's negative results with power, and Q5's lever sizes.
   - It needs holdout confirmation of at least three core claims.
2. **Operator guide.** One page per lever, with effect size, timing and caveats, built from the lever table and the constants panel.
3. **Toolkit.** The impostor checklist, the null library (DQ8), the context ledger and estimators, packaged so that others can run them on their own swarm logs.
4. **Living documents.** The compendium (two pages per hypothesis), the dashboard (matrix, phase diagram, constants) and `OVERVIEW.md`.

## Priorities (in order)
1. **Confirm.** Re-freeze confirm scripts on current inputs, then run the first confirmatory tests: H40 on NE20 and H08, after Vivian's sign-off. Decide on the H02, H04 and H05 re-runs.
2. **Standardize.** Every card and summary meets `STANDARDS.md`: impostor table, two layers, house style, `models` field, estimates rows.
3. **Collective order (Q3, Q4).** Run the cheap, decisive egregore and quantitative tests first: HH293, HH290, HH292, HH309, HH310, HH307 and HH316, once Vivian approves them.
4. **Round 1 for H60–H80.**
5. **Synthesis.** Keep the constants, the lever table and the phase diagram current after every report.

## What "done" looks like
- At least 3 core claims confirmed on the holdout, with credence ≥ 0.9 after the holdout.
- Every claim scored with credence and EU, and every fragile claim flagged.
- A phase diagram with every period placed by its fitted parameters. After H51: x = N (H85 active population, log), marker = scaffold regime, y = g_lag (H67) as the coupling coordinate; field gauges (c_×, S_text) are reported as impostor gauges, not axes. No single dial collapses the diagram (χ ≤ 1.31).
- A clear answer to Q3: either a collective variable that beats all four impostors and size-matched nulls, or a powered negative.
