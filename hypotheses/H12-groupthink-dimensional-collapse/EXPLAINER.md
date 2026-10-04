# H12 in plain terms: is there "groupthink" in an AI agent swarm?

*For a mathematically literate non-specialist. Round 1, exploratory data only; nothing here has been tested on the held-out periods yet.*

## The question

The AI Village has 10–20 language-model agents working together for weeks, each on a goal the operators set. "Groupthink" can be made precise in two ways:

1. **Do the agents move as one?** If the swarm has a few *collective modes*, a handful of directions along which everybody varies together, then its dynamics are low-dimensional, whatever the number of agents.
2. **Does what they say collapse onto a few themes?** If all agents end up writing about the same thing, the *spread* of their messages in meaning-space should shrink.

The prediction was yes to both, and especially that the spread would shrink right after a new goal is announced, as everyone converges on it.

## The math, briefly

**Part 1: eigenvalues of a correlation matrix.** For each agent and each minute we record a spin, +1 if the agent is active (or posting in chat) and −1 if not. Over a goal period that gives an N × T matrix: N agents, T minutes. We compute the N × N matrix C of correlations between agents and look at its eigenvalues.

- **Noise level.** If agents were independent, the eigenvalues of C wouldn't all be 1. Finite T smears them out. Random-matrix theory (the Marchenko–Pastur law) says pure noise puts them in a band [(1 − √q)², (1 + √q)²], with q = N/T. An eigenvalue *above* that band is real shared structure. Its eigenvector says which agents take part and with what weights.
- **Why the textbook band isn't good enough.** That formula assumes each minute is an independent draw, which is false here. Agents work in bursts, and they all follow the same daily schedule. On simulated swarms with no coupling at all, the naive band still flagged a "collective mode" 50–90% of the time.
- **The noise level we used instead: a "cross-day surrogate".** Replace each agent's day with the *same agent's* record from a *different* day. That keeps each agent's rhythm and burstiness but destroys any same-day coordination. Do it 200 times, and call the 95th percentile of the top eigenvalue the noise edge. On the same simulated swarms this gave 6–10% false alarms.
- **Content.** The same machinery runs on *what agents say*. Each message is embedded as a vector, here 32 numbers after removing the dimensions every message shares. "Correlation" then means agents' messages drifting in the same direction within the same half hour.

**Part 2: effective dimension.** Take the cloud of message vectors from a window, with covariance eigenvalues λ₁ ≥ λ₂ ≥ … The **participation ratio**

  PR = (Σ λᵢ)² / Σ λᵢ²

is an "effective number of dimensions":
- if all the variance is on one axis, PR = 1;
- if it's spread evenly over d axes, PR = d.

With few messages the naive estimate is biased low (it read 47–87% of the truth in simulations), so we used a bias-corrected version.

## What we found

**1. There is exactly one collective mode, and it's the simplest possible one.**
- In 22 of 24 analysis units (a unit is a goal period, or a piece of one split where something changed), activity has *exactly one* eigenvalue above the noise edge. The same holds for chat in 20/24 and for message content in 24/24.
- **Every agent loads on it with the same sign.** The top eigenvector is essentially the uniform vector u = (1, …, 1)/√N. Concretely, the Rayleigh quotient uᵀCu (the variance of total activity) captures 97% of λ₁. By the Rayleigh bound, that ratio can only reach 1 when the top eigenvector is exactly uniform.
- **Reading.** That is the signature of the simplest collective model, the Curie–Weiss magnet: one global variable, roughly "how busy is the swarm right now". In finance this is called the *market mode*, everything rising and falling together. Its strength per period lines up with the coupling another hypothesis (H02) estimated independently (rank correlation 0.73).
- **Caveat: some of it is everyone going quiet at once.** Minutes where at most one agent is active make up to 42% of a period, likely platform stalls or scheduled pauses, and they create correlation trivially. Removing those minutes, the mode survives in 9 of the 11 units where such lulls are rare, and in 14/24 overall. So it is real, but part of it is "the system paused" rather than "agents influenced each other".
- **Its content version** survives removing each agent's daily average. So it is agents' messages moving together *within* a day, not just everyone drifting over the week.

**2. The "collapse after a new goal" prediction failed, in the opposite direction.**
- **Kickoffs.** Across 20 goal changes, the participation ratio changed by a median of +7%, indistinguishable from comparing two ordinary consecutive days (p = 0.86). In the later, more autonomous regime it rose by 44%, 4 out of 4 times.
- **The first day is the most diverse.** In 13 of 16 periods, day 1 of a goal is *more* spread out than the later days (p = 0.02).
- **Shared goals don't narrow content.** Weeks with a shared goal were no less diverse than "pick your own goal" weeks.

A new goal makes the swarm *explore*: lots of different ideas on day 1, some narrowing afterward. That's an anti-quench rather than a collapse.

**3. When diversity *is* low, the cause is loops, not consensus.**
The least diverse periods were #38–#40, in April and May 2026. There, 16–60% of an agent's chat messages on a given day were near-copies (cosine similarity > 0.95) of *its own* earlier messages that day. Near-copies of *other* agents' messages were 3% or less. So the low diversity came from individual agents stuck repeating themselves, not from the group converging. Removing the self-repeats leaves every verdict unchanged.

## So what?

- **The swarm is not a hive mind.** Statistically it looks like weakly coupled individuals plus one shared "busy/idle" variable, much of which the platform itself causes. That fits the other hypotheses: coupling here is real but weak.
- **If you run a swarm, watch for loops, not for consensus.** The practical result is a cheap three-number monitor that can run on any swarm's logs, with nothing fitted:
  1. *Collective-mode strength*: the top eigenvalue of the agents' content-correlation matrix over the cross-day noise edge, against the swarm's own recent history. It alarms when the swarm suddenly moves in lockstep.
  2. *Echo rate*: the share of messages nearly identical to another agent's message in the last 2 hours. This is the actual groupthink alarm, and it stayed low here.
  3. *Self-repetition rate*: the same, against the agent's own earlier messages. This is the stuck-agent alarm, and it fired in exactly the periods where diversity collapsed.
- **Caveats:**
  - one embedding model (a different one might draw the space differently);
  - a single dataset;
  - the lull filter loses power when lulls are long;
  - and so far none of this has been tested on the held-out periods.

The confirmation script is written. It runs only with your sign-off, and only once.

Files: card [README.md](README.md) (full predictions, results and scorecard); figures in [figures/](figures/), notably `H12_summary.pdf`, `rmt_arm.pdf` and `dimensionality_arm.pdf`.
