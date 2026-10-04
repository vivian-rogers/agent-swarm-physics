# A concise and formal definition of RAF sets and the RAF algorithm

**Citation:** Wim Hordijk, arXiv:2303.01809 (v1, 2023-03-03). Short reference note summarizing the RAF theory of Hordijk & Steel, *J. Theor. Biol.* 227, 451–461 (2004). The 2004 original is not on arXiv.
**File:** hordijk-2023-raf-sets-formal-definition-algorithm.pdf
**Fields:** origins of life, network theory, algorithms

## Summary
An autocatalytic set is a reaction network in which every reaction is catalyzed by some molecule of the network, and every reactant can be made from a food set by the network's own reactions. Hordijk & Steel formalized this as RAF sets (reflexively autocatalytic and food-generated). This note restates:
- the formal definition;
- the polynomial-time algorithm that finds the unique maximal RAF (maxRAF) by repeatedly pruning reactions;
- the stricter CAF notion, which requires that the set can be built up in order with catalysts already present.

It is a definitions-and-algorithm reference, with no new empirical results.

## Key formalism
- Chemical reaction system Q = {X, R, C, F}: molecule types X; reactions r = (A, B) with reactant multiset A and product multiset B; catalysis assignments C ⊆ X × R; food set F ⊂ X.
- Closure cl_{R′}(X′) is the smallest W ⊇ X′ such that every r ∈ R′ with A ⊆ X′ ∪ W has B ⊆ W. It ignores catalysis: uncatalyzed reactions still produce.
- R′ ⊆ R is a **RAF** if every r = (A,B) ∈ R′ has (1) some catalyst x ∈ cl_{R′}(F) with (x, r) ∈ C, and (2) A ⊆ cl_{R′}(F).
- **RAF algorithm:** start with R′ = R; repeat {compute cl_{R′}(F); remove every r lacking a catalyst or a reactant in the closure} until nothing changes. A non-empty result is the unique maxRAF, which contains every RAF; an empty result means no RAF. Worst case O(|X||R|³); average sub-quadratic on polymer models.
- **subRAFs and iRAFs:** a maxRAF contains nested RAFs; an irreducible RAF (iRAF) loses the property if any reaction is removed. Find them by rerunning the algorithm after deleting random reactions. The RAFs of a network form a partially ordered set.
- **CAF** (constructively autocatalytic, Mossel & Steel 2005): the reactions can be ordered so each reactant **and** a catalyst come from food or earlier reactions. Unique maximal CAF via a modified closure (Algorithm 3). In the example network, the maxRAF {r1…r4} is not a CAF, because p1 and p2 catalyze each other's formation, so one reaction must first happen uncatalyzed. A RAF is a topological object; there can be a waiting time before it is realized dynamically.
- Software: CatlyNet (Steel et al. 2020).

## Mapping to agent swarms
- **H79's reaction system, per goal period:**
  - **X:** artifact types: repos, files, scripts, services, data products, posted URLs (`artifacts`, `artifact_mentions`).
  - **R:** session × repo reactions: inputs read or used → outputs written (DQ4 `work_commits`, with inputs from `artifact_commands_text` and context-ledger reads).
  - **C:** an artifact catalyzes a reaction if it was **executed** in the session that produced it (`artifact_commands_text`: a script run, a deployed service called, an automated stream from HH244).
  - **F:** platforms, kickoff-named artifacts and pre-period artifacts.
- **Agents are not catalysts** (H79's choice, because operators supply them). In RAF terms, agent-performed work is the uncatalyzed background: it may produce reactants within the closure, but a reaction enters a RAF only if some artifact catalyzes it.
- **Time.** RAF is topological, so a time-respecting variant is needed: the catalyst must exist, and have been executed, before the reaction. That is CAF-like ordering on timestamps. H79's time-reversed catalysis null is the matching control: a RAF that survives time reversal is not causal.
- **Outputs:** maxRAF size, the share of a period's work commits whose reactions lie in the maxRAF (H79 predicts ≤ 20%), and the iRAF size distribution (H79 predicts iRAFs of size ≥ 3 in ≤ 1/3 of periods). Report maxCAF size beside maxRAF. A RAF with no CAF needs a spontaneous bootstrap, here an agent action.
- **Impostors.**
  - *Kickoff/goal field:* goes into F. Any RAF that disappears when kickoff-named artifacts are added to the food set was the field.
  - *Scheduler:* cron triggers are timing, not catalysis. Require a content dependence (the executed artifact's output is a reactant or is read) beyond co-timing.
  - *Shared priors:* common tools (git, package managers, platform CLIs) belong in F, or every reaction is trivially "catalyzed".
  - *Contemporaneous convergence:* two repos updated together without a logged execution or read are not a catalysis edge.

## Candidate hypotheses
- **Small, single-loop RAFs.** maxRAF covers ≤ 20% of work commits per period, and most iRAFs have size 1–2 (an automaton feeding its own repo). *Egregore-positive:* an iRAF of size ≥ 3 spanning repos with different maintainers that persists across a roster change.
- **RAF beats rewired nulls only where automata exist.** Periods without HH244-type automata have maxRAF at the degree-preserving rewired null. *Kill:* RAF coverage at null in every period.
- **RAF realization lags topology.** Where a RAF exists topologically but not as a CAF, the first catalyzed cycle follows an agent-performed bootstrap reaction. The waiting time to realization is set by agent cadence (H40), not by the artifacts.

## Caveats
- The note gives definitions and algorithms only, with no empirical rates or thresholds. Results on how much catalysis random networks need for RAFs (Mossel & Steel 2005; Hordijk & Steel 2004) are cited but not in this PDF.
- RAF presence is binary and sensitive to the food set and catalysis rules. Fix F and C before looking, and report sensitivity to adding or removing platform tools from F.
- Catalysis in logs is inferred from execution and read records. Missing logs (screenshots not OCR'd) drop edges, which biases toward no RAF.
- Enumerating all iRAFs can be expensive in large networks. Use the random-deletion heuristic and report coverage, not exhaustive counts.
- The village is open (operators add goals, agents and platforms), so "self-sustaining" can only mean within a goal period with F fixed.
