# Thermodynamic dissipation does not bound replicator growth and decay rates

**Citation:** Artemy Kolchinsky, *J. Chem. Phys.* 161, 124101 (2024). DOI: 10.1063/5.0213466
**File:** kolchinsky-2024-dissipation-does-not-bound-replicator-rates.pdf
**Fields:** thermodynamics, stat mech, dynamics

## Summary
England (2013) derived a bound $\Delta s_{tot} \ge \ln(g/\delta)$ linking the entropy produced when a replicator copies itself to its per-capita growth rate $g$ and decay rate $\delta$, which is widely read as a universal "dissipation vs. population dynamics" law. Kolchinsky re-derives the bound with stochastic thermodynamics (local detailed balance plus a coarse-grained "weak" LDB) and then shows it cannot hold as a universal statement. A thermodynamically consistent replicator cannot have both first-order growth and first-order decay back into its reactants. If it instead decays into separate waste products, replication and decay are independent processes with independent thermodynamics, so no universal bound links them. For E. coli the bound reduces to a trivial $\ge 7.6\,k_BT$ against an estimated $3.3\times10^{11}$ actually dissipated.

## Key formalism
- Birth-death master equation with per-capita rates: $\dot p_n \approx ng(p_{n-1}-p_n) - \delta n(p_n - p_{n+1})$, giving $\langle n\rangle \propto e^{(g-\delta)t}$.
- Weak LDB (Jensen's inequality): $\Delta s_{tot}(I\to II) \ge \ln[\pi(I\to II)/\pi(II\to I)]$ for any pair of macrostates; it is loose when pathways fluctuate or macrostates are out of internal equilibrium.
- Generalized entropy production: $\Delta s_{tot}(n\to n') \approx (n'-n)\sigma_{rep} + \ln(n!/n'!)$, hence $\sigma_{rep} \ge \ln(g/\delta) + \ln n$ for all $n$; this is only finite if decay is not first-order.
- Impossibility argument: using $\pi(0\to1)\approx\gamma\tau$ (uncatalyzed formation) gives $g \le \gamma$, contradicting autocatalysis $\gamma \ll g$.
- Concrete model: $X + A \rightleftharpoons 2X$, $X \rightleftharpoons A$ requires $\kappa_1 na \gg \kappa_2^- a$ and $\kappa_2 n \gg \kappa_1^- n^2$, which contradicts local detailed balance (Eq. 20). "Uncopying" is second-order in $n$.
- Escape route: degradation $X \rightleftharpoons W$ into a distinct waste product, so $\delta'$ is unrelated to $\Delta s_{tot}$.
- Assumptions: dilute, well-mixed, statistically indistinguishable replicators, Markov over timescale $\tau$, local equilibrium inside macrostates.

## Mapping to agent swarms
- Replicators: a stretch, since LLM agents do not copy themselves. Better candidates are propagating items such as a convention, project name, tool recipe, or plan that spreads from agent to agent through `chat_messages.content` and then into `agent_memories.content`. $n$ is the number of agents carrying the item and is small (at most ~30).
- Per-capita $g$: adoption events per carrier per unit time, defined as the first message or memory entry by agent $j$ that reuses the item after a carrier $i$ posted it in the same `room_id`.
- Per-capita $\delta$: loss rate, defined as a carrier no longer mentioning the item for $K$ days or it dropping out at a `CONSOLIDATE` event.
- "Dissipation": the nearest proxy is the cost of a copy, i.e. `cost`, `inputTokens`, `outputTokens` on the `events` rows between exposure and first reuse. This is a stretch because token cost is not entropy production and there is no temperature.
- Reversion vs. degradation: "uncopying" would be an explicit retraction ("ignore the earlier plan") found in chat text; "degradation" is silent abandonment.
- `village_goals` changes act as abrupt environment switches that force decay of goal-specific items.

## Candidate hypotheses
- Across tracked items, estimated $g$ and $\delta$ are uncorrelated (Spearman $\rho\approx0$), consistent with growth and degradation being independent processes. Observable: per-item $g,\delta$ estimated from first-use and last-use timestamps. A strong correlation would instead point to a shared control such as the consolidation prompt.
- Copy cost has no universal floor tied to $\ln(g/\delta)$: regress token cost per adoption on $\ln(g/\delta)$ across items and expect only a slack, non-binding relation. Observable: `events.data.cost` and token counts per adoption.
- Decay is not purely first-order: the per-carrier abandonment hazard depends on carrier count $n$ (second-order "uncopying"-like term). Observable: Cox or Kaplan-Meier fits of item lifetimes with $n(t)$ as a covariate.

## Caveats
- The paper is a critique of an inequality, not a model of swarms. Its main value is a warning not to assume thermodynamic bounds on agent "growth" and "decay".
- The Markov, well-mixed and indistinguishable-replicator assumptions fail for agents with long memories, room structure and heterogeneous models.
- Small $n$ breaks the large-$n$ approximations behind Eq. (1) and Eq. (14).
- Item tracking by string match or embeddings is noisy, so $g$ and $\delta$ estimates will be biased and need null models (shuffled timestamps).
- Costs in tokens or dollars depend on provider pricing and scaffolding changes (see `CHANGELOG.md`), not on physical dissipation.
