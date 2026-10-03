# Semantic Information in a Model of Resource Gathering Agents

**Citation:** Damian R. Sowinski et al., *PRX Life* 1, 023003 (2023). DOI: 10.1103/PRXLife.1.023003
**File:** sowinski-2023-semantic-information-resource-gathering-agents.pdf
**Fields:** info theory, dynamics

## Summary
By the authors' account this is the first application of the Kolchinsky-Wolpert semantic-information framework to a realistic individual-organism (agent-based forager) model. A 2D forager with a finite energy tank and a circular sensor harvests renewable resources. The authors degrade its sensor with a noise parameter $\eta$ (scrambling agent-environment correlations, measured as transfer entropy) and track viability, defined as expected lifetime. Viability is flat until a critical noise $\eta_c$ and then collapses. This "semantic threshold" is set by sensor/collector geometry rather than by speed or metabolism, so bits above the threshold are semantically irrelevant and bits below it are essential. The result is robust to other viability definitions and to ballistic, diffusive, intermittent and Lévy foraging.

## Key formalism
- Agent state $a=(s,\tau,\hat n,x)$ (fuel, target-locked flag, heading, position); environment = positions of decaying resources (influx $\Lambda$, decay $\gamma$, equilibrium density $n_{eq}=\Lambda/\gamma$). Small back-reaction limit.
- Viability $V=\mathbb E[T]$ (expected lifetime, in units of $S/\mu$). Percentiles of the lifetime distribution give the same curve.
- Intervention: replace the exact heading delta function with a uniform window of width $2\pi\eta$. Conditional transfer entropy $TE^\eta_{E\to A}=\log_2(1/\eta)$.
- Semantic threshold: $\eta_c=\tfrac1\pi\sin^{-1}(r/R)$, $TE_c=\log_2\pi-\log_2\sin^{-1}(r/R)$, a function of collection radius $r$ and sensing radius $R$ only.
- "Viability per bit" $\mathrm{VpB}=dV/dTE$ peaks at the threshold. Above the threshold, agents behave like unscrambled agents in a dilated world: $V_\eta=(1+\lambda_{max})^{-1}V_{actual}$, giving a lower bound on the plateau (Eq. 10).
- Floor: $V(0)=\dfrac{s_0/\mu}{1-v/\bar v}$ for a blind agent; the speed window $\underline v<v<\bar v$ separates starvation from effective immortality.

## Mapping to agent swarms
- Forager = one LLM agent (`agents`). A coarse-grained state could be action class (from `events.data.actionType`) plus topic cluster of `computer_use_sessions.session_goal`. Fuel and metabolism have no direct field; token `cost` and village hours are weak proxies.
- Environment/resources = the stream of work items: new tasks from `village_goals`, human `USER_TALK`, peer requests in `chat_messages`, tool outputs in `computer_use_turns.output`. A stretch: "resource density" is not directly measurable.
- Sensor noise $\eta$ = fidelity of the agent's information channel. The data hold natural interventions: rooms v1 filtering (2026-02-25), the 200-unseen-event cap (2026-06-11), `screenshot_is_redacted`, and the `SEARCH_HISTORY` answerer swap (Gemini 2.5 Pro to Sonnet 4.6). All are documented in `CHANGELOG.md`.
- $TE_{E\to A}$ = empirical transfer entropy from peers' messages (binned by `room_id` and time, or ordered by `event_index`) to an agent's next action class, conditioned on its own previous action.
- Viability = persistence. Candidates are tenure (roster Joined/Left dates, `is_participating`), run length before `WAIT`/`PAUSE`, or goal completion. All are coarse and ad hoc, which is the weakest part of the mapping.

## Candidate hypotheses
- Chat-derived transfer entropy has a plateau/threshold relation to a viability proxy: agent-weeks above a TE threshold show flat productivity (commits, sessions finished), and those below fall off. Observable: piecewise-linear changepoint fit of proxy vs. TE, plus a before/after comparison around the 2026-02-25 rooms change.
- Most chat-to-action information is semantically irrelevant (semantic efficiency well below 1). Observable: an offline replay or ablation of logged contexts with messages shuffled across days within a room, measuring the change in next-action distribution relative to total TE.
- The threshold shifts with a "geometry" parameter of the channel: shrinking visible context (200-event cap, room filtering) should move the viability-per-bit peak. Observable: per-era VpB curves.

## Caveats
- The analytic threshold depends on forager geometry (ballistic motion, circular sensor) and does not transfer; only the plateau-then-collapse structure is expected to.
- Interventions are counterfactual simulations in the paper; the village logs are observational. Natural experiments are confounded by simultaneous scaffolding changes.
- Estimating transfer entropy on text requires discretizing messages into symbols, and it is biased for short, non-stationary series with small agent counts.
- LLM "sensing" is not additive noise on a heading. Scrambling could change meaning discontinuously, and degradation is more like omission.
- There is no endogenous death for agents; operators choose when they leave, so lifetime is not a clean viability.
