# The spontaneous emergence of conventions: An experimental study of cultural evolution

**Citation:** Damon Centola and Andrea Baronchelli, *PNAS* 112, 1989–1994 (2015). DOI: 10.1073/pnas.1418838112
**File:** centola-2015-spontaneous-emergence-of-conventions.pdf
**Fields:** sociophysics (naming game), network science, cultural evolution (human experiment)

## Summary
In a web experiment, human subjects play a pairwise naming game for a face, with open-ended name choice and no information about population size, partners or the global state. Only network topology changes. Homogeneously mixing populations always reach a universal convention within ~20 rounds. Spatial (ring) and random networks of degree 4 instead freeze into competing local conventions, with the largest one never above 45%. Repeated interaction with the same neighbors builds local agreement fast but blocks global agreement. In mixed populations, early local failure drives fast population-level learning. Global consensus is reached at n = 24, 48 and 96 on comparable timescales. This is the human baseline that Ashery et al. (2025) replicate with LLMs.

## Key formalism
- **Design:** each round, two network neighbors are drawn at random and name the same pictured face at once. A match pays +$0.50 and a mismatch costs −$0.25 (with no debt). Subjects see only their own and their partner's choice from that round. Names are free text, so innovation is unbounded: in every trial the number of distinct names proposed exceeds n, sometimes by more than 2×. Trials last ~25–30 rounds; there were 13 trials in total.
- **Topologies:** (i) a 1D ring lattice, degree 4 ("spatial"); (ii) a random regular graph, degree 4; (iii) homogeneous mixing, degree n − 1. Sizes are n = 24 and 48 for all three, plus one n = 96 mixed trial. The stated design range is 24 ≤ n ≤ 96 and 4 ≤ Z ≤ n − 1.
- **Results:**
  - Spatial: success ≥ 50% by round 4 in some trials, but < 75% after 25 rounds.
  - Random: success < 75% after 25 rounds; local groups form through repeated interactions, even without clustering.
  - Mixed: success reaches 100%; the leading name passes 60% of the population by round 12 and is universal by **rounds 20–22**. Symmetry breaks around round 16 at n = 48.
  - Dominant-convention size, averaged over trials: **30% (spatial), 33% (random), 96% (mixed)**. The maximum on local networks is 45% (Wilcoxon p < 0.01).
- **Ecology of names:** early frequency-rank plots are broad (close to Zipf, slope −1) in every topology. Local networks then turn exponential, an "oligopoly" of a few entrenched local conventions with no majority (coarsening). Mixed populations go winner-take-all.
- **Model:** the minimal naming game (Baronchelli et al. 2006; details in the SI, not in this PDF) gives the gray bands for 10⁴ runs. Standard results it cites: mean-field t_conv ∝ N^1.5 interactions (∝ N^0.5 rounds per agent); on low-dimensional lattices, coarsening with t ∝ N^3 in 1D; small worlds close to mean-field.
- **Controls:** a randomized list of 10 arbitrary names gives the same results, so convergence is not driven by focal points. Post-game surveys show no difference across topologies in subjects' estimates of n, but in mixed populations every subject knew the norm.
- **Committed minorities are not in this paper.** The follow-up (Centola et al., *Science* 2018) finds a tipping point at ≈25%. Theory gives ≈10% (binary model; Xie et al. 2011), where the transition is a saddle-node fold.

## Mapping to agent swarms
- **Topology = rooms × reads.** Within a room, broadcast reading makes a well-mixed population (H05: rooms couple only through ledger reads). Across rooms, H41 measures a near-complete cage: cross-room hazard 0.001× within-room in #38, and 75–100% of cross-room adoptions fall outside the logged cone. So a multi-room period behaves like separate mixed populations, not like Centola's sparse lattice. Compute the read graph per period from `context_ledger_items` (receiver, `sender`) and room membership from `rooms_timeline`.
- **Natural manipulations:**
  - Pre-2026-02-25: one room, i.e. mixed.
  - NE15 (03-16): #best/#rest split, a cut.
  - NE42 (05-04/05-11): merge into #universe-coordination, then the same split. This is an A-B-A in topology: mixing switched on for a week. Cross-group hazard rose 82× and 863× (H41).
  - #focus (08-05 → ~08-24): a split with bridging hoppers (97% of cross-room adoptions are in-cone).
  - NE32 (07-09): three GPT-5.6 newcomers in isolated rooms, merged the next day.
  - NE29 and other `roster` exits and joins: population turnover. Centola fixes n, so these go beyond his design.
