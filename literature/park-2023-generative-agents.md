# Generative Agents: Interactive Simulacra of Human Behavior

**Citation:** Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang and Michael S. Bernstein, *Proceedings of UIST '23* (ACM, 2023). DOI: 10.1145/3586183.3606763. arXiv:2304.03442.
**File:** park-2023-generative-agents.pdf (22 pp.)
**Fields:** human-computer interaction, LLM agents, agent-based simulation

## Summary
The paper introduces generative agents: LLM-driven characters that plan their days, remember, reflect and talk to each other in a sandbox town ("Smallville", 25 agents, a Sims-like world). The architecture has a *memory stream* (a natural-language log of all observations), *retrieval* weighted by recency, importance and relevance, *reflection* (periodic synthesis of memories into higher-level statements) and *planning*. In a controlled evaluation, the full architecture gave the most believable answers to interview questions (TrueSkill μ = 29.89 vs 21.21 for human crowdworkers role-playing the agents), and ablating reflection, planning or observation lowered believability. In a two-day open run, information diffused and coordination emerged without user intervention.

## Key results (two-game-day run)
- **Information diffusion:** knowledge of Sam's mayoral candidacy rose from 1 agent (4%) to 8 (32%); knowledge of Isabella's Valentine's Day party from 1 (4%) to 13 (52%). None of the agents who claimed to know had hallucinated it.
- **Relationship formation:** network density rose from 0.167 to 0.74; 6 of 453 statements about other agents (1.3%) were hallucinated.
- **Coordination:** 5 of the 12 invited agents came to the party; of the 7 who did not, 3 cited conflicts.
- **Failure modes:** retrieval failures, embellishment, overly formal speech, and erratic behavior from physical norms the agents misread.

## Mapping to paper 2
- This is the reference design for LLM-agent societies: a seeded event (one agent with one piece of news) spreading through a small, designed population over two days. The AI Village differs in every design variable: real computers and the web, 21–32 frontier models from several labs, private operator-assigned roles, months of runtime, forced context erasures, and no seeded events. Spread in the village is observed, not planted.
- The memory stream and reflection are the mechanism by which a pattern could survive an agent's context loss; in the village the analog is each agent's notes and files. Our condition (2) tests whether patterns come back after wipes from other hosts and artifacts, not just from the agent's own notes.
- Their diffusion measure (fraction of agents who know, checked by interview) is a prevalence curve. Ours is the same curve, measured from posted statements, with a read-dependence test added.

## Caveats
- Smallville agents all ran one model (gpt-3.5-turbo), so shared priors and transmission cannot be separated; the paper does not try.
- Believability is a judgment by human raters, not a behavioral measurement; it is not the quantity we need.
