# H08: Context is the coupling

**Status:** reactivated 2026-10-04 (Vivian: start the hypotheses never worked on). Originally parked on 2026-10-03 after a misread. Since then H04 (delayed, context-mediated responses), H15 (context-erasure dip, NE41) and H18 (attention dilution) have all pointed at it. Primary test: HH92, the response kernel predicted from turn timing.
**Fields:** info theory, dynamics, stat mech
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (interventions on information channels)
**Definitions used:** Interaction / exposure (`physics-models/DEFINITIONS.md`); Regime.

## Question
Agents interact *only* through what enters their context. So the coupling between agents is, mechanically, *context inclusion*: what each agent saw, and when. How faithfully can we reconstruct that from the logs, and how much of each agent's behavior does it explain?

Every other direction needs a good answer. Contagion, couplings (S1, S4), field vs. coupling (S5) and H01's natural scrambles all rest on an exposure model.

## Data situation
- **The exact prompts (`llm_calls`) are not public.** AI Digest publishes only `aidigestorg/ai-village`, which has no `llm_calls` file; the prompts are available on request to vetted researchers. Vivian can't obtain them (2026-10-03), so **C4–C6 are blocked**. C1–C3 remain possible from the Claude Code agent's stream and the token accounting.
- **Ground truth for one agent.** The Claude Code agent ("Opus 4.5 (Claude Code)", 2026-01-26 → 04-02) logged its full input side in `claude_code_messages`:
  - every village-API fetch, with the event IDs it returned, `unseenEventsCount`, `hasMore`, the current goal and memory-update reminders;
  - context compactions, with `pre_tokens`;
  - synthetic continuation summaries.

  Its tenure spans the rooms change (NE12, 2026-02-25).
- **Per-call token accounting for everyone.** `computer_use_turns.agent_messages` holds provider responses (no prompts, no sampling parameters) with input tokens and prompt-cache reads and writes. The uncached part of the input is a proxy for *new context per call*.

## Sub-hypotheses
- **C1 · Exposure reconstruction.** A room-based rule ("an agent sees every event in its room between its consecutive turns") reproduces what the agent actually saw.
- **C2 · Information inflow.** New context per call (uncached input tokens) tracks room activity, and drives the next action's latency and type: a Green's function from inflow to action.
- **C3 · Context compression.** Compactions and consolidations are erasure events: their frequency and the context size just before them behave like an equation of state (HH57).
- **C4 · Context → action attribution.** Which context elements predict the next action. Needs `llm_calls` for the standard agents; the Claude Code agent first.
- **C5 · Scaffold ground truth.** Exact prompt diffs at each natural experiment, turning field changes into measured ones. Needs `llm_calls`.
- **C6 · Replay.** Counterfactual scrambles for H01 (Tier R). Needs `llm_calls`.
- **C7 · Sampling parameters.** A literal temperature, from the operators.

## Model
**From:** none primary; this is a measurement hypothesis that calibrates the exposure input of models 01, 02, 03, 09, 11 and H01.

## Data scheme (`scheme/`)
- **Script:** `scheme/build_cc_exposure.py`.
- **Inputs:** `claude_code_messages`, `events`, `agents`.
- **Outputs:** `data/processed/H08-context-is-the-coupling/`:
  - `cc_fetches.parquet`: one row per village-API fetch;
  - `cc_seen.parquet`: one row per event seen, with event time, fetch time, delay, type, actor and room;
  - `cc_usage.parquet`: per assistant message: input, cache-read, cache-write and output tokens;
  - `cc_compactions.parquet`.
- **Regimes covered:** I (to 2026-02-25), II (to 03-24), III (to 04-02).

## Observables (C1)
- **Delay:** time from an event's creation to the agent seeing it.
- **Coverage:** the fraction of village events the agent saw, by event type and by room (own vs. other), before and after NE12.
- **Reconstruction:** precision and recall of the room-based rule against ground truth.

## Null / baseline
"Sees everything instantly" (all-to-all, zero delay) and "sees only its own room's chat" are the two simplest exposure models to beat.

## Prediction (C1)
*Written 2026-10-03, before running the analysis.*
1. **Coverage collapses at NE12.** Before 2026-02-25 the agent sees events from the whole village. After it, it sees ≲ 5% of events originating in other rooms; room filtering is real and near-total.
2. **Not all event types are visible.** Other agents' `AGENT_TALK`, session start/stop and `CONSOLIDATE` events are visible, but not WAITs or pauses. Coverage differs by type.
3. **Median delay is minutes, not seconds:** set by the agent's own turn cadence. The delay distribution is heavy-tailed: long gaps when the agent was busy or paused.
4. **The room-based rule reaches recall ≥ 0.9 after NE12.** Recall drops before NE12 if the agent didn't actually see everything, because of fetch limits.

**Falsifiers:** substantial cross-room visibility after NE12; uniform visibility across types; or recall < 0.7 for the room rule.

## Faithfulness scorecard
This is a calibration measurement, so only some axes apply.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | event IDs match exactly between the fetched feed and `events` | | |
| G ground truth | it *is* the ground truth, for one agent | | |
| I transfer | one agent only; generalizing to the standard scaffold needs `llm_calls` | | |

## Results

## Notes
- 2026-10-03: opened on a misread; parked. `llm_calls` confirmed unavailable on Hugging Face. C1 is ready to run on the Claude Code agent whenever wanted. Its predictions above were written before any data was touched.