- **Identical-field control:** rooms got identical kickoff text in #36, #37, #39, #40 and #42 (H47). That is the same "face" shown to separate populations, so divergence across rooms there cannot be a field effect.
- **Names and ecology:** per referent, competing names come from H34 markers co-occurring with an `artifact_mentions` artifact, a `work_commits` repo or file convention, or a role. Frequency-rank curves come per room and per village, per goal period.
- **Rounds:** a round is one pairwise exposure. A village call reads many items, so convert to per-capita reads of name-bearing items before comparing with "20–22 rounds".

## Candidate hypotheses
- **Rooms make regional dialects.** In multi-room periods, the village-wide dominant name per referent is ≤ ~50% while the within-room dominant name is ≥ 90%. One-room periods reach ≥ 90% village-wide (Centola: 96% vs 30–33%). *Observable:* dominant-convention size by room and village, per period, on identical-kickoff periods first. *Null:* room labels permuted within period (sizes kept). *Impostors:* kickoff field (identical text across rooms predicts convergence, not divergence); shared model priors (rooms with the same family mix coin the same names independently: compare against family-matched rooms in other periods).
- **Merges fix one convention and keep it (HH304, NE42).** During the merged week, competing names for shared referents collapse to one within ~20 per-capita reads. After the 05-11 split, both rooms keep the winner (an absorbing state, i.e. hysteresis) instead of reverting. *Observable:* the leading-name trajectory across the A-B-A, per referent. *Null:* a blend (pre-merge proportions persist), or reversion after the split. *Impostors:* goal #40's shared objective is a field that names things; contemporaneous convergence (only in-cone adoptions count); the winner tracks the larger room (neutral) or the strong family name (Ashery bias). Report which.
- **Splits inherit, then coarsen (NE15, #focus).** Daughter rooms start with the parent's names; new referents gain room-specific names; frequency-rank curves move from broad toward an exponential oligopoly. Divergence slows with cross-room reads (#focus < NE15). *Observable:* the Jaccard overlap of name sets between daughters over time vs the cross-read rate. *Null:* daughters reset to model priors plus kickoff. *Impostor:* H07 found identical innovations in isolated NE15 forks with no channel, so co-generation must be excluded with the light cone.
- **Isolated newcomers cannot form conventions; merged ones learn by failure (NE32).** In their one-agent rooms, the GPT-5.6 newcomers' names are their priors. After the merge, they adopt the incumbent names within a few read calls. *Observable:* the newcomers' isolated coinages compared with each other (same family, no channel), and post-merge time to adoption. *Null:* newcomers adopt only kickoff terms. *Impostor:* shared model priors. Shared coinages among isolates measure the prior field directly.

## Caveats
- Subjects named one fixed object for ~30 rounds. The village has many simultaneous referents, weekly goal changes, and names that also serve as tools (URLs, file paths), so a match carries real payoff beyond coordination.
- Pairwise, one-shot exposures vs broadcast reads plus persistent records. The village's artifacts and history search are global memory that Centola removed by design. This makes even a caged village partly well mixed through stigmergy (HH295).
- Topologies were static and of degree 4. Village rooms are near-complete graphs joined by a few hoppers, closer to a two-block stochastic block model than to a lattice.
- Experiments were short. Local-network "oligopolies" are metastable and might coarsen to consensus with more time, so the 30–33% figure is a transient.
- Populations were closed and fixed in size. Roster turnover, operator injections and model upgrades have no counterpart.
- The n = 96 result is a single trial.
