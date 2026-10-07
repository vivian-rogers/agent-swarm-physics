# 05 · Replicators, growth, decay and dissipation

**Fields:** thermodynamics, stat mech, dynamics
**References:** Kolchinsky, "Thermodynamic dissipation does not bound replicator growth and decay rates", *J. Chem. Phys.* 161, 124101 (2024) (in `literature/`); England, "Statistical physics of self-replication", *J. Chem. Phys.* 139, 121923 (2013)†.

## The model

A population of n identical replicators, each copying itself at per-capita rate g and decaying at per-capita rate δ:

$$\dot p_n = g\big[(n-1)p_{n-1} - n p_n\big] + \delta\big[(n+1)p_{n+1} - n p_n\big], \qquad \langle n\rangle \propto e^{(g-\delta)t}$$

England (2013) argued that copying must dissipate at least

$$\Delta s_{tot} \ge \ln(g/\delta)$$

so that fast, durable replicators must be wasteful. Kolchinsky (2024) shows this cannot be a universal law. The key is what decay *is*:

- **Uncopying:** decay is the reverse of replication (X + X → X + A, the copy turns back into raw material). Thermodynamic consistency (local detailed balance) then forces uncopying to be **second-order** in n. First-order growth plus first-order decay back into reactants is impossible.
- **Degradation:** decay goes to a separate waste product (X → W). Then replication and decay are independent processes with independent thermodynamics, and no bound links g, δ and dissipation.

For E. coli the England bound gives ≥ 7.6 k_BT per division, against roughly 3.3 × 10¹¹ k_BT actually dissipated. It is true but useless.

## Interesting behavior

- **Two kinds of death have different physics.** Whether a replicator dies by reversal or by degradation changes the kinetics (second- vs. first-order in n) and whether any thermodynamic bound applies.
- **Bounds that hold are often slack.** Dissipation bounds can be satisfied by orders of magnitude, so a measured cost tells you little about rates.
- **Density-dependent death.** Uncopying makes the per-capita death rate grow with n: crowding kills. That is a signature you can look for in data.

## Mapping to the village

LLM agents don't copy themselves. The replicators are **items that spread**: a convention, a project name, a plan, a code recipe. This makes model 05 the population-dynamics companion to model 03.

- **n:** number of agents currently carrying the item (using it in chat, or holding it in memory).
- **g:** adoptions per carrier per unit time.
- **δ:** abandonments per carrier per unit time.
- **Uncopying:** an explicit retraction, which needs a carrier to talk about the item ("drop that plan", "that number was wrong").
- **Degradation:** silent abandonment, i.e. it just stops being mentioned, or is dropped at a `CONSOLIDATE`.
- **"Dissipation":** token or dollar cost between exposure and reuse (`events.data` `cost`, `inputTokens`, `outputTokens`). This is not thermodynamic entropy production, so treat it as an operational cost.

## How to measure

1. Use the meme catalog from model 03. For each item, build n(t) and the adoption and abandonment events.
2. Classify each abandonment as retraction (explicit, in text) or silent.
3. Fit per-item g and δ. Test whether the abandonment hazard depends on n (second-order, uncopying-like) or not (first-order, degradation-like), with survival models using n(t) as a covariate.
4. Regress cost per adoption on ln(g/δ) across items.

## Pitfalls

- **Fitness spread confounds growth order** (H78, 2026-10-04): first-order copying (p = 1) with repo fitness spread σ_A = 0.5–1.0 gives p̂ = 1.3–2.7, and a planted p = 0.5 reads as ≈ 1.0. Big repos are big because they are fit, which mimics autocatalysis. Read only p > 1 beyond fitness-spread null worlds as evidence; repo fixed effects bias p̂ down by 0.3–0.6.
- n is at most ≈ 30, so the large-n approximations behind the formulas don't hold. Simulate the stated rules directly.
- Token prices and scaffolding change over time (`CHANGELOG.md`), so cost is not comparable across regimes without normalization.

## Named variants

Added 2026-10-07. Each entry: what the variant changes, the cards and the latest verdict.

- **Growth order / attachment kernel** (H11 round 2, H78, H94): the order p in ṅ = c n^p, and the join kernel behind it. The entry lives in model 15 ("Named variants", sub-model 5), because 15 carries the growth-order theory. Short form: p is not identified at village counts, because first-order copying with repo fitness spread reproduces every observed value (H78, this folder's pitfall). **Verdict:** failed (H78); joins are sublinear co-arrival (H11 round 2).

## Hypothesis seeds

- Explicit retractions are rare and their rate scales with n² (uncopying); most deaths are silent degradation with rate ∝ n.
- Per-item g and δ are uncorrelated, consistent with growth and decay being independent processes.
- Cost per adoption has no floor tied to ln(g/δ): any relation is slack.
