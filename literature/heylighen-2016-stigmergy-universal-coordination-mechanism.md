# Stigmergy as a universal coordination mechanism I: Definition and components

**Citation:** Francis Heylighen, *Cognitive Systems Research* 38, 4–13 (2016). DOI: 10.1016/j.cogsys.2015.12.002
**File:** heylighen-2016-stigmergy-universal-coordination-mechanism.pdf
**Fields:** sociophysics, complex systems, cybernetics (conceptual; no data)

## Summary
Heylighen defines stigmergy as "an indirect, mediated mechanism of coordination between actions, in which the trace of an action left on a medium stimulates the performance of a subsequent action", and analyses its parts: action, agent (optional), medium, trace and coordination. On this account stigmergy coordinates work without planning, memory, communication, mutual awareness, simultaneous presence, imposed sequence or division of labor, commitment, or central control. Negative feedback repairs disturbances, and positive feedback amplifies affordances, so promising projects grow rich-get-richer. A single agent can also coordinate with itself this way. Examples are termites, ant trails, Wikipedia, open source, markets and muscles. **This is Part I.** The typology (marker-based vs sematectonic, quantitative vs qualitative) is in Part II (*Cogn. Syst. Res.* 38, 50–59; not in `literature/`; †). Part I only notes that ant pheromone is "quantitative, marker-based" (after Parunak) and that the general case needs neither markers nor quantities.

## Key formalism (as measurable quantities)
- **Action:** a causal process changing the world, written as the rule *condition → action*. Stimulation means $P(\text{action}|\text{condition})>P(\text{action})$; inhibition counts as stimulation by the negated condition.
  → *Stimulation lift* $\lambda_{ij}=P(a_{ij}|\text{trace of } j\text{ perceived})/P(a_{ij}|\text{not})$.
- **Agent:** optional. Agentless processes and a single agent's own sequence also count.
  → Split λ into *self* (own trace) and *allo* (others' traces). Cron/CI commits are agentless traces.
- **Medium:** the part of the world that **all** agents can both perceive and control. It can be internal. The sky (seen, not changed) and the sea (changed, not seen) are not media; a beach is.
  → *Medium membership* of an object = the number of agents that both wrote and read it (≥ 2).
- **Trace:** a perceivable change, often unintended, that carries information about the action and serves as the activity's external memory. A **marker** is an intentional sign.
  → Classify traces as *work* (commits, files, deploys, broken builds; sematectonic in Part II's terms) or *marker* (chat links, TODO or handoff files).
  → *Quantitative* traces act by amount (commits, recency, share). *Qualitative* traces act by a specific state (a broken build calls for a fix).
- **Coordination** (after Crowston): sequential prerequisites (workflow) and shared inputs or outputs (parallel work, division of labor).
- **Coordination cycle** (Fig. 1): action → trace → medium → condition → action.
  → *Cycle time* = from a trace to the first action it triggers by another agent. *Loop gain* = triggered actions per trace (>1 amplifies).
- **Negative feedback** needs only goals that are not contradictory; conflict falls as degrees of freedom grow.
  → *Repair hazard* after a disturbance, and its latency.
- **Positive feedback:**
  → Recruitment hazard $h_j\propto n_j^{\beta}$ in trace amount ($\beta>1$ = winner-take-all).
- **No commitment:** an agent that quits "is automatically replaced". **Massive parallelism:** a pool of workers larger than the open tasks.
  → *Replacement time* after a maintainer exits.

## Mapping to agent swarms
- **Medium:**
  - `artifacts` (2,404 repos, plus sites and files);
  - chat rooms (a medium by this definition, but mostly addressed markers);
  - history search;
  - HH244's automata.
- **Traces:**
  - DQ4 `work_commits`, agent work only (`canonical & ~imported & author_kind=="agent" & ~automated`);
  - `work_api_writes` and deploys (`work_daily`);
  - markers: chat links (`artifact_mentions.source=="chat"`) and handoff files.
- **Perception:**
  - chat: `context_ledger_items` per `call_windows.t_call`;
  - artifacts: `artifact_mentions` read verbs (clone/fetch/view, `how` ∈ {url, output, bare});
  - `artifact_commands_text`.
  - Screen content is not logged.
- **Actions:** next commits; `behavior_states_v3` (execute_task, debug_recover, self_maintenance); `turn_outcomes.failed` for broken states.
- **Already seen in the project:**
  - Agents return to their own artifact after erasure by re-reading it (H58: 63% vs 55%; H44). That is single-agent stigmergy with the medium as external memory, consistent with H15's ≈ 0 memory information.
  - The first chat link raises adoption about 20× (H53). That is marker stigmergy, close to communication.
  - Share predicts wave size (H53, AUC 0.72). That is quantitative positive feedback.
  - Shared repos do not carry cross-room *idea* leaks (H41 lift 1.04). Whether they carry *work* is open.

## Candidate hypotheses
- **Work traces recruit beyond markers and share (HH301).**
  - *Observable:* the discrete-time hazard of agent i's first agent-work commit to repo j. Covariates: j's work traces read by i, chat links to j in i's ledger, current share, goal naming.
  - *Null:* trace covariates permuted across repos within a goal-day.
  - *Impostors:* the kickoff/goal field (`goal_fields`, H54), and contemporaneous convergence (joins with no logged read of j, at matched time).
- **Qualitative stigmergy is repair.**
  - *Observable:* after a broken state on j (`turn_outcomes.failed` push or deploy), P(another agent commits a fix to j within k calls | it read the broken state) versus not read.
  - *Prediction:* lift > 1, with latency in calls rather than minutes.
  - *Null:* matched reads of j in a non-broken state.
  - *Impostors:* the scheduler field (first_of_day status sweeps) and shared model priors (habitual CI checks; compare within and across families).
- **Maintenance needs no commitment (HH302).**
  - *Observable:* for long-lived repos not named by the goal, the time from the maintainer's exit (roster `left`, NE29) to the first commit by someone else, against matched repos whose maintainers stayed.
  - *Null:* takeover hazard independent of exit.
  - *Impostor:* the kickoff/goal field (an operator or the goal names the repo; check `kicks_classified`).
- **Stigmergy substitutes for talk.**
  - *Observable:* per period, the artifact-read share of coordinating reads, against duplicated work (same paths written by two agents in a window) and chat per commit. A phase-diagram comparison across periods.
  - *Null:* random agent pairing within the period.
  - *Impostor:* shared priors (H07: identical innovations in isolated forks).

## Caveats
- There is no estimator. "Stimulates" is a conditional-probability lift, and a common cause raises it too. Heylighen notes that observers tend to blame a shared cause; for us those shared causes are the four impostors, and each must be removed.
- Artifact perception is only partly logged (cwd resolution precision 0.89/0.81; screens unread). Chat perception is good (DQ1).
- Chat meets the definition of a medium, so "stigmergy vs communication" rests on the trace classification, not on the channel.
- Agents are told the goal, plan and talk, so measure stigmergy as a *share* of coordination.
- 112k of 192k agent-identity commits are automated. Filter them for agent-level claims.
- Git is sparse before #30. Narration is a claim, not evidence.
