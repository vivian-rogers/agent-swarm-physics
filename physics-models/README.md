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
| [09](09-hawkes/) | Hawkes processes | dynamics, stat mech | Event timestamps per agent | Branching ratio n = fraction of self-generated activity; inside vs. outside shocks decay differently |
| [10](10-potts/) | Potts (categorical states) | stat mech, sociophysics | Project, room, role or vote per agent | First-order consensus jumps for q ≥ 3; antiferromagnetic Potts = division of labor (graph coloring) |
| [11](11-vector-spins/) | Vector spins: O(n), Heisenberg, spherical | stat mech, dynamics | Embedding vector (or √p over topics) per agent | Polarization and Goldstone soft modes; the goal is a literal field vector; ordering without a field |
| [12](12-information-dynamics/) | Information dynamics: PID, O-information, causal emergence, individuality | info theory, complex systems | Agents' 1-d or discrete states, a macro-variable and an impostor environment per bin | Fields add redundancy that hides synergy; Ψ > 0 suffices for emergence but Ψ < 0 is inconclusive; individuality never falls with size, so only the excess over size-matched groups counts |
| [13](13-cultural-evolution-conventions/) | Cultural evolution and conventions: naming game, drift, Price, stigmergy | sociophysics, cultural evolution | Names, terms and traces carried by agents and artifacts | Well-mixed rooms fix one convention, caged rooms keep dialects; committed minorities tip a convention through a fold; culture outlives carriers through the record |
| [14](14-scaling-and-fluctuations/) | Scaling and fluctuations: Y ∝ N^β, Taylor's law, phenomenological RG, active order | stat mech, complex systems, active matter | Unit outputs vs N; per-agent means and variances; term usage series; content velocities | Taylor's pair covariance c_× gauges the shared field (c_T does not, H86); superlinear β would be a collective benefit; a field alone mimics a fixed point in α̃ but not in β̃ |
| [15](15-stochastic-thermodynamics-selection/) | Stochastic thermodynamics of selection: excess/housekeeping, speed limits, RAF, assembly | thermodynamics, stat mech, origins of life | Ensemble fluxes between behavior or allocation states; repos as replicators; artifact reaction networks | Day edges are excess and work cycles are housekeeping; selection resolves only s ≥ e^{−σ*}; superlinear growth order means winner-take-all |

## How they connect

- **One spin family: 01 → 10 → 11.** Ising (binary), Potts (q categories) and O(n) (continuous vectors) are the same pairwise max-ent idea with richer state spaces. Potts' clock model at q → ∞ is XY (n = 2). Each has a kinetic version, so each also generalizes 02. Start with the coarsest state that captures the question.
- **01 ⊂ 02.** Model 01 is the equilibrium special case of 02. Fit both to the same spins: if 01 fits well but 02 finds entropy production, the swarm looks like equilibrium in snapshots but isn't.
- **03, 05, 08 share one dataset.** All three need the same meme catalog and transmission trees. 03 asks *how far* things spread, 05 asks *how they live and die*, 08 asks *how faithfully* they're passed on. Build that scheme once and move it to `../infra/`.
- **06 and 07 are the population-level view.** Both treat projects or approaches as competing species: 06 with neutral cooperation, 07 with a changing environment.
- **04 is the interventional lens.** It needs scrambling experiments, which LLM agents (unlike organisms) actually allow, via replay or a fresh small swarm.
- **09 is the baseline for everything with time in it.** It uses only timestamps. If self-excitation already explains the activity, couplings in 01/02 are partly just excitation. Its branching picture is the same object as 03's outbreaks, and its EM fit reconstructs transmission trees for 03, 05 and 08.
- **Pretraining is a field everywhere.** It's ε in 03, the prior that 08's chains converge to, and a source of spurious J in 01. Measuring it once, per model family, helps every model.
- **12 is the information layer over 01, 04 and 08.** PID, O-information and causal emergence decompose the states that 01 fits pairwise. Krakauer individuality gives 04's semantic information a boundary test. The copy/transformation split stays in 08. Size-matched groupings are the shared null.
- **13 carries 03, 06 and 10 into the record.** A naming game is Potts fixation (10) on a read graph. Drift uses 06's neutral null, and adoption cascades are 03's. Stigmergy moves memory into artifacts, where 04 and 12 measure it.
- **14 adds size and scale to every model.** It asks how a statistic changes with N, with the mean or with the bin. The dilution law J ∝ N^−0.6 (01, H18) and per-pair branching (03, 09) are size laws. The Taylor pair covariance c_× is a field gauge for 01, 02 and 11.
- **15 is the thermodynamic layer over 02 and 05.** It adds the excess/housekeeping split and speed limits to 02's kinetic master equations. It adds selection resolution, growth order, RAF closure and assembly to 05's replicators. 06 is its neutral null.

