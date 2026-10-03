# Physics models

Each folder is one physics model: what it is, why it's interesting, how it maps
onto the agent swarm, how to fit it, and the nulls that keep it honest. Hypotheses
in `../hypotheses/` each pick one model from here and pair it with a data scheme.
Simulator and theory code for a model goes in its folder.

[`DEFINITIONS.md`](DEFINITIONS.md) is the shared dictionary: what "agent",
"interaction", "regime", "entropy" and so on mean in terms of dataset fields.
Every model and hypothesis uses it.

References marked † are not in `../literature/` and were written from memory.
Verify them before citing.

## Models

| # | Model | Fields | Swarm variable | Signature behavior |
| --- | --- | --- | --- | --- |
| [01](01-inverse-ising/) | Inverse Ising (pairwise max-ent) | stat mech, info theory | Binary agent state per time bin | Weak couplings, strong collective states; criticality via heat-capacity peak; frustrated factions |
| [02](02-nonequilibrium-ising/) | Nonequilibrium Ising | stat mech, thermo, dynamics | Same, with dynamics and update order | Boltzmann snapshots with nonzero entropy production under ordered updates; leader/follower from J_ij − J_ji |
| [03](03-contagion/) | Contagion (SIS/SIR/Bass/complex) | epidemics, sociophysics | Memes spreading between agents | Absorbing-state transition; pretraining acts as a field; s^{−3/2} outbreaks at threshold; hysteresis for complex contagion |
| [04](04-semantic-information/) | Semantic information | info theory, thermo | Agent or emergent structure vs. environment | Plateau-then-collapse under scrambling; agents found as maxima of semantic information |
| [05](05-replicator-dissipation/) | Replicator dissipation | thermo, stat mech | Spreading items as replicators | Uncopying must be second-order; no universal dissipation bound on growth/decay |
| [06](06-neutral-cooperative-dynamics/) | Neutral cooperative dynamics | stat mech, sociophysics | Project/topic abundances | Bimodal abundances and a long-lived cooperator core at low innovation |
| [07](07-replicators-fluctuating-environments/) | Replicators in fluctuating environments | info theory, dynamics | Approaches competing across goal changes | Passive Kelly betting; value of memory = Ω·I(R;Y); optimal memory timescale |
| [08](08-copying-vs-transformation/) | Copying vs. transformation | info theory, sociophysics | Content passed between agents | Error threshold for long messages; chains drift to model-family priors |

## How they connect

- **01 ⊂ 02.** Model 01 is the equilibrium special case of 02. Fit both to the same spins: if 01 fits well but 02 finds entropy production, the swarm looks like equilibrium in snapshots but isn't.
- **03, 05, 08 share one dataset.** All three need the same meme catalog and transmission trees. 03 asks *how far* things spread, 05 asks *how they live and die*, 08 asks *how faithfully* they're passed on. Build that scheme once and move it to `../infra/`.
- **06 and 07 are the population-level view.** Both treat projects or approaches as competing species: 06 with neutral cooperation, 07 with a changing environment.
- **04 is the interventional lens.** It needs scrambling experiments, which LLM agents (unlike organisms) actually allow, via replay or a fresh small swarm.
- **Pretraining is a field everywhere.** It's ε in 03, the prior that 08's chains converge to, and a source of spurious J in 01. Measuring it once, per model family, helps every model.

## Candidates not yet written up

- **Mismatch cost** (Kolchinsky & Wolpert, *J. Stat. Mech.* 2017†): the extra dissipation from running a process tuned for one input distribution on another. Possible link: token overhead after regime changes.
- **Information bottleneck** (Tishby, Pereira & Bialek 1999†; Kolchinsky, Tracey & Wolpert, *Entropy* 2019†): memory consolidation as compression that keeps what predicts the future.
- **Partial information decomposition** (Williams & Beer 2010†; Kolchinsky, *Entropy* 2022†): synergy among agents as a measure of emergence.
- **Kuramoto synchronization**: phase-locking of agents' activity cycles.

## Adding a model

Make `NN-short-name/README.md` with these sections: The model · Interesting behavior · Mapping to the village · How to fit (or measure) · Nulls and controls · Pitfalls · Hypothesis seeds. Add a row to the table above.
