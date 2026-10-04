# H116 × G26: Elect a village leader. They choose this week's goal! (2026-01-05 → 01-09)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime I · mode C · 10 agents · one room · 5 days. Approval vote (first ballot 19:25:09 UTC) → 9–9–9 tie → runoff → result 01-05 19:35:22.59 UTC, agent 17 elected 7–1–0; confirmatory re-election 01-09 19:00:43 UTC (9–0). DQ6 `phase`, `tally`, `leader`.

## Why this period
The only period where a peer becomes a designated leader at one dated instant, with data on both sides on the same day. HH354 points here; models 10 and 02 rank first and second for #26 in `goal-periods.md`.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Card N1–N4 as written:
- **N1 (primary):** ΔJ_out(17, T*) ≥ 0.05 and above the 95th percentile of time placebos (same offset from day start on other regime-I days of #24–#27; kickoff-matched subset = first days). Kill: not above the placebo 95th percentile, if synthetic power ≥ 0.8 at that size; else inconclusive. [0.3]
- **N1b:** ΔJ_in(17, T*) inside the central 90% of time placebos. [0.7]
- **N1c:** ΔJ_out(17) above the 90th percentile of agent placebos. [0.3]
- **N2 (negative control):** no step at the 01-09 re-election (inside the central 90%). [0.75]
- **N3:** ΔJ_out − ΔJ^P_out > 0 (coupling, not a co-response to the new goal). [0.3]
- **N4:** ΔΣ_mp (winner pairs) above the 95th percentile of time placebos. [0.2]
Expected size: one event gives a step SE of ~0.2 Ising units; HH354's 0.05 is not resolvable by itself.

## Result
*Run 2026-10-04 22:25–22:28 UTC* (`analysis/run_g26.py`, `analysis/posthoc_n2.py`; `data/processed/H116-election-coupling-step/G26/results.json`, `posthoc_n2.json`). Winner-focused event model, λ = 4 for tests (A1), λ = 0.01 for magnitudes. Event windows: pre 18:02:09–19:25:00, post 19:35:23–20:58:13 UTC (3,256 calls of 10 agents; 152 / 204 reader-calls exposed to agent 17's messages).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| N1 ΔJ_out ≥ 0.05 and beyond placebos | +0.035 (λ = 4); magnitude +0.09 ± 0.33 | time placebos (16 days) q95 0.13, pct 0.56; skeleton null q95 0.15, pct 0.71 | **not detected** (kill clause fires; powered only for Δ ≳ 0.75, A1) |
| N1b ΔJ_in inside placebo band | −0.004 (magnitude −0.02 ± 0.14) | time placebos 5–95% [−0.15, +0.18] | consistent |
| N1c winner above agent placebos | pct 0.56 among 9 other agents | q90 0.10 | failed |
| N2 no step at the re-election | **+0.31 ± 0.21** (λ = 4); magnitude +1.03 ± 0.47 | above all 16 event-offset placebos (q95 0.13) | **failed** |
| N3 read step > in-flight step | read − in-flight −0.02 ± 0.28 | — | failed |
| N4 EP rises | ΔΣ_mp (winner pairs) +0.002 nats/call | time placebos pct 0.69 | failed |

- **N1:** the result did not change how often the other nine agents talk after reading agent 17, within 83 min. The unpenalized 95% interval [−0.55, +0.73] excludes a step ≥ 0.75 Ising units and says nothing about HH354's 0.05.
- **N2, post hoc checks:** against placebos at the re-election's own offsets (19 days, untrimmed as A0) the step is still above all of them (q95 0.07), and above all 200 field-only skeleton worlds of 01-09 (q95 0.15). The read-gated step exceeds its in-flight analog (+0.39 ± 0.30 at λ = 4; +1.43 ± 0.89 unpenalized). Exposure is thin (44 / 54 exposed reader-calls).
- **Kickoff-matched placebos** (first days of #24, #25, #27): ΔJ_out +0.11, −0.07, −0.02; the event's +0.035 sits among them.
- **EP:** the held-out Newton bound is ≤ 0 in both windows (−0.011 / −0.009 nats per call, all pairs), so the call-clock multipartite EP is below the estimator's resolution at 10 agents and 1,500 calls.
- **Cross-check with H115 G26:** the leader's sink rank on the result day (after 19:35) was 3 of 10 (sink side), and it was the top source on 01-06, 01-07 and 01-09. Influence flowed toward the leader on the following days and right after the re-election, not at the first result.

Figure: [`figures/event_vs_placebos.pdf`](figures/event_vs_placebos.pdf).

## Scorecard (period-specific axes)
C (time, agent and in-flight placebos), D (in-coupling, EP, re-election null), E (the election as an intervention), G (DQ6 event time).

## Notes
- Windows: pre = [all-present start of 01-05, 19:25:00), guard [19:25:00, 19:35:22.59), post = [19:35:22.59, + same length).