## What held up (round 1, 2026-10-04)

Counts come from the `models` field of the 81 `../hypotheses/*/summary/meta.json` files (H01–H80 without H51, plus H85 and H86). The outcome says whether the model held for the hypothesis's claim after round 1b. "Primary" is the card's model; "secondary" is a second fitted model. Rival, null and tool roles are counted separately.

- **01 Inverse Ising.** Primary 14: 1 supported, 7 mixed, 6 refuted. Secondary 9: 1 supported, 3 mixed, 4 refuted, 1 n/a. The mean-field reading holds: the swarm is subcritical (H16 βJ₀ < 1; H25; H67 g_lag < 0.40), and per-pair coupling dilutes as N^−0.6 (H18). Stance antagonism follows the prize field with no remanent coupling (H64, the one primary support). Spin-glass (H22), dilute-bond (H49) and equal-time collapse (H19) readings fail.
- **02 Nonequilibrium Ising.** Primary 20: 2 supported, 12 mixed, 6 refuted. Secondary 11: 2 supported, 5 mixed, 2 refuted, 2 untested. Read-out-gated kinetics holds: talk couplings act at the recipient's next call (H08, H50), on a call clock in regimes II–III (H40). Idle escape fits kinetic escape with intrinsic aging (H72). Pairwise couplings (H02), the Kramers double well (H16), the EP platform fingerprint (H56) and the one-lever model (H59) fail.
- **03 Contagion.** Primary 5: 2 mixed, 3 refuted. Secondary 4: 1 supported, 1 mixed, 2 refuted. As a rival it won once (H63: links precede herding bursts). Idea cascades are subcritical (H34, R̂ 0.06–0.39), adoption is seed-locked and room-bounded (H53), and the reply premium survives the tie-only guard in 23/26 periods (H62). Links as causes of herding (H28), seed-fitness forecasts (H61) and a two-strategy dilution mixture (H68) fail.
- **04 Semantic information.** Primary 9: 4 mixed, 4 refuted, 1 untested. Secondary 6: 1 supported, 2 mixed, 1 refuted, 2 untested. The context window carries the value: erasure costs 39% of work (H15) and κ_C ≈ 5 commits per 20 calls per bit (H70). Artifacts, not memory, restore output after erasure (H44). No group carries KW semantic information beyond agent + own artifact (H01, H58).
- **05 Replicator dissipation.** Primary 3: 1 mixed, 2 refuted. Secondary 4: 3 mixed, 1 refuted. Null 1: supported (H45, passive import). First-order self-maintenance holds (H79). The affinity σ\* and growth order p are not identified at village counts (H77, H78).
- **06 Neutral cooperative dynamics.** Primary 1: refuted (H06, NCD fails in 4/5 free weeks). Null 4: 3 supported, 1 mixed. As a null it holds: neutral copying on real call schedules reproduces σ\* (H77), p (H78) and RAF coverage (H79).
- **07 Replicators in fluctuating environments.** No summary lists it in any role. Untested.
- **08 Copying vs transformation.** Primary 3: 1 supported, 1 mixed, 1 refuted. Secondary 1: supported. Copying dominates fork lineages (H07) and restatement loops (H69, copies of in-context own text). Vocabulary is copied, plans are not (H23). Copy share does not rise with backlog (H57).
- **09 Hawkes.** Primary 5: 5 refuted. Secondary 9: 4 supported, 4 mixed, 1 untested. The branching ratio holds as a reading of loop gain (H19, H25, H67) and of per-pair uptake (H18). As a primary model it fails: the read-out step removes cross-excitation (H42, n_cross 0.004 vs 0.061), and no refractory window exists (H43).
- **10 Potts.** Primary 6: 1 mixed, 5 refuted. Secondary 10: 1 supported, 5 mixed, 1 refuted, 3 untested. As a rival it won once (H75: instant freeze onto named projects). Two-camp order appears only with assigned sides (H21, H37, H64). Herding-sign (H11), stuckness (H17), critical slowing (H27) and spectral-gap (H31) predictions fail.
- **11 Vector spins.** Primary 13: 1 supported, 7 mixed, 5 refuted. Secondary 8: 4 supported, 2 mixed, 1 refuted, 1 untested. The goal as a field vector holds: kickoff text is the day-1 target (H54), human messages pull content (H30), and the centroid shift dates goal steps (H74, AUC 0.89). Exponential tilt (H10), near-critical content (H26) and content sublattices (H21) fail.
- **12 Information dynamics.** Secondary 2: untested. Tool 3. No claim has run on it yet; its held-out individuality and transfer estimators serve as tools.
- **13 Cultural evolution and conventions.** Secondary 7, rival 1: all untested. Tool 1. No claim has run on it yet.
- **14 Scaling and fluctuations.** Primary 2: 2 mixed. Secondary 3: untested. Tool 4. Talk scales sublinearly with N (H85, β 0.33). Taylor's c_T and b fail as field gauges, and the pair covariance c_× works (H86).
- **15 Stochastic thermodynamics of selection.** Secondary 5: untested. Tool 4. Its content ran under the 02 and 05 labels: excess EP sits at the scheduler's day edges (H76), and speed-limit slack separates named from free kickoffs (H75, S 1.0–1.4 vs 5–15). σ\* and p are not identified (H77, H78).

