# 03 · Contagion with thermodynamic intuition

**Fields:** epidemics, sociophysics, stat mech
**References:** Pastor-Satorras, Castellano, Van Mieghem & Vespignani, "Epidemic processes in complex networks", *Rev. Mod. Phys.* 87, 925 (2015)†; Marro & Dickman, *Nonequilibrium Phase Transitions in Lattice Models* (1999)†; Grassberger, *Math. Biosci.* 63, 157 (1983)†; Bass, *Management Science* 15, 215 (1969)†; Watts, *PNAS* 99, 5766 (2002)†; Centola & Macy, *Am. J. Sociol.* 113, 702 (2007)†; Scheffer et al., "Early-warning signals for critical transitions", *Nature* 461, 53 (2009)†; Vosoughi, Roy & Aral, "The spread of true and false news online", *Science* 359, 1146 (2018)†.

## The model

Something spreads from agent to agent: a phrase, a tool, a URL, a plan, a false claim. Each agent is in a compartment for each spreading item (call it a **meme**):
- **S**, susceptible: has never used it
- **I**, infected: currently uses it
- **R**, recovered: stopped using it, and won't pick it up again

Core variants, all with ρ = fraction infected, k = mean contacts, λ = transmission rate per contact, γ = recovery rate:

- **SIS** (no immunity): dρ/dt = λkρ(1 − ρ) − γρ
- **SIR** (permanent immunity): adds an R compartment; every outbreak eventually ends
- **SIRS** (waning immunity): R → S at rate ξ, i.e. agents can forget they dropped it
- **With spontaneous adoption** (field ε): dρ/dt = λkρ(1 − ρ) + ε(1 − ρ) − γρ
- **Bass diffusion** (SI with field, from marketing): dF/dt = (p + qF)(1 − F), with p = spontaneous "innovation" and q = "imitation"
- **Complex contagion:** adoption needs exposure from ≥ m distinct sources, not one

The basic reproduction number is R₀ = λk/γ.

## The thermodynamic dictionary

| Magnetism / phase transitions | Contagion | Village |
| --- | --- | --- |
| Order parameter (magnetization) | Prevalence ρ | Fraction of agents using the meme |
| Control parameter (temperature) | R₀ | Transmission per contact × contacts ÷ forgetting rate |
| Critical point | Epidemic threshold, R₀ = 1 | Memes that barely persist |
| External field h | Spontaneous adoption ε (Bass p) | Agents producing the meme with no exposure: shared pretraining, the goal prompt, a human |
| Susceptibility χ = ∂m/∂h | ∂ρ/∂ε | How strongly the swarm amplifies a nudge |
| Landau free energy | V(ρ) = −(R₀ − 1)ρ²/2 + R₀ρ³/3 (SIS, γ = 1, ε = 0) | Stability of meme states |
| Thermodynamic limit N → ∞ | Large population | **Many memes**: an ensemble over memes replaces large N |

The mean-field SIS equation is a gradient flow, dρ/dt = −V'(ρ). Below threshold the only minimum is ρ = 0. Above it, a new minimum appears at ρ* = 1 − 1/R₀, exactly like a Landau ferromagnet.

## Interesting behavior

- **Absorbing-state phase transition.** SIS has a state you can never leave (ρ = 0). That breaks detailed balance by construction, so this is an intrinsically nonequilibrium transition (directed percolation universality class on lattices), not an equilibrium one.
- **Fields smear the transition.** With ε > 0 there is no absorbing state and no sharp threshold, just as a magnetic field rounds off the ferromagnetic transition. The susceptibility peak marks where the threshold would be.
- **Critical outbreak statistics.** At R₀ = 1 the spread is a critical branching process. Outbreak sizes are power-law distributed, P(s) ∝ s^{−3/2}, and durations P(T) ∝ T^{−2} (mean-field values). SIR maps exactly onto bond percolation, so the final outbreak size is a percolation cluster.
- **Network heterogeneity lowers the threshold.** On networks, the SIS threshold is λ_c = ⟨k⟩/⟨k²⟩ (heterogeneous mean-field). Hubs make spreading easy. If one or two agents talk to everyone, nearly anything can spread.
- **Complex contagion is first-order.** Needing multiple exposures produces discontinuous jumps, bistability and hysteresis: the analog of a first-order transition with nucleation. A meme can sit dormant and then suddenly take over.
- **Critical slowing down.** Near threshold, recovery from perturbations slows (relaxation time ∝ 1/|R₀ − 1|) and variance and autocorrelation rise. These are the standard early-warning signals for tipping points.
- **Waning immunity oscillates.** SIRS with slow forgetting gives damped oscillations: waves of re-adoption.

## Mapping to the village

- **Memes:** distinctive tokens that can be tracked: invented project names, URLs, tool names, catchphrases, numbers (prices, dates), specific factual claims. Claims are especially interesting because agents misreport, so false claims can spread like misinformation, with corrections acting as recovery or vaccination.
- **Exposure:** the Interaction definition in `../DEFINITIONS.md`. Broadcast within a room is the default.
- **Infection:** the agent's first use of the meme after exposure. See Contagion / adoption event in `../DEFINITIONS.md`.
- **Recovery:** no use for K days, or the meme disappears from the agent's memory at a `CONSOLIDATE`. Memory consolidation is a natural forgetting mechanism, and therefore a natural SIRS clock.
- **Field ε:** adoption with no prior exposure. Estimate it from agents who use the meme before anyone they could have seen did. It probably depends on model family: Claude agents saying "genuinely" is a field, not a contagion.
- **Index cases:** human messages (`USER_TALK`) and goal prompts (`village_goals`) inject memes from outside.

## How to fit

1. Build a meme catalog (start with exact-match tokens; embeddings later). For each meme, record every use: agent, time and room.
2. Reconstruct transmission trees: attribute each adoption to the most recent exposure. Count offspring per adopter; the mean is the empirical branching ratio, an estimate of R₀.
3. Fit Bass (p, q) per meme. The ratio q/p separates field-driven memes (pretraining, prompts) from contagious ones.
4. Over the meme ensemble: outbreak size distribution, duration distribution, and branching ratio, compared with the critical exponents above.

## Nulls and controls

- **Shuffled exposure:** keep each agent's adoption times but randomize who was exposed when. True contagion should beat this.
- **Exposure-free baseline:** adoption rates among agents who could not have seen the meme (other rooms, before rooms existed only via timing).
- **Common-source control:** memes in the goal prompt are seen by everyone at once. Separate them or model them as a field.

## Pitfalls

- N is tiny (≈ 10–30 agents), so a single meme's curve is noisy and thresholds are smeared. The ensemble over memes is the real dataset.
- Pretraining is a strong, model-family-specific field. Ignoring it overestimates transmission.
- Agents copy from tool outputs and the web as well as from each other; those are hidden sources.

## Hypothesis seeds

- The meme ensemble's outbreak size distribution is a power law near s^{−3/2}: the swarm sits near the epidemic threshold.
- False claims spread with a higher branching ratio than their corrections.
- Adoption needs ≥ 2 independent sources for factual claims (complex contagion) but only one for vocabulary (simple contagion).
- Memes not written into memory at consolidation die out; meme lifetime is set by consolidation, not by chat.
