# Towards a synergy-based approach to measuring information modification

**Citation:** Joseph T. Lizier, Benjamin Flecker and Paul L. Williams, *Proc. 2013 IEEE Symposium on Artificial Life (ALIFE)*, 43–51 (2013). arXiv:1303.3440 (v1, 2013-03-14).
**File:** lizier-2013-synergy-information-modification.pdf
**Fields:** info theory, complex systems, distributed computation

## Summary
Distributed computation is described by three operations: information storage, transfer and modification. Storage and transfer have proper measures: active information storage (AIS) and transfer entropy (TE). Modification so far had only a heuristic, the separable information, whose negative local values flagged particle collisions in cellular automata. This paper defines **modified information M_X** as the sum of all synergistic atoms in the partial information decomposition (PID) of the next state over the sources {own past X^(k), causal neighbours Y_1…Y_g}. Modification is then the synergistic part of transfer, not a separate operation. In elementary cellular automata (ECAs), ordered rules have little modification, chaotic rules are dominated by it, and complex rules (54, 110) are intermediate. The paper also proposes a localizability axiom for redundancy measures, and shows that I_min fails it, so modification cannot yet be localized in space and time.

## Key formalism
- Local MI i(x;y) = log₂ p(x|y)/p(x) (can be negative: misinformation).
  - AIS: A_X(k) = I(X^(k); X′), local a_X(n+1,k) = i(x_n^(k); x_{n+1}).
  - TE: T_{Y→X}(k) = I(Y; X′ | X^(k)), local t; conditional or "complete" TE conditions on all other causal sources.
  - Take k → ∞ (in practice large k) so that storage and transfer separate.
- Chain rule: I(X′; X^(k), Y_1, Y_2) = A_X + T_{Y1→X} + T_{Y2→X|Y1}.
- Separable information (heuristic): s_X = a_X + Σ_Y t_{Y→X}. s_X < 0 flags modification events; it double-counts and omits PID atoms.
- For two sources {X^(k), Y}, TE = unique information from Y (state-independent TE) + synergy {X^(k), Y} (state-dependent TE). **M_X = that synergy**, so modification equals state-dependent TE.
- General definition: M_X = I(X′; S_DC) − I_∂^{o=1}, i.e. everything not decodable from any single source. A hierarchy by order o splits information decodable from 1, 2, 3, … sources jointly. Adding spurious uncorrelated sources does not change M_X.
- **ECA results (Table I; I_min; 100 runs × 200 cells × 200 steps; k = 16), in bits:**

  | Rule | Π(o=1) | Π(o=2) | Π(o=3) | M_X | M_X/I |
  | --- | --- | --- | --- | --- | --- |
  | 18 | 0.273 | 0.464 | 0.087 | 0.551 | 0.67 |
  | 22 | 0.188 | 0.188 | 0.559 | 0.747 | 0.80 |
  | 30 | 0.189 | 0.558 | 0.253 | 0.811 | 0.81 |
  | 54 | 0.705 | 0.087 | 0.205 | 0.292 | 0.29 |
  | 110 | 0.689 | 0.177 | 0.121 | 0.298 | 0.30 |

  With k = 1, M_X = 0.691, 0.916, 0.812, **0.860, 0.899**. Short history inflates modification about threefold in the complex rules, because unseparated storage reappears as triplet synergy.
- **Localizability axiom (Axiom 5):** a local redundancy i_∩ must satisfy symmetry and self-redundancy locally, average to I_∩, be once-differentiable in p, and be unique. I_min's localization fails: in the OR gate an infinitesimal δ flips which source is the minimum, so local values jump. Griffith–Koch is not unique; Harder is defined for two sources only.

## Mapping to agent swarms
- **Destination X′** = an agent's next state per call: DQ4 which-repo, `behavior_states_v3`, or a content PC (DQ5). **Own past X^(k)** = its recent states. Large k is the point here: the analogue is the context window, so build X^(k) from the context ledger (`context_ledger_items` visible at the call), or from ≥ one active day of allocation history, not one previous call.
- **Sources Y** = items read at that call: per sender, or bundled. Following HH299's refinement, use at most 3 sources: own past, the read, and one bundled field.
- **Storage / transfer / modification** = AIS / unique TE / M_X. HH299 predicts storage high, transfer gated and modification rare. Lizier's complex-CA numbers (M_X/I ≈ 0.3 at k = 16) give a reference scale; the copier-collective claim needs M_X/I well below that.
- **Locating events** without localizable PID: use the separable information s_X < 0 (computable from local AIS and TE alone) to locate candidate modification calls, then confirm with average PID over the flagged set vs matched unflagged calls. Expected loci: merges, debates, elections (#26).
- **Impostors.**
  - *Kickoff/goal field:* it enters as a common source to all agents; include it as a source so field information lands in redundancy or unique-field atoms, not in M_X.
  - *Scheduler:* condition on call windows (per-call clock); day edges otherwise look like synergy between own past and everything.
  - *Shared priors:* run the decomposition per family. Prior-driven responses look like state-dependent TE if the prior interacts with own state.
  - *Contemporaneous convergence:* an unread in-flight message as a placebo source should get M_X ≈ 0.

## Candidate hypotheses
- **The village computes like a complex CA, not a chaotic one.** On DQ4 allocation with k = one active day, M_X/I ≤ 0.3 in every period; at k = 1 call it rises above 0.6. The difference is the storage misattribution, and its size measures how much the context window carries. *Kill:* M_X/I ≥ 0.6 at large k (a modification-dominated swarm).
- **Modification clusters at a few loci.** Calls with s_X < 0 are ≥ 3× over-represented at merges, debates and elections relative to placebo calls matched on read count and time of day.
- **Copier collective in content.** For content states, M_X from two senders' reads is ≤ 10% of their joint TE (consistent with HH319 and H59).

## Caveats
- The ECA numbers use I_min, which inflates redundancy for independent sources (two-bit copy) and is not localizable. Recompute with BROJA, I_ccs or later pointwise PIDs. Results may shift, as the authors note.
- M_X depends on k and on the source set. Report sensitivity in k, and keep the source set fixed per period.
- With Gaussian estimators and a univariate target, all marginal-based PIDs reduce to MMI (Barrett 2015). If the own past dominates, all TE becomes synergy, i.e. "modification" by construction. Use discrete states.
- Large k needs many samples per agent. Within one goal period (4–32 agents, days of calls), pool across agents with shrinkage, not across periods.
- CA dynamics are synchronous and stationary. The village has a read-out-gated, asynchronous update, so define time per call, not per wall-clock bin.