## Candidates not yet written up

Moved out of this list on 2026-10-04: partial information decomposition now lives in [12](12-information-dynamics/), and stigmergy / reinforced choice (Deneubourg choice function, nonlinear Pólya urn) in [13](13-cultural-evolution-conventions/).

- **Mismatch cost** (Kolchinsky & Wolpert, *J. Stat. Mech.* 2017†): the extra dissipation from running a process tuned for one input distribution on another. Possible link: token overhead after regime changes.
- **Information bottleneck** (Tishby, Pereira & Bialek 1999†; Kolchinsky, Tracey & Wolpert, *Entropy* 2019†): memory consolidation as compression that keeps what predicts the future.
- **Activity-driven temporal networks** (Perra et al., *Sci. Rep.* 2012†): each agent activates at its own rate and makes a few links when active. The natural substrate for 03; the epidemic threshold depends on the spread of activity rates, not on a static network.
- **Drift–diffusion and Markov state models in embedding space**: agents' message streams as trajectories; Kramers–Moyal drift/diffusion fields, or a discretized Markov state model with metastable states and probability currents. Shares its state space with 11 and ties to 02.
- **Random matrix theory** (Marchenko–Pastur†): a tool for separating real structure in small-sample correlation and coupling matrices from noise. Supports 01.
- **Kuramoto synchronization**: phase-locking of agents' activity cycles. It is the n = 2 dynamics of 11 with intrinsic frequencies.

## Adding a model

Make `NN-short-name/README.md` with these sections: The model · Interesting behavior · Mapping to the village · How to fit (or measure) · Nulls and controls · Pitfalls · Hypothesis seeds. Add a row to the table above.
